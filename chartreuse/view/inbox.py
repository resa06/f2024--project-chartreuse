from urllib.parse import unquote
from ..models import Like, User, Post, Comment, FollowRequest, Follow
from ..views import Host, checkIfRequestAuthenticated
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.core.exceptions import ValidationError

def create_user_url_id(request, id):
    id = unquote(id)
    if id.find(":") != -1:
        return id
    else:
        # create the url id
        host = request.get_host()
        scheme = request.scheme
        url = f"{scheme}://{host}/chartreuse/api/authors/{id}"
        print(url,'kkkk')
        return url
    

@extend_schema(
    summary="Handle incoming posts, comments, likes, and follow requests",
    description=(
        "Processes data sent to an author's inbox for different types of content, "
        "including posts, comments, likes, and follow requests. Depending on the content type, "
        "the function adds, updates, or removes the relevant objects in the database."
        "\n\n**When to use:** Use this endpoint when sending new posts, comments, likes, or follow requests "
        "to a remote author's inbox for further processing."
        "\n\n**How to use:** Send a POST request with the remote author's `user_id` in the URL path and a valid JSON payload "
        "specifying the `type` (e.g., 'post', 'comment', 'like', or 'follow') along with the required data."
        "\n\n**Why to use:** This endpoint provides a centralized mechanism to handle interactions with a remote author's "
        "inbox, ensuring consistency in the database."
        "\n\n**Why not to use:** Avoid using this endpoint for retrieving data or if the required data format is unavailable."
    ),
    request=inline_serializer(
        name="InboxRequest",
        fields={
            "type": serializers.ChoiceField(
                choices=["post", "comment", "like", "follow"],
                help_text="The type of data being sent to the inbox."
            ),
            "id": serializers.CharField(help_text="Unique ID of the post/comment/like/follow."),
            "author": serializers.JSONField(help_text="Author information of the object."),
            "published": serializers.DateTimeField(help_text="Timestamp when the object was created."),
            "content": serializers.JSONField(required=False, help_text="Content of the post or comment."),
            "comments": serializers.JSONField(required=False, help_text="Comments associated with the post."),
            "likes": serializers.JSONField(required=False, help_text="Likes associated with the post or comment."),
        }
    ),
    responses={
        200: OpenApiResponse(
            description="Request processed successfully.",
            response=inline_serializer(
                name="SuccessfulResponse",
                fields={
                "status": serializers.CharField(default="Post added successfully")
            }
            )
            
        ),
        400: OpenApiResponse(
            description="Invalid request format.",
            response=inline_serializer(
                name="BadRequestResponse",
                fields={
                    "error": serializers.CharField(default="Invalid input data.")
                }
            )
        ),
        401: OpenApiResponse(
            description="Unauthorized request.",
            response=inline_serializer(
                name="UnauthorizedResponse",
                fields={
                    "error": serializers.CharField(default="Unauthorized.")
                }
            )
        ),
        404: OpenApiResponse(
            description="User not found or data references invalid objects.",
            response=inline_serializer(
                name="NotFoundResponse",
                fields={
                    "error": serializers.CharField(default="Resource not found.")
                }
            )
        ),
    }
)
@api_view(["POST"])
@csrf_exempt
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication])
def inbox(request, user_id):
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({'error':'Invalid JSON Format'},status=400)

    decoded_url_id = create_user_url_id(request, user_id)
    author = User.objects.filter(url_id=decoded_url_id).first()
    if author is None:
        return JsonResponse({"error": f"Author,{user_id},not found"}, status=404)

    # check request headers
    authorization = request.headers.get('Authorization')
    if authorization is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    
    authorization_response = checkIfRequestAuthenticated(request)
    if authorization_response.status_code != 200:
        return authorization_response
    
    if data.get('type') is None:
        return JsonResponse({'error':'Invalid JSON Format'},status=400)

    if (data["type"] == "post"):
        try:
            title = data["title"]
            description = data["description"]
            post_id = data["id"]
            contentType = data["contentType"]
            content = data["content"]
            author = data["author"]
            comments = data.get("comments",{})
            likes = data.get("likes",{})
            published = data["published"]
            visibility = data["visibility"]
        except KeyError:
            return JsonResponse({'error':'Invalid JSON Format'},status=400)

        # check whether we need to add this post or update it or delete it
        post = Post.objects.filter(url_id=post_id).first()

        # get author object
        try:
            author_id = unquote(author["id"])
        except KeyError:
            return JsonResponse({'error':'Author missing ID field'},status=400)
        author = discover_author(author_id,author)

        if author is None:
            return JsonResponse({'error':'Invalid JSON Format'},status=400)

        if post is None:
            # create a new post
            try:
                new_post = Post.objects.create(title=title, url_id=post_id, description=description, contentType=contentType, content=content, user=author, published=published, visibility=visibility)
                new_post.published = published
                new_post.save()
                new_post.full_clean()
            except ValidationError:
                new_post.delete()
                return JsonResponse({'error':'Invalid JSON Format'},status=400)
            

            # add comment objects
            post_comments = comments.get('src',[])
            
            for post_comment in post_comments:
                try:
                    comment_author = post_comment["author"]
                    comment = post_comment["comment"]
                    contentType = post_comment["contentType"]
                    comment_id = post_comment["id"]
                    post = post_comment["post"]
                    published = post_comment["published"]
                    likes = post_comment.get('likes',{})
                except KeyError:
                    continue
                
                try:
                    comment_author_id = unquote(comment_author["id"])
                except KeyError:
                    continue

                comment_author = discover_author(comment_author_id,post_comment['author'])
                if comment_author is None:
                    continue

                try:
                    new_comment = Comment.objects.create(user=comment_author, url_id=comment_id, comment=comment, contentType=contentType, post=new_post)
                    new_comment.dateCreated = published
                    new_comment.save()
                    new_comment.full_clean()
                except ValidationError:
                    new_comment.delete()
                    continue

                
                
                # add comment likes
                comment_likes = post_comment.get('likes',{})
                comments_src = comment_likes.get('src',[])
                for comment_like in comments_src:
                    try:
                        like_author = comment_like["author"]
                        published = comment_like["published"]
                        like_id = comment_like["id"]
                        post = comment_like["object"]
                    except KeyError:
                        continue
                    
                    try:
                        like_author_id = unquote(like_author["id"])
                    except KeyError:
                        continue
                    like_author = discover_author(like_author_id,comment_like['author'])

                    if like_author is None:
                        continue
                    
                    try:
                        new_like = Like.objects.create(user=like_author, url_id=like_id, comment=new_comment)
                        new_like.dateCreated = published
                        new_like.save()
                        new_like.full_clean()
                    except ValidationError:
                        new_like.delete()
                        continue
                    
                   

            # add like objects
            
            post_likes = data.get("likes",{})
            for post_like in post_likes.get('src',[]):
                try:
                    author_id = post_like["author"]['id']
                except KeyError:
                    continue

                # check to see whether the author has been discovered yet or not!
                current_author = discover_author(author_id,post_like['author'])
                if current_author is None:
                    continue
                try:
                    published = post_like["published"]
                    like_id = post_like["id"]
                    post = post_like["object"]
                except KeyError:
                    continue
                
                try:
                    new_like = Like.objects.create(user=current_author, url_id=like_id, post=new_post)
                    new_like.dateCreated = published
                    new_like.save()
                    new_like.full_clean()
                except ValidationError:
                    new_like.delete()
                    continue
                    

        else:
            try:
                post.visibility = visibility
                post.title = title
                post.description = description
                post.contentType = contentType
                post.content = content
                post.save()
                post.full_clean()
            except ValidationError:
                post.delete()
                JsonResponse({'error':'Invalid JSON Format'},status=400)
                    
        return JsonResponse({"status": "Post added successfully"},status=200)

    elif (data["type"] == "comment"):
        try:
            comment_author = data["author"]
            comment_text = data["comment"]
            contentType = data["contentType"]
            comment_id = data["id"]
            post = data["post"]
            published = data["published"]
        except KeyError:
            return JsonResponse({'error':'Invalid JSON Format'},status=400)
        likes = data.get("likes",{})
        # add this new comment if it does not exist, if it exists, then delete it

        try:
            comment_author_id = unquote(comment_author["id"])
        except KeyError:
            return JsonResponse({'error':'Invalid JSON Format'},status=400)
        
        comment_author = discover_author(comment_author_id,comment_author)
        if comment_author is None:
            return JsonResponse({'error':'Invalid JSON Format'},status=400)
        
        new_post = Post.objects.filter(url_id=post).first()

        if new_post is None:
            return JsonResponse({'error':'Post does not exist'},status=404)

        # check whether comment already exists
        comment = Comment.objects.filter(comment=comment_text, user=comment_author, post=new_post).first()

        if comment is None:
            try:
                comment = Comment.objects.create(user=comment_author, comment=comment_text, url_id=comment_id, contentType=contentType, post=new_post)
                comment.dateCreated = published
                comment.save()
                comment.full_clean()
            except ValidationError:
                comment.delete()
                return JsonResponse({'error':'Invalid JSON Format'},status=400)

        # add comment likes
        comment_likes = likes.get('src',[])
        for comment_like in comment_likes:
            try:
                like_author = comment_like["author"]
                published = comment_like["published"]
                like_id = comment_like["id"]
                post = comment_like["object"]
            except KeyError:
                continue # just skip to the next like.

            try: # see if author would be correctly formatted...
                like_author_id = unquote(like_author["id"])
            except KeyError:
                continue

            like_author = discover_author(like_author_id,like_author)

            if like_author is None:
                continue
            

            # check whether like already exists
            like = Like.objects.filter(user=like_author, url_id=like_id, comment=comment).first()

            if like is None:
                try:
                    new_like = Like.objects.create(user=like_author, url_id=like_id, comment=comment)
                    new_like.dateCreated = published
                    new_like.save()
                    new_like.full_clean()
                except ValidationError:
                    new_like.delete()
                    continue

        return JsonResponse({"status": "Comment added successfully"})
        
    elif (data["type"] == "like"):
        try:
            author = data["author"]
            published = data["published"]
            like_id = data["id"]
            object_id = data["object"]
        except KeyError:
            return JsonResponse({'error':"Invalid JSON format"},status=400)
        # add the like if it does not exist, if it exists, delete the like
        try:
            author_id = unquote(author["id"])
        except KeyError:
            return JsonResponse({'error':"Invalid JSON format"},status=400)
        
        author = discover_author(author_id,author)

        if author is None:
            return JsonResponse({'error':"Invalid JSON format"},status=400)
        

        post = Post.objects.filter(url_id=object_id).first()

        if post is None:
            object_type = "comment"
        else:
            object_type = "post"

        # check whether like already exists
        if object_type == "post":
            like = Like.objects.filter(user=author, post=post).first()
            if like is None:
                try:
                    new_like = Like.objects.create(user=author, url_id=like_id, post=post)
                    new_like.dateCreated = published
                    new_like.save()
                    new_like.full_clean()
                    return JsonResponse({"status": "Like added successfully"})
                except ValidationError:
                    new_like.delete()
                    return JsonResponse({'error':'Invalid JSON format'},status=400)

        else:
            comment = Comment.objects.filter(url_id=object_id).first()
            if comment is None:
                return JsonResponse({"error":'Object to like does not exist'},status=404)
            like = Like.objects.filter(user=author, comment=comment).first()
            if like is None:
                try:
                    new_like = Like.objects.create(user=author, url_id=like_id, comment=comment)
                    new_like.dateCreated = published
                    new_like.save()
                    new_like.full_clean()
                    return JsonResponse({"status": "Like added successfully"})
                except ValidationError:
                    new_like.delete()
                    return JsonResponse({'error':'Invalid JSON format'},status=400)
       
            

    elif (data["type"] == "follow"):
        try:
            actor = data["actor"]
            object_to_follow = data["object"]
        except KeyError:
            return JsonResponse({'error':'Invalid JSON format'},status=400)

        try:
            author_queryset = User.objects.filter(url_id=unquote(actor['id'])).first()
        except:
            return JsonResponse({'error':'Missing object id field'})

        if not author_queryset:
            # discovered a new author to add to database...

            # November 14, 2024: Asked Agent: CHAT GPT, why we may be getting null constraints failed when we have nullability allowed, chatgpt recommended setting the value explicitly to null or
            # maybe migrations we not applied.
            try:
                remote_author = User.objects.create(
                    user = None,
                    url_id = unquote(actor['id']),
                    displayName = actor.get('displayName',''),
                    host = actor.get('host',''),
                    github = actor.get('github',''),
                    profileImage = actor.get('profileImage',''),
                )
                remote_author.full_clean()
            except ValidationError:
                remote_author.delete()
                return JsonResponse({'error':'Invalid JSON format'},status=400)
        else:
            remote_author = author_queryset

        # check if either a follow already exists or a follow request is already sent to them...

        try:
            follower = User.objects.get(pk=unquote(actor["id"]))
            followed = User.objects.filter(pk=unquote(object_to_follow["id"])).first()
            if followed is None:
                return JsonResponse({'error':'User to follow does not exist'},status=404)
            
        except KeyError:
            return JsonResponse({'error':'Invalid JSON format'},status=400)


        follow_queryset = Follow.objects.filter(followed=followed,follower=follower)
        follow_request_queryset = FollowRequest.objects.filter(requester=remote_author,requestee=followed)
        if follow_queryset.exists() or follow_request_queryset.exists():
            # no need to send duplicate request.
            return JsonResponse({"status": "Follow request sent successfully"},status=200)

        # add the follow request if it does not exist, if it exists, delete the follow request
        new_follow_request = FollowRequest.objects.create(requester=remote_author, requestee=followed)
        new_follow_request.save()
    
        return JsonResponse({"status": "Follow request sent successfully"},status=200)
    
def discover_author(url_id,json_obj):

    author_queryset = User.objects.filter(url_id=url_id)
    if not author_queryset.exists():
        try:
            current_author = User.objects.create(
                url_id = url_id,
                displayName = json_obj.get('displayName'),
                host = json_obj.get('host'),
                github = json_obj.get('github'),
                profileImage = json_obj.get('profileImage')
            )
            # CHATGPT (OpenAI) citation. on November 26, 2024, asked: "why is my validation not being checked, and does the create method check for validation",
            # To which chat gpt said my test data urls in test_inpox.py were incorrect and that calling full_clean will validate the items.
            current_author.full_clean()
        except ValidationError:
            current_author.delete()
            return None
    else:
        current_author = author_queryset[0]
    return current_author


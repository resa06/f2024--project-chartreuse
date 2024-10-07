from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from .models import User,Like,Comment,Post,Follow,FollowRequest
from django.views.generic.detail import DetailView
from django.http import HttpResponseNotAllowed


class Host():
    host = "https://f24-project-chartreuse-b4b2bcc83d87.herokuapp.com/"

def signup(request):
    return render(request, 'signup.html')

def save_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password_1 = request.POST.get('password1')
        password_2 = request.POST.get('password2')
        displayname = request.POST.get('displayname')
        github = request.POST.get('github')

        # create the auth user first, bacause User has a one to one relationship with it
        auth_user = AuthUser(username=username, password=password_1)
        auth_user.save()

        # now create the User
        user = User(user=auth_user, displayName=displayname, github=github)
        user.save()

        return redirect('chartreuse/login')

def login(request):
    return render(request, 'login.html')

def error(request):
    return render(request, 'error.html')



def follow_accept(request,followee,follower):

    '''
    Purpose: View to interact with the follow requests database by deleting a request and processing the request into a new follower

    Arguments:
    request: Request body containing the followee id and the follower id to process into the database.
    followee: the primary key of the User object getting followed.
    follower: the primary key of the User object doing the following
    '''

    if request.method == "POST": # get the request body.
        followed_used = get_object_or_404(User,user=followee)
        following_user = get_object_or_404(User,user=follower)
        follow_request = get_object_or_404(FollowRequest,requester=following_user,requestee=followed_used)
        follow = Follow(follower=following_user,followed=followed_used) # create the new follow!
        follow.save()
        follow_request.delete()
        return redirect('chartreuse:profile',pk=followee)
    
    return HttpResponseNotAllowed(["POST"])

def follow_reject(request,followee,follower):
    '''
    Purpose: View to interact with the follow requests database by rejecting a follow request and not processing it into a follow!!

    Arguments:
    request: Request body containing the id's of who is to be followed and who is following
    followee: the primary key of the User object getting followed.
    follower: the primary key of the User object doing the following
    '''
    if request.method == "POST":
        followed_used = get_object_or_404(User,user=followee)
        following_user = get_object_or_404(User,user=follower)
        follow_request = get_object_or_404(FollowRequest,requester=following_user,requestee=followed_used)
        follow_request.delete()
        return redirect("chartreuse:profile",pk=followee)
    return HttpResponseNotAllowed(["POST"])



class ProfileDetailView(DetailView):

    '''
    Purpose: Serve associated files related to the user specified in the URL pk

    Inherits From: DetailView (Allows us to obtain all fields associated to a user whilst adding more
    By overriding get_context_data, and retreiving the nested user primary key in the url by overriding get_object)

    '''


    model = User
    template_name = "profile.html"
    context_object_name= "profile"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        user = context['profile']
        # Overriden to get these addition counts.
        context['like_count'] = Like.objects.filter(user=user).count()
        context['comment_count'] = Comment.objects.filter(user=user).count()
        context['post_count'] = Post.objects.filter(user=user).count()

        follow_requests = FollowRequest.objects.filter(requestee=user)
        requests = [fk for fk in follow_requests]

        context['requests'] = requests
        print(requests)
        print(context)
    
        return context
        

    def get_object(self):
        # user's Id can't be obtained since the User model does not explicity state a primary key. Will retrieve the user by grabbing them by the URL pk param.
        
        user_id = self.kwargs['pk']
        return get_object_or_404(User,user=user_id)
        


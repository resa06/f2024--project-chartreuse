from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from chartreuse.models import User,Like,Comment,Post,Follow,FollowRequest
from django.views.generic.detail import DetailView
from django.http import HttpResponseNotAllowed
from urllib.parse import unquote, quote
from django.http import Http404 

class FollowListDetailView(DetailView):
    template = 'follow-list.html'
    context_object_name = 'user'
    model = User

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)

        user = context['user']
        relationship = self.kwargs['relationship']
        context['relationship'] = relationship

        # On October 14, 2024 Asked ChatGPT: How to throw django 404 error
        if relationship != "following" and relationship != "followers":
            raise Http404("Page not found")
        elif relationship == "followers":
            follows = self.get_followers(user)
        else:
            follows = self.get_following(user)

        

        # need to be able to send the correct percent encoded url upon view-profile action, so percent encode all id's
        for follow_user in follows:
            follow_user.url_id = quote(follow_user.url_id,safe='')
            
        


    def get_object(self):
        user_id = unquote(self.kwargs['url_id'])
        return get_object_or_404(User,url_id=user_id)
    
    def get_following(self,user):
        '''
        Purpose: Portion of the View that returns a queryset of all following for that user.

        Arguments:
        user: The User Model object to find the the users being followed by this user

        '''
        follows = Follow.objects.filter(follower = user)
        return [follow.followed for follow in follows]
        

    def get_followers(self,user):
        '''
        Purpose: Portion of the View that returns a queryset of all followers for the user.

        Arguments:
        user: The User Model object to find the followers for
        '''
        follows = Follow.objects.filter(followed = user)
        return [follow.follower for follow in follows]
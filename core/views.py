from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from django.http import HttpResponseRedirect

from django.utils import timezone

from .models import Post, Comment, PostVote
from .forms import PostForm, CommentForm, CommentReplyForm

from .hreporter import Reporter

def home(request):
    post_list = Post.score_sorted.all()
    page = request.GET.get('p', 1)

    paginator = Paginator(post_list, 10)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'post_list.html', {'posts' : posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=pk)
    form = CommentForm()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user.username
            comment.post = Post.score_sorted.get(pk=pk)
            comment.published_date = timezone.now()
            comment.save()
    return render(request, 'post_detail.html', {'post'     : post,
                                                'comments' : comments,
                                                'form'     : form })
def comment_reply(request,post_id,parent_id):
    formset = ""
    if request.method == 'POST':
		formset = CommentReplyForm(request.POST)
		if formset.is_valid():
			comment = formset.save(commit=False)
			comment.author = request.user
			comment.save()
			return redirect('/post/' + post_id)
    else:
		comment = Comment()
		comment.post = Post.score_sorted.get(pk=post_id)
		if parent_id != "0":
			comment.parent = Comment.objects.get(pk=parent_id)
		formset = CommentReplyForm(instance=comment)
    formset.fields['post'].widget = forms.HiddenInput()
    formset.fields['parent'].widget = forms.HiddenInput()
    return render(request,"comment_reply.html", {"formset": formset})


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def submit(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user.username
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'submit.html', {'form' : form})

@login_required
def submit_vote(request, pk):
    if request.method == 'POST':
        u = User.objects.get(id=request.user.id)
        p = Post.score_sorted.get(id=pk)
        voteargs = request.body.split("&vote=")[1]
        try:
            v, created = PostVote.objects.update_or_create(post=p, user=u)
        except:
            v, created = (PostVote(post=p, user=u, vote=0), True)
        if not created:
            if v.vote != 0:
                v.vote = 0
            else:
                v.vote = get_vote_value(voteargs)
            v.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            v.vote = get_vote_value(voteargs)
            v.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def get_vote_value(voteargs):
    '''
    returns 1 if voteargs is +
    returns -1 if voteargs is -
    '''
    if voteargs == '%2B':
        return 1
    elif voteargs == '-':
        return -1
    else:
        return 0

def send_newsreporter(request):
    r = Reporter()
    r.get_top_thirty_stories()
    return redirect('/')

def search_posts(request):
    searchq = request.GET.get('searchq', '')
    d_posts = []
    posts = Post.score_sorted.annotate(
        search=SearchVector('title', 'text', 'link', 'comment__text')
    ).filter(search=searchq)
    for post in posts:
        if post not in d_posts:
            d_posts.append(post)
    return render(request, 'post_list.html', {'posts' : d_posts, 'searchq' : searchq})

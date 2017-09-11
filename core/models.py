# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone
import operator

from django_markdown.models import MarkdownField

from django.db import models
from django.contrib.auth.models import User

class PostManager(models.Manager):
    '''
    sorting news using hackernews sorting algoritm
    https://medium.com/hacking-and-gonzo/how-hacker-news-ranking-algorithm-works-1d9b0cf2c08d

    Post.objects.filter().annotate(votes_score=Sum('postvote__vote')).order_by('-votes_score')
    '''
    def calculate_score(self, votes, item_hour_age, gravity=1.8):
        return (votes - 1) / pow((item_hour_age+2), gravity)

    def get_query_set(self):
        return super(PostManager, self).get_query_set().filter() \
                                       .annotate(vote_score=calculate_score(models.Sum('postvote__vote'), 'published_date__hour')) \
                                       .order_by('-vote_score')

class Post(models.Model):
    title = models.CharField(max_length=200)
    user = models.CharField(max_length=150)
    link = models.URLField(max_length=600, blank=True)
    text = models.TextField(blank=True)
    published_date = models.DateTimeField(default=timezone.now)
    score_sorted = PostManager()

    def __unicode__(self):
        return self.title

    def score(self):
        return PostVote.objects.filter(post=self).aggregate(models.Sum('vote'))['vote__sum']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.CharField(max_length=150)
    text = models.TextField(blank=False)
    published_date = models.DateTimeField(default=timezone.now)


class PostVote(models.Model):
    VOTE_CHOICES = (
        (1,     'UPVOTE'),
        (0,     'NOVOTE'),
        (-1,    'DOWNVOTE'),
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField(choices=VOTE_CHOICES)

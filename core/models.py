# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length=200)
    user = models.CharField(max_length=150)
    link = models.URLField(max_length=600, blank=True)
    text = models.TextField(blank=True)
    published_date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return self.title

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

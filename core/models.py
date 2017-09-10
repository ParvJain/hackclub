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

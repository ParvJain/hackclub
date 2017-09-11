from django import template
from core.models import PostVote
from django.contrib.auth.models import User

register = template.Library()

@register.assignment_tag
def has_voted(post, user):
    try:
        return PostVote.objects.get(post=post, user=user)
    except:
        return None

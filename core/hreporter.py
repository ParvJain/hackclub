import json
import requests

from django.contrib.auth.models import User

from .models import Post, PostVote, Comment


class Reporter(object):
    """docstring for Reporter."""
    def __init__(self):
        self.API_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
        self.stories = json.loads(requests.get(self.API_URL).content)

    def story_url(self, story_id):
        return "https://hacker-news.firebaseio.com/v0/item/{}.json".format(story_id)

    def get_top_thirty_stories(self):
        for story in self.stories[:30]:
            story_obj = {}
            story = json.loads(requests.get(self.story_url(self, story)).content)
            story_obj['title'] = story['title']
            story_obj['user'] = story['by']
            story_obj['link'] = story.get('url', '')
            story_obj['text'] = story.get('text', '')
            post, created = Post.score_sorted.get_or_create(**story_obj)
            post.save()
            if len(PostVote.objects.filter(post=post)) == 0:
                u = User.objects.get_or_create(username="hackernews")[0]
                vote = PostVote(post=post, user=u, vote=story['score'])
                vote.save()
            try:
                for comment in story['kids']:
                    comment_obj = {}
                    comment = json.loads(requests.get(self.story_url(self, comment)).content)
                    comment_obj['author'] = comment['by']
                    comment_obj['text'] = comment['text']
                    comment_obj['post'] = post
                    if len(Comment.objects.filter(author=comment_obj['author'],text=comment_obj['text'], post=post)) == 0:
                        c = Comment(**comment_obj)
                        c.save()
            except:
                pass

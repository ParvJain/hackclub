from django import forms
from .models import Post
from django_markdown.fields import MarkdownFormField
from django_markdown.widgets import MarkdownWidget

class PostForm(forms.ModelForm):
    text = forms.CharField(widget=MarkdownWidget(), required=False)
    class Meta:
        model = Post
        fields = ('title','link', 'text')

from django import forms
from blog.models import Blog, CategoryBlog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['category', 'image', 'title', 'content']
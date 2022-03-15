from unicodedata import category
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField('category_name', max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def count_posts_belong_to(self):
        n = Post.objects.filter(category = self).count()
        return n
    
    def __str__(self):
        return self.name
    

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=False)
    title = models.CharField('title', max_length=50)
    content = models.TextField('content')
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    thumbnail = models.ImageField(upload_to='images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    

class Like(models.Model):
    post = models.ForeignKey(Post, verbose_name="Post", on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.PROTECT)
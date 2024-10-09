from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
from users.models import User
from bs4 import BeautifulSoup

class CategoryBlog(models.Model):
    nama = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True, editable=False)
    def __str__(self):
        return self.nama
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    def generate_unique_slug(self):
        slug = slugify(self.nama)
        unique_slug = slug
        number = 1
        while CategoryBlog.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{number}"
            number += 1
        return unique_slug
    
class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(CategoryBlog, on_delete=models.CASCADE, related_name='materis')
    image = models.ImageField(upload_to='Blog', blank=True, null=True)
    title = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, editable=False)
    description =  models.CharField(max_length=203, blank=True, editable=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        self.slug = self.generate_unique_slug()
        self.description = self.generate_description()
        super().save(*args, **kwargs)
    def generate_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        number = 1
        while Blog.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{slug}-{number}"
            number += 1
        return unique_slug
    def generate_description(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        paragraphs = soup.find_all('p')
        text_content = ' '.join([p.get_text() for p in paragraphs])
        if len(text_content) > 197:
            return text_content[:197] + '...'
        return text_content
@receiver(pre_save, sender=CategoryBlog)
def create_unique_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = instance.generate_unique_slug()

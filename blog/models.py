from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField

import uuid


# Create your models here.
class PublishManager(models.Manager):
    def get_queryset(self):
        return super(PublishManager, self).get_queryset().filter(status='published', poster__confirm=True)


class Post(models.Model):
    status_choices = (
        ('draft', 'Drafted'),
        ('published', 'Published'),
        )

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    body = RichTextUploadingField()
    image = models.ImageField(upload_to='realty_post/%Y-%m', blank=True, null=True)

    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=12, choices=status_choices, default='draft')

    view_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)

    objects = models.Manager()
    publishee = PublishManager()

    class Meta:
        ordering = ('-publish',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        post_time = timezone.localtime(self.publish)
        return reverse('blog:detail', args=[self.slug, post_time.year, post_time.month, post_time.day])


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "Comment by {} on {}".format(self.name, self.post)


class Subscriber(models.Model):
    # name = models.CharField(max_length=200)
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
    code = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    subscribe = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('unsubscribe', args=[self.code])


class Poster(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='poster')
    confirm = models.BooleanField(default=False)

    def __str__(self):
        return self.post.title


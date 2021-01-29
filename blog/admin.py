from django.contrib import admin
from .models import Post, Comment, Subscriber, Poster


# Register your models here.
class PosterInline(admin.TabularInline):
    model = Poster


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'status')
    list_filter = ('author', 'status', 'publish', 'created')
    list_editable = ('status',)
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish'
    autocomplete_fields = ('author',)
    inlines = [PosterInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created')
    search_fields = ('name', 'email', 'body', 'post__title')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created', 'subscribe')
    list_filter = ('subscribe',)
    search_fields = ('email',)

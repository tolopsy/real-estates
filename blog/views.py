from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from .models import Post
from .forms import CommentForm, SubscriberForm


# handles newsletter subscription
def subscribe(request):
    subscriber = SubscriberForm(request.POST or None)
    if subscriber.is_valid:
        subscriber.save()
        return "You have successfully subscribed to our newsletter. Thank you."


def blog_list(request):
    post = Post.publishee.all().order_by('-publish')
    paginator = Paginator(post, 3)
    blog_page = request.GET.get('page')
    subscribe_alert = None
    try:
        pager = paginator.page(blog_page)
    except PageNotAnInteger:
        pager = paginator.page(1)
    except EmptyPage:
        pager = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        if 'subscribe' in request.POST:
            subscribe_alert = subscribe(request)

    context = {
        'posts': pager,
        'subscribe_alert': subscribe_alert,
    }

    return render(request, 'blog.html', context)


def blog_detail(request, post_slug, year, month, day):
    post = get_object_or_404(Post, slug=post_slug, status='published', publish__year=year, publish__month=month,
                             publish__day=day)
    post.view_count += 1
    post.save()

    comment_list = post.comments.filter(active=True)

    new_comment = None
    subscribe_alert = None

    if request.method == 'POST':
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST or None)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                post.comment_count += 1
                post.save()
                new_comment.post = post
                new_comment.save()
            else:
                print('error somewhere')
        elif 'subscribe' in request.POST:
            subscribe_alert = subscribe(request)

    context = {
        'post': post,
        'comments': comment_list,
        'new_comment': new_comment,
        'subscribe_alert': subscribe_alert,
    }
    return render(request, 'post.html', context)

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from yatube.settings import POSTS_ON_PAGE


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    username = get_object_or_404(User, username=username)
    post_list = username.posts.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = True
    if request.user.is_authenticated:
        follower = request.user.follower.all()
        try:
            follower.get(user=request.user, author=username)
        except ObjectDoesNotExist:
            following = False
    context = {
        'username': username,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    page_obj = get_object_or_404(Post, id=post_id)
    comments = page_obj.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'page_obj': page_obj,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'POST':
        if form.is_valid():
            author = request.user
            form = form.save(commit=False)
            form.author_id = author.id
            form.save()
            return redirect('posts:profile', username=author)

    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(request, template, {'form': form})

    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(
        request.POST or None,
    )
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    username = get_object_or_404(User, username=request.user)
    followers = []
    for follower in username.follower.all():
        followers.append(follower.author)
    post_list = Post.objects.filter(author__in=followers)
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    username = get_object_or_404(User, username=username)
    follower = request.user.follower.all()
    try:
        follower.get(user=request.user, author=username)
    except ObjectDoesNotExist:
        if request.user != username:
            follow = Follow()
            follow.user = request.user
            follow.author = username
            follow.save()
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    username = get_object_or_404(User, username=username)
    try:
        following = request.user.follower.get(
            user=request.user,
            author=username
        )
        following.delete()
    except ObjectDoesNotExist:
        pass
    return redirect('posts:follow_index')

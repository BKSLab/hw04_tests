from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from posts.forms import PostForm
from posts.models import Group, Post
from yatube.utils import paginate

User = get_user_model()


def index(request: object) -> Post:
    posts = Post.objects.all()
    page = paginate(request, posts)
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': page,
        },
    )


def group_posts(request: object, slug: str) -> Group:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').all()
    page = paginate(request, posts)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': page,
        },
    )


def profile(request: Any, username: Any) -> Any:
    user_name = get_object_or_404(User, username=username)
    posts = user_name.posts.all()
    page = paginate(request, posts)
    return render(
        request,
        'posts/profile.html',
        {
            'page_obj': page,
            'user_name': user_name,
        },
    )


def post_detail(request: Any, pk: Any) -> Any:
    post = get_object_or_404(Post, pk=pk)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
        },
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {
                'form': form,
            },
        )
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:
        return redirect('posts:post_detail', pk)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk)
    return render(
        request,
        'posts/create_post.html',
        {
            'is_edit': True,
            'post': post,
            'form': form,
        },
    )

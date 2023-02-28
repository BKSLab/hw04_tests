from django.urls import path

from posts.views import (
    group_posts,
    index,
    post_create,
    post_detail,
    post_edit,
    profile,
)

app_name = '%(posts_label)s'

urlpatterns = [
    path('', index, name='h_page'),
    path('create/', post_create, name='post_create'),
    path('group/<slug:slug>/', group_posts, name='page_post'),
    path('posts/<int:pk>/', post_detail, name='post_detail'),
    path('posts/<int:pk>/edit/', post_edit, name='post_edit'),
    path('profile/<str:username>/', profile, name='profile'),
]

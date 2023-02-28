from django.contrib import admin
from django.urls import include, path

from about.apps import AboutConfig
from posts.apps import PostsConfig
from users.apps import UsersConfig

urlpatterns = [
    path('', include('posts.urls', PostsConfig.name)),
    path('about/', include('about.urls', AboutConfig.name)),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', UsersConfig.name)),
    path('auth/', include('django.contrib.auth.urls')),
]

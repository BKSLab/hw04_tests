from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_author = User.objects.create_user(username='author_post')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user_author)

    def test_create_post_form(self):
        """Валидная форма создает запись в Post."""
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        data = {
            'text': 'Тестовый пост',
            'group': group.pk,
            'author': self.user_author,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user_author}),
        )
        self.assertTrue(Post.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_form(self):
        """Форма при редактирование поста изменяет существующий пост."""
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый пост',
            group=group,
        )
        group_two = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-two',
            description='Тестовое описание 2',
        )
        data = {
            'author': self.user_author,
            'text': 'Тестовый пост, измененный',
            'group': group_two.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=data,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'pk': post.pk})
        )
        self.assertTrue(Post.objects.filter(text=data['text']))
        self.assertTrue(Post.objects.filter(group=data['group']))

    def test_create_post_by_unauthorized_user(self):
        """Неавторизованный пользователь не может создать пост."""
        data = {
            'text': 'Тестовый пост',
            'author': self.user_author,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=data,
            follow=True,
        )
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertFalse(Post.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_by_unauthorized_user(self):
        """Неавторизованный пользователь не может редактировать пост."""
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый пост',
        )
        data = {
            'author': self.user_author,
            'text': 'Тестовый пост, измененный',
        }
        response = self.client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=data,
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{post.pk}/edit/'
        )
        self.assertFalse(Post.objects.filter(text=data['text']))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_by_non_author(self):
        """Не автор поста не может редактировать пост."""
        post = Post.objects.create(
            author=self.user_author,
            text='Тестовый пост',
        )
        data = {
            'author': User.objects.create_user(username='Mask'),
            'text': 'Тестовый пост, измененный',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'pk': post.pk}),
            data=data,
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'pk': post.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

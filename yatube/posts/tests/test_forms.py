from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='author_post')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

        cls.form = PostForm

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_create_post_form(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.pk,
            "author": self.user_author,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={"username": self.user_author}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(response.status_code, 200)

    def test_edit_post_form(self):
        """Форма при редактирование поста изменяет существующий пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост, измененный',
            'group': self.group.pk,
            "author": self.user_author,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={"pk": self.post.pk}),
            data=form_data,
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={"pk": self.post.pk})
        )
        self.assertTrue(Post.objects.filter(text=form_data['text']))

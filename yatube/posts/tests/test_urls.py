from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_guest = User.objects.create_user(username='NoName')
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

        cls.templates_url_names = {
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            '/': 'posts/index.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
            f'/profile/{cls.user_guest}/': 'posts/profile.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_urls_uses_authorized_client_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон
        для зарегистрированного пользователя.
        """

        for address_url, template in self.templates_url_names.items():
            with self.subTest(address_url=address_url):
                response = self.authorized_client.get(address_url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(
                    response.status_code,
                    200,
                    f'страница {address_url} недоступна',
                )

    def test_create_page(self):
        """Страница '/create/' не доступна неавторизованному пользователю."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_non_existent_page(self):
        """Тест несуществующей страницы"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

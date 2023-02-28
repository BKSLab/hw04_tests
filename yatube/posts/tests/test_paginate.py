from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


NUMBER_TEST_POSTS = 13


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.new_user_author = User.objects.create_user(username='author_post')
        cls.group_test_paginate = Group.objects.create(
            title='Тестовая группа pag',
            slug='test-slug-pag',
            description='Тестовое описание pag',
        )
        cls.post = []
        for i in range(NUMBER_TEST_POSTS):
            cls.post.append(
                Post.objects.create(
                    author=cls.new_user_author,
                    text=f'Тестовый пост {i}',
                    group=cls.group_test_paginate,
                )
            )

        cls.reverse_names_paginate = {
            reverse(
                'posts:page_post',
                kwargs={"slug": cls.group_test_paginate.slug},
            ),
            reverse('posts:h_page'),
            reverse('posts:profile', kwargs={"username": cls.new_user_author}),
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.new_user_author)

    def test_first_and_second_pages_paginate(self):
        """
        Постраничный вывод постов на главной странице, странице группы
        и на странице профиля.
        """
        for reverse_name in self.reverse_names_paginate:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.OBJECTS_PER_PAGE,
                )
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    NUMBER_TEST_POSTS - settings.OBJECTS_PER_PAGE,
                )

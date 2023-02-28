from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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

        cls.templates_pages_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={"pk": cls.post.pk}
            ): 'posts/create_post.html',
            reverse(
                'posts:page_post', kwargs={"slug": cls.group.slug}
            ): 'posts/group_list.html',
            reverse('posts:h_page'): 'posts/index.html',
            reverse(
                'posts:post_detail', kwargs={"pk": cls.post.pk}
            ): 'posts/post_detail.html',
            reverse(
                'posts:profile', kwargs={"username": cls.user_author}
            ): 'posts/profile.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_correct_contecst(self):
        """В шаблон index.html передается правильный контекст"""

        response = self.authorized_client.get(reverse('posts:h_page'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.pub_date, self.post.pub_date)
        self.assertEqual(first_object.author, self.post.author)
        self.assertEqual(first_object.group, self.post.group)

    def test_group_list_page_correct_contecst(self):
        """В шаблон group_list.html передается правильный контекст"""

        response = self.authorized_client.get(
            reverse('posts:page_post', kwargs={"slug": self.group.slug})
        )
        first_object = response.context['group']
        self.assertEqual(first_object.title, self.group.title)
        self.assertEqual(first_object.slug, self.group.slug)
        self.assertEqual(first_object.description, self.group.description)

    def test_profile_page_correct_contecst(self):
        """В шаблон profile.html передается правильный контекст"""

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={"username": self.user_author})
        )
        first_object = response.context['user_name']
        self.assertEqual(first_object, self.user_author)

    def test_post_detail_page_correct_contecst(self):
        """В шаблон post_detail.html передается правильный контекст"""

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={"pk": self.post.pk})
        )
        first_object = response.context['post']
        self.assertEqual(first_object.pk, self.post.pk)

    def test_create_post_correct_context(self):
        """
        В шаблон create_post.html передается правильный контекст
        при созздании поста.
        """

        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_correct_context(self):
        """
        В шаблон create_post.html передается правильный контекст
        при редактирование поста.
        """

        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={"pk": self.post.pk})
        )
        first_object = response.context['post']
        self.assertEqual(first_object.pk, self.post.pk)

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class GroupPostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_from_group = User.objects.create_user(
            username='author_post_with_group'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author_from_group,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author_from_group)

    def test_show_post_with_group_on_index_page(self):
        """Пост с группой показывается на главной странице"""

        response = self.authorized_client.get(reverse('posts:h_page'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group, self.post.group)

    def test_show_post_with_group_on_group_list_page(self):
        """Пост с группой показывается на странице выбранной группы"""

        response = self.authorized_client.get(
            reverse('posts:page_post', kwargs={"slug": self.group.slug})
        )
        posts_of_group = list(self.group.posts.all())
        self.assertEqual(list(response.context['page_obj']), posts_of_group)

    def test_show_post_with_group_on_profile_page(self):
        """Пост с группой показывается на странице профайла пользователя"""

        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={"username": self.author_from_group}
            )
        )
        posts_of_group = list(self.author_from_group.posts.all())
        self.assertEqual(list(response.context['page_obj']), posts_of_group)

    def test_do_not_show_post_with_group_on_another_group_page(self):
        """Не попал ли пост в группу, к которой он не относится"""
        another_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-two',
            description='Тестовое описание 2',
        )
        self.assertNotEqual(self.post.group, another_group)

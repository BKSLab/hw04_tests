from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Group(models.Model):
    title = models.CharField('название группы', max_length=200)
    slug = models.SlugField('уникальный адрес группы', unique=True)
    description = models.TextField('описание группы')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'

    def __str__(self) -> str:
        return self.title[: settings.SHOW_WORDS]


class Post(models.Model):
    text = models.TextField('текст поста')
    pub_date = models.DateTimeField(
        'дата и время публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
    )

    class Meta:
        verbose_name = 'пост'
        verbose_name_plural = 'посты'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.text[: settings.SHOW_WORDS]

    def get_absolute_url(self) -> str:
        return reverse("posts:post_detail", kwargs={"pk": self.pk})

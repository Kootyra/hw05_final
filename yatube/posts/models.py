from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
CHARS_IN_RETURN_POST: int = 15


class Group(models.Model):
    title = models.CharField(verbose_name='Название группы',
                             max_length=200,
                             help_text='Введите название группы')
    slug = models.SlugField(verbose_name='Адрес для ссылки',
                            max_length=15,
                            unique=True,
                            help_text='Уникальный адрес')
    description = models.TextField(verbose_name='Описание группы',
                                   help_text='Введите описание сообщества')

    def __str__(self):
        return f"Группа {self.title}"


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Здесь будет Ваш пост')
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True)
    author = models.ForeignKey(
        User,
        verbose_name='Автор поста',
        help_text='Укажите автора',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        help_text='Выберите группу (необязательно)',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        help_text='Загрузите картинку (необязательно)',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:CHARS_IN_RETURN_POST]

    class Meta:
        ordering = ('-pub_date',)


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        help_text='Укажите автора',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Здесь будет Ваш комментарий')
    created = models.DateTimeField(verbose_name='Дата комментария',
                                   auto_now_add=True)


class Follow(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='follower'
    )

import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post
from ..utils import PAGES_FOR_PAGINATOR

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='noauth')
        cls.author = User.objects.create_user(username='author')
        cls.follower = User.objects.create_user(username='follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group1',
            description='Тестовое описание',
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='group2',
            description='Тестовое описание2',
        )
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )

        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        for i in range(PAGES_FOR_PAGINATOR):
            cls.post = Post.objects.create(
                author=cls.user2,
                text=f'Тестовый пост №{i} другая группа и автор',
                group=cls.group2,
            )
        count_posts = PAGES_FOR_PAGINATOR + 1
        while count_posts != 0:
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост №{count_posts}- про тестирование!!!',
                group=cls.group,
                image=uploaded,
            )
            count_posts -= 1

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='OneUs')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.get(username='auth')
        self.author = Client()
        self.author.force_login(self.user2)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

    def test_pages_uses_correct_template(self):
        '''Проверяем корректность использования шаблонов'''
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:universal',
                                             kwargs={'slug': 'group1'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'auth'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={'post_id': '1'}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_author(self):
        '''Проверяем корректность использования шаблонов для автора поста'''
        response = self.author.get(reverse('posts:post_edit',
                                           kwargs={'post_id':
                                                   PAGES_FOR_PAGINATOR + 1}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_paginator(self):
        '''Проверяем паджинатор'''
        count_pages = {
            reverse('posts:index'): PAGES_FOR_PAGINATOR,
            reverse('posts:index') + '?page=3': 1,
            reverse('posts:universal',
                    kwargs={'slug': 'group1'}): PAGES_FOR_PAGINATOR,
            reverse('posts:universal',
                    kwargs={'slug': 'group1'}) + '?page=2': 1,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}): PAGES_FOR_PAGINATOR,
            reverse('posts:profile',
                    kwargs={'username': 'auth'}) + '?page=2': 1,
        }
        for reverse_name, count_page in count_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), count_page)

    def test_index_show_correct_context(self):
        '''Проверяем контекст главной страницы'''
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        '''post_image_0 = first_object.image'''
        self.assertEqual(post_text_0, 'Тестовый пост №1- про тестирование!!!')
        self.assertEqual(post_author_0, 'auth')
        self.assertEqual(post_group_0, 'Тестовая группа')
        '''self.assertEqual(post_image_0, 'posts/small.gif')'''

    def test_group_show_correct_context(self):
        '''Проверяем контекст страницы группы'''
        response = self.authorized_client.get(reverse('posts:universal',
                                              kwargs={'slug': 'group1'}))

        for i in range(PAGES_FOR_PAGINATOR):
            objects = response.context['page_obj'][i]
            post_group = objects.group.title
            self.assertEqual(post_group, 'Тестовая группа')

    def test_profile_show_correct_context(self):
        '''Проверяем контекст страницы автора'''
        response = self.authorized_client.get(reverse('posts:profile',
                                              kwargs={'username': 'noauth'}))

        for i in range(PAGES_FOR_PAGINATOR):
            objects = response.context['page_obj'][i]
            post_author = objects.author.username
            self.assertEqual(post_author, 'noauth')

    def test_post_show_correct_context(self):
        '''Проверяем контекст страницы группы'''
        response = self.authorized_client.get(reverse('posts:post_detail',
                                              kwargs={'post_id': '7'}))
        objects = response.context['post']
        post_text = objects.text
        self.assertEqual(post_text, 'Тестовый пост №6 другая группа и автор')

    def test_create_post_show_correct_context(self):
        '''Проверяем контекст при создании поста'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        '''Проверяем контекст при редактировании поста'''
        response = self.author.get(reverse('posts:post_edit',
                                   kwargs={'post_id':
                                           PAGES_FOR_PAGINATOR + 1}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_authorized_client_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей."""
        self.follower_client.get(reverse('posts:profile_follow',
                                 kwargs={'username': self.user}
                                         ))
        self.assertTrue(Follow.objects.filter(
                        user=self.follower,
                        author=self.user
                        ).exists())

    def test_authorized_client_unfollow(self):
        """Авторизованный пользователь может отписываться от других
        пользователей."""
        Follow.objects.create(author=self.user,
                              user=self.follower,
                              )
        self.follower_client.get(reverse('posts:profile_unfollow',
                                 kwargs={'username': self.user}
                                         ))
        self.assertFalse(Follow.objects.filter(
                         user=self.follower,
                         author=self.user
                         ).exists())

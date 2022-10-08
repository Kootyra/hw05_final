from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='OneUs')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - про тестирование и многое много едругое',
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.get(username='OneUs')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текстовый текст',
            'group': '',

        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'OneUs'}))
        self.assertTrue(
            Post.objects.filter(
                text='Текстовый текст'
            ).exists()
        )


class PostEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='OneUs')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - про тестирование и многое много едругое',
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.get(username='OneUs')
        self.author = Client()
        self.author.force_login(self.user)

    def test_edit_post(self):
        """Валидная форма редактирует пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текстовый текст после изменения',
            'group': '',

        }
        response = self.author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.pk}))
        self.assertTrue(
            Post.objects.filter(
                text='Текстовый текст после изменения'
            ).exists()
        )

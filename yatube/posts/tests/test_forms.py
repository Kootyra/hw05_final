import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост - про тестирование и многое много едругое',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
            'image': (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                      b'\x01\x00\x80\x00\x00\x00\x00\x00'
                      b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                      b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                      b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                      b'\x0A\x00\x3B'
                      )


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

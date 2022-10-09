from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User

User = get_user_model()


class PostUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='OneUs')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.user2 = User.objects.get(username='auth')
        self.author = Client()
        self.author.force_login(self.user2)

    def test_urls_guest(self):
        '''Проверяем ответы страниц'''
        url = {
            '/': 'OK',
            f'/group/{self.group.slug}/': 'OK',
            f'/profile/{self.user.username}/': 'OK',
            f'/posts/{self.post.pk}/': 'OK',
            '/nopage/': 'Not Found',
            f'/posts/{self.post.pk}/edit/': 'Found',
            '/create/': 'Found',
        }
        for address, status in url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.reason_phrase, status)

    def test_create_url_exists_at_desired_location_authorized(self):
        '''Проверяем ответ страницы create'''
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.reason_phrase, 'OK')

    def test_edit_url_exists_at_desired_location_author(self):
        '''Проверяем ответ страницы edit для автора'''
        response = self.author.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.reason_phrase, 'OK')

    def test_edit_list_url_redirect_authorized(self):
        '''Проверяем ответ страницы edit для авторизованного пользователя'''
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/',
                                              follow=True)
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_urls_uses_correct_template(self):
        '''Проверяем какие шаблоны подтягиваются на страницы'''
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_update_post_template(self):
        '''Проверяем шаблон страницы редактирования для автора'''
        response = self.author.get(f'/posts/{self.post.pk}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_show_in_followers_feed(self):
        """Новая запись пользователя появляется
        в ленте тех, кто на него подписан"""
        new_post = Post.objects.create(
            author=self.author,
            text='New Post',
        )
        self.follower_client.force_login(self.follower)
        response = self.follower_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj']
        self.assertIn(new_post, posts, 'Поста нет')

    def test_post_now_show_in_unfollowers_feed(self):
        """Новая запись пользователя не появляется
        в ленте тех, кто не подписан."""
        new_post = Post.objects.create(
            author=self.author,
            text='New Post',
        )
        self.follower_client.force_login(self.user)
        response = self.follower_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj']
        self.assertNotIn(new_post, posts, 'Пост есть')

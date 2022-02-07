from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, Client

from .models import Post, Group, Follow, Comment


class BaseTest(TestCase):

    def setUp(self) -> None:
        cache.clear()
        self.client = Client()
        self.user = User.objects.create(username='test_user',
                                        email='test@email.com')
        self.user.set_password('test_password')
        self.user.save()
        self.text = 'Test text'
        self.group = Group.objects.create(title='Test group',
                                          slug='test')

    def tearDown(self) -> None:
        User.objects.filter(username=self.user.username).delete()
        Post.objects.filter(author=self.user).delete()
        Group.objects.filter(pk=self.group.pk).delete()

    def test_profile_exists(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_auth_post(self):
        self.client.login(username=self.user.username,
                          password='test_password')
        self.client.post('/new/', data={'text': self.text})
        self.assertTrue(Post.objects.filter(text=self.text).exists())

    def test_anon_post(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/')

    def test_post_exists(self):
        post = Post.objects.create(text=self.text,
                                   author=self.user)
        username = self.user.username
        post_id = f'{post.id}'
        responses = [self.client.get('/'),
                     self.client.get(f'/{username}/'),
                     self.client.get(f'/{username}/{post_id}/')]
        for response in responses:
            self.assertContains(response, text=self.text)

    def test_edited_post_exists(self):
        self.client.login(username=self.user.username,
                          password='test_password')
        post = Post.objects.create(text=self.text,
                                   author=self.user)
        username = self.user.username
        post_id = f'{post.id}'
        edited_text = 'New test text'
        self.client.post(f'/{username}/{post_id}/edit/',
                         data={'text': edited_text})
        responses = [self.client.get('/'),
                     self.client.get(f'/{username}/'),
                     self.client.get(f'/{username}/{post_id}/')]
        for response in responses:
            self.assertContains(response, text=edited_text)

    def test_404(self):
        response = self.client.get('/345/')
        self.assertEqual(response.status_code, 404)

    def test_image_exists(self):
        self.client.login(username=self.user.username,
                          password='test_password')
        with open('test_img/3030.jpg', 'rb') as img:
            self.client.post("/new/",
                             {'text': self.text, 'image': img,
                              'group': self.group.pk})
            post = Post.objects.get(group=self.group)
            username = self.user.username
            slug = self.group.slug
            responses = [self.client.get(f"/"),
                         self.client.get(f"/{username}/"),
                         self.client.get(f"/{username}/{post.id}/"),
                         self.client.get(f"/group/{slug}/")]
            for response in responses:
                self.assertContains(response, 'img')

    def test_non_img_format(self):
        self.client.login(username=self.user.username,
                          password='test_password')
        with open('test_img/test.txt', 'rb') as img:
            response = self.client.post("/new/",
                                        {'text': self.text, 'image': img})
            self.assertTrue(response.context['form'].has_error('image'))

    def test_follow_unfollow(self):
        self.client.login(username=self.user.username,
                          password='test_password')


class CacheTest(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create(username='test_user',
                                        email='test@email.com')
        self.user.set_password('test_password')
        self.user.save()
        self.text = 'Test text'

    def tearDown(self) -> None:
        User.objects.filter(username=self.user.username).delete()
        Post.objects.filter(author=self.user).delete()

    def test_index_cache(self):
        Post.objects.create(text=self.text,
                            author=self.user)
        response = self.client.get('/')
        self.assertContains(response, self.text)
        Post.objects.create(text='Text for cache',
                            author=self.user)
        response = self.client.get('/')
        self.assertNotContains(response, 'Text for cache')


class FollowTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = User.objects.create(username='test_user',
                                        email='test@email.com')
        self.user.set_password('test_password')
        self.user.save()
        self.user_2 = User.objects.create(username='test_user_2',
                                          email='test_2@email.com')
        self.user_2.set_password('test_password_2')
        self.user_2.save()
        self.text = 'Test text'

    def tearDown(self) -> None:
        User.objects.filter(username=self.user.username).delete()
        User.objects.filter(username=self.user_2.username).delete()
        Post.objects.filter(author=self.user).delete()
        Post.objects.filter(author=self.user_2).delete()
        Comment.objects.filter(author=self.user).delete()

    def test_follow_unfollow(self):
        self.client.login(username=self.user.username,
                          password='test_password')
        username = self.user_2.username
        self.client.get(f'/{username}/follow/')
        follower = Follow.objects.filter(user=self.user, author=self.user_2)\
            .exists()
        self.assertTrue(follower)
        self.client.get(f'/{username}/unfollow/')
        follower = Follow.objects.filter(user=self.user, author=self.user_2)\
            .exists()
        self.assertFalse(follower)

    def test_following_post(self):
        self.client.login(username=self.user.username,
                          password='test_password')
        username = self.user_2.username
        self.client.get(f'/{username}/follow/')
        Post.objects.create(text=self.text, author=self.user_2)
        response = self.client.get(f'/follow/')
        self.assertContains(response, text=self.text)
        self.client.get(f'/{username}/unfollow/')
        response = self.client.get(f'/follow/')
        self.assertNotContains(response, text=self.text)

    def test_comment(self):
        self.client.login(username=self.user.username,
                          password='test_password')
        self.client.post('/new/', data={'text': self.text})
        post = Post.objects.get(author=self.user, text=self.text)
        username = self.user.username
        self.client.post(f'/{username}/{post.id}/comment',
                         data={'text': 'Test comment'})
        comment = Comment.objects.filter(text='Test comment').exists()
        self.assertTrue(comment)

        Comment.objects.filter(text='Test comment').delete()
        self.client.logout()
        self.client.post(f'/{username}/{post.id}/comment',
                         data={'text': 'Test comment'})
        comment = Comment.objects.filter(text='Test comment').exists()
        self.assertFalse(comment)





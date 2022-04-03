import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User

AUTHOR = 'auth'
GIF = (
    b'\x47\x49\x46\x38\x39\x61\x01\x00'
    b'\x01\x00\x00\x00\x00\x21\xf9\x04'
    b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
    b'\x00\x00\x01\x00\x01\x00\x00\x02'
    b'\x02\x4c\x01\x00\x3b'
)
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-slug'
GROUP_TITLE = 'Тестовая группа'
NAME_FILE = 'small.gif'
POST_ID = '1'
POST_IMAGE = 'posts/' + NAME_FILE
POST_TEXT = 'Тестовая пост'
POST_TEXT_EDITED = 'Редактированный Тестовый текст'
REVERSE_POST_CREATE = reverse('posts:post_create')
REVERSE_POST_EDIT = reverse('posts:post_edit', args=(POST_ID,))
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
UPLOADED = SimpleUploadedFile(
    name=NAME_FILE,
    content=GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.form = PostForm()
        cls.reverse_profile = reverse('posts:profile', args=(cls.author,))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_edit(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
        }
        response = self.authorized_client.post(
            REVERSE_POST_CREATE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.reverse_profile
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT,
            ).latest('pk')
        )

        form_data = {
            'text': POST_TEXT_EDITED,
        }
        post_id = Post.objects.latest('pk').id
        reverse_post_edit = reverse('posts:post_edit', args=(post_id,))
        reverse_post_detail = reverse('posts:post_detail', args=(post_id,))
        response = self.authorized_client.post(
            reverse_post_edit,
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse_post_detail
        )

        posts_count = Post.objects.count()
        form_data = {
            'text': POST_TEXT,
            'image': UPLOADED,
        }
        response = self.authorized_client.post(
            REVERSE_POST_CREATE,
            data=form_data,
            follow=True
        )

        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=POST_TEXT,
                image=POST_IMAGE,
            ).latest('pk')
        )

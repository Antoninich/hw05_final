import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

AUTHOR = 'auth'
CONTEXT = 'page_obj'
FORM_FIELDS = {
    'text': forms.fields.CharField,
    'group': forms.models.ModelChoiceField,
}
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
GROUP_ANOTHER_DESCRIPTION = 'Другое тестовое описание'
GROUP_ANOTHER_SLUG = 'another-slug'
GROUP_ANOTHER_TITLE = 'Другая группа'
NAME_FILE = 'small.gif'
NOT_AUTHOR = 'not_author'
NOT_AUTHORS_FOLLOWER = 'not_authors_follower'
POST_IMAGE = 'posts/' + NAME_FILE
POST_TEXT = 'Тестовая пост'
POST_TEXT_FIRST = 'Тестовый пост другой группы'
REVERSE_FOLLOW_INDEX = reverse('posts:follow_index')
REVERSE_INDEX = reverse('posts:index')
REVERSE_POST_CREATE = reverse('posts:post_create')
TEMPLATES_INDEX = 'posts/index.html'
TEMPLATES_GROUP = 'posts/group_list.html'
TEMPLATES_POST_CREATE = 'posts/create_post.html'
TEMPLATES_POST_DETAIL = 'posts/post_detail.html'
TEMPLATES_PROFILE = 'posts/profile.html'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
UPLOADED = SimpleUploadedFile(
    name=NAME_FILE,
    content=GIF,
    content_type='image/gif'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.not_author = User.objects.create_user(username=NOT_AUTHOR)
        cls.not_authors_follower = User.objects.create_user(
            username=NOT_AUTHORS_FOLLOWER
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.another_group = Group.objects.create(
            title=GROUP_ANOTHER_TITLE,
            slug=GROUP_ANOTHER_SLUG,
            description=GROUP_ANOTHER_DESCRIPTION,
        )
        cls.first_post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT_FIRST,
            group=cls.another_group,
            image=UPLOADED,
        )
        for i in range(13):
            cls.last_post = Post.objects.create(
                author=cls.author,
                text=f'{POST_TEXT} {i}',
                group=cls.group,
            )
        cls.reverse_profile = reverse('posts:profile', args=(cls.author,))
        cls.reverse_profile_follow = reverse(
            'posts:profile_follow',
            args=(cls.author,)
        )
        cls.reverse_profile_unfollow = reverse(
            'posts:profile_unfollow',
            args=(cls.author,)
        )
        cls.reverse_group = reverse(
            'posts:group_list',
            kwargs={'slug': cls.group.slug}
        )
        cls.reverse_anouther_group = reverse(
            'posts:group_list',
            kwargs={'slug': cls.another_group.slug}
        )
        cls.post_detail = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.last_post.id}
        )
        cls.post_edit = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.last_post.id}
        )
        cls.pages_with_paginator = {
            REVERSE_INDEX: TEMPLATES_INDEX,
            cls.reverse_group: TEMPLATES_GROUP,
            cls.reverse_profile: TEMPLATES_PROFILE,
        }
        cls.page_post_detail = {
            cls.post_detail: TEMPLATES_POST_DETAIL,
        }
        cls.pages_without_paginator = {
            cls.post_edit: TEMPLATES_POST_CREATE,
            REVERSE_POST_CREATE: TEMPLATES_POST_CREATE,
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(self.not_author)
        self.authorized_not_authors_follower_client = Client()
        self.authorized_not_authors_follower_client.force_login(
            self.not_authors_follower
        )
        cache.clear()

    def test_templates(self):
        pages_templates = {
            **self.pages_with_paginator,
            **self.page_post_detail,
            **self.pages_without_paginator
        }
        for reverse_name, template in pages_templates.items():
            with self.subTest(page=reverse_name, template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_with_paginator(self):
        pages = (
            *self.pages_with_paginator.keys(),
            *self.page_post_detail.keys(),
        )
        for reverse_name in pages:
            with self.subTest(page=reverse_name):
                response = self.client.get(reverse_name)
                try:
                    first_object = response.context[CONTEXT][0]
                except TypeError:
                    first_object = response.context[CONTEXT]
                post_author_0 = first_object.author
                post_text_0 = first_object.text
                post_group_0 = first_object.group
                self.assertEqual(post_author_0, self.author)
                self.assertEqual(post_text_0, self.last_post.text)
                self.assertEqual(post_group_0, self.group)

    def test_paginator(self):
        for reverse_name in self.pages_with_paginator.keys():
            with self.subTest(page=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context[CONTEXT]), 10)
                response = self.client.get((reverse_name) + '?page=2')
                if reverse_name == self.reverse_group:
                    last_objects = 3
                else:
                    last_objects = 4

                self.assertEqual(
                    len(response.context[CONTEXT]),
                    last_objects
                )

    def test_context_without_paginator(self):
        for reverse_name in self.pages_without_paginator.keys():
            response = self.authorized_client.get(reverse_name)
            first_context = response.context['form']
            try:
                second_context = response.context['is_edit']
            except KeyError:
                second_context = True

            for value, expected in FORM_FIELDS.items():
                with self.subTest(value=value, page=reverse_name):
                    form_field = first_context.fields[value]
                    self.assertIsInstance(form_field, expected)
                    self.assertEqual(second_context, True)

    def test_post_with_another_group(self):
        reverse_name = self.reverse_anouther_group
        response = self.authorized_client.get(reverse_name)
        first_object = response.context[CONTEXT][0]
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertNotEqual(post_group_0, self.group)
        self.assertEqual(post_image_0, POST_IMAGE)

    def test_cache(self):
        response_before_delete = self.client.get(REVERSE_INDEX)
        Post.objects.latest('pk').delete()
        response_after_delete = self.client.get(REVERSE_INDEX)
        self.assertEqual(
            response_before_delete.content,
            response_after_delete.content
        )

    def test_subscribe_unsubscribe(self):
        follower = self.not_author.follower
        followers_before_subscribe = follower.count()
        self.authorized_not_author_client.get(self.reverse_profile_follow)
        followers_after_subscribe = follower.count()
        self.assertNotEqual(
            followers_before_subscribe,
            followers_after_subscribe
        )

        new_post = Post.objects.create(
            author=self.author,
            text=POST_TEXT_FIRST,
        )
        response = self.authorized_not_author_client.get(REVERSE_FOLLOW_INDEX)
        response_last_id = response.context[CONTEXT][0].pk
        self.assertEqual(
            new_post.pk,
            response_last_id,
        )
        response = self.authorized_not_authors_follower_client.get(
            REVERSE_FOLLOW_INDEX
        )
        with self.assertRaises(IndexError):
            response_last_id = response.context[CONTEXT][0].pk

        self.authorized_not_author_client.get(self.reverse_profile_unfollow)
        followers_after_unsubscribe = follower.count()
        self.assertNotEqual(
            followers_after_subscribe,
            followers_after_unsubscribe
        )

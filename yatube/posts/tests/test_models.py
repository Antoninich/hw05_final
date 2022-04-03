from django.test import TestCase

from posts.models import Group, Post, User

AUTHOR = 'auth'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-slug'
GROUP_TITLE = 'Тестовая группа'
POST_ID = '1'
POST_TEXT = 'Тестовая пост'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text=POST_TEXT,
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        model_object = {
            self.post: self.post.text[:15],
            self.group: self.group.title,
        }
        for model, object in model_object.items():
            with self.subTest(model=model):
                self.assertEqual(object, str(model))

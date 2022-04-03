from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User

AUTHOR = 'auth'
COMMENT_TEXT = 'Комментарий'
GROUP_DESCRIPTION = 'Тестовое описание'
GROUP_SLUG = 'test-slug'
GROUP_TITLE = 'Тестовая группа'
NOT_AUTHOR = 'not_author'
POST_ID = '1'
POST_TEXT = 'Тестовая пост'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.not_author = User.objects.create_user(username=NOT_AUTHOR)
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
        cls.comment = Comment.objects.create(
            author=cls.author,
            text=COMMENT_TEXT,
            post_id=POST_ID
        )
        cls.follow = Follow.objects.create(
            user=cls.not_author,
            author=cls.author
        )

    def test_models_have_correct_object_names(self):
        follow_str = f'{self.not_author} {self.author}'
        model_object = {
            self.post: self.post.text[:15],
            self.group: self.group.title,
            self.comment: self.comment.text[:15],
            self.follow: follow_str,
        }
        for model, object in model_object.items():
            with self.subTest(model=model):
                self.assertEqual(object, str(model))

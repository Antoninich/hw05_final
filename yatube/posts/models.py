from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint, Q, F

from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Текст нового поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='groups',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    comment = models.ForeignKey(
        'Comment',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='comments',
        verbose_name='Комментарий',
        help_text='Комментарий, который будет относиться к посту'

    )

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        'Заголовок',
        max_length=200
    )
    slug = models.SlugField(
        'Метка',
        unique=True
    )
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Пост, к которому относится комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
        help_text='Автор комментария'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Текст нового комментария'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь, который подписывается',
        help_text='Пользователь, который подписывается'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь, на которого подписываются',
        help_text='Пользователь, на которого подписываются'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='Вы уже подписаны на этого автора.'
            ),
            CheckConstraint(
                check=~Q(user=F('author')),
                name='Нельзя подписываться на себя.',
            ),
        ]

    def __str__(self):
        result = f'{self.user} {self.author}'
        return result

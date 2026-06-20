"""Models for users application."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    """Custom user model."""

    email = models.EmailField(unique=True)
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]


class Subscription(models.Model):
    """User subscription model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
    )

    class Meta:
        """Model configuration."""

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            ),
            models.CheckConstraint(
                condition=~Q(user=F('author')),
                name='prevent_self_subscription',
            ),
        ]

    def __str__(self):
        """Return subscription representation."""
        return f'{self.user} подписан на {self.author}'

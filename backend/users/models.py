from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='users/',
        blank=True,
        null=True,
    )


class Subscription(models.Model):
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
        return f'{self.user} подписан на {self.author}'

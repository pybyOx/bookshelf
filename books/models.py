from django.db import models
from django.conf import settings   # рекомендованный Django способ ссылаться на модель пользователя User


class Book(models.Model):
    title = models.CharField()
    author = models.CharField()
    year = models.IntegerField()
    added_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='books',
            null=True, blank=True,
        )

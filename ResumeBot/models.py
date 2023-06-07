# Импорты
from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.contrib.auth import get_user_model


# Модель Телеграм юзеров (все поля отсюда идут в базу данных)
class TgUser(models.Model):
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    tguser = models.IntegerField(unique=True)

    class Meta:
        unique_together = ('user', 'tguser')

# Импорты
from django.db import models

from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.conf import settings
from django.contrib.auth import get_user_model


# Функция загрузки и переименовывания изображений
def upload_and_rename(instance, filename):
    # file will be uploaded to MEDIA_ROOT/photos/<user_id>.<extension>
    ext = filename.split('.')[-1]
    return '{0}/{1}.{2}'.format('photos', instance.user.id, ext)


# Модель Резюме (все поля отсюда идут в базу данных)
class Resume(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    photo = models.ImageField(blank=True, null=True, upload_to=upload_and_rename)
    fio = models.CharField(max_length=100)
    birthday = models.DateField(blank=True, null=True)
    phonenum = models.CharField(max_length=12, unique=True)
    grade = models.IntegerField(blank=True, null=True)
    institution = models.CharField(max_length=100)
    curator = models.CharField(max_length=100)
    spec = models.CharField(blank=True, max_length=30, null=True)
    skills = models.CharField(blank=True, max_length=300, null=True)
    projects = models.TextField(blank=True, null=True)
    project_links = models.CharField(blank=True, max_length=500, null=True)
    education = models.CharField(blank=True, max_length=100, null=True)
    first_lang = models.CharField(blank=True, max_length=20, null=True)
    other_lang = models.CharField(blank=True, max_length=300, null=True)
    country = models.CharField(blank=True, max_length=100, null=True)
    pract_name = models.CharField(blank=True, max_length=100, null=True)
    pract_period_from = models.DateField()
    pract_period_to = models.DateField()
    pract_jobs = models.TextField()
    linkedin = models.URLField(blank=True, null=True)
    pract_tasks = models.CharField(max_length=100)
    laptop = models.BooleanField()



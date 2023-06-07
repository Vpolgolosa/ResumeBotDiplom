# Импорты
from django import template

from ResumeWeb.models import Resume

register = template.Library()


# Функция проверки на наличие у данного пользователя созданного резюме
@register.filter(name='has_resume')
def has_resume(user):
    return Resume.objects.filter(user_id=user.id).exists()


# Функция проверки на наличие данного пользователя в данной группе пользователей
@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

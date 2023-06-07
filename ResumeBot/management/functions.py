# Импорты
import os
import re
from datetime import date, datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.auth.models import User
from ResumeBot.models import TgUser
from ResumeWeb.models import Resume
from asgiref.sync import sync_to_async


# Функция проверки введенных данных по паттернам regex
def checkpatt(text, pat):
    pattern = None
    if pat == 1:
        pattern = "[A-Za-z0-9@.+_-]{1,150}"
    elif pat == 2:
        pattern = "[^@]+@[^@]+\.[^@]+"
    elif pat == 3:
        pattern = "\S{8,128}"
    elif pat == 4:
        pattern = "[А-Яа-яЁё]+\s{1}[А-Яа-яЁё]+\s{1}[А-Яа-яЁё]+"
    elif pat == 5:
        pattern = "[+]{0,1}[7-8]{1}[0-9]{10}"
    if pattern is not None:
        return re.fullmatch(pattern, text)
    else:
        return None


# Функция проверки введенных дат
def checkdate(date1, date2, oper):
    if oper == 1:
        return 65 >= (date1.year - date2.year) >= 16
    elif oper == 2:
        return (date1-date2).days <= 90
    elif oper == 3:
        today = date.today()
        return date1 > today and (date1-date2).days <= 90 and date1 > date2


# Функция удаления изображения из локального хранилища
def removeImage(filename):
    fdict = "media/" + filename
    try:
        os.remove(fdict)
    except FileNotFoundError:
        print("FileNotFoundError (Ignored)")


# Функция запросов к БД
@sync_to_async
def db_access(tgid, oper=None, ret=None, target=None, msg=None, obj=None):
    rt = False
    val = None
    if oper is None or oper < 3:
        try:
            result = TgUser.objects.get(tguser=tgid)
        except ObjectDoesNotExist or MultipleObjectsReturned:
            rt = False
        else:
            if oper is None:
                rt = True
                val = result
            elif oper == 1:
                try:
                    result2 = User.objects.get(id=result.user_id)
                except ObjectDoesNotExist or MultipleObjectsReturned:
                    rt = False
                else:
                    rt = True
                    val = result2
            elif oper == 2:
                try:
                    result2 = Resume.objects.get(user_id=result.user_id)
                except ObjectDoesNotExist or MultipleObjectsReturned:
                    rt = False
                else:
                    if target is None:
                        rt = True
                        val = result2
                    elif target == 1:
                        rt = True
                        result2 = Resume.objects.filter(user_id=result.user_id).values(msg)
                        val = result2[0][msg]
    else:
        if oper == 3:
            result2 = Resume.objects.all()
            val = result2
            rt = True
        elif oper == 4:
            result2 = obj.values(msg)[0][msg]
            val = result2
            rt = True
        elif oper == 5:
            result2 = [User.objects.all()]
            try:
                result2.append(User.objects.get(id=msg))
            except ObjectDoesNotExist or MultipleObjectsReturned:
                rt = False
            else:
                val = result2
                rt = True
    if ret is None:
        return rt
    elif ret == 1:
        return val
    elif ret == 2:
        return rt, val


# Функция перемещения пользователя из одной группы пользователей в другую
@sync_to_async
def db_groups(gr1, gr2, user):
    gr2.user_set.add(user)
    gr1.user_set.remove(user)

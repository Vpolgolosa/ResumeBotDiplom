import logging
import re
from datetime import date, datetime

import django.db
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import connection

from ResumeBot.management import config
from ResumeBot.management import functions as func
from ResumeBot.models import TgUser
from ResumeWeb.models import Resume

# log level
logging.basicConfig(level=logging.INFO)

# bot init
storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)


# run long-polling


class Command(BaseCommand):
    help = "Tg bot"

    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=False)


# States class
class Register(StatesGroup):
    username = State()
    email = State()
    password = State()


class Auth(StatesGroup):
    username = State()
    password = State()


class ResumeTg(StatesGroup):
    photoChoose = State()
    photo = State()
    fio = State()
    birthday = State()
    phonenum = State()
    grade = State()
    institution = State()
    curator = State()
    spec = State()
    skills = State()
    projects = State()
    project_links = State()
    education = State()
    first_lang = State()
    other_lang = State()
    country = State()
    pract_name = State()
    pract_period_from = State()
    pract_period_to = State()
    pract_jobs = State()
    linkedin = State()
    pract_tasks = State()
    laptop = State()


class ResumeDel(StatesGroup):
    answ = State()
    confirm = State()
    confirmadmin = State()
    deluser = State()


class ResumeEdit(StatesGroup):
    show = State()
    repeat_show = State()
    change = State()
    repeat = State()


# global tuples
columns = ("photo", "fio", "birthday", "phonenum", "grade", "institution", "curator", "spec", "skills",
           "projects", "project_links", "education", "first_lang", "other_lang", "country",
           "pract_name", "pract_period_from", "pract_period_to",
           "pract_jobs", "linkedin", "pract_tasks", "laptop")

columns_prefix = ("", "ФИО", "Дата рождения", "Номер телефона", "Номер курса", "Наименование учебного заведения",
                  "Куратор от учебного заведения", "Специальность", "Ключевые навыки", "Реализованные проекты",
                  "Ссылки на реализованные проекты", "Уровень образования", "Родной язык", "Другие языки",
                  "Гражданство", "Тип практики", "Начало практики", "Окончание практики",
                  "Работы, которые необходимо реализовать в рамках практики", "Ссылка на профиль LinkedIn",
                  "Выбранный вид деятельности", "Наличие ноутбука")

columns_prefix_edit = (
    "фотографию", "ФИО", "дату рождения", "номер телефона", "номер курса (цифрой)", "наименование учебного заведения",
    "ФИО куратора от учебного заведения", "специальность", "ключевые навыки", "реализованные проекты",
    "ссылки на реализованные проекты", "уровень образования", "родной язык", "другие языки",
    "гражданство", "тип практики", "начало практики", "окончание практики",
    "работы, которые необходимо реализовать в рамках практики", "ссылку на профиль LinkedIn",
    "выбранный вид деятельности", "наличие ноутбука")

columns_examples = ("", "Иванов Иван Иванович", "день.месяц.год - 01.01.0001", "+71234567890\n   81234567890", "1",
                    "Санкт-Петербургский государственный университет\n   СПбГУ",
                    "Иванов Иван Иванович", "Web-Разработчик",
                    "Опыт работы с базами данных; Python; Опыт работы с Visual Studio, Pycharm; ...",
                    "(Описание Вашего проекта); (Описание Вашего проекта); (Описание Вашего проекта)",
                    "(Ссылка на первый описанный проект); (Ссылка на второй описанный проект); (Ссылка на "
                    "третий описанный проект)",
                    "Среднее специальное", "Русский", "Английский, Китайский, ...",
                    "Российская Федерация", "Производственная практика", "день.месяц.год - 01.01.0001",
                    "день.месяц.год - 31.01.0001", "Работа1; Работа2; ...", "https://www.linkedin.com/in/...",
                    "Простые задачи операционной деятельности организации\n   Задачи на разработку программных "
                    "продуктов\n   Бизнес анализ для создания программных продуктов\n   Дизайн и прототипирование "
                    "программных продуктов\n   Тестирование программных продуктов\n   Работа с серверами\n   "
                    "Системная аналитика",
                    "'+' - есть ноутбук\n   '-' - нет ноутбука\n  Вводите + или - без кавычек")
restrict = {1: 100, 5: 100, 6: 100, 7: 30, 8: 300, 10: 500, 11: 100, 12: 20, 13: 300, 14: 100, 15: 100, 19: 200,
            20: 100}
lap = {True: "Есть", False: "Нет"}
lap2 = {"+": True, "-": False}


# command handlers
######################################################################
# start
@dp.message_handler(commands=["start"], commands_prefix="/")
async def cmd_start(message: types.Message):
    result = await func.db_access(message.from_user.id)
    if not result:
        start = "Привет! Для начала работы с ботом, введите следующие команды: \n   /reg - Регистрация;\n   /auth - " \
                "Авторизация; "
    else:
        result = await func.db_access(message.from_user.id, 1, 1)
        if not result.is_staff:
            start = "Привет! Для работы с ботом, введите следующие команды: \n   /resume - Создать свое резюме;\n   " \
                    "/edit - Изменить свое резюме;\n   /show - Показать свое резюме;\n   /delete - Удалить свое резюме "
        else:
            if not result.is_superuser:
                start = "Привет! Для работы с ботом, введите следующие команды: \n   /resume - Создать свое резюме;\n  " \
                        "/edit - Изменить свое резюме;\n   /show - Показать свое резюме;\n   /delete - Удалить свое " \
                        "резюме;\n\nКоманды администратора:\n   /show [номер телефона]/[all] - Показать резюме " \
                        "пользователя с данным номером телефона;\n   /delete - Удалить резюме;\n   /deleteold - " \
                        "Удалить резюме всех участников, уже прошедших практику;\n   Ввод [...] осуществляется без " \
                        "скобок! "
            else:
                start = "Привет! Для работы с ботом, введите следующие команды: \n   /resume - Создать свое резюме;\n  " \
                        "/edit - Изменить свое резюме;\n   /show - Показать свое резюме;\n   /delete - Удалить свое " \
                        "резюме;\n\nКоманды администратора:\n   /show [номер телефона]/[all] - Показать резюме " \
                        "пользователя с данным номером телефона;\n   /delete - Удалить резюме;\n   /deleteold - " \
                        "Удалить резюме всех участников, уже прошедших практику;\n   Ввод [...] осуществляется без " \
                        "скобок! "
    await message.answer(start)


######################################################################
# user register
@dp.message_handler(commands=["reg"], commands_prefix="/", state="*")
async def cmd_reg(message: types.Message):
    result = await func.db_access(message.from_user.id)
    if not result:
        await message.answer("Введите Ваш логин")
        # Переходим на следующий стейт
        await Register.username.set()
    else:
        await message.answer("Вы уже зарегистрированы!")


@dp.message_handler(state=Register.username, content_types=types.ContentTypes.TEXT)
async def regusername(message: types.Message, state: FSMContext):
    username = message.text
    if func.checkpatt(username, 1) is not None:
        await state.update_data(username=username)
        await message.answer("Введите Вашу почту")
        await Register.email.set()
    else:
        await message.answer("Логин введен неправильно!\nРазрешены только латинские буквы, цифры и символы @.+-_ !")


@dp.message_handler(state=Register.email, content_types=types.ContentTypes.TEXT)
async def regemail(message: types.Message, state: FSMContext):
    email = message.text
    if len(email) < 254:
        if func.checkpatt(email, 2) is not None:
            await state.update_data(email=email)
            await message.answer("Введите пароль")
            await Register.password.set()
        else:
            await message.answer("Почта введена неправильно!")
    else:
        await message.answer("Почта введена неправильно!")


@sync_to_async
def registersync(username, email, password, tguser):
    connection.connect()
    user = User.objects.create_user(username=username, email=email, password=password)
    value = "Guests"
    connection.connect()
    group = Group.objects.get(name=value)
    if user is not None:
        connection.connect()
        try:
            ret1 = TgUser.objects.get_or_create(tguser=tguser, user_id=user.id)
        except django.db.IntegrityError:
            print("Ошибка создания тг-пользователя")
        connection.connect()
        group.user_set.add(user)


@dp.message_handler(state=Register.password, content_types=types.ContentTypes.TEXT)
async def regpassword(message: types.Message, state: FSMContext):
    password = message.text
    if func.checkpatt(password, 3) is not None:
        await state.update_data(password=password)
        await state.update_data(laptop=message.text)
        data = await state.get_data()
        username = f'{data.get("username")}'
        email = f'{data.get("email")}'
        password = f'{data.get("password")}'
        await registersync(username, email, password, message.from_user.id)
        await message.answer("Регистрация завершена!")
        await state.finish()
    else:
        await message.answer("Пароль должен быть не короче 8 символов!")


######################################################################
# user auth
@dp.message_handler(commands=["auth"], commands_prefix="/", state="*")
async def cmd_auth(message: types.Message):
    await message.answer("Введите Ваш логин")
    # Переходим на следующий стейт
    await Auth.username.set()


@dp.message_handler(state=Auth.username, content_types=types.ContentTypes.TEXT)
async def authusername(message: types.Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Введите Ваш пароль")
    await Auth.password.set()


@sync_to_async
def authsync(username, password, tguser):
    connection.connect()
    user = authenticate(username=username, password=password)
    if user is not None:
        connection.connect()
        try:
            ret1 = TgUser.objects.get_or_create(tguser=tguser, user_id=user.id)
        except django.db.IntegrityError:
            print("Ошибка создания тг-пользователя")
        return True
    else:
        return False


@dp.message_handler(state=Auth.password, content_types=types.ContentTypes.TEXT)
async def authpassword(message: types.Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)
    await state.update_data(laptop=message.text)
    data = await state.get_data()
    username = f'{data.get("username")}'
    password = f'{data.get("password")}'
    tguser = message.from_user.id
    result = await authsync(username, password, tguser)
    if result:
        await message.answer("Авторизация успешна!")
    else:
        await message.answer("Ошибка авторизации!")
    await state.finish()


######################################################################
# resume creation
@dp.message_handler(commands="cancel", commands_prefix="/", state="*")
async def menu_button(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get("photo") is not None:
        func.removeImage(f'{data.get("photo")}')
    await state.finish()
    await message.answer("Действие отменено.")


@dp.message_handler(commands=["resume"], commands_prefix="/", state="*")
async def cmd_resume(message: types.Message):
    result = await func.db_access(message.from_user.id, 2)
    if not result:
        await message.answer(
            "Процесс создания Вашего резюме начался!\nВводите ответы на поставленные запросы одним "
            "сообщением!\nОтменить регистрацию - /cancel\nВернуться к предыдущему шагу - /return")
        await message.answer("Выберите, какую фотографию использовать:\n   1 - Фотографию профиля telegram\n   2 - "
                             "Прислать другую фотографию")
        # Переходим на следующий стейт
        await ResumeTg.photoChoose.set()
    else:
        await message.answer("Вы уже создали свое резюме!")


@dp.message_handler(state=ResumeTg.photoChoose, content_types=types.ContentTypes.TEXT)
async def photoChoose(message: types.Message, state: FSMContext):
    if message.text == "1":
        result = await func.db_access(message.from_user.id, ret=1)
        photo_name = "photos/" + str(result.user_id) + '.jpg'
        img = await bot.get_user_profile_photos(message.from_user.id, 0, 2)
        file_id = img["photos"][0][0]["file_id"]
        file = await bot.get_file(file_id)
        file_path = file.file_path
        destination_path = f"{settings.MEDIA_ROOT}/" + photo_name
        await bot.download_file(file_path, destination_path)
        await state.update_data(photoChoose=message.text)
        await state.update_data(photo=photo_name)
        await message.answer("Введите Ваше ФИО\nПример:\n   Иванов Иван Иванович")
        await ResumeTg.fio.set()
    elif message.text == "2":
        await state.update_data(photoChoose=message.text)
        await message.answer("Пришлите Вашу фотографию.\nВаше лицо на фотографии должно быть хорошо видно.")
        await ResumeTg.photo.set()
    else:
        await message.answer("Ответ введен некорректно!\nВведите 1 или 2 еще раз!")


@dp.message_handler(state=ResumeTg.photo, content_types=['photo', 'document'])
async def photo(message: types.Message, state: FSMContext):
    result = await func.db_access(message.from_user.id, ret=1)
    photo_name = "photos/" + str(result.user_id) + '.jpg'
    destination_path = "media/" + photo_name
    try:
        await message.photo[-1].download(destination_path)
    except IndexError:
        await message.document.download(destination_path)
    await state.update_data(photo=photo_name)
    await message.answer("Введите Ваше ФИО\nПример:\n   Иванов Иван Иванович")
    await ResumeTg.fio.set()


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.fio)
@dp.message_handler(state=ResumeTg.fio, content_types=types.ContentTypes.TEXT)
async def fio(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Выберите, какую фотографию использовать:\n   1 - Фотографию профиля telegram\n   2 - "
                             "Прислать другую фотографию")
        await ResumeTg.photoChoose.set()
    else:
        if 100 > len(message.text) > 0:
            if func.checkpatt(message.text, 4) is not None:
                await state.update_data(fio=message.text)
                await message.answer("Введите дату Вашего рождения\nПример:\n   день.месяц.год - 01.01.0001")
                await ResumeTg.birthday.set()
            else:
                await message.answer("ФИО введено неправильно!\nРазрешены только русские буквы и пробел\nВведите ФИО "
                                     "еще раз!")
        else:
            await message.answer("Ваше ФИО слишком большое!\nВведите ФИО еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.birthday)
@dp.message_handler(state=ResumeTg.birthday, content_types=types.ContentTypes.TEXT)
async def birthday(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите Ваше ФИО\nПример:\n   Иванов Иван Иванович")
        await ResumeTg.fio.set()
    else:
        try:
            bday = datetime.strptime(message.text, '%d.%m.%Y').date()
        except ValueError:
            await message.answer("Дата введена неверно!\nВведите дату еще раз!")
        else:
            if func.checkdate(date.today(), bday, 1) is True:
                await state.update_data(birthday=bday)
                await message.answer("Введите номер Вашего телефона\nПример:\n   +71234567890\n   81234567890")
                await ResumeTg.phonenum.set()
            else:
                await message.answer("Указанный возраст должен быть в диапазоне от 16 до 65 лет!"
                                     "\nВведите дату еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.phonenum)
@dp.message_handler(state=ResumeTg.phonenum, content_types=types.ContentTypes.TEXT)
async def phonenum(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите дату Вашего рождения\nПример:\n   день.месяц.год - 01.01.0001")
        await ResumeTg.birthday.set()
    else:
        if func.checkpatt(message.text, 5) is not None:
            if message.text.startswith('+7'):
                msg = message.text[2:]
                result = await func.db_access(message.from_user.id, 3, 1)
            else:
                msg = message.text[1:]
                result = await func.db_access(message.from_user.id, 3, 1)
            if not await result.filter(phonenum__contains=msg).aexists():
                await state.update_data(phonenum=message.text)
                await message.answer("Введите номер Вашего курса (цифрой)\nПример:\n   1")
                await ResumeTg.grade.set()
            else:
                await message.answer("Этот номер телефона уже занят!\nВведите номер еще раз!")
        else:
            await message.answer("Вы неверно ввели номер!\nВведите номер еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.grade)
@dp.message_handler(state=ResumeTg.grade, content_types=types.ContentTypes.TEXT)
async def grade(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите номер Вашего телефона\nПример:\n   +71234567890\n   81234567890")
        await ResumeTg.phonenum.set()
    else:
        if len(message.text) == 1 and message.text.isdigit():
            if 1 <= int(message.text) <= 7:
                await state.update_data(grade=int(message.text))
                await message.answer("Введите наименование Вашего учебного заведения\nПример:\n   Санкт-Петербургский государственный университет\n   СПбГУ")
                await ResumeTg.institution.set()
            else:
                await message.answer("Вы неверно ввели номер курса!\nВведите номер Вашего курса еще раз!")
        else:
            await message.answer("Вы неверно ввели номер курса!\nВведите номер Вашего курса еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.institution)
@dp.message_handler(state=ResumeTg.institution, content_types=types.ContentTypes.TEXT)
async def institution(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите номер Вашего курса\nПример:\n   1 курс")
        await ResumeTg.grade.set()
    else:
        if 100 >= len(message.text) > 0:
            await state.update_data(institution=message.text)
            await message.answer("Введите ФИО Вашего куратора от учебного заведения\nПример:\n   Иванов Иван Иванович")
            await ResumeTg.curator.set()
        else:
            await message.answer(
                "Вы неверно ввели наименование Вашего учебного заведения!\nВведите наименование Вашего учебного "
                "заведения еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.curator)
@dp.message_handler(state=ResumeTg.curator, content_types=types.ContentTypes.TEXT)
async def curator(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer(
            "Введите наименование Вашего учебного заведения\nПример:\n   Санкт-Петербургский государственный "
            "университет\n   СПбГУ")
        await ResumeTg.institution.set()
    else:
        text_list = re.split(" ", message.text)
        if len(text_list) == 3 and 100 >= len(message.text) > 0:
            await state.update_data(curator=message.text)
            await message.answer("Введите наименование Вашей специальности\nПример:\n   Web-Разработчик")
            await ResumeTg.spec.set()
        else:
            await message.answer("Вы неверно ввели ФИО Вашего куратора!\nВведите ФИО Вашего куратора еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.spec)
@dp.message_handler(state=ResumeTg.spec, content_types=types.ContentTypes.TEXT)
async def spec(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите ФИО Вашего куратора от учебного заведения\nПример:\n   Иванов Иван Иванович")
        await ResumeTg.curator.set()
    else:
        if 30 >= len(message.text) > 0:
            await state.update_data(spec=message.text)
            await message.answer(
                "Перечислите Ваши ключевые навыки\nПример:\n   Опыт работы с базами данных; Python; Опыт работы с "
                "Visual Studio, Pycharm; ...")
            await ResumeTg.skills.set()
        else:
            await message.answer(
                "Вы неверно ввели наименование Вашей специальности!\nВведите наименование Вашей специальности еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.skills)
@dp.message_handler(state=ResumeTg.skills, content_types=types.ContentTypes.TEXT)
async def skills(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите наименование Вашей специальности\nПример:\n   Web-Разработчик")
        await ResumeTg.spec.set()
    else:
        text_list = re.split(";", message.text)
        if len(text_list) > 1 and 300 >= len(message.text) > 0:
            await state.update_data(skills=message.text)
            await message.answer(
                "Введите описание не более трех выполненых Вами проектов\nПример:\n   (Описание Вашего проекта); "
                "(Описание Вашего проекта); (Описание Вашего проекта)")
            await ResumeTg.projects.set()
        else:
            await message.answer("Вы неверно ввели Ваши ключевые навыки!\nПеречислите Ваши ключевые навыки еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.projects)
@dp.message_handler(state=ResumeTg.projects, content_types=types.ContentTypes.TEXT)
async def projects(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer(
            "Перечислите Ваши ключевые навыки\nПример:\n   Опыт работы с базами данных; Python; Опыт работы с "
            "Visual Studio, Pycharm; ...")
        await ResumeTg.skills.set()
    else:
        text_list = re.split(";", message.text)
        if len(text_list) > 1 and len(message.text) > 0:
            await state.update_data(projects=message.text)
            await message.answer(
                "Введите ссылки на репозитории с Вашими проектами\nПример:\n   (Ссылка на первый описанный "
                "проект); (Ссылка на второй описанный проект); (Ссылка на третий описанный проект)")
            await ResumeTg.project_links.set()
        else:
            await message.answer(
                "Вы неверно ввели описание выполненых Вами 2-3х проектов!\nВведите описание выполненых Вами 2-3х "
                "проектов "
                "еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.project_links)
@dp.message_handler(state=ResumeTg.project_links, content_types=types.ContentTypes.TEXT)
async def project_links(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer(
            "Введите описание не более трех выполненых Вами проектов\nПример:\n   (Описание Вашего проекта); "
            "(Описание Вашего проекта); (Описание Вашего проекта)")
        await ResumeTg.projects.set()
    else:
        text_list = re.split(";", message.text)
        if len(text_list) > 1 and 500 >= len(message.text) > 0:
            await state.update_data(project_links=message.text)
            await message.answer("Введите уровень Вашего образования\nПример:\n   Среднее специальное")
            await ResumeTg.education.set()
        else:
            await message.answer(
                "Вы неверно ввели ссылки на репозитории с Вашими проектами!\nВведите ссылки на репозитории с Вашими "
                "проектами еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.education)
@dp.message_handler(state=ResumeTg.education, content_types=types.ContentTypes.TEXT)
async def education(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer(
            "Введите ссылки на репозитории с Вашими проектами\nПример:\n   (Ссылка на первый описанный "
            "проект); (Ссылка на второй описанный проект); (Ссылка на третий описанный проект)")
        await ResumeTg.project_links.set()
    else:
        if 100 >= len(message.text) > 0:
            await state.update_data(education=message.text)
            await message.answer("Введите Ваш родной язык\nПример:\n   Русский")
            await ResumeTg.first_lang.set()
        else:
            await message.answer(
                "Вы неверно ввели уровень Вашего образования!\nВведите уровень Вашего образования еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.first_lang)
@dp.message_handler(state=ResumeTg.first_lang, content_types=types.ContentTypes.TEXT)
async def first_lang(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите уровень Вашего образования\nПример:\n   Среднее специальное")
        await ResumeTg.education.set()
    else:
        if 20 >= len(message.text) > 0:
            await state.update_data(first_lang=message.text)
            await message.answer(
                "Перечислите другие языки, которыми Вы владеете\nУровень владения - выше среднего\nПример:\n   "
                "Английский, Францусзкий, ...")
            await ResumeTg.other_lang.set()
        else:
            await message.answer("Вы неверно ввели Ваш родной язык!\nВведите Ваш родной язык еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.other_lang)
@dp.message_handler(state=ResumeTg.other_lang, content_types=types.ContentTypes.TEXT)
async def other_lang(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите Ваш родной язык\nПример:\n   Русский")
        await ResumeTg.first_lang.set()
    else:
        if 300 >= len(message.text) > 0:
            await state.update_data(other_lang=message.text)
            await message.answer("Введите Ваше гражданство\nПример:\n   Российская Федерация")
            await ResumeTg.country.set()
        else:
            await message.answer(
                "Вы неверно ввели другие языки, которыми Вы владеете!\nПеречислите другие языки, которыми Вы владеете "
                "еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.country)
@dp.message_handler(state=ResumeTg.country, content_types=types.ContentTypes.TEXT)
async def country(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer(
            "Перечислите другие языки, которыми Вы владеете\nУровень владения - выше среднего\nПример:\n   "
            "Английский, Францусзкий, ...")
        await ResumeTg.other_lang.set()
    else:
        if 100 >= len(message.text) > 0:
            await state.update_data(country=message.text)
            await message.answer("Введите тип Вашей практики\nПример:\n   Производственная практика")
            await ResumeTg.pract_name.set()
        else:
            await message.answer("Вы неверно ввели Ваше гражданство!\nВведите Ваше гражданство еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.pract_name)
@dp.message_handler(state=ResumeTg.pract_name, content_types=types.ContentTypes.TEXT)
async def pract_name(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите Ваше гражданство\nПример:\n   Российская Федерация")
        await ResumeTg.country.set()
    else:
        if 100 >= len(message.text) > 0:
            await state.update_data(pract_name=message.text)
            await message.answer("Введите дату начала периода прохождения Вашей практики\nПример:\n   31.12.0001")
            await ResumeTg.pract_period_from.set()
        else:
            await message.answer("Вы неверно ввели название Вашей практики!\nВведите название Вашей практики еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.pract_period_from)
@dp.message_handler(state=ResumeTg.pract_period_from, content_types=types.ContentTypes.TEXT)
async def pract_period_from(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите тип Вашей практики\nПример:\n   Производственная практика")
        await ResumeTg.pract_name.set()
    else:
        try:
            dat = datetime.strptime(message.text, '%d.%m.%Y').date()
        except ValueError:
            await message.answer("Дата введена неверно!\nВведите дату еще раз!")
        else:
            if func.checkdate(date.today(), dat, 2) is True:
                await state.update_data(pract_period_from=dat)
                await message.answer(
                    "Введите дату окончания периода прохождения Вашей практики\nПример:\n   31.01.0002")
                await ResumeTg.pract_period_to.set()
            else:
                await message.answer("Дата начала практики должна быть не раньше 3 месяцев назад!"
                                     "\nВведите дату еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.pract_period_to)
@dp.message_handler(state=ResumeTg.pract_period_to, content_types=types.ContentTypes.TEXT)
async def pract_period_to(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите дату начала периода прохождения Вашей практики\nПример:\n   31.12.0001")
        await ResumeTg.pract_period_from.set()
    else:
        try:
            dat = datetime.strptime(message.text, '%d.%m.%Y').date()
        except ValueError:
            await message.answer("Дата введена неверно!\nВведите дату еще раз!")
        else:
            data = await state.get_data()
            if func.checkdate(dat, data.get("pract_period_from"), 3) is True:
                await state.update_data(pract_period_to=dat)
                await message.answer("Перечислите работы, которые необходимо выполнить во время практики\nПример:\n   "
                                     "Работа1; Работа2; ...")
                await ResumeTg.pract_jobs.set()
            else:
                await message.answer("Дата окончания практики должна быть не раньше чем сегодня и не позже чем 3 "
                                     "месяца от даты начала практики!\nВведите дату еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.pract_jobs)
@dp.message_handler(state=ResumeTg.pract_jobs, content_types=types.ContentTypes.TEXT)
async def pract_jobs(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите дату окончания периода прохождения Вашей практики\nПример:\n   31.01.0002")
        await ResumeTg.pract_period_to.set()
    else:
        text_list = re.split(";", message.text)
        if len(text_list) > 1 and 1000 >= len(message.text) > 0:
            await state.update_data(pract_jobs=message.text)
            await message.answer("Введите ссылку на Ваш профиль LinkedIn\nПример:\n   https://www.linkedin.com/in/...")
            await ResumeTg.linkedin.set()
        else:
            await message.answer("Вы неверно ввели работы!\nВведите работы Вашей практики еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.linkedin)
@dp.message_handler(state=ResumeTg.linkedin, content_types=types.ContentTypes.TEXT)
async def linkedin(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer(
            "Перечислите работы, которые необходимо выполнить во время практики\nПример:\n   Работа1; Работа2; "
            "...")
        await ResumeTg.pract_jobs.set()
    else:
        if 200 >= len(message.text) > 0:
            await state.update_data(linkedin=message.text)
            await message.answer(
                "Укажите один из ниже перечисленных видов деятельности, который Вы хотите выполнять на практике:\n   "
                "Простые задачи операционной деятельности организации\n   Задачи на разработку программных продуктов\n "
                "  Бизнес анализ для создания программных продуктов\n   Дизайн и прототипирование программных "
                "продуктов\n   Тестирование программных продуктов\n   Работа с серверами\n   Системная аналитика")
            await ResumeTg.pract_tasks.set()
        else:
            await message.answer("Вы неверно ввели ссылку!\nВведите ссылку на Ваш профиль LinkedIn еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.pract_tasks)
@dp.message_handler(state=ResumeTg.pract_tasks, content_types=types.ContentTypes.TEXT)
async def pract_tasks(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer("Введите ссылку на Ваш профиль LinkedIn\nПример:\n   https://www.linkedin.com/in/...")
        await ResumeTg.linkedin.set()
    else:
        choices = ('Простые задачи операционной деятельности организации', 'Задачи на разработку программных продуктов',
                   'Бизнес анализ для создания программных продуктов',
                   'Бизнес анализ для создания программных продуктов',
                   'Дизайн и прототипирование программных продуктов', 'Системная аналитика', 'Работа с серверами')
        if 100 >= len(message.text) > 0 and str(message.text) in choices:
            await state.update_data(pract_tasks=message.text)
            await message.answer(
                "Укажите наличие у Вас ноутбука\nПример:\n   '+' - есть ноутбук\n   '-' - нет ноутбука\n  Вводите + "
                "или - без кавычек")
            await ResumeTg.laptop.set()
        else:
            await message.answer("Вы неверно вид деятельности!\nВведите вид деятельности еще раз!")


@dp.message_handler(commands="return", commands_prefix="/", state=ResumeTg.laptop)
@dp.message_handler(state=ResumeTg.laptop, content_types=types.ContentTypes.TEXT)
async def laptop(message: types.Message, state: FSMContext):
    if "/return" in message.text:
        await message.answer(
            "Укажите один из ниже перечисленных видов деятельности, который Вы хотите выполнять на практике:\n   "
            "Простые задачи операционной деятельности организации\n   Задачи на разработку программных продуктов\n   "
            "Бизнес анализ для создания программных продуктов\n   Дизайн и прототипирование программных продуктов\n   "
            "Тестирование программных продуктов\n   Работа с серверами\n   Системная аналитика")
        await ResumeTg.pract_tasks.set()
    else:
        if message.text == "+" or message.text == "-":
            await state.update_data(laptop=lap2[message.text])
            data = await state.get_data()
            result = await func.db_access(message.from_user.id, ret=1)
            try:
                await Resume.objects.acreate(photo=data.get("photo"), fio=data.get("fio"),
                                             birthday=data.get("birthday"), phonenum=data.get("phonenum"),
                                             grade=data.get("grade"), institution=data.get("institution"),
                                             curator=data.get("curator"), spec=data.get("spec"),
                                             skills=data.get("skills"), projects=data.get("projects"),
                                             project_links=data.get("project_links"), education=data.get("education"),
                                             first_lang=data.get("first_lang"), other_lang=data.get("other_lang"),
                                             country=data.get("country"), pract_name=data.get("pract_name"),
                                             pract_period_from=data.get("pract_period_from"),
                                             pract_period_to=data.get("pract_period_to"),
                                             pract_jobs=data.get("pract_jobs"), linkedin=data.get("linkedin"),
                                             pract_tasks=data.get("pract_tasks"), laptop=data.get("laptop"),
                                             user_id=result.user_id)
                user = await User.objects.aget(id=result.user_id)
                group1 = await Group.objects.aget(name="Guests")
                group2 = await Group.objects.aget(name="Interns")
                if await user.groups.filter(name="Guests").aexists():
                    await func.db_groups(group1, group2, user)
            except django.db.IntegrityError:
                await message.answer("Ошибка при создании резюме!")
            else:
                await message.answer("Резюме успешно создано!")
            await state.finish()
        else:
            await message.answer("Вы неверно ввели наличие у Вас ноутбука!\nВведите наличие у Вас ноутбука еще раз!")


####################################################


# resume edition
@dp.message_handler(commands=["edit"], commands_prefix="/")
async def cmd_edit(message: types.Message):
    result = await func.db_access(message.from_user.id, 2)
    if not result:
        await message.answer("Вы еще не создали свое резюме!")
    else:
        await message.answer("Процесс изменения Вашего резюме начался!\nЗавершить процесс - /cancel")
        await message.answer(
            "Введите номер одного из пунктов Вашего резюме:\n   1 - Фотография\n   2 - ФИО\n   3 - Дата рождения\n   "
            "4 - Номер телефона\n   5 - Номер курса\n   6 - Наименование учебного заведения\n   7 - ФИО куратора от "
            "учебного заведения\n   8 - Специальность\n   9 - Ключевые навыки\n   10 - Описание реализованных "
            "проектов\n   11 - Ссылки на проекты\n   12 - Образование\n   13 - Родной язык\n   14 - Другие языки\n   "
            "15 - Гражданство\n   16 - Тип практики\n   17 - Дата начала практики\n   18 - Дата окончания практики\n  "
            " 19 - Работы на практику\n   20 - Ссылка на профиль LinkedIn\n   21 - Вид деятельности на практику\n   "
            "22 - Наличие ноутбука")
        await ResumeEdit.show.set()


@dp.message_handler(state=ResumeEdit.show, content_types=types.ContentTypes.TEXT)
async def editshow(message: types.Message, state: FSMContext):
    try:
        i = int(message.text)
    except ValueError:
        await message.answer("Номер введён неверно!\nВведите номер ещё раз!")
    else:
        if 1 <= i <= 22:
            x = i - 1
            db_data = await func.db_access(message.from_user.id, 2, 1, 1, columns[x])
            if db_data is not None:
                if i == 1:
                    f_name = f'{settings.MEDIA_ROOT}/{db_data}'
                    img = open(f_name, 'rb')
                    await bot.send_photo(message.chat.id, img)
                    img.close()
                elif i in (3, 17, 18):
                    text = columns_prefix[x] + "\n   " + db_data.strftime("%d.%m.%Y")
                    await bot.send_message(message.chat.id, text)
                elif i == 22:
                    text = columns_prefix[x] + "\n   " + lap[db_data]
                    await bot.send_message(message.chat.id, text)
                else:
                    text = columns_prefix[x] + "\n   " + str(db_data)
                    await bot.send_message(message.chat.id, text)
            else:
                text = "Вы не указали " + columns_prefix_edit[x]
                await bot.send_message(message.chat.id, text)
            await state.update_data(show=x)
            await message.answer("Хотите ли изменить данный пункт Вашего резюме?\n   y - Да\n   n - Нет")
            await ResumeEdit.repeat_show.set()
        else:
            await message.answer("Номер введён неверно!\nВведите номер ещё раз!")


@dp.message_handler(state=ResumeEdit.repeat_show, content_types=types.ContentTypes.TEXT)
async def editrepeatshow(message: types.Message, state: FSMContext):
    if message.text == "y":
        data = await state.get_data()
        i = f'{data.get("show")}'
        x = int(i)
        if x == 0:
            text = "Пришлите " + columns_prefix_edit[x]
        elif x in (8, 9, 10, 13, 18):
            text = "Перечислите " + columns_prefix_edit[x]
        elif x in (20, 21):
            text = "Укажите " + columns_prefix_edit[x]
        else:
            text = "Введите " + columns_prefix_edit[x]
        if x > 0:
            text += "\nПример:\n   " + columns_examples[x]
        await message.answer(text)
        await ResumeEdit.change.set()
    elif message.text == "n":
        await message.answer(
            "Введите номер одного из пунктов Вашего резюме:\n   1 - Фотография\n   2 - ФИО\n   3 - Дата рождения\n   "
            "4 - Номер телефона\n   5 - Номер курса\n   6 - Наименование учебного заведения\n   7 - ФИО куратора от "
            "учебного заведения\n   8 - Специальность\n   9 - Ключевые навыки\n   10 - Описание реализованных "
            "проектов\n   11 - Ссылки на проекты\n   12 - Образование\n   13 - Родной язык\n   14 - Другие языки\n   "
            "15 - Гражданство\n   16 - Тип практики\n   17 - Дата начала практики\n   18 - Дата окончания практики\n  "
            " 19 - Работы на практику\n   20 - Ссылка на профиль LinkedIn\n   21 - Вид деятельности на практику\n   "
            "22 - Наличие ноутбука")
        await ResumeEdit.show.set()
    else:
        await message.answer("Вы ввели неправильное значение!\nВведите y или n еще раз!")


@dp.message_handler(state=ResumeEdit.change, content_types=['photo'])
@dp.message_handler(state=ResumeEdit.change, content_types=types.ContentTypes.TEXT)
async def edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    i = f'{data.get("show")}'
    x = int(i)
    result = await func.db_access(message.from_user.id, ret=1)
    upd = None
    resp = " "
    if x == 0:
        photo_name = "photos/" + str(result.user_id) + '.jpg'
        destination_path = f"{settings.MEDIA_ROOT}/" + photo_name
        result2 = await func.db_access(message.from_user.id, 2, 1)
        if result2.photo is not None:
            func.removeImage(str(result2.photo))
        try:
            await message.photo[-1].download(destination_path)
        except IndexError:
            await message.document.download(destination_path)
        upd = {columns[x]: photo_name}
        gtg = True
    elif x == 3:
        if func.checkpatt(message.text, 5) is not None:
            if message.text.startswith('+7'):
                msg = message.text[2:]
                result = await func.db_access(message.from_user.id, 3, 1)
            else:
                msg = message.text[1:]
                result = await func.db_access(message.from_user.id, 3, 1)
            if not await result.filter(phonenum__contains=msg).aexists():
                upd = {columns[x]: message.text}
                gtg = True
            else:
                gtg = False
                resp = "Этот номер телефона уже занят!\nВведите номер еще раз!"
        else:
            gtg = False
            resp = "Вы неверно ввели номер!\nВведите номер еще раз!"
    elif x == 4:
        if len(message.text) == 1 and message.text.isdigit():
            if 1 <= int(message.text) <= 7:
                upd = {columns[x]: message.text}
                gtg = True
            else:
                resp = "Вы неверно ввели номер курса!\nВведите номер Вашего курса еще раз!"
                gtg = False
        else:
            resp = "Вы неверно ввели номер курса!\nВведите номер Вашего курса еще раз!"
            gtg = False
    elif x in (2, 16, 17):
        try:
            dat = datetime.strptime(message.text, '%d.%m.%Y').date()
        except ValueError:
            gtg = False
            resp = "Дата введена неверно!\nВведите дату еще раз!"
        else:
            if x == 2:
                if func.checkdate(date.today(), dat, 1) is True:
                    upd = {columns[x]: dat}
                    gtg = True
                else:
                    gtg = False
                    resp = "Дата введена неверно!\nВведите дату еще раз!"
            elif x == 16:
                if func.checkdate(date.today(), dat, 2) is True:
                    upd = {columns[x]: dat}
                    gtg = True
                else:
                    gtg = False
                    resp = "Дата введена неверно!\nВведите дату еще раз!"
            else:
                result2 = await func.db_access(message.from_user.id, 2, 1)
                if func.checkdate(dat, result2.pract_period_from, 3) is True:
                    upd = {columns[x]: dat}
                    gtg = True
                else:
                    gtg = False
                    resp = "Дата введена неверно!\nВведите дату еще раз!"

    elif x == 21:
        if message.text == "+" or message.text == "-":
            upd = {columns[x]: lap2[message.text]}
            gtg = True
        else:
            gtg = False
            resp = "Вы неверно ввели наличие у Вас ноутбука!\nВведите наличие у Вас ноутбука еще раз!"
    elif x in (8, 10):
        text_list = re.split(";", message.text)
        if len(text_list) > 1 and restrict[x] >= len(message.text) > 0:
            upd = {columns[x]: message.text}
            gtg = True
        else:
            gtg = False
            resp = "Данные введены неверно!\nВведите данные еще раз!"
    elif x in (9, 18):
        text_list = re.split(";", message.text)
        if len(text_list) > 1 and len(message.text) > 0:
            upd = {columns[x]: message.text}
            gtg = True
        else:
            gtg = False
            resp = "Данные введены неверно!\nВведите данные еще раз!"
    else:
        if restrict[x] >= len(message.text) > 0:
            if x == 1:
                if func.checkpatt(message.text, 4) is not None:
                    upd = {columns[x]: message.text}
                    gtg = True
                else:
                    gtg = False
                    resp = "Данные введены неверно!\nВведите данные еще раз!"
            else:
                upd = {columns[x]: message.text}
                gtg = True
        else:
            gtg = False
            resp = "Данные введены неверно!\nВведите данные еще раз!"
    if gtg:
        await Resume.objects.filter(user_id=result.user_id).aupdate(**upd)
        await message.answer("Хотите ли изменить другой пункт Вашего резюме?\n   y - Да\n   n - Нет")
        await ResumeEdit.repeat.set()
    else:
        await message.answer(resp)


@dp.message_handler(state=ResumeEdit.repeat, content_types=types.ContentTypes.TEXT)
async def editrepeat(message: types.Message, state: FSMContext):
    if message.text == "y":
        await message.answer(
            "Введите номер одного из пунктов Вашего резюме:\n   1 - Фотография\n   2 - ФИО\n   3 - Дата рождения\n   "
            "4 - Номер телефона\n   5 - Номер курса\n   6 - Наименование учебного заведения\n   7 - ФИО куратора от "
            "учебного заведения\n   8 - Специальность\n   9 - Ключевые навыки\n   10 - Описание реализованных "
            "проектов\n   11 - Ссылки на проекты\n   12 - Образование\n   13 - Родной язык\n   14 - Другие языки\n   "
            "15 - Гражданство\n   16 - Тип практики\n   17 - Дата начала практики\n   18 - Дата окончания практики\n  "
            " 19 - Работы на практику\n   20 - Ссылка на профиль LinkedIn\n   21 - Вид деятельности на практику\n   "
            "22 - Наличие ноутбука")
        await ResumeEdit.show.set()
    elif message.text == "n":
        await message.answer("Процесс изменения Вашего резюме завершен!")
        await state.finish()
    else:
        await message.answer("Вы ввели неправильное значение!\nВведите y или n еще раз!")


####################################################
# resume showing
@dp.message_handler(commands=["show"], commands_prefix="/")
async def cmd_show(message: types.Message):
    result = await func.db_access(message.from_user.id, 1, 1)
    everybody = 0
    if message.text == "/show":
        tgt = 0
        answ = "Вы еще не создали свое резюме!"
    elif message.text != "/show" and result.is_staff and message.get_args() == "all":
        tgt = 2
        answ = " "
        everybody = 1
    elif message.text != "/show" and result.is_staff:
        if len(message.get_args()) == 12 and message.get_args().startswith('+7') and message.get_args()[1:].isdigit() \
                or len(message.get_args()) == 11 and message.get_args().startswith('8') \
                and message.get_args().isdigit():
            tgt = 1
            answ = "Резюме не найдено!"
            if message.get_args().startswith('+7'):
                num = message.get_args()[2:]
            else:
                num = message.get_args()[1:]
        else:
            tgt = 2
            answ = "Номер указан неверно!"
    else:
        tgt = 2
        answ = "У Вас нет доступа к чужим резюме!"

    if everybody == 0:
        if tgt == 0:
            result2 = await func.db_access(message.from_user.id, 3, 1)
            if await result2.filter(user_id=result.id).aexists():
                result3 = result2.filter(user_id=result.id)
                res = True
            else:
                res = False
        elif tgt == 1:
            result2 = await func.db_access(message.from_user.id, 3, 1)
            if await result2.filter(phonenum__contains=num).aexists():
                result3 = result2.filter(phonenum__contains=num)
                res = True
            else:
                res = False
        else:
            res = False
        if not res:
            await message.answer(answ)
        else:
            x = 0
            text = ""
            for i in columns:
                db_data = await func.db_access(message.from_user.id, 4, 1, msg=i, obj=result3)
                if db_data is not None:
                    if x == 0:
                        f_name = f'{settings.MEDIA_ROOT}/{db_data}'
                        img = open(f_name, 'rb')
                        await bot.send_photo(message.chat.id, img)
                        img.close()
                    elif x in (2, 16, 17):
                        text += columns_prefix[x] + "\n   " + db_data.strftime("%d.%m.%Y")
                    elif x in (8, 9, 10, 18):
                        db_data_list = re.split(";|; |,|, ", db_data.replace("\r\n", ""))
                        text += columns_prefix[x] + ":"
                        for j in db_data_list:
                            if j != "":
                                text += "\n  - " + j.strip()
                    elif x == 21:
                        text += columns_prefix[x] + "\n   " + lap[db_data]
                    else:
                        text += columns_prefix[x] + "\n   " + str(db_data)
                    text += "\n\n"
                x += 1
            await bot.send_message(message.chat.id, text)
    else:
        result2 = await func.db_access(message.from_user.id, 3, 1)
        async for i in result2:
            answ = "Номер телефона - " + i.phonenum + "\n"
            answ += "ФИО - " + i.fio + "\n"
            answ += "user_id - " + str(i.user_id)
            await message.answer(answ)


####################################################
# resume deleting
@dp.message_handler(state="*", commands=["delete"], commands_prefix="/")
async def cmd_delete(message: types.Message):
    result = await func.db_access(message.from_user.id, 1, 1)
    if not result.is_staff:
        result2 = await func.db_access(message.from_user.id, 2)
        if not result2:
            await message.answer("Вы еще не создали свое резюме!")
        else:
            await message.answer("Завершить процесс - /cancel")
            await message.answer(
                "Подтвердите удаление Вашего резюме.\n   y - Подтвердить\n   n - Отменить")
            await ResumeDel.confirm.set()
    else:
        await message.answer("Завершить процесс - /cancel")
        await message.answer("Введите user_id пользователя, чье резюме хотите удалить.\n   Введите 0, если хотите "
                             "удалить свое резюме.")
        await ResumeDel.answ.set()


@dp.message_handler(state=ResumeDel.answ, content_types=types.ContentTypes.TEXT)
async def delansw(message: types.Message, state: FSMContext):
    if message.text == "0":
        result = await func.db_access(message.from_user.id, 2)
        if not result:
            await message.answer("Вы еще не создали свое резюме!")
        else:
            await message.answer("Подтвердите удаление Вашего резюме.\n   y - Подтвердить\n   n - Отменить")
            await ResumeDel.confirm.set()
    else:
        result2 = await func.db_access(message.from_user.id, 3, 1)
        try:
            msg = int(message.text)
        except ValueError:
            await message.answer("user_id введен неправильно!\nВведите user_id еще раз!")
        else:
            if not await result2.filter(user_id=msg).aexists():
                await message.answer("Указанный user_id не найден!")
            else:
                await message.answer("Подтвердите удаление резюме.\n   y - Подтвердить\n   n - Отменить")
                await state.update_data(answ=msg)
                await ResumeDel.confirmadmin.set()


@dp.message_handler(state=ResumeDel.confirmadmin, content_types=types.ContentTypes.TEXT)
async def delconfirmadmin(message: types.Message, state: FSMContext):
    if message.text == "y":
        data = await state.get_data()
        i = data.get("answ")
        result = await func.db_access(message.from_user.id, 3, 1)
        result2 = await func.db_access(message.from_user.id, 4, 1, msg="photo", obj=result.filter(user_id=i))
        if result2 is not None:
            func.removeImage(str(result2))
        await result.filter(user_id=i).adelete()
        await message.answer("Резюме успешно удалено!")
        await message.answer("Удалить аккаунт автора этого резюме?\n   y - Подтвердить\n   n - Отменить")
        await ResumeDel.deluser.set()
    elif message.text == "n":
        await message.answer("Удаление резюме отменено")
        await state.finish()
    else:
        await message.answer("Вы ввели неправильное значение!\nВведите y или n еще раз!")


@dp.message_handler(state=ResumeDel.deluser, content_types=types.ContentTypes.TEXT)
async def deluser(message: types.Message, state: FSMContext):
    if message.text == "y":
        data = await state.get_data()
        i = data.get("answ")
        ret, result = await func.db_access(message.from_user.id, 5, 2, msg=i)
        if ret:
            if not result[1].is_staff:
                await result[0].filter(id=result[1].id).adelete()
                await message.answer("Пользователь успешно удален!")
                await state.finish()
            else:
                await message.answer("Пользователь не удален, так как является админом!")
                await state.finish()
        else:
            await message.answer("Ошибка!\n Пользователь не найден!")
            await state.finish()
    elif message.text == "n":
        await message.answer("Удаление пользователя отменено")
        await state.finish()
    else:
        await message.answer("Вы ввели неправильное значение!\nВведите y или n еще раз!")


@dp.message_handler(state=ResumeDel.confirm, content_types=types.ContentTypes.TEXT)
async def delconfirm(message: types.Message, state: FSMContext):
    if message.text == "y":
        result = await func.db_access(message.from_user.id, 2, 1)
        result2 = await func.db_access(message.from_user.id, 3, 1)
        if result.photo is not None:
            func.removeImage(str(result.photo))
        await result2.filter(user_id=result.user_id).adelete()
        await message.answer("Резюме успешно удалено!")
        await state.finish()
    elif message.text == "n":
        await message.answer("Удаление резюме отменено")
        await state.finish()
    else:
        await message.answer("Вы ввели неправильное значение!\nВведите y или n еще раз!")


########################################################
# ADMIN COMMANDS
####################################################
# delete all old resume
@dp.message_handler(state="*", commands=["deleteold"], commands_prefix="/")
async def cmd_deleteold(message: types.Message):
    result = await func.db_access(message.from_user.id, 1, 1)
    if not result.is_staff:
        await message.answer("У Вас нет доступа к этой команде!")
    else:
        result2 = await func.db_access(message.from_user.id, 3, 1)
        today = date.today()
        y = 0
        async for i in result2:
            if i.pract_period_to < today:
                ret, result3 = await func.db_access(message.from_user.id, 5, 2, msg=i.user_id)
                if ret:
                    if i.photo is not None:
                        func.removeImage(str(i.photo))
                    if not result3[1].is_staff:
                        await result3[0].filter(id=result3[1].id).adelete()
                    else:
                        await i.adelete()
                    y += 1

        txt = "Удалено " + str(y) + " резюме"
        await message.answer(txt)

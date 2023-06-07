# Импорты
from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ResumeBot.management import functions as func

from .models import Resume
import re


# Формы
# Все классы в этом файле являются формами, используемыми для ввода данных в шаблонах


# Форма выбора типа работ при поиске резюме администратором
class ChseTyForm(forms.Form):
    CHOICES = (
        ('', ''),
        (
            'Простые задачи операционной деятельности организации',
            'Простые задачи операционной деятельности организации'),
        ('Задачи на разработку программных продуктов', 'Задачи на разработку программных продуктов'),
        ('Бизнес анализ для создания программных продуктов', 'Бизнес анализ для создания программных продуктов'),
        ('Дизайн и прототипирование программных продуктов', 'Дизайн и прототипирование программных продуктов'),
        ('Работа с серверами', 'Работа с серверами'),
        ('Системная аналитика', 'Системная аналитика'),
    )
    srchty = forms.ChoiceField(label="Выберите тип выполняемых работ", choices=CHOICES,
                               widget=forms.Select(attrs={'class': 'w-50'}))


# Форма выбора по какому параметру проводить поиск резюме администратором
class ChseSrchForm(forms.Form):
    CHOICES = (
        ('0', ''),
        ('1', 'Телефону'),
        ('2', 'Наличию ноутбука'),
        ('3', 'Типу выполняемых работ'),
    )
    choose = forms.ChoiceField(required=False, label="Выберите, по какому параметру проводить поиск", choices=CHOICES)


# Форма регистрации пользователя
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Форма создания резюме
class CrResumeForm(forms.ModelForm):
    CHOICES = (
        ('', ''),
        (
            'Простые задачи операционной деятельности организации',
            'Простые задачи операционной деятельности организации'),
        ('Задачи на разработку программных продуктов', 'Задачи на разработку программных продуктов'),
        ('Бизнес анализ для создания программных продуктов', 'Бизнес анализ для создания программных продуктов'),
        ('Дизайн и прототипирование программных продуктов', 'Дизайн и прототипирование программных продуктов'),
        ('Работа с серверами', 'Работа с серверами'),
        ('Системная аналитика', 'Системная аналитика'),
    )
    # Поля ввода данных
    photo = forms.ImageField(required=False, label="Прикрепите Вашу фотографию:")
    fio = forms.CharField(label="Введите Ваше ФИО", help_text="Пример: Петров Петр Петрович")
    birthday = forms.DateField(required=False, label="Введите дату Вашего рождения",
                               help_text="Пример: 31.12.0001")
    phonenum = forms.CharField(label="Введите Ваш номер телефона", help_text="Пример: +71234567890 / 81234567890")
    grade = forms.IntegerField(required=False, label="Введите номер Вашего курса",
                               help_text="Пример: 1")
    institution = forms.CharField(label="Введите наименование Вашего учебного заведения",
                                  help_text="Пример: Московский Государственный Университет / МГУ")
    curator = forms.CharField(label="Введите ФИО куратора от Вашего учебного заведения",
                              help_text="Пример: Петров Петр Петрович")
    spec = forms.CharField(required=False, label="Введите наименование Вашей специальности",
                           help_text="Пример: Web-Разработчик")
    skills = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                             label="Перечислите Ваши ключевые навыки",
                             help_text="Пример: Навык 1; Навык 2; Навык 3;")
    projects = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                               label="Перечислите (опишите) ключевые проекты, реализованные Вами",
                               help_text="Пример: Название проекта 1 - описание проекта 1; название проекта 2 - "
                                         "описание проекта 2; итд")
    project_links = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                                    label="Введите ссылки на репозитории вышеперечисленных проектов",
                                    help_text="Пример: Ссылка на проект 1; ссылка на проект 2; итд")
    education = forms.CharField(required=False, label="Введите уровень Вашего образования",
                                help_text="Пример: Среднее специальное")
    first_lang = forms.CharField(required=False, label="Введите Ваш родной язык",
                                 help_text="Пример: Русский")
    other_lang = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                                 label="Перечислите другие языки, которыми Вы владеете"
                                       "\nУровень владения - выше среднего",
                                 help_text="Пример: Английский, Францусзкий, ...")
    country = forms.CharField(required=False, label="Введите Ваше гражданство",
                              help_text="Пример: Российская Федерация")
    pract_name = forms.CharField(required=False, label="Введите название Вашей практики",
                                 help_text="Пример: Производственная практика")
    pract_period_from = forms.DateField(label="Введите дату начала периода прохождения Вашей практики",
                                        help_text="Пример: 31.12.0001")
    pract_period_to = forms.DateField(label="Введите дату окончания периода прохождения Вашей практики",
                                      help_text="Пример: 31.01.0002")
    pract_jobs = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}),
                                 label="Перечислите задачи, которые необходимо выполнить на практике",
                                 help_text="Пример: Задача 1; задача 2; итд")
    linkedin = forms.URLField(required=False, label="Введите ссылку на Ваш профиль LinkedIn",
                              help_text="Пример: https://www.linkedin.com/in/...")
    pract_tasks = forms.ChoiceField(label="Выберите, какой тип работ Вы хотите выполнять", choices=CHOICES)
    laptop = forms.BooleanField(required=False, label="Укажите наличие у Вас ноутбука")

    class Meta:
        model = Resume
        fields = (
            'photo', 'fio', 'birthday', 'phonenum', 'grade', 'institution', 'curator', 'spec', 'skills', 'projects',
            'project_links', 'education', 'first_lang', 'other_lang', 'country', 'pract_name',
            'pract_period_from', 'pract_period_to', 'pract_jobs', 'linkedin', 'pract_tasks', 'laptop')

    # Валидация полей
    def clean(self):
        cleaned_data = super().clean()
        pract_period_from = cleaned_data.get("pract_period_from")
        pract_period_to = cleaned_data.get("pract_period_to")
        if pract_period_to and pract_period_from:
            if func.checkdate(pract_period_to, pract_period_from, 3) is False:
                self.add_error("pract_period_to", "Период практики указан неверно")
                self.add_error("pract_period_from", "Период практики указан неверно")

    def clean_fio(self, *args, **kwargs):
        fio = self.cleaned_data.get("fio")
        if 100 > len(fio) > 0:
            if func.checkpatt(fio, 4) is not None:
                return fio
            else:
                raise forms.ValidationError("ФИО введено неправильно")
        else:
            raise forms.ValidationError("ФИО введено неправильно")

    def clean_birthday(self, *args, **kwargs):
        birthday = self.cleaned_data.get("birthday")
        if birthday is not None:
            if func.checkdate(date.today(), birthday, 1) is True:
                return birthday
            else:
                raise forms.ValidationError("Дата рождения введена неправильно")
        else:
            return birthday

    def clean_phonenum(self, *args, **kwargs):
        phonenum = self.cleaned_data.get("phonenum")
        if func.checkpatt(phonenum, 5) is not None:
            return phonenum
        else:
            raise forms.ValidationError("Номер телефона введен неправильно")

    def clean_grade(self, *args, **kwargs):
        grade = self.cleaned_data.get("grade")
        if grade is not None:
            if len(grade) == 1 and grade.isdigit() and 1 <= int(grade) <= 7:
                return grade
            else:
                raise forms.ValidationError("Номер курса введен неправильно")
        else:
            return grade

    def clean_institution(self, *args, **kwargs):
        institution = self.cleaned_data.get("institution")
        if 100 >= len(institution) > 0:
            return institution
        else:
            raise forms.ValidationError("Наименование введено неправильно")

    def clean_curator(self, *args, **kwargs):
        curator = self.cleaned_data.get("curator")
        text_list = re.split(" ", curator)
        if len(text_list) == 3 and 100 >= len(curator) > 0:
            return curator
        else:
            raise forms.ValidationError("ФИО куратора введено неправильно")

    def clean_spec(self, *args, **kwargs):
        spec = self.cleaned_data.get("spec")
        if 30 >= len(spec) > 0 or len(spec) <= 0:
            return spec
        else:
            raise forms.ValidationError("Наименование специальности введено неправильно")

    def clean_skills(self, *args, **kwargs):
        skills = self.cleaned_data.get("skills")
        text_list = re.split(";", skills)
        if len(text_list) >= 1 and 300 >= len(skills) > 0 or len(skills) <= 0:
            return skills
        else:
            raise forms.ValidationError("Ключевые навыки введены неправильно")

    def clean_projects(self, *args, **kwargs):
        projects = self.cleaned_data.get("projects")
        text_list = re.split(";", projects)
        if len(text_list) > 1 and len(projects) > 0 or len(projects) <= 0:
            return projects
        else:
            raise forms.ValidationError("Ключевые проекты перечислены неправильно")

    def clean_project_links(self, *args, **kwargs):
        project_links = self.cleaned_data.get("project_links")
        text_list = re.split(";", project_links)
        if len(text_list) > 1 and 500 >= len(project_links) > 0 or len(project_links) <= 0:
            return project_links
        else:
            raise forms.ValidationError("Ссылки на ключевые проекты перечислены неправильно")

    def clean_education(self, *args, **kwargs):
        education = self.cleaned_data.get("education")
        if 100 >= len(education) > 0 or len(education) <= 0:
            return education
        else:
            raise forms.ValidationError("Уровень образования введен неправильно")

    def clean_first_lang(self, *args, **kwargs):
        first_lang = self.cleaned_data.get("first_lang")
        if 20 >= len(first_lang) > 0 or len(first_lang) <= 0:
            return first_lang
        else:
            raise forms.ValidationError("Родной язык введен неправильно")

    def clean_other_lang(self, *args, **kwargs):
        other_lang = self.cleaned_data.get("other_lang")
        if 300 >= len(other_lang) > 0 or len(other_lang) <= 0:
            return other_lang
        else:
            raise forms.ValidationError("Другие языки введены неправильно")

    def clean_country(self, *args, **kwargs):
        country = self.cleaned_data.get("country")
        if 100 >= len(country) > 0 or len(country) <= 0:
            return country
        else:
            raise forms.ValidationError("Гражданство введено неправильно")

    def clean_pract_name(self, *args, **kwargs):
        pract_name = self.cleaned_data.get("pract_name")
        if 100 >= len(pract_name) > 0 or len(pract_name) <= 0:
            return pract_name
        else:
            raise forms.ValidationError("Название практики введено неправильно")

    def clean_pract_jobs(self, *args, **kwargs):
        pract_jobs = self.cleaned_data.get("pract_jobs")
        text_list = re.split(";", pract_jobs)
        if len(text_list) > 1 and 1000 >= len(pract_jobs) > 0:
            return pract_jobs
        else:
            raise forms.ValidationError("Задачи перечислены неправильно")

    def clean_linkedin(self, *args, **kwargs):
        linkedin = self.cleaned_data.get("linkedin")
        if 200 >= len(linkedin) > 0 or len(linkedin) <= 0:
            return linkedin
        else:
            raise forms.ValidationError("Ссылка введена неправильно")

    def clean_pract_tasks(self, *args, **kwargs):
        pract_tasks = self.cleaned_data.get("pract_tasks")
        if 100 >= len(pract_tasks) > 0:
            return pract_tasks
        else:
            raise forms.ValidationError("Тип работ введен неправильно")


# Форма изменения резюме
class UpdResumeForm(forms.ModelForm):
    CHOICES = (
        ('', ''),
        (
            'Простые задачи операционной деятельности организации',
            'Простые задачи операционной деятельности организации'),
        ('Задачи на разработку программных продуктов', 'Задачи на разработку программных продуктов'),
        ('Бизнес анализ для создания программных продуктов', 'Бизнес анализ для создания программных продуктов'),
        ('Дизайн и прототипирование программных продуктов', 'Дизайн и прототипирование программных продуктов'),
        ('Работа с серверами', 'Работа с серверами'),
        ('Системная аналитика', 'Системная аналитика'),
    )
    photo = forms.ImageField(required=False, label="Фотография:")
    fio = forms.CharField(required=False, label="ФИО", help_text="Пример: Петров Петр Петрович")
    birthday = forms.DateField(required=False, label="Дата Вашего рождения",
                               help_text="Пример: 31.12.0001")
    grade = forms.IntegerField(required=False, label="Номер Вашего курса",
                               help_text="Пример: 1")
    institution = forms.CharField(required=False,
                                  label="Наименование Вашего учебного заведения",
                                  help_text="Пример: Московский Государственный Университет / МГУ")
    curator = forms.CharField(required=False,
                              label="ФИО куратора от Вашего учебного заведения",
                              help_text="Пример: Петров Петр Петрович")
    spec = forms.CharField(required=False, label="Наименование Вашей специальности",
                           help_text="Пример: Web-Разработчик")
    skills = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                             label="Ваши ключевые навыки",
                             help_text="Пример: Навык 1; Навык 2; Навык 3;")
    projects = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                               label="Ключевые проекты, реализованные Вами",
                               help_text="Пример: Название проекта 1 - описание проекта 1; название проекта 2 - "
                                         "описание проекта 2; итд")
    project_links = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                                    label="Ссылки на репозитории вышеперечисленных проектов",
                                    help_text="Пример: Ссылка на проект 1; ссылка на проект 2; итд")
    education = forms.CharField(required=False, label="Уровень Вашего образования",
                                help_text="Пример: Среднее специальное")
    first_lang = forms.CharField(required=False, label="Ваш родной язык",
                                 help_text="Пример: Русский")
    other_lang = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False,
                                 label="Другие языки, которыми Вы владеете"
                                       "\nУровень владения - выше среднего",
                                 help_text="Пример: Английский, Францусзкий, ...")
    country = forms.CharField(required=False, label="Ваше гражданство",
                              help_text="Пример: Российская Федерация")
    pract_name = forms.CharField(required=False, label="Название Вашей практики",
                                 help_text="Пример: Производственная практика")
    pract_period_from = forms.DateField(required=False,
                                        label="Дата начала периода прохождения Вашей практики",
                                        help_text="Пример: 01.01.0001")
    pract_period_to = forms.DateField(required=False,
                                      label="Дата окончания периода прохождения Вашей практики",
                                      help_text="Пример: 01.02.0001")
    pract_jobs = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}), required=False,
                                 label="Задачи, которые необходимо выполнить на практике",
                                 help_text="Пример: Задача 1; задача 2; итд")
    linkedin = forms.URLField(required=False, label="Ссылка на Ваш профиль LinkedIn",
                              help_text="Пример: https://www.linkedin.com/in/...")
    pract_tasks = forms.ChoiceField(required=False, label="Какой тип работ Вы хотите выполнять", choices=CHOICES)

    laptop = forms.BooleanField(required=False, label="Наличие у Вас ноутбука")

    class Meta:
        model = Resume
        fields = ('photo', 'fio', 'birthday', 'grade', 'institution', 'curator', 'spec', 'skills', 'projects',
                  'project_links', 'education', 'first_lang', 'other_lang', 'country', 'pract_name',
                  'pract_period_from', 'pract_period_to', 'pract_jobs', 'linkedin', 'pract_tasks', 'laptop')

    # Валидация полей
    def clean(self):
        cleaned_data = super().clean()
        pract_period_from = cleaned_data.get("pract_period_from")
        pract_period_to = cleaned_data.get("pract_period_to")
        if pract_period_to or pract_period_from:
            if pract_period_to:
                if pract_period_from:
                    if func.checkdate(pract_period_to, pract_period_from, 3) is False:
                        self.add_error("pract_period_to", "Период практики указан неверно")
                        self.add_error("pract_period_from", "Период практики указан неверно")
                else:
                    self.add_error("pract_period_to", "Необходимо также указать дату начала практики")
                    self.add_error("pract_period_from", "Обязательное поле")
            else:
                self.add_error("pract_period_to", "Обязательное поле")
                self.add_error("pract_period_from", "Необходимо также указать дату окончания практики")

    def clean_fio(self, *args, **kwargs):
        fio = self.cleaned_data.get("fio")
        if 100 > len(fio) > 0 or len(fio) <= 0:
            if len(fio) <= 0:
                return fio
            else:
                if func.checkpatt(fio, 4) is not None:
                    return fio
                else:
                    raise forms.ValidationError("ФИО введено неправильно")
        else:
            raise forms.ValidationError("ФИО введено неправильно")

    def clean_birthday(self, *args, **kwargs):
        birthday = self.cleaned_data.get("birthday")
        if birthday is not None:
            if func.checkdate(date.today(), birthday, 1) is True:
                return birthday
            else:
                raise forms.ValidationError("Дата рождения введена неправильно")
        else:
            return birthday

    def clean_grade(self, *args, **kwargs):
        grade = self.cleaned_data.get("grade")
        if grade is not None:
            if len(grade) == 1 and grade.isdigit() and 1 <= int(grade) <= 7:
                return grade
            else:
                raise forms.ValidationError("Номер курса введен неправильно")
        else:
            return grade

    def clean_institution(self, *args, **kwargs):
        institution = self.cleaned_data.get("institution")
        if 100 >= len(institution) > 0 or len(institution) <= 0:
            return institution
        else:
            raise forms.ValidationError("Наименование введено неправильно")

    def clean_curator(self, *args, **kwargs):
        curator = self.cleaned_data.get("curator")
        text_list = re.split(" ", curator)
        if len(text_list) == 3 and 100 >= len(curator) > 0 or len(curator) <= 0:
            return curator
        else:
            raise forms.ValidationError("ФИО куратора введено неправильно")

    def clean_spec(self, *args, **kwargs):
        spec = self.cleaned_data.get("spec")
        if 30 >= len(spec) > 0 or len(spec) <= 0:
            return spec
        else:
            raise forms.ValidationError("Наименование специальности введено неправильно")

    def clean_skills(self, *args, **kwargs):
        skills = self.cleaned_data.get("skills")
        text_list = re.split(";", skills)
        if len(text_list) >= 1 and 300 >= len(skills) > 0 or len(skills) <= 0:
            return skills
        else:
            raise forms.ValidationError("Ключевые навыки введены неправильно")

    def clean_projects(self, *args, **kwargs):
        projects = self.cleaned_data.get("projects")
        text_list = re.split(";", projects)
        if len(text_list) > 1 and len(projects) > 0 or len(projects) <= 0:
            return projects
        else:
            raise forms.ValidationError("Ключевые проекты перечислены неправильно")

    def clean_project_links(self, *args, **kwargs):
        project_links = self.cleaned_data.get("project_links")
        text_list = re.split(";", project_links)
        if len(text_list) > 1 and 500 >= len(project_links) > 0 or len(project_links) <= 0:
            return project_links
        else:
            raise forms.ValidationError("Ссылки на ключевые проекты перечислены неправильно")

    def clean_education(self, *args, **kwargs):
        education = self.cleaned_data.get("education")
        if 100 >= len(education) > 0 or len(education) <= 0:
            return education
        else:
            raise forms.ValidationError("Уровень образования введен неправильно")

    def clean_first_lang(self, *args, **kwargs):
        first_lang = self.cleaned_data.get("first_lang")
        if 20 >= len(first_lang) > 0 or len(first_lang) <= 0:
            return first_lang
        else:
            raise forms.ValidationError("Родной язык введен неправильно")

    def clean_other_lang(self, *args, **kwargs):
        other_lang = self.cleaned_data.get("other_lang")
        if 300 >= len(other_lang) > 0 or len(other_lang) <= 0:
            return other_lang
        else:
            raise forms.ValidationError("Другие языки введены неправильно")

    def clean_country(self, *args, **kwargs):
        country = self.cleaned_data.get("country")
        if 100 >= len(country) > 0 or len(country) <= 0:
            return country
        else:
            raise forms.ValidationError("Гражданство введено неправильно")

    def clean_pract_name(self, *args, **kwargs):
        pract_name = self.cleaned_data.get("pract_name")
        if 100 >= len(pract_name) > 0 or len(pract_name) <= 0:
            return pract_name
        else:
            raise forms.ValidationError("Название практики введено неправильно")

    def clean_pract_jobs(self, *args, **kwargs):
        pract_jobs = self.cleaned_data.get("pract_jobs")
        text_list = re.split(";", pract_jobs)
        if len(text_list) > 1 and 1000 >= len(pract_jobs) > 0 or len(pract_jobs) <= 0:
            return pract_jobs
        else:
            raise forms.ValidationError("Задачи перечислены неправильно")

    def clean_linkedin(self, *args, **kwargs):
        linkedin = self.cleaned_data.get("linkedin")
        if 200 >= len(linkedin) > 0 or len(linkedin) <= 0:
            return linkedin
        else:
            raise forms.ValidationError("Ссылка введена неправильно")

    def clean_pract_tasks(self, *args, **kwargs):
        pract_tasks = self.cleaned_data.get("pract_tasks")
        if 100 >= len(pract_tasks) > 0 or len(pract_tasks) <= 0:
            return pract_tasks
        else:
            raise forms.ValidationError("Тип работ введен неправильно")

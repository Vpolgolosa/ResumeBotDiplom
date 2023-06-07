Telegram Bot on aiogram, with Django web interface
Установка:
При создании руководства использовались:
	Веб-сервер Apache на ОС Ubuntu с установленной на него структурой баз данных MariaDB и веб-интерфейсом hestia;
	Разворачиваемый проект на Django версии 4.1.7 с использованием базы данных SQLite и двумя приложениями (Django apps):
o	Приложение веб-интерфейса со стандартной структурой приложения;
o	Приложение Telegram-бота со следующей структурой, где файл bot.py является исполняемым:
 ![image](https://github.com/Vpolgolosa/ResumeBotDiplom/assets/73917745/f7e24848-f970-4721-b394-8851b07d4f29)
Рисунок 1 - файловая структура приложения Telegram-бота

	Интернет-ресурсы с советами по развертыванию:
o	https://github.com/jonlachmann/hestiacp-wsgi - запуск развернутого проекта на сервере через apache wsgi;
o	https://www.digitalocean.com/community/tutorials/how-to-install-the-django-web-framework-on-ubuntu-18-04-ru - установка библиотек и разворачивание проекта на сервере;
o	https://stackoverflow.com/questions/3034910/whats-the-best-way-to-migrate-a-django-db-from-sqlite-to-mysql - перенос данных из старой БД в новую;
o	https://www.digitalocean.com/community/tutorials/how-to-use-mysql-or-mariadb-with-your-django-application-on-ubuntu-14-04 - перенос моделей БД на MariaDB (или на MySQL);
Ход развертывания:
1.	Установка необходимых библиотек на сервере:
a.	Во-первых, необходимо обновить локальный индекс пакетов с помощью команды «sudo apt update»
b.	Теперь, по очереди выполняем приведенные ниже команды:
	sudo apt install python3 – устанавливаем Python версии 3 (необходимо указать версию, используемую при разработке проекта);
	sudo apt install python3-pip – устанавливаем систему управления пакетами Python;
	sudo apt install python3-venv – устанавливаем систему управления виртуальными пространствами Python;
	sudo apt-get install libapache2-mod-wsgi-py3 – устанавливаем модуль wsgi для apache;
	sudo apt-get install libmariadbclient-dev – устанавливаем библиотеку для связывания моделей БД нашего проекта со структурой баз данных сервера. На более поздних версиях ОС Ubuntu libmariadbclient-dev меняем на libmariadb-dev, так как эту библиотеку удалили из последних версий ОС;
	a2enmod wsgi – активируем модуль wsgi;
	wget https://github.com/jonlachmann/hestiacp-wsgi/archive/refs/heads/master.zip - скачиваем шаблон wsgi;
	unzip master.zip – разархивируем скачанный шаблон;
	sudo cp hestiacp-wsgi-master/apache2/* /usr/local/hestia/data/templates/web/apache2/php-fpm/ - копируем файлы из архива в директорию apache;
2.	Развертывание проекта на сервере:
a.	Создаем домен на сервере через веб-интерфейс и создаем базу данных;
![image](https://github.com/Vpolgolosa/ResumeBotDiplom/assets/73917745/42d5f506-453f-4ad3-827a-55ef7c4d50a7)
Рисунок 2 - Создание домена
![image](https://github.com/Vpolgolosa/ResumeBotDiplom/assets/73917745/238e4f35-f16d-4965-8de8-b0febe623c1e)
Рисунок 3 - Создание базы данных

b.	Возвращаемся в терминал и переходим в папку private в директории нашего домена с помощью команды «cd …/web/имя домена/private»;
c.	Выполняем следующие команды:
	python3 -m venv venv – создаем виртуальную среду в папке private с именем venv. Имя среды менять не желательно;
	source venv/bin/activate – активируем виртуальную среду;
	Устанавливаем библиотеки, используемые в нашем проекте. В моем случае это:
•	pip install Django~=4.1.7 – установка Django;
•	pip install aiogram~=2.19 – установка библиотеки для Telegram-бота;
•	pip install asgiref~=3.6.0 – установка библиотеки для работы асинхронных функций на синхронном Django;
•	pip install mysqlclient – установка библиотеки для работы с базой данных. Обязательный пункт при переносе БД на серверную структуру баз данных.
d.	В панели Hestia переходим в файловый менеджер и переходим в директорию нашего домена. В папке private создаем папку app. Загружаем файлы нашего проекта в папку app. Результат должен выглядеть примерно так:
![image](https://github.com/Vpolgolosa/ResumeBotDiplom/assets/73917745/d3626b7e-efd7-435f-80cc-fbe7b47b3c16)
Рисунок 4 - Загруженные файлы проекта
 
e.	В терминале вводим следующую команду:
	python -Xutf8 app/manage.py dumpdata --exclude contenttypes --exclude auth.permission --exclude sessions --indent 2 > app/datadump.json – создаем дамп нашей базы данных; 
f.	В панели Hestia, заходим в папку, в которой у нас находится файл settings.py. Редактируем содержимое файлов в данной папке:
	В settings.py:
•	Редактируем ALLOWED_HOSTS:
ALLOWED_HOSTS = ['IP сервера', 'имя домена']
•	Редактируем DATABASES:
DATABASES = {
    'default': {
      'ENGINE': 'django.db.backends.mysql',
      'NAME': 'Имя бд',
      'USER':'Имя админа бд',
      'PASSWORD':'Пароль админа бд',
      'HOST':'localhost',
      'PORT':'',
      'OPTIONS': {'charset': 'utf8mb4',},
    }
}
	В wsgi.py:
import os
import sys
path = '/home/Имя пользователя/web/Домен/private/app'
if path not in sys.path:
    sys.path.insert(0, path)    
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Название_папки_с_settings.py_.settings')
application = get_wsgi_application()
g.	Копируем файл wsgi.py в корневую папку проекта (папку app);
h.	В терминале вводим следующие команды:
	python app/manage.py migrate – переносим модели БД нашего проекта на структуру БД сервера;
	python app/manage.py loaddata app/datadump.json – загружаем в БД сервера дамп БД нашего проекта;
 
	export PYTHONIOENCODING="UTF-8"; python3 app/manage.py createsuperuser – создаем суперпользователя. Эта команда необходима только тогда, когда загрузка дампа не удалась и БД осталась пустой;
	python manage.py collectstatic – копируем все статические файлы нашего проекта (css, js, логотипы и т.п.) в папку static в корневой папке нашего проекта;
	deactivate – выходим из виртуальной среды.
i.	Копируем папку static из корневой папки нашего проекта (private/app) в папку public_html;
j.	Выходим в контрольную панель Hestia и настраиваем наш домен как на скриншоте:
![image](https://github.com/Vpolgolosa/ResumeBotDiplom/assets/73917745/23a82210-8579-4265-81f0-7288a61448f9)
Рисунок 5 - Настройка домена
k.	Вводим в терминале команды:
	touch app/wsgi.py – команда переподключения нашего домена к серверу. Если Вам будет необходимо ввести изменения в уже развернутый код, необходимо будет выполнить эту команду для того, чтобы изменения вступили в силу;
	source venv/bin/activate;
	nohup python3 -u app/manage.py bot > output.log & - запуск Telegram-бота в фоновом режиме.

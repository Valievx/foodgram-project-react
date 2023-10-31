# Дипломный проект Foodgram
Url - https://foodinst.ddns.net
### 1.Описание
Веб-Cервис Foodgram - Проект где его участники могут делится друг с другом своими рецептами.
Проект обладает такими возможностями как:
1. Создавать собственные рецепты и редактировать их
2. Добавлять понравившиеся рецепты в "Избранное" и в "Корзину"
3. Подписываться на авторов и быть в курсе их последних рецептов
4. Добавлять ингедиенты рецепта в "Корзину" и скачивать список в .txt формате

### 2.Установка Docker (на платформе Ubuntu) 
Веб-Cервис Foodgram поставляется в четырех контейнерах Docker (db, frontend, backend, nginx).
Для запуска необходимо установить Docker и Docker Compose.
Подробнее об установке можно узнать на https://docs.docker.com/engine/install/

1.Обновите пакеты:
```
sudo apt update
```
2.Установите пакеты, которые необходимы для работы пакетного менеджера apt по протоколу HTTPS:
```
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```
3.Добавьте GPG-ключ репозитория Docker:
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```
4.Добавьте репозиторий Docker:
```
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
```
5.Обновите пакеты:
```
sudo apt update
```
6.Переключитесь в репозиторий Docker, чтобы его установить:
```
apt-cache policy docker-ce
```
7.Установите Docker:
```
sudo apt install docker-ce
```
8.Проверьте работоспособность программы:
```
sudo systemctl status docker
```
9.Чтобы использовать утилиту docker, нужно добавить ваше имя пользователя в группу Docker. 
```
sudo usermod -aG docker ${user}
```
Где user — имя пользователя.
10.Введите:
```
su - ${user}
```
Где user — имя пользователя.
11.Задайте пароль пользователя.
12.Проверьте доступ к образам Docker:
```
docker run hello-world
```

### 3.База данных и переменные окружения 
Веб-Cервис Foodgram использует базу данных PostgreSQL.
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" 
с переменными окружения в папке "./infra/".

Шаблон для заполнения файла ".env":
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_USER=postgres
POSTGRES_PASSWORD=thepaik88
DB_HOST=db
DB_PORT=5432
SECRET_KEY='Cекретный ключ'
ALLOWED_HOSTS='Имя или IP хоста' (Для локального запуска - 127.0.0.1)
```

### 4.Команды для запуска 
1. Перед запуском необходимо склонировать проект:
```
SSH: git@github.com:Valievx/foodgram-project-react.git
```
2. Cоздать и активировать виртуальное окружение:
```
python -m venv venv
source venv/bin/activate
```
3. Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
4. Собрать образы для фронтенда и бэкенда.
Из директории "./backend/foodgram/" выполнить команду:
```
docker build -t theosmi808/foodgram_backend .
```
Из директории "./frontend/" выполнить команду:
```
docker build -t theosmi808/foodgram_frontend .
```
Из директории "./infra/" выполнить команду:
```
docker-compose up -d
```
5. После запуска контейнеров выполнить миграции:
```
docker-compose exec backend python manage.py migrate
```
6. Создать Суперюзера:
```
docker-compose exec backend python manage.py createsuperuser
```
7. Собрать статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
Теперь доступность проекта можно проверить по адресу http://localhost/

### 5.Заполнение базы данных 
С Веб-Cервисом Foodgram поставляется БД с ингредиентами
Заполнить базу данных ингредиентами можно выполнив следующую команду из папки "./infra/":
```
docker compose exec backend python manage.py load_ingredients_data 
```
Также необходимо заполнить базу данных тегами.
Для этого требуется войти в админ-зону проекта под логином и паролем суперпользователя

### 6.Техническая информация 
Стек технологий: Python 3, Django, Django Rest, React, Docker, PostgreSQL, nginx, gunicorn, Djoser.

Веб-сервер: nginx (контейнер nginx)
Frontend фреймворк: React (контейнер frontend)
Backend фреймворк: Django (контейнер backend)
API фреймворк: Django REST (контейнер backend)
База данных: PostgreSQL (контейнер db)

Веб-сервер nginx перенаправляет запросы клиентов к контейнерам frontend и backend, либо к хранилищам (volume) статики и файлов.
Контейнер nginx взаимодействует с контейнером backend через gunicorn.
Контейнер frontend взаимодействует с контейнером backend посредством API-запросов.


### 7.Об авторе 
Валиев Александр Альфредович
Python-разработчик (Backend)
E-mail: worxvaliev@gmail.com
Telegram: @valiev88

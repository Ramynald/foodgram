Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

# Foodgram

## Описание проекта

Foodgram — сервис для публикации рецептов.

Пользователи могут:

- создавать рецепты;
- добавлять рецепты в избранное;
- подписываться на авторов;
- формировать список покупок.

Проект развёрнут в Docker-контейнерах и автоматизирован с помощью GitHub Actions для тестирования и деплоя.

## Используемые технологии

- Python 3.12
- Django
- Django REST Framework (DRF)
- PostgreSQL
- Docker
- Docker Compose
- Nginx
- Gunicorn
- GitHub Actions
- React

## Адрес проекта

http://178.154.209.56

## Запуск проекта

Клонируйте репозиторий:

https://github.com/Ramynald/foodgram.git

Перейдите в папку проекта:

cd foodgram

Создайте файл .env и заполните его необходимыми переменными окружения.

Запустите контейнеры:

docker compose up -d

Выполните миграции:

docker compose exec backend python manage.py migrate

Соберите статику:

docker compose exec backend python manage.py collectstatic --noinput

## Автор

Подгородецкий Андрей

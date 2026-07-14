# Foodgram

## Описание проекта

**Foodgram** — сервис для публикации рецептов.

Пользователи могут:

- создавать и редактировать рецепты;
- добавлять рецепты в избранное;
- подписываться на авторов;
- формировать список покупок;
- скачивать список покупок.

Проект разработан на Django, использует Django REST Framework и PostgreSQL, запускается в Docker-контейнерах и автоматизирован с помощью GitHub Actions.

---

## Используемые технологии

- Python 3.12
- Django
- Django REST Framework (DRF)
- PostgreSQL
- Docker
- Docker Compose
- Gunicorn
- Nginx
- GitHub Actions
- React

---

## Запуск проекта

### Клонирование репозитория

```bash
git clone https://github.com/Ramynald/foodgram.git
cd foodgram
```

### Создание файла окружения

Создайте файл `.env` в корне проекта и заполните его необходимыми переменными окружения.

### Запуск контейнеров

```bash
docker compose up -d
```

### Применение миграций

```bash
docker compose exec backend python manage.py migrate
```

### Сбор статических файлов

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

### Запуск проекта

После выполнения всех команд приложение будет доступно локально.

---

## Особенности проекта

- REST API
- Docker-контейнеризация
- PostgreSQL
- GitHub Actions (CI/CD)
- Авторизация пользователей
- Работа с рецептами
- Избранное
- Подписки
- Список покупок

---

## Автор

**Неля Романенко**

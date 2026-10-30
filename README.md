# Bookshelf — каталог книг (Django + Django REST Framework)

[![tests](https://github.com/pybyOx/bookshelf/actions/workflows/tests.yml/badge.svg)](https://github.com/pybyOx/bookshelf/actions/workflows/tests.yml)

Веб-приложение «книжная полка»: каталог книг с веб-интерфейсом и REST API. Пет-проект, задеплоен в production.

🔗 **Живой сайт:** https://bookshelf-leee.onrender.com/books/

## Возможности

- **Веб-интерфейс на Django:** список и детальная страница книг, добавление / редактирование / удаление через формы, наследование шаблонов, админка.
- **REST API на Django REST Framework:** сериализаторы, ViewSets, роутеры, пагинация.
- **Аутентификация и права:** токен-аутентификация; owner-based permissions — свою запись редактирует только её владелец.
- **Тесты:** pytest + `APITestCase` (позитивные и негативные сценарии, проверка прав).

## Стек

- Python, Django, Django REST Framework
- PostgreSQL (production и Docker), SQLite (локально без Docker)
- pytest, gunicorn, WhiteNoise
- Docker, Docker Compose
- Деплой: Render (авто-деплой из GitHub при пуше)

## Запуск локально

```bash
git clone https://github.com/pybyOx/bookshelf.git
cd bookshelf
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # заполнить SECRET_KEY
python manage.py migrate
python manage.py runserver
```

Открыть: http://127.0.0.1:8000/books/

## Тесты

```bash
pip install -r requirements-dev.txt   # pytest и pytest-django поверх основных зависимостей
pytest -q
```

14 тестов на `APITestCase` в `books/tests.py`: CRUD через API, права владельца, негативные сценарии.
Прогон идёт на настройках `bookshelf/settings_test.py` (отключён `SECURE_SSL_REDIRECT`, иначе тестовый клиент получает редирект 301).
На каждый пуш в `main` и на каждый pull request те же тесты гоняет GitHub Actions — см. бейдж выше.

## Запуск через Docker

Нужен только установленный Docker — Python и PostgreSQL ставить не надо:

```bash
git clone https://github.com/pybyOx/bookshelf.git
cd bookshelf
docker compose up --build
```

Поднимутся два контейнера: приложение (gunicorn) и PostgreSQL. Сборка статики и миграции выполняются автоматически при старте.

Открыть: http://localhost:8000/books/

- База стартует пустой. Создать администратора: `docker compose exec web python manage.py createsuperuser`
- Остановить: `Ctrl+C` или `docker compose down` (данные базы сохраняются в томе `pgdata`)

## API

- `GET/POST /api/books/` — список книг / создание
- `GET/PUT/PATCH/DELETE /api/books/<id>/` — операции над конкретной книгой

Доступен DRF Browsable API по адресу `/api/books/`.

## Деплой

Задеплоен на [Render](https://render.com) из этого репозитория: образ собирается по `Dockerfile`, статика собирается на этапе сборки образа, миграции применяются при старте контейнера. База — PostgreSQL на [Neon](https://neon.com), адрес передаётся через переменную окружения `DATABASE_URL`. Раздача статики — WhiteNoise, HTTPS и переменные окружения — на стороне Render.

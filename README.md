# Bookshelf — каталог книг (Django + Django REST Framework)

Веб-приложение «книжная полка»: каталог книг с веб-интерфейсом и REST API. Пет-проект, задеплоен в production.

🔗 **Живой сайт:** https://bookshelf-leee.onrender.com/books/

## Возможности

- **Веб-интерфейс на Django:** список и детальная страница книг, добавление / редактирование / удаление через формы, наследование шаблонов, админка.
- **REST API на Django REST Framework:** сериализаторы, ViewSets, роутеры, пагинация.
- **Аутентификация и права:** токен-аутентификация; owner-based permissions — свою запись редактирует только её владелец.
- **Тесты:** pytest + `APITestCase` (позитивные и негативные сценарии, проверка прав).

## Стек

- Python, Django, Django REST Framework
- PostgreSQL (production), SQLite (локально)
- pytest, gunicorn, WhiteNoise
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

## API

- `GET/POST /api/books/` — список книг / создание
- `GET/PUT/PATCH/DELETE /api/books/<id>/` — операции над конкретной книгой

Доступен DRF Browsable API по адресу `/api/books/`.

## Деплой

Задеплоен на [Render](https://render.com): PostgreSQL, gunicorn, WhiteNoise (раздача статики), HTTPS, конфигурация через переменные окружения. Сборка описана в `build.sh` (установка зависимостей → `collectstatic` → `migrate`).

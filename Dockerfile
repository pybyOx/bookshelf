# Базовый образ: Python (slim = лёгкая версия)
FROM python:3.13-slim

# Настройки Python для контейнера
# не создавать .pyc-файлы (кэш не нужен)
ENV PYTHONDONTWRITEBYTECODE=1
# не буферизовать вывод (логи видны сразу)
ENV PYTHONUNBUFFERED=1

# Рабочая папка внутри контейнера (всё дальше — относительно неё)
WORKDIR /app

# Сначала копируем зависимости и ставим их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем весь остальной проект внутрь образа
COPY . .

# Собираем статику внутрь образа — на этапе сборки, файлам база не нужна.
# SECRET_KEY подставляем фиктивный: settings.py читает его через os.environ[...]
# и без него падает с KeyError, а collectstatic настоящий ключ не использует.
RUN SECRET_KEY=build-only-dummy python manage.py collectstatic --no-input

# Обозначаем порт, на котором будет слушать gunicorn
EXPOSE 8000

# При старте: сначала миграции (база доступна только сейчас, не при сборке),
# затем боевой сервер. PORT приходит от хостинга, локально берётся 8000.
CMD ["sh", "-c", "python manage.py migrate && gunicorn bookshelf.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
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

# Обозначаем порт, на котором будет слушать gunicorn
EXPOSE 8000

# Что запустить при старте контейнера — боевой сервер gunicorn
CMD ["gunicorn", "bookshelf.wsgi:application", "--bind", "0.0.0.0:8000"]
#!/usr/bin/env bash
# Скрипт сборки для Render. Выполняется при каждом деплое.
set -o errexit  # при любой ошибке — сразу выход (не продолжать сборку)

# 1. Установить зависимости
pip install -r requirements.txt

# 2. Собрать статику в STATIC_ROOT (её раздаёт whitenoise)
python manage.py collectstatic --no-input

# 3. Применить миграции к базе PostgreSQL
python manage.py migrate

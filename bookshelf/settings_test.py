"""Настройки для прогона тестов — локально и в CI.

Берём обычные настройки и отключаем то, что мешает тестовому клиенту:
при DEBUG=False в settings.py включается SECURE_SSL_REDIRECT, и тогда
клиент на каждый запрос получает редирект 301 вместо ответа API.
"""

from .settings import *  # noqa: F401,F403

SECURE_SSL_REDIRECT = False

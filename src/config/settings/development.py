"""Настройки для разработки на своём компьютере."""
from .base import *


DEBUG = True

ALLOWED_HOSTS = ALLOWED_HOSTS or ['localhost', '127.0.0.1']

# Письма (подтверждение email, сброс пароля) печатаются в лог контейнера
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

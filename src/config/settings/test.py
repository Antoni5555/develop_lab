"""Настройки для pytest."""
from .base import *


# Кэш в памяти — тестам не нужен запущенный Redis
CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'},
}

# Быстрый хешер паролей: тесты с пользователями идут в разы быстрее
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

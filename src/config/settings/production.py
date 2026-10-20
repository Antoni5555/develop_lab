"""Настройки для сервера: DEBUG выключен, только HTTPS."""
from .base import *


DEBUG = False

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

# collectstatic добавляет к файлам хеш (base.3f9a1c.css) — браузер может
# кэшировать их надолго, а после изменения файла получит новый адрес
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}

# HTTPS завершается на Nginx, он передаёт схему в заголовке
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Без этого при DEBUG = False ошибки 500 не попадают в логи контейнера
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}

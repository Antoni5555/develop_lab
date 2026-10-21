"""Настройки для сервера: DEBUG выключен, только HTTPS."""
from .base import *


DEBUG = False

CSRF_TRUSTED_ORIGINS = env_list('CSRF_TRUSTED_ORIGINS')

# collectstatic добавляет к файлам хеш (base.3f9a1c.css) — браузер может
# кэшировать их надолго, а после изменения файла получит новый адрес
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'core.storage.StaticStorage',

    },
}

# HTTPS завершается на Nginx, он передаёт схему в заголовке
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# Preload (вшить домен в браузеры как «только HTTPS») почти не отменить —
# решим, когда будет постоянный домен. Пока предупреждение check --deploy глушим.
SILENCED_SYSTEM_CHECKS = ['security.W021']
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Соединение с базой живёт до минуты, а не открывается на каждый запрос
DATABASES['default']['CONN_MAX_AGE'] = 60
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

# Почта (SMTP) — настройки из .env. Пока SMTP не настроен (EMAIL_HOST пуст),
# письма пишутся в лог контейнера: иначе регистрация падала бы с ошибкой 500
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
if EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
# Письма об ошибках сервера — с того же адреса, что и письма пользователям
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Без этого при DEBUG = False ошибки 500 не попадают в логи контейнера
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}

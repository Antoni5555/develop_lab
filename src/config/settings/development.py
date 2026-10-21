"""Настройки для разработки на своём компьютере."""
from .base import *


DEBUG = True

ALLOWED_HOSTS = ALLOWED_HOSTS or ['localhost', '127.0.0.1']

# Письма (подтверждение email, сброс пароля). В Docker Compose — в Mailpit:
# локальный почтовый ящик, письма видны на http://localhost:8025.
# Без EMAIL_HOST (manage.py с компьютера) — печатаются в консоль.
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
if EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '1025'))
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

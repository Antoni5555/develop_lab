"""Общие настройки для всех окружений.

development.py, production.py и test.py импортируют всё отсюда
и меняют только то, что отличается.
"""
import os
from pathlib import Path

from dotenv import load_dotenv


# src/ — здесь manage.py, приложения, шаблоны и статика
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env лежит в корне репозитория (на уровень выше src/).
# Переменные, уже заданные в окружении (например, Docker Compose), не перезаписываются.
load_dotenv(BASE_DIR.parent / '.env')


def env_list(name, default=''):
    """Читает из окружения список через запятую: 'a, b' → ['a', 'b']."""
    items = os.getenv(name, default).split(',')
    return [item.strip() for item in items if item.strip()]


SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError('SECRET_KEY is not set')

DEBUG = False

ALLOWED_HOSTS = env_list('ALLOWED_HOSTS')

# Название сайта ещё не выбрано — берём из .env, в шаблонах это {{ SITE_NAME }}
SITE_NAME = os.getenv('SITE_NAME', 'SITE_NAME')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core.apps.CoreConfig',
    'apps.pages.apps.PagesConfig',
    'apps.courses.apps.CoursesConfig',
    'apps.cheatsheets.apps.CheatsheetsConfig',
    'apps.trainers.apps.TrainersConfig',
    'apps.accounts.apps.AccountsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.site',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# PostgreSQL во всех окружениях — чтобы не ловить различия SQLite и Postgres на сервере
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Redis: один кэш на все воркеры Gunicorn (LocMem у каждого воркера свой)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    }
}


_VALIDATORS = 'django.contrib.auth.password_validation'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': f'{_VALIDATORS}.UserAttributeSimilarityValidator'},
    {'NAME': f'{_VALIDATORS}.MinimumLengthValidator'},
    {'NAME': f'{_VALIDATORS}.CommonPasswordValidator'},
    {'NAME': f'{_VALIDATORS}.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Уроки и задачи (папка content/ в корне репозитория). Загружаются командой
# manage.py load_content; в Docker папка подключена в /content
CONTENT_DIR = Path(os.getenv('CONTENT_DIR', BASE_DIR.parent / 'content'))

# Pyodide (Python в браузере) — с CDN jsDelivr: ~13 МБ, хранить в репозитории невыгодно.
# Версия 0.27 — внутри Python 3.12, как в формате контента (тексты ошибок совпадают).
PYODIDE_URL = os.getenv(
    'PYODIDE_URL', 'https://cdn.jsdelivr.net/pyodide/v0.27.8/full/',
)

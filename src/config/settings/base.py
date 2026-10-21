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

    'allauth',
    'allauth.account',
    'rest_framework',

    'core.apps.CoreConfig',
    'apps.pages.apps.PagesConfig',
    'apps.courses.apps.CoursesConfig',
    'apps.cheatsheets.apps.CheatsheetsConfig',
    'apps.trainers.apps.TrainersConfig',
    'apps.accounts.apps.AccountsConfig',
    'apps.progress.apps.ProgressConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
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


# --- Аккаунты: свой пользователь (вход по email) + django-allauth ---
AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*']   # без повтора пароля и username
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
# + имя, фамилия и согласие на обработку данных
ACCOUNT_FORMS = {'signup': 'apps.accounts.forms.SignupForm'}
ACCOUNT_ADAPTER = 'apps.accounts.adapter.AccountAdapter'
# В сообщениях allauth («Вы вошли как …») — имя, а не email
ACCOUNT_USER_DISPLAY = 'apps.accounts.models.user_display'
# Войти можно только после подтверждения почты: ссылка в письме подтверждает
# сразу при открытии (без второй кнопки) и, в том же браузере, сразу входит
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
# Название сайта — в теме письма (шаблон *_subject.txt), префикс «[сайт]» не нужен
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'accounts:profile'

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@localhost')

# Оператор персональных данных — для страниц «Политика конфиденциальности»
# и «Согласие на обработку данных». В .env, а не в коде: репозиторий публичный,
# а данные зависят от того, кто и где запускает сайт
OPERATOR = {
    'name': os.getenv('OPERATOR_NAME', ''),
    'inn': os.getenv('OPERATOR_INN', ''),
    'city': os.getenv('OPERATOR_CITY', ''),
    'email': os.getenv('OPERATOR_EMAIL', ''),
}


# --- API (DRF): его вызывает JS страниц, вход — обычной сессией сайта (с CSRF) ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
}

# Уроки и задачи (папка content/ в корне репозитория). Загружаются командой
# manage.py load_content; в Docker папка подключена в /content
CONTENT_DIR = Path(os.getenv('CONTENT_DIR', BASE_DIR.parent / 'content'))

# Pyodide (Python в браузере) — с CDN jsDelivr: ~13 МБ, хранить в репозитории невыгодно.
# Версия 0.27 — внутри Python 3.12, как в формате контента (тексты ошибок совпадают).
PYODIDE_URL = os.getenv(
    'PYODIDE_URL', 'https://cdn.jsdelivr.net/pyodide/v0.27.8/full/',
)

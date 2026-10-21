"""Главный роутер: подключает URL всех приложений."""
from django.contrib import admin
from django.urls import include, path

from core.views import health


handler404 = 'core.errors.page_not_found'
handler500 = 'core.errors.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),

    path('', include('apps.pages.urls')),
    path('courses/', include('apps.courses.urls')),
    path('cheatsheets/', include('apps.cheatsheets.urls')),
    # тренажёр подключён к корню: в нём будут и /playground/, и адреса задач
    path('', include('apps.trainers.urls')),
    path('accounts/', include('apps.accounts.urls')),   # профиль
    path('accounts/', include('allauth.urls')),         # вход, регистрация, пароль
    path('api/progress/', include('apps.progress.urls')),
    path('api/notes/', include('apps.cheatsheets.api_urls')),
]

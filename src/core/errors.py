"""Свои страницы ошибок. Подключаются в config/urls.py (handler404, handler500)."""
from django.conf import settings
from django.shortcuts import render


def page_not_found(request, exception):
    """404 — страница не найдена."""
    return render(request, 'errors/404.html', status=404)


def server_error(request):
    """500 — ошибка сервера.

    Рендерим без запроса (context processors не запускаются): если сломалась
    БД или что-то в обработке запроса, страница ошибки не упадёт вслед за ними.
    """
    context = {'SITE_NAME': settings.SITE_NAME}
    return render(None, 'errors/500.html', context, status=500)

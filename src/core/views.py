from django.http import HttpResponse


def health(request):
    """Проверка, что приложение живо (для Docker и мониторинга)."""
    return HttpResponse('ok', content_type='text/plain')

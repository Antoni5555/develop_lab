"""Middleware для разработки."""
from django.conf import settings


class NoCacheStaticMiddleware:
    """Статика в разработке: браузер каждый раз сверяется с сервером.

    runserver отдаёт файлы без хеша в имени и без Cache-Control — браузер
    кэширует их на глазок и после правки CSS показывает старую версию.
    С `no-cache` он спрашивает «изменился ли файл?» (If-Modified-Since):
    не изменился — 304 без тела, изменился — свежий файл.
    На production не нужен: там имена файлов с хешем.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith(settings.STATIC_URL):
            response['Cache-Control'] = 'no-cache'
        return response

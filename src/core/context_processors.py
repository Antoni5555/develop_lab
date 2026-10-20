from django.conf import settings


def site(request):
    """Добавляет во все шаблоны название сайта: {{ SITE_NAME }}."""
    return {'SITE_NAME': settings.SITE_NAME}

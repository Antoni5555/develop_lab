"""Общий код из core/: название сайта, страницы ошибок, health-check."""
import pytest
from django.test import RequestFactory
from django.urls import reverse

from core.errors import server_error


@pytest.mark.django_db
def test_site_name_in_html(client, settings):
    """SITE_NAME из настроек попадает в шапку, подвал и <title>."""
    settings.SITE_NAME = 'Тестовый сайт'

    html = client.get(reverse('pages:home')).content.decode()

    assert '<title>Тестовый сайт</title>' in html
    assert html.count('Тестовый сайт') >= 3


def test_404_uses_own_template(client):
    """Несуществующий адрес → 404 с нашим шаблоном."""
    response = client.get('/no-such-page/')

    assert response.status_code == 404
    assert 'errors/404.html' in [t.name for t in response.templates]


def test_500_renders_without_request_context(settings):
    """Страница 500 рендерится сама по себе и показывает SITE_NAME."""
    settings.SITE_NAME = 'Тестовый сайт'
    request = RequestFactory().get('/')

    response = server_error(request)

    assert response.status_code == 500
    assert 'Тестовый сайт' in response.content.decode()


def test_health(client):
    """/health/ отвечает ok — по нему Docker понимает, что приложение живо."""
    response = client.get(reverse('health'))

    assert response.status_code == 200
    assert response.content == b'ok'

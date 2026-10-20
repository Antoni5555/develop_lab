"""Страницы этапа 0: открываются, рендерят свой шаблон, подсвечивают пункт меню."""
import pytest
from django.urls import reverse


# каталог и главная читают курсы из БД
pytestmark = pytest.mark.django_db

PAGES = [
    # (имя URL, шаблон, активный пункт меню)
    ('pages:home', 'home/home.html', 'home'),
    ('pages:about', 'about/about.html', 'about'),
    ('courses:list', 'courses/course_list.html', 'courses'),
    ('cheatsheets:list', 'cheatsheets/cheatsheet_list.html', 'cheatsheets'),
    ('trainers:playground', 'trainers/playground.html', 'playground'),


    ('accounts:login', 'accounts/login.html', None),
    ('accounts:signup', 'accounts/signup.html', None),
    ('accounts:profile', 'accounts/profile.html', None),
]


@pytest.mark.parametrize('url_name, template, active_nav', PAGES)
def test_page_opens(client, url_name, template, active_nav):
    """Страница отдаёт 200 и рендерит ожидаемый шаблон внутри base.html."""
    response = client.get(reverse(url_name))

    assert response.status_code == 200
    names = [t.name for t in response.templates]
    assert template in names
    assert 'base/base.html' in names
    assert response.context.get('active_nav') == active_nav


@pytest.mark.parametrize('url_name, template, active_nav', PAGES)
def test_active_nav_link(client, url_name, template, active_nav):
    """В меню подсвечен ровно один нужный пункт (в шапке и в мобильном меню)."""
    html = client.get(reverse(url_name)).content.decode()

    if active_nav is None:
        assert 'nav-link--active' not in html
        return
    # пункт меню ведёт на эту же страницу и есть дважды: в шапке и в мобильном меню
    active_link = f'href="{reverse(url_name)}" class="nav-link nav-link--active"'
    assert html.count(active_link) == 2
    assert html.count('nav-link--active') == 2


def test_page_css_only_on_own_page(client):
    """Каждая страница грузит только свой CSS из pages/."""
    html = client.get(reverse('pages:home')).content.decode()

    assert 'css/pages/home.css' in html
    assert 'css/pages/about.css' not in html

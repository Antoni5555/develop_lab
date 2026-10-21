"""Аккаунты: регистрация и вход по email (django-allauth), профиль, шапка."""
import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse

from tests.factories import UserFactory


pytestmark = pytest.mark.django_db

User = get_user_model()


def test_user_is_identified_by_email():
    user = User.objects.create_user(email='Anna@Example.com', password='x')

    assert user.email == 'Anna@example.com'   # домен — в нижнем регистре
    assert User.USERNAME_FIELD == 'email'
    assert user.display_name == 'Anna'
    assert user.initials == 'A'


def test_display_name_and_initials_from_full_name():
    user = User(email='ivan@example.com', first_name='Иван', last_name='Петров')

    assert user.display_name == 'Иван Петров'
    assert user.initials == 'ИП'


def test_create_superuser():
    admin = User.objects.create_superuser(email='admin@example.com', password='x')

    assert admin.is_staff and admin.is_superuser


def test_signup_with_email_and_password(client):
    response = client.post(reverse('account_signup'), {
        'email': 'new@example.com', 'password1': 'Long-enough-pass-1',
    })

    assert response.status_code == 302
    assert response.url == reverse('accounts:profile')
    user = User.objects.get(email='new@example.com')
    assert client.session['_auth_user_id'] == str(user.pk)
    # письмо с подтверждением ушло, но вход не ждёт подтверждения
    assert len(mail.outbox) == 1 and 'new@example.com' in mail.outbox[0].to


def test_signup_rejects_short_password(client):
    response = client.post(reverse('account_signup'), {
        'email': 'new@example.com', 'password1': '123',
    })

    assert response.status_code == 200
    assert 'field__error' in response.content.decode()
    assert not User.objects.filter(email='new@example.com').exists()


def test_login_and_logout(client):
    UserFactory(email='anna@example.com')

    response = client.post(reverse('account_login'), {
        'login': 'anna@example.com', 'password': 'secret-pass-123',
    })
    assert response.status_code == 302

    response = client.post(reverse('account_logout'))
    assert response.status_code == 302
    assert '_auth_user_id' not in client.session


def test_login_wrong_password_shows_error(client):
    UserFactory(email='anna@example.com')

    response = client.post(reverse('account_login'), {
        'login': 'anna@example.com', 'password': 'wrong',
    })

    assert response.status_code == 200
    assert 'alert--error' in response.content.decode()


def test_auth_pages_use_site_design(client):
    """Страницы allauth встроены в наш base.html и карточку входа."""
    for name in ['account_login', 'account_signup', 'account_reset_password']:
        html = client.get(reverse(name)).content.decode()
        assert 'class="auth__card"' in html, name
        assert 'class="header"' in html, name
        assert 'class="field__input' in html, name


def test_profile_requires_login(client):
    response = client.get(reverse('accounts:profile'))

    assert response.status_code == 302
    assert response.url.startswith(reverse('account_login'))


def test_profile_and_header_for_logged_in_user(client):
    user = UserFactory(email='ivan@example.com', first_name='Иван', last_name='Петров')
    client.force_login(user)

    html = client.get(reverse('accounts:profile')).content.decode()

    assert '<h1 class="page-title">Иван Петров</h1>' in html
    assert 'aria-label="Профиль">ИП</a>' in html      # аватар в шапке вместо «Войти»
    assert '>Войти</a>' not in html


def test_messages_shown_on_regular_pages(client):
    """Сообщения allauth («Вы вышли») видны на обычной странице, куда вернул выход."""
    client.force_login(UserFactory())

    response = client.post(reverse('account_logout'), follow=True)

    assert 'class="container stack-messages"' in response.content.decode()

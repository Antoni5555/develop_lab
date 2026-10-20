"""Заглушки страниц аккаунта. На этапе 3 вход и регистрацию заменит django-allauth
по тем же адресам (/accounts/login/, /accounts/signup/)."""
from django.views.generic import TemplateView


class LoginView(TemplateView):
    """Вход."""

    template_name = 'accounts/login.html'


class SignupView(TemplateView):
    """Регистрация."""

    template_name = 'accounts/signup.html'


class ProfileView(TemplateView):
    """Профиль."""

    template_name = 'accounts/profile.html'

"""Профиль. Вход, регистрация и выход — django-allauth (/accounts/login/ и т. д.)."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль пользователя. Статистика и прогресс появятся на шаге 3.2."""

    template_name = 'accounts/profile.html'

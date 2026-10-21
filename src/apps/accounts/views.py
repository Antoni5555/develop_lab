"""Профиль. Вход, регистрация и выход — django-allauth (/accounts/login/ и т. д.)."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.courses.services import selectors
from apps.progress.services import progress


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль: статистика, прогресс по курсам, активность за 5 недель."""

    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, _, cards = selectors.catalog()
        context['summary'] = progress.profile_summary(self.request.user, cards)
        return context

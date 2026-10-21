"""Профиль. Вход, регистрация и выход — django-allauth (/accounts/login/ и т. д.)."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from apps.cheatsheets.services import notes
from apps.courses.services import selectors
from apps.progress.services import progress

from .forms import ProfileForm


class ProfileView(LoginRequiredMixin, TemplateView):
    """Профиль: статистика, прогресс по курсам, активность за 5 недель."""

    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        _, _, cards = selectors.catalog()
        context['summary'] = progress.profile_summary(self.request.user, cards)
        context['recent_notes'] = notes.recent_notes(self.request.user)
        context['notes_count'] = self.request.user.notes.count()
        return context


class SettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Настройки профиля: имя и фамилия; оттуда же — смена пароля."""

    form_class = ProfileForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = 'Настройки сохранены.'

    def get_object(self, queryset=None):
        return self.request.user

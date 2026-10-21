"""Шпаргалки: заметки пользователя по курсам и темам."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.courses.services import selectors

from .services import notes


class CheatsheetListView(TemplateView):
    """Карточка шпаргалки на каждый курс. Гостю — «как это работает» и вход."""

    template_name = 'cheatsheets/cheatsheet_list.html'
    extra_context = {'active_nav': 'cheatsheets'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            _, _, cards = selectors.catalog()
            context['cards'] = notes.sheet_cards(self.request.user, cards)
        return context


class CheatsheetDetailView(LoginRequiredMixin, TemplateView):
    """Шпаргалка курса: карточки тем с заметками."""

    template_name = 'cheatsheets/cheatsheet_detail.html'
    extra_context = {'active_nav': 'cheatsheets'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(notes.cheatsheet(self.request.user, kwargs['course']))
        return context

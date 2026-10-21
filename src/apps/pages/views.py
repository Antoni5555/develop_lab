from django.conf import settings
from django.views.generic import TemplateView

from apps.courses.services.selectors import home_summary


class HomeView(TemplateView):
    """Главная."""

    template_name = 'home/home.html'
    extra_context = {'active_nav': 'home'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(home_summary())
        return context


class AboutView(TemplateView):
    """О проекте."""

    template_name = 'about/about.html'
    extra_context = {'active_nav': 'about'}


class LegalView(TemplateView):
    """Юридический документ: политика конфиденциальности или согласие на обработку.

    Реквизиты оператора — из настроек (OPERATOR в .env), не из шаблона.
    """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operator'] = settings.OPERATOR
        return context

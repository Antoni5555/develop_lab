from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Главная."""

    template_name = 'home/home.html'
    extra_context = {'active_nav': 'home'}


class AboutView(TemplateView):
    """О проекте."""

    template_name = 'about/about.html'
    extra_context = {'active_nav': 'about'}

from django.views.generic import TemplateView


class PlaygroundView(TemplateView):
    """Тренажёр-песочница. Заглушка: SQL-тренажёр появится на этапе 2."""

    template_name = 'trainers/playground.html'
    extra_context = {'active_nav': 'playground'}

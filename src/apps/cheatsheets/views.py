from django.views.generic import TemplateView


class CheatsheetListView(TemplateView):
    """Шпаргалки. Заглушка: заметки пользователя появятся на этапе 3."""

    template_name = 'cheatsheets/cheatsheet_list.html'
    extra_context = {'active_nav': 'cheatsheets'}

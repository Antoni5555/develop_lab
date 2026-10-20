from django.views.generic import TemplateView


class CourseListView(TemplateView):
    """Каталог курсов. Заглушка: список из БД появится на этапе 1."""

    template_name = 'courses/course_list.html'
    extra_context = {'active_nav': 'courses'}

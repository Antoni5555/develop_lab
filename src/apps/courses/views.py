"""Страницы курсов. Views тонкие: данные готовят функции из services/selectors.py."""
from django.views.generic import TemplateView

from .services import selectors


class CourseListView(TemplateView):
    """Каталог курсов направления: /courses/?track=backend."""

    template_name = 'courses/course_list.html'
    extra_context = {'active_nav': 'courses'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tracks, track, cards = selectors.catalog(self.request.GET.get('track'))
        context.update(tracks=tracks, track=track, cards=cards)
        return context


class CourseDetailView(TemplateView):
    """Курс: программа по разделам и темам."""

    template_name = 'courses/course_detail.html'
    extra_context = {'active_nav': 'courses'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(selectors.course_detail(kwargs['course']))
        return context


class LessonView(TemplateView):
    """Урок темы с программой курса справа."""

    template_name = 'courses/lesson_detail.html'
    extra_context = {'active_nav': 'courses'}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(selectors.lesson_page(
            kwargs['course'], kwargs['section'], kwargs['topic'],
        ))
        return context

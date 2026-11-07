"""Главная админки (Unfold): счётчики и последние сообщения об ошибках.

Функции подключены в настройках UNFOLD (DASHBOARD_CALLBACK, badge в меню).
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from apps.cheatsheets.models import Note
from apps.feedback.models import ContentReport
from apps.progress.models import ExerciseProgress

WEEK = timedelta(days=7)
RECENT_REPORTS = 5


def new_reports_badge(request):
    """Число новых сообщений об ошибках — рядом с пунктом меню (пусто, если 0)."""
    return ContentReport.objects.filter(status=ContentReport.Status.NEW).count() or None


def dashboard_callback(request, context):
    week_ago = timezone.now() - WEEK
    users = get_user_model().objects.filter(is_active=True)
    reports_url = reverse('admin:feedback_contentreport_changelist')
    new_reports = (
        ContentReport.objects.filter(status=ContentReport.Status.NEW)
        .select_related('topic__section__course', 'exercise')
        .order_by('-created_at')
    )

    context['stats'] = [
        {
            'title': 'Новые сообщения об ошибках',
            'value': new_reports.count(),
            'href': f'{reports_url}?status__exact=new',
        },
        {
            'title': 'Пользователи',
            'value': users.count(),
            'note': f'+{users.filter(date_joined__gte=week_ago).count()} за неделю',
            'href': reverse('admin:accounts_user_changelist'),
        },
        {
            'title': 'Решено задач за неделю',
            'value': ExerciseProgress.objects.filter(solved_at__gte=week_ago).count(),
            'note': f'всего {ExerciseProgress.objects.count()}',
            'href': reverse('admin:progress_exerciseprogress_changelist'),
        },
        {
            'title': 'Заметки',
            'value': Note.objects.count(),
            'note': (
                f'+{Note.objects.filter(created_at__gte=week_ago).count()} за неделю'
            ),
            'href': reverse('admin:cheatsheets_note_changelist'),
        },
    ]
    context['recent_reports'] = {
        'headers': ['Что выделено', 'Где', 'Когда'],
        'rows': [
            [
                format_html(
                    '<a href="{}" class="{}">{}</a>',
                    reverse('admin:feedback_contentreport_change', args=[report.pk]),
                    'text-primary-600 dark:text-primary-500',
                    report.quote[:70] + ('…' if len(report.quote) > 70 else ''),
                ),
                report.topic.section.course.title + ' › ' + (
                    report.exercise.title if report.exercise else report.topic.title
                ),
                timezone.localtime(report.created_at).strftime('%d.%m.%Y %H:%M'),
            ]
            for report in new_reports[:RECENT_REPORTS]
        ],
    }
    return context

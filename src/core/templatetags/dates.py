"""Даты в шаблонах."""
from datetime import timedelta

from django import template
from django.utils import timezone
from django.utils.timesince import timesince


register = template.Library()


@register.filter
def ago(value):
    """«5 дней назад», «2 недели назад», «только что» — одна, самая крупная единица."""
    if not value:
        return ''
    if timezone.now() - value < timedelta(minutes=1):
        return 'только что'
    return f'{timesince(value, depth=1)} назад'

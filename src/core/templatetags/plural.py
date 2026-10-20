"""Русское множественное число в шаблонах: {{ count|plural:"задача,задачи,задач" }}."""
from django import template


register = template.Library()


def plural_form(number, one, few, many):
    """Форма слова для числа: 1 задача, 3 задачи, 5 задач, 21 задача, 11 задач."""
    number = abs(int(number))
    if number % 10 == 1 and number % 100 != 11:
        return one
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return few
    return many


@register.filter
def plural(number, forms):
    """'3' + 'задача,задачи,задач' → '3 задачи'."""
    one, few, many = forms.split(',')
    return f'{number} {plural_form(number, one, few, many)}'

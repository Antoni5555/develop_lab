"""Помощники для форм в шаблонах."""
from django import template


register = template.Library()


@register.filter
def add_class(field, css_class):
    """{{ form.email|add_class:"field__input" }} — поле формы с классом из дизайна."""
    classes = field.field.widget.attrs.get('class', '')
    if field.errors:
        css_class += f' {css_class}--error'
    return field.as_widget(attrs={'class': f'{classes} {css_class}'.strip()})

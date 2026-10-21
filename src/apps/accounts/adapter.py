"""Настройка поведения django-allauth под сайт."""
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class AccountAdapter(DefaultAccountAdapter):
    """Письма allauth знают название сайта."""

    def send_mail(self, template_prefix, email, context):
        # Тело письма allauth рендерит с request (context processors дают
        # SITE_NAME), а тему — без него: передаём название явно
        context = {**context, 'SITE_NAME': settings.SITE_NAME}
        super().send_mail(template_prefix, email, context)

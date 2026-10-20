from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Общий код проекта. Не импортирует ничего из apps/."""

    name = 'core'

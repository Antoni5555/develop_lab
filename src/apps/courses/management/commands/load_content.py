"""manage.py load_content — загрузить курсы, уроки и задачи из content/ в БД."""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.courses.services.content_loader import ContentError, ContentLoader


class Command(BaseCommand):
    help = (
        'Загружает контент из папки content/ '
        '(повторный запуск обновляет, не дублирует).'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            'path', nargs='?', default=settings.CONTENT_DIR,
            help='папка с контентом (по умолчанию — CONTENT_DIR из настроек)',
        )

    def handle(self, *args, path, **options):
        content_dir = Path(path)
        if not content_dir.is_dir():
            raise CommandError(f'Нет папки с контентом: {content_dir}')

        try:
            report = ContentLoader(content_dir).load()
        except ContentError as error:
            message = f'Ошибка в контенте, БД не изменена.\n{error}'
            raise CommandError(message) from error

        for title, counter in [
            ('Создано', report.created),
            ('Обновлено', report.updated),
            ('Скрыто (нет в content/)', report.hidden),
        ]:
            if counter:
                items = ', '.join(
                    f'{name}: {count}' for name, count in sorted(counter.items())
                )
                self.stdout.write(f'{title}: {items}')
        if not (report.created or report.updated or report.hidden):
            self.stdout.write('Изменений нет.')
        self.stdout.write(self.style.SUCCESS('Контент загружен.'))

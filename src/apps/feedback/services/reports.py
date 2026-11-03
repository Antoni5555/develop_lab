"""Сообщения об ошибках: создание и поиск файла в content/, который надо поправить."""
from django.conf import settings

from apps.cheatsheets.services.notes import resolve_source

from ..models import ContentReport


MAX_QUOTE = 500
MAX_CONTEXT = 1000
MAX_COMMENT = 1000


def create_report(user, source_key, quote, context='', comment=''):
    """Ключ источника — как у заметок: «курс/раздел/тема[/задача]».

    Возвращает None, если такого урока или задачи нет (или это песочница — там
    нечего исправлять в контенте).
    """
    source = resolve_source(source_key)
    if source is None or source.topic is None:
        return None
    return ContentReport.objects.create(
        user=user, topic=source.topic, exercise=source.exercise,
        quote=quote.strip(), context=context.strip(), comment=comment.strip(),
    )


def content_path(report):
    """Путь к файлу урока или задачи в content/.

    Например: content/backend/python/01-basics/01-hello/02-greeting.yaml.

    Папки в content/ называются NN-slug, а в базе хранится только slug, поэтому
    файл ищем по шаблону. Не нашли (контент переехал) — показываем сам шаблон.
    """
    topic = report.topic
    section = topic.section
    course = section.course
    folder = (f'{course.track.slug}/{course.slug}/'
              f'[0-9]*-{section.slug}/[0-9]*-{topic.slug}')
    name = f'[0-9]*-{report.exercise.slug}.yaml' if report.exercise else '*.md'
    pattern = f'{folder}/{name}'
    found = sorted(settings.CONTENT_DIR.glob(pattern))
    if not found:
        return f'content/{pattern}'
    return f'content/{found[0].relative_to(settings.CONTENT_DIR)}'

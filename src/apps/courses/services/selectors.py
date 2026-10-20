"""Выборки контента для страниц. Views только вызывают эти функции.

Каждая функция делает фиксированное число SQL-запросов, сколько бы ни было
разделов и тем (prefetch_related вместо запроса на каждую тему — без N+1).
"""
from dataclasses import dataclass

from django.db.models import Count, Prefetch, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.courses.models import Course, Exercise, Lesson, Section, Topic, Track


PUBLISHED_TOPICS = Q(sections__is_published=True, sections__topics__is_published=True)
PUBLISHED_EXERCISES = Q(sections__topics__exercises__is_published=True)


def published_courses():
    """Опубликованные курсы с числом тем и задач (для карточек)."""
    return (
        Course.objects.published()
        .filter(track__is_published=True)
        .select_related('track')
        .annotate(
            topic_count=Count(
                'sections__topics', filter=PUBLISHED_TOPICS, distinct=True,
            ),
            exercise_count=Count(
                'sections__topics__exercises',
                filter=PUBLISHED_TOPICS & PUBLISHED_EXERCISES,
                distinct=True,
            ),
        )
        .order_by('track__order', 'order')
    )


@dataclass
class CourseCard:
    """Курс в каталоге: номер шага в программе направления и «скоро»."""

    course: Course
    step: int

    @property
    def is_soon(self):
        """Курс без опубликованных тем — карточка «скоро»."""
        return self.course.topic_count == 0


def catalog(track_slug=None):
    """Каталог: направления и курсы выбранного направления (по умолчанию — первого).

    Возвращает (направления, текущее направление, карточки курсов).
    """
    tracks = list(Track.objects.published())
    if not tracks:
        return [], None, []
    current = next((t for t in tracks if t.slug == track_slug), tracks[0])
    courses = published_courses().filter(track=current)
    cards = [CourseCard(course, step) for step, course in enumerate(courses, start=1)]
    return tracks, current, cards


def course_outline(course):
    """Разделы курса → темы → урок и задачи. 3 запроса на любой размер курса."""
    exercises = Exercise.objects.published().only('id', 'title', 'slug', 'topic_id')
    topics = (
        Topic.objects.published()
        .select_related('lesson')
        .prefetch_related(Prefetch('exercises', queryset=exercises))
    )
    sections = list(
        Section.objects.published()
        .filter(course=course)
        .prefetch_related(Prefetch('topics', queryset=topics))
    )
    # Курс уже загружен — кладём его в разделы, чтобы topic.get_absolute_url()
    # не делал по запросу на каждый раздел
    for section in sections:
        section.course = course
        # число задач раздела — для подписи «N задач»; считаем в Python, без запросов
        section.exercise_count = sum(
            len(topic.exercises.all()) for topic in section.topics.all()
        )
    return sections


def level_range(sections):
    """Уровни разделов курса для подписи: «основы → продвинутое» или «основы»."""
    levels = sorted({section.level for section in sections})
    if not levels:
        return ''
    labels = [Section.Level(levels[0]).label, Section.Level(levels[-1]).label]
    return labels[0] if labels[0] == labels[1] else ' → '.join(labels)


def course_detail(slug):
    """Курс, его программа и соседние шаги направления."""
    course = get_object_or_404(
        published_courses().filter(slug=slug)
    )
    sections = course_outline(course)
    siblings = list(published_courses().filter(track=course.track))
    index = next(i for i, c in enumerate(siblings) if c.pk == course.pk)
    reading_time = (
        Topic.objects.published()
        .filter(section__course=course, section__is_published=True,
                lesson__is_published=True)
        .aggregate(total=Sum('lesson__reading_time'))['total']
    ) or 0
    return {
        'course': course,
        'step': index + 1,
        'sections': sections,
        'first_topic': next(
            (topic for section in sections for topic in section.topics.all()), None,
        ),
        'level_range': level_range(sections),
        'reading_time': reading_time,
        'prev_course': siblings[index - 1] if index > 0 else None,
        'next_course': siblings[index + 1] if index + 1 < len(siblings) else None,
    }


def lesson_page(course_slug, section_slug, topic_slug):
    """Урок темы, программа курса для правой панели, соседние уроки."""
    course = get_object_or_404(
        Course.objects.published().select_related('track'), slug=course_slug,
    )
    sections = course_outline(course)
    topics = [
        (section, topic) for section in sections for topic in section.topics.all()
    ]
    index = next(
        (i for i, (section, topic) in enumerate(topics)
         if section.slug == section_slug and topic.slug == topic_slug),
        None,
    )
    if index is None:
        raise Http404('Тема не найдена')
    section, topic = topics[index]
    lesson = getattr(topic, 'lesson', None)
    if lesson is None or not lesson.is_published:
        raise Http404('У темы нет урока')
    return {
        'course': course,
        'section': section,
        'topic': topic,
        'lesson': lesson,
        'sections': sections,
        'prev_topic': topics[index - 1][1] if index > 0 else None,
        'next_topic': topics[index + 1][1] if index + 1 < len(topics) else None,
    }


def home_summary():
    """Для главной: первые курсы программы и общие числа."""
    _, _, cards = catalog()
    open_cards = [card for card in cards if not card.is_soon]
    return {
        'start_cards': open_cards[:3],
        'stats': {
            'courses': len(open_cards),
            'lessons': Lesson.objects.published().filter(
                topic__is_published=True, topic__section__is_published=True,
                topic__section__course__in=[card.course for card in open_cards],
            ).count(),
            'exercises': sum(card.course.exercise_count for card in open_cards),
        },
    }

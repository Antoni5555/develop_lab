"""Прогресс пользователя: отметки, перенос из браузера, статусы для страниц.

Ключ задачи — путь из slug: «python/first-steps/strings/sku-parts»; ключ урока —
«python/first-steps/strings». Такие же ключи хранит гость в localStorage, поэтому
после входа его прогресс переносится без пересчёта id.
"""
from collections import Counter
from dataclasses import dataclass
from datetime import timedelta

from django.db.models import Count, Max
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.courses.models import Exercise, Lesson

from ..models import ExerciseProgress, LessonView


HEATMAP_DAYS = 35   # 5 недель


# --- ключи ---

def lesson_key(topic):
    section = topic.section
    return f'{section.course.slug}/{section.slug}/{topic.slug}'


def exercise_key(exercise):
    return f'{lesson_key(exercise.topic)}/{exercise.slug}'


# --- отметки ---

def mark_solved(user, exercise):
    """Задача решена. Повторная отметка ничего не меняет (дата — первого решения)."""
    ExerciseProgress.objects.get_or_create(user=user, exercise=exercise)


def mark_viewed(user, lesson):
    """Урок открыт."""
    LessonView.objects.get_or_create(user=user, lesson=lesson)


def find_exercise(key):
    """Опубликованная задача по ключу или None."""
    parts = key.split('/')
    if len(parts) != 4:
        return None
    course, section, topic, exercise = parts
    return (
        Exercise.objects.published()
        .filter(
            slug=exercise, topic__slug=topic, topic__is_published=True,
            topic__section__slug=section, topic__section__is_published=True,
            topic__section__course__slug=course,
        )
        .first()
    )


def import_guest(user, solved_keys, viewed_keys):
    """Переносит прогресс гостя из браузера. Неизвестные ключи пропускаются.

    Возвращает (сколько задач, сколько уроков найдено по ключам).
    """
    courses = {key.split('/')[0] for key in [*solved_keys, *viewed_keys]}
    exercises = {
        exercise_key(exercise): exercise
        for exercise in Exercise.objects.published()
        .filter(topic__section__course__slug__in=courses)
        .select_related('topic__section__course')
    }
    lessons = {
        lesson_key(lesson.topic): lesson
        for lesson in Lesson.objects.published()
        .filter(topic__section__course__slug__in=courses)
        .select_related('topic__section__course')
    }
    solved = [exercises[key] for key in set(solved_keys) if key in exercises]
    viewed = [lessons[key] for key in set(viewed_keys) if key in lessons]
    ExerciseProgress.objects.bulk_create(
        [ExerciseProgress(user=user, exercise=exercise) for exercise in solved],
        ignore_conflicts=True,
    )
    LessonView.objects.bulk_create(
        [LessonView(user=user, lesson=lesson) for lesson in viewed],
        ignore_conflicts=True,
    )
    return len(solved), len(viewed)


# --- статусы для страниц курса ---

def apply_to_outline(sections, user):
    """Отмечает в программе курса, что решено и прочитано. 2 запроса на курс.

    Ставит атрибуты: exercise.is_solved, topic.lesson_viewed, topic.solved_count,
    topic.is_done, section.done_topics, section.is_done, section.is_started.
    Для гостя только считает итоги (всё «не начато»): его прогресс рисует JS.
    """
    solved, viewed = set(), set()
    if user.is_authenticated and sections:
        course = sections[0].course
        solved = set(
            ExerciseProgress.objects
            .filter(user=user, exercise__topic__section__course=course)
            .values_list('exercise_id', flat=True)
        )
        viewed = set(
            LessonView.objects
            .filter(user=user, lesson__topic__section__course=course)
            .values_list('lesson_id', flat=True)
        )

    total = done = 0
    for section in sections:
        section.done_topics = 0
        section.is_started = False
        topics = section.topics.all()
        for topic in topics:
            exercises = topic.exercises.all()
            for exercise in exercises:
                exercise.is_solved = exercise.pk in solved
            lesson = getattr(topic, 'lesson', None)
            topic.lesson_viewed = lesson is not None and lesson.pk in viewed
            topic.solved_count = sum(exercise.is_solved for exercise in exercises)
            topic.is_done = (
                (lesson is None or topic.lesson_viewed)
                and topic.solved_count == len(exercises)
            )
            topic.is_started = topic.lesson_viewed or topic.solved_count > 0
            section.done_topics += topic.is_done
            section.is_started = section.is_started or topic.is_started
            total += len(exercises)
            done += topic.solved_count
        section.is_done = bool(topics) and section.done_topics == len(topics)
    return {'solved': done, 'total': total}


def next_item(items):
    """Первый не пройденный шаг курса — для кнопки «Продолжить»."""
    for item in items:
        if item.exercise is not None:
            if not item.exercise.is_solved:
                return item
        elif not item.topic.lesson_viewed:
            return item
    return None


# --- статусы карточек курсов ---

def apply_to_cards(cards, user):
    """Статус карточки: done — всё решено, current — курс с последней активностью,
    new — не начат, soon — нет тем. Для гостя — только new/soon."""
    stats = {}
    if user.is_authenticated:
        for row in (
            ExerciseProgress.objects.filter(user=user)
            .values('exercise__topic__section__course')
            .annotate(solved=Count('id'), last=Max('solved_at'))
        ):
            stats[row['exercise__topic__section__course']] = row
        for row in (
            LessonView.objects.filter(user=user)
            .values('lesson__topic__section__course')
            .annotate(last=Max('viewed_at'))
        ):
            course_stats = stats.setdefault(
                row['lesson__topic__section__course'], {'solved': 0, 'last': None},
            )
            course_stats['last'] = max(
                filter(None, [course_stats['last'], row['last']]),
            )

    current = None
    for card in cards:
        course_stats = stats.get(card.course.pk, {})
        card.solved = course_stats.get('solved', 0)
        total = card.course.exercise_count
        card.percent = round(card.solved * 100 / total) if total else 0
        if card.is_soon:
            card.status = 'soon'
        elif total and card.solved >= total:
            card.status = 'done'
        else:
            card.status = 'new'
            last = course_stats.get('last')
            if last and (current is None or last > current[1]):
                current = (card, last)
    if current:
        current[0].status = 'current'
    return cards


# --- профиль ---

@dataclass
class CourseProgress:
    course: object
    solved: int
    total: int

    @property
    def percent(self):
        return round(self.solved * 100 / self.total) if self.total else 0

    @property
    def is_done(self):
        return self.total > 0 and self.solved >= self.total


def activity_by_day(user):
    """Счётчик действий по дням: решённые задачи + открытые уроки."""
    counts = Counter()
    for model, field in ((ExerciseProgress, 'solved_at'), (LessonView, 'viewed_at')):
        rows = (
            model.objects.filter(user=user)
            .annotate(day=TruncDate(field))
            .values('day').annotate(n=Count('id'))
        )
        for row in rows:
            counts[row['day']] += row['n']
    return counts


def streak(days, today):
    """Сколько дней подряд была активность. Сегодня ещё можно успеть —
    поэтому серия, закончившаяся вчера, не обрывается."""
    day = today if today in days else today - timedelta(days=1)
    count = 0
    while day in days:
        count += 1
        day -= timedelta(days=1)
    return count


def heatmap(days, today):
    """35 клеток (5 недель) от старых к новым: уровень 0–3 по числу действий."""
    cells = []
    for offset in range(HEATMAP_DAYS - 1, -1, -1):
        day = today - timedelta(days=offset)
        n = days.get(day, 0)
        level = 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3
        cells.append({'day': day, 'count': n, 'level': level})
    return cells


def profile_summary(user, course_cards):
    """Статистика профиля. course_cards — карточки курсов с exercise_count."""
    solved_by_course = dict(
        ExerciseProgress.objects.filter(user=user)
        .values_list('exercise__topic__section__course')
        .annotate(n=Count('id'))
    )
    viewed_courses = set(
        LessonView.objects.filter(user=user)
        .values_list('lesson__topic__section__course', flat=True)
    )
    courses = [
        CourseProgress(card.course, solved_by_course.get(card.course.pk, 0),
                       card.course.exercise_count)
        for card in course_cards
        if card.course.pk in solved_by_course or card.course.pk in viewed_courses
    ]
    days = activity_by_day(user)
    today = timezone.localdate()
    return {
        'solved': sum(solved_by_course.values()),
        'lessons': LessonView.objects.filter(user=user).count(),
        'streak': streak(days, today),
        'completed': sum(progress.is_done for progress in courses),
        'courses': courses,
        'heatmap': heatmap(days, today),
    }

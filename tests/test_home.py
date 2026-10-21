"""Главная: цифры первого экрана и карта пути (статусы курсов направления)."""
import re

import pytest
from django.urls import reverse

from apps.courses.models import Exercise
from apps.progress.models import ExerciseProgress
from tests.factories import (
    CourseFactory, SectionFactory, TrackFactory, UserFactory, topic_with_lesson,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def courses():
    """Направление из трёх курсов: два открыты (по 2 задачи), третий — «скоро»."""
    track = TrackFactory(title='Backend')
    first = CourseFactory(track=track, title='Python')
    second = CourseFactory(track=track, title='Linux')
    soon = CourseFactory(track=track, title='Docker')
    topic_with_lesson(SectionFactory(course=first))
    topic_with_lesson(SectionFactory(course=second))
    return first, second, soon


def stops(html):
    """Станции карты пути: [(статус, html станции)]."""
    return re.findall(
        r'<li class="metro__stop metro__stop--(\w+)">(.*?)</li>', html, re.S,
    )


def test_numbers_count_all_courses_and_published_exercises(client, courses):
    html = client.get(reverse('pages:home')).content.decode()

    assert '<dt>3</dt><dd>курса в программе</dd>' in html   # «скоро» — тоже в программе
    assert '<dt>4</dt><dd>задачи</dd>' in html


def test_guest_path_starts_at_first_course(
    client, courses, django_assert_max_num_queries,
):
    with django_assert_max_num_queries(6):
        html = client.get(reverse('pages:home')).content.decode()

    (s1, first), (s2, second), (s3, soon) = stops(html)
    assert (s1, s2, s3) == ('current', 'open', 'soon')
    assert 'начни здесь' in first
    assert '2 задачи' in second
    assert 'скоро' in soon and '<a ' not in soon      # у курса «скоро» нет ссылки
    assert 'Путь обучения Backend' in html


def test_user_path_shows_done_and_current(client, courses):
    first, second, _ = courses
    user = UserFactory()
    for exercise in Exercise.objects.filter(topic__section__course=first):
        ExerciseProgress.objects.create(user=user, exercise=exercise)
    ExerciseProgress.objects.create(
        user=user, exercise=Exercise.objects.filter(topic__section__course=second)[0],
    )
    client.force_login(user)

    html = client.get(reverse('pages:home')).content.decode()

    (s1, first_html), (s2, second_html), _ = stops(html)
    assert (s1, s2) == ('done', 'current')
    assert '✓ пройден' in first_html
    assert 'вы здесь · 1 / 2' in second_html


def test_reveal_script_only_on_home(client, courses):
    assert 'js/reveal.js' in client.get(reverse('pages:home')).content.decode()
    assert 'js/reveal.js' not in client.get(reverse('pages:about')).content.decode()

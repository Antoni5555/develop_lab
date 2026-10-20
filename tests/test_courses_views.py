"""Каталог, страница курса, урок."""
import pytest
from django.urls import reverse

from apps.courses.models import Topic
from tests.factories import CourseFactory, SectionFactory, topic_with_lesson


pytestmark = pytest.mark.django_db

LESSON_URL = reverse('courses:lesson', args=['python', 'basics', 'hello'])


def test_catalog_shows_steps_and_soon_card(client, loaded_content):
    html = client.get(reverse('courses:list')).content.decode()

    assert 'Шаг 1' in html and 'Шаг 2' in html
    assert 'href="/courses/python/"' in html
    assert 'course-card--soon' in html and 'href="/courses/soon/"' not in html
    assert '2 темы · 4 задачи' in html


def test_course_page(client, loaded_content):
    response = client.get(reverse('courses:detail', args=['python']))
    html = response.content.decode()

    assert response.status_code == 200
    assert 'Привет' in html and 'Вторая тема' in html
    assert f'href="{LESSON_URL}"' in html                 # «Начать курс» и тема
    assert '~10 мин чтения' in html                       # 7 + 3 минуты
    assert 'Python в браузере' in html


def test_soon_course_page_says_in_progress(client, loaded_content):
    html = client.get(reverse('courses:detail', args=['soon'])).content.decode()

    assert 'Курс в работе' in html


def test_lesson_page(client, loaded_content):
    response = client.get(LESSON_URL)
    html = response.content.decode()

    assert response.status_code == 200
    assert '<h1 class="article__title">Привет, Python</h1>' in html
    assert 'class="lesson lesson--current"' in html       # текущая тема в программе
    assert 'Дальше →</span>Вторая тема' in html
    assert 'js/code-copy.js' in html


@pytest.mark.parametrize('url', [
    reverse('courses:detail', args=['nope']),
    reverse('courses:lesson', args=['python', 'basics', 'nope']),
    reverse('courses:lesson', args=['python', 'nope', 'hello']),
])
def test_unknown_pages_404(client, loaded_content, url):
    assert client.get(url).status_code == 404


def test_hidden_topic_is_not_shown(client, loaded_content):
    Topic.objects.filter(slug='hello').update(is_published=False)

    assert client.get(LESSON_URL).status_code == 404
    html = client.get(reverse('courses:detail', args=['python'])).content.decode()
    assert 'Привет' not in html


def test_no_template_comments_leak(client, loaded_content):
    """Многострочный {# #} Django выводит как текст — его не должно быть в HTML."""
    for url in [reverse('pages:home'), reverse('courses:list'),
                reverse('courses:detail', args=['python']), LESSON_URL]:
        assert '{#' not in client.get(url).content.decode(), url


def make_course(topics):
    course = CourseFactory(slug='big')
    section = SectionFactory(course=course)
    for _ in range(topics):
        topic_with_lesson(section)
    return course


@pytest.mark.parametrize('topics', [1, 10])
def test_course_page_query_count_does_not_grow(
    client, django_assert_max_num_queries, topics,
):
    """Число SQL-запросов не зависит от числа тем (нет N+1)."""
    make_course(topics)

    with django_assert_max_num_queries(6):
        assert client.get(reverse('courses:detail', args=['big'])).status_code == 200


@pytest.mark.parametrize('topics', [1, 10])
def test_lesson_page_query_count_does_not_grow(
    client, django_assert_max_num_queries, topics,
):
    course = make_course(topics)
    topic = course.sections.get().topics.first()

    with django_assert_max_num_queries(4):
        assert client.get(topic.get_absolute_url()).status_code == 200

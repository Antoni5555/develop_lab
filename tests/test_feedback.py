"""«Сообщить об ошибке»: API, кнопка на страницах, админка."""
import pytest
from django.urls import reverse

from apps.feedback.models import ContentReport
from apps.feedback.services.reports import content_path
from tests.factories import UserFactory


pytestmark = pytest.mark.django_db

LESSON_URL = reverse('courses:lesson', args=['python', 'basics', 'hello'])
EXERCISE_URL = reverse('trainers:exercise',
                       args=['python', 'basics', 'hello', 'greeting'])


@pytest.fixture
def user(loaded_content):
    return UserFactory()


@pytest.fixture
def logged_in(client, user):
    client.force_login(user)
    return client


def report(client, source='python/basics/hello', quote='опечатка', **extra):
    return client.post(reverse('reports:list'),
                       {'source': source, 'quote': quote, **extra},
                       content_type='application/json')


def test_api_requires_login(client, loaded_content):
    assert report(client).status_code == 403
    assert not ContentReport.objects.exists()


@pytest.mark.parametrize('source, exercise', [
    ('python/basics/hello', None),                 # урок
    ('python/basics/hello/greeting', 'greeting'),  # задача
])
def test_create_report(logged_in, user, source, exercise):
    response = report(logged_in, source, quote='  принт  ',
                      context='Функция принт выводит', comment='print, а не принт')

    assert response.status_code == 201
    saved = ContentReport.objects.get()
    assert saved.user == user
    assert saved.topic.slug == 'hello'
    assert (saved.exercise.slug if saved.exercise else None) == exercise
    assert (saved.quote, saved.context, saved.comment) == (
        'принт', 'Функция принт выводит', 'print, а не принт')
    assert saved.status == ContentReport.Status.NEW


@pytest.mark.parametrize('source, quote, code', [
    ('python/basics/nope', 'текст', 404),     # нет такой темы
    ('python', 'текст', 400),                 # песочница: исправлять нечего
    ('python/basics/hello', '', 400),         # пустая цитата
    ('python/basics/hello', 'x' * 501, 400),  # длиннее лимита
])
def test_invalid_report(logged_in, source, quote, code):
    assert report(logged_in, source, quote).status_code == code
    assert not ContentReport.objects.exists()


def test_rate_limit(logged_in):
    """Не больше 20 сообщений в час — чтобы никто не завалил админку."""
    codes = [report(logged_in).status_code for _ in range(21)]

    assert codes[:20] == [201] * 20
    assert codes[20] == 429


@pytest.mark.parametrize('url', [LESSON_URL, EXERCISE_URL])
def test_pages_have_report_dialog(client, loaded_content, url):
    html = client.get(url).content.decode()

    assert 'data-report-scope' in html
    assert 'js/report-error.js' in html
    assert 'Войти, чтобы сообщить' in html        # гость видит приглашение войти


def test_report_dialog_source(logged_in):
    lesson = logged_in.get(LESSON_URL).content.decode()
    task = logged_in.get(EXERCISE_URL).content.decode()

    assert 'data-source="python/basics/hello"' in lesson
    assert 'data-source="python/basics/hello/greeting"' in task
    assert 'data-report-send' in lesson


def test_content_path(logged_in, loaded_content, settings):
    settings.CONTENT_DIR = loaded_content
    report(logged_in)
    report(logged_in, 'python/basics/hello/greeting')
    lesson, task = ContentReport.objects.order_by('id')

    folder = 'content/backend/python/01-basics/01-hello'
    assert content_path(lesson) == f'{folder}/01-hello.md'
    assert content_path(task) == f'{folder}/02-greeting.yaml'


def test_admin_list_and_actions(admin_client, logged_in, loaded_content, settings,
                                django_assert_max_num_queries):
    settings.CONTENT_DIR = loaded_content
    for source in ['python/basics/hello', 'python/basics/hello/greeting'] * 3:
        report(logged_in, source)
    url = reverse('admin:feedback_contentreport_changelist')

    with django_assert_max_num_queries(10):    # без N+1 по числу сообщений
        response = admin_client.get(url)
    assert response.status_code == 200
    assert 'опечатка' in response.content.decode()

    ids = list(ContentReport.objects.values_list('id', flat=True)[:2])
    admin_client.post(url, {'action': 'mark_fixed', '_selected_action': ids})
    assert ContentReport.objects.filter(status='fixed').count() == 2

    detail = admin_client.get(
        reverse('admin:feedback_contentreport_change', args=[ids[0]]))
    assert 'content/backend/python/01-basics/01-hello/' in detail.content.decode()

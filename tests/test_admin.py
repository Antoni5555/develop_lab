"""Админка (Unfold): главная со счётчиками, меню, лишние разделы скрыты."""
import pytest
from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse

from apps.cheatsheets.models import Note
from apps.courses.models import Course, Exercise
from apps.feedback.models import ContentReport
from apps.progress.models import ExerciseProgress
from tests.factories import UserFactory


pytestmark = pytest.mark.django_db


def test_unused_sections_hidden():
    assert not admin.site.is_registered(Group)
    assert not admin.site.is_registered(EmailAddress)


def test_dashboard_counters(admin_client, loaded_content):
    user = UserFactory()
    course = Course.objects.get(slug='python')
    exercise = Exercise.objects.first()
    topic = exercise.topic
    ExerciseProgress.objects.create(user=user, exercise=exercise)
    Note.objects.create(user=user, course=course, topic=topic, title='t', body_html='')
    ContentReport.objects.create(user=user, topic=topic, quote='опечатка в уроке')
    ContentReport.objects.create(user=user, topic=topic, quote='старое',
                                 status=ContentReport.Status.FIXED)

    response = admin_client.get(reverse('admin:index'))

    assert response.status_code == 200
    stats = {stat['title']: stat['value'] for stat in response.context['stats']}
    assert stats['Новые сообщения об ошибках'] == 1
    assert stats['Решено задач за неделю'] == 1
    assert stats['Заметки'] == 1
    # в таблице — только новые сообщения
    rows = response.context['recent_reports']['rows']
    assert len(rows) == 1 and 'опечатка в уроке' in rows[0][0]
    html = response.content.decode()
    # меню собрано по смыслу; у «Сообщений об ошибках» — счётчик новых
    for item in ['Обратная связь', 'Активность учеников', 'Решённые задачи']:
        assert item in html


def test_user_admin_shows_verified_email(admin_client, db):
    user = UserFactory(email='student@example.com')   # почту создаёт фабрика

    changelist = admin_client.get(reverse('admin:accounts_user_changelist'))
    change = admin_client.get(reverse('admin:accounts_user_change', args=[user.pk]))

    assert changelist.status_code == 200 and 'student@example.com' in (
        changelist.content.decode())
    assert change.status_code == 200
    assert 'emailaddress_set' in change.content.decode()


def test_user_add_page_opens(admin_client, db):
    assert admin_client.get(reverse('admin:accounts_user_add')).status_code == 200


@pytest.mark.parametrize('name', [
    'cheatsheets_note', 'progress_lessonview', 'progress_exerciseprogress',
    'courses_course', 'courses_topic', 'courses_exercise',
])
def test_read_only_sections(admin_client, loaded_content, name):
    assert admin_client.get(reverse(f'admin:{name}_changelist')).status_code == 200
    assert admin_client.get(reverse(f'admin:{name}_add')).status_code == 403

"""Страница задачи и песочница Python."""
import json
import re

import pytest
from django.urls import reverse

from apps.courses.models import Exercise


pytestmark = pytest.mark.django_db


def exercise_url(slug):
    return reverse('trainers:exercise', args=['python', 'basics', 'hello', slug])


def exercise_data(html):
    """JSON с данными задачи, который страница передаёт в JS."""
    match = re.search(
        r'<script id="exercise-data" type="application/json">(.*?)</script>', html,
    )
    return json.loads(match.group(1))


def test_exercise_page(client, loaded_content):
    response = client.get(exercise_url('greeting'))
    html = response.content.decode()

    assert response.status_code == 200
    assert '<h1 class="task__title">Приветствие</h1>' in html
    assert 'Задача 1' in html and 'Лёгкая' in html
    assert 'Подсказка 1 из 1' in html
    assert '>print(...)\n</textarea>' in html                 # заготовка в редакторе
    assert 'js/pages/exercise.js' in html
    assert 'data-pyodide="https://cdn.jsdelivr.net/pyodide/v0.27.8/full/"' in html
    # разбор и эталон — на странице, но скрыты до верного решения
    assert 'data-explanation hidden' in html and 'Эталонное решение' in html

    data = exercise_data(html)
    assert data['type'] == 'exercise'
    assert data['starter_code'] == 'print(...)\n'
    assert data['check']['tests'][0]['fail'] == 'Нужно вывести слово Привет.'
    assert 'hints' not in data


def test_exercise_navigation(client, loaded_content):
    """← урок темы, → следующая задача; в программе курса задача выделена."""
    html = client.get(exercise_url('greeting')).content.decode()

    assert 'aria-label="Назад: Привет, Python"' in html
    assert 'aria-label="Дальше: Что выведет"' in html
    assert ('<li class="lesson lesson--task lesson--current">'
            '<a href="/courses/python/basics/hello/greeting/">'
            '<span class="lesson__label">Задача 1</span>Приветствие</a>') in html


def test_playground_opens_first_section(client, loaded_content):
    """В песочнице нет текущей темы — открыт первый раздел, как на странице курса."""
    html = client.get(reverse('trainers:playground')).content.decode()

    assert '<details class="module-nav" open>' in html
    # в тренажёре — только разделы и темы, без задач
    assert 'topic--flat' in html and 'lesson--task' not in html
    assert 'href="/courses/python/basics/hello/"' in html


def test_predict_page(client, loaded_content):
    html = client.get(exercise_url('guess')).content.decode()

    assert 'Что выведет код' in html
    assert '<span class="fn">print</span>' in html            # код с подсветкой
    assert 'editor--answer' in html
    assert exercise_data(html) == {
        'type': 'predict', 'code': 'print(True + True)\n', 'answer': '2\n',
    }


def test_quiz_page_is_placeholder_for_now(client, loaded_content):
    html = client.get(exercise_url('pick')).content.decode()

    assert 'Задачи этого типа появятся' in html


def test_unknown_or_hidden_exercise_404(client, loaded_content):
    assert client.get(exercise_url('nope')).status_code == 404

    Exercise.objects.filter(slug='greeting').update(is_published=False)
    assert client.get(exercise_url('greeting')).status_code == 404


def test_last_exercise_has_no_next_but_lesson_follows(client, loaded_content):
    """После последней задачи темы — урок следующей темы."""
    html = client.get(exercise_url('fix-conf')).content.decode()

    assert 'aria-label="Дальше: Вторая тема"' in html


def test_playground(client, loaded_content):
    html = client.get(reverse('trainers:playground')).content.decode()

    assert 'data-playground="python"' in html
    assert 'js/pages/playground.js' in html
    assert 'Программа курса' in html and 'Основы' in html     # курс движка python


def test_playground_without_python_course(client, db):
    response = client.get(reverse('trainers:playground'))

    assert response.status_code == 200
    assert 'Программа курса' not in response.content.decode()

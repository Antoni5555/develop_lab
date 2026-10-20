"""runner.py — запуск кода и тестов задач Python (тот же файл выполняет Pyodide).

Здесь он работает в обычном Python: правила те же, что в браузере.
Последний тест прогоняет все задачи из content/ — эталоны должны проходить на сайте.
"""
import contextlib
import importlib.util
import signal
from pathlib import Path

import pytest
import yaml
from django.conf import settings

RUNNER_PATH = Path(settings.BASE_DIR) / 'static/js/engines/python/runner.py'
spec = importlib.util.spec_from_file_location('runner', RUNNER_PATH)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


@contextlib.contextmanager
def timeout_guard(seconds=2):
    """Тайм-аут как в браузере: зависшая программа → TimeoutError."""
    def stop(signum, frame):
        raise TimeoutError

    previous = signal.signal(signal.SIGALRM, stop)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)


TASK = {
    'inputs': 'total = 2500\n',
    'check': {'tests': [
        {'code': 'assert delivery == 0', 'fail': 'Бесплатно от 2000.'},
        {'code': 'assert run(total=500)["delivery"] == 399', 'fail': 'До 2000 — 399.'},
        {'code': 'assert "print" in source', 'fail': 'Выведите результат.'},
    ]},
}
SOLUTION = 'delivery = 0 if total >= 2000 else 399\nprint(delivery)\n'


def test_inputs_then_student_code_and_run_overrides():
    result = runner.check_exercise(SOLUTION, TASK)

    assert result == {'output': '0\n', 'error': '', 'failed': [], 'total': 3}


def test_failed_tests_return_fail_messages_in_order():
    result = runner.check_exercise('delivery = 0\n', TASK)

    assert result['failed'] == ['До 2000 — 399.', 'Выведите результат.']


def test_crash_is_reported_with_student_lines_only():
    result = runner.check_exercise('x = 1\nprint(undefined)\n', TASK)

    assert result['error'].splitlines() == [
        'Traceback (most recent call last):',
        '  File "main.py", line 2, in <module>',
        'NameError: name \'undefined\' is not defined',
    ]
    assert result['failed'][0] == 'Бесплатно от 2000.'


def test_crash_with_all_tests_passed_is_still_a_failure():
    task = {'check': {'tests': [{'code': 'assert x == 1', 'fail': '-'}]}}

    result = runner.check_exercise('x = 1\n1 / 0\n', task)

    assert result['failed'] == ['код упал: ZeroDivisionError: division by zero']


def test_syntax_error_shows_line_and_caret():
    result = runner.run_program('print("a"\n')

    assert 'SyntaxError' in result['error'] and 'line 1' in result['error']


def test_predict_compares_normalized_output():
    code = 'print(True + True)\nprint("a  ")\n'

    assert runner.check_predict(code, '2\na\n\n')['correct'] is True
    assert runner.check_predict(code, '1\na')['correct'] is False
    assert runner.check_predict(code, '2')['actual'] == '2\na  \n'


def test_timeout_message():
    task = {'check': {'tests': [{'code': 'assert True', 'fail': '-'}]}}

    _, error, _ = runner.run_tests(
        'while True:\n    pass\n', task, guard=lambda: timeout_guard(1),
    )

    assert isinstance(error, TimeoutError)
    assert runner.format_error(error) == 'Программа не завершилась'


def content_tasks():
    """Все задачи exercise и predict из content/ (кроме служебных файлов)."""
    tasks = []
    for path in sorted(Path(settings.CONTENT_DIR).rglob('*.yaml')):
        if path.name.startswith('_'):
            continue
        task = yaml.safe_load(path.read_text(encoding='utf-8'))
        if task.get('type') in ('exercise', 'predict'):
            name = str(path.relative_to(settings.CONTENT_DIR))
            tasks.append(pytest.param(task, id=name))
    return tasks


@pytest.mark.parametrize('task', content_tasks())
def test_content_task_works_in_runner(task):
    """Эталон проходит все тесты, заготовка — нет; ответ predict совпадает с выводом."""
    guard = timeout_guard
    if task['type'] == 'exercise':
        _, _, failed = runner.run_tests(task['solution'], task, guard=guard)
        assert failed == [], 'эталон не проходит тесты'
        _, _, failed = runner.run_tests(task['starter_code'], task, guard=guard)
        assert failed, 'заготовка проходит все тесты'
    else:
        result = runner.check_predict(task['code'], task['answer'])
        assert result['correct'], f'вывод: {result["actual"]!r}'

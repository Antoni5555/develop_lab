"""Запуск кода ученика и тестов задачи Python.

Один и тот же файл выполняют:
- тренажёр в браузере (Pyodide загружает его в Web Worker);
- проверка контента content/_tools/check_tasks.py и тесты сайта (обычный Python).
Так эталон, прошедший проверку контента, гарантированно проходит и на сайте.

Правила — docs/content-format.md, раздел «Как выполняются тесты»:
1. выполняется inputs (входные данные), затем код ученика в том же пространстве имён;
2. тестам доступны переменные ученика, output (вывод), source (код), run(**значения).

Тайм-аут здесь не реализован: в браузере зависшую программу останавливает
главная страница (перезапуском Web Worker), в check_tasks.py — signal.alarm через guard.
"""
import contextlib
import io
import traceback


STUDENT_FILE = 'main.py'
TIMEOUT_MESSAGE = 'Программа не завершилась'


def execute(code, inputs='', override=None, guard=contextlib.nullcontext):
    """Выполняет inputs, подменяет значения из override, затем код ученика.

    Возвращает (пространство имён, ошибка или None). Вывод — в ns['output'].
    guard — контекст-менеджер вокруг выполнения (в check_tasks.py — тайм-аут).
    """
    ns = {}
    exec(inputs or '', ns)
    ns.update(override or {})
    buffer = io.StringIO()
    try:
        with guard(), contextlib.redirect_stdout(buffer):
            exec(compile(code, STUDENT_FILE, 'exec'), ns)
        error = None
    except BaseException as exc:  # нужна любая ошибка ученика, даже SystemExit
        error = exc
    ns['output'] = buffer.getvalue()
    return ns, error


def format_error(error):
    """Ошибка ученика как в терминале, но только со строками его кода (main.py)."""
    if isinstance(error, TimeoutError):
        return TIMEOUT_MESSAGE
    if isinstance(error, SyntaxError):
        # у синтаксической ошибки нет стека — Python показывает строку и стрелку
        return ''.join(traceback.format_exception_only(error)).rstrip()
    summary = traceback.TracebackException.from_exception(error)
    summary.stack = traceback.StackSummary.from_list(
        [frame for frame in summary.stack if frame.filename == STUDENT_FILE]
    )
    return ''.join(summary.format()).rstrip()


def run_tests(code, task, guard=contextlib.nullcontext):
    """Прогоняет тесты задачи exercise.

    Возвращает (ns, error, failed): пространство имён первого запуска,
    ошибку кода ученика и список сообщений fail непройденных тестов.
    """
    inputs = task.get('inputs') or ''
    ns, error = execute(code, inputs, guard=guard)

    def run(**override):
        result, _ = execute(code, inputs, override, guard=guard)
        return result

    failed = []
    for test in task['check']['tests']:
        env = {**ns, 'source': code, 'run': run}
        try:
            with guard():
                exec(test['code'], env)
        except TimeoutError:
            failed.append(TIMEOUT_MESSAGE)
        except Exception:
            failed.append(test['fail'])
    if error is not None and not failed:
        failed.append(f'код упал: {type(error).__name__}: {error}')
    return ns, error, failed


def run_program(code, inputs=''):
    """Запуск в песочнице и кнопка «Запустить»: вывод и текст ошибки."""
    ns, error = execute(code, inputs)
    return {
        'output': ns['output'],
        'error': format_error(error) if error is not None else '',
    }


def check_exercise(code, task):
    """Кнопка «Проверить» у задачи exercise: вывод, ошибка, результаты тестов."""
    ns, error, failed = run_tests(code, task)
    return {
        'output': ns['output'],
        'error': format_error(error) if error is not None else '',
        'failed': failed,
        'total': len(task['check']['tests']),
    }


def normalize_output(text):
    """Вывод для сравнения в predict.

    Без пробелов в конце строк и без пустых строк в конце.
    """
    return '\n'.join(line.rstrip() for line in text.rstrip().splitlines())


def check_predict(code, answer):
    """Задача predict: запускает код и сравнивает его вывод с ответом ученика."""
    ns, error = execute(code)
    actual = ns['output']
    if error is not None:
        actual += format_error(error) + '\n'
    return {
        'actual': actual,
        'correct': normalize_output(actual) == normalize_output(answer),
    }

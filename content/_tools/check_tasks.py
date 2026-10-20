"""Проверка контента курсов Python: эталоны задач и оформление уроков.

Запуск: python3 content/_tools/check_tasks.py [путь]   (по умолчанию — content/backend)
Правила — docs/content-format.md, разделы 4–5.
"""
import contextlib
import difflib
import io
import re
import signal
import sys
import traceback
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 2
H2_ORDER = ["Теория", "Наглядно", "На практике", "Частые ошибки", "Итог",
            "Вопросы на собеседовании", "Глубже", "Связанные темы"]
H2_REQUIRED = H2_ORDER[:6]
PSEUDO_GRAPHICS = re.compile(r"[─│┌┐└┘├┤►◄▼▲]")


class Timeout(Exception):
    pass


def _alarm(signum, frame):
    raise Timeout("Программа не завершилась")


signal.signal(signal.SIGALRM, _alarm)


def execute(code, inputs="", override=None):
    """Выполнить код ученика так же, как тренажёр: сначала inputs (код входных данных),
    затем подмена значений из override, затем код ученика."""
    ns = {}
    exec(inputs or "", ns)
    ns.update(override or {})
    buf = io.StringIO()
    signal.alarm(TIMEOUT)
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<student>", "exec"), ns)
        error = None
    except BaseException as e:  # noqa: BLE001 — нужна любая ошибка ученика
        error = e
    finally:
        signal.alarm(0)
    ns["output"] = buf.getvalue()
    return ns, error


def run_tests(code, task):
    """Вернуть список сообщений fail для непройденных тестов."""
    inputs = task.get("inputs") or ""
    ns, error = execute(code, inputs)

    def run(**override):
        result, _ = execute(code, inputs, override)
        return result

    failed = []
    for test in task["check"]["tests"]:
        env = {**ns, "source": code, "run": run}
        try:
            signal.alarm(TIMEOUT)
            exec(test["code"], env)
        except Timeout:
            failed.append("Программа не завершилась")
        except Exception:
            failed.append(test["fail"])
        finally:
            signal.alarm(0)
    if error is not None and not failed:
        failed.append(f"код упал: {type(error).__name__}: {error}")
    return failed


def check_quiz(task):
    problems, options, answer, kind = [], task.get("options") or [], task.get("answer"), task.get("kind")
    if kind not in ("single", "multiple", "order"):
        return [f"kind должен быть single, multiple или order, а не {kind!r}"]
    if len(options) < 2:
        problems.append("вариантов ответа меньше двух")
    if not isinstance(answer, list) or not all(isinstance(i, int) for i in answer):
        return problems + ["answer — список индексов (целых чисел)"]
    if any(i < 0 or i >= len(options) for i in answer):
        problems.append(f"индекс в answer вне options (вариантов {len(options)}, индексы с нуля)")
    if len(set(answer)) != len(answer):
        problems.append("индексы в answer повторяются")
    if kind == "single" and len(answer) != 1:
        problems.append("для single в answer ровно один индекс")
    if kind == "multiple" and not answer:
        problems.append("для multiple в answer хотя бы один индекс")
    if kind == "order" and sorted(answer) != list(range(len(options))):
        problems.append("для order в answer должны быть все индексы options")
    return problems


def failed_rules(files, rules):
    """Сообщения fail для правил, которые files не проходят (как на сайте: поиск по файлу, флаг m)."""
    failed = []
    for rule in rules:
        name = rule.get("file") or next(iter(files))
        text = files.get(name, "")
        if "must_match" in rule and not re.search(rule["must_match"], text, flags=re.M):
            failed.append(rule["fail"])
        if "must_not_match" in rule and re.search(rule["must_not_match"], text, flags=re.M):
            failed.append(rule["fail"])
    return failed


COMMENT = {".sql": "-- ", ".js": "// "}  # остальные файлы (nginx, Python, YAML, Dockerfile, bash) — "# "


def comment_out_changes(files, solution):
    """Эталон, в котором строки, отличающиеся от исходных файлов, закомментированы."""
    result, changed = {}, False
    for name, text in solution.items():
        marker = COMMENT.get(Path(name).suffix, "# ")
        old, new = files.get(name, "").splitlines(), text.splitlines()
        lines = list(new)
        for tag, _, _, j1, j2 in difflib.SequenceMatcher(None, old, new).get_opcodes():
            if tag in ("replace", "insert"):
                for j in range(j1, j2):
                    if lines[j].strip():
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        lines[j] = lines[j][:indent] + marker + lines[j][indent:]
                        changed = True
        result[name] = "\n".join(lines) + "\n"
    return result, changed


def check_fix(task):
    problems = []
    files, solution = task.get("files") or {}, task.get("solution") or {}
    rules = (task.get("check") or {}).get("rules") or []
    if task.get("check", {}).get("type") != "rules":
        problems.append("check.type для fix — rules")
    if not files or not rules:
        return problems + ["нужны files и check.rules"]
    for rule in rules:
        kinds = [k for k in ("must_match", "must_not_match") if k in rule]
        if len(kinds) != 1:
            problems.append(f"в правиле должно быть ровно одно из must_match / must_not_match: {rule}")
            continue
        if "fail" not in rule:
            problems.append(f"у правила нет fail: {rule}")
        if "file" not in rule and len(files) > 1:
            problems.append(f"файлов несколько — у правила нужен file: {rule}")
        if rule.get("file", next(iter(files))) not in files:
            problems.append(f"файла {rule['file']!r} нет в files")
        try:
            re.compile(rule[kinds[0]])
        except re.error as e:
            problems.append(f"шаблон не компилируется: {rule[kinds[0]]!r}: {e}")
        if "(?P<" in rule[kinds[0]] or re.search(r"\\[AZ]|\(\?[aiLmsux]+\)", rule[kinds[0]]):
            problems.append(f"шаблон несовместим с JavaScript: {rule[kinds[0]]!r}")
    if problems:
        return problems
    if set(solution) != set(files):
        return problems + ["в solution должны быть те же файлы, что в files"]
    if fails := failed_rules(solution, rules):
        problems.append(f"эталон не проходит правила: {fails}")
    if not failed_rules(files, rules):
        problems.append("исходные файлы проходят все правила — задача ничего не проверяет")
    commented, changed = comment_out_changes(files, solution)
    if changed and not failed_rules(commented, rules):
        problems.append("закомментированный эталон проходит правила — начните шаблоны директив с ^\\s*")
    return problems


def check_task(path):
    try:
        task = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        return [f"YAML не читается: {e}"]
    problems = []

    def walk(value):
        if isinstance(value, dict):
            for v in value.values():
                yield from walk(v)
        elif isinstance(value, list):
            for v in value:
                yield from walk(v)
        elif isinstance(value, str):
            yield value

    for value in walk({k: v for k, v in task.items() if k not in ("starter_code", "solution", "code", "inputs")}):
        if '\\"' in value and "assert" not in value:
            problems.append(f"буквальный \\\" в тексте (нужны кавычки в YAML): {value[:60]!r}")
    for key in ("title", "type", "difficulty", "pitfall", "statement", "explanation"):
        if key not in task:
            problems.append(f"нет поля {key}")
    if task["type"] == "exercise":
        if fails := run_tests(task["solution"], task):
            problems.append(f"эталон не проходит: {fails}")
        if not run_tests(task["starter_code"], task):
            problems.append("заготовка проходит все тесты — задача ничего не проверяет")
    elif task["type"] == "quiz":
        problems += check_quiz(task)
    elif task["type"] == "fix":
        problems += check_fix(task)
    elif task["type"] == "predict":
        ns, error = execute(task["code"])
        if ns["output"] != task["answer"]:
            problems.append(f"ответ не совпадает с выводом:\n{ns['output']!r}\n{task['answer']!r}")
    return problems


def fenced_blocks(text):
    """Блоки кода урока: (язык, код, строка перед блоком)."""
    blocks, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        if lines[i].startswith("```"):
            lang = lines[i][3:].strip()
            prev = next((l for l in reversed(lines[:i]) if l.strip()), "")
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            blocks.append((lang, "\n".join(lines[i + 1:j]), prev))
            i = j
        i += 1
    return blocks


def check_lesson_code(text):
    """Выполнить блоки ```python по порядку и сверить с блоками «Результат:»."""
    problems, ns = [], {}
    blocks = fenced_blocks(text)
    for k, (lang, code, _) in enumerate(blocks):
        if lang != "python":
            continue
        expected = None
        if k + 1 < len(blocks) and blocks[k + 1][0] == "" and blocks[k + 1][2].startswith("Результат"):
            expected = blocks[k + 1][1]
        buf = io.StringIO()
        error = None
        signal.alarm(TIMEOUT)
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, "main.py", "exec"), ns)
        except BaseException as e:  # noqa: BLE001
            error = traceback.format_exception(e)[-1].rstrip("\n")
        finally:
            signal.alarm(0)
        actual = buf.getvalue().rstrip("\n")
        first = code.splitlines()[0][:50]
        if expected is None:
            if error:
                problems.append(f"пример «{first}» упал без блока «Результат:»: {error}")
            continue
        exp_lines = expected.splitlines()
        markers = [n for n, l in enumerate(exp_lines) if l.startswith("Traceback") or l.startswith('  File "')]
        looks_like_error = bool(re.match(r"^[\w.]+(Error|Exception)\b.*: ", exp_lines[-1]))
        if markers or (error and looks_like_error):
            exp_out = "\n".join(exp_lines[:markers[0]] if markers else exp_lines[:-1])
            if error != exp_lines[-1]:
                problems.append(f"пример «{first}»: ожидалась ошибка {exp_lines[-1]!r}, получено {error!r}")
            if actual != exp_out:
                problems.append(f"пример «{first}»: вывод до ошибки {actual!r} ≠ {exp_out!r}")
        else:
            if error:
                problems.append(f"пример «{first}» упал: {error}")
            elif actual != expected.rstrip("\n"):
                problems.append(f"пример «{first}»: вывод {actual!r} ≠ ожидаемому {expected!r}")
    return problems


def check_lesson(path):
    text = path.read_text()
    problems = []
    h2 = re.findall(r"^## (.+)$", text, flags=re.M)
    if [h for h in h2 if h not in H2_ORDER]:
        problems.append(f"лишние заголовки H2: {[h for h in h2 if h not in H2_ORDER]}")
    if [h for h in h2 if h in H2_ORDER] != sorted([h for h in h2 if h in H2_ORDER], key=H2_ORDER.index):
        problems.append(f"порядок H2 нарушен: {h2}")
    if missing := [h for h in H2_REQUIRED if h not in h2]:
        problems.append(f"нет обязательных блоков: {missing}")
    if PSEUDO_GRAPHICS.search(text):
        problems.append("псевдографика в тексте — нужен SVG")

    lines = text.splitlines()
    in_code = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            if not in_code:
                prev = next((l for l in reversed(lines[:i]) if l.strip()), "")
                if not (prev.rstrip().endswith(":") or prev.startswith("Результат")):
                    problems.append(f"строка {i + 1}: блок кода без пояснения перед ним")
            in_code = not in_code
            continue
        if in_code:
            continue
        prev = next((l for l in reversed(lines[:i]) if l.strip()), "")
        if line.startswith("|---") or (line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|---")):
            if line.startswith("|") and not prev.startswith("|") and not prev.startswith("**Таблица"):
                problems.append(f"строка {i + 1}: таблица без подписи «**Таблица N.**»")
        if line.startswith("![") and not prev.startswith("**Рисунок"):
            problems.append(f"строка {i + 1}: рисунок без подписи «**Рисунок N.**»")
        if line.startswith("![") and (m := re.search(r"\]\((.+?)\)", line)):
            if not (path.parent / m.group(1)).exists():
                problems.append(f"строка {i + 1}: нет файла {m.group(1)}")
    problems += check_lesson_code(text)
    return problems


def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "backend"
    total = bad = 0
    for path in sorted(base.rglob("*")):
        if path.name.startswith("_") or path.parent.name == "img":
            continue
        if path.suffix == ".yaml":
            problems = check_task(path)
        elif path.suffix == ".md":
            problems = check_lesson(path)
        else:
            continue
        total += 1
        if problems:
            bad += 1
            print(f"✗ {path.relative_to(base) if path.is_relative_to(base) else path}")
            for p in problems:
                print(f"    {p}")
    print(f"\nПроверено файлов: {total}, с ошибками: {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

"""Проверка контента курсов Python: эталоны задач и оформление уроков.

Запуск: python3 content/_tools/check_tasks.py [путь] [--quick]   (по умолчанию — content/backend)
Правила — docs/content-format.md, разделы 4–5.

Проверка идёт параллельно при SEEDS разных PYTHONHASHSEED: хеш строк в Python случаен
в каждом запуске, и пример, зависящий от него (порядок множества строк, совпадение ячеек
словаря), даёт разный вывод. Такие ошибки помечаются как нестабильные. --quick — один запуск.
"""
import concurrent.futures
import contextlib
import json
import os
import subprocess
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
            with contextlib.redirect_stdout(io.StringIO()):   # print из функций ученика не мешает выводу проверки
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


# Команды симулятора Linux/Git и их флаги (docs/content-format.md, «exercise с проверкой состояния»).
# None — флаги не поддерживаются; набор — разрешённые флаги.
LINUX_COMMANDS = {
    "pwd": None, "cd": None, "ls": {"-l", "-a"}, "cat": None, "echo": None, "mkdir": {"-p"},
    "touch": None, "rm": {"-r"}, "cp": {"-r"}, "mv": None, "ln": {"-s"}, "head": {"-n"}, "tail": {"-n"},
    "wc": {"-l"}, "grep": {"-i", "-n", "-r", "-c", "-v"}, "sort": {"-n", "-r"}, "uniq": {"-c"},
    "cut": {"-d", "-f"}, "find": {"-name", "-type", "-size"}, "tar": {"-c", "-x", "-z", "-f"},
    "chmod": None, "chown": {"-R"},
}
GIT_COMMANDS = {
    "init": None, "status": None, "add": None, "commit": {"-m"}, "log": {"--oneline", "--graph"},
    "branch": None, "switch": {"-c"}, "merge": None, "rebase": None, "reset": {"--soft", "--hard"},
    "restore": {"--staged"}, "stash": None, "diff": None, "cherry-pick": None, "revert": None, "tag": None,
}
STATE_RULES = {  # ключ, по которому узнаём правило → какие ещё ключи обязательны
    "exists": {"path"}, "contains": {"path"}, "mode": {"path"}, "owner": {"path"}, "link_to": {"path"},
    "output_matches": set(),
    "head": set(), "commit_in": set(), "clean": set(), "merged": set(),
}


def check_command(line):
    """Проблемы одной строки solution: неизвестные команды и флаги."""
    problems = []
    line_wo_strings = re.sub(r"\"[^\"]*\"|'[^']*'", "STR", line)   # текст в кавычках — не флаги
    for part in line_wo_strings.split("|"):
        part = re.split(r"\d?>>?", part)[0]       # перенаправление (>, >>, 2>, 2>&1): дальше — цель
        tokens = part.split()
        if not tokens:
            continue
        if tokens[0] == "git":
            if len(tokens) < 2 or tokens[1] not in GIT_COMMANDS:
                problems.append(f"команды git {tokens[1] if len(tokens) > 1 else ''!s} нет в симуляторе: {line!r}")
                continue
            allowed, flags = GIT_COMMANDS[tokens[1]], tokens[2:]
            if tokens[1] == "stash" and flags[:1] == ["pop"]:
                flags = flags[1:]
        elif tokens[0] in LINUX_COMMANDS:
            allowed, flags = LINUX_COMMANDS[tokens[0]], tokens[1:]
        else:
            problems.append(f"команды {tokens[0]!r} нет в симуляторе: {line!r}")
            continue
        for flag in (t for t in flags if t.startswith("-") and not re.fullmatch(r"[-+]?\d+[KMG]?", t)):
            letters = [flag] if flag.startswith("--") or len(flag) == 2 else [f"-{c}" for c in flag[1:]]
            if flag in (allowed or set()):
                continue
            if any(flag.startswith(v) and v in (allowed or set()) for v in ("-n", "-d", "-f")):
                continue                        # значение слитно с флагом: -n20, -d, -f1
            if any(f not in (allowed or set()) for f in letters):
                problems.append(f"флаг {flag} у {tokens[0] if tokens[0] != 'git' else 'git ' + tokens[1]} не поддерживается симулятором: {line!r}")
    return problems


def check_state(task):
    problems = []
    setup, rules = task.get("setup") or {}, (task.get("check") or {}).get("expect") or []
    unknown = set(setup) - {"cwd", "files", "dirs", "commits", "branch", "head"}
    if unknown:
        problems.append(f"неизвестные ключи setup: {sorted(unknown)}")
    if "cwd" in setup and not str(setup["cwd"]).startswith("/"):
        problems.append("setup.cwd — абсолютный путь")
    for path in list((setup.get("files") or {})) + list(setup.get("dirs") or []):
        if not str(path).startswith("/"):
            problems.append(f"путь в setup не абсолютный: {path!r}")
    file_keys = {"content", "size", "owner", "mode"}
    for path, value in (setup.get("files") or {}).items():
        if isinstance(value, dict):
            if set(value) - file_keys:
                problems.append(f"у файла {path} неизвестные ключи: {sorted(set(value) - file_keys)}")
            if "content" in value and "size" in value:
                problems.append(f"у файла {path} либо content, либо size")
            if "size" in value and not re.fullmatch(r"\d+[KMG]?", str(value["size"])):
                problems.append(f"размер файла {path} — число с K, M или G: {value['size']!r}")
            if "mode" in value and not (isinstance(value["mode"], str) and re.fullmatch(r"[0-7]{3}", value["mode"])):
                problems.append(f"mode файла {path} — три цифры строкой")
        elif not isinstance(value, str):
            problems.append(f"файл {path}: текст или словарь content/size, owner, mode")
    dirs = setup.get("dirs") or []
    if isinstance(dirs, dict):
        for path, value in dirs.items():
            if not isinstance(value, dict) or set(value) - {"owner", "mode"}:
                problems.append(f"папка {path}: словарь с owner/mode")
    for commit in setup.get("commits") or []:
        if not isinstance(commit, dict) or "message" not in commit:
            problems.append(f"у коммита в setup нужен message: {commit!r}")
    if not rules:
        problems.append("нет правил check.expect")
    for rule in rules:
        kinds = [k for k in STATE_RULES if k in rule]
        if "branch" in rule and "exists" in rule and "path" not in rule:
            kinds = ["exists"]
        if len(kinds) != 1:
            problems.append(f"в правиле должен быть ровно один вид проверки: {rule}")
            continue
        kind = kinds[0]
        if "fail" not in rule:
            problems.append(f"у правила нет fail: {rule}")
        if kind == "exists" and "path" not in rule and "branch" not in rule:
            problems.append(f"exists проверяет path или branch: {rule}")
        if kind in ("contains", "mode") and "path" not in rule:
            problems.append(f"{kind} требует path: {rule}")
        if kind == "mode" and not (isinstance(rule["mode"], str) and re.fullmatch(r"[0-7]{3}", rule["mode"])):
            problems.append(f"mode — три восьмеричные цифры строкой, например '644': {rule}")
        if kind == "commit_in" and not {"branch", "message"} <= set(rule["commit_in"] or {}):
            problems.append(f"commit_in требует branch и message: {rule}")
        if kind == "merged" and not {"from", "into"} <= set(rule["merged"] or {}):
            problems.append(f"merged требует from и into: {rule}")
        for pattern in (rule.get("contains"), rule.get("output_matches"), (rule.get("commit_in") or {}).get("message")):
            if pattern is None:
                continue
            try:
                re.compile(pattern)
            except re.error as e:
                problems.append(f"шаблон не компилируется: {pattern!r}: {e}")
    lines = [l.strip() for l in (task.get("solution") or "").splitlines() if l.strip()]
    if not lines:
        problems.append("нет solution — команды по одной на строку")
    for line in lines:
        problems += check_command(line)
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
    if task["type"] == "exercise" and (task.get("check") or {}).get("type") == "state":
        problems += check_state(task)
    elif task["type"] == "exercise":
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


SEEDS = 16


def collect(base):
    """{файл: [проблемы]} для одного запуска интерпретатора."""
    results = {}
    for path in sorted(base.rglob("*")):
        if path.name.startswith("_") or path.parent.name == "img":
            continue
        if path.suffix == ".yaml":
            problems = check_task(path)
        elif path.suffix == ".md":
            problems = check_lesson(path)
        else:
            continue
        results[str(path.relative_to(base) if path.is_relative_to(base) else path)] = problems
    return results


def run_seed(base, seed):
    env = {**os.environ, "PYTHONHASHSEED": str(seed)}
    proc = subprocess.run([sys.executable, __file__, str(base), "--json"],
                          capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return json.loads(proc.stdout)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base = Path(args[0]).resolve() if args else ROOT / "backend"
    if "--json" in sys.argv:
        print(json.dumps(collect(base), ensure_ascii=False))
        return
    if "--quick" in sys.argv:
        runs = [collect(base)]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
            runs = list(pool.map(lambda seed: run_seed(base, seed), range(SEEDS)))
    bad = 0
    for name in runs[0]:
        counts = {}
        for run in runs:
            for problem in run.get(name, []):
                counts[problem] = counts.get(problem, 0) + 1
        if not counts:
            continue
        bad += 1
        print(f"✗ {name}")
        for problem, n in counts.items():
            note = "" if n == len(runs) else f"  [нестабильно: в {n} из {len(runs)} запусков — зависит от хеша строк?]"
            print(f"    {problem}{note}")
    print(f"\nПроверено файлов: {len(runs[0])}, с ошибками: {bad}, запусков: {len(runs)}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

---
title: pathlib
type: lesson
level: 2
reading_time: 7
---

## Теория
Путь к файлу можно хранить строкой, но склеивать пути строками неудобно и опасно: легко забыть разделитель, а на Windows он вообще другой (`\` вместо `/`). Модуль `pathlib` даёт объект `Path`: пути соединяются оператором `/`, у пути есть удобные свойства (имя файла, расширение, родительская папка) и методы — проверить, существует ли файл, создать папку, прочитать или записать текст, найти файлы по шаблону. Код с `Path` одинаково работает на Linux, macOS и Windows.

В Django-проектах `pathlib` встречается с первой строки `settings.py`: `BASE_DIR = Path(__file__).resolve().parent.parent`, `MEDIA_ROOT = BASE_DIR / "media"`. Две вещи, на которых чаще всего ошибаются: папки создаются явно, причём для вложенных нужен `parents=True`, а повторное создание без `exist_ok=True` падает; и шаблон `glob("*.csv")` ищет только в самой папке — в подпапки он не заходит.

## Наглядно
**Таблица 1.** Части пути `Path("reports/2026-10/orders.csv")`.

| Запись | Результат |
|---|---|
| `path.name` | `orders.csv` |
| `path.stem` | `orders` |
| `path.suffix` | `.csv` |
| `path.parent` | `reports/2026-10` |
| `Path("reports") / "2026-10" / "orders.csv"` | тот же путь, собранный из частей |

**Таблица 2.** Основные методы `Path`.

| Метод | Что делает |
|---|---|
| `exists()`, `is_file()`, `is_dir()` | проверки |
| `mkdir(parents=True, exist_ok=True)` | создать папку вместе с родительскими; не падать, если есть |
| `write_text(text, encoding="utf-8")`, `read_text(encoding="utf-8")` | записать / прочитать файл целиком |
| `iterdir()` | содержимое папки |
| `glob("*.csv")`, `rglob("*.csv")` | файлы по шаблону: в папке / во всех подпапках |
| `unlink(missing_ok=True)` | удалить файл |

## На практике
Задача: складывать ежемесячные отчёты в папки `reports/<месяц>/`, читать их и находить все отчёты за год.

### Шаг 1. Собираем путь из частей
Оператор `/` соединяет части с правильным разделителем:
```python
from pathlib import Path

reports = Path("reports")
path = reports / "2026-10" / "orders.csv"
print(path)
print(path.name, path.stem, path.suffix, path.parent)
```
Результат:
```
reports/2026-10/orders.csv
orders.csv orders .csv reports/2026-10
```

### Шаг 2. Создаём папки
Папки отчёта ещё нет. Без `parents=True` вложенную папку не создать:
```python
month_dir = reports / "2026-10"
month_dir.mkdir(parents=True, exist_ok=True)
print(month_dir.is_dir())
(reports / "2026-11" / "daily").mkdir()
```
Результат:
```
True
FileNotFoundError: [Errno 2] No such file or directory: 'reports/2026-11/daily'
```
`exist_ok=True` разрешает повторный вызов, когда папка уже есть, — без него второй `mkdir` выбросил бы `FileExistsError`.

### Шаг 3. Пишем и читаем файл
Для небольших файлов `open` не нужен — у `Path` есть методы целиком:
```python
path.write_text("order_id,total\n1042,1499\n", encoding="utf-8")
print(path.exists(), path.is_file())
print(path.read_text(encoding="utf-8"))
```
Результат:
```
True True
order_id,total
1042,1499
```

### Шаг 4. Находим файлы по шаблону
Добавим отчёт за ноябрь и поищем все CSV. `glob` смотрит только в саму папку, `rglob` — во все вложенные:
```python
(reports / "2026-11").mkdir(exist_ok=True)
(reports / "2026-11" / "orders.csv").write_text("order_id,total\n", encoding="utf-8")

print(list(reports.glob("*.csv")))
print(sorted(str(p) for p in reports.rglob("*.csv")))
print(sorted(p.name for p in reports.iterdir()))
```
Результат:
```
[]
['reports/2026-10/orders.csv', 'reports/2026-11/orders.csv']
['2026-10', '2026-11']
```
Порядок файлов от `glob` и `iterdir` не гарантирован — для вывода и тестов результат сортируют.

### Шаг 5. Работаем с путями в настройках
Так в Django считают пути от расположения файла настроек — `__file__` содержит путь к текущему файлу:
```python
settings_file = Path("/srv/shop/config/settings.py")
base_dir = settings_file.parent.parent
print(base_dir, base_dir / "media")
```
Результат:
```
/srv/shop /srv/shop/media
```

## Частые ошибки
- **Склейка путей строками.** `"reports" + "2026-10"` даёт `reports2026-10`; `"reports/" + ...` ломается на Windows. Используйте `Path(...) / "часть"`.
- **`mkdir` без параметров.** Вложенная папка без `parents=True` — `FileNotFoundError`; повторное создание без `exist_ok=True` — `FileExistsError`.
- **`glob` вместо `rglob`.** `glob("*.csv")` не заходит в подпапки; для поиска по всему дереву — `rglob("*.csv")` или `glob("**/*.csv")`.
- **Порядок файлов.** `glob` и `iterdir` не сортируют — сортируйте сами.
- **`read_text` без `encoding`.** Как и у `open`, кодировка по умолчанию зависит от системы.

## Итог
**Пути**
- `Path("a") / "b" / "c.csv"` — сборка пути; `name`, `stem`, `suffix`, `parent` — части.
- `Path(__file__).resolve().parent` — папка текущего файла (так устроен `BASE_DIR` в Django).

**Файлы и папки**
- `exists()`, `is_file()`, `is_dir()`; `mkdir(parents=True, exist_ok=True)`.
- `write_text(…, encoding="utf-8")`, `read_text(encoding="utf-8")` — для небольших файлов.

**Поиск**
- `glob("*.csv")` — в папке, `rglob("*.csv")` — по всему дереву; порядок не гарантирован — `sorted(...)`.

## Вопросы на собеседовании
<details><summary>Чем `pathlib.Path` лучше строк для путей?</summary>

Пути собираются оператором `/` с правильным разделителем для системы, у пути есть свойства (`name`, `suffix`, `parent`) и методы работы с файлами. Код получается короче, читается лучше и одинаково работает на разных ОС.
</details>

<details><summary>Как создать вложенную папку, не падая, если она уже есть?</summary>

`Path("a/b/c").mkdir(parents=True, exist_ok=True)`: `parents` создаёт недостающие родительские папки, `exist_ok` разрешает вызов для уже существующей папки.
</details>

<details><summary>Чем `glob` отличается от `rglob`?</summary>

`glob("*.csv")` ищет совпадения только в самой папке, `rglob("*.csv")` — рекурсивно во всех вложенных (то же самое, что `glob("**/*.csv")`).
</details>

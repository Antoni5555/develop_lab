# Программа направления Backend (Python) — обзор

> Черновик от 2026-10-20. Карты составлены по структуре и заголовкам конспектов.
> Стандарт темы и сквозной контекст — [01-standard.md](01-standard.md).

## Принятые решения
- Курс **Git** добавлен. За основу берём конспект `Git.docx` (он по чужому курсу): теорию и примеры пишем заново, своими словами.
- **ООП и асинхронность** — разделы курса Python.
- **NoSQL** убран.
- **Django ORM** — строго модели и QuerySet. Остальное из Django — позже.
- **Python** — с нуля.
- Во всех курсах один контекст: **backend интернет-магазина**. Внутри курса сложность растёт от раздела к разделу (●○○ → ●●○ → ●●●).

## Курсы
| Шаг | Курс | Разделов | Тем | Сырьё в конспектах | Карта |
|---|---|---|---|---|---|
| 10 | Python | 8 | 57 | ~половина (коллекции, функции, ООП, SOLID); с нуля — основы, файлы, asyncio | [python.md](python.md) |
| 20 | Linux | 6 | 24 | почти нет | [linux.md](linux.md) |
| 30 | Git | 5 | 24 | `Git.docx` → разделы 1–4 | [git.md](git.md) |
| 40 | SQL | 9 | 47 | лучшее покрытие (~35 тем) | [sql.md](sql.md) |
| 50 | Django ORM | 6 | 34 | только план в README | [django-orm.md](django-orm.md) |
| 60 | SQLAlchemy | 6 | 24 | нет | [sqlalchemy.md](sqlalchemy.md) |
| 70 | Docker | 4 | 17 | команды есть, Dockerfile/compose нет | [docker.md](docker.md) |
| 80 | Nginx | 5 | 17 | кэш и ошибки есть, синтаксис конфига нет | [nginx.md](nginx.md) |
| | **Всего** | **49** | **244** | | |

Docker и Nginx разделены на два курса: у них разные тренажёры (в `docs/architecture.md` они упомянуты отдельно), и каждый получился полноценным.

## Источники
| Где | Что там | Используем в |
|---|---|---|
| `THEORY_BOOK/base_python_backend_theory/day_1_python_basics`, `day_3_oop`, `day_4_async` | Python | Python |
| `THEORY_BOOK/base_python_backend_theory/day_2_databases/01–05` | SQL-теория | SQL |
| `THEORY_BOOK/training_skills/SQL` | DDL + практикум с заданиями | SQL |
| `КОНСПЕКТЫ/ТЕОРИЯ/Базы данных/Базы данных.docx` | оглавление по SQL | SQL |
| `THEORY_BOOK/README.md` | план Django | Django ORM |
| `КОНСПЕКТЫ/ТЕОРИЯ/Git/Git.docx` | конспект по Git | Git |
| `THEORY_BOOK/training_skills/Docker`, `DevOps/Nginx`, `nginx_gunicorn.md`, `website_performance_optimization.md` | Docker, деплой, кэш | Docker, Nginx |
| `training_skills/connect_to_*.md`, `Python/pyenv.md` | SSH, pyenv | Linux, Git, Python |

**Не используем:** `day_2_databases/06_nosql_overview.md`, `practice/` (кроме хода мысли о проектировании моделей), `reserve_data_server/`, ffmpeg, файлы с промптами, папки практики Git-курса, `middle_course/` (только как ориентир по коду).

## Исправить в источниках при написании (⚠️)
- SQL: «кластеризованные индексы» — термин MySQL/SQL Server, к PostgreSQL не относится; пример Phantom Read для MySQL — заменить на PostgreSQL.
- Git: вероятно, старые `checkout`/`reset HEAD` → даём `switch`/`restore`.
- Python: `OrderedDict` подавать как устаревающий; `super()` перенести из функций в ООП.

## Вопросы к «Разработке» (влияют на типы задач)
1. Git в браузере (isomorphic-git?) — будут ли живые задачи по веткам и remote.
2. Django + SQLAlchemy 2.0 в Pyodide; async SQLAlchemy.
3. Новые типы задач для тем без живого запуска: `quiz` и `fix` (проверка конфига или кода по правилам).

## Что дальше
1. Ты смотришь программы и стандарт ([01-standard.md](01-standard.md)), правишь или говоришь «ок».
2. Обновляем черновик схемы магазина: `profiles`, `tags`, `attributes jsonb`, `promo_codes`.
3. Пилотная тема в стандарте (предлагаю SQL → «LEFT и RIGHT JOIN»): урок + 5 задач.
4. После оценки пилота — пишем курсы по порядку, порциями по разделу.

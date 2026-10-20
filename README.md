# SITE_NAME

Бесплатная платформа практики для разработчиков: короткая теория + интерактивные
тренажёры (SQL, ORM, Python, Linux) прямо в браузере.

Контекст проекта и принятые решения — в [docs/architecture.md](docs/architecture.md), план и архитектура —
в [docs/START.md](docs/START.md).

## Запуск в Docker (рекомендуется)

```bash
cp .env.example .env              # и впишите SECRET_KEY
docker compose up --build
```

Сайт: http://localhost:8000. Поднимаются три контейнера: `db` (PostgreSQL 16),
`redis`, `web` (Django, runserver). Код из `src/` подключён папкой — правки видны сразу.

## Тесты и линтер

Нужен Python 3.12.

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
flake8
pytest
```

Тестам с базой данных нужен PostgreSQL: проще всего держать запущенным
`docker compose up db` (порт 5432 открыт только для вашего компьютера).

## Структура

```
src/
├── config/          настройки (settings/base, development, production, test) и urls
├── core/            общий код: context processors, страницы ошибок, health-check
├── apps/            приложения: pages, courses, cheatsheets, trainers, accounts
├── templates/       base/, common/, <страница>/components/ — как помечено в design/
└── static/          css/ (base, components, pages/*, media), js/, fonts/
tests/               pytest
design/              макет — эталон дизайна, как код проекта не правится
```

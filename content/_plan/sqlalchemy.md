# Курс: SQLAlchemy 2.0 — карта

Источники: **нет** (ни в THEORY_BOOK, ни в КОНСПЕКТЫ). Можно глянуть `КОНСПЕКТЫ/ТЕОРИЯ/FastAPI/` — там SQLAlchemy может встречаться.
Всё ниже — моё предложение программы, все темы ❌.

## 1. Введение
- Что такое SQLAlchemy: Core и ORM, чем отличается от Django ORM (таблица-сравнение)
- `Engine`, подключение, `Session`

## 2. Модели (Declarative, стиль 2.0)
- `DeclarativeBase`, `Mapped[...]`, `mapped_column()`
- Ограничения, значения по умолчанию
- Создание таблиц `metadata.create_all()`; миграции Alembic — обзорно

## 3. Запросы `select()`
- `session.scalars(select(...))`, `session.execute()`
- `where`, `order_by`, `limit`
- `scalar_one`, `first`, `all` — что когда

## 4. Изменение данных
- `session.add`, `commit`, `rollback`; `update()`/`delete()` конструкцией
- Жизненный цикл объекта в сессии (identity map) — коротко

## 5. Связи
- `relationship()`, `back_populates`, 1:N и N:M (`secondary`)
- `join()` в запросах
- Ленивая загрузка и N+1; `selectinload`, `joinedload`

## 6. Агрегация и продвинутое
- `func.count`, `group_by`, `having`
- Подзапросы и CTE (`.subquery()`, `.cte()`)

## Итог
Пишется полностью с нуля. ⚠️ Нужно подтвердить у «Разработки», что SQLAlchemy запускается в браузере (Pyodide) с PGlite/SQLite — от этого зависят задачи.

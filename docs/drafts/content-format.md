> **ЧЕРНОВИК.** Стартовое предложение, не утверждено. Дорабатывается в сессии «Контент».

# Формат контента

Весь контент хранится в репозитории и загружается командой `manage.py load_content`.
Если формат меняется, правим этот файл и загрузчик в одном коммите.

## Структура папок

```
content/
  backend/                      # направление (track)
    _track.yaml                 # title, description, order
    _shared/                    # общая учебная БД «магазин»
    sql/                        # курс
      _course.yaml              # title, description, engine, order (шаг 10)
      04-joins/                 # раздел: NN-slug
        _section.yaml           # title, description
        02-join-types/          # тема: NN-slug
          _topic.yaml           # title
          01-join-types.md      # урок (теория)
          02-users-without-orders.yaml   # задача
```

Номер `NN` задаёт порядок. Slug пишется латиницей в kebab-case и после публикации не меняется, потому что от него зависят URL и прогресс пользователей.

## Урок: Markdown

```markdown
---
title: Виды JOIN
type: lesson
reading_time: 7          # минуты
---

Короткое вступление: какую проблему решает тема (1–2 предложения).

## Как это работает
...

## Пример
```sql
SELECT ...
```

## Частые ошибки
- ...

## Итого
- 3–5 пунктов, которые стоит запомнить.
```

Правила:
- объём 300–900 слов;
- один урок посвящён одной идее;
- все примеры на учебной БД «магазин» (`docs/shop-schema.md`);
- каждый пример реально запускается.

## Задача: YAML

```yaml
title: Покупатели без заказов
type: exercise
difficulty: 2               # 1 — лёгкая, 2 — средняя, 3 — сложная
statement: |
  Выведите `id` и `email` пользователей, которые ни разу не оформили заказ.
  Отсортируйте по `id`.
solutions:                  # эталоны; ключи — тренажёры, где задача доступна
  sql: |
    SELECT u.id, u.email
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.id
    WHERE o.id IS NULL
    ORDER BY u.id;
  django: |
    User.objects.filter(orders__isnull=True).order_by('id').values('id', 'email')
  sqlalchemy: |
    select(User.id, User.email).outerjoin(User.orders).where(Order.id.is_(None)).order_by(User.id)
check:
  type: result              # result — сравнить результат; state — сравнить таблицы после DML
  order_matters: true
hints:
  - Подойдёт LEFT JOIN.
  - У пользователя без заказов поля из orders будут NULL.
explanation: |              # показывается после решения
  INNER JOIN отбросил бы пользователей без заказов...
```

Правила:
- в условии сказано, какие колонки и в каком порядке вывести и нужна ли сортировка, чтобы проверка была однозначной;
- 1–3 подсказки, от намёка к почти готовому решению;
- `explanation` объясняет, почему решение работает, а не пересказывает код.

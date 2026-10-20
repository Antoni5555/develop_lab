# Курс: Django ORM (Django 5.x) — карта

Источники:
- `THEORY_BOOK/README.md`, «Блок: Изучение Django → День 1» — **подробный план** 8 тем (текста нет)
- `django_learning/day_1_models_and_orm/01_models_fields_and_relationships.md` — **пустой**
- `practice/create_foodgram/create_foodgrame.md` — «Проектирование моделей» (ход мысли при проектировании) — кандидат в пример
- `middle_course/new_admin_panel_sprint_1` — модели кино-БД (код)

Легенда — в [00-overview.md](00-overview.md).

## 1. Модели
| Тема | Покрытие | Комментарий |
|---|---|---|
| Модель = таблица; поля и их типы | 🟡 план | README 1 |
| Параметры полей: `null`, `blank`, `default`, `choices`, `unique`, `db_index` | 🟡 план | README 1 |
| Связи: `ForeignKey`, `on_delete`, `related_name` | 🟡 план | README 1 |
| `ManyToManyField`, `through`; `OneToOneField` | 🟡 план | README 1 |
| `class Meta`: `ordering`, `constraints`, `db_table` | 🟡 план | README 2 |
| Методы модели: `save()`, `clean()`, `__str__` | 🟡 план | README 2 |
| Миграции: `makemigrations`, `migrate`, `sqlmigrate` | 🟡 план | README 8 — ⚠️ в браузере не запустить; показывать «какой SQL получится» |

## 2. Чтение данных (QuerySet)
| Тема | Покрытие | Комментарий |
|---|---|---|
| Ленивость QuerySet, когда уходит запрос | 🟡 план | README 3 — ключевая тема для визуализации «какие SQL ушли» |
| `all`, `filter`, `exclude`, `get`, `first`, `exists`, `count` | 🟡 план | README 3 |
| Lookups: `__gt`, `__in`, `__contains`, связи через `__` | 🟡 план | README 3 |
| `Q`-объекты, `F`-выражения | 🟡 / ❌ | `Q` в плане, `F` нет — нужен |
| `order_by`, срезы | ❌ | |
| `values`, `values_list` | 🟡 план | README 5 |

## 3. Связи и N+1
| Тема | Покрытие | Комментарий |
|---|---|---|
| Обратные связи, `related_name` в запросах | 🟡 план | |
| Проблема N+1 | 🟡 план | README 4 — главная «фишка» тренажёра (подсветка N+1) |
| `select_related` vs `prefetch_related`, `Prefetch` | 🟡 план | README 4 |

## 4. Агрегация
| Тема | Покрытие | Комментарий |
|---|---|---|
| `aggregate` vs `annotate`; `Count`, `Sum`, `Avg` | 🟡 план | README 5 |
| `Subquery`, `OuterRef` | 🟡 план | README 5 — «дополнительно» |

## 5. Изменение данных
| Тема | Покрытие | Комментарий |
|---|---|---|
| `create`, `save`, `update`, `delete`; `save()` vs `update()` | 🟡 | разбросано по README 3 и Дню 5 |
| `bulk_create`, `get_or_create` | ❌ | |
| Транзакции `transaction.atomic()` | 🟡 план | README 7 |

## 6. Продвинутое
| Тема | Покрытие | Комментарий |
|---|---|---|
| Кастомные менеджеры и QuerySet | 🟡 план | README 6 |
| Сигналы | 🟡 план | README 7 — ⚠️ не совсем ORM; можно убрать в будущий курс Django |

## Вне курса ORM (в README есть, но это «Django целиком»)
Views/CBV, URL, формы, шаблоны, админка, аутентификация, middleware, безопасность, тесты, деплой (README Дни 2–4). В браузерном тренажёре это не запустить → кандидат в будущий теоретический курс «Django» или в DevOps.

## Итог
- Оглавление хорошее и готово почти целиком; **текста нет** — писать всё.
- Нужно решить, как тренажёр выполняет ORM в браузере (Django в Pyodide?) — вопрос к «Разработке», влияет на то, какие задачи возможны.

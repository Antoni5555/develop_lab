---
title: Дата и время
type: lesson
level: 2
reading_time: 9
---

## Теория
Даты в магазине повсюду: когда создан заказ, до какого числа действует промокод, какие заказы пришли за неделю. В Python для этого модуль `datetime`: `date` — календарная дата, `datetime` — дата и время, `timedelta` — промежуток («30 дней», «2 часа»). С ними можно считать — прибавлять промежутки, вычитать даты, сравнивать — и не нужно вручную разбираться с длиной месяцев и високосными годами.

Самое коварное — часовые пояса. `datetime` бывает **наивным** (без часового пояса — «14:30, а где — неизвестно») и **осведомлённым** (`aware`, с поясом — «14:30 UTC»). Сравнивать наивное и осведомлённое время нельзя — `TypeError`. В backend принято правило: **хранить и сравнивать время в UTC**, а в местное время переводить только при показе пользователю. Django и PostgreSQL (`timestamptz`) работают именно так. Для обмена с API время записывают в формате ISO 8601 (`2026-10-20T14:30:00+00:00`), а для людей — в привычном виде через `strftime`.

## Наглядно
**Таблица 1.** Типы модуля `datetime`.

| Тип | Что хранит | Пример | Где в магазине |
|---|---|---|---|
| `date` | год, месяц, день | `date(2026, 12, 31)` | срок действия промокода, день рождения |
| `datetime` | дата + время (+ пояс) | `datetime(2026, 10, 20, 14, 30, tzinfo=timezone.utc)` | создание заказа, время оплаты |
| `timedelta` | промежуток | `timedelta(days=30, hours=2)` | «действует 30 дней», «заказы за 7 дней» |
| `timezone` | фиксированное смещение от UTC | `timezone.utc` | хранение и сравнение времени в UTC |
| `ZoneInfo` (модуль `zoneinfo`) | часовой пояс по имени, с летним временем | `ZoneInfo("Europe/Moscow")` | показ времени покупателю в его поясе |

**Таблица 2.** Преобразование в строку и обратно.

| Задача | Запись | Результат |
|---|---|---|
| для API | `dt.isoformat()` | `"2026-10-20T14:30:00+00:00"` |
| из API | `datetime.fromisoformat(text)` | `datetime` |
| для людей | `dt.strftime("%d.%m.%Y %H:%M")` | `"20.10.2026 14:30"` |
| из формы | `datetime.strptime(text, "%d.%m.%Y")` | `datetime`; формат не совпал — `ValueError` |
| коды формата | `%Y` год, `%m` месяц, `%d` день, `%H` часы, `%M` минуты | |

## На практике
Задача: выдать промокод на 30 дней, проверять, действует ли он, показывать даты покупателю и выбирать заказы за последнюю неделю.

### Шаг 1. Создаём даты
Дата выдачи промокода и момент создания заказа (в UTC):
```python
from datetime import date, datetime, timedelta, timezone

issued = date(2026, 10, 20)
created_at = datetime(2026, 10, 20, 14, 30, tzinfo=timezone.utc)
print(issued, issued.year, issued.month)
print(created_at)
```
Результат:
```
2026-10-20 2026 10
2026-10-20 14:30:00+00:00
```

### Шаг 2. Считаем с промежутками
Прибавление `timedelta` само переходит через границы месяцев, а вычитание дат даёт промежуток:
```python
valid_until = issued + timedelta(days=30)
print(valid_until)
left = valid_until - date(2026, 11, 10)
print(left, left.days)
```
Результат:
```
2026-11-19
9 days, 0:00:00 9
```

### Шаг 3. Сравниваем даты
Даты сравниваются обычными операторами. Промокод действует по последний день включительно:
```python
def is_promo_active(valid_until, today):
    return today <= valid_until

print(is_promo_active(valid_until, date(2026, 11, 19)))
print(is_promo_active(valid_until, date(2026, 11, 20)))
```
Результат:
```
True
False
```

### Шаг 4. Показываем дату покупателю и отдаём в API
Для людей — `strftime`, для API — `isoformat`:
```python
print(created_at.strftime("%d.%m.%Y %H:%M"))
print(created_at.isoformat())
```
Результат:
```
20.10.2026 14:30
2026-10-20T14:30:00+00:00
```

### Шаг 5. Разбираем дату из строки
Дата из формы в формате `ДД.ММ.ГГГГ` и из API в ISO:
```python
birth = datetime.strptime("05.03.1998", "%d.%m.%Y").date()
paid_at = datetime.fromisoformat("2026-10-20T15:02:11+00:00")
print(birth, paid_at.minute)
datetime.strptime("1998-03-05", "%d.%m.%Y")
```
Результат:
```
1998-03-05 2
ValueError: time data '1998-03-05' does not match format '%d.%m.%Y'
```
Строка не в том формате — `ValueError`; данные из формы проверяют так же, как числа.

### Шаг 6. Переводим в местное время
Заказ создан в 14:30 UTC; покупатель в Москве должен увидеть местное время. Пояс задаём по имени через `zoneinfo`:
```python
from zoneinfo import ZoneInfo

moscow = ZoneInfo("Europe/Moscow")
local = created_at.astimezone(moscow)
print(local.strftime("%d.%m.%Y %H:%M %Z"), local.isoformat())
print(local == created_at)
```
Результат:
```
20.10.2026 17:30 MSK 2026-10-20T17:30:00+03:00
True
```
Это один и тот же момент времени, просто записанный в другом поясе, — поэтому `==` даёт `True`.

### Шаг 7. Не смешиваем наивное и осведомлённое время
Время без пояса нельзя сравнить со временем в UTC:
```python
naive = datetime(2026, 10, 20, 14, 0)
print(naive.tzinfo, created_at.tzinfo)
naive < created_at
```
Результат:
```
None UTC
TypeError: can't compare offset-naive and offset-aware datetimes
```
Текущее время в UTC берут так: `datetime.now(timezone.utc)`. Голый `datetime.now()` возвращает наивное местное время сервера.

### Шаг 8. Выбираем заказы за неделю
«Сейчас» передаём параметром — так функцию легко проверить на любой дате:
```python
orders = [
    (1042, datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)),
    (1043, datetime(2026, 10, 13, 12, 0, tzinfo=timezone.utc)),
    (1044, datetime(2026, 10, 10, 18, 0, tzinfo=timezone.utc)),
]

def recent_orders(orders, now, days=7):
    since = now - timedelta(days=days)
    return [order_id for order_id, created in orders if created >= since]

now = datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc)
print(recent_orders(orders, now))
```
Результат:
```
[1042, 1043]
```

## Частые ошибки
- **Наивное и осведомлённое время вместе.** Сравнение — `TypeError`, а вычисления «на глаз» сдвигаются на часы. Храните и сравнивайте время в UTC (`tzinfo=timezone.utc`).
- **`datetime` против `date`.** `datetime(…) <= date(…)` — `TypeError`. Приводите к одному типу: `dt.date()`.
- **Арифметика по полям.** `date(year, month, day - 7)` падает в начале месяца (`ValueError: day is out of range for month`). Промежутки — только через `timedelta`.
- **`datetime.now()` в логике.** Наивное местное время сервера и результат, который нельзя проверить тестом. Берите `datetime.now(timezone.utc)` и передавайте «сейчас» параметром.
- **Фиксированное смещение вместо пояса.** `timezone(timedelta(hours=3))` — просто «+3 часа» и не знает о переходах на летнее время в других странах. Местное время задают поясом по имени: `ZoneInfo("Europe/Berlin")`; в Django — настройкой `TIME_ZONE`.

## Итог
**Типы**
- `date` — дата, `datetime` — дата и время, `timedelta` — промежуток, `timezone` — смещение.
- Дата + `timedelta` → дата; дата − дата → `timedelta` (`.days`).

**Строки**
- Для API — `isoformat()` / `fromisoformat()`; для людей — `strftime()`; из формы — `strptime()` (несовпадение формата — `ValueError`).

**Часовые пояса**
- Наивное время — без пояса, осведомлённое — с поясом; смешивать нельзя.
- Хранить и сравнивать в UTC, переводить в местное при показе: `dt.astimezone(ZoneInfo("Europe/Moscow"))`.
- «Сейчас» — `datetime.now(timezone.utc)`; в функции лучше передавать параметром.

## Вопросы на собеседовании
<details><summary>Чем наивный `datetime` отличается от осведомлённого?</summary>

У наивного нет информации о часовом поясе (`tzinfo is None`), у осведомлённого — есть. Наивное время неоднозначно: «14:30» в Москве и в Лондоне — разные моменты. Сравнивать их между собой Python не даёт (`TypeError`).
</details>

<details><summary>Почему время в базе хранят в UTC?</summary>

UTC не зависит от пояса сервера и пользователя и не имеет переходов на летнее время, поэтому сравнения и вычисления однозначны. В местное время переводят только при показе. PostgreSQL `timestamptz` и Django с `USE_TZ=True` работают именно так.
</details>

<details><summary>Как прибавить к дате месяц?</summary>

Стандартный `timedelta` не умеет «месяц» — у месяцев разная длина. Обычно решают задачей: «30 дней» через `timedelta(days=30)` или, если нужен именно календарный месяц, сторонней библиотекой `dateutil.relativedelta`.
</details>

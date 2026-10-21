---
title: Enum
type: lesson
level: 2
reading_time: 8
---

## Теория
У заказа четыре статуса: `new`, `paid`, `shipped`, `cancelled`. Пока это строки, ничто не мешает написать `order.status = "payed"`. Опечатка не даёт ошибки, а заказ навсегда выпадает из всех отчётов и фильтров. Список допустимых статусов нигде не записан: его ищут поиском по коду. **Перечисление** (`Enum` из модуля `enum`) — класс с фиксированным набором именованных значений: `OrderStatus.PAID`. Опечатка в имени сразу даёт `AttributeError`, редактор подсказывает варианты, а все статусы видны в одном месте.

У каждого члена перечисления есть **имя** (`PAID`) и **значение** (`"paid"`). Значение хранят в базе и передают в API. Строку из запроса превращают в член перечисления по значению: `OrderStatus("paid")`. Неизвестная строка даёт `ValueError` — так невалидный статус отсекается на входе. Обычный `Enum` намеренно не равен своему значению: `OrderStatus.PAID == "paid"` — `False`. Для backend, где статусы постоянно ходят строками в JSON и в базу, удобнее **`StrEnum`** (Python 3.11+). Его члены — настоящие строки: равны значению, подставляются в f-строки и сериализуются в JSON без преобразований.

## Наглядно
**Таблица 1.** Строки, `Enum` и `StrEnum`.

| | Строки `"paid"` | `Enum` | `StrEnum` |
|---|---|---|---|
| Опечатка `PAYED` | не замечается | `AttributeError` | `AttributeError` |
| Список допустимых значений | нигде | `list(OrderStatus)` | `list(OrderStatus)` |
| `status == "paid"` | `True` | **`False`** | `True` |
| `f"{status}"` | `paid` | `OrderStatus.PAID` | `paid` |
| `json.dumps(status)` | работает | **`TypeError`** | работает |
| Из строки | — | `OrderStatus("paid")` | `OrderStatus("paid")` |

**Таблица 2.** Как получить член перечисления.

| Запись | Ищет по | Пример | Если нет |
|---|---|---|---|
| `OrderStatus.PAID` | имени, в коде | — | `AttributeError` |
| `OrderStatus("paid")` | **значению** | строка из API или базы | `ValueError` |
| `OrderStatus["PAID"]` | **имени**, строкой | имя из конфига | `KeyError` |

## На практике
Задача: заменить строковые статусы заказа перечислением, принимать статус из API и задать, какие переходы между статусами разрешены.

### Шаг 1. Видим проблему строк
Опечатка в статусе не даёт никакой ошибки:
```python
orders = [{"id": 1042, "status": "paid"}, {"id": 1043, "status": "payed"}]
print([o["id"] for o in orders if o["status"] == "paid"])
```
Результат:
```
[1042]
```
Заказ 1043 оплачен, но в отчёт об оплаченных не попал.

### Шаг 2. Объявляем перечисление
Члены перечисления — атрибуты класса. У каждого есть `name` и `value`:
```python
from enum import Enum


class OrderStatus(Enum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


status = OrderStatus.PAID
print(status, status.name, status.value)
print([s.value for s in OrderStatus])
print(OrderStatus.PAID is OrderStatus("paid"))
OrderStatus.PAYED
```
Результат:
```
OrderStatus.PAID PAID paid
['new', 'paid', 'shipped', 'cancelled']
True
AttributeError: type object 'OrderStatus' has no attribute 'PAYED'. Did you mean: 'PAID'?
```
Каждый член существует в одном экземпляре, поэтому сравнивать можно и через `==`, и через `is`.

### Шаг 3. Принимаем статус из API
Из запроса приходит строка — её превращают в член перечисления **по значению**. Неизвестное значение отсекается сразу:
```python
def parse_status(raw):
    try:
        return OrderStatus(raw)
    except ValueError:
        allowed = ", ".join(s.value for s in OrderStatus)
        raise ValueError(f"неизвестный статус {raw!r}, допустимы: {allowed}") from None


print(parse_status("shipped"))
parse_status("payed")
```
Результат:
```
OrderStatus.SHIPPED
ValueError: неизвестный статус 'payed', допустимы: new, paid, shipped, cancelled
```
`from None` убирает из traceback исходную ошибку `Enum`: новое сообщение и так всё объясняет.

### Шаг 4. Переходим на StrEnum
Обычный `Enum` не равен строке и не сериализуется в JSON. Пока статусы гуляют между базой, JSON и шаблонами, это мешает. `StrEnum` устраняет оба неудобства:
```python
import json
from enum import StrEnum


print(OrderStatus.PAID == "paid")


class OrderStatus(StrEnum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


status = OrderStatus.PAID
print(status == "paid", f"статус: {status}", json.dumps({"status": status}))
```
Результат:
```
False
True статус: paid {"status": "paid"}
```

### Шаг 5. Описываем разрешённые переходы
Перечисление удобно использовать ключами словаря. Например, так записывают, из какого статуса в какой можно перейти:
```python
TRANSITIONS = {
    OrderStatus.NEW: (OrderStatus.PAID, OrderStatus.CANCELLED),
    OrderStatus.PAID: (OrderStatus.SHIPPED, OrderStatus.CANCELLED),
    OrderStatus.SHIPPED: (),
    OrderStatus.CANCELLED: (),
}


def change_status(current, new):
    if new not in TRANSITIONS[current]:
        raise ValueError(f"нельзя перейти из {current} в {new}")
    return new


print(change_status(OrderStatus.NEW, OrderStatus.PAID))
change_status(OrderStatus.SHIPPED, OrderStatus.NEW)
```
Результат:
```
paid
ValueError: нельзя перейти из shipped в new
```
Все статусы и правила видны в одном месте. Новый статус без строки в `TRANSITIONS` даст `KeyError` при первом же переходе — его не забудут.

## Частые ошибки
- **Сравнение обычного `Enum` со строкой.** `order.status == "paid"` для `Enum` всегда `False`, без ошибки. Сравнивайте с членом (`== OrderStatus.PAID`) или используйте `StrEnum`.
- **`OrderStatus["paid"]` для строки из API.** Квадратные скобки ищут по **имени** (`"PAID"`) — `KeyError: 'paid'`. Значение из API превращают круглыми скобками: `OrderStatus("paid")`.
- **`json.dumps` с обычным `Enum`.** `TypeError: Object of type OrderStatus is not JSON serializable`. Передавайте `.value` или используйте `StrEnum`.
- **Строки «на всякий случай» рядом с `Enum`.** Если в одном месте `OrderStatus.PAID`, а в другом `"paid"`, перечисление ничего не гарантирует. Строку переводят в член один раз — на входе.
- **Печать множества статусов.** Порядок элементов `set` зависит от хеша и может меняться между запусками. Для вывода — список или кортеж.

## Итог
**Перечисление**
- `class OrderStatus(Enum)` — фиксированный набор именованных значений; опечатка — `AttributeError`.
- У члена есть `name` (`PAID`) и `value` (`"paid"`); `list(OrderStatus)` — все члены по порядку.
- Каждый член — единственный объект: можно сравнивать через `is`.

**Получение из строки**
- `OrderStatus("paid")` — по значению (API, база); нет — `ValueError`.
- `OrderStatus["PAID"]` — по имени; нет — `KeyError`.

**StrEnum**
- Члены — строки: `== "paid"` истинно, f-строки и `json.dumps` дают значение.
- Обычный `Enum` строке не равен и в JSON не сериализуется.

## Вопросы на собеседовании
<details><summary>Зачем нужен `Enum`, если можно использовать строковые константы?</summary>

Перечисление собирает все допустимые значения в одном месте, ловит опечатки (`AttributeError` вместо тихой ошибки), позволяет перебрать варианты и проверить входную строку (`OrderStatus(raw)`). Константы `PAID = "paid"` не мешают передать любую другую строку.
</details>

<details><summary>Чем `OrderStatus("paid")` отличается от `OrderStatus["PAID"]`?</summary>

Круглые скобки ищут член по значению, квадратные — по имени. Значения приходят извне (API, база), имена используют в коде и иногда в конфигурации. Ошибки разные: `ValueError` и `KeyError`.
</details>

<details><summary>Почему `OrderStatus.PAID == "paid"` даёт `False` и как это исправить?</summary>

Член обычного `Enum` — отдельный объект, а не строка, и сравнение с другими типами намеренно ложно. Исправления: сравнивать с членом перечисления, использовать `.value` или наследоваться от `StrEnum`, члены которого являются строками.
</details>

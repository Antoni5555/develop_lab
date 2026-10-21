---
title: Виды методов
type: lesson
level: 2
reading_time: 8
---

## Теория
Обычный метод работает с готовым объектом: `order.total()` считает сумму **этого** заказа через `self`. Но некоторые действия нужны раньше, чем объект появится. Заказ приходит из API в виде JSON, и из словаря нужно **создать** `Order`: перевести цены в `Decimal`, подставить статус по умолчанию. Делать это в каждом месте, где приходит JSON, — дублирование. Писать отдельную функцию `order_from_dict()` вне класса — значит снова разносить код заказа по модулям. Для таких случаев есть **метод класса** (`@classmethod`). Он получает первым аргументом не объект, а сам класс (`cls`), поэтому может создавать объекты: `Order.from_dict(data)`. Такие методы называют альтернативными конструкторами.

Бывает и третий случай. Функция по смыслу относится к заказу, но не нужны ни объект, ни класс: например, проверить, что строка — допустимый статус заказа. Её оформляют **статическим методом** (`@staticmethod`). Это обычная функция, которая просто живёт в пространстве имён класса: `Order.is_valid_status("paid")`. Важная деталь: имена из тела класса (атрибуты, статические методы) **не видны** внутри методов как голые имена — только через `self.`, `cls.` или имя класса.

## Наглядно
**Таблица 1.** Три вида методов.

| | Обычный метод | `@classmethod` | `@staticmethod` |
|---|---|---|---|
| Первый параметр | `self` — объект | `cls` — класс | нет |
| Что доступно | данные объекта и класса | данные класса, создание объектов `cls(...)` | только аргументы |
| Вызов | `order.total()` | `Order.from_dict(data)` (или через объект) | `Order.is_valid_status(s)` (или через объект) |
| Типичная задача | работа с данными объекта | альтернативный конструктор: `from_dict`, `from_csv_row` | проверка или расчёт, логически связанный с классом |

## На практике
Задача: описать заказ классом `Order`. Заказ должен создаваться из словаря, который пришёл из API, и проверять статус.

### Шаг 1. Описываем заказ с обычным методом
Позиция заказа — словарь с `product_id`, `quantity` и `price`. `total()` — обычный метод: ему нужны данные конкретного заказа:
```python
import json
from decimal import Decimal


class Order:
    STATUSES = ("new", "paid", "shipped", "cancelled")

    def __init__(self, id, user_id, items, status="new"):
        self.id = id
        self.user_id = user_id
        self.items = items
        self.status = status

    def total(self):
        return sum(item["price"] * item["quantity"] for item in self.items)


order = Order(1042, 7, [{"product_id": 1, "quantity": 2, "price": Decimal("1499.00")}])
print(order.total(), order.status)
```
Результат:
```
2998.00 new
```

### Шаг 2. Добавляем альтернативный конструктор
Из API приходит JSON: цены в нём — строки, статуса может не быть. `from_dict` приводит данные к нужному виду и создаёт объект через `cls(...)`:
```python
class Order:
    STATUSES = ("new", "paid", "shipped", "cancelled")

    def __init__(self, id, user_id, items, status="new"):
        self.id = id
        self.user_id = user_id
        self.items = items
        self.status = status

    def total(self):
        return sum(item["price"] * item["quantity"] for item in self.items)

    @classmethod
    def from_dict(cls, data):
        items = [
            {"product_id": i["product_id"], "quantity": i["quantity"], "price": Decimal(i["price"])}
            for i in data["items"]
        ]
        return cls(data["id"], data["user_id"], items, data.get("status", "new"))


payload = json.loads('{"id": 1043, "user_id": 8, "items": [{"product_id": 2, "quantity": 3, "price": "490.00"}]}')
order = Order.from_dict(payload)
print(type(order).__name__, order.id, order.total(), order.status)
```
Результат:
```
Order 1043 1470.00 new
```
`cls` здесь — сам класс `Order`, поэтому `cls(...)` равносильно `Order(...)`. Почему пишут именно `cls`, станет видно в теме «Наследование»: класс-наследник, вызвавший `from_dict`, получит объект своего класса, а не `Order`.

### Шаг 3. Добавляем статический метод
Проверка статуса не использует ни объект, ни класс — только строку. Это статический метод:
```python
class Order:
    STATUSES = ("new", "paid", "shipped", "cancelled")

    def __init__(self, id, user_id, items, status="new"):
        if not self.is_valid_status(status):
            raise ValueError(f"неизвестный статус: {status}")
        self.id = id
        self.user_id = user_id
        self.items = items
        self.status = status

    @staticmethod
    def is_valid_status(status):
        return status in Order.STATUSES


print(Order.is_valid_status("paid"), Order.is_valid_status("payed"))
Order(1044, 7, [], status="payed")
```
Результат:
```
True False
ValueError: неизвестный статус: payed
```
Внутри `__init__` метод вызван через `self.`, внутри статического метода атрибут взят через `Order.`. Голые имена `is_valid_status` и `STATUSES` там не видны.

### Шаг 4. Проверяем, что голое имя из класса не видно в методе
Тело класса не становится областью видимости для своих методов — в отличие от внешней функции для вложенной:
```python
class Order:
    STATUSES = ("new", "paid", "shipped", "cancelled")

    def __init__(self, status):
        if status not in STATUSES:
            raise ValueError(status)
        self.status = status


Order("new")
```
Результат:
```
NameError: name 'STATUSES' is not defined. Did you mean: 'self.STATUSES'?
```
Python 3.12 сам подсказывает исправление. Внутри метода к атрибутам класса обращаются через `self.STATUSES`, `Order.STATUSES` или `cls.STATUSES` в методе класса.

## Частые ошибки
- **Забыли `@classmethod`.** `def from_dict(cls, data)` без декоратора — обычный метод. Вызов `Order.from_dict(payload)` кладёт `payload` в `cls`, и получается `TypeError: Order.from_dict() missing 1 required positional argument: 'data'`.
- **Голое имя атрибута или статического метода внутри метода.** `normalize(code)` или `STATUSES` без `self.`/`cls.`/имени класса дают `NameError`.
- **`Order(...)` вместо `cls(...)` в методе класса.** Работает, пока нет наследников. Наследник, вызвавший `from_dict`, получит объект базового класса.
- **Статический метод там, где нужен объект.** Если функции нужны данные заказа, это обычный метод. `@staticmethod` с параметром `order`, в который передают `self`, — признак ошибки в выборе.
- **Ссылка на чужой список в конструкторе.** `cls(data["items"])` сохраняет в объекте тот же список, что лежит в словаре. Изменения словаря снаружи меняют заказ. Если данные дальше живут своей жизнью — копируйте: `list(data["items"])`.

## Итог
**Обычный метод**
- Получает объект (`self`), работает с его данными: `order.total()`.

**Метод класса**
- `@classmethod`, первый параметр `cls` — класс.
- Альтернативный конструктор: `Order.from_dict(data)` готовит данные и возвращает `cls(...)`.
- `cls(...)`, а не `Order(...)`: наследник получит объект своего класса.

**Статический метод**
- `@staticmethod`, без `self` и `cls` — обычная функция в пространстве имён класса.
- Для проверок и расчётов, связанных с классом по смыслу: `Order.is_valid_status("paid")`.

**Имена внутри методов**
- Атрибуты класса и другие методы — только через `self.`, `cls.` или имя класса. Голое имя даёт `NameError`.

## Вопросы на собеседовании
<details><summary>Чем `@classmethod` отличается от `@staticmethod`?</summary>

Метод класса получает первым аргументом класс (`cls`) и может создавать объекты и работать с атрибутами класса. Статический метод не получает ни объект, ни класс — это обычная функция, помещённая в класс ради порядка в коде.
</details>

<details><summary>Зачем нужны альтернативные конструкторы?</summary>

Чтобы создавать объект из разных источников — словаря, строки CSV, JSON — без перегруженного `__init__` с кучей условий. Каждый источник получает свой метод класса (`from_dict`, `from_csv_row`), который готовит данные и вызывает `cls(...)`.
</details>

<details><summary>Можно ли вызвать метод класса или статический метод через объект?</summary>

Да: `order.from_dict(data)` и `order.is_valid_status("paid")` работают. Метод класса всё равно получит класс, а статический — только свои аргументы. Но читается понятнее вызов через класс.
</details>

## Глубже
Как `@classmethod` и `@staticmethod` меняют то, что получает метод при вызове, — в курсе «Python под капотом», тема «Дескрипторы».

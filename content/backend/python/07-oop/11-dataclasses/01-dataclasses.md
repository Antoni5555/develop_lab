---
title: dataclasses
type: lesson
level: 2
reading_time: 9
---

## Теория
Много классов магазина — просто данные с именами: позиция заказа, адрес доставки, строка прайс-листа. Для каждого приходится писать одно и то же. `__init__` перекладывает аргументы в `self`. `__repr__` нужен, чтобы объект был виден в логе. `__eq__` — чтобы два одинаковых объекта были равны. Это десятки строк шаблонного кода, и в них легко ошибиться: добавили поле в `__init__`, а в `__eq__` забыли. Декоратор **`@dataclass`** из модуля `dataclasses` генерирует эти методы сам. Поля описывают аннотациями типов в теле класса: `quantity: int`.

Сгенерированный `__init__` принимает поля в порядке объявления, а значения по умолчанию задаются как у параметров функции. Изменяемое значение по умолчанию (`[]`, `{}`) запрещено — вместо него `field(default_factory=list)`. Проверки и вычисляемые поля пишут в `__post_init__`: его вызывает сгенерированный `__init__`. С `frozen=True` объект нельзя изменить после создания, зато он становится хешируемым. Важно помнить: **аннотации не проверяются**. `quantity: int` не помешает передать строку `"2"` — это подсказка для людей и mypy, а не проверка.

## Наглядно
**Таблица 1.** Что `@dataclass` пишет за вас.

| Метод | Обычный класс | `@dataclass` |
|---|---|---|
| `__init__` | пишете сами | по полям, в порядке объявления |
| `__repr__` | `<OrderItem object at 0x…>` | `OrderItem(product_id=1, quantity=2, …)` |
| `__eq__` | по тождеству | по всем полям, по порядку |
| `__hash__` | по тождеству | нет — объект нехешируемый; с `frozen=True` — по полям |
| `__lt__` и другие | нет | с `order=True` — сравнение полей по порядку |

**Таблица 2.** Основные настройки и функции.

| Что | Пример | Зачем |
|---|---|---|
| Значение по умолчанию | `quantity: int = 1` | как у параметра функции |
| `field(default_factory=...)` | `tags: list = field(default_factory=list)` | свой изменяемый объект для каждого экземпляра |
| `__post_init__` | проверка, вычисляемое поле | вызывается в конце сгенерированного `__init__` |
| `frozen=True` | `@dataclass(frozen=True)` | неизменяемый и хешируемый объект |
| `asdict(obj)` | `{"product_id": 1, ...}` | словарь для JSON и логов |
| `replace(obj, поле=...)` | `replace(item, quantity=5)` | копия с изменённым полем — для `frozen` |

## На практике
Задача: описать позицию заказа `OrderItem` — товар, количество и цену на момент покупки — без шаблонного кода и с проверкой количества.

### Шаг 1. Объявляем dataclass
Поля — аннотации в теле класса. `__init__`, `__repr__` и `__eq__` появляются сами:
```python
from dataclasses import asdict, dataclass, field, replace
from decimal import Decimal


@dataclass
class OrderItem:
    product_id: int
    quantity: int
    price: Decimal


item = OrderItem(1, 2, Decimal("1499.00"))
print(item)
print(item == OrderItem(product_id=1, quantity=2, price=Decimal("1499.00")))
```
Результат:
```
OrderItem(product_id=1, quantity=2, price=Decimal('1499.00'))
True
```
Обычный класс с тем же поведением занял бы около 15 строк: `__init__` с тремя присваиваниями, `__repr__`, `__eq__` с проверкой типа.

### Шаг 2. Задаём значения по умолчанию
Поля со значением по умолчанию идут после полей без него — как параметры функции. Для списков и словарей нужен `default_factory`, иначе dataclass выдаст ошибку ещё при объявлении класса:
```python
@dataclass
class Order:
    id: int
    user_id: int
    status: str = "new"
    items: list = field(default_factory=list)


a, b = Order(1042, 7), Order(1043, 8)
a.items.append(item)
print(len(a.items), len(b.items), b)
```
Результат:
```
1 0 Order(id=1043, user_id=8, status='new', items=[])
```
`default_factory=list` вызывает `list()` для **каждого** объекта, поэтому списки у заказов разные. Если написать `items: list = []`, получится ошибка при объявлении класса: `ValueError: mutable default <class 'list'> for field items is not allowed: use default_factory`.

### Шаг 3. Проверяем данные в `__post_init__`
Аннотации ничего не проверяют — строка вместо числа проходит:
```python
print(OrderItem(1, "2", Decimal("1499.00")))
```
Результат:
```
OrderItem(product_id=1, quantity='2', price=Decimal('1499.00'))
```
Проверки пишут в `__post_init__`. Его вызывает сгенерированный `__init__`, когда поля уже заполнены. Там же удобно считать производные поля, а `field(init=False)` убирает такое поле из параметров:
```python
@dataclass
class OrderItem:
    product_id: int
    quantity: int
    price: Decimal
    total: Decimal = field(init=False)

    def __post_init__(self):
        if not isinstance(self.quantity, int) or self.quantity < 1:
            raise ValueError(f"товар {self.product_id}: неверное количество {self.quantity!r}")
        self.total = self.price * self.quantity


print(OrderItem(1, 2, Decimal("1499.00")).total)
OrderItem(1, "2", Decimal("1499.00"))
```
Результат:
```
2998.00
ValueError: товар 1: неверное количество '2'
```

### Шаг 4. Замораживаем объект
Обычный dataclass с `__eq__` нехешируем — его нельзя положить в `set`. `frozen=True` запрещает менять поля и делает объект хешируемым. Это удобно для ключей и значений, которые не должны меняться:
```python
@dataclass(frozen=True)
class PriceKey:
    product_id: int
    currency: str


prices = {PriceKey(1, "RUB"): Decimal("1499.00"), PriceKey(1, "USD"): Decimal("16.66")}
print(prices[PriceKey(1, "USD")])
key = PriceKey(1, "RUB")
print(replace(key, currency="EUR"))
key.currency = "EUR"
```
Результат:
```
16.66
PriceKey(product_id=1, currency='EUR')
dataclasses.FrozenInstanceError: cannot assign to field 'currency'
```
«Изменить» замороженный объект — значит создать копию через `replace`.

### Шаг 5. Превращаем в словарь
`asdict` собирает словарь из полей — например, для ответа API. Вложенные dataclass-объекты он тоже превращает в словари:
```python
item = OrderItem(1, 2, Decimal("1499.00"))
order = Order(1042, 7, items=[item])
print(asdict(order))
```
Результат:
```
{'id': 1042, 'user_id': 7, 'status': 'new', 'items': [{'product_id': 1, 'quantity': 2, 'price': Decimal('1499.00'), 'total': Decimal('2998.00')}]}
```
`Decimal` в `json.dumps` сам не сериализуется — его переводят в строку отдельно, как в теме «JSON».

## Частые ошибки
- **Изменяемое значение по умолчанию.** `items: list = []` — `ValueError` при объявлении класса. Нужно `field(default_factory=list)`.
- **Ожидание, что типы проверяются.** `quantity: int` пропустит `"2"` и `-5`. Проверки — в `__post_init__`.
- **Поле со значением по умолчанию перед полем без него.** `TypeError: non-default argument 'b' follows default argument` — как у параметров функции. Поля без значений объявляют первыми.
- **dataclass в `set` или ключом `dict`.** Обычный dataclass нехешируем: `TypeError: unhashable type`. Для ключей — `frozen=True`.
- **`frozen` — неглубокая заморозка.** Поле-список нельзя переприсвоить, но `obj.items.append(...)` работает. Для неизменяемых данных — кортеж.
- **dataclass с поведением.** Если у класса сложные правила изменения состояния (резерв, оплата), dataclass подходит хуже. Это инструмент для «данных с именами».

## Итог
**Объявление**
- `@dataclass` + аннотации полей — генерирует `__init__`, `__repr__`, `__eq__`.
- Поля без значения по умолчанию — первыми; списки и словари — через `field(default_factory=list)`.

**Проверки и вычисления**
- Аннотации не проверяются при создании объекта.
- `__post_init__` — проверки и производные поля; `field(init=False)` — поле не в параметрах.

**Настройки**
- `frozen=True` — нельзя менять поля, объект хешируемый; заморозка неглубокая.
- `order=True` — сравнение `<`, `>` по полям; `replace(obj, ...)` — копия с изменениями; `asdict(obj)` — словарь.

## Вопросы на собеседовании
<details><summary>Что генерирует `@dataclass`?</summary>

По умолчанию — `__init__`, `__repr__` и `__eq__` по объявленным полям. С `order=True` — методы сравнения, с `frozen=True` — запрет присваивания и `__hash__`. Поля берутся из аннотаций класса в порядке объявления.
</details>

<details><summary>Почему обычный dataclass нехешируемый?</summary>

Он определяет `__eq__` по значениям полей, а поля можно менять. Если бы хеш считался по полям, изменённый объект «потерялся» бы в словаре. Поэтому dataclass, как и любой класс со своим `__eq__`, получает `__hash__ = None`. С `frozen=True` поля менять нельзя, и хеш по ним безопасен.
</details>

<details><summary>Проверяет ли dataclass типы полей?</summary>

Нет. Аннотации нужны генератору, чтобы найти поля, а людям и mypy — как документация. Проверки во время выполнения пишут в `__post_init__` или используют библиотеки вроде pydantic.
</details>

<details><summary>Когда dataclass, а когда словарь?</summary>

Словарь — для данных с заранее неизвестными ключами или «на один раз» (разобранный JSON). dataclass — когда набор полей известен: опечатка в имени поля даёт `AttributeError` или `TypeError` сразу, редактор подсказывает поля, а к данным можно добавить методы и проверки в `__post_init__`.
</details>

## Глубже
Почему изменённый ключ «теряется» в словаре и как с этим связан `frozen=True` — в курсе «Python под капотом», тема «`__eq__` и `__hash__` в своих классах». Сколько памяти занимает миллион позиций и как помогает `__slots__` (`@dataclass(slots=True)`) — тема «Размер объектов и `__slots__`».

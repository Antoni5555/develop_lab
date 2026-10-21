---
title: Полиморфизм и утиная типизация
type: lesson
level: 2
reading_time: 9
---

## Теория
Магазин доставляет курьером, в пункт выдачи и почтой, и у каждого способа своя цена. Первое решение — функция с цепочкой `if kind == "courier": ... elif kind == "pickup": ...`. С каждым новым способом её приходится править, а таких функций со временем несколько: цена, срок, текст в письме. **Полиморфизм** — когда разные объекты отвечают на один и тот же вызов каждый по-своему. Каждый способ доставки — класс с методом `calc_price(total)`. Код оформления заказа просто вызывает `delivery.calc_price(total)` и не знает, какой способ ему передали. Новый способ — новый класс, а код оформления не меняется.

В Python для этого не нужен общий родитель. Это **утиная типизация**: «если ходит как утка и крякает как утка — это утка». Важен не тип объекта, а то, что у него есть нужный метод с нужными параметрами. Набор методов, на который рассчитывает код, называют **интерфейсом**. Если интерфейс хочется записать явно — для редактора и проверки типов (mypy), — его описывают через `typing.Protocol`. Классы при этом ни от чего не наследуют, а Python во время выполнения ничего не проверяет.

## Наглядно
**Таблица 1.** Три способа работать с разными видами доставки.

| Подход | Как выглядит | Новый способ доставки |
|---|---|---|
| Ветвление по типу | `if isinstance(d, Courier): ... elif isinstance(d, Pickup): ...` | правка каждой такой функции |
| Полиморфизм через наследование | все наследуют `Delivery`, код вызывает `d.calc_price(total)` | новый класс-наследник |
| Утиная типизация | любой объект с `calc_price(total)` | новый класс, родитель не нужен; можно взять класс из чужой библиотеки |

**Таблица 2.** Как проверить, что объект «умеет» нужное.

| Способ | Пример | Подвох |
|---|---|---|
| Просто вызвать (EAFP) | `d.calc_price(total)` | нет метода — `AttributeError`, и это нормально: ошибка видна сразу |
| `try/except AttributeError` вокруг вызова | `try: d.calc_price(t) except AttributeError: ...` | ловит и `AttributeError` **внутри** метода — баг маскируется |
| Проверить заранее (LBYL) | `hasattr(d, "calc_price")`, `getattr(d, "calc_price", None)` | проверяет только наличие, не параметры |
| `Protocol` + mypy | `def checkout(d: Delivery)` | проверка до запуска; во время выполнения ничего не делает |

## На практике
Задача: считать стоимость доставки для разных способов так, чтобы новый способ не требовал правки кода оформления заказа.

### Шаг 1. Видим проблему ветвления
Функция знает про все способы доставки поимённо:
```python
from decimal import Decimal


def delivery_price(kind, total):
    if kind == "courier":
        return Decimal("0.00") if total >= 3000 else Decimal("299.00")
    elif kind == "pickup":
        return Decimal("0.00")
    elif kind == "post":
        return Decimal("350.00")
    raise ValueError(f"неизвестный способ доставки: {kind}")


print(delivery_price("courier", Decimal("1499.00")), delivery_price("pickup", Decimal("1499.00")))
```
Результат:
```
299.00 0.00
```
Новый способ — правка этой функции, а также функций «срок доставки» и «текст в письме», в каждой своя цепочка `elif`.

### Шаг 2. Даём каждому способу свой класс с общим методом
У всех классов один метод `calc_price(total)` с одинаковыми параметрами. Поэтому функция `checkout_total` не знает ни одного класса доставки по имени:
```python
class CourierDelivery:
    def calc_price(self, total):
        return Decimal("0.00") if total >= 3000 else Decimal("299.00")


class PickupDelivery:
    def calc_price(self, total):
        return Decimal("0.00")


class PostDelivery:
    def __init__(self, tariff):
        self.tariff = tariff

    def calc_price(self, total):
        return self.tariff


def checkout_total(total, delivery):
    return total + delivery.calc_price(total)


total = Decimal("1499.00")
for delivery in (CourierDelivery(), PickupDelivery(), PostDelivery(Decimal("350.00"))):
    print(type(delivery).__name__, checkout_total(total, delivery))
```
Результат:
```
CourierDelivery 1798.00
PickupDelivery 1499.00
PostDelivery 1849.00
```
Данные, которые нужны только одному способу (тариф почты), передаются в его `__init__`, а не в `calc_price`. Так параметры метода остаются у всех одинаковыми.

### Шаг 3. Подключаем класс, который ни от кого не наследует
Партнёрская служба прислала свой класс. Он ничего не знает о наших классах, но у него есть такой же метод — и этого достаточно:
```python
class PartnerExpress:
    def __init__(self, rate_percent):
        self.rate_percent = rate_percent

    def calc_price(self, total):
        return (total * self.rate_percent / 100).quantize(Decimal("0.01"))


print(checkout_total(total, PartnerExpress(5)))
```
Результат:
```
1573.95
```
`checkout_total` не изменилась. Это и есть утиная типизация: функции важно поведение объекта, а не его класс.

### Шаг 4. Не маскируем ошибки внутри метода
Иногда объект может не поддерживать метод, и тогда нужно значение по умолчанию. Обернуть вызов в `try/except AttributeError` опасно: так ловится и опечатка **внутри** метода:
```python
class BrokenDelivery:
    def __init__(self):
        self.tariff = Decimal("500.00")

    def calc_price(self, total):
        return self.tarif


def price_or_default(delivery, total):
    try:
        return delivery.calc_price(total)
    except AttributeError:
        return Decimal("299.00")


print(price_or_default(BrokenDelivery(), total))
```
Результат:
```
299.00
```
Баг в `BrokenDelivery` не виден — клиент платит не тот тариф. Надёжнее проверить наличие метода, а вызывать его уже вне `try`:
```python
def price_or_default(delivery, total):
    calc = getattr(delivery, "calc_price", None)
    if calc is None:
        return Decimal("299.00")
    return calc(total)


print(price_or_default(object(), total))
price_or_default(BrokenDelivery(), total)
```
Результат:
```
299.00
AttributeError: 'BrokenDelivery' object has no attribute 'tarif'. Did you mean: 'tariff'?
```

### Шаг 5. Записываем интерфейс через Protocol
`Protocol` описывает, какие методы ждёт код. Классы доставки от него не наследуют:
```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class Delivery(Protocol):
    def calc_price(self, total: Decimal) -> Decimal: ...


def checkout_total(total: Decimal, delivery: Delivery) -> Decimal:
    return total + delivery.calc_price(total)


print(isinstance(PickupDelivery(), Delivery), isinstance(object(), Delivery))
```
Результат:
```
True False
```
Главная польза — подсказки редактора и проверка mypy до запуска: объект без `calc_price` подсветится как ошибка. `@runtime_checkable` разрешает `isinstance`, но тот проверяет только **имя** метода, без параметров. Для полной проверки нужен mypy.

## Частые ошибки
- **Цепочка `isinstance` вместо общего метода.** Каждый новый вид объекта требует правки всех таких цепочек. Пусть объект сам знает, как себя считать.
- **Разные параметры у «одинаковых» методов.** `PostDelivery.calc_price(self, total, region)` ломает общий вызов `d.calc_price(total)` с `TypeError` — только для почты. Особые данные передают в `__init__`.
- **`try/except AttributeError` вокруг вызова.** Перехватывает и опечатки внутри метода, и баг превращается в неверный результат. Проверяйте наличие метода через `getattr(obj, "имя", None)`, а вызывайте вне `try`.
- **Ожидание, что `Protocol` проверит что-то при запуске.** Аннотации Python не проверяет. `Protocol` работает в редакторе и mypy, а `isinstance` с `@runtime_checkable` смотрит только на имена методов.

## Итог
**Полиморфизм**
- Один вызов — разное поведение: `delivery.calc_price(total)` у каждого класса свой.
- Код, который вызывает метод, не знает конкретных классов. Новый вид — новый класс без правки старого кода.

**Утиная типизация**
- Важен не тип, а наличие метода с нужными параметрами; общий родитель не обязателен.
- Интерфейс — набор методов, на которые рассчитывает код. Параметры у всех реализаций одинаковые.

**Проверки**
- Обычно просто вызывают метод: нет метода — сразу `AttributeError`.
- Нужна альтернатива — `getattr(obj, "метод", None)`, а не `try/except AttributeError` вокруг вызова.
- `typing.Protocol` — явный интерфейс для mypy и редактора; при запуске не проверяется.

## Вопросы на собеседовании
<details><summary>Что такое полиморфизм?</summary>

Возможность работать с объектами разных классов через один интерфейс: код вызывает `obj.calc_price(total)`, а каждый класс выполняет свою реализацию. Новые классы подключаются без изменения кода, который их использует.
</details>

<details><summary>Что такое утиная типизация и чем она отличается от полиморфизма через наследование?</summary>

При утиной типизации объект подходит, если у него есть нужные методы, — родство классов не важно. При наследовании общий интерфейс задаёт базовый класс, и подходят только его наследники. Утиная типизация гибче: подходит и класс из чужой библиотеки. Наследование явно фиксирует контракт.
</details>

<details><summary>EAFP или LBYL — что принято в Python?</summary>

EAFP («проще попросить прощения») — сделать действие и обработать исключение. LBYL («смотри, прежде чем прыгать») — проверить заранее. В Python чаще EAFP, но `try` должен охватывать только то действие, ошибку которого вы ждёте. Иначе `except AttributeError` вокруг вызова метода поймает и ошибки внутри метода.
</details>

<details><summary>Зачем нужен `typing.Protocol`?</summary>

Чтобы описать интерфейс для статической проверки типов без наследования (структурная типизация): mypy и редактор проверяют, что переданный объект имеет нужные методы с нужными параметрами. Во время выполнения Python протоколы не проверяет; `@runtime_checkable` добавляет только поверхностную проверку имён в `isinstance`.
</details>

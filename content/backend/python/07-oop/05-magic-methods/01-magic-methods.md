---
title: Магические методы
type: lesson
level: 2
reading_time: 10
---

## Теория
Свой класс поначалу ведёт себя хуже встроенных типов. `print(product)` выводит что-то вроде `<__main__.Product object at 0x7f…>` — в логе это бесполезно. Два объекта одного товара не равны, `len(cart)` падает, по корзине нельзя пройти `for`. Встроенные функции и операторы Python работают через **магические методы** — методы с двойным подчёркиванием с обеих сторон (их ещё называют dunder-методами). `len(x)` вызывает `x.__len__()`, `a + b` — `a.__add__(b)`, `a == b` — `a.__eq__(b)`, `for` — `x.__iter__()`. Определив эти методы в своём классе, вы получаете привычный синтаксис: `len(cart)`, `for item in cart`, `guest_cart + user_cart`.

Сами магические методы не вызывают — их вызывает Python. Нужно знать, какой оператор какой метод запускает, и помнить о побочных эффектах. Свой `__eq__` делает объекты **нехешируемыми**, если не задать `__hash__`: их нельзя положить в `set` и использовать как ключи `dict`. `__len__` влияет на истинность: пустая корзина становится ложной в `if cart:`. Если метод не умеет работать с объектом другого типа, он возвращает специальное значение `NotImplemented`: тогда Python пробует другой вариант или выбрасывает понятную `TypeError`.

## Наглядно
**Таблица 1.** Какой код вызывает какой магический метод.

| Код | Метод | Для чего в магазине |
|---|---|---|
| `repr(p)`, вывод списка объектов, отладчик | `__repr__` | однозначный вид для логов: `Product(id=1, name='Мышь')` |
| `str(p)`, `print(p)`, f-строка | `__str__` (если нет — `__repr__`) | текст для пользователя: `Мышь — 1499.00 ₽` |
| `a == b`, `x in список` | `__eq__` | один товар, загруженный дважды, равен себе |
| `hash(p)`, `set`, ключ `dict` | `__hash__` | уникальные товары, словарь «товар → остаток» |
| `len(cart)` | `__len__` | сколько позиций в корзине |
| `bool(cart)`, `if cart:` | `__bool__`, иначе `__len__` | пустая корзина — ложь |
| `for item in cart`, `list(cart)` | `__iter__` | перебор позиций |
| `a + b` | `__add__`, иначе `b.__radd__(a)` | слить корзину гостя с корзиной покупателя |
| `a < b`, `sorted(...)` | `__lt__` | сортировка без `key=` |

## На практике
Задача: научить товар понятно выводиться и сравниваться, а корзину — вести себя как коллекция: `len`, `for` и слияние корзин после входа покупателя.

### Шаг 1. Добавляем `__repr__` и `__str__`
`__repr__` — для разработчика: по нему видно, что это за объект. `__str__` — для покупателя:
```python
from decimal import Decimal


class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name!r}, price={self.price!r})"

    def __str__(self):
        return f"{self.name} — {self.price} ₽"


mouse = Product(1, "Мышь", Decimal("1499.00"))
print(mouse)
print(repr(mouse))
print([mouse])
```
Результат:
```
Мышь — 1499.00 ₽
Product(id=1, name='Мышь', price=Decimal('1499.00'))
[Product(id=1, name='Мышь', price=Decimal('1499.00'))]
```
Список при выводе показывает элементы через `__repr__`. Поэтому `__repr__` нужен почти всегда, а `__str__` — когда объект показывают людям. `!r` в f-строке подставляет `repr` значения — строки получают кавычки.

### Шаг 2. Сравниваем товары по `id` и делаем их хешируемыми
Два объекта одного товара должны быть равны. Чужой тип — `NotImplemented`, а не `False`: так Python сам решит, что делать дальше. Вместе с `__eq__` задаём `__hash__` по тому же полю:
```python
class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

    def __repr__(self):
        return f"Product(id={self.id}, name={self.name!r})"

    def __eq__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


a = Product(1, "Мышь", Decimal("1499.00"))
b = Product(1, "Мышь", Decimal("1299.00"))
print(a == b, a == 1, len({a, b}))
```
Результат:
```
True False 1
```
Правило: **равные объекты обязаны иметь равные хеши**. Поэтому хеш считают по тем же полям, что и равенство. Если задать `__eq__` без `__hash__`, Python выключит хеширование, и `{a, b}` упадёт с `TypeError: unhashable type: 'Product'`.

### Шаг 3. Делаем корзину коллекцией
`__len__` отвечает на `len()`, `__iter__` — на `for`. Самый простой `__iter__` — генератор: каждый `for` получает новый итератор:
```python
class Cart:
    def __init__(self, user_id):
        self.user_id = user_id
        self._items = {}

    def add(self, product, quantity=1):
        self._items[product] = self._items.get(product, 0) + quantity

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for product, quantity in self._items.items():
            yield product, quantity

    def __repr__(self):
        return f"Cart(user_id={self.user_id}, items={len(self)})"


cart = Cart(user_id=7)
cart.add(a, 2)
cart.add(b)
cart.add(Product(2, "Коврик", Decimal("490.00")))
print(len(cart), cart)
for product, quantity in cart:
    print(product.name, quantity)
print(bool(cart), bool(Cart(user_id=8)))
```
Результат:
```
2 Cart(user_id=7, items=2)
Мышь 3
Коврик 1
True False
```
Товар `b` попал в ту же позицию, что и `a`, — это работают `__eq__` и `__hash__` из шага 2. А пустая корзина ложна: без `__bool__` Python берёт истинность из `__len__`.

### Шаг 4. Сливаем корзины оператором `+`
После входа корзину гостя сливают с корзиной покупателя. `__add__` возвращает **новую** корзину и не меняет исходные. Класс тот же, что в шаге 3, плюс `__add__`:
```python
class Cart:
    def __init__(self, user_id):
        self.user_id = user_id
        self._items = {}

    def add(self, product, quantity=1):
        self._items[product] = self._items.get(product, 0) + quantity

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        for product, quantity in self._items.items():
            yield product, quantity

    def __repr__(self):
        return f"Cart(user_id={self.user_id}, items={len(self)})"

    def __add__(self, other):
        if not isinstance(other, Cart):
            return NotImplemented
        merged = Cart(self.user_id)
        for cart in (self, other):
            for product, quantity in cart:
                merged.add(product, quantity)
        return merged


user_cart = Cart(user_id=7)
user_cart.add(a, 3)
guest_cart = Cart(user_id=None)
guest_cart.add(Product(2, "Коврик", Decimal("490.00")), 2)
merged = user_cart + guest_cart
print(merged, list(merged))
user_cart + 5
```
Результат:
```
Cart(user_id=7, items=2) [(Product(id=1, name='Мышь'), 3), (Product(id=2, name='Коврик'), 2)]
TypeError: unsupported operand type(s) for +: 'Cart' and 'int'
```
`NotImplemented` превратился в понятную `TypeError`. Если бы метод вернул `False` или `None`, ошибка всплыла бы позже и в другом месте.

### Шаг 5. Пишем класс-итератор
Иногда нужен сам итератор, а не коллекция. Например, выдача номеров заказов по одному. Итератору нужны два метода: `__next__` выдаёт следующий элемент или выбрасывает `StopIteration`, а `__iter__` возвращает сам объект:
```python
class OrderNumbers:
    def __init__(self, start, count):
        self.current = start
        self.end = start + count

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        number = self.current
        self.current += 1
        return number


numbers = OrderNumbers(1042, 3)
print(list(numbers))
print(list(numbers))
```
Результат:
```
[1042, 1043, 1044]
[]
```
Как и любой итератор, он одноразовый: позиция хранится в самом объекте. Поэтому коллекция (корзина, каталог) **не должна** быть собственным итератором. Её `__iter__` каждый раз возвращает новый итератор — генератор, как в шаге 3, или `iter(self._items)`.

## Частые ошибки
- **`__eq__` без `__hash__`.** Класс становится нехешируемым: `TypeError: unhashable type` при добавлении в `set` или в ключ `dict`. Задайте `__hash__` по тем же полям, что и `__eq__`.
- **`__len__` и проверка `if not cart`.** Пустая корзина ложна, и `if not cart:` срабатывает не только для `None`. Отсутствие объекта проверяют через `is None`.
- **Коллекция — собственный итератор.** `__iter__` возвращает `self`, а позиция хранится в объекте — второй `for` по корзине ничего не выводит. `__iter__` коллекции должен каждый раз создавать новый итератор.
- **`return False` вместо `NotImplemented`.** Для `==` разница небольшая. А `__add__`, вернувший `None`, даёт `None` вместо ошибки, и падение случается далеко от причины.
- **`sum()` по своим объектам.** `sum` начинает с `0`, и первым выполняется `0 + объект`. Без `__radd__` это `TypeError`. Нужно передать начальное значение: `sum(carts, Cart(...))`.
- **`__repr__` с непредсказуемыми данными.** Адреса объектов и время в `__repr__` мешают сравнивать логи. Выводите поля, которые однозначно определяют объект.

## Итог
**Строковое представление**
- `__repr__` — для разработчика и логов, в идеале выглядит как код создания объекта.
- `__str__` — для людей; без него `print` использует `__repr__`.

**Сравнение и хеш**
- `__eq__` задаёт `==`; чужой тип — `return NotImplemented`.
- Равные объекты — равные хеши: `__hash__` по тем же полям.
- `__eq__` без `__hash__` — объект нельзя положить в `set` или в ключ `dict`.

**Коллекции**
- `__len__` — `len()` и истинность: пустой объект ложен.
- `__iter__` — `for`; у коллекции — генератор (`yield`), каждый раз новый.
- Класс-итератор: `__iter__` возвращает `self`, `__next__` выдаёт элемент или `StopIteration`. Одноразовый.

**Операторы**
- `__add__`, `__lt__` и другие задают `+`, `<`; возвращают новый объект, исходные не меняют.

## Вопросы на собеседовании
<details><summary>Чем `__str__` отличается от `__repr__`?</summary>

`__repr__` — однозначное представление для разработчика: используется в `repr()`, отладчике, при выводе контейнеров. В идеале по нему можно воссоздать объект. `__str__` — читаемый вид для пользователя (`print`, `str()`). Если `__str__` нет, используется `__repr__`, а наоборот — нет.
</details>

<details><summary>Как связаны `__eq__` и `__hash__`?</summary>

Если `a == b`, то обязательно `hash(a) == hash(b)` — иначе `dict` и `set` не найдут равный объект. Поэтому, определив `__eq__`, Python ставит `__hash__ = None`, и класс становится нехешируемым, пока вы не зададите `__hash__` по тем же полям. Поля, от которых зависит хеш, не должны меняться, пока объект лежит в `set` или в ключе `dict`.
</details>

<details><summary>Зачем возвращать `NotImplemented`?</summary>

Это сигнал «я не умею работать с этим типом». Тогда Python пробует обратную операцию у второго объекта (`__radd__`, отражённое сравнение). Если и она не поддерживается — выбрасывает `TypeError`, а для `==` сравнивает по тождеству. Возврат `False` или `None` скрыл бы ошибку.
</details>

<details><summary>Чем итерируемый объект отличается от итератора на уровне методов?</summary>

У итерируемого объекта есть `__iter__`, который возвращает новый итератор. У итератора есть `__next__` и `__iter__`, возвращающий его самого. Поэтому коллекцию можно перебирать сколько угодно раз, а итератор — один.
</details>

## Глубже
Почему `__eq__` выключает хеширование и как изменённый объект «теряется» в словаре — в курсе «Python под капотом», тема «`__eq__` и `__hash__` в своих классах». Какие ещё протоколы есть (`__contains__`, `__getitem__`, `__bool__`) — тема «Протоколы и модель данных».

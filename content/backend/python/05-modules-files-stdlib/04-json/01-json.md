---
title: JSON
type: lesson
level: 2
reading_time: 8
---

## Теория
JSON — текстовый формат обмена данными, на котором говорит почти весь веб: тело запроса к API, ответ сервера, настройки, сообщения в очередях. Он похож на запись словарей и списков Python, но это **строка**: прежде чем работать с данными, её нужно разобрать в объекты Python (`json.loads`), а прежде чем отправить — превратить объекты обратно в строку (`json.dumps`). Этот перевод называют десериализацией и сериализацией.

Перевод не всегда взаимно однозначен, и на этом ошибаются. В JSON нет кортежей, множеств, `Decimal` и дат: кортеж становится списком, а `Decimal`, `set` и `datetime` по умолчанию вообще не сериализуются — `TypeError`. **Ключи объекта в JSON — всегда строки**: словарь `{42: "Мышь"}` после пути «туда и обратно» вернётся как `{"42": "Мышь"}`. И разбор чужого текста может упасть: клиент прислал не JSON — `json.JSONDecodeError` (это подвид `ValueError`), и сервер должен ответить `400`, а не упасть.

## Наглядно
**Таблица 1.** Как типы Python превращаются в JSON и обратно.

| Python → | JSON | → Python после `loads` |
|---|---|---|
| `dict` | объект `{...}` | `dict`, **ключи — строки** |
| `list`, `tuple` | массив `[...]` | `list` (кортеж не восстановится) |
| `str` | строка `"..."` | `str` |
| `int`, `float` | число | `int`, `float` |
| `True`, `False`, `None` | `true`, `false`, `null` | `True`, `False`, `None` |
| `Decimal`, `datetime`, `set` | — | `TypeError` при `dumps`; нужен `default=` или ручное преобразование |

**Таблица 2.** Функции и параметры модуля `json`.

| Запись | Что делает |
|---|---|
| `json.dumps(obj)` | объект Python → строка JSON |
| `json.loads(text)` | строка JSON → объект Python |
| `ensure_ascii=False` | кириллица как есть, а не `\u041c…` |
| `indent=2` | красивый многострочный вывод |
| `default=str` | функция для типов, которые JSON не знает (`Decimal`, даты) |
| `json.dump(obj, f)`, `json.load(f)` | то же для файлов (тема «Файлы и with») |

## На практике
Задача: принять заказ из тела запроса API, вернуть ответ с ценами и не уронить сервер на кривом запросе.

### Шаг 1. Превращаем словарь в JSON
`dumps` возвращает строку. По умолчанию не-ASCII символы экранируются:
```python
import json

order = {"id": 1042, "status": "paid", "items": [{"name": "Мышь", "qty": 2}]}
text = json.dumps(order)
print(type(text))
print(text)
```
Результат:
```
<class 'str'>
{"id": 1042, "status": "paid", "items": [{"name": "\u041c\u044b\u0448\u044c", "qty": 2}]}
```

### Шаг 2. Делаем вывод читаемым
Для логов и отладки — кириллица как есть и отступы:
```python
print(json.dumps(order, ensure_ascii=False, indent=2))
```
Результат:
```
{
  "id": 1042,
  "status": "paid",
  "items": [
    {
      "name": "Мышь",
      "qty": 2
    }
  ]
}
```

### Шаг 3. Разбираем тело запроса
Клиент прислал JSON-строку — `loads` превращает её в словарь:
```python
body = '{"product_id": 42, "qty": 2, "gift": false, "comment": null}'
data = json.loads(body)
print(data)
print(data["qty"] * 1499, data["gift"], data["comment"] is None)
```
Результат:
```
{'product_id': 42, 'qty': 2, 'gift': False, 'comment': None}
2998 False True
```

### Шаг 4. Видим, что ключи стали строками
Остатки на складе сохранили в JSON и прочитали обратно:
```python
stock = {42: 12, 7: 0}
restored = json.loads(json.dumps(stock))
print(restored)
print(restored.get(42), restored.get("42"))
```
Результат:
```
{'42': 12, '7': 0}
None 12
```
Поиск по числовому `id` перестал работать. Ключи приводят обратно явно: `{int(k): v for k, v in restored.items()}`.

### Шаг 5. Сериализуем Decimal
Цены в магазине — `Decimal`, а JSON его не знает:
```python
from decimal import Decimal

response = {"product_id": 42, "price": Decimal("1499.90")}
print(json.dumps(response, default=str))
json.dumps(response)
```
Результат:
```
{"product_id": 42, "price": "1499.90"}
TypeError: Object of type Decimal is not JSON serializable
```
`default=str` превращает незнакомые типы в строку — цена в API приходит строкой `"1499.90"` и не теряет копейки, как потеряла бы при переводе во `float`.

### Шаг 6. Обрабатываем невалидный JSON
Клиент прислал тело с одинарными кавычками — это не JSON. Ошибку разбора ловим и отвечаем `400`:
```python
def handle(body):
    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        return {"status": 400, "error": f"тело запроса — не JSON: {e}"}
    return {"status": 200, "qty": data["qty"]}

print(handle('{"qty": 2}'))
print(handle("{'qty': 2}"))
```
Результат:
```
{'status': 200, 'qty': 2}
{'status': 400, 'error': 'тело запроса — не JSON: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)'}
```
`JSONDecodeError` — подкласс `ValueError`, поэтому `except ValueError` тоже его поймает.

## Частые ошибки
- **Числовые ключи после JSON.** Ключи объектов — всегда строки: `{42: ...}` возвращается как `{"42": ...}`. Приводите ключи обратно или храните id в значениях.
- **`Decimal` и даты в `dumps`.** `TypeError: Object of type ... is not JSON serializable`. Используйте `default=str` или преобразуйте заранее; деньги — строкой, не `float`.
- **Неперехваченная ошибка разбора.** Тело запроса — чужие данные: `json.loads` может упасть, ответ — `400`, а не `500`.
- **Одинарные кавычки и `True`.** `{'a': True}` — запись Python, не JSON. В JSON только двойные кавычки и `true/false/null`.
- **Кортежи и множества.** Кортеж вернётся списком, множество не сериализуется вовсе.

## Итог
**Перевод**
- `json.dumps(obj)` → строка; `json.loads(text)` → объекты Python.
- `ensure_ascii=False` — кириллица как есть; `indent=2` — читаемый вывод.

**Что меняется по пути**
- Ключи объектов — всегда строки.
- Кортеж → список; `True/False/None` ↔ `true/false/null`.
- `Decimal`, `datetime`, `set` — не сериализуются: `default=str` или своё преобразование.

**Чужие данные**
- `json.loads` бросает `json.JSONDecodeError` (подкласс `ValueError`) — ловим и отвечаем `400`.

## Вопросы на собеседовании
<details><summary>Чем `json.dumps` отличается от `json.dump`?</summary>

`dumps` возвращает строку (s — string), `dump` записывает JSON в открытый файл. Аналогично `loads` разбирает строку, `load` читает из файла.
</details>

<details><summary>Почему после `json.loads(json.dumps({1: "a"}))` ключ стал строкой?</summary>

В JSON ключи объекта могут быть только строками. `dumps` превращает ключ `1` в `"1"`, а `loads` не знает, что когда-то это было число, и оставляет строку.
</details>

<details><summary>Как передать в JSON `Decimal` без потери точности?</summary>

Строкой: `json.dumps(data, default=str)` или явным `str(price)`. Перевод во `float` может исказить копейки. На стороне клиента строку снова разбирают в десятичный тип.
</details>

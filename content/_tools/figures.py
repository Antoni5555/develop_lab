"""Все SVG-рисунки уроков. Запуск: python3 content/_tools/figures.py — пересоздаёт файлы."""
from pathlib import Path

from svgkit import Figure

ROOT = Path(__file__).resolve().parents[1] / "backend"
PY1 = ROOT / "python" / "01-first-steps"
INT3 = ROOT / "python-internals" / "03-collections-internals"


def out(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


# ---------- Python 1.01: устройство traceback ----------
def traceback_anatomy():
    f = Figure(880, 276, "Устройство сообщения об ошибке: читаем снизу вверх")
    f.raw('<rect x="20" y="20" width="560" height="176" rx="14" class="fig-term"/>')
    rows = [
        ('Traceback (most recent call last):', "tt"),
        ('  File "main.py", line 2, in <module>', "tt"),
        ('    prnt("Заказ №1042 принят")', "tt"),
        ("    ^^^^", "tterr"),
        ("NameError: name 'prnt' is not defined.", "tterr"),
        ("Did you mean: 'print'?", "tterr"),
    ]
    for i, (s, cls) in enumerate(rows):
        f.text(40, 52 + i * 26, s, cls)
    notes = [  # (y строки, номер, подпись)
        (166, "1", "тип ошибки и сообщение — читаем первым"),
        (117, "2", "строка кода и место ошибки в ней"),
        (78, "3", "файл и номер строки"),
        (52, "4", "заголовок: дальше идёт отчёт об ошибке"),
    ]
    for y, n, s in notes:
        f.line(f"M584 {y - 5}H620", "lnd")
        f.raw(f'<circle cx="634" cy="{y - 5}" r="11" class="fig-acc"/>')
        f.text(634, y, n, "onacc", "middle")
        f.text(652, y, s, "s")
    f.arrow("M870 180V40")
    f.text(20, 231, "Читаем снизу вверх: сначала что случилось, потом где.", "t")
    f.text(20, 254, "Python показывает подсказку «Did you mean», если похожее имя существует.", "s")
    f.save(out(PY1 / "01-first-program" / "img" / "traceback-anatomy.svg"))


# ---------- Python 1.02: имена и значения ----------
def names_to_values():
    f = Figure(640, 310, "Имена переменных указывают на значения, у каждого значения свой тип")
    f.text(20, 20, "имя", "h"); f.text(260, 20, "значение", "h"); f.text(520, 20, "тип значения", "h")
    rows = [("name", '"Беспроводная мышь"', "str"), ("price", "1499", "int"), ("rating", "4.7", "float"),
            ("is_active", "True", "bool"), ("discount", "None", "NoneType")]
    for i, (n, val, t) in enumerate(rows):
        y = 36 + i * 54
        f.box(20, y, 150, 38, n, "box", "c", rx=19)
        f.arrow(f"M174 {y + 19}H254")
        f.raw(f'<rect x="260" y="{y}" width="240" height="38" rx="10" class="fig-box2"/>')
        f.text(276, y + 24, val, "c")
        f.raw(f'<rect x="520" y="{y + 5}" width="100" height="28" rx="14" class="fig-acc"/>')
        f.text(570, y + 24, t, "onacc", "middle")
    f.save(out(PY1 / "02-variables-and-types" / "img" / "names-to-values.svg"))


# ---------- Python 1.04: индексы и срез строки ----------
def string_indices():
    f = Figure(620, 250, "Индексы символов строки: положительные слева, отрицательные справа; срез не включает конец")
    sku = "KB-0142"
    x0, w = 60, 70
    f.text(20, 72, "индекс", "s"); f.text(20, 172, "с конца", "s")
    for i, ch in enumerate(sku):
        x = x0 + i * w
        cls = "acc" if 3 <= i <= 6 else "box2"
        f.raw(f'<rect x="{x}" y="90" width="{w - 6}" height="56" rx="10" class="fig-{cls}"/>')
        f.text(x + (w - 6) / 2, 125, ch, "onacc" if cls == "acc" else "c", "middle")
        f.text(x + (w - 6) / 2, 76, str(i), "cs", "middle")
        f.text(x + (w - 6) / 2, 172, str(i - len(sku)), "cs", "middle")
    f.text(20, 30, 'sku = "KB-0142"', "c")
    f.text(20, 214, 'sku[3:7] → "0142"  (символы 3, 4, 5, 6 — индекс 7 не входит)', "c")
    f.text(20, 238, "sku[0] → \"K\"   sku[-1] → \"2\"   sku[:2] → \"KB\"", "cs")
    f.save(out(PY1 / "04-strings" / "img" / "string-indices.svg"))


# ---------- Python 1.07: цепочка if/elif/else ----------
def delivery_elif():
    f = Figure(760, 470, "Цепочка if/elif/else: проверки идут сверху вниз, срабатывает первая истинная")
    f.box(250, 20, 260, 44, "сумма заказа: total", "box")
    f.arrow("M380 64V96")
    f.diamond(380, 140, 260, 84, "total >= 3000 ?")
    f.box(580, 118, 160, 44, "delivery = 0", "ok", "c")
    f.arrow("M510 140H576"); f.text(526, 132, "да", "s")
    f.arrow("M380 182V222"); f.text(390, 206, "нет", "s")
    f.diamond(380, 266, 260, 84, "total >= 1000 ?")
    f.box(580, 244, 160, 44, "delivery = 199", "ok", "c")
    f.arrow("M510 266H576"); f.text(526, 258, "да", "s")
    f.arrow("M380 308V348"); f.text(390, 332, "нет (else)", "s")
    f.box(300, 352, 160, 44, "delivery = 399", "ok", "c")
    f.box(250, 420, 260, 40, "дальше по программе", "box2")
    f.arrow("M380 396V416")
    f.arrow("M660 162V200H740V440H514")
    f.line("M660 288V300H740")
    f.text(20, 140, "if", "c"); f.text(20, 266, "elif", "c"); f.text(20, 376, "else", "c")
    f.save(out(PY1 / "07-conditions" / "img" / "delivery-elif.svg"))


# ---------- Python 1.08: цикл while ----------
def while_loop():
    f = Figure(720, 400, "Цикл while: условие проверяется перед каждым повтором; break выходит из цикла сразу")
    f.box(240, 20, 240, 44, "stock = 3", "box", "c")
    f.arrow("M360 64V96")
    f.diamond(360, 140, 240, 84, "stock > 0 ?")
    f.box(240, 230, 240, 64, "тело цикла:|stock -= 1", "box2", "c")
    f.arrow("M360 182V226"); f.text(370, 210, "да", "s")
    f.arrow("M240 262H120V140H236"); f.text(130, 196, "повтор:", "s"); f.text(130, 214, "проверить", "s"); f.text(130, 232, "условие снова", "s")
    f.box(540, 118, 160, 44, "после цикла", "ok")
    f.arrow("M480 140H536"); f.text(496, 132, "нет", "s")
    f.arrow("M480 270H620V166", "lnd"); f.text(500, 290, "break — выход сразу", "s")
    f.text(20, 340, "Если в теле ничего не меняет stock, условие всегда истинно — цикл бесконечный.", "t")
    f.text(20, 364, "continue — сразу к проверке условия, пропуская остаток тела.", "s")
    f.save(out(PY1 / "08-while-loop" / "img" / "while-loop.svg"))


# ---------- Под капотом 3.03: поиск ключа в dict ----------
def dict_lookup():
    f = Figure(900, 420, "Как dict ищет ключ: хеш, ячейка, сравнение через ==")
    f.box(20, 20, 180, 46, 'ключ: (42, "M")', "box", "c")
    f.box(250, 20, 170, 46, "hash(ключ)", "box", "c")
    f.box(470, 20, 170, 46, "номер ячейки")
    f.arrow("M200 43H246"); f.arrow("M420 43H466"); f.arrow("M555 66V106")
    f.diamond(555, 150, 240, 84, "В ячейке что-то есть?")
    f.box(710, 128, 170, 44, "KeyError", "err", "errt")
    f.arrow("M675 150H706"); f.text(680, 142, "нет", "s")
    f.arrow("M555 192V234"); f.text(565, 218, "да", "s")
    f.diamond(555, 278, 260, 84, "Лежащий ключ == искомый?")
    f.box(450, 350, 210, 46, "значение найдено", "ok")
    f.arrow("M555 320V346"); f.text(565, 338, "да", "s")
    f.box(60, 256, 250, 44, "следующая ячейка (коллизия)", "box")
    f.arrow("M425 278H314"); f.text(380, 270, "нет", "s")
    f.arrow("M185 256V150H431"); f.text(195, 140, "проверяем её так же", "s")
    f.save(out(INT3 / "03-hashable-and-immutability" / "img" / "dict-lookup.svg"))


# ---------- Под капотом 3.03: потерянный ключ ----------
def lost_key():
    f = Figure(760, 300, "Ключ изменили после вставки: поиск по старому и новому хешу не находит запись")
    for i in range(8):
        x = 40 + i * 85
        f.text(x + 40, 124, str(i), "s", "middle")
        if i == 1:
            f.raw(f'<rect x="{x}" y="132" width="80" height="64" rx="10" class="fig-err"/>')
            f.text(x + 40, 158, "SKU(1002)", "cs", "middle"); f.text(x + 40, 180, "→ 12", "cs", "middle")
        else:
            f.raw(f'<rect x="{x}" y="132" width="80" height="64" rx="10" class="fig-{"dash" if i == 2 else "box2"}"/>')
    f.text(420, 222, "ячейки таблицы dict из 8 мест", "h")
    f.text(40, 26, "SKU(1001) in stock", "c")
    f.text(40, 48, "hash(1001) % 8 = 1 → ячейка 1: ячейка та, но в ней уже ключ 1002", "s")
    f.arrow("M165 58V128"); f.text(177, 96, "== даёт False → не найден", "errt")
    f.arrow("M250 248V200")
    f.text(220, 268, "key in stock", "c")
    f.text(220, 290, "hash(1002) % 8 = 2 → ячейка 2: она пуста → не найден", "s")
    f.save(out(INT3 / "03-hashable-and-immutability" / "img" / "lost-key.svg"))


PY2 = ROOT / "python" / "02-collections"


# ---------- Python 2.04: операции над множествами ----------
def sets_venn():
    f = Figure(760, 390, "Операции над множествами на примере покупателей мыши и клавиатуры")
    f.raw('<circle cx="300" cy="150" r="115" class="fig-m1 fig-venn"/>')
    f.raw('<circle cx="460" cy="150" r="115" class="fig-m2 fig-venn"/>')
    f.text(300, 24, "mouse = {1, 2, 3, 5}", "c", "middle")
    f.text(460, 290, "keyboard = {2, 3, 8}", "c", "middle")
    f.text(250, 156, "1, 5", "c", "middle"); f.text(250, 176, "только мышь", "s", "middle")
    f.text(380, 156, "2, 3", "c", "middle"); f.text(380, 176, "оба товара", "s", "middle")
    f.text(515, 156, "8", "c", "middle"); f.text(515, 176, "только клавиатура", "s", "middle")
    rows = [("mouse & keyboard", "{2, 3}", "пересечение: купили оба"),
            ("mouse | keyboard", "{1, 2, 3, 5, 8}", "объединение: купили хоть что-то"),
            ("mouse - keyboard", "{1, 5}", "разность: мышь, но не клавиатуру"),
            ("mouse ^ keyboard", "{1, 5, 8}", "ровно один из двух товаров")]
    for i, (expr, res, note) in enumerate(rows):
        y = 320 + i * 20
        f.text(40, y, expr, "cs"); f.text(220, y, "→ " + res, "cs"); f.text(400, y, note, "s")
    f.save(out(PY2 / "04-sets" / "img" / "sets-venn.svg"))


# ---------- Python 2.05: вложенный заказ ----------
def nested_order():
    f = Figure(860, 380, "Структура заказа: словарь со вложенным словарём и списком словарей")
    f.text(20, 24, 'order["items"][0]["price"]  →  1499', "c")
    f.box(20, 40, 820, 320, "", "box")
    f.text(36, 64, "order — dict", "h")
    f.text(40, 98, '"id": 1042', "c"); f.text(40, 126, '"status": "paid"', "c")
    f.text(40, 172, '"customer":', "c"); f.arrow("M150 167H216")
    f.box(220, 146, 300, 46, "", "box2"); f.text(236, 174, '{"name": "Анна", "city": None}', "cs")
    f.text(526, 160, "dict", "h")
    f.text(40, 236, '"items":', "c"); f.arrow("M122 231H216")
    f.box(220, 208, 610, 140, "", "box2"); f.text(236, 228, "list", "h")
    for k, (name, price, qty) in enumerate([("Мышь", "1499", "2"), ("Коврик", "490", "1")]):
        x = 236 + k * 296
        f.text(x, 252, f"[{k}] — dict", "s")
        f.box(x, 258, 280, 80, "", "box")
        if k == 0:
            f.raw(f'<rect x="{x + 8}" y="{258 + 30}" width="130" height="22" rx="6" class="fig-acc"/>')
        f.text(x + 14, 280, f'"name": "{name}"', "cs")
        f.text(x + 14, 304, f'"price": {price}', "onacc" if k == 0 else "cs")
        f.text(x + 14, 328, f'"qty": {qty}', "cs")
    f.save(out(PY2 / "05-nested-structures" / "img" / "nested-order.svg"))


# ---------- Python 2.06: присваивание, copy, deepcopy ----------
def copy_modes():
    f = Figure(900, 290, "Присваивание, поверхностная и глубокая копия списка со вложенным словарём")
    panels = [("b = a", "одно и то же: изменения|видны через оба имени"),
              ("b = a.copy()", "внешний список новый,|а вложенный словарь общий"),
              ("b = copy.deepcopy(a)", "полностью независимая|копия")]
    for p, (title, note) in enumerate(panels):
        x0 = 10 + p * 300
        f.text(x0 + 10, 24, title, "c")
        f.box(x0 + 10, 60, 46, 32, "a", "box", "c", rx=16)
        f.box(x0 + 10, 150, 46, 32, "b", "box", "c", rx=16)
        if p == 0:
            f.box(x0 + 100, 100, 70, 40, "[ • ]", "box2", "c")
            f.arrow(f"M{x0 + 56} 76L{x0 + 98} 112"); f.arrow(f"M{x0 + 56} 166L{x0 + 98} 128")
            f.box(x0 + 200, 100, 80, 40, "qty: 2", "box", "cs")
            f.arrow(f"M{x0 + 170} 120H{x0 + 196}")
        elif p == 1:
            f.box(x0 + 100, 56, 70, 40, "[ • ]", "box2", "c"); f.box(x0 + 100, 146, 70, 40, "[ • ]", "box2", "c")
            f.arrow(f"M{x0 + 56} 76H{x0 + 96}"); f.arrow(f"M{x0 + 56} 166H{x0 + 96}")
            f.box(x0 + 200, 100, 80, 40, "qty: 2", "err", "cs")
            f.arrow(f"M{x0 + 170} 76L{x0 + 198} 108"); f.arrow(f"M{x0 + 170} 166L{x0 + 198} 132")
        else:
            for y in (56, 146):
                f.box(x0 + 100, y, 70, 40, "[ • ]", "box2", "c")
                f.box(x0 + 200, y, 80, 40, "qty: 2", "ok", "cs")
                f.arrow(f"M{x0 + 170} {y + 20}H{x0 + 196}")
            f.arrow(f"M{x0 + 56} 76H{x0 + 96}"); f.arrow(f"M{x0 + 56} 166H{x0 + 96}")
        for k, line in enumerate(note.split("|")):
            f.text(x0 + 10, 230 + k * 18, line, "s")
    f.save(out(PY2 / "06-mutability" / "img" / "copy-modes.svg"))


# ---------- Python 2.07: устройство comprehension ----------
def comprehension_anatomy():
    f = Figure(760, 300, "Части list comprehension и соответствующие строки обычного цикла")
    cw = 8.4  # ширина символа JetBrains Mono 14px

    def seg(x0, y, col, n, cls, num=None):
        f.raw(f'<rect x="{x0 + col * cw - 2}" y="{y - 17}" width="{n * cw + 4}" height="24" rx="5" class="fig-{cls}"/>')
        if num:
            f.raw(f'<circle cx="{x0 + col * cw + n * cw / 2}" cy="{y - 30}" r="10" class="fig-{cls} fig-venn"/>')
            f.text(x0 + col * cw + n * cw / 2, y - 26, num, "cs", "middle")

    x0, y = 30, 64
    seg(x0, y, 1, 12, "acc", "1"); seg(x0, y, 14, 20, "m1", "2"); seg(x0, y, 35, 20, "m3", "3")
    f.text(x0, y, 'names = [item["name"] for item in products if item["stock"] > 0]'.replace("names = ", ""), "c")
    f.text(x0, 112, "то же самое циклом:", "s")
    lines = ["names = []", "for item in products:", '    if item["stock"] > 0:', '        names.append(item["name"])']
    ys = [146, 174, 202, 230]
    seg(x0, ys[1], 0, 20, "m1"); seg(x0, ys[2], 4, 20, "m3"); seg(x0, ys[3], 21, 12, "acc")
    for line, yy in zip(lines, ys):
        f.text(x0, yy, line, "c")
    f.text(x0, 272, "1 — что кладём в результат   2 — откуда берём элементы   3 — какие оставляем (необязательно)", "s")
    f.save(out(PY2 / "07-comprehensions" / "img" / "comprehension-anatomy.svg"))


PY3 = ROOT / "python" / "03-functions"


# ---------- Python 3.02: изменяемое значение по умолчанию ----------
def mutable_default():
    f = Figure(780, 270, "Изменяемое значение по умолчанию создаётся один раз и копит данные между вызовами")
    f.box(20, 30, 330, 70, "", "box")
    f.text(36, 60, "def add_to_cart(item, cart=[]):", "cs")
    f.text(36, 84, "[] создаётся один раз — при выполнении def", "s")
    f.box(440, 42, 320, 46, '["мышь", "коврик"]', "err", "c")
    f.arrow("M350 65H436"); f.text(362, 56, "cart по умолчанию", "s")
    f.text(20, 150, 'add_to_cart("мышь")', "c"); f.text(250, 150, '→ ["мышь"]', "c")
    f.text(20, 180, 'add_to_cart("коврик")', "c"); f.text(250, 180, '→ ["мышь", "коврик"]  — ожидали ["коврик"]', "c")
    f.text(440, 108, "один и тот же список для всех вызовов", "errt")
    f.text(20, 230, "Исправление: cart=None, а внутри — if cart is None: cart = []", "t")
    f.text(20, 252, "Тогда новый список создаётся при каждом вызове.", "s")
    f.save(out(PY3 / "02-parameters" / "img" / "mutable-default.svg"))


# ---------- Python 3.04: области видимости LEGB ----------
def legb_scopes():
    f = Figure(820, 330, "Области видимости LEGB: имя ищется от локальной области наружу")
    f.box(20, 20, 660, 290, "", "box2"); f.text(36, 44, "Built-in — встроенные имена", "h"); f.text(36, 64, "print, len, sum, max …", "cs")
    f.box(50, 80, 600, 220, "", "box"); f.text(66, 104, "Global — уровень модуля", "h"); f.text(66, 124, "TAX_RATE = 20", "cs")
    f.box(80, 140, 540, 150, "", "box2"); f.text(96, 164, "Enclosing — внешняя функция", "h"); f.text(96, 184, "def make_order(): discount = 10", "cs")
    f.raw('<rect x="110" y="200" width="480" height="80" rx="12" class="fig-m1"/>')
    f.text(126, 224, "Local — текущая функция", "h"); f.text(126, 248, "def apply(price): result = price * …", "cs")
    f.arrow("M700 290V30")
    for y, label in ((248, "1  Local"), (184, "2  Enclosing"), (124, "3  Global"), (64, "4  Built-in")):
        f.text(712, y, label, "t")
    f.text(700, 318, "первое найденное имя побеждает", "s", "middle")
    f.save(out(PY3 / "04-scope" / "img" / "legb-scopes.svg"))


# ---------- Python 3.07: стек рекурсивных вызовов ----------
def recursion_stack():
    f = Figure(880, 280, "Рекурсия: вызовы спускаются до базового случая, результаты поднимаются обратно")
    f.text(20, 24, "вызовы", "h"); f.text(520, 24, "возвраты", "h")
    calls = [("path(5)  — Мыши", "parent_id = 2 → ждёт path(2)", "box"),
             ("path(2)  — Периферия", "parent_id = 1 → ждёт path(1)", "box"),
             ("path(1)  — Электроника", "parent_id = None → базовый случай", "ok")]
    rets = ['"Электроника > Периферия > Мыши"', '"Электроника > Периферия"', '"Электроника"']
    for i, (title, sub, cls) in enumerate(calls):
        x, y = 20 + i * 40, 40 + i * 76
        f.box(x, y, 380, 56, "", cls)
        f.text(x + 14, y + 24, title, "c"); f.text(x + 14, y + 44, sub, "s")
        f.text(520, y + 34, "← " + rets[i], "cs")
        if i < 2:
            f.arrow(f"M{x + 60} {y + 56}V{y + 74}")
            f.arrow(f"M560 {y + 64}V{y + 46}", "lnd")
    f.text(20, 268, "Без базового случая вызовы не остановятся: RecursionError после ~1000 уровней.", "s")
    f.save(out(PY3 / "07-recursion" / "img" / "recursion-stack.svg"))


# ---------- Python 3.08: декоратор оборачивает функцию ----------
def decorator_wrap():
    f = Figure(780, 300, "Декоратор: имя функции теперь указывает на обёртку, которая вызывает исходную функцию")
    f.text(20, 26, "@log_call  ≡  add_to_cart = log_call(add_to_cart)", "c")
    f.box(20, 120, 150, 40, "add_to_cart", "box", "c", rx=20)
    f.arrow("M170 140H206")
    f.box(210, 50, 540, 232, "", "box2"); f.text(226, 72, "wrapper — функция, которую вернул log_call", "h")
    f.text(226, 100, "1. до вызова: print(\"вызов add_to_cart\", args)", "cs")
    f.box(240, 116, 340, 56, "", "box"); f.text(256, 140, "2. result = func(*args, **kwargs)", "cs")
    f.text(256, 160, "func — исходная add_to_cart", "s")
    f.text(226, 200, "3. после вызова: print(\"результат\", result)", "cs")
    f.text(226, 228, "4. return result", "cs")
    f.text(226, 256, "забыли return — любой вызов вернёт None", "errt")
    f.save(out(PY3 / "08-decorators" / "img" / "decorator-wrap.svg"))


PY4 = ROOT / "python" / "04-exceptions"


# ---------- Python 4.01: пути выполнения try / except / else / finally ----------
def try_flow():
    f = Figure(860, 300, "Какие блоки выполняются: без ошибки, с пойманной и с непойманной ошибкой")
    lanes = [("ошибки нет", [("try", "box2", "весь"), ("else", "ok", ""), ("finally", "box2", ""), ("дальше", "box", "")]),
             ("ошибка поймана", [("try", "box2", "до ошибки"), ("except", "err", ""), ("finally", "box2", ""), ("дальше", "box", "")]),
             ("ошибку не поймали", [("try", "box2", "до ошибки"), ("finally", "box2", ""), ("ошибка — выше", "err", "")])]
    for i, (title, steps) in enumerate(lanes):
        y = 40 + i * 86
        f.text(20, y + 30, title, "t")
        for k, (name, cls, sub) in enumerate(steps):
            x = 190 + k * 165
            f.box(x, y, 140, 46, "", cls)
            f.text(x + 70, y + 22 if sub else y + 28, name, "c", "middle")
            if sub:
                f.text(x + 70, y + 38, sub, "s", "middle")
            if k < len(steps) - 1:
                f.arrow(f"M{x + 140} {y + 23}H{x + 161}")
    f.text(20, 292, "finally выполняется всегда — даже если ошибка полетела дальше или в try сработал return.", "s")
    f.save(out(PY4 / "01-exceptions" / "img" / "try-flow.svg"))


# ---------- Python 4.03: traceback из нескольких вызовов ----------
def traceback_stack():
    f = Figure(900, 400, "Traceback цепочки вызовов: внизу — где упало, выше — кто вызвал")
    f.raw('<rect x="20" y="20" width="600" height="336" rx="14" class="fig-term"/>')
    rows = [("Traceback (most recent call last):", "tt"),
            ('  File "main.py", line 12, in <module>', "tt"),
            ('    print(checkout([1499, 490], "WINTER-15"))', "tt"),
            ("          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", "tterr"),
            ('  File "main.py", line 8, in checkout', "tt"),
            ("    percent = parse_percent(code)", "tt"),
            ("              ^^^^^^^^^^^^^^^^^^^", "tterr"),
            ('  File "main.py", line 3, in parse_percent', "tt"),
            ("    return int(code[5:])", "tt"),
            ("           ^^^^^^^^^^^^^", "tterr"),
            ("ValueError: invalid literal for int() with base 10: 'R-15'", "tterr")]
    for i, (text, cls) in enumerate(rows):
        f.text(36, 50 + i * 28, text, cls)
    notes = [(330, "1", "что случилось"), (274, "2", "где упало: последний кадр"),
             (190, "3", "кто вызвал parse_percent"), (106, "4", "откуда всё началось")]
    for y, n, label in notes:
        f.line(f"M624 {y - 5}H660", "lnd")
        f.raw(f'<circle cx="674" cy="{y - 5}" r="11" class="fig-acc"/>')
        f.text(674, y, n, "onacc", "middle")
        f.text(692, y, label, "s")
    f.text(20, 384, "Упало в parse_percent, а причина — в допущении «префикс промокода всегда из 4 букв».", "s")
    f.save(out(PY4 / "03-debugging" / "img" / "traceback-stack.svg"))

if __name__ == "__main__":
    for build in (traceback_anatomy, names_to_values, string_indices, delivery_elif, while_loop,
                  sets_venn, nested_order, copy_modes, comprehension_anatomy,
                  mutable_default, legb_scopes, recursion_stack, decorator_wrap,
                  try_flow, traceback_stack, dict_lookup, lost_key):
        build()
    print("ok")

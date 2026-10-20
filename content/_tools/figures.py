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
    f.raw('<rect x="20" y="20" width="560" height="176" rx="14" class="term"/>')
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
        f.raw(f'<circle cx="634" cy="{y - 5}" r="11" class="acc"/>')
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
        f.raw(f'<rect x="260" y="{y}" width="240" height="38" rx="10" class="box2"/>')
        f.text(276, y + 24, val, "c")
        f.raw(f'<rect x="520" y="{y + 5}" width="100" height="28" rx="14" class="acc"/>')
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
        f.raw(f'<rect x="{x}" y="90" width="{w - 6}" height="56" rx="10" class="{cls}"/>')
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
        if i == 2:
            f.raw(f'<rect x="{x}" y="132" width="80" height="64" rx="10" class="err"/>')
            f.text(x + 40, 158, "SKU(KB-02)", "cs", "middle"); f.text(x + 40, 180, "→ 12", "cs", "middle")
        else:
            f.raw(f'<rect x="{x}" y="132" width="80" height="64" rx="10" class="{"dash" if i == 6 else "box2"}"/>')
    f.text(40, 222, "ячейки таблицы dict (схематично)", "h")
    f.text(40, 26, 'SKU("KB-01") in stock', "c")
    f.text(40, 48, 'hash("KB-01") → ячейка 2: ячейка та, но в ней уже ключ KB-02', "s")
    f.arrow("M250 58V128"); f.text(262, 96, "== даёт False → не найден", "errt")
    f.arrow("M590 248V200")
    f.text(420, 268, "key in stock", "c")
    f.text(420, 290, 'hash("KB-02") → ячейка 6: она пуста → не найден', "s")
    f.save(out(INT3 / "03-hashable-and-immutability" / "img" / "lost-key.svg"))


if __name__ == "__main__":
    for build in (traceback_anatomy, names_to_values, string_indices, delivery_elif, while_loop, dict_lookup, lost_key):
        build()
    print("ok")

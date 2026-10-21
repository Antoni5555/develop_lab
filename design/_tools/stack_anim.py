"""Генератор картинки первого экрана главной: «полный цикл» (стек слоёв).

Блок кода падает сверху, задевает слой — слой зеленеет, прилипает и едет дальше вместе с ним.
Скрипт печатает SVG и CSS (@keyframes) — их вставляют в шаблон и в стили главной.
Менять слои, размеры или длительность — здесь, а не руками в CSS: проценты в keyframes считаются.

Запуск:  python3 design/_tools/stack_anim.py svg   → разметка SVG
         python3 design/_tools/stack_anim.py css   → CSS-анимации (без базовых стилей .stk-*)
"""
import sys

# ---------- 1. Стек: блок кода опускается, слои зеленеют и слипаются ----------
W, H, T = 76, 38, 12          # полуширина и полувысота ромба, толщина слоя
CX = 160
S = 46                        # шаг слоёв в покое
G = S - T                     # зазор, который закрывается за одну фазу
Y0 = 14                       # верх ромба «кода» в покое
LAYERS = ['Frontend', 'Backend', 'База данных', 'Docker', 'CI/CD']
D = 8.0                       # длительность цикла, с
MOVE = 0.55                   # время падения в фазе (из 1 с)


def pct(t):
    return f'{t / D * 100:.2f}%'


def slab(y, cls, label=None, label_cls=''):
    top = f'M{CX} {y} l{W} {H} l{-W} {H} l{-W} {-H}z'
    left = f'M{CX - W} {y + H} l{W} {H} l0 {T} l{-W} {-H}z'
    right = f'M{CX + W} {y + H} l{-W} {H} l0 {T} l{W} {-H}z'
    out = [f'<path d="{left}" class="stk-left"/>',
           f'<path d="{right}" class="stk-right"/>',
           f'<path d="{top}" class="stk-top"/>']
    if label:
        ly = y + H
        out.append(f'<line x1="{CX + W + 6}" y1="{ly}" x2="{CX + W + 26}" y2="{ly}" class="ha-leader"/>')
        out.append(f'<text x="{CX + W + 32}" y="{ly + 5}" class="stk-label {label_cls}">{label}</text>')
    return '\n'.join(out)


def stack_svg():
    parts = ['<svg viewBox="0 0 440 340" class="hero-art__svg hero-art__svg--stack">',
             '  <!-- Слои fullstack-цикла; «код» падает сверху, задевает слой — тот зеленеет и едет дальше вместе с ним -->']
    # рисуем снизу вверх: верхний слой должен перекрывать нижний, когда они слиплись
    for i, name in reversed(list(enumerate(LAYERS))):
        y = Y0 + S * (i + 1)
        parts.append(f'  <g class="stk stk--{i}">\n{slab(y, "")}\n  </g>')
    parts.append(f'  <g class="stk stk--code">\n{slab(Y0, "")}\n'
                 f'<text x="{CX}" y="{Y0 + H + 5}" class="stk-code-label">&lt;/&gt;</text>\n  </g>')
    # Подписи стоят на месте (список справа) и загораются, когда их слой «прилип»
    for i, name in enumerate(LAYERS):
        ly = Y0 + S * (i + 1) + H
        parts.append(f'  <g class="stk-tag stk-tag--{i}"><circle cx="{CX + W + 30}" cy="{ly}" r="5" class="stk-bullet"/>'
                     f'<text x="{CX + W + 44}" y="{ly + 5}" class="stk-label">{name}</text></g>')
    parts.append('</svg>')
    return '\n'.join(parts)


def stack_css():
    css = ['/* Стек: позиции по фазам. Элемент e (код = -1, слои 0..4) едет в фазах k > e. */']
    n = len(LAYERS)
    for e in [-1] + list(range(n)):
        name = 'code' if e == -1 else str(e)
        frames = [(0, 0)]
        for k in range(e + 1, n):
            done_before = k - (e + 1)
            frames.append((k, done_before * G))
            frames.append((k + MOVE, (done_before + 1) * G))
        final = frames[-1][1]
        frames.append((7.0, final))
        frames.append((D, 0))
        kf = '\n'.join(f'  {pct(t)} {{ transform: translateY({d}px); }}' for t, d in frames)
        css.append(f'@keyframes stk-move-{name} {{\n{kf}\n}}')
        css.append(f'.stk--{name} {{ animation: stk-move-{name} {D}s ease-in-out infinite; }}')
        if e >= 0:
            touch = e + MOVE
            css.append(
                f'@keyframes stk-on-{name} {{\n'
                f'  0%, {pct(touch - 0.01)} {{ --on: 0; }}\n'
                f'  {pct(touch)}, {pct(7.0)} {{ --on: 1; }}\n'
                f'  100% {{ --on: 0; }}\n}}')
            css.append(f'.stk--{name} {{ animation: stk-move-{name} {D}s ease-in-out infinite, stk-on-{name} {D}s step-end infinite; }}')
            css.append(f'.stk-tag--{name} {{ animation: stk-on-{name} {D}s step-end infinite; }}')
    return '\n'.join(css)


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'svg'
    print(stack_svg() if what == 'svg' else stack_css())

"""Генератор картинки первого экрана «О проекте»: путь разработчика.

Лаймовая кривая рисуется и проходит через стеки курсов (Python → … → Nginx).
Стек сначала белый; когда линия до него доходит — загорается лаймом, линия идёт дальше.
Фон — пунктир маршрута, тонкие параллельные кривые, кольца и точки.
Позиции станций на кривой и тайминги считаются здесь — руками в CSS не править.

Запуск:  python3 design/_tools/path_anim.py svg
         python3 design/_tools/path_anim.py css
"""
import math
import sys

W, H = 440, 440
D = 10.0                       # длительность цикла, с
DRAW_START, DRAW_END = 0.4, 7.2  # когда линия рисуется
HOLD_END = 9.0                 # до какой секунды держим готовую картинку

# Кривая — цепочка кубических Безье: (p0, c1, c2, p1)
SEGMENTS = [
    ((24, 52), (120, 10), (150, 120), (230, 98)),
    ((230, 98), (330, 70), (430, 120), (372, 196)),
    ((372, 196), (320, 262), (150, 190), (110, 262)),
    ((110, 262), (72, 330), (200, 380), (290, 356)),
    ((290, 356), (360, 338), (380, 300), (420, 316)),
]
STACKS = ['Python', 'Linux', 'Git', 'HTTP', 'SQL', 'Django', 'Docker', 'Nginx']
FRACTIONS = [0.06, 0.19, 0.31, 0.44, 0.57, 0.69, 0.82, 0.94]


def bez(seg, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = seg
    u = 1 - t
    return (u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
            u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3)


def sample(n=400):
    """Точки кривой и накопленная длина — чтобы найти точку на доле длины пути."""
    pts = []
    for seg in SEGMENTS:
        for i in range(n):
            pts.append(bez(seg, i / n))
    pts.append(SEGMENTS[-1][3])
    acc = [0.0]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        acc.append(acc[-1] + math.hypot(bx - ax, by - ay))
    return pts, acc


def point_at(frac, pts, acc):
    target = frac * acc[-1]
    for i, length in enumerate(acc):
        if length >= target:
            return pts[i]
    return pts[-1]


def path_d(dx=0, dy=0):
    (x0, y0) = SEGMENTS[0][0]
    d = f'M{x0 + dx} {y0 + dy}'
    for _, (x1, y1), (x2, y2), (x3, y3) in SEGMENTS:
        d += f' C{x1 + dx} {y1 + dy}, {x2 + dx} {y2 + dy}, {x3 + dx} {y3 + dy}'
    return d


def pct(t):
    return f'{t / D * 100:.2f}%'


def svg():
    pts, acc = sample()
    main = path_d()
    out = [f'<svg viewBox="0 0 {W} {H}" class="about-art__svg">',
           '  <!-- Фон: две тонкие кривые повторяют маршрут со сдвигом + геометрия (всё приглушено) -->',
           f'  <path d="{path_d(-26, 34)}" class="dp-bg-line"/>',
           f'  <path d="{path_d(30, -30)}" class="dp-bg-line dp-bg-line--dashed"/>',
           '  <path d="M372 44a30 30 0 0 1 60 0" class="dp-shape"/>',
           '  <g class="dp-dots"><circle cx="300" cy="18" r="1.8"/><circle cx="312" cy="18" r="1.8"/><circle cx="324" cy="18" r="1.8"/>'
           '<circle cx="300" cy="30" r="1.8"/><circle cx="312" cy="30" r="1.8"/><circle cx="324" cy="30" r="1.8"/>'
           '<circle cx="300" cy="42" r="1.8"/><circle cx="312" cy="42" r="1.8"/><circle cx="324" cy="42" r="1.8"/></g>',
           '  <rect x="28" y="370" width="24" height="24" rx="5" class="dp-shape dp-shape--accent" transform="rotate(20 40 382)"/>',
           '  <path d="M150 166l9 16h-18z" class="dp-shape"/>',
           '  <circle cx="268" cy="168" r="6" class="dp-shape"/>',
           '  <path d="M60 134v12m-6-6h12M420 236v12m-6-6h12M200 414v10m-5-5h10" class="dp-shape"/>',
           '  <circle cx="408" cy="272" r="3.5" class="dp-spark"/><circle cx="24" cy="196" r="3" class="dp-spark"/>',
           '  <!-- Маршрут пунктиром и сама линия, которая рисуется -->',
           f'  <path d="{main}" class="dp-route"/>',
           f'  <path d="{main}" pathLength="1" class="dp-line"/>',
           '  <!-- Стеки на маршруте: белые, загораются, когда до них доходит линия -->']
    for i, (name, f) in enumerate(zip(STACKS, FRACTIONS)):
        x, y = point_at(f, pts, acc)
        w = 38 + len(name) * 8   # слева точка и отступ 24, справа такое же поле
        out.append(f'  <g class="dp-stack dp-stack--{i}">'
                   f'<rect x="{x - w / 2:.1f}" y="{y - 15:.1f}" width="{w:.1f}" height="30" rx="15" class="dp-chip"/>'
                   f'<circle cx="{x - w / 2 + 14:.1f}" cy="{y:.1f}" r="4" class="dp-dot"/>'
                   f'<text x="{x - w / 2 + 24:.1f}" y="{y + 4.5:.1f}" class="dp-label">{name}</text></g>')
    end = SEGMENTS[-1][3]
    out.append(f'  <circle cx="{end[0]}" cy="{end[1]}" r="7" class="dp-end"/>')
    out.append('</svg>')
    return '\n'.join(out)


def css():
    out = [f'/* Линия рисуется {DRAW_START}–{DRAW_END} с, держим до {HOLD_END} с, затем гаснет; цикл {D} с */',
           f'@keyframes dp-line {{ 0%, {pct(DRAW_START)} {{ stroke-dashoffset: 1; opacity: 1; }} '
           f'{pct(DRAW_END)}, {pct(HOLD_END)} {{ stroke-dashoffset: 0; opacity: 1; }} '
           f'{pct(D - 0.3)} {{ stroke-dashoffset: 0; opacity: 0; }} 100% {{ stroke-dashoffset: 1; opacity: 0; }} }}',
           f'.dp-line {{ stroke-dasharray: 1; stroke-dashoffset: 1; animation: dp-line {D}s cubic-bezier(0.45, 0, 0.55, 1) infinite; }}']
    # линия рисуется с плавным ускорением/замедлением — момент прихода к станции считаем по той же кривой времени
    def eased_time(frac):
        # обратная функция к ease-in-out (приближённо, бинарным поиском по кубической кривой 0.45,0,0.55,1)
        def bez1(t, p1, p2):
            return 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if bez1(mid, 0, 1) < frac:   # y(t) по контрольным точкам 0 и 1
                lo = mid
            else:
                hi = mid
        s = (lo + hi) / 2
        x = bez1(s, 0.45, 0.55)          # доля времени для этой доли пути
        return DRAW_START + x * (DRAW_END - DRAW_START)
    for i, f in enumerate(FRACTIONS):
        t = eased_time(f)
        out.append(f'@keyframes dp-on-{i} {{ 0%, {pct(t - 0.01)} {{ --on: 0; }} {pct(t)}, {pct(HOLD_END + 0.3)} {{ --on: 1; }} 100% {{ --on: 0; }} }}')
        out.append(f'@keyframes dp-pop-{i} {{ 0%, {pct(t - 0.01)} {{ transform: scale(1); }} {pct(t + 0.15)} {{ transform: scale(1.12); }} {pct(t + 0.4)}, 100% {{ transform: scale(1); }} }}')
        out.append(f'.dp-stack--{i} {{ animation: dp-on-{i} {D}s step-end infinite, dp-pop-{i} {D}s ease-out infinite; }}')
    return '\n'.join(out)


if __name__ == '__main__':
    what = sys.argv[1] if len(sys.argv) > 1 else 'svg'
    print(svg() if what == 'svg' else css())

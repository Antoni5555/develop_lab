"""Картинка превью ссылки (Open Graph) 1200×630: её показывают мессенджеры и соцсети.

Текст — буквы шрифтов сайта, переведённые в контуры (как в logo_gen.py), поэтому
картинка не зависит от установленных шрифтов. Шрифты сайта разрезаны на латиницу
и кириллицу — каждая буква берётся из того файла, где она есть.
Результат: design/og/og.svg и og.png; og.png копируется в src/static/img/.

Нужны fonttools, brotli, uharfbuzz и Inkscape:
    .venv/bin/python design/_tools/og_gen.py
"""
import shutil
import subprocess
from functools import cache
from io import BytesIO
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT.parent / 'src' / 'static' / 'fonts'
OUT = ROOT / 'og'
STATIC_IMG = ROOT.parent / 'src' / 'static' / 'img'

W, H = 1200, 630
LIME, INK, WHITE, MUTED, LINE = '#dcf25c', '#0e0e0e', '#f1f1ee', '#8e8e8a', '#2a2a2e'


@cache
def load(font_file):
    tt = TTFont(FONTS / font_file)
    tt.flavor = None
    buf = BytesIO()
    tt.save(buf)
    font = hb.Font(hb.Face(buf.getvalue()))
    return tt, font


def runs(text, family):
    """Делит строку на куски: латиница + общие знаки / кириллица."""
    latin = load(f'{family}-latin-{WEIGHTS[family]}.woff2')[0].getBestCmap()
    out = []
    for ch in text:
        part = 'latin' if ord(ch) in latin else 'cyrillic'
        if out and out[-1][0] == part:
            out[-1][1] += ch
        else:
            out.append([part, ch])
    return out


WEIGHTS = {'unbounded': 600, 'manrope': 600}


def text(s, x, y, size, family, fill, weight=None):
    """SVG-путь строки: x, y — начало базовой линии. Возвращает (svg, ширина)."""
    w = weight or WEIGHTS[family]
    pen_x = 0.0
    parts = []
    for part, chunk in runs(s, family):
        tt, font = load(f'{family}-{part}-{w}.woff2')
        k = size / tt['head'].unitsPerEm
        buf = hb.Buffer()
        buf.add_str(chunk)
        buf.guess_segment_properties()
        hb.shape(font, buf, {'kern': True, 'liga': False})
        glyphs, order = tt.getGlyphSet(), tt.getGlyphOrder()
        pen = SVGPathPen(glyphs)
        gx = 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            glyphs[order[info.codepoint]].draw(TransformPen(pen, (1, 0, 0, -1, gx + pos.x_offset, 0)))
            gx += pos.x_advance
        parts.append(f'<path transform="translate({x + pen_x:.1f} {y}) scale({k:.5f})" d="{pen.getCommands()}" fill="{fill}"/>')
        pen_x += gx * k
    return ''.join(parts), pen_x


def mark(x, y, size):
    k = size / 88
    return (f'<g transform="translate({x - 6 * k:.2f} {y - 9 * k:.2f}) scale({k:.4f})">'
            f'<path d="M50 14L88 34L50 54L12 34Z" fill="{WHITE}" stroke="{WHITE}" stroke-width="8" stroke-linejoin="round"/>'
            f'<path d="M12 52L50 72L88 52M12 70L50 90L88 70" fill="none" stroke="{LIME}" stroke-width="10" '
            'stroke-linecap="round" stroke-linejoin="round"/></g>')


def chips(names, x, y):
    out = []
    for name in names:
        label, width = text(name, x + 26, y + 33, 24, 'manrope', WHITE)
        w = width + 52
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="50" rx="25" fill="none" stroke="{LINE}" stroke-width="2"/>{label}')
        x += w + 12
    return ''.join(out)


def svg():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
             f'<rect width="{W}" height="{H}" fill="{INK}"/>',
             # фон: крупный знак за краем справа, едва заметный
             f'<g opacity="0.07">{mark(820, 150, 520).replace(WHITE, LIME)}</g>',
             mark(72, 64, 52)]
    word, _ = text('stackflow', 136, 103, 38, 'manrope', LIME)
    parts.append(word)
    line1, _ = text('Практика', 72, 262, 78, 'unbounded', WHITE)
    line2, _ = text('для разработчиков', 72, 356, 78, 'unbounded', WHITE)
    sub, _ = text('Теория, задачи и тренажёры прямо в браузере. Бесплатно.', 72, 424, 30, 'manrope', MUTED, 400)
    _, domain_width = text('stack-flow.ru', 0, 0, 26, 'manrope', MUTED)
    domain, _ = text('stack-flow.ru', W - 72 - domain_width, 103, 26, 'manrope', MUTED)
    parts += [line1, line2, sub, chips(['Python', 'SQL', 'Django', 'Linux', 'Git', 'Docker'], 72, 508), domain, '</svg>']
    return ''.join(parts)


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    (OUT / 'og.svg').write_text(svg() + '\n', encoding='utf-8')
    png = OUT / 'og.png'
    subprocess.run(['inkscape', str(OUT / 'og.svg'), '--export-type=png', f'--export-filename={png}',
                    '-w', str(W), '-h', str(H)], check=True, capture_output=True)
    shutil.copy(png, STATIC_IMG / 'og.png')
    print('ok', png.stat().st_size)

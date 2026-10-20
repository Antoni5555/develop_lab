"""Мини-библиотека для SVG-рисунков уроков (правила — docs/content-format.md, раздел 4).

Цвета — переменные темы сайта с запасным цветом светлой темы:
сайт вставляет SVG inline, и рисунок меняет цвета вместе с темой.
"""


def _v(prop, var, fallback):
    return f"{prop}:{fallback};{prop}:var({var},{fallback})"


MAIN = "font-family:Manrope,sans-serif;font-family:var(--font-main,Manrope,sans-serif)"
CODE = "font-family:'JetBrains Mono',monospace;font-family:var(--font-code,'JetBrains Mono',monospace)"

STYLE = f"""<style>
text{{white-space:pre}}
.t{{{MAIN};font-size:14px;{_v('fill', '--text', '#0e0e0e')}}}
.c{{{CODE};font-size:14px;{_v('fill', '--text', '#0e0e0e')}}}
.cs{{{CODE};font-size:12px;{_v('fill', '--text', '#0e0e0e')}}}
.h{{{MAIN};font-size:12px;letter-spacing:.04em;text-transform:uppercase;{_v('fill', '--muted', '#6e6e6a')}}}
.s{{{MAIN};font-size:12px;{_v('fill', '--muted', '#6e6e6a')}}}
.box{{{_v('fill', '--surface', '#ffffff')};{_v('stroke', '--border', '#e0e0dc')};stroke-width:1.5}}
.box2{{{_v('fill', '--surface-2', '#ebebe8')};{_v('stroke', '--border', '#e0e0dc')};stroke-width:1.5}}
.acc{{{_v('fill', '--accent', '#dcf25c')}}}
.onacc{{{CODE};font-size:13px;{_v('fill', '--on-accent', '#0e0e0e')}}}
.ln{{{_v('stroke', '--muted', '#6e6e6a')};stroke-width:1.5;fill:none}}
.lnd{{{_v('stroke', '--muted', '#6e6e6a')};stroke-width:1.5;fill:none;stroke-dasharray:5 4}}
.ah{{{_v('fill', '--muted', '#6e6e6a')}}}
.err{{{_v('fill', '--error-bg', '#fdecea')};{_v('stroke', '--error', '#d93025')};stroke-width:1.5}}
.errt{{{MAIN};font-size:13px;{_v('fill', '--error', '#d93025')}}}
.ok{{{_v('fill', '--success-bg', '#e7f6ec')};{_v('stroke', '--success', '#1f9d55')};stroke-width:1.5}}
.dash{{fill:none;{_v('stroke', '--muted', '#6e6e6a')};stroke-width:1.5;stroke-dasharray:5 4}}
.term{{fill:#0d0d0f;fill:var(--term-bg,#0d0d0f)}}
.tt{{{CODE};font-size:13px;fill:#e6e6e3;fill:var(--term-text,#e6e6e3)}}
.tterr{{{CODE};font-size:13px;fill:#f87171}}
</style>
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="ah"/></marker></defs>"""


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


class Figure:
    def __init__(self, width, height, title):
        self.w, self.h, self.title, self.parts = width, height, title, []

    def raw(self, svg):
        self.parts.append(svg)

    def text(self, x, y, s, cls="t", anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" class="{cls}">{esc(s)}</text>')

    def box(self, x, y, w, h, label="", cls="box", tcls="t", rx=12):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>')
        lines = label.split("|") if label else []
        for k, line in enumerate(lines):
            ty = y + h / 2 + 5 + (k - (len(lines) - 1) / 2) * 18
            self.text(x + w / 2, ty, line, tcls, "middle")

    def diamond(self, cx, cy, w, h, label, cls="box2"):
        self.parts.append(f'<path d="M{cx} {cy - h / 2}L{cx + w / 2} {cy}L{cx} {cy + h / 2}L{cx - w / 2} {cy}Z" class="{cls}"/>')
        self.text(cx, cy + 5, label, "t", "middle")

    def arrow(self, d, cls="ln"):
        self.parts.append(f'<path d="{d}" class="{cls}" marker-end="url(#a)"/>')

    def line(self, d, cls="ln"):
        self.parts.append(f'<path d="{d}" class="{cls}"/>')

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img" aria-labelledby="t">'
                f'<title id="t">{esc(self.title)}</title>\n{STYLE}\n')
        path.write_text(head + "\n".join(self.parts) + "\n</svg>\n")

"""Gera os cards da seção Atividade do perfil (linguagens + streak, claro/escuro).

Segue o sistema visual do cauedev.shop (ver tools/README.md): paper com borda ink,
sombra dura sem blur, malha azul a 5%, Space Grotesk no display, Inter no corpo,
selo girado -8°. O texto vira <path> vetorial — nada de font-family que o leitor
pode não ter.

Uso:
    pip install fonttools
    GITHUB_TOKEN=... python tools/gen_activity_cards.py [saida/]

Saída: langs-light.svg, langs-dark.svg, streak-light.svg, streak-dark.svg
"""

import io
import json
import os
import sys
import urllib.request
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

USER = "cauelimsia"
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
CACHE = Path(__file__).parent / ".fonts"

# ---------------------------------------------------------------- tokens
INK, BLUE, LIME, CORAL = "#111111", "#125cfe", "#ccff00", "#ff4d4d"
PAPER, MUTED = "#ffffff", "#6b7280"
D_BG, D_TEXT, D_BLUE, D_MUTED = "#161b22", "#e6edf3", "#7da2ff", "#9ba3af"

LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "HTML": "#e34c26",
    "CSS": "#663399", "PLpgSQL": "#336790", "Python": "#3572A5", "Shell": "#89e051",
}
LANG_COLORS_DARK = {**LANG_COLORS, "CSS": "#a371f7", "PLpgSQL": "#58a6ff"}
LANG_ABBREV = {"TypeScript": "TS", "JavaScript": "JS", "PLpgSQL": "SQL", "Python": "PY"}

FONTS = {
    "display": ("https://github.com/google/fonts/raw/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf", {"wght": 700}),
    "body": ("https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf", {"wght": 400}),
    "bold": ("https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf", {"wght": 700}),
}


def load_font(key):
    url, axes = FONTS[key]
    CACHE.mkdir(exist_ok=True)
    raw = CACHE / (url.rsplit("/", 1)[-1].replace("%5B", "[").replace("%5D", "]").replace("%2C", ","))
    if not raw.exists():
        raw.write_bytes(urllib.request.urlopen(url).read())
    font = TTFont(raw)
    instantiateVariableFont(font, axes)
    return font


_fonts = {}


def text_path(text, key, size, x, y, fill, tracking=0.0, anchor="start"):
    """Renderiza `text` como paths. tracking em em; anchor start|middle|end."""
    if key not in _fonts:
        _fonts[key] = load_font(key)
    font = _fonts[key]
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = size / font["head"].unitsPerEm
    track = tracking * size

    widths, names = [], []
    for ch in text:
        name = cmap.get(ord(ch), ".notdef")
        names.append(name)
        widths.append(glyphset[name].width * scale)
    total = sum(widths) + track * max(0, len(text) - 1)
    cursor = x - {"start": 0, "middle": total / 2, "end": total}[anchor]

    parts = []
    for name, w in zip(names, widths):
        pen = SVGPathPen(glyphset)
        glyphset[name].draw(pen)
        d = pen.getCommands()
        if d:
            parts.append(
                f'<path transform="translate({cursor:.2f},{y:.2f}) scale({scale:.6f},{-scale:.6f})" d="{d}"/>'
            )
        cursor += w + track
    return f'<g fill="{fill}">{"".join(parts)}</g>', total


# ---------------------------------------------------------------- dados
def gh(path_or_query, graphql=False):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        sys.exit("defina GITHUB_TOKEN")
    if graphql:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": path_or_query}).encode(),
            headers={"Authorization": f"bearer {token}"},
        )
    else:
        req = urllib.request.Request(
            f"https://api.github.com{path_or_query}",
            headers={"Authorization": f"bearer {token}"},
        )
    return json.load(io.TextIOWrapper(urllib.request.urlopen(req), "utf-8"))


def get_languages():
    repos = gh(f"/users/{USER}/repos?per_page=100")
    skip = {USER, "sandbox"}
    totals = {}
    for repo in repos:
        if repo["fork"] or repo["name"] in skip:
            continue
        for lang, n in gh(f"/repos/{USER}/{repo['name']}/languages").items():
            totals[lang] = totals.get(lang, 0) + n
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
    total = sum(n for _, n in ranked)
    return [(lang, n / total * 100) for lang, n in ranked]


def get_streaks():
    q = f'query {{ user(login:"{USER}") {{ contributionsCollection {{ contributionCalendar {{ totalContributions weeks {{ contributionDays {{ date contributionCount }} }} }} }} }} }}'
    cal = gh(q, graphql=True)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])

    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)

    current = 0
    idx = len(days) - 1
    # dia de hoje sem commit ainda não quebra o streak
    if days and days[-1]["contributionCount"] == 0:
        idx -= 1
    while idx >= 0 and days[idx]["contributionCount"] > 0:
        current += 1
        idx -= 1
    return cal["totalContributions"], current, longest


# ---------------------------------------------------------------- desenho
W, H = 420, 165
CW, CH = 406, 151  # card


def fmt(n):
    return f"{n:,}".replace(",", ".")


def pct(p):
    return f"{p:.1f}".replace(".", ",") + "%"


def card_shell(dark, shadow):
    """Sombra dura + card + malha. Retorna (abertura, clip-id do card)."""
    bg = D_BG if dark else PAPER
    border = D_TEXT if dark else INK
    mesh = "#7da2ff" if dark else BLUE
    mesh_op = "0.07" if dark else "0.05"
    lines = "".join(
        f'<path d="M{x} 2 V{CH + 2}" stroke="{mesh}" stroke-opacity="{mesh_op}" stroke-width="1"/>'
        for x in range(26, CW, 24)
    ) + "".join(
        f'<path d="M2 {y} H{CW + 2}" stroke="{mesh}" stroke-opacity="{mesh_op}" stroke-width="1"/>'
        for y in range(26, CH, 24)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
        f'<rect x="8" y="8" width="{CW}" height="{CH}" rx="18" fill="{shadow}"/>'
        f'<rect x="2" y="2" width="{CW}" height="{CH}" rx="18" fill="{bg}" stroke="{border}" stroke-width="2"/>'
        f'<clipPath id="card"><rect x="2" y="2" width="{CW}" height="{CH}" rx="18"/></clipPath>'
        f'<g clip-path="url(#card)">{lines}</g>'
    )


def sticker(cx, cy, label, dark):
    """Selo girado -8°: lime com borda ink, texto ink."""
    text, tw = text_path(label, "display", 14, 0, 5, INK, tracking=-0.02, anchor="middle")
    w = tw + 26
    return (
        f'<g transform="translate({cx},{cy}) rotate(-8)">'
        f'<rect x="{-w / 2 + 3}" y="-9" width="{w}" height="26" rx="13" fill="{INK}"/>'
        f'<rect x="{-w / 2}" y="-12" width="{w}" height="26" rx="13" fill="{LIME}" stroke="{INK}" stroke-width="2"/>'
        f"{text}</g>"
    )


def langs_card(langs, dark):
    text_c = D_TEXT if dark else INK
    title_c = D_BLUE if dark else BLUE
    border = D_TEXT if dark else INK
    muted = D_MUTED if dark else MUTED
    colors = LANG_COLORS_DARK if dark else LANG_COLORS
    shadow = LIME if dark else INK
    svg = card_shell(dark, shadow)

    title, _ = text_path("Linguagens", "display", 20, 26, 40, title_c, tracking=-0.035)
    svg += title
    lead = LANG_ABBREV.get(langs[0][0], langs[0][0][:2].upper())
    svg += sticker(322, 34, f"{lead} lidera", dark)

    # barra empilhada, segmentos com contorno
    bx, by, bw, bh = 26, 60, 358, 16
    svg += f'<clipPath id="bar"><rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8"/></clipPath><g clip-path="url(#bar)">'
    x = bx
    for lang, p in langs:
        w = bw * p / 100
        svg += f'<rect x="{x:.1f}" y="{by}" width="{w:.1f}" height="{bh}" fill="{colors.get(lang, muted)}" stroke="{border}" stroke-width="1.4"/>'
        x += w
    svg += "</g>"
    svg += f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="none" stroke="{border}" stroke-width="2"/>'

    # legenda: grade 3 x 2, quadradinhos com borda
    cols = [26, 158, 290]
    rows = [100, 130]
    for i, (lang, p) in enumerate(langs):
        cx, cy = cols[i % 3], rows[i // 3]
        svg += f'<rect x="{cx}" y="{cy - 9}" width="11" height="11" rx="2" fill="{colors.get(lang, muted)}" stroke="{border}" stroke-width="1.4"/>'
        name, nw = text_path(lang, "body", 12.5, cx + 17, cy + 1, text_c)
        svg += name
        val, _ = text_path(pct(p), "bold", 12.5, cx + 17 + nw + 5, cy + 1, muted)
        svg += val
    return svg + "</svg>"


def streak_card(total, current, longest, dark):
    text_c = D_TEXT if dark else INK
    title_c = D_BLUE if dark else BLUE
    border = D_TEXT if dark else INK
    muted = D_MUTED if dark else MUTED
    shadow = LIME if dark else INK
    svg = card_shell(dark, shadow)

    title, _ = text_path("Ritmo", "display", 20, 26, 40, title_c, tracking=-0.035)
    svg += title
    svg += sticker(316, 34, "commit a commit", dark)

    # coluna central em destaque: sticker gigante com o streak atual
    cx = 210
    hero_w, hero_h = 120, 66
    svg += (
        f'<g transform="translate({cx},100) rotate(-8)">'
        f'<rect x="{-hero_w / 2 + 4}" y="{-hero_h / 2 - 1}" width="{hero_w}" height="{hero_h}" rx="16" fill="{INK}"/>'
        f'<rect x="{-hero_w / 2}" y="{-hero_h / 2 - 5}" width="{hero_w}" height="{hero_h}" rx="16" fill="{LIME}" stroke="{INK}" stroke-width="2.5"/>'
    )
    num, _ = text_path(str(current), "display", 40, 0, 4, INK, tracking=-0.02, anchor="middle")
    lab, _ = text_path("streak atual", "bold", 10.5, 0, 22, INK, anchor="middle")
    svg += num + lab + "</g>"

    for x, value, label in ((80, fmt(total), "contribs no ano"), (340, str(longest), "maior streak")):
        v, _ = text_path(value, "display", 30, x, 100, text_c, tracking=-0.02, anchor="middle")
        l, _ = text_path(label, "body", 12, x, 122, muted, anchor="middle")
        svg += v + l
    return svg + "</svg>"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    langs = get_languages()
    total, current, longest = get_streaks()
    print(f"linguagens: {[(l, round(p, 1)) for l, p in langs]}")
    print(f"contribs ano={total} atual={current} maior={longest}")
    for dark, suffix in ((False, "light"), (True, "dark")):
        (OUT / f"langs-{suffix}.svg").write_text(langs_card(langs, dark), encoding="utf-8")
        (OUT / f"streak-{suffix}.svg").write_text(streak_card(total, current, longest, dark), encoding="utf-8")
    print(f"4 cards em {OUT}/")


if __name__ == "__main__":
    main()

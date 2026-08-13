"""Gera o banner do perfil e os social previews dos repositorios.

Segue o sistema visual do cauedev.shop (DESIGN.md / src/styles/main.css): neubrutalismo
com borda ink de 2px, sombra dura sem blur, cor chapada, Space Grotesk no display e Inter
no corpo. A marca Atlas (mascote, lockup, nome) NAO entra aqui de proposito: o perfil se
apresenta como pessoa procurando vaga, nao como agencia. O que atravessa e a linguagem
visual, para que quem sai do GitHub para o site sinta a mesma mao.
"""
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(BASE, "fonts")
OUT = os.path.join(BASE, "cards")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FONTS, exist_ok=True)

# Space Grotesk + Inter, as mesmas do site (OFL). Baixadas na primeira execucao.
FONT_URLS = {
    "SpaceGrotesk-Bold.ttf":
        "https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj4PVksj.ttf",
    "SpaceGrotesk-Medium.ttf":
        "https://fonts.gstatic.com/s/spacegrotesk/v22/V8mQoQDjQSkFtoMM3T6r8E7mF71Q-gOoraIAEj7aUUsj.ttf",
    "Inter-SemiBold.ttf":
        "https://fonts.gstatic.com/s/inter/v20/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuGKYMZg.ttf",
    "Inter-Regular.ttf":
        "https://fonts.gstatic.com/s/inter/v20/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfMZg.ttf",
}
for _name, _url in FONT_URLS.items():
    _dest = os.path.join(FONTS, _name)
    if not os.path.exists(_dest):
        print("baixando", _name)
        urllib.request.urlretrieve(_url, _dest)

GROTESK_BOLD = os.path.join(FONTS, "SpaceGrotesk-Bold.ttf")
GROTESK_MED = os.path.join(FONTS, "SpaceGrotesk-Medium.ttf")
INTER = os.path.join(FONTS, "Inter-Regular.ttf")

# tokens de main.css
BLUE = (18, 92, 254)
LIME = (204, 255, 0)
CORAL = (255, 77, 77)
INK = (0, 0, 0)
PAPER = (255, 255, 255)
CREAM = (245, 242, 234)
TEXT = (10, 10, 10)
MUTED = (86, 86, 86)

BORDER = 3        # a borda de 2px do site, engrossada para 1280px de card
SHADOW = 14       # sombra dura, sem blur
RADIUS = 18


def font(path, size):
    return ImageFont.truetype(path, size)


def on(fill):
    """Tinta legivel sobre um preenchimento chapado. Preto sobre o azul da marca
    da 4.0:1 e branco da 5.2:1 — entao azul pede branco, lime e coral pedem preto."""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    lum = 0.2126 * lin(fill[0]) + 0.7152 * lin(fill[1]) + 0.0722 * lin(fill[2])
    contrast_white = 1.05 / (lum + 0.05)
    contrast_black = (lum + 0.05) / 0.05
    return PAPER if contrast_white > contrast_black else INK


def tracked(draw, xy, text, f, fill, tracking=0.0, anchor_top=True):
    """Desenha com letter-spacing. Pillow nao tem tracking, entao vai glifo a glifo.
    O display do site usa ate -0.04em; tracking e uma fracao do corpo da fonte."""
    x, y = xy
    step = f.size * tracking
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill, anchor="la" if anchor_top else "ls")
        x += draw.textlength(ch, font=f) + step
    return x


def tracked_width(draw, text, f, tracking=0.0):
    step = f.size * tracking
    return sum(draw.textlength(c, font=f) for c in text) + step * max(len(text) - 1, 0)


def fit_tracked(draw, text, path, start, max_w, tracking, min_size=34):
    size = start
    while size > min_size:
        f = font(path, size)
        if tracked_width(draw, text, f, tracking) <= max_w:
            return f
        size -= 2
    return font(path, min_size)


def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def hard_box(d, box, fill, shadow=SHADOW, radius=RADIUS, border=BORDER):
    """Caixa neubrutalist: preenchimento chapado, borda ink, sombra dura deslocada."""
    x0, y0, x1, y1 = box
    if shadow:
        d.rounded_rectangle([x0 + shadow, y0 + shadow, x1 + shadow, y1 + shadow],
                            radius=radius, fill=INK)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=INK, width=border)


def blue_grid(img, step=44, alpha=13):
    """Malha azul de fundo — o mesmo motivo do hero do site."""
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(0, w, step):
        d.line([x, 0, x, h], fill=BLUE + (alpha,), width=1)
    for y in range(0, h, step):
        d.line([0, y, w, y], fill=BLUE + (alpha,), width=1)
    img.alpha_composite(layer)


def sticker(img, text, accent, cx, cy, angle=-8):
    """Selo girado, como os stickers do hero. Rotacionado fora e colado depois."""
    f = font(GROTESK_BOLD, 26)
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    tw = tracked_width(tmp, text, f, 0.06)
    pad_x, pad_y = 26, 16
    w, h = int(tw + pad_x * 2), int(f.size + pad_y * 2)
    pill = Image.new("RGBA", (w + SHADOW + 8, h + SHADOW + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(pill)
    hard_box(d, [4, 4, 4 + w, 4 + h], accent, shadow=9, radius=10)
    tracked(d, (4 + pad_x, 4 + pad_y - 2), text, f, on(accent), tracking=0.06)
    pill = pill.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(pill, (int(cx - pill.width / 2), int(cy - pill.height / 2)))


def chips(img, items, x, y, accent):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(GROTESK_MED, 25)
    pad_x, gap, hgt = 20, 14, 50
    fills = [accent, PAPER, PAPER, CREAM, PAPER]
    for i, item in enumerate(items):
        tw = d.textlength(item, font=f)
        fill = fills[i % len(fills)]
        hard_box(d, [x, y, x + tw + pad_x * 2, y + hgt], fill, shadow=6, radius=8)
        d.text((x + pad_x, y + hgt / 2 + 1), item, font=f, fill=on(fill), anchor="lm")
        x += tw + pad_x * 2 + gap
    img.alpha_composite(layer)


def card(name, title, subtitle, tech, accent, badge, size=(1280, 640),
         eyebrow="github.com/cauelimsia"):
    w, h = size
    img = Image.new("RGBA", (w, h), CREAM + (255,))
    blue_grid(img)

    d = ImageDraw.Draw(img)
    m = round(h * 0.075)                      # margem externa
    hard_box(d, [m, m, w - m - SHADOW, h - m - SHADOW], PAPER)

    pad = m + round(h * 0.062)
    col = int(w * 0.66) - pad

    # eyebrow com marcador quadrado chapado
    f_eye = font(GROTESK_MED, 22)
    sq = 15
    ey = pad + 6
    d.rectangle([pad, ey, pad + sq, ey + sq], fill=accent, outline=INK, width=2)
    tracked(d, (pad + sq + 14, ey - 3), eyebrow.upper(), f_eye, TEXT, tracking=0.11)

    # os chips ancoram no rodape; o bloco de texto e centrado no que sobra,
    # senao o card fica pesado em cima com um vao morto no meio
    chips_y = h - pad - 50
    f_title = fit_tracked(d, title, GROTESK_BOLD, round(h * 0.135), col, -0.035)
    f_sub = font(INTER, max(20, round(h * 0.039)))
    sub_lines = wrap(d, subtitle, f_sub, col)[:3]

    gap_rule = round(h * 0.030)
    gap_sub = round(h * 0.048)
    line_h = round(f_sub.size * 1.55)
    block_h = f_title.size * 1.12 + gap_rule + 9 + gap_sub + line_h * len(sub_lines)

    region_top = ey + sq + round(h * 0.040)
    region_bottom = chips_y - round(h * 0.045)
    ty = region_top + max((region_bottom - region_top - block_h) / 2, 0)

    # titulo: Space Grotesk 700 com tracking negativo, como o display do site
    tracked(d, (pad, ty), title, f_title, INK, tracking=-0.035)

    # barra chapada no lugar da regua fina
    ry = ty + f_title.size * 1.12 + gap_rule
    d.rectangle([pad, ry, pad + 92, ry + 9], fill=accent, outline=INK, width=2)

    y = ry + 9 + gap_sub
    for line in sub_lines:
        d.text((pad, y), line, font=f_sub, fill=MUTED, anchor="la")
        y += line_h

    chips(img, tech, pad, chips_y, accent)

    if badge:
        sticker(img, badge, accent, w - m - round(w * 0.13), m + round(h * 0.20))

    path = os.path.join(OUT, f"{name}.png")
    img.convert("RGB").save(path, "PNG", optimize=True)
    return path


# A paleta e fixa (azul/lime/coral). O que varia por repo e qual acento lidera e o selo,
# entao os cards continuam sendo obviamente da mesma familia.
CARDS = [
    ("pront-saude-digital", "Pront.",
     "SaaS multi-tenant de saúde digital. O isolamento entre clínicas está nas policies do Postgres, não na aplicação.",
     ["Next.js 14", "TypeScript", "Supabase", "RLS"], BLUE, "SAAS"),

    ("surebet-api", "surebet-api",
     "Motor de arbitragem esportiva como função pura, e um worker que reconcilia estado em vez de acumular.",
     ["TypeScript", "Node.js", "pnpm", "Postgres"], LIME, "OPEN SOURCE"),

    ("redecorr-apresentacao", "RedeCORR",
     "Deck institucional em WebGL: 2.800 partículas que mudam de formação conforme a narrativa.",
     ["three.js", "WebGL", "JavaScript"], BLUE, "WEBGL"),

    ("plano-a-apresentacao", "Plano A",
     "Engine de slides onde o conteúdo é dado, não marcação: o index.html tem 44 linhas.",
     ["JavaScript", "HTML", "CSS"], CORAL, "SEM BUILD"),

    ("presentations", "Nutrição & Estilo de Vida",
     "Deck data-driven em ES modules: cada slide é um objeto, e o layout é derivado dele.",
     ["ES Modules", "HTML", "CSS"], CORAL, "DATA-DRIVEN"),

    ("trends-marketing", "Trends do Dia",
     "O que está em alta no Google, TikTok e Instagram — já virado em pauta de conteúdo.",
     ["HTML", "CSS", "Pages"], LIME, "DIÁRIO"),

    ("cauelimsia", "Cauê Lima",
     "Desenvolvedor full-stack. Levo produto do schema ao domínio no ar.",
     ["TypeScript", "Next.js", "Postgres", "Node.js"], BLUE, "FULL-STACK"),
]

if __name__ == "__main__":
    for args in CARDS:
        print("card:", card(*args))

    print("banner:", card(
        "banner-perfil", "Cauê Lima",
        "Dev full-stack — do schema ao domínio no ar.",
        ["TypeScript", "Next.js", "Postgres", "Supabase", "Docker"],
        BLUE, "MANAUS · REMOTO", size=(1280, 460),
        eyebrow="disponível para contratação",
    ))

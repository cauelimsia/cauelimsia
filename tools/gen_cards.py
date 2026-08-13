"""Gera os social previews (1280x640) e o banner de perfil (1280x360).

Identidade compartilhada: fundo escuro em gradiente, malha de pontos, e uma nuvem
de particulas do lado direito que ecoa o organismo CORE5 do deck da RedeCORR.
Cada repo tem uma cor de acento propria, mas a composicao e a mesma — os cards
precisam ler como familia quando aparecem juntos.
"""
import math
import os
import random
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(BASE, "fonts")
OUT = os.path.join(BASE, "cards")
os.makedirs(OUT, exist_ok=True)
os.makedirs(FONTS, exist_ok=True)

# Poppins e a familia de todas as marcas — baixada na primeira execucao (OFL).
POPPINS = {
    "Poppins-Regular.ttf": "https://fonts.gstatic.com/s/poppins/v24/pxiEyp8kv8JHgFVrFJA.ttf",
    "Poppins-SemiBold.ttf": "https://fonts.gstatic.com/s/poppins/v24/pxiByp8kv8JHgFVrLEj6V1s.ttf",
    "Poppins-ExtraBold.ttf": "https://fonts.gstatic.com/s/poppins/v24/pxiByp8kv8JHgFVrLDD4V1s.ttf",
}
for _name, _url in POPPINS.items():
    _dest = os.path.join(FONTS, _name)
    if not os.path.exists(_dest):
        print("baixando", _name)
        urllib.request.urlretrieve(_url, _dest)

REGULAR = os.path.join(FONTS, "Poppins-Regular.ttf")
SEMI = os.path.join(FONTS, "Poppins-SemiBold.ttf")
XBOLD = os.path.join(FONTS, "Poppins-ExtraBold.ttf")

BG_TOP = (7, 11, 22)
BG_BOTTOM = (13, 20, 38)
INK = (255, 255, 255)
MUTED = (139, 148, 168)


def font(path, size):
    return ImageFont.truetype(path, size)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w, h):
    img = Image.new("RGB", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        px[0, y] = tuple(
            round(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)
        )
    return img.resize((w, h), Image.BICUBIC)


def dot_grid(img, step=34, alpha=10):
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step, h, step):
        for x in range(step, w, step):
            d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 255, 255, alpha))
    img.alpha_composite(layer)


def glow(img, cx, cy, radius, rgb, strength=64):
    """Halo radial suave atras da nuvem de particulas."""
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 26
    for i in range(steps, 0, -1):
        r = radius * i / steps
        a = int(strength * (1 - i / steps) ** 2.2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgb + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    img.alpha_composite(layer)


def particles(img, cx, cy, spread, rgb, count=520, seed=7):
    """Nuvem gaussiana de pontos — a assinatura visual, vinda do organismo CORE5."""
    rnd = random.Random(seed)
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        ang = rnd.uniform(0, math.tau)
        # raiz da uniforme deixa o miolo mais denso que a borda
        rad = spread * math.sqrt(rnd.random()) * rnd.uniform(0.55, 1.0)
        x = cx + math.cos(ang) * rad
        y = cy + math.sin(ang) * rad * 0.92
        if not (-20 < x < w + 20 and -20 < y < h + 20):
            continue
        falloff = 1 - min(rad / spread, 1)
        size = rnd.uniform(1.1, 3.4) * (0.55 + falloff)
        a = int(rnd.uniform(70, 235) * (0.3 + 0.7 * falloff))
        d.ellipse([x - size, y - size, x + size, y + size], fill=rgb + (a,))
    img.alpha_composite(layer)


def fit(draw, text, path, start, max_w, min_size=30):
    """Diminui a fonte ate o texto caber na largura disponivel."""
    size = start
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 2
    return font(path, min_size)


def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def lighten(rgb, amount=0.45):
    return tuple(round(c + (255 - c) * amount) for c in rgb)


def chips(img, items, x, y, rgb):
    """Desenhado em camada propria: ImageDraw substitui alpha em vez de mesclar,
    entao pintar direto na imagem transformaria o preenchimento translucido em bloco solido."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(SEMI, 21)
    pad_x, gap, hgt = 18, 11, 42
    ink = lighten(rgb, 0.55) + (255,)
    for item in items:
        tw = d.textlength(item, font=f)
        d.rounded_rectangle([x, y, x + tw + pad_x * 2, y + hgt], radius=hgt // 2,
                            fill=rgb + (30,), outline=rgb + (115,), width=1)
        d.text((x + pad_x, y + hgt / 2 + 1), item, font=f, fill=ink, anchor="lm")
        x += tw + pad_x * 2 + gap
    img.alpha_composite(layer)


def card(name, title, subtitle, tech, accent, size=(1280, 640), eyebrow="github.com/cauelimsia"):
    w, h = size
    rgb = hex_rgb(accent)
    img = gradient(w, h).convert("RGBA")

    glow(img, w * 0.78, h * 0.46, h * 0.62, rgb, strength=58)
    dot_grid(img)
    particles(img, w * 0.78, h * 0.46, h * 0.44, rgb, count=560, seed=abs(hash(name)) % 9999)

    d = ImageDraw.Draw(img)
    # metricas proporcionais a altura: o mesmo layout serve card 2:1 e banner baixo
    pad = round(h * 0.134)
    col = int(w * 0.60) - pad
    title_size = round(h * 0.122)
    sub_size = max(21, round(h * 0.042))
    line_h = round(sub_size * 1.40)

    # barra de acento na borda esquerda
    d.rectangle([0, 0, 7, h], fill=rgb + (255,))

    f_eye = font(SEMI, max(16, round(h * 0.031)))
    d.text((pad, h * 0.185), eyebrow.upper(), font=f_eye, fill=lighten(rgb, 0.25) + (240,), anchor="ls")

    f_title = fit(d, title, XBOLD, title_size, col, min_size=round(title_size * 0.52))
    title_y = h * 0.185 + round(h * 0.047)
    d.text((pad, title_y), title, font=f_title, fill=INK, anchor="la")

    # regua fina separando titulo do subtitulo
    rule_y = title_y + f_title.size * 1.34
    d.line([pad, rule_y, pad + 66, rule_y], fill=rgb + (200,), width=3)

    f_sub = font(REGULAR, sub_size)
    y = rule_y + round(h * 0.041)
    for line in wrap(d, subtitle, f_sub, col)[:3]:
        d.text((pad, y), line, font=f_sub, fill=MUTED, anchor="la")
        y += line_h

    # ancora os chips no rodape, mas nunca por cima do subtitulo
    chips(img, tech, pad, max(y + 20, h - pad - 42), rgb)

    path = os.path.join(OUT, f"{name}.png")
    img.convert("RGB").save(path, "PNG", optimize=True)
    return path


CARDS = [
    ("pront-saude-digital", "Pront.",
     "SaaS multi-tenant de saúde digital. O isolamento entre clínicas está nas policies do Postgres, não na aplicação.",
     ["Next.js 14", "TypeScript", "Supabase", "RLS"], "#2DD4A7"),

    ("surebet-api", "surebet-api",
     "Motor de arbitragem esportiva como função pura, e um worker que reconcilia estado em vez de acumular.",
     ["TypeScript", "Node.js", "pnpm", "Postgres", "Vitest"], "#38BDF8"),

    ("redecorr-apresentacao", "RedeCORR · CORE5®",
     "Deck institucional em WebGL: 2.800 partículas que mudam de formação conforme a narrativa.",
     ["three.js", "WebGL", "JavaScript"], "#4C8DFF"),

    ("plano-a-apresentacao", "Plano A · GoCare",
     "Engine de slides onde o conteúdo é dado, não marcação: o index.html tem 44 linhas.",
     ["JavaScript", "HTML", "CSS"], "#FF3D71"),

    ("presentations", "Nutrição & Estilo de Vida",
     "Deck data-driven em ES modules: cada slide é um objeto, e o layout é derivado dele.",
     ["ES Modules", "HTML", "CSS"], "#F472B6"),

    ("trends-marketing", "Trends do Dia",
     "O que está em alta no Google, TikTok e Instagram — já virado em pauta de conteúdo.",
     ["HTML", "CSS", "GitHub Pages"], "#FF6B3D"),

    ("cauelimsia", "Cauê Lima",
     "Desenvolvedor full-stack. Levo produto do schema ao domínio no ar.",
     ["TypeScript", "Next.js", "Postgres", "Node.js"], "#125CFE"),
]

if __name__ == "__main__":
    for args in CARDS:
        print("card:", card(*args))

    # banner do perfil — mesma identidade, faixa mais baixa
    print("banner:", card(
        "banner-perfil", "Cauê Lima",
        "Dev full-stack — do schema ao domínio no ar.",
        ["TypeScript", "Next.js", "Postgres", "Supabase", "Docker"],
        "#125CFE", size=(1280, 440), eyebrow="Manaus, AM · disponível para remoto",
    ))

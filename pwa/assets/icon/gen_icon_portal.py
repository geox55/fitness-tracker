"""Генератор иконки в стиле игры Portal (Aperture Science).

Тёмный фон + два светящихся овальных портала (синий и оранжевый —
как портальная пушка в игре, и заодно фирменные цвета приложения).
Дизайн оригинальный, «по мотивам» — без копирования логотипа Valve.

Запуск:  python3 pwa/assets/icon/gen_icon_portal.py
Результат: app_icon_portal.png (512×512) + копия в ~/Downloads.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SIZE = 512
SS = 4  # суперсэмплинг для гладких краёв
HERE = Path(__file__).resolve().parent


def _portal(size, color, *, w, h):
    """Светящийся овальный портал на прозрачном слое (по центру)."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    cx, cy = size / 2, size / 2

    # 1) Внешнее свечение — заливка эллипса, сильное размытие.
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
               fill=color + (180,))
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.05))
    layer = Image.alpha_composite(layer, glow)

    # 2) Кольцо портала — несколько обводок от насыщенной к белой сердцевине.
    d = ImageDraw.Draw(layer)
    rings = [
        (color + (255,), int(size * 0.055)),          # толстый цветной обод
        (_lighten(color, 0.5) + (255,), int(size * 0.030)),
        ((255, 255, 255, 255), int(size * 0.012)),     # белая сердцевина
    ]
    for col, width in rings:
        d.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2],
                  outline=col, width=width)

    # 3) Тёмная «глубина» внутри портала с лёгким цветным отливом.
    inner = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    idr = ImageDraw.Draw(inner)
    pad = int(size * 0.075)
    idr.ellipse([cx - w / 2 + pad, cy - h / 2 + pad,
                 cx + w / 2 - pad, cy + h / 2 - pad],
                fill=_darken(color, 0.72) + (150,))
    inner = inner.filter(ImageFilter.GaussianBlur(size * 0.012))
    layer = Image.alpha_composite(layer, inner)
    return layer


def _lighten(c, t):
    return tuple(int(c[i] + (255 - c[i]) * t) for i in range(3))


def _darken(c, t):
    return tuple(int(c[i] * (1 - t)) for i in range(3))


def _rotate_paste(base, layer, angle):
    rot = layer.rotate(angle, resample=Image.BICUBIC, center=(base.width / 2,
                                                              base.height / 2))
    return Image.alpha_composite(base, rot)


def build():
    s = SIZE * SS

    # Фон — тёмный радиальный градиент Aperture (графит → почти чёрный).
    bg = Image.new("RGBA", (s, s), (0, 0, 0, 255))
    px = bg.load()
    cx, cy = s / 2, s / 2
    maxd = (cx ** 2 + cy ** 2) ** 0.5
    top = (0x1B, 0x24, 0x33)   # графитово-синий центр
    edge = (0x07, 0x0A, 0x10)  # почти чёрные края
    for y in range(s):
        for x in range(s):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / maxd
            px[x, y] = tuple(int(top[i] + (edge[i] - top[i]) * d) for i in range(3)) + (255,)

    blue = (0x2E, 0xA8, 0xFF)
    orange = (0xFF, 0x8A, 0x14)

    # Два вертикальных овала-портала, разнесённых и наклонённых навстречу.
    pw, ph = int(s * 0.30), int(s * 0.62)
    blue_layer = _portal(s, blue, w=pw, h=ph)
    orange_layer = _portal(s, orange, w=pw, h=ph)

    # Синий — левее и выше, наклон вправо; оранжевый — правее и ниже.
    blue_layer = blue_layer.transform(
        blue_layer.size, Image.AFFINE,
        (1, 0, int(s * 0.16), 0, 1, -int(s * 0.04)), resample=Image.BICUBIC)
    orange_layer = orange_layer.transform(
        orange_layer.size, Image.AFFINE,
        (1, 0, -int(s * 0.16), 0, 1, int(s * 0.04)), resample=Image.BICUBIC)
    bg = _rotate_paste(bg, blue_layer, 12)
    bg = _rotate_paste(bg, orange_layer, -12)

    # Лёгкий верхний глянец.
    gloss = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ggd = ImageDraw.Draw(gloss)
    ggd.ellipse([-s * 0.3, -s * 0.7, s * 1.1, s * 0.22],
                fill=(255, 255, 255, 26))
    gloss = gloss.filter(ImageFilter.GaussianBlur(s * 0.04))
    bg = Image.alpha_composite(bg, gloss)

    # Скругление углов.
    radius = int(s * 0.22)
    mask = Image.new("L", (s, s), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, s - 1, s - 1], radius=radius, fill=255)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)

    # Даунскейл до 512 (антиалиасинг).
    out = out.resize((SIZE, SIZE), Image.LANCZOS)

    dst = HERE / "app_icon_portal.png"
    out.save(dst, format="PNG")
    downloads = Path.home() / "Downloads" / "portal-icon-512-game.png"
    out.save(downloads, format="PNG")
    print(f"Wrote: {dst} ({dst.stat().st_size/1024:.0f} КБ, {SIZE}x{SIZE})")
    print(f"Wrote: {downloads}")


if __name__ == "__main__":
    build()

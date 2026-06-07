"""Генератор иконки приложения Portal (512×512, 1:1).

Мотив — суть приложения: прогноз состава тела с доверительным интервалом.
Восходящая кривая (прогноз) + расширяющийся вправо коридор (CI, который
растёт с горизонтом) на сине-оранжевом фирменном фоне с глянцевым бликом.

Запуск:  python3 pwa/assets/icon/gen_icon.py
Результат: app_icon.png (512×512) рядом + копия в ~/Downloads для загрузки.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SIZE = 512
HERE = Path(__file__).resolve().parent


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _gradient(size, top_left, bottom_right):
    """Диагональный градиент."""
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            px[x, y] = _lerp(top_left, bottom_right, t)
    return img


def build():
    # Фон — диагональный градиент: глубокий синий → яркий голубой.
    bg = _gradient(SIZE, (0x12, 0x3A, 0x6B), (0x3C, 0x9A, 0xE6)).convert("RGBA")

    draw = ImageDraw.Draw(bg)

    # --- Доверительный коридор (CI) и кривая прогноза ---
    x0, x1 = SIZE * 0.16, SIZE * 0.84
    y_base = SIZE * 0.66          # старт кривой (низ)
    amp = SIZE * 0.34             # подъём
    n = 80

    curve = []
    upper = []
    lower = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        # Плавный подъём (ease-out) — прогноз растёт.
        y = y_base - amp * (t ** 1.25)
        curve.append((x, y))
        # Коридор расширяется с горизонтом (как реальный CI).
        hw = SIZE * (0.015 + 0.085 * t)
        upper.append((x, y - hw))
        lower.append((x, y + hw))

    # Лента CI — полупрозрачная белая.
    band = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.polygon(upper + lower[::-1], fill=(255, 255, 255, 95))
    bg = Image.alpha_composite(bg, band)
    draw = ImageDraw.Draw(bg)

    # Кривая прогноза — белая, толстая, со сглаживанием.
    draw.line(curve, fill=(255, 255, 255, 255), width=18, joint="curve")

    # Точки-замеры на кривой (3 горизонта: 1/2/4 нед).
    for t in (0.0, 0.45, 1.0):
        idx = int(t * n)
        cx, cy = curve[idx]
        r = 17 if t == 1.0 else 12
        # Финальная точка — оранжевая (акцент), остальные — белые.
        if t == 1.0:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=(0xF5, 0x7C, 0x00, 255),
                         outline=(255, 255, 255, 255), width=6)
        else:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                         fill=(255, 255, 255, 255))

    # Базовая ось — тонкая полупрозрачная линия снизу.
    draw.line([(x0, y_base + SIZE * 0.11), (x1, y_base + SIZE * 0.11)],
              fill=(255, 255, 255, 90), width=5)

    # Глянцевый блик сверху (стекло).
    gloss = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    ggd = ImageDraw.Draw(gloss)
    ggd.ellipse([-SIZE * 0.3, -SIZE * 0.7, SIZE * 1.1, SIZE * 0.25],
                fill=(255, 255, 255, 38))
    gloss = gloss.filter(ImageFilter.GaussianBlur(25))
    bg = Image.alpha_composite(bg, gloss)

    # --- Скругление углов (rounded square, как у store-иконок) ---
    radius = int(SIZE * 0.22)
    mask = Image.new("L", (SIZE, SIZE), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=radius, fill=255)
    out = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)

    dst = HERE / "app_icon.png"
    out.save(dst, format="PNG")
    # Копия в Downloads — удобнее загружать в RuStore.
    downloads = Path.home() / "Downloads" / "portal-icon-512.png"
    out.save(downloads, format="PNG")
    kb = dst.stat().st_size / 1024
    print(f"Wrote: {dst} ({kb:.0f} КБ, {SIZE}x{SIZE})")
    print(f"Wrote: {downloads}")


if __name__ == "__main__":
    build()

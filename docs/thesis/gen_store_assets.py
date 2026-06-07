"""Генерация графики для карточки RuStore.

1) Витринный баннер 16:9 (1920×1080, JPG) — тёмный фон в стиле Portal,
   название, слоган, ключевые фичи и телефон-мокап со скриншотом.
2) Скриншоты для телефонов, приведённые к безопасному 9:16 (1080×1920):
   исходники 1206×2622 уже́ е, чем 9:16, поэтому вписываем без обрезки и
   добавляем боковые поля цветом фона скриншота.

Запуск:  python3 docs/thesis/gen_store_assets.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SHOTS = HERE / "screenshots"
OUT = HERE / "store"
OUT.mkdir(exist_ok=True)
DOWNLOADS = Path.home() / "Downloads"

ARIAL = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

BLUE = (0x2E, 0xA8, 0xFF)
ORANGE = (0xFF, 0x8A, 0x14)


def _font(path, size):
    return ImageFont.truetype(path, size)


def _glow(size, box, color, alpha, blur):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse(box, fill=color + (alpha,))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def _round(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.width - 1, img.height - 1],
                                           radius=radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def build_banner():
    W, H = 1920, 1080
    # Фон — вертикальный градиент графит → почти чёрный.
    bg = Image.new("RGBA", (W, H))
    px = bg.load()
    top, bot = (0x1B, 0x26, 0x38), (0x07, 0x0A, 0x10)
    for y in range(H):
        t = y / (H - 1)
        row = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
        for x in range(W):
            px[x, y] = row

    # Порталы-блики: синий слева, оранжевый справа.
    bg = Image.alpha_composite(bg, _glow((W, H), [-200, 200, 500, 950], BLUE, 90, 130))
    bg = Image.alpha_composite(bg, _glow((W, H), [1300, 100, 2050, 850], ORANGE, 70, 150))

    # Телефон-мокап справа со скриншотом главного экрана.
    shot_path = SHOTS / "03_home.png"
    if shot_path.exists():
        shot = _crop_chrome(Image.open(shot_path).convert("RGB")).convert("RGBA")
        ph_h = 900
        ph_w = int(shot.width * ph_h / shot.height)
        shot = shot.resize((ph_w, ph_h), Image.LANCZOS)
        shot = _round(shot, 46)
        # Рамка телефона.
        frame = Image.new("RGBA", (ph_w + 24, ph_h + 24), (0, 0, 0, 0))
        ImageDraw.Draw(frame).rounded_rectangle(
            [0, 0, frame.width - 1, frame.height - 1], radius=58,
            fill=(0x10, 0x16, 0x20, 255), outline=(0x33, 0x3E, 0x4E, 255), width=3)
        frame.paste(shot, (12, 12), shot)
        # Тень.
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sx, sy = W - frame.width - 150, (H - frame.height) // 2
        ImageDraw.Draw(shadow).rounded_rectangle(
            [sx + 18, sy + 26, sx + frame.width + 18, sy + frame.height + 26],
            radius=58, fill=(0, 0, 0, 150))
        shadow = shadow.filter(ImageFilter.GaussianBlur(35))
        bg = Image.alpha_composite(bg, shadow)
        bg.paste(frame, (sx, sy), frame)

    draw = ImageDraw.Draw(bg)

    # Заголовок + слоган + фичи (левая колонна).
    x = 120
    draw.text((x, 250), "Portal", font=_font(ARIAL_BOLD, 140), fill=(255, 255, 255))
    draw.text((x + 6, 415), "Прогноз состава тела", font=_font(ARIAL, 50),
              fill=(0x9E, 0xD2, 0xFF))
    draw.text((x + 6, 478), "и адаптация тренировок", font=_font(ARIAL, 50),
              fill=(0x9E, 0xD2, 0xFF))

    bullets = [
        (BLUE, "Прогноз на 1, 2 и 4 недели"),
        (BLUE, "Доверительный интервал «от и до»"),
        (ORANGE, "Умная адаптация плана"),
    ]
    by = 620
    for color, text in bullets:
        draw.ellipse([x + 6, by + 14, x + 30, by + 38], fill=color)
        draw.text((x + 52, by), text, font=_font(ARIAL, 38), fill=(0xE8, 0xEE, 0xF6))
        by += 78

    out = bg.convert("RGB")
    dst = OUT / "feature-banner-1920x1080.jpg"
    out.save(dst, "JPEG", quality=90)
    out.save(DOWNLOADS / "rustore-banner-1920x1080.jpg", "JPEG", quality=90)
    print(f"Баннер: {dst} ({dst.stat().st_size/1024:.0f} КБ)")


def _crop_chrome(im, *, light_thr=200):
    """Срезать светлые полосы сверху/снизу (строка статуса iOS и панель
    браузера). Светлой считаем строку, у которой МЕДИАННАЯ яркость высокая —
    то есть фон строки белый, даже если поверх него тёмные иконки/текст
    (адресная строка браузера). У приложения тёмная тема, поэтому контент
    даёт низкую медиану и не срезается.
    """
    g = im.convert("L")
    w, h = g.size
    cols = g.resize((48, h))  # сжать по ширине → быстрый профиль строки
    px = cols.load()

    def is_chrome(y):
        row = sorted(px[x, y] for x in range(48))
        return row[24] > light_thr  # медиана строки светлая

    top = 0
    while top < h // 2 and is_chrome(top):
        top += 1
    bottom = h - 1
    while bottom > h // 2 and is_chrome(bottom):
        bottom -= 1
    if bottom - top < h * 0.5:  # подстраховка: не срезать слишком много
        return im
    return im.crop((0, top, im.width, bottom + 1))


def build_screenshots():
    TW, TH = 1080, 1920  # целевой 9:16
    shots = sorted(SHOTS.glob("*.png"))
    sdir = OUT / "screenshots"
    sdir.mkdir(exist_ok=True)
    for p in shots:
        im = Image.open(p).convert("RGB")
        im = _crop_chrome(im)
        # Цвет полей — из верхнего-левого пикселя скриншота.
        pad_color = im.getpixel((4, 4))
        scale = min(TW / im.width, TH / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        im2 = im.resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGB", (TW, TH), pad_color)
        canvas.paste(im2, ((TW - nw) // 2, (TH - nh) // 2))
        dst = sdir / f"{p.stem}.jpg"
        canvas.save(dst, "JPEG", quality=90)
    print(f"Скриншоты 9:16: {len(shots)} шт → {sdir}")
    # Копия набора в Downloads для удобства.
    import shutil
    zip_base = DOWNLOADS / "rustore-screenshots"
    shutil.make_archive(str(zip_base), "zip", sdir)
    print(f"Архив: {zip_base}.zip")


if __name__ == "__main__":
    build_banner()
    build_screenshots()

#!/usr/bin/env python3
"""Build the 79 new visual assets for The Seamless Stay campaign."""

from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path("/Users/coong/Documents/lajora-social-30days")
PLAN = ROOT / "content-plan.json"
SOURCES = ROOT / "editorial-30-en" / "seamless-stay-sources"
OUT = ROOT / "posts" / "the-seamless-stay-100d"
PACK = ROOT / "editorial-30-en" / "seamless-stay-100d-posts"
REVISION = ROOT / "editorial-30-en" / "seamless-stay-100d-revision"

W, H = 1080, 1350
BLACK = (13, 14, 17)
WHITE = (248, 244, 235)
COBALT = (31, 64, 215)
CORAL = (255, 100, 86)
LIME = (207, 255, 63)
YELLOW = (255, 210, 27)
VIOLET = (74, 42, 144)
CYAN = (46, 199, 223)
STONE = (224, 213, 194)
PALE = (245, 233, 215)
PALETTES = [
    (COBALT, CORAL, LIME, PALE),
    (VIOLET, YELLOW, CYAN, WHITE),
    (BLACK, CORAL, LIME, STONE),
    (COBALT, YELLOW, CORAL, WHITE),
    (VIOLET, CORAL, LIME, PALE),
]

SOURCE_NAMES = [
    "arrival-portal.png",
    "hotel-courtyard.png",
    "villa-pool.png",
    "suite-geometry.png",
    "key-token.png",
    "website-pathway.png",
    "payment-rings.png",
    "welcome-desk.png",
    "room-light.png",
    "villa-facade.png",
    "service-gesture.png",
    "identity-threads.png",
]

HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"


def font(size: int, index: int = 9):
    return ImageFont.truetype(HELVETICA, size=size, index=index)


def cover(source: Image.Image, center: tuple[float, float]) -> Image.Image:
    return ImageOps.fit(
        source.convert("RGB"),
        (W, H),
        method=Image.Resampling.LANCZOS,
        centering=center,
    )


def circle(draw, x, y, radius, fill, outline=None, width=1):
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=fill,
        outline=outline,
        width=width,
    )


def route_motif(image: Image.Image, index: int, strength: int = 210) -> Image.Image:
    primary, secondary, accent, neutral = PALETTES[index % len(PALETTES)]
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    side = index % 4
    if side == 0:
        points = [(82, 1110), (260, 1010), (460, 1080), (690, 970), (970, 1030)]
    elif side == 1:
        points = [(930, 200), (800, 350), (860, 520), (700, 670), (830, 820)]
    elif side == 2:
        points = [(120, 250), (300, 390), (220, 580), (420, 730), (280, 900)]
    else:
        points = [(930, 1120), (760, 970), (830, 800), (650, 670), (760, 500)]
    draw.line(points, fill=accent + (strength,), width=6, joint="curve")
    for n, (x, y) in enumerate(points):
        if n == len(points) - 1 or n % 2 == index % 2:
            circle(draw, x, y, 14 if n % 3 else 19, primary + (235,))
        else:
            circle(draw, x, y, 12, (0, 0, 0, 0), neutral + (220,), 5)
    ring_x = 160 + (index * 137) % 760
    ring_y = 180 + (index * 83) % 860
    draw.ellipse((ring_x - 44, ring_y - 44, ring_x + 44, ring_y + 44), outline=secondary + (strength,), width=7)
    return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")


def image_variant(source: Image.Image, index: int) -> Image.Image:
    centers = [(0.38, 0.48), (0.62, 0.5), (0.5, 0.38), (0.5, 0.62), (0.44, 0.54)]
    image = cover(source, centers[index % len(centers)])
    image = ImageEnhance.Color(image).enhance(0.9 + (index % 4) * 0.08)
    image = ImageEnhance.Contrast(image).enhance(0.96 + (index % 3) * 0.04)
    if index % 7 == 3:
        image = ImageOps.mirror(image)
    if index % 9 == 5:
        tint = Image.new("RGBA", (W, H), PALETTES[index % len(PALETTES)][0] + (20,))
        image = Image.alpha_composite(image.convert("RGBA"), tint).convert("RGB")
    return route_motif(image, index, 175)


def object_post(source: Image.Image, index: int) -> Image.Image:
    primary, secondary, accent, neutral = PALETTES[index % len(PALETTES)]
    background = cover(source, (0.5, 0.5)).filter(ImageFilter.GaussianBlur(3.2))
    background = ImageEnhance.Brightness(background).enhance(0.62)
    canvas = background.convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    mode = index % 6
    if mode == 0:
        for box, color, width in [
            ((170, 230, 910, 1060), primary, 28),
            ((260, 330, 820, 960), secondary, 22),
            ((360, 430, 720, 860), accent, 18),
        ]:
            draw.rounded_rectangle(box, radius=150, outline=color + (235,), width=width)
        circle(draw, 540, 650, 86, neutral + (235,))
        circle(draw, 540, 650, 42, primary + (255,))
    elif mode == 1:
        draw.ellipse((110, 210, 970, 1170), fill=neutral + (65,), outline=accent + (130,), width=6)
        draw.rounded_rectangle((245, 330, 835, 1030), radius=125, fill=primary + (225,))
        draw.rounded_rectangle((310, 410, 770, 925), radius=105, fill=secondary + (245,))
        draw.ellipse((402, 550, 678, 826), fill=accent + (245,))
        draw.ellipse((455, 603, 625, 773), fill=neutral + (215,), outline=primary + (255,), width=12)
        draw.line((540, 290, 540, 410), fill=neutral + (210,), width=12)
        circle(draw, 540, 270, 28, accent + (255,))
    elif mode == 2:
        draw.ellipse((170, 260, 910, 1000), fill=primary + (230,))
        draw.ellipse((280, 370, 800, 890), fill=secondary + (240,))
        draw.ellipse((385, 475, 695, 785), fill=accent + (245,))
        draw.ellipse((448, 538, 632, 722), fill=neutral + (230,), outline=primary + (255,), width=11)
        draw.arc((190, 180, 890, 1110), 180, 360, fill=neutral + (220,), width=18)
        draw.line((540, 1000, 540, 1140), fill=accent + (230,), width=11)
    elif mode == 3:
        draw.rounded_rectangle((210, 220, 870, 1120), radius=210, fill=primary + (225,))
        draw.rounded_rectangle((335, 390, 745, 980), radius=160, fill=neutral + (235,))
        draw.rounded_rectangle((430, 510, 650, 850), radius=110, fill=secondary + (245,))
        draw.ellipse((480, 600, 600, 720), fill=accent + (255,))
        draw.arc((100, 210, 980, 1180), 25, 155, fill=accent + (220,), width=13)
    elif mode == 4:
        draw.ellipse((250, 300, 830, 880), fill=neutral + (235,), outline=primary + (255,), width=17)
        draw.ellipse((370, 420, 710, 760), fill=secondary + (245,))
        draw.rounded_rectangle((450, 730, 630, 1030), radius=85, fill=accent + (245,))
        draw.line((540, 250, 540, 420), fill=primary + (245,), width=11)
        circle(draw, 540, 215, 38, primary + (255,))
        draw.arc((190, 160, 890, 1120), 190, 335, fill=neutral + (230,), width=10)
    else:
        points = [(245, 420), (540, 250), (830, 420), (760, 850), (320, 850)]
        for a, b in zip(points, points[1:] + points[:1]):
            draw.line((a, b), fill=neutral + (210,), width=10)
        for n, (x, y) in enumerate(points):
            circle(draw, x, y, 90, [primary, secondary, accent, neutral, primary][n] + (235,))
            circle(draw, x, y, 40, BLACK + (150,), outline=neutral + (220,), width=7)
    canvas = Image.alpha_composite(canvas, overlay).convert("RGB")
    return route_motif(canvas, index + 2, 130)


def fit_title(draw: ImageDraw.ImageDraw, title: str, max_width: int = 850, max_lines: int = 3):
    """Wrap and size headlines by rendered width, not character count."""
    words = title.upper().split()
    for size in range(176, 71, -4):
        title_font = font(size, 9)
        lines: list[str] = []
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if line and draw.textlength(candidate, font=title_font) > max_width:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        if len(lines) <= max_lines and all(draw.textlength(line, font=title_font) <= max_width for line in lines):
            # Avoid an orphaned one-word middle line when a smaller display size
            # gives the headline a cleaner editorial rhythm.
            if len(lines) > 1 and any(len(line.split()) == 1 for line in lines) and size > 80:
                continue
            return lines, title_font
    fallback = font(72, 9)
    return [" ".join(words)], fallback


def type_post(item: dict, index: int) -> Image.Image:
    primary, secondary, accent, neutral = PALETTES[index % len(PALETTES)]
    canvas = Image.new("RGB", (W, H), neutral)
    draw = ImageDraw.Draw(canvas)
    mode = index % 7
    if mode == 0:
        draw.rectangle((0, 0, W, H), fill=BLACK)
        draw.rectangle((72, 235, 1008, 1060), fill=primary)
        draw.rectangle((0, 0, 230, H), fill=secondary)
        text_fill = neutral
        accent_fill = accent
    elif mode == 1:
        draw.rectangle((0, 0, W, H), fill=primary)
        draw.ellipse((-220, -180, 700, 740), fill=neutral)
        draw.rounded_rectangle((70, 250, 1010, 760), radius=44, fill=BLACK)
        draw.rectangle((86, 650, 990, 1050), fill=BLACK)
        text_fill = neutral
        accent_fill = secondary
    elif mode == 2:
        draw.rectangle((0, 0, W, H), fill=neutral)
        draw.rectangle((0, 0, W, 170), fill=primary)
        draw.rectangle((0, 1120, W, H), fill=accent)
        text_fill = BLACK
        accent_fill = secondary
    elif mode == 3:
        draw.rectangle((0, 0, W, H), fill=secondary)
        for x in range(60, 1020, 110):
            draw.line((x, 80, x + 320, 1230), fill=primary, width=6)
        draw.rounded_rectangle((70, 250, 1010, 1110), radius=52, fill=neutral)
        text_fill = BLACK
        accent_fill = primary
    elif mode == 4:
        draw.rectangle((0, 0, W, H), fill=BLACK)
        draw.rectangle((70, 350, 1010, 1110), fill=secondary)
        draw.rectangle((70, 350, 1010, 455), fill=primary)
        text_fill = neutral
        accent_fill = accent
    elif mode == 5:
        draw.rectangle((0, 0, 540, H), fill=primary)
        draw.rectangle((540, 0, W, H), fill=secondary)
        draw.rounded_rectangle((90, 250, 990, 1090), radius=70, fill=neutral)
        draw.rectangle((90, 250, 990, 350), fill=accent)
        text_fill = BLACK
        accent_fill = primary
    else:
        draw.rectangle((0, 0, W, H), fill=VIOLET)
        draw.ellipse((-210, -160, 660, 700), fill=primary)
        draw.rounded_rectangle((70, 250, 1010, 610), radius=40, fill=BLACK)
        draw.rounded_rectangle((76, 570, 1000, 1080), radius=34, fill=BLACK)
        text_fill = neutral
        accent_fill = LIME

    canvas = route_motif(canvas, index + 3, 205)
    draw = ImageDraw.Draw(canvas)
    lines, title_font = fit_title(draw, item["title"])
    y = 390 if mode in {0, 1, 4} else 330
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        draw.text((86, y), line, font=title_font, fill=text_fill)
        y += bbox[3] - bbox[1] + 36
    draw.line((86, 1145, 830, 1145), fill=accent_fill, width=13)
    draw.text((86, 1175), "THE SEAMLESS STAY", font=font(40, 10), fill=accent_fill)
    return canvas


def mixed_post(source: Image.Image, item: dict, index: int) -> Image.Image:
    image = image_variant(source, index)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    primary, secondary, accent, neutral = PALETTES[index % len(PALETTES)]
    draw.rounded_rectangle((72, 72, 510, 176), radius=52, fill=BLACK + (185,))
    draw.text((108, 96), "THE SEAMLESS STAY", font=font(37, 10), fill=neutral + (255,))
    small = " / ".join(item["chapter"].upper().split()[:3])
    draw.text((86, 1195), small, font=font(32, 10), fill=neutral + (240,))
    return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")


def save(image: Image.Image, item: dict):
    post_id = int(item["id"])
    jpg = f"day-{post_id:03}.jpg"
    png = f"day-{post_id:03}.png"
    image.convert("RGB").save(OUT / jpg, quality=92, subsampling=0)
    image.convert("RGB").save(PACK / png, compress_level=1)


def contact_sheet(items: list[dict]):
    REVISION.mkdir(parents=True, exist_ok=True)
    thumb_w, thumb_h, gap = 180, 225, 12
    cols = 5
    rows = math.ceil(len(items) / cols)
    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, rows * (thumb_h + 30) + (rows + 1) * gap), BLACK)
    draw = ImageDraw.Draw(sheet)
    label_font = font(18, 1)
    for pos, item in enumerate(items):
        col, row = pos % cols, pos // cols
        x, y = gap + col * (thumb_w + gap), gap + row * (thumb_h + 30 + gap)
        image = Image.open(OUT / f"day-{int(item['id']):03}.jpg").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        sheet.paste(image, (x, y))
        draw.text((x, y + thumb_h + 4), str(item["id"]), font=label_font, fill=WHITE)
    sheet.save(REVISION / "contact-sheet-31-109.jpg", quality=90)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PACK.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text())
    items = [item for item in plan if int(item["id"]) >= 31]
    if len(items) != 79:
        raise ValueError(f"Expected 79 new plan items, got {len(items)}")
    source_images = [Image.open(SOURCES / name).convert("RGB") for name in SOURCE_NAMES]
    for index, item in enumerate(items):
        source = source_images[(index * 5 + index // 8) % len(source_images)]
        if item["format"] == "type":
            image = type_post(item, index)
        elif item["format"] == "object":
            image = object_post(source, index)
        elif item["format"] == "mixed":
            image = mixed_post(source, item, index)
        else:
            image = image_variant(source, index)
        save(image, item)
    contact_sheet(items)
    print(f"Built {len(items)} The Seamless Stay assets in {OUT}")


if __name__ == "__main__":
    main()

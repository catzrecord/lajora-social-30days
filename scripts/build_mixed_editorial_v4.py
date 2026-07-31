#!/usr/bin/env python3
"""Build a varied, case-study-style editorial feed for Lajora."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path("/Users/coong/Documents/lajora-social-30days")
PACK = ROOT / "editorial-v4-mixed"
OUT = PACK / "posts"
NEW_BG = PACK / "backgrounds"
OLD_BG = ROOT / "editorial-30" / "backgrounds"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
CREAM = (247, 241, 229)
BLACK = (15, 16, 16)
COBALT = (31, 58, 211)
CORAL = (255, 102, 90)
LIME = (195, 244, 92)
YELLOW = (255, 222, 43)
CYAN = (53, 197, 222)
PINK = (245, 118, 187)

CONDENSED = "/System/Library/Fonts/Avenir Next Condensed.ttc"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"

BACKGROUND_MAP = {
    1: NEW_BG / "new-01-chrome-ribbon.png",
    2: None,
    3: NEW_BG / "new-02-blank-billboard.png",
    4: NEW_BG / "new-03-paper-collage.png",
    5: OLD_BG / "bg-13-hospitality.png",
    6: NEW_BG / "new-04-blank-vessels.png",
    7: None,
    8: NEW_BG / "new-05-studio-bts.png",
    9: NEW_BG / "new-06-jelly-shore.png",
    10: NEW_BG / "new-07-kinetic-objects.png",
    11: OLD_BG / "bg-11-detail.png",
    12: NEW_BG / "new-08-woven-room.png",
    13: OLD_BG / "bg-02-character.png",
    14: NEW_BG / "new-09-hand-sun-collage.png",
    15: OLD_BG / "bg-04-positioning.png",
    16: None,
    17: NEW_BG / "new-10-surreal-table.png",
    18: OLD_BG / "bg-06-personality.png",
    19: NEW_BG / "new-11-glass-portrait.png",
    20: OLD_BG / "bg-14-authenticity.png",
    21: NEW_BG / "new-12-floating-tags.png",
    22: OLD_BG / "bg-07-emotion.png",
    23: OLD_BG / "bg-01-attention.png",
    24: OLD_BG / "bg-03-distinction.png",
    25: OLD_BG / "bg-05-voice.png",
    26: OLD_BG / "bg-08-memory.png",
    27: OLD_BG / "bg-09-rhythm.png",
    28: OLD_BG / "bg-10-visual-identity.png",
    29: OLD_BG / "bg-12-community.png",
    30: OLD_BG / "bg-15-trust.png",
}

# Deliberately varied like a creative-agency feed: case-study frame, art object,
# studio process, typographic statement, outdoor installation, and collage.
LAYOUTS = [
    "bottom_caption",
    "type_only",
    "side_caption",
    "museum_label",
    "image_card",
    "top_strip",
    "type_only",
    "small_caption",
    "frame",
    "split_vertical",
    "circle_window",
    "bottom_caption",
    "small_caption",
    "image_card",
    "top_strip",
    "type_only",
    "museum_label",
    "frame",
    "side_caption",
    "bottom_caption",
    "small_caption",
    "split_vertical",
    "image_card",
    "circle_window",
    "frame",
    "top_strip",
    "museum_label",
    "side_caption",
    "bottom_caption",
    "small_caption",
]

PALETTES = [
    (CREAM, BLACK, COBALT),
    (BLACK, CREAM, LIME),
    (YELLOW, BLACK, CORAL),
    (CREAM, BLACK, CORAL),
    (COBALT, CREAM, LIME),
    (PINK, BLACK, YELLOW),
    (CYAN, BLACK, CREAM),
    (BLACK, CREAM, CORAL),
]


def font(size: int, family: str = "condensed", style: str = "heavy") -> ImageFont.FreeTypeFont:
    if family == "condensed":
        index = 8 if style == "heavy" else 7
        return ImageFont.truetype(CONDENSED, size, index=index)
    if family == "helvetica":
        index = 4 if style == "heavy" else 10
        return ImageFont.truetype(HELVETICA, size, index=index)
    index = 8 if style == "heavy" else 5
    return ImageFont.truetype(AVENIR, size, index=index)


def cover(path: Path, box=(0, 0, W, H)) -> Image.Image:
    x1, y1, x2, y2 = box
    width, height = x2 - x1, y2 - y1
    image = Image.open(path).convert("RGB")
    ratio = max(width / image.width, height / image.height)
    resized = image.resize(
        (round(image.width * ratio), round(image.height * ratio)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def text_width(draw: ImageDraw.ImageDraw, value: str, face: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), value, font=face)
    return box[2] - box[0]


def wrap_title(
    draw: ImageDraw.ImageDraw,
    title: str,
    max_width: int,
    max_lines: int = 3,
    start_size: int = 144,
    min_size: int = 48,
) -> tuple[list[str], ImageFont.FreeTypeFont]:
    words = title.upper().split()
    for size in range(start_size, min_size - 1, -2):
        face = font(size)
        lines: list[str] = []
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if not line or text_width(draw, candidate, face) <= max_width:
                line = candidate
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        if len(lines) <= max_lines and all(
            text_width(draw, line, face) <= max_width for line in lines
        ):
            return lines, face
    return [" ".join(words)], font(min_size)


def draw_title(
    draw: ImageDraw.ImageDraw,
    title: str,
    xy: tuple[int, int],
    max_width: int,
    fill,
    max_lines: int = 3,
    start_size: int = 144,
    align: str = "left",
) -> tuple[int, int]:
    lines, face = wrap_title(draw, title, max_width, max_lines, start_size)
    x, y = xy
    line_height = round(face.size * 0.83)
    for line in lines:
        width = text_width(draw, line, face)
        tx = x if align == "left" else x + max_width - width if align == "right" else x + (max_width - width) // 2
        draw.text((tx, y), line, font=face, fill=fill, stroke_width=0)
        y += line_height
    return face.size, y


def add_label(draw: ImageDraw.ImageDraw, value: str, xy: tuple[int, int], fill) -> None:
    label = value.upper()
    face = font(19, family="avenir", style="medium")
    draw.text(xy, label, font=face, fill=fill)


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *size), radius=radius, fill=255)
    return mask


def paste_rounded(canvas: Image.Image, image: Image.Image, xy: tuple[int, int], radius: int) -> None:
    canvas.paste(image, xy, rounded_mask(image.size, radius))


def type_only(index: int, item: dict, palette) -> Image.Image:
    background, ink, accent = palette
    image = Image.new("RGB", (W, H), background)
    draw = ImageDraw.Draw(image)
    if index == 2:
        draw.ellipse((610, 80, 1160, 630), fill=accent)
        draw.rectangle((0, 960, 1080, 1350), fill=CORAL)
        draw_title(draw, item["title"], (120, 260), 720, ink, start_size=164)
        add_label(draw, item["pillar"], (120, 1110), BLACK)
    elif index == 7:
        for radius, color in [(540, CORAL), (400, CREAM), (260, COBALT), (120, LIME)]:
            box = (540 - radius // 2, 260 - radius // 2, 540 + radius // 2, 260 + radius // 2)
            draw.ellipse(box, outline=color, width=34)
        draw_title(draw, item["title"], (108, 680), 864, CREAM, start_size=156, align="center")
        add_label(draw, item["pillar"], (108, 1130), LIME)
    else:
        draw.rectangle((0, 0, 210, H), fill=LIME)
        draw.polygon([(210, 0), (1080, 0), (1080, 420), (210, 780)], fill=CREAM)
        draw_title(draw, item["title"], (280, 250), 690, BLACK, start_size=168)
        add_label(draw, item["pillar"], (280, 1090), CORAL)
    return image


def render(index: int, item: dict) -> Image.Image:
    palette = PALETTES[(index - 1) % len(PALETTES)]
    background, ink, accent = palette
    layout = LAYOUTS[index - 1]
    bg_path = BACKGROUND_MAP[index]
    if layout == "type_only":
        return type_only(index, item, palette)

    bg = cover(bg_path)
    bg = ImageEnhance.Color(bg).enhance(1.03)
    image = bg.copy()
    draw = ImageDraw.Draw(image, "RGBA")

    if layout == "bottom_caption":
        draw.rectangle((0, 760, W, H), fill=(*background, 244))
        draw_title(draw, item["title"], (108, 815), 864, ink, start_size=132)
        add_label(draw, item["pillar"], (108, 1185), accent)

    elif layout == "side_caption":
        side = 520 if index % 2 else 560
        if index % 2:
            draw.rectangle((0, 0, side, H), fill=(*background, 242))
            draw_title(draw, item["title"], (108, 300), 330, ink, start_size=106, max_lines=5)
            add_label(draw, item["pillar"], (108, 1080), accent)
        else:
            draw.rectangle((side, 0, W, H), fill=(*background, 242))
            draw_title(draw, item["title"], (620, 280), 350, ink, start_size=102, max_lines=5)
            add_label(draw, item["pillar"], (620, 1080), accent)

    elif layout == "museum_label":
        x1, y1, x2, y2 = (108, 760, 810, 1175) if index % 2 else (270, 160, 972, 575)
        draw.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=(*background, 245))
        draw_title(draw, item["title"], (x1 + 42, y1 + 62), x2 - x1 - 84, ink, start_size=112)
        add_label(draw, item["pillar"], (x1 + 42, y2 - 66), accent)

    elif layout == "image_card":
        image = Image.new("RGB", (W, H), background)
        photo = cover(bg_path, (0, 0, 816, 720))
        paste_rounded(image, photo, (132, 120), 22)
        draw = ImageDraw.Draw(image)
        draw_title(draw, item["title"], (132, 850), 816, ink, start_size=122, align="center")
        add_label(draw, item["pillar"], (132, 1210), accent)

    elif layout == "top_strip":
        draw.rectangle((0, 0, W, 535), fill=(*background, 246))
        draw_title(draw, item["title"], (108, 165), 864, ink, start_size=128)
        add_label(draw, item["pillar"], (108, 465), accent)

    elif layout == "small_caption":
        # Intentionally quiet, as a counterpoint to the louder typographic tiles.
        draw.rounded_rectangle((108, 930, 640, 1190), radius=10, fill=(*background, 232))
        draw_title(draw, item["title"], (142, 975), 465, ink, start_size=74, max_lines=3)
        add_label(draw, item["pillar"], (142, 1135), accent)

    elif layout == "frame":
        draw.rounded_rectangle((108, 135, 972, 1215), radius=16, outline=(*accent, 255), width=14)
        draw.rounded_rectangle((150, 850, 930, 1165), radius=10, fill=(*BLACK, 214))
        draw_title(draw, item["title"], (185, 900), 710, CREAM, start_size=104)
        add_label(draw, item["pillar"], (185, 1095), accent)

    elif layout == "split_vertical":
        image = Image.new("RGB", (W, H), background)
        photo_width = 610
        photo = cover(bg_path, (0, 0, photo_width, H))
        if index % 2:
            image.paste(photo, (0, 0))
            draw = ImageDraw.Draw(image)
            draw_title(draw, item["title"], (660, 270), 310, ink, start_size=100, max_lines=4)
            add_label(draw, item["pillar"], (660, 1080), accent)
        else:
            image.paste(photo, (W - photo_width, 0))
            draw = ImageDraw.Draw(image)
            draw_title(draw, item["title"], (108, 270), 310, ink, start_size=100, max_lines=4)
            add_label(draw, item["pillar"], (108, 1080), accent)

    elif layout == "circle_window":
        image = Image.new("RGB", (W, H), background)
        photo = cover(bg_path, (0, 0, 700, 700))
        circle = Image.new("L", (700, 700), 0)
        ImageDraw.Draw(circle).ellipse((0, 0, 700, 700), fill=255)
        image.paste(photo, (190, 115), circle)
        draw = ImageDraw.Draw(image)
        draw_title(draw, item["title"], (108, 875), 864, ink, start_size=116, align="center")
        add_label(draw, item["pillar"], (108, 1215), accent)
    else:
        raise ValueError(layout)

    return image.convert("RGB")


plan = json.loads((ROOT / "content-plan.json").read_text(encoding="utf-8"))
dynamic_keys = {
    "instagram_url",
    "execution_confirmed",
    "published_at",
    "scheduled_at",
}

for index, item in enumerate(plan, 1):
    for key in dynamic_keys:
        item.pop(key, None)
    item["status"] = "ready_now" if index <= 9 else "scheduled"
    item["format"] = "Mixed editorial case-study feed"
    item["asset"] = f"posts/editorial-v4-20260730/day-{index:02}.jpg"
    item["public_asset_url"] = f"PUBLIC_ASSET_BASE_URL/{item['asset']}"
    item["visual_layout"] = LAYOUTS[index - 1]
    item["visual_source"] = (
        "type_only"
        if BACKGROUND_MAP[index] is None
        else BACKGROUND_MAP[index].name
    )
    artwork = render(index, item)
    artwork.save(OUT / f"day-{index:02}.jpg", quality=95, subsampling=0, optimize=True)
    artwork.save(OUT / f"day-{index:02}.png", optimize=True)

(PACK / "content-plan.json").write_text(
    json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

fieldnames = []
for item in plan:
    for key in item:
        if key not in fieldnames and key != "steps":
            fieldnames.append(key)
with (PACK / "content-plan.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(plan)

(PACK / "CAPTION-SIAP-POSTING.txt").write_text(
    "\n\n".join(
        f"POSTINGAN {item['id']:02}\n"
        f"{item['date']} — {item['time_wib']} WIB\n\n"
        f"{item['title']}\n\n"
        f"{item['final_caption']}"
        for item in plan
    )
    + "\n",
    encoding="utf-8",
)

print(f"Built {len(plan)} mixed editorial posts in {OUT}")

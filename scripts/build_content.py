#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import textwrap
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("/Users/coong/Documents/lajora-web/public/assets")
OUT = ROOT / "posts"
START_DATE = date(2026, 7, 31)

FONT_REGULAR = "/System/Library/Fonts/SFNS.ttf"
FONT_BOLD = "/System/Library/Fonts/SFNS.ttf"

INK = "#11110f"
PAPER = "#f4f0e8"
LIME = "#c9f47d"
ORANGE = "#ff8a66"
WHITE = "#ffffff"


from education_content import CONTENT

def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REGULAR, size=size)


def cover(image: Image.Image, size=(1080, 1350), focus=0.5) -> Image.Image:
    w, h = image.size
    target_ratio = size[0] / size[1]
    ratio = w / h
    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = int((w - new_w) * focus)
        image = image.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w / target_ratio)
        top = max(0, int((h - new_h) * 0.45))
        image = image.crop((0, top, w, top + new_h))
    return image.resize(size, Image.Resampling.LANCZOS)


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def draw_logo(draw: ImageDraw.ImageDraw, x: int, y: int, color: str, mark_bg: str | None = None):
    draw.ellipse((x, y, x + 58, y + 58), outline=color, width=2, fill=mark_bg)
    draw.text((x + 19, y + 8), "L", font=font(31, True), fill=color)
    draw.ellipse((x + 43, y + 9, x + 51, y + 17), fill=ORANGE)
    draw.text((x + 76, y + 13), "LAJORA", font=font(21, True), fill=color, spacing=4)


def fit_title(draw: ImageDraw.ImageDraw, text: str, max_width: int, preferred=78, minimum=54):
    size = preferred
    while size >= minimum:
        f = font(size, True)
        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split()
            line = ""
            for word in words:
                test = f"{line} {word}".strip()
                if draw.textbbox((0, 0), test, font=f)[2] <= max_width:
                    line = test
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        if len(lines) <= 4:
            return f, lines
        size -= 3
    return font(minimum, True), lines


def draw_multiline(draw, xy, lines, fnt, fill, spacing=8):
    x, y = xy
    line_height = int(fnt.size * 1.02)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += line_height + spacing
    return y


def render_photo(item: dict, index: int, path: Path):
    base = cover(Image.open(SOURCE / item["background"]).convert("RGB"))
    base = ImageEnhance.Color(base).enhance(0.82)
    base = ImageEnhance.Contrast(base).enhance(1.06)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(1350):
        alpha = int(18 + 178 * (y / 1350) ** 1.7)
        od.line((0, y, 1080, y), fill=(8, 10, 8, alpha))
    od.rectangle((0, 0, 1080, 180), fill=(8, 10, 8, 62))
    base = Image.alpha_composite(base.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(base)
    draw_logo(draw, 74, 64, WHITE)
    draw.text((74, 220), f"{index:02d}  /  {item['pillar'].upper()}", font=font(18, True), fill=LIME)
    title_font, lines = fit_title(draw, item["title"], 920, 82, 58)
    title_y = 770 if len(lines) <= 3 else 690
    end_y = draw_multiline(draw, (74, title_y), lines, title_font, WHITE, 4)
    draw.line((74, end_y + 26, 198, end_y + 26), fill=LIME, width=4)
    subtitle = textwrap.wrap(item["subtitle"], width=46)
    draw_multiline(draw, (74, end_y + 54), subtitle[:3], font(27), PAPER, 7)
    draw.text((74, 1278), "LAJORA.WEB.ID", font=font(17, True), fill=WHITE)
    draw.text((865, 1278), "HOSPITALITY", font=font(15), fill=LIME)
    base.convert("RGB").save(path, quality=94, subsampling=0)


def render_paper(item: dict, index: int, path: Path):
    base = Image.new("RGB", (1080, 1350), PAPER)
    draw = ImageDraw.Draw(base)
    draw.ellipse((720, -120, 1220, 380), fill=LIME)
    draw.ellipse((-220, 1050, 300, 1570), fill=ORANGE)
    draw.rounded_rectangle((62, 54, 1018, 1296), radius=38, outline="#d7d1c7", width=2)
    draw_logo(draw, 88, 82, INK)
    draw.text((88, 230), f"{index:02d}", font=font(105, True), fill=ORANGE)
    draw.text((850, 254), item["format"].upper(), font=font(14, True), fill=INK)
    title_font, lines = fit_title(draw, item["title"], 870, 86, 60)
    end_y = draw_multiline(draw, (88, 450), lines, title_font, INK, 6)
    draw.line((88, end_y + 34, 250, end_y + 34), fill=ORANGE, width=5)
    subtitle = textwrap.wrap(item["subtitle"], width=43)
    draw_multiline(draw, (88, end_y + 78), subtitle[:4], font(31), "#4c4b47", 9)
    draw.text((88, 1210), item["pillar"].upper(), font=font(16, True), fill=INK)
    draw.text((807, 1210), "LAJORA.WEB.ID", font=font(16, True), fill=INK)
    base.save(path, quality=95, subsampling=0)


def render_split(item: dict, index: int, path: Path):
    base = Image.new("RGB", (1080, 1350), INK)
    photo = cover(Image.open(SOURCE / item["background"]).convert("RGB"), (936, 620))
    photo = ImageEnhance.Color(photo).enhance(0.86)
    mask = rounded_mask(photo.size, 34)
    base.paste(photo, (72, 72), mask)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((72, 72, 1008, 692), radius=34, outline=(255, 255, 255, 45), width=2)
    draw.ellipse((886, 100, 968, 182), fill=LIME)
    draw.text((911, 120), f"{index:02d}", font=font(23, True), fill=INK)
    draw.text((72, 744), item["pillar"].upper(), font=font(17, True), fill=ORANGE)
    title_font, lines = fit_title(draw, item["title"], 936, 72, 54)
    end_y = draw_multiline(draw, (72, 804), lines, title_font, WHITE, 3)
    subtitle = textwrap.wrap(item["subtitle"], width=52)
    draw_multiline(draw, (72, end_y + 32), subtitle[:3], font(25), "#b9b7b0", 6)
    draw_logo(draw, 72, 1222, WHITE)
    draw.text((829, 1241), "LAJORA.WEB.ID", font=font(15, True), fill=LIME)
    base.save(path, quality=94, subsampling=0)


PHOTO_MAP = {
    1: SOURCE / "editorial/hero.webp",
    7: SOURCE / "editorial/veluvana.webp",
    8: ROOT / "brand-assets/ai/direct-booking-owner.png",
    10: ROOT / "brand-assets/ai/mobile-booking.png",
    13: SOURCE / "editorial/casa-veranda.webp",
    16: ROOT / "brand-assets/ai/restaurant-payment.png",
    20: ROOT / "brand-assets/ai/restaurant-payment.png",
    22: SOURCE / "editorial/ubud-villas.webp",
    24: ROOT / "brand-assets/ai/analytics-team.png",
    27: SOURCE / "editorial/indies-heritage.webp",
    30: ROOT / "brand-assets/ai/direct-booking-owner.png",
}


def centered_text(draw, box, text, fnt, fill, max_lines=2):
    x0, y0, x1, y1 = box
    width = x1 - x0 - 24
    words = text.replace("|", "\n").split()
    lines, line = [], ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=fnt)[2] <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    lines = lines[:max_lines]
    line_h = int(fnt.size * 1.05)
    total_h = len(lines) * line_h
    y = y0 + ((y1 - y0) - total_h) / 2
    for value in lines:
        bbox = draw.textbbox((0, 0), value, font=fnt)
        x = x0 + ((x1 - x0) - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), value, font=fnt, fill=fill)
        y += line_h


def draw_flow(draw, box, steps, ink, accent, panel):
    x0, y0, x1, y1 = box
    count = len(steps)
    gap = 18
    node_w = int((x1 - x0 - gap * (count - 1)) / count)
    node_h = 112
    y = int((y0 + y1 - node_h) / 2)
    for i, step in enumerate(steps):
        x = x0 + i * (node_w + gap)
        if i:
            draw.line((x - gap + 3, y + node_h // 2, x - 3, y + node_h // 2), fill=accent, width=4)
            draw.polygon([(x - 8, y + node_h // 2 - 6), (x - 2, y + node_h // 2), (x - 8, y + node_h // 2 + 6)], fill=accent)
        draw.rounded_rectangle((x, y, x + node_w, y + node_h), radius=22, fill=panel, outline=accent if i == count - 1 else None, width=2)
        draw.text((x + 13, y + 12), f"{i + 1:02d}", font=font(15, True), fill=accent)
        centered_text(draw, (x + 4, y + 28, x + node_w - 4, y + node_h - 5), step, font(18, True), ink)


def draw_grid(draw, box, steps, ink, accent, panel):
    x0, y0, x1, y1 = box
    cols = 2
    rows = (len(steps) + 1) // 2
    gap = 18
    cell_w = int((x1 - x0 - gap) / 2)
    cell_h = int((y1 - y0 - gap * (rows - 1)) / rows)
    for i, step in enumerate(steps):
        col, row = i % cols, i // cols
        x = x0 + col * (cell_w + gap)
        y = y0 + row * (cell_h + gap)
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=20, fill=panel)
        draw.ellipse((x + 18, y + 18, x + 38, y + 38), fill=accent)
        centered_text(draw, (x + 45, y + 8, x + cell_w - 8, y + cell_h - 8), step, font(21, True), ink)


def draw_hub(draw, box, steps, ink, accent, panel, center_label):
    import math
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    radius_x, radius_y = (x1 - x0) * .36, (y1 - y0) * .34
    node_w, node_h = 176, 76
    for i, step in enumerate(steps):
        angle = -math.pi / 2 + i * (2 * math.pi / len(steps))
        nx, ny = cx + math.cos(angle) * radius_x, cy + math.sin(angle) * radius_y
        draw.line((cx, cy, nx, ny), fill=accent, width=3)
        rect = (nx - node_w / 2, ny - node_h / 2, nx + node_w / 2, ny + node_h / 2)
        draw.rounded_rectangle(rect, radius=18, fill=panel)
        centered_text(draw, rect, step, font(17, True), ink)
    draw.ellipse((cx - 78, cy - 78, cx + 78, cy + 78), fill=accent)
    centered_text(draw, (cx - 70, cy - 70, cx + 70, cy + 70), center_label.upper(), font(17, True), INK)


def draw_funnel(draw, box, steps, ink, accent, panel):
    x0, y0, x1, y1 = box
    height = (y1 - y0) / len(steps)
    for i, step in enumerate(steps):
        shrink = i * 58
        left, right = x0 + shrink, x1 - shrink
        top = y0 + i * height
        fill = accent if i == len(steps) - 1 else panel
        draw.rounded_rectangle((left, top, right, top + height - 12), radius=18, fill=fill)
        centered_text(draw, (left, top, right, top + height - 12), step, font(19, True), INK if fill == accent else ink)


def draw_comparison(draw, box, steps, ink, accent, panel):
    x0, y0, x1, y1 = box
    gap = 20
    width = (x1 - x0 - gap) / 2
    for i, value in enumerate(steps[:2]):
        title, _, detail = value.partition("|")
        x = x0 + i * (width + gap)
        draw.rounded_rectangle((x, y0, x + width, y1), radius=28, fill=panel, outline=accent if i else None, width=3)
        draw.text((x + 30, y0 + 30), f"0{i + 1}", font=font(18, True), fill=accent)
        centered_text(draw, (x + 20, y0 + 72, x + width - 20, y0 + 190), title, font(31, True), ink)
        centered_text(draw, (x + 30, y0 + 205, x + width - 30, y1 - 28), detail, font(23), ink, 3)


def draw_phone(draw, box, steps, ink, accent, panel):
    x0, y0, x1, y1 = box
    phone_w = 330
    px = (x0 + x1 - phone_w) / 2
    draw.rounded_rectangle((px, y0, px + phone_w, y1), radius=48, fill=panel, outline=accent, width=3)
    draw.rounded_rectangle((px + 105, y0 + 18, px + 225, y0 + 30), radius=7, fill=ink)
    row_y = y0 + 72
    for i, step in enumerate(steps):
        draw.rounded_rectangle((px + 30, row_y, px + phone_w - 30, row_y + 58), radius=14, fill=accent if i == len(steps) - 1 else None, outline=ink, width=2)
        centered_text(draw, (px + 38, row_y, px + phone_w - 38, row_y + 58), step, font(17, True), INK if i == len(steps) - 1 else ink)
        row_y += 72


def draw_target(draw, box, steps, ink, accent):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sizes = [330, 260, 190, 120]
    for i, size in enumerate(sizes[:len(steps)]):
        draw.ellipse((cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2), outline=accent if i % 2 == 0 else ink, width=4)
    for i, step in enumerate(steps):
        y = y0 + 12 + i * 54
        draw.rounded_rectangle((x0 + 14, y, x0 + 220, y + 42), radius=18, fill=accent if i == len(steps) - 1 else None, outline=ink, width=2)
        centered_text(draw, (x0 + 20, y, x0 + 214, y + 42), step, font(15, True), INK if i == len(steps) - 1 else ink)


def draw_dashboard(draw, box, steps, ink, accent, panel):
    x0, y0, x1, y1 = box
    cols, gap = 2, 18
    cell_w = (x1 - x0 - gap) / 2
    cell_h = (y1 - y0 - gap * 2) / 3
    for i, step in enumerate(steps):
        col, row = i % 2, i // 2
        x, y = x0 + col * (cell_w + gap), y0 + row * (cell_h + gap)
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=18, fill=panel)
        draw.text((x + 18, y + 16), step, font=font(17, True), fill=ink)
        bar_w = int((cell_w - 36) * (.38 + (i % 3) * .19))
        draw.rounded_rectangle((x + 18, y + cell_h - 30, x + 18 + bar_w, y + cell_h - 18), radius=6, fill=accent)


def render_education(item: dict, index: int, path: Path):
    photo_path = PHOTO_MAP.get(index)
    has_photo = bool(photo_path and Path(photo_path).exists())
    if has_photo:
        base = cover(Image.open(photo_path).convert("RGB"))
        base = ImageEnhance.Color(base).enhance(.82).convert("RGBA")
        shade = Image.new("RGBA", base.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shade)
        for y in range(1350):
            alpha = int(92 + 118 * (y / 1350) ** 1.25)
            sd.line((0, y, 1080, y), fill=(8, 10, 8, alpha))
        base = Image.alpha_composite(base, shade).convert("RGB")
        background, text_color, muted, accent = INK, WHITE, "#d1cec6", LIME
    else:
        variants = [
            (PAPER, INK, "#595750", ORANGE),
            (INK, WHITE, "#b9b7b0", LIME),
            ("#12352e", WHITE, "#c7d5ce", ORANGE),
        ]
        background, text_color, muted, accent = variants[(index - 1) % len(variants)]
        base = Image.new("RGB", (1080, 1350), background)
        decoration = ImageDraw.Draw(base)
        decoration.ellipse((760, -190, 1240, 290), fill=accent)
        decoration.ellipse((-240, 1120, 180, 1540), outline=accent, width=3)

    draw = ImageDraw.Draw(base, "RGBA")
    draw_logo(draw, 68, 56, text_color)
    draw.rounded_rectangle((892, 58, 1008, 106), radius=24, fill=accent)
    centered_text(draw, (892, 58, 1008, 106), f"{index:02d}/30", font(16, True), INK)
    draw.text((68, 160), item["pillar"].upper(), font=font(17, True), fill=accent)

    title_font, title_lines = fit_title(draw, item["title"], 930, 78, 54)
    end_y = draw_multiline(draw, (68, 205), title_lines, title_font, text_color, 3)
    subtitle_lines = textwrap.wrap(item["subtitle"], width=58)
    subtitle_end = draw_multiline(draw, (68, end_y + 24), subtitle_lines[:3], font(25), muted, 7)

    panel_top = max(640, int(subtitle_end + 48))
    panel_box = (58, panel_top, 1022, 1205)
    panel_fill = (17, 17, 15, 230) if has_photo else ((255, 255, 255, 28) if text_color == WHITE else (255, 255, 255, 135))
    draw.rounded_rectangle(panel_box, radius=32, fill=panel_fill, outline=(255, 255, 255, 46) if text_color == WHITE else (17, 17, 15, 28), width=2)
    inner = (88, panel_top + 32, 992, 1173)
    diagram = item.get("diagram", "flow")
    steps = item.get("steps", [])
    node_panel = (255, 255, 255, 30) if text_color == WHITE else (244, 240, 232, 255)
    diagram_ink = WHITE if text_color == WHITE else INK
    if diagram in {"flow", "journey", "roadmap", "timeline"}:
        draw_flow(draw, inner, steps, diagram_ink, accent, node_panel)
    elif diagram in {"grid", "quadrant", "checklist"}:
        draw_grid(draw, inner, steps, diagram_ink, accent, node_panel)
    elif diagram in {"hub", "ecosystem", "engine", "automation", "ownership", "data", "growth", "search", "loop"}:
        draw_hub(draw, inner, steps, diagram_ink, accent, node_panel, item["pillar"])
    elif diagram == "funnel":
        draw_funnel(draw, inner, steps, diagram_ink, accent, node_panel)
    elif diagram == "comparison":
        draw_comparison(draw, inner, steps, diagram_ink, accent, node_panel)
    elif diagram == "phone":
        draw_phone(draw, inner, steps, diagram_ink, accent, node_panel)
    elif diagram == "target":
        draw_target(draw, inner, steps, diagram_ink, accent)
    elif diagram == "dashboard":
        draw_dashboard(draw, inner, steps, diagram_ink, accent, node_panel)
    else:
        draw_grid(draw, inner, steps, diagram_ink, accent, node_panel)

    draw.text((68, 1274), "EDUKASI HOSPITALITY SYSTEM", font=font(14, True), fill=text_color)
    draw.text((858, 1274), "LAJORA.WEB.ID", font=font(14, True), fill=accent)
    base.save(path, quality=95, subsampling=0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    times = ["19:30"]
    for i, item in enumerate(CONTENT, 1):
        publish_date = START_DATE + timedelta(days=i - 1)
        record = {
            "id": i,
            "date": publish_date.isoformat(),
            "time_wib": times[(i - 1) % len(times)],
            "timezone": "Asia/Jakarta",
            "status": "ready",
            "approval_required": False,
            **item,
            "asset": f"posts/day-{i:02d}.jpg",
            "public_asset_url": f"PUBLIC_ASSET_BASE_URL/posts/day-{i:02d}.jpg",
            "final_caption": f"{item['caption']}\n\n{item['cta']}\n\n{item['hashtags']}",
        }
        records.append(record)
        output = OUT / f"day-{i:02d}.jpg"
        render_education(item, i, output)

    (ROOT / "content-plan.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (ROOT / "content-plan.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields = [
            "id", "date", "time_wib", "timezone", "status", "approval_required",
            "format", "pillar", "title", "subtitle", "final_caption", "asset",
            "public_asset_url",
        ]
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print(f"Built {len(records)} posts in {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the hospitality, website, payment, and branding revision for posts 10-30."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path("/Users/coong/Documents/lajora-social-30days")
REVISION = ROOT / "editorial-30-en" / "revisions-20260731"
SOURCES = REVISION / "sources"
ORIGINALS = REVISION / "originals"
PACK_POSTS = ROOT / "editorial-30-en" / "posts"
CAMPAIGN_POSTS = ROOT / "posts" / "editorial-system-v2-20260731"

W, H = 1080, 1350
BLACK = (14, 14, 14)
WHITE = (248, 244, 235)
COBALT = (31, 64, 215)
CORAL = (255, 100, 86)
LIME = (207, 255, 63)
YELLOW = (255, 210, 27)
VIOLET = (74, 42, 144)
CYAN = (46, 199, 223)
METAL = (210, 205, 190)

IMAGE_LED = {11, 12, 14, 15, 17, 18, 20, 21, 23, 24, 26, 27, 29}
TYPE_LED = {10, 13, 16, 19, 22, 25, 28, 30}


def cover(path: Path) -> Image.Image:
    with Image.open(path) as source:
        image = ImageOps.fit(
            source.convert("RGB"),
            (W, H),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    return image


def circle(draw: ImageDraw.ImageDraw, x: int, y: int, radius: int, fill, outline=None, width=1):
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=fill,
        outline=outline,
        width=width,
    )


def add_type_motif(post_id: int, image: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    if post_id == 10:
        draw.line((188, 1165, 470, 1165, 560, 1235, 820, 1235), fill=CYAN + (220,), width=5)
        circle(draw, 188, 1165, 14, CORAL + (255,))
        circle(draw, 470, 1165, 12, LIME + (255,))
        circle(draw, 820, 1235, 20, (0, 0, 0, 0), METAL + (255,), 7)
        draw.arc((845, 1105, 990, 1270), 180, 360, fill=LIME + (230,), width=7)
    elif post_id == 13:
        for offset, color in [(0, COBALT), (36, CORAL), (72, BLACK)]:
            draw.rounded_rectangle(
                (720 + offset, 82, 830 + offset, 205),
                radius=48,
                outline=color + (235,),
                width=7,
            )
        draw.line((775, 205, 775, 260, 930, 260), fill=BLACK + (210,), width=5)
        circle(draw, 930, 260, 13, CORAL + (255,))
    elif post_id == 16:
        draw.line((590, 1130, 725, 1060, 855, 1130), fill=CORAL + (235,), width=6)
        circle(draw, 590, 1130, 12, WHITE + (255,))
        circle(draw, 725, 1060, 18, (0, 0, 0, 0), METAL + (255,), 6)
        circle(draw, 855, 1130, 12, LIME + (255,))
        draw.arc((870, 990, 1018, 1150), 180, 360, fill=CYAN + (225,), width=6)
    elif post_id == 19:
        draw.arc((820, 135, 1000, 390), 180, 360, fill=COBALT + (230,), width=9)
        draw.line((910, 390, 910, 480, 970, 540), fill=COBALT + (210,), width=6)
        circle(draw, 910, 480, 15, METAL + (255,))
        circle(draw, 970, 540, 11, LIME + (255,))
    elif post_id == 22:
        draw.rounded_rectangle((745, 110, 895, 260), radius=42, outline=CORAL + (230,), width=8)
        draw.rounded_rectangle((810, 220, 960, 370), radius=42, outline=COBALT + (230,), width=8)
        draw.line((820, 260, 820, 420, 960, 420), fill=BLACK + (190,), width=5)
        circle(draw, 960, 420, 16, METAL + (255,))
    elif post_id == 25:
        draw.arc((790, 72, 1008, 285), 180, 360, fill=CYAN + (235,), width=9)
        circle(draw, 820, 180, 13, YELLOW + (255,))
        circle(draw, 975, 180, 18, (0, 0, 0, 0), METAL + (255,), 6)
        draw.line((75, 1135, 205, 1135, 270, 1210), fill=VIOLET + (220,), width=7)
        circle(draw, 75, 1135, 12, CORAL + (255,))
        circle(draw, 270, 1210, 12, COBALT + (255,))
    elif post_id == 28:
        draw.line((850, 1010, 950, 1010, 950, 1065), fill=CORAL + (235,), width=6)
        circle(draw, 850, 1010, 12, COBALT + (255,))
        circle(draw, 950, 1010, 17, (0, 0, 0, 0), METAL + (255,), 6)
        draw.arc((830, 1040, 1010, 1170), 180, 360, fill=CYAN + (220,), width=7)
    elif post_id == 30:
        draw.line((820, 340, 965, 470, 965, 585), fill=CYAN + (225,), width=6)
        circle(draw, 820, 340, 12, CORAL + (255,))
        circle(draw, 965, 470, 18, (0, 0, 0, 0), METAL + (255,), 6)
        circle(draw, 965, 585, 12, LIME + (255,))
        draw.arc((805, 1085, 1015, 1260), 180, 360, fill=CORAL + (230,), width=8)
    else:
        raise ValueError(f"Unsupported type post {post_id}")

    return Image.alpha_composite(image.convert("RGBA"), layer).convert("RGB")


def save_post(post_id: int, image: Image.Image):
    filename = f"day-{post_id:02}.jpg"
    png_name = f"day-{post_id:02}.png"
    image.save(PACK_POSTS / filename, quality=95, subsampling=0, optimize=True)
    image.save(PACK_POSTS / png_name, optimize=True)
    image.save(CAMPAIGN_POSTS / filename, quality=95, subsampling=0, optimize=True)


def make_contact_sheet():
    thumb_w, thumb_h = 216, 270
    gap = 16
    cols, rows = 5, 5
    sheet = Image.new(
        "RGB",
        (cols * thumb_w + (cols + 1) * gap, rows * (thumb_h + 34) + (rows + 1) * gap),
        BLACK,
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 22, index=1)
    for index, post_id in enumerate(range(10, 31)):
        col, row = index % cols, index // cols
        x = gap + col * (thumb_w + gap)
        y = gap + row * (thumb_h + 34 + gap)
        thumb = cover(CAMPAIGN_POSTS / f"day-{post_id:02}.jpg").resize(
            (thumb_w, thumb_h), Image.Resampling.LANCZOS
        )
        sheet.paste(thumb, (x, y))
        draw.text((x, y + thumb_h + 5), f"{post_id:02}", font=font, fill=WHITE)
    sheet.save(REVISION / "contact-sheet-posts-10-30.jpg", quality=92, optimize=True)

    grid_thumb_w, grid_thumb_h = 270, 338
    grid_cols, grid_rows = 3, 7
    grid = Image.new(
        "RGB",
        (
            grid_cols * grid_thumb_w + (grid_cols + 1) * gap,
            grid_rows * grid_thumb_h + (grid_rows + 1) * gap,
        ),
        BLACK,
    )
    for index, post_id in enumerate(range(10, 31)):
        col, row = index % grid_cols, index // grid_cols
        x = gap + col * (grid_thumb_w + gap)
        y = gap + row * (grid_thumb_h + gap)
        thumb = cover(CAMPAIGN_POSTS / f"day-{post_id:02}.jpg").resize(
            (grid_thumb_w, grid_thumb_h), Image.Resampling.LANCZOS
        )
        grid.paste(thumb, (x, y))
    grid.save(REVISION / "grid-preview-posts-10-30.jpg", quality=92, optimize=True)


def main():
    PACK_POSTS.mkdir(parents=True, exist_ok=True)
    CAMPAIGN_POSTS.mkdir(parents=True, exist_ok=True)
    for post_id in range(10, 31):
        if post_id in IMAGE_LED:
            source = SOURCES / f"day-{post_id:02}.png"
            if not source.exists():
                raise FileNotFoundError(source)
            image = cover(source)
        elif post_id in TYPE_LED:
            source = ORIGINALS / f"day-{post_id:02}.jpg"
            if not source.exists():
                raise FileNotFoundError(source)
            image = add_type_motif(post_id, cover(source))
        else:
            raise ValueError(f"Post {post_id} has no content mode")
        save_post(post_id, image)
    make_contact_sheet()
    print(f"Built 21 revised Lajora posts in {CAMPAIGN_POSTS}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the English, project-led Lajora 30-post campaign."""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


ROOT = Path("/Users/coong/Documents/lajora-social-30days")
PACK = ROOT / "editorial-30-en"
BG = PACK / "backgrounds"
OUT = PACK / "posts"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
BLACK = (14, 14, 14)
WHITE = (248, 244, 235)
COBALT = (31, 64, 215)
CORAL = (255, 100, 86)
LIME = (207, 255, 63)
YELLOW = (255, 210, 27)
VIOLET = (74, 42, 144)
CYAN = (46, 199, 223)

HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"


def font(size: int, face: str = "black") -> ImageFont.FreeTypeFont:
    index = {"black": 9, "bold": 1, "medium": 10, "regular": 0}[face]
    return ImageFont.truetype(HELVETICA, size=size, index=index)


def cover(path: Path, anchor: str = "center") -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize(
        (round(im.width * scale), round(im.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (im.width - W) // 2)
    if anchor == "top":
        top = 0
    elif anchor == "bottom":
        top = max(0, im.height - H)
    else:
        top = max(0, (im.height - H) // 2)
    return im.crop((left, top, left + W, top + H))


def fit(text: str, max_width: int, start: int = 170, minimum: int = 48, face: str = "black"):
    probe = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(probe)
    for size in range(start, minimum - 1, -2):
        fnt = font(size, face)
        if draw.textbbox((0, 0), text, font=fnt)[2] <= max_width:
            return fnt
    return font(minimum, face)


def image_post(path: Path, anchor: str = "center") -> Image.Image:
    return cover(path, anchor)


def tote_post() -> Image.Image:
    im = cover(BG / "bg-21-tote.png", "center").convert("RGBA")
    text_layer = Image.new("RGBA", (720, 340), (0, 0, 0, 0))
    d = ImageDraw.Draw(text_layer)
    fnt = font(98, "black")
    d.text((30, 38), "BE", font=fnt, fill=BLACK + (255,))
    d.text((30, 128), "UNMISSABLE.", font=fnt, fill=BLACK + (255,))
    text_layer = text_layer.rotate(-4, resample=Image.Resampling.BICUBIC, expand=True)
    im.alpha_composite(text_layer, (182, 330))
    return im.convert("RGB")


def type_post(kind: str) -> Image.Image:
    im = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(im)

    if kind == "seen":
        d.rectangle((0, 0, W, H), fill=WHITE)
        d.rectangle((72, 90, 1010, 160), fill=COBALT)
        d.text((76, 205), "SEEN", font=font(230), fill=BLACK)
        d.text((78, 480), "≠", font=font(150, "bold"), fill=CORAL)
        f = fit("REMEMBERED", 920, 176)
        d.text((76, 700), "REMEMBERED", font=f, fill=BLACK)
        d.ellipse((865, 1060, 1010, 1205), fill=LIME)

    elif kind == "quietly":
        d.rectangle((0, 0, W, H), fill=BLACK)
        d.text((650, 155), "QUIETLY", font=font(70, "medium"), fill=WHITE)
        d.rectangle((72, 305, 1008, 1060), fill=COBALT)
        d.text((108, 405), "DISTINCT.", font=fit("DISTINCT.", 850, 190), fill=WHITE)
        d.line((108, 760, 940, 760), fill=LIME, width=14)
        d.ellipse((94, 1030, 166, 1102), fill=CORAL)

    elif kind == "claim":
        d.rectangle((0, 0, W, H), fill=YELLOW)
        d.rectangle((0, 0, 230, H), fill=COBALT)
        d.text((276, 220), "CLAIM", font=font(190), fill=BLACK)
        d.text((276, 450), "A", font=font(140), fill=CORAL)
        d.text((276, 650), "PLACE.", font=font(190), fill=BLACK)
        d.line((280, 1030, 980, 1030), fill=BLACK, width=10)

    elif kind == "voice":
        d.rectangle((0, 0, W, H), fill=COBALT)
        for y in range(160, 1180, 70):
            d.line((60, y, 1020, y - 90), fill=(65, 98, 235), width=4)
        d.text((92, 260), "VOICE,", font=font(190), fill=WHITE)
        d.text((92, 520), "MADE", font=font(142, "bold"), fill=CORAL)
        d.text((92, 700), "VISIBLE.", font=font(168), fill=WHITE)
        d.ellipse((870, 1005, 1008, 1143), fill=LIME)

    elif kind == "feel":
        d.rectangle((0, 0, W, H), fill=CORAL)
        d.ellipse((-180, -30, 780, 930), fill=WHITE)
        d.text((80, 215), "FEEL", font=font(235), fill=BLACK)
        d.rectangle((80, 560, 1000, 970), fill=BLACK)
        d.text((118, 610), "FIRST.", font=font(215), fill=WHITE)
        d.rectangle((910, 1020, 970, 1200), fill=LIME)

    elif kind == "repeat":
        d.rectangle((0, 0, W, H), fill=LIME)
        ghost = font(108, "bold")
        for y in [95, 205, 315, 425]:
            d.text((65, y), "REPEAT", font=ghost, fill=(164, 205, 45))
        d.rectangle((62, 580, 1016, 1120), fill=BLACK)
        d.text((103, 660), "REPEAT", font=font(170), fill=WHITE)
        d.text((103, 870), "THE CODE.", font=font(138), fill=CORAL)

    elif kind == "color":
        d.rectangle((0, 0, 540, 675), fill=COBALT)
        d.rectangle((540, 0, W, 675), fill=CORAL)
        d.rectangle((0, 675, 540, H), fill=LIME)
        d.rectangle((540, 675, W, H), fill=YELLOW)
        d.rectangle((96, 255, 984, 1095), fill=WHITE)
        d.text((132, 340), "COLOR", font=font(174), fill=BLACK)
        d.text((132, 555), "HAS AN", font=font(128, "bold"), fill=COBALT)
        d.text((132, 735), "ATTITUDE.", font=font(154), fill=BLACK)

    elif kind == "detail":
        d.rectangle((0, 0, W, H), fill=WHITE)
        d.ellipse((92, 122, 132, 162), fill=CORAL)
        d.line((155, 142, 972, 142), fill=BLACK, width=5)
        d.text((86, 265), "ONE", font=font(205), fill=BLACK)
        d.text((86, 505), "DETAIL.", font=font(190), fill=BLACK)
        d.text((86, 800), "BIG MEMORY.", font=fit("BIG MEMORY.", 890, 140), fill=COBALT)
        d.rectangle((88, 1080, 1010, 1150), fill=LIME)

    elif kind == "felt":
        d.rectangle((0, 0, W, H), fill=BLACK)
        d.text((72, 170), "NOT JUST", font=font(132, "bold"), fill=CORAL)
        d.text((72, 345), "SEEN.", font=font(225), fill=WHITE)
        d.rectangle((72, 655, 1008, 1085), fill=VIOLET)
        d.text((112, 725), "FELT.", font=font(230), fill=LIME)
        d.ellipse((848, 150, 1006, 308), outline=CYAN, width=14)
    else:
        raise ValueError(kind)
    return im


POSTS = [
    {"kind": "image", "source": "bg-16-vinyl.png", "title": "Vinyl Study", "caption": ""},
    {
        "kind": "image",
        "source": "bg-17-book.png",
        "title": "Energy, Bound",
        "caption": "An editorial cover study built around energy as a moving field. We blurred the boundary between image and surface, letting color behave like light rather than decoration. Quiet from a distance. Alive up close.",
    },
    {"kind": "image", "source": "bg-18-billboard.png", "title": "A Bigger Stage", "caption": ""},
    {
        "kind": "image",
        "source": "bg-19-bts.png",
        "title": "Behind the Cloud",
        "caption": "A little behind the scenes from our latest visual experiment.",
    },
    {
        "kind": "image",
        "source": "bg-20-bottle.png",
        "title": "Fruit, Reframed",
        "caption": "A packaging study built from contrast: crisp geometry against hand-made botanical forms, a quiet label inside a loud world. The goal was simple—make the object feel joyful before anyone knows what it is.",
    },
    {"kind": "tote", "title": "Be Unmissable", "caption": ""},
    {
        "kind": "image",
        "source": "bg-01-attention.png",
        "title": "Presence Study",
        "caption": "A study in presence, repetition, and the one shape that refuses to disappear.",
    },
    {"kind": "type", "style": "seen", "title": "Seen Is Not Remembered", "caption": ""},
    {
        "kind": "image",
        "source": "bg-02-character.png",
        "title": "The Face That Stays",
        "caption": "When every face in the room looks the same, character becomes the clearest form of recognition. This frame explores identity through repetition, interruption, and one deliberately unfamiliar gesture.",
    },
    {"kind": "type", "style": "quietly", "title": "Quietly Distinct", "caption": ""},
    {
        "kind": "image",
        "source": "bg-03-distinction.png",
        "title": "Choose Another Door",
        "caption": "Different does not have to mean louder.",
    },
    {"kind": "image", "source": "bg-04-positioning.png", "title": "The Chosen Place", "caption": ""},
    {
        "kind": "type",
        "style": "claim",
        "title": "Claim a Place",
        "caption": "A typographic study in focus. One field, one interruption, one place to land. The composition strips away explanation and lets position carry the idea.",
    },
    {"kind": "image", "source": "bg-05-voice.png", "title": "Sound in Color", "caption": ""},
    {
        "kind": "image",
        "source": "bg-06-personality.png",
        "title": "Inside the Surface",
        "caption": "Built around the tension between restraint and expression. A neutral shell opens to reveal a much louder interior—because personality should feel structural, never applied at the end.",
    },
    {"kind": "type", "style": "voice", "title": "Voice, Made Visible", "caption": ""},
    {
        "kind": "image",
        "source": "bg-07-emotion.png",
        "title": "Enter the Feeling",
        "caption": "Feeling enters the room before explanation does.",
    },
    {
        "kind": "image",
        "source": "bg-08-memory.png",
        "title": "A Rhythm That Stays",
        "caption": "A visual system can repeat without standing still. We used recurring arches, shifting scale, and a single moving trail to explore how consistency becomes memory.",
    },
    {"kind": "type", "style": "feel", "title": "Feel First", "caption": ""},
    {
        "kind": "image",
        "source": "bg-09-rhythm.png",
        "title": "Three Poses, One Code",
        "caption": "Same code. Different pose.",
    },
    {"kind": "image", "source": "bg-10-visual-identity.png", "title": "Forms with a Voice", "caption": ""},
    {
        "kind": "type",
        "style": "repeat",
        "title": "Repeat the Code",
        "caption": "Repetition is not sameness. It is the discipline of returning to a recognizable idea while giving it new energy every time.",
    },
    {"kind": "image", "source": "bg-11-detail.png", "title": "The Detail", "caption": ""},
    {
        "kind": "image",
        "source": "bg-12-community.png",
        "title": "A Shared Center",
        "caption": "A shared center turns individual gestures into one living composition. This study uses tension, connection, and a deliberately imperfect network to make closeness visible.",
    },
    {"kind": "type", "style": "color", "title": "Color Has an Attitude", "caption": ""},
    {
        "kind": "image",
        "source": "bg-13-hospitality.png",
        "title": "The Small Gesture",
        "caption": "The smallest gesture can hold the entire room.",
    },
    {
        "kind": "image",
        "source": "bg-14-authenticity.png",
        "title": "How It Felt",
        "caption": "An exploration of atmosphere as memory. Soft material, moving color, and a human gesture work together to create a frame that is understood emotionally before it is read visually.",
    },
    {"kind": "type", "style": "detail", "title": "One Detail. Big Memory.", "caption": ""},
    {
        "kind": "image",
        "source": "bg-15-trust.png",
        "title": "Alignment",
        "caption": "Alignment creates the confidence to expand.",
    },
    {"kind": "type", "style": "felt", "title": "Not Just Seen. Felt.", "caption": ""},
]


def schedule_for(index: int):
    launch = date(2026, 7, 31)
    if index <= 9:
        return launch.isoformat(), "NOW", "ready_now"
    slots = {
        1: ["09:00", "11:00", "13:00", "15:00", "18:00", "21:00"],
        2: ["09:00", "12:00", "15:00", "18:00", "21:00"],
        3: ["09:00", "12:00", "15:00", "18:00", "21:00"],
        4: ["09:00", "12:00", "15:00", "18:00", "21:00"],
    }
    remaining = index - 10
    day_number = 1
    while remaining >= len(slots[day_number]):
        remaining -= len(slots[day_number])
        day_number += 1
    return (
        (launch + timedelta(days=day_number)).isoformat(),
        slots[day_number][remaining],
        "scheduled",
    )


plan = []
for index, post in enumerate(POSTS, 1):
    if post["kind"] == "image":
        anchor = "top" if post["source"] in {"bg-17-book.png", "bg-19-bts.png"} else "center"
        image = image_post(BG / post["source"], anchor)
        contains_text = False
    elif post["kind"] == "tote":
        image = tote_post()
        contains_text = True
    else:
        image = type_post(post["style"])
        contains_text = True

    image.save(OUT / f"day-{index:02}.jpg", quality=95, subsampling=0, optimize=True)
    image.save(OUT / f"day-{index:02}.png", optimize=True)
    post_date, post_time, status = schedule_for(index)
    asset = f"posts/editorial-20260731/day-{index:02}.jpg"
    plan.append(
        {
            "id": index,
            "date": post_date,
            "time_wib": post_time,
            "timezone": "Asia/Jakarta",
            "status": status,
            "approval_required": False,
            "format": post["kind"],
            "pillar": "Creative direction",
            "title": post["title"],
            "subtitle": "",
            "caption": post["caption"],
            "cta": "",
            "hashtags": "",
            "diagram": "project_led",
            "steps": [],
            "asset": asset,
            "public_asset_url": f"PUBLIC_ASSET_BASE_URL/{asset}",
            "final_caption": post["caption"],
            "contains_text": contains_text,
            "language": "en",
        }
    )

(PACK / "content-plan.json").write_text(
    json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

with (PACK / "content-plan.csv").open("w", encoding="utf-8", newline="") as handle:
    fields = [
        "id",
        "date",
        "time_wib",
        "status",
        "format",
        "title",
        "caption",
        "asset",
    ]
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for item in plan:
        writer.writerow({key: item[key] for key in fields})

(PACK / "CAPTION-SIAP-POSTING.txt").write_text(
    "\n\n".join(
        f"POST {item['id']:02}\n"
        f"{item['date']} — {item['time_wib']} WIB\n"
        f"{item['title']}\n\n"
        f"{item['final_caption'] if item['final_caption'] else '[NO CAPTION]'}"
        for item in plan
    )
    + "\n",
    encoding="utf-8",
)

print(
    json.dumps(
        {
            "posts": len(plan),
            "image_only": sum(not x["contains_text"] for x in plan),
            "with_text": sum(x["contains_text"] for x in plan),
            "blank_captions": sum(not x["final_caption"] for x in plan),
            "output": str(OUT),
        },
        indent=2,
    )
)

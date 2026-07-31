#!/usr/bin/env python3
"""Build the 30-post Lajora surreal-editorial campaign."""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


ROOT = Path("/Users/coong/Documents/lajora-social-30days")
PACK = ROOT / "editorial-30"
BG_DIR = PACK / "backgrounds"
OUT = PACK / "posts"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1350
CREAM = (249, 241, 225, 255)
BLACK = (17, 17, 16, 255)
COBALT = (24, 61, 211, 255)
CORAL = (255, 102, 91, 255)
LIME = (205, 255, 73, 255)
YELLOW = (255, 205, 30, 255)
VIOLET = (75, 45, 145, 255)
TURQUOISE = (42, 207, 196, 255)

HELVETICA = "/System/Library/Fonts/HelveticaNeue.ttc"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"


def font(size: int, role: str = "headline") -> ImageFont.FreeTypeFont:
    if role == "headline":
        return ImageFont.truetype(HELVETICA, size=size, index=9)
    if role == "label":
        return ImageFont.truetype(AVENIR, size=size, index=2)
    return ImageFont.truetype(HELVETICA, size=size, index=10)


def cover(path: Path, variant: int) -> Image.Image:
    im = Image.open(path).convert("RGB")
    if variant:
        im = ImageOps.mirror(im)
        im = ImageEnhance.Color(im).enhance(1.08)
        im = ImageEnhance.Contrast(im).enhance(1.04)
    zoom = 1.06 if variant else 1.0
    scale = max((W * zoom) / im.width, (H * zoom) / im.height)
    im = im.resize(
        (round(im.width * scale), round(im.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (im.width - W) // 2 + (24 if variant else 0))
    top_bias = -28 if variant else 0
    top = max(0, min(im.height - H, (im.height - H) // 2 + top_bias))
    return im.crop((left, top, left + W, top + H)).convert("RGBA")


def fit_font(lines: list[str], max_width: int, max_size: int, min_size: int = 52):
    size = max_size
    probe = Image.new("RGB", (10, 10))
    draw = ImageDraw.Draw(probe)
    while size >= min_size:
        f = font(size)
        if max(draw.textbbox((0, 0), line, font=f)[2] for line in lines) <= max_width:
            return f
        size -= 2
    return font(min_size)


def text_height(draw: ImageDraw.ImageDraw, lines: list[str], fnt, spacing: int) -> int:
    heights = []
    for line in lines:
        box = draw.textbbox((0, 0), line, font=fnt)
        heights.append(box[3] - box[1])
    return sum(heights) + spacing * (len(lines) - 1)


def draw_lines(draw, x, y, lines, fnt, fill, spacing):
    for line in lines:
        box = draw.textbbox((x, y), line, font=fnt)
        draw.text((x, y), line, font=fnt, fill=fill)
        y += (box[3] - box[1]) + spacing


LAYOUTS = [
    {"box": (74, 162, 950, 590), "panel": CREAM, "text": BLACK, "accent": COBALT},
    {"box": (95, 690, 986, 1150), "panel": BLACK, "text": CREAM, "accent": LIME},
    {"box": (78, 255, 820, 765), "panel": COBALT, "text": CREAM, "accent": CORAL},
    {"box": (174, 160, 990, 610), "panel": CREAM, "text": BLACK, "accent": VIOLET},
    {"box": (72, 760, 915, 1195), "panel": CORAL, "text": BLACK, "accent": LIME},
    {"box": (122, 330, 986, 790), "panel": BLACK, "text": CREAM, "accent": TURQUOISE},
]


POSTS = [
    {
        "title": "Dilihat belum tentu diingat.",
        "lines": ["DILIHAT", "BELUM TENTU", "DIINGAT."],
        "label": "PERSEPSI",
        "pillar": "Perception",
        "caption": "Mata bisa berhenti sesaat, tetapi ingatan memilih lebih ketat. Bentuk yang khas, nada yang konsisten, dan rasa yang jelas membuat sebuah identitas bertahan setelah orang beranjak. Kejar bukan hanya perhatian, tetapi jejak yang tertinggal.",
        "closing": "Terlihat adalah awal. Diingat adalah tujuan.",
        "hashtags": "#BrandPerception #CreativeDirection #BrandMemory #HospitalityBranding",
    },
    {
        "title": "Ramai belum tentu relevan.",
        "lines": ["RAMAI", "BELUM TENTU", "RELEVAN."],
        "label": "RELEVANSI",
        "pillar": "Relevance",
        "caption": "Ramai adalah ukuran suasana, bukan ukuran kedekatan. Komunikasi yang kuat berbicara kepada orang yang tepat dengan bahasa yang terasa dekat. Lebih baik menyentuh kelompok yang benar daripada berteriak kepada semua orang tanpa arah.",
        "closing": "Relevansi membuat perhatian punya arti.",
        "hashtags": "#BrandRelevance #AudienceInsight #CreativeStrategy #BrandThinking",
    },
    {
        "title": "Perhatian datang. Karakter bertahan.",
        "lines": ["PERHATIAN", "DATANG.", "KARAKTER BERTAHAN."],
        "label": "KARAKTER",
        "pillar": "Character",
        "caption": "Tren dapat membawa sorotan dengan cepat. Karakter membuat orang tetap mengenali siapa yang sedang berbicara. Identitas yang kuat tidak bergantung pada satu gaya populer karena ia memiliki prinsip, sikap, dan dunia yang konsisten.",
        "closing": "Sorotan lewat. Karakter menetap.",
        "hashtags": "#BrandCharacter #VisualIdentity #BrandStrategy #CreativeCulture",
    },
    {
        "title": "Cantik belum tentu berkarakter.",
        "lines": ["CANTIK", "BELUM TENTU", "BERKARAKTER."],
        "label": "IDENTITAS",
        "pillar": "Identity",
        "caption": "Visual yang rapi bisa menarik mata, tetapi karakter membuatnya memiliki nama dan suara. Setiap pilihan perlu membawa sikap: warna, bentuk, ritme, bahasa, hingga cara menyambut orang. Keindahan bekerja lebih kuat ketika punya alasan.",
        "closing": "Jangan berhenti pada cantik.",
        "hashtags": "#VisualIdentity #BrandCharacter #ArtDirection #BrandingIndonesia",
    },
    {
        "title": "Berbeda bukan berisik.",
        "lines": ["BERBEDA", "BUKAN", "BERISIK."],
        "label": "PEMBEDA",
        "pillar": "Distinctiveness",
        "caption": "Perbedaan yang kuat tidak selalu datang dari warna paling keras atau kalimat paling heboh. Ia bisa muncul dari satu sudut pandang yang jernih dan dijaga terus-menerus. Pembeda terbaik terasa tepat, bukan dipaksakan.",
        "closing": "Tajam tanpa perlu berteriak.",
        "hashtags": "#DistinctiveBrand #BrandPositioning #CreativeDirection #BrandClarity",
    },
    {
        "title": "Jangan tampil seperti semua.",
        "lines": ["JANGAN TAMPIL", "SEPERTI", "SEMUA."],
        "label": "DISTINGSI",
        "pillar": "Distinctiveness",
        "caption": "Saat semua mengikuti formula yang sama, hasilnya mudah tertukar. Cari elemen yang hanya masuk akal untuk satu identitas: cara melihat, cara berkata, dan cara menghadirkan pengalaman. Keunikan lahir dari keputusan yang spesifik.",
        "closing": "Yang spesifik lebih mudah dikenali.",
        "hashtags": "#BrandDistinctiveness #CreativeStrategy #BrandIdentity #ArtDirection",
    },
    {
        "title": "Pilih tempat di kepala.",
        "lines": ["PILIH TEMPAT", "DI KEPALA."],
        "label": "POSITIONING",
        "pillar": "Positioning",
        "caption": "Positioning bekerja seperti memilih satu kursi di ruang yang penuh. Kita perlu tahu ingin dikenal sebagai apa, oleh siapa, dan karena alasan apa. Pilihan yang tegas membuat seluruh komunikasi bergerak ke arah yang sama.",
        "closing": "Pilih tempat. Lalu miliki.",
        "hashtags": "#BrandPositioning #BrandStrategy #AudienceInsight #CreativeClarity",
    },
    {
        "title": "Untuk semua, bukan siapa-siapa.",
        "lines": ["UNTUK SEMUA,", "BUKAN", "SIAPA-SIAPA."],
        "label": "FOKUS",
        "pillar": "Focus",
        "caption": "Ketika ingin diterima semua orang, suara biasanya menjadi terlalu netral. Identitas yang berani memilih audiens dapat berbicara lebih hangat, lebih tajam, dan lebih bermakna. Fokus bukan mempersempit peluang; fokus memperjelas daya tarik.",
        "closing": "Pilih siapa yang ingin disentuh.",
        "hashtags": "#AudienceFocus #BrandPositioning #BrandVoice #StrategicBranding",
    },
    {
        "title": "Niche membuatmu lebih tajam.",
        "lines": ["NICHE", "MEMBUATMU", "LEBIH TAJAM."],
        "label": "NICHE",
        "pillar": "Positioning",
        "caption": "Fokus memperjelas keahlian, bahasa, dan standar yang ingin dibangun. Semakin jelas ruang yang dipilih, semakin mudah orang memahami alasan untuk memperhatikan. Niche memberi bentuk pada reputasi.",
        "closing": "Ketajaman datang dari pilihan.",
        "hashtags": "#NicheBrand #BrandFocus #PositioningStrategy #CreativeBusiness",
    },
    {
        "title": "Punya suara. Punya tempat.",
        "lines": ["PUNYA SUARA.", "PUNYA TEMPAT."],
        "label": "SUARA",
        "pillar": "Voice",
        "caption": "Suara yang jelas membuat pesan terasa berasal dari pribadi yang sama, meski topiknya berubah. Ia menentukan pilihan kata, tingkat keberanian, humor, kehangatan, dan batas. Suara bukan hiasan kalimat; suara adalah kehadiran.",
        "closing": "Bicaralah sampai mudah dikenali.",
        "hashtags": "#BrandVoice #ToneOfVoice #CreativeWriting #BrandPersonality",
    },
    {
        "title": "Nada membentuk rasa.",
        "lines": ["NADA", "MEMBENTUK", "RASA."],
        "label": "TONE",
        "pillar": "Tone of voice",
        "caption": "Pesan yang sama dapat terasa ramah, dingin, berani, atau membosankan bergantung pada nadanya. Tentukan rasa yang ingin ditinggalkan sebelum memilih kalimat. Nada yang tepat membuat komunikasi terdengar manusiawi.",
        "closing": "Orang merasakan sebelum menyimpulkan.",
        "hashtags": "#ToneOfVoice #BrandLanguage #BrandFeeling #CreativeDirection",
    },
    {
        "title": "Kepribadian bukan dekorasi.",
        "lines": ["KEPRIBADIAN", "BUKAN", "DEKORASI."],
        "label": "PERSONALITAS",
        "pillar": "Personality",
        "caption": "Kepribadian terlihat dari keputusan, bukan dari ornamen tambahan. Bagaimana sebuah bisnis menjawab, menyapa, memilih kata, dan menjaga standar menunjukkan siapa dirinya. Tampilan membantu, tetapi perilaku yang membuat karakter dipercaya.",
        "closing": "Karakter harus hadir dalam tindakan.",
        "hashtags": "#BrandPersonality #BrandBehavior #CreativeStrategy #BrandCulture",
    },
    {
        "title": "Rasa datang sebelum alasan.",
        "lines": ["RASA DATANG", "SEBELUM", "ALASAN."],
        "label": "EMOSI",
        "pillar": "Emotion",
        "caption": "Orang sering merasakan sesuatu lebih dulu sebelum mampu menjelaskannya. Warna, ruang, ritme, suara, dan sikap membangun kesan dalam hitungan detik. Karena itu, pengalaman emosional perlu dirancang dengan sengaja.",
        "closing": "Buat rasa yang ingin dikenang.",
        "hashtags": "#EmotionalBranding #BrandExperience #CreativeDirection #BrandFeeling",
    },
    {
        "title": "Cerita membuat orang tinggal.",
        "lines": ["CERITA", "MEMBUAT ORANG", "TINGGAL."],
        "label": "CERITA",
        "pillar": "Storytelling",
        "caption": "Cerita memberi konteks pada apa yang dilihat dan dirasakan. Ia menghubungkan detail menjadi alasan untuk peduli. Cerita terbaik tidak hanya menjelaskan siapa kita, tetapi mengajak orang menemukan bagian dirinya di dalamnya.",
        "closing": "Informasi lewat. Cerita menemani.",
        "hashtags": "#BrandStorytelling #BrandNarrative #CreativeCulture #BrandMeaning",
    },
    {
        "title": "Yang terasa akan diingat.",
        "lines": ["YANG TERASA", "AKAN", "DIINGAT."],
        "label": "INGATAN",
        "pillar": "Memory",
        "caption": "Ingatan jarang menyimpan semua detail. Ia menyimpan suasana, momen, dan perasaan yang paling kuat. Ciptakan satu pengalaman emosional yang jernih daripada memenuhi ruang dengan terlalu banyak pesan.",
        "closing": "Rasa adalah jalan menuju ingatan.",
        "hashtags": "#BrandMemory #EmotionalDesign #BrandExperience #CreativeStrategy",
    },
    {
        "title": "Konsisten bukan membosankan.",
        "lines": ["KONSISTEN", "BUKAN", "MEMBOSANKAN."],
        "label": "KONSISTENSI",
        "pillar": "Consistency",
        "caption": "Konsistensi bukan menyalin tampilan yang sama tanpa henti. Ia berarti menjaga prinsip sambil memberi ruang untuk bereksperimen. Kode tetap dikenali, tetapi ekspresinya terus bergerak.",
        "closing": "Tetap satu. Jangan diam.",
        "hashtags": "#BrandConsistency #VisualSystem #CreativeDirection #BrandGrowth",
    },
    {
        "title": "Ulangi kode, bukan pose.",
        "lines": ["ULANGI KODE,", "BUKAN POSE."],
        "label": "KODE",
        "pillar": "Consistency",
        "caption": "Kode visual memberi benang merah: proporsi, ritme, warna, cara memotret, dan cara menyusun kata. Kode dapat diulang tanpa membuat setiap karya terlihat kembar. Inilah cara identitas tetap luwes sekaligus mudah dikenali.",
        "closing": "Sistem memberi ruang untuk bermain.",
        "hashtags": "#VisualSystem #BrandCodes #ArtDirection #BrandConsistency",
    },
    {
        "title": "Ritme membentuk ingatan.",
        "lines": ["RITME", "MEMBENTUK", "INGATAN."],
        "label": "RITME",
        "pillar": "Consistency",
        "caption": "Ritme hadir dari pengulangan yang terukur. Ketika elemen khas muncul kembali dengan variasi yang tepat, orang mulai mengenali pola tanpa perlu melihat nama. Pengakuan tumbuh lewat kebiasaan yang dirancang.",
        "closing": "Ulangi dengan niat, bukan malas.",
        "hashtags": "#BrandRhythm #VisualIdentity #BrandRecall #CreativeSystem",
    },
    {
        "title": "Warna punya sikap.",
        "lines": ["WARNA", "PUNYA", "SIKAP."],
        "label": "WARNA",
        "pillar": "Color",
        "caption": "Warna bukan sekadar pemanis. Ia dapat terasa hangat, tajam, tenang, nakal, atau berani bahkan sebelum satu kalimat dibaca. Pilih warna berdasarkan kepribadian yang ingin dibangun, bukan hanya karena sedang populer.",
        "closing": "Pilih warna yang berani bersikap.",
        "hashtags": "#ColorStrategy #VisualIdentity #ArtDirection #BrandPersonality",
    },
    {
        "title": "Huruf juga punya suara.",
        "lines": ["HURUF JUGA", "PUNYA", "SUARA."],
        "label": "TIPOGRAFI",
        "pillar": "Typography",
        "caption": "Tipografi dapat berbisik, berbicara tegas, atau terasa terlalu kaku. Bentuk huruf, jarak, ukuran, dan ritme menentukan nada visual. Pilihan yang tepat membuat pesan terdengar bahkan sebelum benar-benar dibaca.",
        "closing": "Huruf adalah nada yang terlihat.",
        "hashtags": "#Typography #VisualVoice #GraphicDesign #BrandIdentity",
    },
    {
        "title": "Satu detail bisa melekat.",
        "lines": ["SATU DETAIL", "BISA", "MELEKAT."],
        "label": "DETAIL",
        "pillar": "Detail",
        "caption": "Satu detail yang khas sering lebih kuat daripada sepuluh elemen yang saling berebut. Bisa berupa bentuk, gestur, cara menyapa, atau momen kecil yang selalu hadir. Detail memberi titik jangkar bagi ingatan.",
        "closing": "Kecil bentuknya. Besar jejaknya.",
        "hashtags": "#BrandDetail #BrandMemory #CreativeDirection #ExperienceDesign",
    },
    {
        "title": "Konten butuh sudut pandang.",
        "lines": ["KONTEN BUTUH", "SUDUT", "PANDANG."],
        "label": "KONTEN",
        "pillar": "Content",
        "caption": "Topik bisa sama, tetapi sudut pandang membuatnya terasa milik sendiri. Jangan hanya bertanya apa yang sedang ramai. Tanyakan apa yang benar-benar kita percaya dan bagaimana cara melihatnya secara berbeda.",
        "closing": "Opini memberi konten tulang belakang.",
        "hashtags": "#ContentStrategy #PointOfView #CreativeContent #BrandVoice",
    },
    {
        "title": "Interaksi dimulai dari relevansi.",
        "lines": ["INTERAKSI", "DIMULAI DARI", "RELEVANSI."],
        "label": "INTERAKSI",
        "pillar": "Engagement",
        "caption": "Orang merespons ketika merasa dipahami, bukan ketika sekadar diminta berkomentar. Berikan gagasan yang dekat dengan pengalaman mereka, buka ruang untuk berpendapat, lalu hadir dalam percakapannya.",
        "closing": "Hubungan dimulai dari rasa nyambung.",
        "hashtags": "#AudienceEngagement #BrandCommunity #ContentStrategy #SocialCulture",
    },
    {
        "title": "Komunitas bukan kumpulan angka.",
        "lines": ["KOMUNITAS", "BUKAN KUMPULAN", "ANGKA."],
        "label": "KOMUNITAS",
        "pillar": "Community",
        "caption": "Komunitas tumbuh dari rasa memiliki, bahasa bersama, dan pertemuan yang bermakna. Ukuran dapat terlihat mengesankan, tetapi kedekatanlah yang membuat orang kembali dan mengajak orang lain.",
        "closing": "Bangun kedekatan, bukan keramaian kosong.",
        "hashtags": "#BrandCommunity #AudienceConnection #SocialCulture #BrandRelationship",
    },
    {
        "title": "Keramahan tinggal dalam detail.",
        "lines": ["KERAMAHAN", "TINGGAL DALAM", "DETAIL."],
        "label": "KERAMAHAN",
        "pillar": "Hospitality",
        "caption": "Keramahan sering hadir melalui hal yang tampak kecil: nada sambutan, perhatian pada kebiasaan, kejelasan arahan, atau kejutan sederhana. Detail membuat pelayanan terasa personal tanpa harus berlebihan.",
        "closing": "Perhatian kecil terasa sangat besar.",
        "hashtags": "#HospitalityExperience #GuestFeeling #ServiceCulture #ExperienceDesign",
    },
    {
        "title": "Suasana adalah janji diam.",
        "lines": ["SUASANA", "ADALAH", "JANJI DIAM."],
        "label": "SUASANA",
        "pillar": "Hospitality",
        "caption": "Suasana berbicara melalui cahaya, aroma, suara, tekstur, dan gerak orang di dalam ruang. Semuanya membentuk harapan tanpa perlu dijelaskan. Ketika suasana selaras dengan karakter, pengalaman terasa utuh.",
        "closing": "Ruang berbicara tanpa kalimat.",
        "hashtags": "#HospitalityDesign #Atmosphere #BrandExperience #SensoryDesign",
    },
    {
        "title": "Tamu mengingat cara merasa.",
        "lines": ["TAMU MENGINGAT", "CARA", "MERASA."],
        "label": "PENGALAMAN",
        "pillar": "Hospitality",
        "caption": "Tamu mungkin lupa detail percakapan atau urutan kejadian, tetapi mereka mengingat apakah merasa tenang, diperhatikan, dan diterima. Pengalaman terbaik dirancang dari emosi yang ingin ditinggalkan.",
        "closing": "Perasaan pulang lebih lama.",
        "hashtags": "#GuestExperience #HospitalityCulture #EmotionalDesign #ServiceExperience",
    },
    {
        "title": "Keaslian tidak butuh kostum.",
        "lines": ["KEASLIAN", "TIDAK BUTUH", "KOSTUM."],
        "label": "KEASLIAN",
        "pillar": "Authenticity",
        "caption": "Keaslian tidak perlu terlihat sempurna atau mengikuti persona yang sedang populer. Ia muncul ketika ucapan, tindakan, dan pengalaman berjalan searah. Orang dapat merasakan saat sesuatu dibuat-buat.",
        "closing": "Jujur terasa lebih kuat.",
        "hashtags": "#BrandAuthenticity #BrandCharacter #CreativeCulture #BrandTrust",
    },
    {
        "title": "Kepercayaan tumbuh dari kesesuaian.",
        "lines": ["KEPERCAYAAN", "TUMBUH DARI", "KESESUAIAN."],
        "label": "KEPERCAYAAN",
        "pillar": "Trust",
        "caption": "Kepercayaan muncul saat janji, penampilan, bahasa, dan pengalaman saling menguatkan. Ketidaksesuaian kecil yang berulang dapat mengikis keyakinan. Sebaliknya, keselarasan membuat orang merasa aman untuk kembali.",
        "closing": "Selaras berarti dapat dipercaya.",
        "hashtags": "#BrandTrust #BrandAlignment #BrandExperience #StrategicBranding",
    },
    {
        "title": "Brand hebat terasa hidup.",
        "lines": ["BRAND HEBAT", "TERASA", "HIDUP."],
        "label": "MANIFESTO",
        "pillar": "Manifesto",
        "caption": "Brand hidup ketika ia punya keyakinan, cara bergerak, suara, dan hubungan dengan manusia di sekitarnya. Ia dapat berubah mengikuti zaman tanpa kehilangan inti. Bukan sekadar tampilan, melainkan energi yang terus dirasakan.",
        "closing": "Bangun sesuatu yang bernapas.",
        "hashtags": "#BrandManifesto #LivingBrand #BrandCulture #CreativeDirection",
    },
]

# Launch with fifteen distinct visual worlds before presenting their companion
# variants. This keeps the first nine-post grid visually diverse.
POSTS = POSTS[::2] + POSTS[1::2]


def render_post(index: int, post: dict) -> Image.Image:
    pair = index if index <= 15 else index - 15
    bg_path = sorted(BG_DIR.glob(f"bg-{pair:02}-*.png"))[0]
    variant = 0 if index <= 15 else 1
    image = cover(bg_path, variant)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    layout = LAYOUTS[(index - 1) % len(LAYOUTS)]
    x1, y1, x2, y2 = layout["box"]
    panel = layout["panel"]
    if panel == CREAM:
        fill = (panel[0], panel[1], panel[2], 232)
    elif panel == BLACK:
        fill = (panel[0], panel[1], panel[2], 214)
    else:
        fill = (panel[0], panel[1], panel[2], 225)
    draw.rounded_rectangle((x1, y1, x2, y2), radius=20, fill=fill)
    draw.rectangle((x1, y1, x1 + 12, y2), fill=layout["accent"])

    label_font = font(20, "label")
    draw.text(
        (x1 + 44, y1 + 35),
        post["label"],
        font=label_font,
        fill=layout["accent"] if layout["text"] == CREAM else COBALT,
    )

    max_width = x2 - x1 - 88
    headline_font = fit_font(post["lines"], max_width, 128, 54)
    spacing = max(0, round(headline_font.size * -0.05))
    height = text_height(draw, post["lines"], headline_font, spacing)
    start_y = y1 + 88 + max(0, (y2 - y1 - 118 - height) // 2)
    draw_lines(
        draw,
        x1 + 44,
        start_y,
        post["lines"],
        headline_font,
        layout["text"],
        spacing,
    )

    # Contemporary registration mark: flat geometry, never retro ornament.
    mx = 938 if index % 2 else 88
    my = 118 if index % 3 else 1200
    draw.ellipse((mx, my, mx + 42, my + 42), fill=layout["accent"])
    draw.line((mx - 28, my + 21, mx + 70, my + 21), fill=layout["text"], width=4)

    return Image.alpha_composite(image, overlay).convert("RGB")


def schedule_for(index: int):
    launch = date(2026, 7, 30)
    if index <= 9:
        return launch.isoformat(), "SEKARANG", "ready_now"
    slots = {
        1: ["09:00", "11:00", "13:00", "15:00", "18:00", "21:00"],
        2: ["09:00", "12:00", "15:00", "18:00", "21:00"],
        3: ["09:00", "12:00", "15:00", "18:00", "21:00"],
        4: ["09:00", "12:00", "15:00", "18:00", "21:00"],
    }
    remaining = index - 10
    day = 1
    while remaining >= len(slots[day]):
        remaining -= len(slots[day])
        day += 1
    return (launch + timedelta(days=day)).isoformat(), slots[day][remaining], "scheduled"


plan = []
for index, post in enumerate(POSTS, 1):
    image = render_post(index, post)
    asset = f"posts/editorial-20260730/day-{index:02}.jpg"
    image.save(OUT / f"day-{index:02}.jpg", quality=95, subsampling=0, optimize=True)
    image.save(OUT / f"day-{index:02}.png", optimize=True)
    post_date, post_time, status = schedule_for(index)
    final_caption = f"{post['caption']}\n\n{post['closing']}\n\n{post['hashtags']}"
    plan.append(
        {
            "id": index,
            "date": post_date,
            "time_wib": post_time,
            "timezone": "Asia/Jakarta",
            "status": status,
            "approval_required": False,
            "format": "Surreal editorial",
            "pillar": post["pillar"],
            "title": post["title"],
            "subtitle": post["closing"],
            "caption": post["caption"],
            "cta": post["closing"],
            "hashtags": post["hashtags"],
            "diagram": "surreal_metaphor",
            "steps": [],
            "asset": asset,
            "public_asset_url": f"PUBLIC_ASSET_BASE_URL/{asset}",
            "final_caption": final_caption,
            "editorial_pair": index if index <= 15 else index - 15,
        }
    )

(PACK / "content-plan.json").write_text(
    json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

with (PACK / "content-plan.csv").open("w", encoding="utf-8", newline="") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=[
            "id",
            "date",
            "time_wib",
            "status",
            "pillar",
            "title",
            "caption",
            "cta",
            "hashtags",
            "asset",
        ],
    )
    writer.writeheader()
    for item in plan:
        writer.writerow({key: item[key] for key in writer.fieldnames})

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

print(f"Built {len(plan)} posts in {OUT}")

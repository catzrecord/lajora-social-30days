from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json, math

ROOT = Path('/Users/coong/Documents/lajora-social-30days')
OUT = ROOT / 'concept-posts-v3'
W, H = 1080, 1350
CREAM=(250,239,218,255); COBALT=(19,61,211,255); LIME=(201,255,55,255)
CORAL=(255,101,91,255); RED=(219,18,17,255); BLACK=(17,14,13,255); YELLOW=(255,205,0,255)
IMPACT='/System/Library/Fonts/Supplemental/Impact.ttf'
ARIAL_BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
ARIAL='/System/Library/Fonts/Supplemental/Arial.ttf'

def fnt(size, kind='impact'):
    return ImageFont.truetype(IMPACT if kind=='impact' else ARIAL_BOLD if kind=='bold' else ARIAL, size)

def cover(path):
    im=Image.open(path).convert('RGB')
    scale=max(W/im.width,H/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
    l=(im.width-W)//2; t=(im.height-H)//2
    return im.crop((l,t,l+W,t+H)).convert('RGBA')

def rotated_plate(text, font, fg, bg, angle, pad=(30,14), stroke=0, stroke_fill=None):
    dummy=Image.new('RGBA',(10,10)); d=ImageDraw.Draw(dummy)
    box=d.textbbox((0,0),text,font=font,stroke_width=stroke)
    tw,th=box[2]-box[0],box[3]-box[1]
    plate=Image.new('RGBA',(tw+2*pad[0],th+2*pad[1]),bg)
    pd=ImageDraw.Draw(plate)
    pd.text((pad[0]-box[0],pad[1]-box[1]),text,font=font,fill=fg,stroke_width=stroke,stroke_fill=stroke_fill or fg)
    return plate.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)

def draw_shadow_text(d, pos, text, font, fill, shadow, off=(9,9), stroke=0, stroke_fill=None):
    x,y=pos
    d.text((x+off[0],y+off[1]),text,font=font,fill=shadow,stroke_width=stroke,stroke_fill=shadow)
    d.text((x,y),text,font=font,fill=fill,stroke_width=stroke,stroke_fill=stroke_fill or fill)

def post1():
    im=cover(OUT/'backgrounds/attention-vs-booking.png')
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    # Tactile editorial markers framing the center-safe headline.
    d.ellipse((62,170,112,220),fill=LIME)
    d.line((85,195,183,195),fill=BLACK,width=8)
    draw_shadow_text(d,(82,215),'RAMAI',fnt(172),COBALT,LIME,off=(10,10))
    plate=rotated_plate('BELUM TENTU',fnt(43,'bold'),CREAM,BLACK,-4,pad=(34,15))
    ov.alpha_composite(plate,(518,388))
    draw_shadow_text(d,(84,476),'LAKU.',fnt(195),CREAM,COBALT,off=(11,13),stroke=4,stroke_fill=BLACK)
    # Small provocative label; still no brand identity.
    d.rounded_rectangle((82,735,381,786),radius=25,fill=LIME)
    d.text((231,761),'PERHATIAN ≠ KONVERSI',font=fnt(19,'bold'),fill=BLACK,anchor='mm')
    # Graphic registration marks.
    d.line((950,225,1005,225),fill=BLACK,width=7); d.line((977,198,977,252),fill=BLACK,width=7)
    d.ellipse((927,1075,1010,1158),outline=CREAM,width=6)
    d.ellipse((956,1104,981,1129),fill=CORAL)
    return Image.alpha_composite(im,ov).convert('RGB')

def post2():
    im=cover(OUT/'backgrounds/owned-booking-path.png')
    ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    # Headline stays well inside Instagram's square grid crop.
    draw_shadow_text(d,(78,170),'PUNYA',fnt(126),CREAM,COBALT,off=(9,10))
    draw_shadow_text(d,(78,292),'SISTEM.',fnt(158),YELLOW,BLACK,off=(10,12),stroke=3,stroke_fill=BLACK)
    plate=rotated_plate('PUNYA KENDALI.',fnt(58,'bold'),CREAM,COBALT,3,pad=(32,16))
    ov.alpha_composite(plate,(74,918))
    # Rhythmic system line and playful marks.
    d.rounded_rectangle((76,1083,741,1141),radius=28,fill=CREAM)
    d.text((408,1112),'WEBSITE  •  BOOKING  •  PAYMENT  •  DATA',font=fnt(19,'bold'),fill=BLACK,anchor='mm')
    d.ellipse((908,174,985,251),fill=LIME)
    d.text((946,211),'→',font=fnt(50,'bold'),fill=BLACK,anchor='mm')
    d.line((83,1206,330,1206),fill=CREAM,width=8)
    d.ellipse((333,1194,358,1219),fill=YELLOW)
    return Image.alpha_composite(im,ov).convert('RGB')

assets=[]
for im,slug in [(post1(),'01-ramai-belum-tentu-laku'),(post2(),'02-punya-sistem-punya-kendali')]:
    png=OUT/f'{slug}.png'; jpg=OUT/f'{slug}.jpg'
    im.save(png,optimize=True)
    im.save(jpg,quality=95,subsampling=0,optimize=True)
    assets.append({'png':png.name,'jpg':jpg.name})

captions=[
  {
    'asset':'01-ramai-belum-tentu-laku.jpg',
    'headline':'Ramai belum tentu laku.',
    'caption':'Likes memberi perhatian. Sistem yang tepat mengubah perhatian menjadi pemesanan.\n\nKonten perlu terhubung ke website yang cepat, informasi yang jelas, proses booking yang ringkas, dan pembayaran yang terasa aman. Tanpa jalur konversi, traffic hanya datang lalu pergi.\n\nPerhatian adalah awal. Booking adalah hasil.\n\n#HospitalityMarketing #DirectBooking #DigitalStrategy #BookingSystem'
  },
  {
    'asset':'02-punya-sistem-punya-kendali.jpg',
    'headline':'Punya sistem. Punya kendali.',
    'caption':'Website sendiri memberi bisnis kendali atas seluruh perjalanan tamu: menemukan kamar, memilih tanggal, membayar, menerima konfirmasi, hingga kembali menginap.\n\nKetika website, booking, payment, dan data terhubung, bisnis tidak hanya mendapatkan transaksi. Bisnis membangun hubungan yang bisa tumbuh.\n\nMiliki jalurnya. Kenali tamunya. Tumbuhkan bisnisnya.\n\n#HospitalityBusiness #BookingEngine #PaymentGateway #GuestJourney'
  }
]
(OUT/'CAPTIONS.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2)+'\n')
(OUT/'CAPTION-SIAP-POSTING.txt').write_text('\n\n'.join(f"POSTINGAN {i+1}\n\n{x['headline']}\n\n{x['caption']}" for i,x in enumerate(captions))+'\n')
print(json.dumps({'assets':assets,'captions':len(captions)},indent=2))

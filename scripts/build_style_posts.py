from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'concept-posts-v2'
W,H=1080,1350
CHARCOAL='#11110F';CREAM='#F4F0E8';LIME='#C9F47D';CORAL='#FF8264';GREEN='#123E33'
FONT_REG='/System/Library/Fonts/HelveticaNeue.ttc'
FONT_BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'


def cover(im, size=(W,H), anchor='center'):
    im=im.convert('RGB')
    scale=max(size[0]/im.width,size[1]/im.height)
    nw,nh=round(im.width*scale),round(im.height*scale)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    left=(nw-size[0])//2
    if anchor=='top': top=0
    elif anchor=='bottom': top=nh-size[1]
    else: top=(nh-size[1])//2
    return im.crop((left,top,left+size[0],top+size[1]))

def font(size,bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG,size=size)

def brand(draw,x,y,dark=False):
    color=CHARCOAL if dark else CREAM
    r=25
    draw.ellipse((x,y,x+2*r,y+2*r),outline=color,width=3)
    draw.text((x+15,y+5),'L',font=font(31),fill=color,anchor='la')
    draw.ellipse((x+36,y+5,x+47,y+16),fill=CORAL)
    draw.ellipse((x+40,y+37,x+49,y+46),fill=LIME)
    draw.text((x+68,y+6),'LAJORA',font=font(22,True),fill=color,anchor='la')

def line_text(draw,xy,lines,fnt,fill,spacing=4,anchor=None):
    x,y=xy
    for line in lines:
        draw.text((x,y),line,font=fnt,fill=fill,anchor=anchor)
        box=draw.textbbox((x,y),line,font=fnt,anchor=anchor)
        y += (box[3]-box[1])+spacing
    return y

def post1():
    bg=cover(Image.open(OUT/'backgrounds/direct-booking-bg.png'))
    layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    # Quiet editorial headline field, safely inset for grid preview.
    d.rounded_rectangle((92,72,665,430),radius=34,fill=(17,17,15,222),outline=(244,240,232,36),width=2)
    brand(d,130,108,dark=False)
    d.text((130,188),'DIRECT BOOKING / 01',font=font(18,True),fill=LIME)
    line_text(d,(130,230),['Booking langsung.','Data tetap milikmu.'],font(58,True),CREAM,spacing=0)
    d.text((132,374),'Website  •  Booking  •  Payment  •  Guest Data',font=font(18),fill=(244,240,232,205))
    # Footer CTA plate, simple and premium.
    d.rounded_rectangle((96,1226,512,1305),radius=38,fill=(17,17,15,232),outline=(201,244,125,130),width=2)
    d.ellipse((119,1246,138,1265),fill=LIME)
    d.text((158,1240),'Bangun owned system-mu',font=font(20,True),fill=CREAM)
    d.text((158,1269),'lajora.web.id',font=font(16),fill=(244,240,232,190))
    return Image.alpha_composite(bg.convert('RGBA'),layer).convert('RGB')

def post2():
    bg=cover(Image.open(OUT/'backgrounds/guest-journey-bg.png'))
    layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    # Warm-cream headline panel follows the image architecture.
    d.rounded_rectangle((92,72,747,404),radius=34,fill=(244,240,232,224),outline=(17,17,15,38),width=2)
    brand(d,130,108,dark=True)
    d.text((130,188),'GUEST JOURNEY / 02',font=font(18,True),fill=GREEN)
    line_text(d,(130,228),['Dari perhatian','menjadi booking.'],font(61,True),CHARCOAL,spacing=-2)
    d.text((132,364),'Konten  •  Website  •  Payment  •  Relasi Tamu',font=font(18),fill=(17,17,15,190))
    # Bottom manifesto strip stays inside grid-safe zone.
    d.rounded_rectangle((92,1220,988,1308),radius=34,fill=(17,17,15,236),outline=(244,240,232,32),width=2)
    d.text((130,1242),'Jangan berhenti di traffic.',font=font(23,True),fill=CREAM)
    d.text((130,1272),'Bangun hubungan yang bisa tumbuh.',font=font(17),fill=(244,240,232,190))
    d.rounded_rectangle((804,1241,947,1288),radius=22,fill=LIME)
    d.text((875,1264),'LAJORA',font=font(16,True),fill=CHARCOAL,anchor='mm')
    return Image.alpha_composite(bg.convert('RGBA'),layer).convert('RGB')

p1=post1();p2=post2()
for im,name in [(p1,'lajora-direct-booking-01'),(p2,'lajora-guest-journey-02')]:
    im.save(OUT/f'{name}.png',quality=95)
    im.save(OUT/f'{name}.jpg',quality=94,subsampling=0,optimize=True)

captions=[
  {
    'asset':'lajora-direct-booking-01.jpg',
    'title':'Booking langsung. Data tetap milikmu.',
    'caption':'Website milik sendiri bukan hanya etalase. Ia bisa menghubungkan ketersediaan kamar, proses booking, payment gateway, konfirmasi otomatis, dan data tamu dalam satu alur yang kamu kendalikan.\n\nMarketplace membantu distribusi. Owned system membantu bisnis membangun margin, data, dan hubungan jangka panjang.\n\nBangun sistem direct booking untuk bisnismu di lajora.web.id\n\n#DirectBooking #HospitalityWebsite #BookingEngine #PaymentGateway #Lajora'
  },
  {
    'asset':'lajora-guest-journey-02.jpg',
    'title':'Dari perhatian menjadi booking.',
    'caption':'Konten yang bagus menghasilkan perhatian. Website mengubah perhatian menjadi minat. Booking dan payment menyelesaikan transaksi. Data membantu bisnis menjaga hubungan setelah tamu pulang.\n\nKetika seluruh tahap terhubung, pemasaran tidak berhenti pada likes dan traffic—tetapi bergerak sampai booking dan repeat guest.\n\nBangun guest journey yang utuh bersama Lajora.\n\n#GuestJourney #HospitalityMarketing #DirectBooking #GuestData #Lajora'
  }
]
(OUT/'captions.json').write_text(json.dumps(captions,ensure_ascii=False,indent=2)+'\n')
print('Built',', '.join(x['asset'] for x in captions))

#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'profile-assets'; OUT.mkdir(parents=True,exist_ok=True)
INK='#11110f'; PAPER='#f4f0e8'; LIME='#c9f47d'; ORANGE='#ff8a66'
FONT='/System/Library/Fonts/SFNS.ttf'
def f(s): return ImageFont.truetype(FONT,s)
# Avatar: simple enough to remain legible at 32px.
im=Image.new('RGB',(1080,1080),INK); d=ImageDraw.Draw(im)
d.ellipse((145,145,935,935),outline=PAPER,width=18)
d.text((366,255),'L',font=f(470),fill=PAPER)
d.ellipse((720,255,810,345),fill=ORANGE)
d.ellipse((790,790,860,860),fill=LIME)
im.save(OUT/'lajora-avatar.png',quality=98)
svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080"><rect width="1080" height="1080" fill="{INK}"/><circle cx="540" cy="540" r="395" fill="none" stroke="{PAPER}" stroke-width="18"/><text x="365" y="710" fill="{PAPER}" font-family="-apple-system,BlinkMacSystemFont,Arial" font-size="470" font-weight="600">L</text><circle cx="765" cy="300" r="45" fill="{ORANGE}"/><circle cx="825" cy="825" r="35" fill="{LIME}"/></svg>'''
(OUT/'lajora-avatar.svg').write_text(svg)
# Highlight covers
icons={
 'branding':('B','Brand'),
 'website':('W','Website'),
 'booking':('↗','Booking'),
 'payment':('P','Payment'),
 'social':('S','Social'),
 'contact':('@','Contact'),
}
for i,(name,(symbol,label)) in enumerate(icons.items()):
 bg=INK if i%2==0 else PAPER; fg=PAPER if bg==INK else INK; accent=LIME if i%3 else ORANGE
 img=Image.new('RGB',(1080,1920),bg); q=ImageDraw.Draw(img)
 q.ellipse((250,620,830,1200),outline=accent,width=16)
 box=q.textbbox((0,0),symbol,font=f(260)); x=(1080-(box[2]-box[0]))/2; y=780
 q.text((x,y),symbol,font=f(260),fill=fg)
 box=q.textbbox((0,0),label.upper(),font=f(48)); q.text(((1080-(box[2]-box[0]))/2,1310),label.upper(),font=f(48),fill=fg)
 q.ellipse((504,1435,576,1507),fill=accent)
 img.save(OUT/f'highlight-{name}.png',quality=98)
print('built',len(list(OUT.iterdir())),'profile assets in',OUT)

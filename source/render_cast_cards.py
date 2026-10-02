#!/usr/bin/env python3
"""Diagnostic atlas layout; this output is not a Mesen runtime screenshot."""
from pathlib import Path
import sys
from PIL import Image, ImageDraw

if len(sys.argv)!=3:
    raise SystemExit('usage: python3 source/render_cast_cards.py HF14_PRIVATE.ws OUT.png')
b=Path(sys.argv[1]).read_bytes()
e=0x1E0000

def glyph(word):
    im=Image.new('RGB',(8,16),'#f8f8f8')
    for t in range(2):
        o=0x1F0000+(word+t*16)*16
        for y in range(8):
            a,c=b[o+y*2:o+y*2+2]
            for x in range(8):
                if ((a>>(7-x))&1)|(((c>>(7-x))&1)<<1):
                    im.putpixel((x,y+t*8),(20,20,20))
    return im

count=int.from_bytes(b[e+0x01de:e+0x01e0],'little')
assert count==0x39
words=[int.from_bytes(b[e+0x01e0+i*2:e+0x01e2+i*2],'little') for i in range(count)]
im=Image.new('RGB',(240,13*40),'#dedede')
d=ImageDraw.Draw(im)
for i in range(13):
    p=int.from_bytes(b[e+0x057a+i*2:e+0x057c+i*2],'little')
    row=b[e+p:b.index(0xff,e+p)].split(b'\xfe')
    d.text((3,i*40+8),f'{i:02}',fill='black')
    for j,line in enumerate(row):
        for k,v in enumerate(line):
            im.paste(glyph(words[v]),(20+8*k,i*40+2+16*j))
im.resize((720,1560),resample=Image.Resampling.NEAREST).save(sys.argv[2])

#!/usr/bin/env python3
"""HF17: native-type localization of the orientation and controls bitmap.

Reconstructs HF16 from the clean Japanese ROM, then patches bounded tilemaps
and private tiles in bank 0x30000. Complete EN-US build; still development.
"""
from pathlib import Path
from collections import defaultdict
import hashlib, json, sys

from build_phase4w_hf16 import build as build_hf16
from build_phase4w_hf2 import decode_tile, encode_tile, glyph_8x16, ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

SHA_HF16='1be7103b2c0c5c4577a89706560115196357c8b43db35b835e184a459f68b95a'
MAPS=(0x307E0,0x30BD0)
GFX_BASE=0x307C0
PRIVATE=0x1AE
BLANK=0x0F7
TEXT=('HOLD THE','CONSOLE ','UPRIGHT ')
LABELS=(('MOVE',16,172,(12,52,172,190)),
        ('ATTACK',86,172,(82,139,172,190)),
        ('JUMP',94,190,(82,139,190,208)))
CLEAR_AREAS=((8,56,170,192),(80,140,170,190),(64,140,190,209))

def sha(x):return hashlib.sha256(x).hexdigest()
def cw(tile):return [[tile[7-x][y] for x in range(8)] for y in range(8)]
def ccw(tile):return [[tile[x][7-y] for x in range(8)] for y in range(8)]

def render_plane(rom,mb):
    screen=[[3]*144 for _ in range(224)]
    for r in range(18):
        for c in range(28):
            p=mb+2*(r*28+c);word=int.from_bytes(rom[p:p+2],'little');tile=word&0x1ff
            if tile<0x80:continue
            native=decode_tile(rom[GFX_BASE+tile*16:GFX_BASE+(tile+1)*16])
            upright=ccw(native)
            if word&0x4000:upright=list(reversed(upright))
            if word&0x8000:upright=[row[::-1] for row in upright]
            y0=224-8*(c+1)
            for y in range(8):screen[y0+y][r*8:r*8+8]=upright[y]
    return screen

def draw_labels(base,old,b,next_tile):
    mb=MAPS[0]
    before=render_plane(old,mb)
    after=[row.copy() for row in before]
    for x1,x2,y1,y2 in CLEAR_AREAS:
        for y in range(y1,y2):
            for x in range(x1,x2):after[y][x]=3
    for word,x0,y0,box in LABELS:
        x1,x2,y1,y2=box
        for x in range(x1,x2):after[y1][x]=after[y2-1][x]=0
        for y in range(y1,y2):after[y][x1]=after[y][x2-1]=0
        for i,ch in enumerate(word):
            glyph=glyph_8x16(base,ch)
            for gy,row in enumerate(glyph):
                for gx,v in enumerate(row):
                    if v:after[y0+gy][x0+i*8+gx]=0 if v==1 else 1
    changed=[];new_graphics={}
    for r in range(18):
        for c in range(28):
            y0=224-8*(c+1);x0=r*8
            prior=[row[x0:x0+8] for row in before[y0:y0+8]]
            target=[row[x0:x0+8] for row in after[y0:y0+8]]
            if prior==target:continue
            p=mb+2*(r*28+c);word=int.from_bytes(old[p:p+2],'little')
            # Bit 14 mirrors native X, which becomes upright Y after
            # the console's portrait rotation. Counter it before encoding.
            assert not (word&0x8000),'unmapped second tile-flip attribute'
            raw=encode_tile(cw(list(reversed(target)) if (word&0x4000) else target))
            if raw in new_graphics:t=new_graphics[raw]
            else:
                t=next_tile;next_tile+=1
                assert t<0x200,'not enough isolated resource tiles'
                new_graphics[raw]=t
                off=GFX_BASE+t*16
                b[off:off+16]=raw
            assert word&0x1ff>=0x80
            b[p:p+2]=((word&~0x1ff)|t).to_bytes(2,'little')
            changed.append((r,c,t))
    return changed,next_tile

def build(base):
    old,_,_=build_hf16(base)
    assert sha(old)==SHA_HF16
    b=bytearray(old)
    maps=[old[0x30000+i*0x3F0:0x30000+(i+1)*0x3F0] for i in range(4)]
    used={int.from_bytes(m[i:i+2],'little')&0x1FF for m in maps for i in range(0,len(m),2)}
    assert used.isdisjoint(range(PRIVATE,0x200))
    blank=decode_tile(old[GFX_BASE+BLANK*16:GFX_BASE+(BLANK+1)*16])
    chars=sorted(set(''.join(TEXT))-{ ' '})
    ids={(ch,half):PRIVATE+i*2+half for i,ch in enumerate(chars) for half in range(2)}
    assert max(ids.values())<0x200
    for ch in chars:
        gl=glyph_8x16(base,ch)
        for half in range(2):
            source=cw(gl[half*8:(half+1)*8])
            tile=[[0 if v==1 else 1 if v==2 else blank[y][x] for x,v in enumerate(row)] for y,row in enumerate(source)]
            t=ids[ch,half];p=GFX_BASE+t*16
            b[p:p+16]=encode_tile(tile)
    for mb in MAPS:
        assert old[mb+2*(4*28+15):mb+2*(4*28+24)]==bytes.fromhex('c506c606c706c806c906ca06cb06cc06cd06')
        # The Japanese notice occupies output x32..103, y40..103.
        for r in range(4,13):
            for c in range(15,23):
                p=mb+2*(r*28+c)
                word=int.from_bytes(old[p:p+2],'little')
                assert 0x80<=(word&0x1ff)<PRIVATE
                ch=' ';half=0
                if 4<=r<12 and 16<=c<=21:
                    line=(21-c)//2
                    half=(21-c)%2
                    ch=TEXT[line][r-4]
                tile=ids[ch,half] if ch!=' ' else BLANK
                b[p:p+2]=((word&~0x1FF)|tile).to_bytes(2,'little')
    label_tiles,next_tile=draw_labels(base,old,b,PRIVATE+len(chars)*2)
    b[-2:]=ws_checksum(b).to_bytes(2,'little')
    return bytes(b),{'panel_lines':TEXT,'private_char_tiles':ids,'checksum':f'0x{ws_checksum(b):04X}',
        'labels':[x[0] for x in LABELS],'label_tiles':label_tiles,'next_free_tile':next_tile,
        'changed_bytes_from_hf16':sum(x!=y for x,y in zip(old,b))}

def main():
    if len(sys.argv)<2:
        raise SystemExit('usage: python3 source/build_phase4w_hf17.py CLEAN_JP.ws [HF17.ws] [HF17_FROM_JP.bps]')
    base=Path(sys.argv[1]).read_bytes()
    out,info=build(base)
    patch=bps_create(base,out)
    if bps_apply(base,patch)!=out:raise SystemExit('cumulative BPS replay mismatch')
    if len(sys.argv)>2:Path(sys.argv[2]).write_bytes(out)
    if len(sys.argv)>3:Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base),'hf17_sha256':sha(out),
       'cumulative_bps_sha256':sha(patch),'checksum':info['checksum'],
       'changed_bytes_from_hf16':info['changed_bytes_from_hf16'],
       'panel_lines':info['panel_lines'],'labels':info['labels'],
       'private_tile_range':f'0x{PRIVATE:03X}..0x{info["next_free_tile"]-1:03X}',
       'new_label_cell_references':len(info['label_tiles'])},indent=2))

if __name__=='__main__':main()

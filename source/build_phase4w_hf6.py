#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
from build_phase4w_hf5 import build as build_hf5
from build_phase4w_hf2 import ws_checksum, decode_tile, encode_tile, SEGD, SIZE, EXPECTED_JP

EXPECTED_HF5='3c1f578cbc198c9628944287a7b3bdab5a68126e62736d53e0fc694935c01710'
ARTHUR_HEADER_OFF=SEGD+0xF8F7
ARTHUR_TILES=23
PROMPT_TOP_OFF=0x1FB1D2
PROMPT_BOTTOM_OFF=0x1FB2A2
PROMPT_CHARS='USE PASSWORD'

FONT5X7={
 'A':['01110','10001','10001','11111','10001','10001','10001'],
 'D':['11110','10001','10001','10001','10001','10001','11110'],
 'E':['11111','10000','10000','11110','10000','10000','11111'],
 'H':['10001','10001','10001','11111','10001','10001','10001'],
 'O':['01110','10001','10001','10001','10001','10001','01110'],
 'P':['11110','10001','10001','11110','10000','10000','10000'],
 'R':['11110','10001','10001','11110','10100','10010','10001'],
 'S':['01111','10000','10000','01110','00001','00001','11110'],
 'T':['11111','00100','00100','00100','00100','00100','00100'],
 'U':['10001','10001','10001','10001','10001','10001','01110'],
 'W':['10001','10001','10001','10101','10101','11011','10001'],
 ' ':['00000']*7,
}

def sha(b): return hashlib.sha256(b).hexdigest()

def draw_5x7_scaled(canvas, text, x0, y0, fg=0, scale_y=2, gap=1):
    x=x0
    for ch in text:
        pat=FONT5X7[ch]
        for ry,row in enumerate(pat):
            for rx,c in enumerate(row):
                if c=='1':
                    for sy in range(scale_y):
                        yy=y0+ry*scale_y+sy
                        xx=x+rx
                        if 0<=yy<len(canvas) and 0<=xx<len(canvas[0]):
                            canvas[yy][xx]=fg
        x += 5+gap
    return x-x0-gap if text else 0

def patch_arthur_header_legible(b):
    base=ARTHUR_HEADER_OFF
    # Runtime tilemap mapping for this 8x3 header.  The third row reuses
    # resource tile #2 twice, so a 16px-high title corrupts/repeats its lower
    # half.  HF6 fixes the root cause by using a native-sized 5x7 title in the
    # middle row only and by clearing the stale lower-row text cells.
    visual_to_resource=list(range(8))+list(range(8,16))+[16,17,2,18,2,19,20,21]
    tiles=[decode_tile(b[base+i*16:base+(i+1)*16]) for i in range(ARTHUR_TILES)]
    pix=[[3]*64 for _ in range(24)]
    for v,ri in enumerate(visual_to_resource):
        tx=v%8; ty=v//8; tile=tiles[ri]
        for y in range(8):
            for x in range(8): pix[ty*8+y][tx*8+x]=tile[y][x]
    # Preserve top ornament row. Clear only the former English text interior
    # in rows 2/3, retaining the far-edge decoration.
    for y in range(8,24):
        for x in range(3,61): pix[y][x]=3
    title='ARTHUR'
    width=len(title)*5+(len(title)-1)
    x0=(64-width)//2
    y0=9
    draw_5x7_scaled(pix,title,x0,y0,fg=0,scale_y=1,gap=1)
    # Middle row maps 1:1 to resource tiles 8..15.
    for col,ri in enumerate(range(8,16)):
        tile=[[pix[8+y][col*8+x] for x in range(8)] for y in range(8)]
        b[base+ri*16:base+(ri+1)*16]=encode_tile(tile)
    # Clear/rebuild the unique tiles used by the lower row. Resource #2 is
    # shared with the untouched top row and is left intact; it is already a
    # background tile at the reused lower-row positions.
    lower_unique=[(0,16),(1,17),(3,18),(5,19),(6,20),(7,21)]
    for col,ri in lower_unique:
        tile=[[pix[16+y][col*8+x] for x in range(8)] for y in range(8)]
        b[base+ri*16:base+(ri+1)*16]=encode_tile(tile)
    return {'offset':f'0x{base:X}','title':title,'font':'custom 5x7 native-height','x0':x0,'y0':y0,'width':width,
            'runtime_map':visual_to_resource,'reason':'avoid third-row shared-tile aliasing'}

def make_prompt_glyph(ch):
    # 8x16 cell: background index 3, high-contrast foreground index 0.
    pix=[[3]*8 for _ in range(16)]
    if ch!=' ':
        pat=FONT5X7[ch]
        x0=1
        y0=1
        for ry,row in enumerate(pat):
            for rx,c in enumerate(row):
                if c=='1':
                    for sy in (0,1):
                        pix[y0+ry*2+sy][x0+rx]=0
    top=[row[:] for row in pix[:8]]
    bottom=[row[:] for row in pix[8:16]]
    return encode_tile(top), encode_tile(bottom)

def patch_password_prompt_legible(b):
    # Existing tilemap uses 12 private cells in this order:
    # U S E [blank spacer] P A S S W O R D. Keep the map untouched.
    order=['U','S','E',' ','P','A','S','S','W','O','R','D']
    for i,ch in enumerate(order):
        top,bottom=make_prompt_glyph(ch)
        b[PROMPT_TOP_OFF+i*16:PROMPT_TOP_OFF+(i+1)*16]=top
        b[PROMPT_BOTTOM_OFF+i*16:PROMPT_BOTTOM_OFF+(i+1)*16]=bottom
    return {
      'top_offset':f'0x{PROMPT_TOP_OFF:X}',
      'bottom_offset':f'0x{PROMPT_BOTTOM_OFF:X}',
      'cells':len(order),'order':'USE [space] PASSWORD',
      'font':'custom 5x7, vertical x2, palette fg=0/bg=3',
      'scope':'prompt glyph cells only; tilemap, YES/NO and control flow unchanged'
    }

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf5,_,d5=build_hf5(base)
    if sha(hf5)!=EXPECTED_HF5:
        raise SystemExit('HF5 reconstruction mismatch: '+sha(hf5))
    b=bytearray(hf5)
    a=patch_arthur_header_legible(b)
    p=patch_password_prompt_legible(b)
    b[-2:]=(ws_checksum(b)).to_bytes(2,'little')
    return bytes(b),hf5,{'hf5':d5,'arthur_header_hf6':a,'password_prompt_hf6':p}

def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf6.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes()
    outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF6_PRIVATE.ws')
    out,hf5,details=build(base); outp.write_bytes(out)
    print(json.dumps({
      'phase':'Phase4W-HF6','base_sha256':sha(base),'hf5_sha256':sha(hf5),
      'target_sha256':sha(out),'size':len(out),
      'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}',
      'checksum_recalc':f'0x{ws_checksum(out):04X}','details':details
    },indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""HF19: localize the enemy-library erase confirmation graphic."""
from pathlib import Path
import json, sys
from hashlib import sha256

from build_phase4w_hf18 import build as build_hf18, sha
from build_phase4w_hf2 import encode_tile, glyph_8x16, ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

EXPECTED_HF18='0ee826c9d1c98b3b2e02a525dd9a089a961be48e0cea5c9a2d55b8421e807c25'
RESOURCE=0x1C0405  # C000:0405, copied to WRAM graphics 0x2800..0x36BF
LAYOUT=(('ERASE ALL',94,118,12,12),('ENEMY DATA?',140,162,13,4))
OLD_SHA=(
 'f6e169685604c41f0f1f00aae9ab03bc1b0a238d6d4abd9e3774777194984daa',
 '919b16860e576ca2bdd2cb552983ec80dcab6edc7a127a4d07b5916912287086',
 'aa31b81e1d4fc99b55141114ab69c5ef681b9e1617a3d0c99e07478c9ca918ae',
 'bb03315d205ad2e96ab0aeeeec7d480aa033baec08d47cc475e97d2c7e7ae27c',
)

def sha_part(data):return sha256(data).hexdigest()

def build(base):
    old,_,_=build_hf18(base)
    if sha(old)!=EXPECTED_HF18:raise SystemExit('HF18 signature mismatch')
    rows=((94,12),(118,12),(140,13),(162,13))
    for (index,cells),expected in zip(rows,OLD_SHA):
        begin=RESOURCE+index*16;end=begin+cells*16
        if old[begin:end]!=base[begin:end] or sha_part(old[begin:end])!=expected:
            raise SystemExit(f'prompt tile precondition mismatch at {begin:06X}')
    out=bytearray(old)
    for line,top,bottom,cells,x0 in LAYOUT:
        assert len(line)*8+x0<=cells*8
        pix=[[1]*(cells*8) for _ in range(16)]
        for i,ch in enumerate(line):
            if ch==' ':continue
            glyph=glyph_8x16(base,ch)
            for y,row in enumerate(glyph):
                for x,v in enumerate(row):
                    if v:pix[y][x0+i*8+x]=0 if v==1 else 3
        for half,index in enumerate((top,bottom)):
            for c in range(cells):
                p=RESOURCE+(index+c)*16
                tile=[row[c*8:(c+1)*8] for row in pix[half*8:(half+1)*8]]
                out[p:p+16]=encode_tile(tile)
    out[-2:]=ws_checksum(out).to_bytes(2,'little')
    return bytes(out),old,{'prompt':['ERASE ALL','ENEMY DATA?'],
      'resource':'C000:0405','graphics_rows':[(f'0x{RESOURCE+n*16:X}',cells) for n,cells in rows],
      'changed_bytes_from_hf18':sum(a!=b for a,b in zip(old,out)),
      'checksum':f'0x{ws_checksum(out):04X}'}

def main():
    if len(sys.argv)<2:raise SystemExit('usage: python3 source/build_phase4w_hf19.py CLEAN_JP.ws [HF19.ws] [JP_TO_HF19.bps]')
    base=Path(sys.argv[1]).read_bytes()
    out,old,detail=build(base)
    patch=bps_create(base,out)
    if bps_apply(base,patch)!=out:raise SystemExit('BPS replay mismatch')
    if len(sys.argv)>2:Path(sys.argv[2]).write_bytes(out)
    if len(sys.argv)>3:Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base),'hf18_sha256':sha(old),
      'hf19_sha256':sha(out),'bps_sha256':sha(patch),**detail},indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""HF20: repair the first book's contents heading with native Latin glyphs."""
from pathlib import Path
from hashlib import sha256
import json,sys

from build_phase4w_hf19 import build as build_hf19,sha
from build_phase4w_hf2 import glyph_8x16,encode_tile,ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

EXPECTED_HF19='a924932e2aac1f3350badb3f82fe946d716a6abd1474e4cbd3bc86214227e22b'
# The 48x16 area occupies six consecutive tiles in each of two rows.
ROWS=(0x1FBBF9,0x1FBD69)
OLD_SHA=(
 '8a94fac44bf61281bb65fb5f0237ea847fe0404cfe7680272f16cdf16d10fb56',
 'e73b95f253f882db0e82e3382212e2a84bfddf9ec227a7cde1eba09a0923aa39',
)
HEADING='INDEX'

def build(base):
    old,_,_=build_hf19(base)
    if sha(old)!=EXPECTED_HF19:raise SystemExit('HF19 signature mismatch')
    for start,expected in zip(ROWS,OLD_SHA):
        if sha256(old[start:start+96]).hexdigest()!=expected:
            raise SystemExit(f'Arthur index graphic precondition mismatch: {start:06X}')
    out=bytearray(old)
    # Draw five 8x16 native glyphs within the original 6x2 tile heading field.
    # The book graphic uses inverse palette indices relative to the native font.
    palette={0:3,1:0,2:1,3:2}
    pixels=[[3]*48 for _ in range(16)]
    for i,ch in enumerate(HEADING):
        glyph=glyph_8x16(base,ch)
        for y in range(16):
            for x in range(8):pixels[y][4+i*8+x]=palette[glyph[y][x]]
    for row,start in enumerate(ROWS):
        for tile in range(6):
            block=[line[tile*8:(tile+1)*8] for line in pixels[row*8:(row+1)*8]]
            out[start+tile*16:start+(tile+1)*16]=encode_tile(block)
    out[-2:]=ws_checksum(out).to_bytes(2,'little')
    return bytes(out),old,{'screen':'Arthur book index','heading':HEADING,
                           'graphic_rows':[f'0x{a:X}' for a in ROWS],
                           'changed_bytes_from_hf19':sum(a!=b for a,b in zip(old,out)),
                           'checksum':f'0x{ws_checksum(out):04X}'}

def main():
    if len(sys.argv)<2:raise SystemExit('usage: build_phase4w_hf20.py CLEAN_JP.ws [HF20.ws] [JP_TO_HF20.bps]')
    base=Path(sys.argv[1]).read_bytes()
    out,old,detail=build(base)
    patch=bps_create(base,out)
    if bps_apply(base,patch)!=out:raise SystemExit('BPS replay mismatch')
    if len(sys.argv)>2:Path(sys.argv[2]).write_bytes(out)
    if len(sys.argv)>3:Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base),'hf19_sha256':sha(old),
        'hf20_sha256':sha(out),'bps_sha256':sha(patch),**detail},indent=2))

if __name__=='__main__':main()

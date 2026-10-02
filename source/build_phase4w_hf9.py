#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
from build_phase4w_hf8 import build as build_hf8, remap_header, native_glyph
from build_phase4w_hf7 import ARTHUR_HEADER_OFF
from build_phase4w_hf2 import ws_checksum, decode_tile, encode_tile, SEGD, SIZE, EXPECTED_JP

EXPECTED_HF8='3c76dc4f8d59c179be4398a0bfae4bd0ac59aef77628717ea32856bb8a8051bf'
ARTHUR_MAP_OFF=SEGD+0xF8C5
OLD_MAP=list(range(16))+[16,17,2,18,2,19,20,21]
NEW_MAP=list(range(16))+[16,17,20,18,22,19,20,21]

def sha(b): return hashlib.sha256(b).hexdigest()

def patch_arthur_vertical_alignment(base,b):
    # Decode the original clean-JP header using its real 8x3 tile map.
    src_tiles=[decode_tile(base[ARTHUR_HEADER_OFF+i*16:ARTHUR_HEADER_OFF+(i+1)*16]) for i in range(23)]
    pix=[[3]*64 for _ in range(24)]
    for v,ri in enumerate(OLD_MAP):
        tx=v%8; ty=v//8; tile=src_tiles[ri]
        for y in range(8):
            for x in range(8): pix[ty*8+y][tx*8+x]=tile[y][x]

    # Remove the JP title only.  The original title begins at asset y=7.
    for y in range(7,24):
        for x in range(3,61): pix[y][x]=3

    # Exact native 8x16 Latin glyphs, lowered 5 px vs HF8.
    # Native ink is rows 2..12, so y0=5 yields asset ink y=7..17,
    # matching the original title's vertical band/optical center.
    word='ARTHUR'; x0=8; y0=5
    provenance=[]
    for i,ch in enumerate(word):
        g,w,src=native_glyph(base,ch); q=remap_header(g)
        for gy in range(16):
            yy=y0+gy
            if 0<=yy<24:
                for gx in range(8):
                    xx=x0+i*8+gx
                    if 0<=xx<64: pix[yy][xx]=q[gy][gx]
        provenance.append({'char':ch,'fontword':f'0x{w:04X}','source_top':f'0x{src:X}','source_bottom':f'0x{src+0x100:X}'})

    # The native resource map aliases row3 col2 and col4 to tile #2.
    # For ARTHUR, col2 and col6 are both R, so col2 safely reuses tile #20 (R lower).
    # Col4 (H lower) gets the previously unused resource tile #22.
    # Patch the descriptor map words (index byte + 0x0C attribute byte).
    cur=[]
    for i in range(24):
        w=int.from_bytes(b[ARTHUR_MAP_OFF+i*2:ARTHUR_MAP_OFF+i*2+2],'little')
        cur.append(w & 0xFF)
        if (w>>8)!=0x0C: raise SystemExit(f'Arthur map attribute mismatch at {i}: 0x{w:04X}')
    if cur!=OLD_MAP: raise SystemExit('Arthur map signature mismatch: '+repr(cur))
    for i,ri in enumerate(NEW_MAP):
        b[ARTHUR_MAP_OFF+i*2:ARTHUR_MAP_OFF+i*2+2]=bytes((ri,0x0C))

    # Encode the 24 visual cells back into 23 resources under NEW_MAP.
    # Shared resource #20 must be identical at row3 col2 and col6 (both R lower).
    assigned={}
    for v,ri in enumerate(NEW_MAP):
        tx=v%8; ty=v//8
        tile=[[pix[ty*8+y][tx*8+x] for x in range(8)] for y in range(8)]
        enc=encode_tile(tile)
        if ri in assigned and assigned[ri]!=enc:
            raise SystemExit(f'new Arthur map aliases non-identical visual tiles at resource {ri}')
        assigned[ri]=enc
    for ri,enc in assigned.items():
        b[ARTHUR_HEADER_OFF+ri*16:ARTHUR_HEADER_OFF+(ri+1)*16]=enc

    return {
      'text':word,'x0':x0,'y0':y0,'native_ink_asset_y':'7..17','expected_screen_ink_y':'15..25',
      'font_source':'clean JP ROM exact 8x16 Latin UI glyphs','old_map':OLD_MAP,'new_map':NEW_MAP,
      'map_patch':{'row3_col2':'resource 2 -> 20 (reuse identical R lower)','row3_col4':'resource 2 -> 22 (private H lower)'},
      'provenance':provenance
    }

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP: raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf8,_,d8=build_hf8(base)
    if sha(hf8)!=EXPECTED_HF8: raise SystemExit('HF8 reconstruction mismatch: '+sha(hf8))
    b=bytearray(hf8)
    arthur=patch_arthur_vertical_alignment(base,b)
    b[-2:]=ws_checksum(b).to_bytes(2,'little')
    return bytes(b),hf8,{'hf8':d8,'arthur_hf9':arthur}

def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf9.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes(); outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF9_PRIVATE.ws')
    out,hf8,details=build(base); outp.write_bytes(out)
    print(json.dumps({'phase':'Phase4W-HF9','base_sha256':sha(base),'hf8_sha256':sha(hf8),'target_sha256':sha(out),'size':len(out),'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}','checksum_recalc':f'0x{ws_checksum(out):04X}','details':details},indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
from build_phase4w_hf9 import build as build_hf9
from build_phase4w_hf2 import ws_checksum, SIZE, EXPECTED_JP, decode_tile, encode_tile

EXPECTED_HF9='984905e5c70c340e51ad489469fd4459f67d440ac9a52aa989590c9b27ae8048'
# 12 runtime header tiles (1C..27) are sourced here, one horizontal 96x8 strip.
INDEX_STRIP_OFF=0x1FBBC9
INDEX_STRIP_TILES=12
NATIVE_SMALL_FONT_A=0x1800A0
WORD='INDEX'
TITLE_ORIGINAL_X0=32
TITLE_ORIGINAL_W=32
TITLE_NEW_W=40
TITLE_CENTER=TITLE_ORIGINAL_X0 + TITLE_ORIGINAL_W//2
TITLE_NEW_X0=TITLE_CENTER - TITLE_NEW_W//2  # 28; 4 px expansion on each side
HEADER_BG=3


def sha(b): return hashlib.sha256(b).hexdigest()


def native_small_tile(base,ch):
    if not ('A' <= ch <= 'Z'):
        raise ValueError(ch)
    off=NATIVE_SMALL_FONT_A+(ord(ch)-ord('A'))*0x10
    raw=bytes(base[off:off+0x10])
    # Preserve exact native glyph geometry. The INDEX header uses a different
    # palette-index ordering than the main-menu bank, so adapt indices only:
    # 0<->1, with 2/3 unchanged. No pixel geometry is redrawn or approximated.
    pix=decode_tile(raw)
    q=[[1 if v==0 else 0 if v==1 else v for v in row] for row in pix]
    return q, off, raw


def decode_strip(rom):
    pix=[[HEADER_BG]*96 for _ in range(8)]
    for t in range(INDEX_STRIP_TILES):
        tile=decode_tile(rom[INDEX_STRIP_OFF+t*16:INDEX_STRIP_OFF+(t+1)*16])
        for y in range(8):
            for x in range(8):
                pix[y][t*8+x]=tile[y][x]
    return pix


def encode_strip(b,pix):
    for t in range(INDEX_STRIP_TILES):
        tile=[[pix[y][t*8+x] for x in range(8)] for y in range(8)]
        b[INDEX_STRIP_OFF+t*16:INDEX_STRIP_OFF+(t+1)*16]=encode_tile(tile)


def patch_demons_index(base,b):
    # Start from the clean-JP header strip so the ornaments are not inherited
    # from any earlier English redraw. The Japanese title occupied x=32..63.
    # INDEX is 40 px at native 8x8 cell size, so expand symmetrically 4 px into
    # each side while preserving the original title center and the surrounding ornament.
    pix=decode_strip(base)
    x0=TITLE_NEW_X0
    for y in range(8):
        for x in range(x0,x0+TITLE_NEW_W):
            pix[y][x]=HEADER_BG

    provenance=[]
    for i,ch in enumerate(WORD):
        glyph,src,raw=native_small_tile(base,ch)
        gx=x0+i*8
        for y in range(8):
            for x in range(8):
                pix[y][gx+x]=glyph[y][x]
        provenance.append({
            'char':ch,
            'source':f'0x{src:X}',
            'screen_x':gx,
            'source_bytes':raw.hex(),
            'palette_index_remap':'0<->1; 2,3 unchanged',
        })

    encode_strip(b,pix)
    return {
        'text':WORD,
        'strip_range':f'0x{INDEX_STRIP_OFF:X}-0x{INDEX_STRIP_OFF+INDEX_STRIP_TILES*16-1:X}',
        'font_source':'clean JP ROM native 8x8 Latin main-menu font; exact geometry with destination palette-index adaptation',
        'font_bank_A':f'0x{NATIVE_SMALL_FONT_A:X}',
        'original_title_region':{'x0':TITLE_ORIGINAL_X0,'width':TITLE_ORIGINAL_W,'center':TITLE_CENTER},
        'new_title_region':{'x0':x0,'width':TITLE_NEW_W,'center':TITLE_CENTER},
        'layout':'40 px INDEX centered on the exact original Japanese title center; expansion is symmetric 4 px left/right',
        'glyph_count':len(WORD),
        'provenance':provenance,
    }


def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf9,_,d9=build_hf9(base)
    if sha(hf9)!=EXPECTED_HF9:
        raise SystemExit('HF9 reconstruction mismatch: '+sha(hf9))
    b=bytearray(hf9)
    idx=patch_demons_index(base,b)
    b[-2:]=ws_checksum(b).to_bytes(2,'little')
    return bytes(b),hf9,{'hf9':d9,'demons_index_hf10':idx}


def main():
    if len(sys.argv)<2:
        raise SystemExit('usage: build_phase4w_hf10.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes()
    outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF10_PRIVATE.ws')
    out,hf9,details=build(base)
    outp.write_bytes(out)
    print(json.dumps({
        'phase':'Phase4W-HF10',
        'base_sha256':sha(base),
        'hf9_sha256':sha(hf9),
        'target_sha256':sha(out),
        'size':len(out),
        'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}',
        'checksum_recalc':f'0x{ws_checksum(out):04X}',
        'details':details,
    },indent=2))
if __name__=='__main__': main()

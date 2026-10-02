#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
from build_phase4w_hf6 import build as build_hf6
from build_phase4w_hf2 import ws_checksum, decode_tile, encode_tile, SEGD, SEGF, SIZE, EXPECTED_JP, fontword

EXPECTED_HF6='6b98073fd2483525e269f29c4bddc34fed87bbcfe6ae671f24b9f7340c3da05d'
ARTHUR_HEADER_OFF=SEGD+0xF8F7
ARTHUR_TILES=23
PROMPT_TOP_OFF=0x1FB1D2
PROMPT_BOTTOM_OFF=0x1FB2A2
BAD_PASSWORD_OFF=0x1FF45D

# The small header font is based directly on the game's native 8x8
# "BAD PASSWORD" graphic family. A/R are copied byte-for-byte from ROM;
# T/H/U follow the same 1-pixel, 5x7 metrics and palette indices.
NATIVE_SMALL_PATTERNS={
 'T':['.#####..','...#....','...#....','...#....','...#....','...#....','...#....','........'],
 'H':['.#...#..','.#...#..','.#...#..','.#####..','.#...#..','.#...#..','.#...#..','........'],
 'U':['.#...#..','.#...#..','.#...#..','.#...#..','.#...#..','.#...#..','..###...','........'],
}

def sha(b): return hashlib.sha256(b).hexdigest()

def make_small_native_tile(pattern):
    pix=[[3]*8 for _ in range(8)]
    for y,row in enumerate(pattern):
        for x,c in enumerate(row):
            if c=='#': pix[y][x]=0
    return encode_tile(pix)

def native_small_glyphs(b):
    # BAD PASSWORD = B A D [space] P A S S W O R D
    src='BAD PASSWORD'
    exact={}
    for i,ch in enumerate(src):
        if ch!=' ' and ch not in exact:
            src_tile=decode_tile(b[BAD_PASSWORD_OFF+i*16:BAD_PASSWORD_OFF+(i+1)*16])
            # Preserve exact native glyph geometry, but use the header palette's
            # darkest index (0) for the stroke; index 1 is too light on this header.
            src_tile=[[0 if v==1 else v for v in row] for row in src_tile]
            exact[ch]=encode_tile(src_tile)
    exact['T']=make_small_native_tile(NATIVE_SMALL_PATTERNS['T'])
    exact['H']=make_small_native_tile(NATIVE_SMALL_PATTERNS['H'])
    exact['U']=make_small_native_tile(NATIVE_SMALL_PATTERNS['U'])
    return exact

def patch_arthur_native_typography(b):
    base=ARTHUR_HEADER_OFF
    # Preserve HF6's cleaned asset and actual runtime mapping. Only replace the
    # middle-row title cells with the game's native small UI-font family.
    glyphs=native_small_glyphs(b)
    # Clear middle row resource tiles 8..15 to native background index 3.
    blank=encode_tile([[3]*8 for _ in range(8)])
    for ri in range(8,16):
        b[base+ri*16:base+(ri+1)*16]=blank
    # Center six 8px cells in the 8-cell middle row: columns 1..6.
    word='ARTHUR'
    for col,ch in enumerate(word, start=1):
        ri=8+col
        b[base+ri*16:base+(ri+1)*16]=glyphs[ch]
    # Keep lower row clean exactly as HF6 established it; do not draw text there.
    return {
      'offset':f'0x{base:X}','text':word,
      'font':'native in-ROM 8x8 small UI geometry (BAD PASSWORD family), remapped to header dark stroke',
      'middle_row_columns':'1..6','cell_height':8,
      'scope':'Arthur header title cells only; ornament and lower-row alias handling preserved'
    }

def decode_native_font_glyph(b,ch):
    w=fontword(ch)
    off=SEGF+(w<<4)
    return decode_tile(b[off:off+16])+decode_tile(b[off+0x100:off+0x110])

def remap_native_font_to_popup(g):
    # Preserve the exact normal UI glyph geometry. The popup uses index 3 as
    # its grey background, while the standard font's background is index 0.
    # Both native stroke/antialias indices (1/2) are mapped to the darkest
    # popup stroke (0) so letters remain crisp at WonderSwan scale.
    mp={0:3,1:0,2:0,3:2}
    return [[mp[v] for v in row] for row in g]

def patch_password_native_typography(b):
    text='USE PASSWORD'
    for i,ch in enumerate(text):
        if ch==' ':
            g=[[3]*8 for _ in range(16)]
        else:
            g=remap_native_font_to_popup(decode_native_font_glyph(b,ch))
        b[PROMPT_TOP_OFF+i*16:PROMPT_TOP_OFF+(i+1)*16]=encode_tile(g[:8])
        b[PROMPT_BOTTOM_OFF+i*16:PROMPT_BOTTOM_OFF+(i+1)*16]=encode_tile(g[8:])
    return {
      'top_offset':f'0x{PROMPT_TOP_OFF:X}','bottom_offset':f'0x{PROMPT_BOTTOM_OFF:X}',
      'text':text+'?','cells':12,
      'font':'exact game-native 8x16 Latin UI glyph geometry; high-contrast popup remap',
      'palette_map':'native bg 0 -> popup bg 3; native stroke/AA 1/2 -> popup dark 0',
      'scope':'12 prompt glyph cells only; native question mark, YES/NO, tilemap and control flow unchanged'
    }

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf6,_,d6=build_hf6(base)
    if sha(hf6)!=EXPECTED_HF6:
        raise SystemExit('HF6 reconstruction mismatch: '+sha(hf6))
    b=bytearray(hf6)
    a=patch_arthur_native_typography(b)
    p=patch_password_native_typography(b)
    b[-2:]=(ws_checksum(b)).to_bytes(2,'little')
    return bytes(b),hf6,{'hf6':d6,'arthur_header_hf7':a,'password_prompt_hf7':p}

def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf7.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes()
    outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF7_PRIVATE.ws')
    out,hf6,details=build(base); outp.write_bytes(out)
    print(json.dumps({
      'phase':'Phase4W-HF7','base_sha256':sha(base),'hf6_sha256':sha(hf6),
      'target_sha256':sha(out),'size':len(out),
      'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}',
      'checksum_recalc':f'0x{ws_checksum(out):04X}','details':details
    },indent=2))
if __name__=='__main__': main()

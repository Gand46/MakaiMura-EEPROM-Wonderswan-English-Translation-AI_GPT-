#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
from build_phase4w_hf7 import build as build_hf7, ARTHUR_HEADER_OFF, PROMPT_TOP_OFF, PROMPT_BOTTOM_OFF
from build_phase4w_hf2 import ws_checksum, decode_tile, encode_tile, SEGF, SIZE, EXPECTED_JP, fontword

EXPECTED_HF7='7bf84d4c24b3c7ea37023e327f4caa92e1ae439afba61bf8eaf65f390ea0cf96'

def sha(b): return hashlib.sha256(b).hexdigest()

def native_glyph(base,ch):
    """Return the exact 8x16 glyph from the clean JP ROM Latin UI bank."""
    w=fontword(ch)
    off=SEGF+(w<<4)
    return decode_tile(base[off:off+16])+decode_tile(base[off+0x100:off+0x110]), w, off

def remap_header(g):
    # Same geometry; only adapt source palette indices to the Arthur header palette.
    # Source font: 0=background, 1=stroke, 2=AA. Header: 3=background, 0=stroke, 1=AA.
    mp={0:3,1:0,2:1,3:2}
    return [[mp[v] for v in row] for row in g]

def remap_popup(g):
    # Preserve the native 3-level edge geometry. Popup: 3=grey background, 0=dark stroke,
    # 2=light AA. Crucially, unlike HF7, do NOT collapse native AA into the main stroke.
    mp={0:3,1:0,2:2,3:1}
    return [[mp[v] for v in row] for row in g]

def patch_arthur_native(base,b):
    """Render ARTHUR with exact clean-ROM 8x16 native Latin glyphs.

    Root cause in HF6/HF7: the title used a fabricated/reconstructed 5x7/8x8 family.
    The Arthur 8x3 runtime tilemap aliases resource tile #2 in visual row 3, so a normal
    8x16 title placed in rows 2+3 cannot be correct. Rows 1+2 are unique, so HF8 places
    the exact native 8x16 glyph cells there and preserves the edge ornament cells.
    """
    baseoff=ARTHUR_HEADER_OFF
    word='ARTHUR'
    provenance=[]
    # Visual row0->resource 0..7 and row1->resource 8..15 are both unique.
    # Center six 8px glyph cells: columns 1..6, leaving columns 0 and 7 intact.
    for col,ch in enumerate(word,start=1):
        g,w,src=native_glyph(base,ch)
        q=remap_header(g)
        top_ri=col
        bot_ri=8+col
        b[baseoff+top_ri*16:baseoff+(top_ri+1)*16]=encode_tile(q[:8])
        b[baseoff+bot_ri*16:baseoff+(bot_ri+1)*16]=encode_tile(q[8:])
        provenance.append({'char':ch,'fontword':f'0x{w:04X}','source_top':f'0x{src:X}','source_bottom':f'0x{src+0x100:X}','dest_top_resource_tile':top_ri,'dest_bottom_resource_tile':bot_ri})
    return {
      'text':word,
      'font_source':'clean JP ROM native SEGF 8x16 Latin UI bank',
      'placement':'Arthur header visual rows 0+1, columns 1..6; unique tilemap rows',
      'palette_map':'native 0/1/2 -> header 3/0/1; glyph geometry unchanged',
      'provenance':provenance,
      'root_cause_fixed':'remove non-native HF6/HF7 small-font reconstruction and avoid aliased third row'
    }

def patch_password_native(base,b):
    """Render USE PASSWORD with exact clean-ROM native glyphs and correct runtime bank order.

    Root cause in HF7: the top row has an external spacer before the private top glyph bank,
    while the bottom row does not. Writing the same 12-cell order to both banks shifted every
    top half from P onward by one cell. HF8 compensates with separate top/bottom orders.
    """
    top_order='USEPASSWORD '     # external runtime spacer provides the visible word space
    bottom_order='USE PASSWORD'  # bottom row needs an internal spacer
    provenance=[]
    blank16=[[3]*8 for _ in range(16)]
    for bank_name,order,off,half in (
        ('top',top_order,PROMPT_TOP_OFF,'top'),
        ('bottom',bottom_order,PROMPT_BOTTOM_OFF,'bottom'),
    ):
        for i,ch in enumerate(order):
            if ch==' ':
                q=blank16
                srcinfo=None
            else:
                g,w,src=native_glyph(base,ch)
                q=remap_popup(g)
                srcinfo={'fontword':f'0x{w:04X}','source_top':f'0x{src:X}','source_bottom':f'0x{src+0x100:X}'}
            tile=q[:8] if half=='top' else q[8:]
            b[off+i*16:off+(i+1)*16]=encode_tile(tile)
            provenance.append({'bank':bank_name,'cell':i,'char':ch,'dest':f'0x{off+i*16:X}',**(srcinfo or {})})
    return {
      'text':'USE PASSWORD',
      'font_source':'clean JP ROM native SEGF 8x16 Latin UI bank',
      'top_order':top_order,
      'bottom_order':bottom_order,
      'palette_map':'native 0/1/2 -> popup 3/0/2; glyph geometry/AA preserved',
      'provenance':provenance,
      'root_cause_fixed':'top and bottom private tile banks have asymmetric spacer semantics; HF7 used identical orders and misaligned P/A/S/S/W/O/R/D halves'
    }

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf7,_,d7=build_hf7(base)
    if sha(hf7)!=EXPECTED_HF7:
        raise SystemExit('HF7 reconstruction mismatch: '+sha(hf7))
    b=bytearray(hf7)
    arthur=patch_arthur_native(base,b)
    password=patch_password_native(base,b)
    b[-2:]=ws_checksum(b).to_bytes(2,'little')
    return bytes(b),hf7,{'hf7':d7,'arthur_hf8':arthur,'password_hf8':password}

def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf8.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes()
    outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF8_PRIVATE.ws')
    out,hf7,details=build(base); outp.write_bytes(out)
    print(json.dumps({
      'phase':'Phase4W-HF8','base_sha256':sha(base),'hf7_sha256':sha(hf7),
      'target_sha256':sha(out),'size':len(out),
      'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}',
      'checksum_recalc':f'0x{ws_checksum(out):04X}','details':details
    },indent=2))
if __name__=='__main__': main()

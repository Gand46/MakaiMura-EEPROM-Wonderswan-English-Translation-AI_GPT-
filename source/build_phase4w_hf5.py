#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
from build_phase4w_hf4 import build as build_hf4
from build_phase4w_hf2 import ws_checksum, SIZE, EXPECTED_JP

EXPECTED_HF4='526d60b33167cb34bed90f80a07037f4771bc6d298d802d6a33f31589c7889d5'
PROMPT_TOP_OFF=0x1FB1D2
PROMPT_BOTTOM_OFF=0x1FB2A2
PROMPT_HALF_SIZE=12*16
EXPECTED_TOP_SHA='a06b740e27f436a22bb8b51d2528652e8d08aefc6f2d7d8f4de38f93ff6dca94'
EXPECTED_BOTTOM_SHA='81b8c3f6c9a217f30f5a4e6b54b268ae15213d9a3649d651a2f31877adcbdb1a'

def sha(b): return hashlib.sha256(b).hexdigest()

def decode_tile(d):
    out=[[0]*8 for _ in range(8)]
    for y in range(8):
        p0,p1=d[2*y],d[2*y+1]
        for x in range(8):
            bit=7-x
            out[y][x]=((p0>>bit)&1)|(((p1>>bit)&1)<<1)
    return out

def encode_tile(a):
    out=bytearray()
    for y in range(8):
        p0=p1=0
        for x in range(8):
            v=a[y][x]; bit=7-x
            p0|=(v&1)<<bit
            p1|=((v>>1)&1)<<bit
        out += bytes((p0,p1))
    return bytes(out)

def transform_half(src):
    before={0:0,1:0,2:0,3:0}
    after={0:0,1:0,2:0,3:0}
    out=bytearray()
    for t in range(12):
        pix=decode_tile(src[t*16:(t+1)*16])
        for y in range(8):
            for x in range(8):
                v=pix[y][x]; before[v]+=1
                # Index 3 is the popup's grey field background. The original
                # localized lettering uses indices 1/2 and becomes too close in
                # luminance to that background. Index 0 is otherwise unused or
                # already used as the high-contrast stroke in this asset family.
                if v in (1,2): v=0
                pix[y][x]=v; after[v]+=1
        out += encode_tile(pix)
    return bytes(out),before,after

def patch_password_prompt_contrast(b):
    top=bytes(b[PROMPT_TOP_OFF:PROMPT_TOP_OFF+PROMPT_HALF_SIZE])
    bottom=bytes(b[PROMPT_BOTTOM_OFF:PROMPT_BOTTOM_OFF+PROMPT_HALF_SIZE])
    if sha(top)!=EXPECTED_TOP_SHA:
        raise SystemExit('password prompt TOP signature mismatch: '+sha(top))
    if sha(bottom)!=EXPECTED_BOTTOM_SHA:
        raise SystemExit('password prompt BOTTOM signature mismatch: '+sha(bottom))
    new_top,top_before,top_after=transform_half(top)
    new_bottom,bottom_before,bottom_after=transform_half(bottom)
    b[PROMPT_TOP_OFF:PROMPT_TOP_OFF+PROMPT_HALF_SIZE]=new_top
    b[PROMPT_BOTTOM_OFF:PROMPT_BOTTOM_OFF+PROMPT_HALF_SIZE]=new_bottom
    return {
        'text':'USE PASSWORD?',
        'top':{
            'offset':f'0x{PROMPT_TOP_OFF:X}','size':PROMPT_HALF_SIZE,
            'source_sha256':sha(top),'patched_sha256':sha(new_top),
            'before_palette_index_counts':top_before,'after_palette_index_counts':top_after,
        },
        'bottom':{
            'offset':f'0x{PROMPT_BOTTOM_OFF:X}','size':PROMPT_HALF_SIZE,
            'source_sha256':sha(bottom),'patched_sha256':sha(new_bottom),
            'before_palette_index_counts':bottom_before,'after_palette_index_counts':bottom_after,
        },
        'operation':'both 8x8 halves of each 8x16 prompt glyph: indices 1/2 -> 0; background index 3 preserved',
        'scope':'password confirmation prompt only; no tilemap, code, YES/NO, list data, or shared tables changed'
    }

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf4,_,d4=build_hf4(base)
    if sha(hf4)!=EXPECTED_HF4:
        raise SystemExit('HF4 reconstruction mismatch: '+sha(hf4))
    b=bytearray(hf4)
    prompt=patch_password_prompt_contrast(b)
    b[-2:]=(ws_checksum(b)).to_bytes(2,'little')
    return bytes(b),hf4,{'hf4':d4,'password_prompt_hf5':prompt}

def main():
    if len(sys.argv)<2:
        raise SystemExit('usage: build_phase4w_hf5.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes()
    outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF5_PRIVATE.ws')
    out,hf4,details=build(base)
    outp.write_bytes(out)
    print(json.dumps({
        'phase':'Phase4W-HF5',
        'base_sha256':sha(base),
        'hf4_sha256':sha(hf4),
        'target_sha256':sha(out),
        'size':len(out),
        'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}',
        'checksum_recalc':f'0x{ws_checksum(out):04X}',
        'details':details
    },indent=2))

if __name__=='__main__': main()

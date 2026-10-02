#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
from build_phase4w_hf3 import build as build_hf3
from build_phase4w_hf2 import ws_checksum, decode_tile, encode_tile, glyph_8x16, SEGD, SIZE, EXPECTED_JP

EXPECTED_HF3='1c72bc6e168dc3cda021b7f4fec54be026dc07a18cc4146857091d19e6c33bc6'

def sha(b): return hashlib.sha256(b).hexdigest()

def patch_arthur_header_optical(b):
    # Rebuild Arthur header with optical centering. Same resource as HF2,
    # but shift the title left to recover breathing room from the right ornament.
    base=SEGD+0xF8F7
    pix=[[3]*64 for _ in range(24)]
    for t in range(23):
        tile=decode_tile(b[base+t*16:base+(t+1)*16])
        tx=t%8; ty=t//8
        for y in range(8):
            for x in range(8):
                pix[ty*8+y][tx*8+x]=tile[y][x]
    for y in range(8,24):
        for x in range(3,61):
            pix[y][x]=3
    palmap={0:3,1:0,2:1,3:2}
    x0=4
    for i,ch in enumerate('ARTHUR'):
        g=glyph_8x16(b,ch)
        for y in range(16):
            for x in range(8):
                pix[8+y][x0+i*8+x]=palmap[g[y][x]]
    for t in range(23):
        tx=t%8;ty=t//8
        tile=[[pix[ty*8+y][tx*8+x] for x in range(8)] for y in range(8)]
        b[base+t*16:base+(t+1)*16]=encode_tile(tile)
    return {'offset':f'0x{base:X}','size':23*16,'localized':'ARTHUR','x0':x0,'note':'optical centering hotfix'}


def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf3,_,d3=build_hf3(base)
    if sha(hf3)!=EXPECTED_HF3:
        raise SystemExit('HF3 reconstruction mismatch: '+sha(hf3))
    b=bytearray(hf3)
    arthur=patch_arthur_header_optical(b)
    b[-2:]=(ws_checksum(b)).to_bytes(2,'little')
    return bytes(b),hf3,{'hf3':d3,'arthur_header_hf4':arthur}


def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf4.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes(); outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF4_PRIVATE.ws')
    out,hf3,details=build(base); outp.write_bytes(out)
    print(json.dumps({'phase':'Phase4W-HF4','base_sha256':sha(base),'hf3_sha256':sha(hf3),'target_sha256':sha(out),'size':len(out),'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}','checksum_recalc':f'0x{ws_checksum(out):04X}','details':details},indent=2))

if __name__=='__main__':
    main()

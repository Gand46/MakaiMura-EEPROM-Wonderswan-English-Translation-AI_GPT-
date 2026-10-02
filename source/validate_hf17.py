#!/usr/bin/env python3
"""Structural regression for the bounded HF17 graphics and cumulative BPS."""
from pathlib import Path
import json,sys
from build_phase4w_hf17 import build,sha,MAPS,GFX_BASE,PRIVATE
from build_phase4w_hf16 import build as build_hf16
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply

EXPECTED_HF17='90cc07da4db2909d47f131134564d3b1b796823f16f1d30200b17d9059f10715'
EXPECTED_BPS='9191d203b97a078af7a7f23476d3094013090e118828b38a1dd475dcf2e89011'

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: python3 source/validate_hf17.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes()
    current,info=build(base)
    prior,_,_=build_hf16(base)
    assert len(base)==len(current)==0x200000
    assert sha(current)==EXPECTED_HF17
    assert current[-2:]==ws_checksum(current).to_bytes(2,'little')
    patch=bps_create(base,current)
    assert sha(patch)==EXPECTED_BPS
    assert apply(base,patch)==current
    map_offsets=set()
    for mb in MAPS:
        for r in range(4,13):
            for c in range(15,23):
                p=mb+2*(r*28+c)
                map_offsets.update((p,p+1))
    for r,c,_ in info['label_tiles']:
        p=MAPS[0]+2*(r*28+c)
        map_offsets.update((p,p+1))
    graphics_offsets=set(range(GFX_BASE+PRIVATE*16,
                               GFX_BASE+info['next_free_tile']*16))
    allowed=map_offsets|graphics_offsets|{len(current)-2,len(current)-1}
    changed={i for i,(a,b) in enumerate(zip(prior,current)) if a!=b}
    unexpected=changed-allowed
    assert not unexpected, f'unexpected changes: {sorted(unexpected)[:12]}'
    assert len(changed)==1518
    assert info['next_free_tile']==0x1ff
    assert current[0x30000:0x307e0]==prior[0x30000:0x307e0]
    assert current[0x327b0:-2]==prior[0x327b0:-2]
    print(json.dumps({'passed':True,'base_sha256':sha(base),'hf16_sha256':sha(prior),
        'hf17_sha256':sha(current),'bps_sha256':sha(patch),
        'checksum':f'0x{ws_checksum(current):04X}','changed_bytes_from_hf16':len(changed),
        'unexpected_changed_offsets':len(unexpected),
        'private_tile_ids':'0x1AE..0x1FE','other_banks_unchanged':True},indent=2))

if __name__=='__main__':main()

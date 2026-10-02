#!/usr/bin/env python3
"""Rebuild HF19 and enforce resource confinement and patch replay."""
from pathlib import Path
import json,sys

from build_phase4w_hf19 import build,RESOURCE,LAYOUT,sha
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply

EXPECTED_HF19='a924932e2aac1f3350badb3f82fe946d716a6abd1474e4cbd3bc86214227e22b'
EXPECTED_BPS='b7cc60569242f95881439ab3fa541a350ecd203c122dc98b9c49161ea7194059'

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: python3 source/validate_hf19.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes();current,prior,detail=build(base)
    assert len(base)==len(current)==0x200000
    assert sha(current)==EXPECTED_HF19
    assert current[-2:]==ws_checksum(current).to_bytes(2,'little')
    patch=bps_create(base,current)
    assert sha(patch)==EXPECTED_BPS and apply(base,patch)==current
    allowed={len(current)-2,len(current)-1}
    for _,top,bottom,cells,_ in LAYOUT:
        for index in (top,bottom):
            allowed.update(range(RESOURCE+index*16,RESOURCE+(index+cells)*16))
    changed={i for i,(a,b) in enumerate(zip(prior,current)) if a!=b}
    unexpected=changed-allowed
    assert len(changed)==595 and not unexpected
    assert prior[0x1C0000:RESOURCE+94*16]==current[0x1C0000:RESOURCE+94*16]
    assert prior[RESOURCE+(162+13)*16:0x1D0000]==current[RESOURCE+(162+13)*16:0x1D0000]
    print(json.dumps({'passed':True,'base_sha256':sha(base),'hf18_sha256':sha(prior),
        'hf19_sha256':sha(current),'bps_sha256':sha(patch),
        'checksum':f'0x{ws_checksum(current):04X}',
        'changed_bytes_from_hf18':len(changed),'unexpected_changed_offsets':len(unexpected),
        'resource':'C000:0405','screen_text':detail['prompt']},indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Independent structural checks of the cumulative HF14 ROM and patch."""
from pathlib import Path
import hashlib
import json
import sys

from build_phase4w_hf14 import build, SEG_E, TABLE, COUNT, FIRST_NAMES, sha
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: python3 source/validate_hf14.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes()
    rom,prior,detail=build(base)
    assert len(rom)==len(base)==0x200000
    assert bps_apply(base,bps_create(base,rom))==rom
    assert rom[-2:]==ws_checksum(rom).to_bytes(2,'little')
    allowed=lambda x: (SEG_E+0x0594<=x<=SEG_E+0x06F4) or x>=len(base)-2
    diff=[i for i,(a,b) in enumerate(zip(prior,rom)) if a!=b]
    assert all(allowed(i) for i in diff),[hex(i) for i in diff if not allowed(i)]
    assert rom[SEG_E:SEG_E+0x0594]==prior[SEG_E:SEG_E+0x0594]
    assert rom[SEG_E+0x06F5:-2]==prior[SEG_E+0x06F5:-2]
    assert rom[0x1460A8:0x1460AB]==b'\xBE\x79\x05'
    rows=[]
    for i in range(COUNT):
        p=int.from_bytes(rom[SEG_E+TABLE+1+2*i:SEG_E+TABLE+3+2*i],'little')
        oldp=int.from_bytes(prior[SEG_E+TABLE+1+2*i:SEG_E+TABLE+3+2*i],'little')
        assert p==oldp
        end=rom.index(0xFF,SEG_E+p)
        row=rom[SEG_E+p:end]
        original=prior[SEG_E+p:prior.index(0xFF,SEG_E+p)]
        parts=original.split(b'\xFE')
        assert row==(parts[0]+(b'\xFE'+parts[2] if i==11 else b''))
        assert all(x in (0,1,2,3,4,5,6,12,13,14,15,20,21,22,23,24,31,42,46,47,55) for x in parts[0])
        assert len(row)<=33 and (row.count(0xFE)==(1 if i==11 else 0))
        nextp=(int.from_bytes(rom[SEG_E+TABLE+3+2*i:SEG_E+TABLE+5+2*i],'little') if i<COUNT-1 else 0x06F5)
        assert all(x==0xFF for x in rom[end+1+SEG_E:nextp+SEG_E])
        rows.append({'index':i,'pointer':hex(p),'original_bytes':len(original)+1,
                     'active_bytes':len(row)+1,'english_name':FIRST_NAMES[i]})
    report={'base_sha256':sha(base),'hf13_sha256':sha(prior),'hf14_sha256':sha(rom),
            'bps_sha256':sha(bps_create(base,rom)),
            'checksum':hex(ws_checksum(rom)),'changed_bytes_from_hf13':len(diff),
            'changed_bytes_outside_cast_and_checksum':0,
            'cast_consumer_and_atlas_unchanged':True,
            'active_japanese_readings':0,'preserved_measurements':'B88 W58 H90',
            'rows':rows,'passed':True}
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

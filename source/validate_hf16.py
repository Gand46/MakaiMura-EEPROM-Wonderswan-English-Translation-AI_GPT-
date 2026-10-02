#!/usr/bin/env python3
"""Structural and BPS regression gate for HF16's bounded ending rewrite."""
from pathlib import Path
import json
import sys

from build_phase4w_hf16 import build, LINES_16, TABLE, SEG_E, encode, sha
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: python3 source/validate_hf16.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes()
    current, prior, detail=build(base)
    patch=bps_create(base,current)
    assert len(base)==len(current)==0x200000
    assert bps_apply(bytes(base),patch)==current
    assert current[-2:]==ws_checksum(current).to_bytes(2,'little')
    encoded,end=encode(LINES_16)
    old_end=int(detail['old_end'].split(':')[1],16)
    assert current[SEG_E+TABLE:SEG_E+end]==encoded
    assert current[SEG_E+end:SEG_E+max(end,old_end)]==b'\xFF'*max(0,old_end-end)
    assert current[0x145C80:0x145C85]==b'\xC7\x47\x11\x19\x00'
    assert current[0x145F28:0x145F2B]==b'\xB9\x19\x00'
    assert current[0x145F30:0x145F33]==b'\xBE\x80\xD1'
    pointers=[int.from_bytes(current[SEG_E+TABLE+1+i*2:SEG_E+TABLE+3+i*2],'little') for i in range(25)]
    assert pointers==sorted(pointers) and all(TABLE+51<=p<end for p in pointers)
    for i,p in enumerate(pointers):
        raw=current[SEG_E+p:current.index(0xFF,SEG_E+p)]
        expected=bytes('ABCDEFGHIJKLMNOPQRSTUVWXYZ .?'.index(c) for c in LINES_16[i])
        assert raw==expected,(i,raw,expected)
    assert [i for i,x in enumerate(LINES_16) if not x]==[4,9,14,20,24]
    changed=[i for i,(a,b) in enumerate(zip(prior,current)) if a!=b]
    assert all(SEG_E+TABLE<=i<SEG_E+max(end,old_end) or i>=len(base)-2 for i in changed)
    assert current[:SEG_E+TABLE]==prior[:SEG_E+TABLE]
    assert current[SEG_E+max(end,old_end):-2]==prior[SEG_E+max(end,old_end):-2]
    print(json.dumps({'passed':True,'base_sha256':sha(base),'hf15_sha256':sha(prior),
       'hf16_sha256':sha(current),'bps_sha256':sha(patch),'checksum':f'0x{ws_checksum(current):04X}',
       'line_count':25,'blank_rows':[4,9,14,20,24],'max_cells':max(map(len,LINES_16)),
       'end':f'E000:{end:04X}','changed_bytes_from_hf15':len(changed),
       'unexpected_changed_offsets':0,'other_story_cast_and_gameplay_bytes_unchanged':True},indent=2))

if __name__=='__main__':main()

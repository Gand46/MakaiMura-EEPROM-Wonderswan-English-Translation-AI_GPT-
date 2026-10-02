#!/usr/bin/env python3
"""Validate HF15 against the 25-step ending consumer and the clean ROM."""
from pathlib import Path
import json
import sys

from build_phase4w_hf15 import build, encode, LINES_25, TABLE, ATLAS, SEG_E, sha
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: python3 source/validate_hf15.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes()
    rom,prior,detail=build(base)
    assert len(rom)==len(base)==0x200000
    patch=bps_create(base,rom)
    assert bps_apply(base,patch)==rom
    assert rom[-2:]==ws_checksum(rom).to_bytes(2,'little')
    assert rom[0x145C80:0x145C85]==b'\xC7\x47\x11\x19\x00'
    assert rom[0x145F28:0x145F2B]==b'\xB9\x19\x00'
    assert rom[0x145F30:0x145F33]==b'\xBE\x80\xD1'
    encoded,end=encode(LINES_25)
    assert rom[SEG_E+TABLE:SEG_E+end]==encoded
    assert rom[SEG_E+4:SEG_E+6]==ATLAS.to_bytes(2,'little')
    pointers=[int.from_bytes(rom[SEG_E+TABLE+1+i*2:SEG_E+TABLE+3+i*2],'little') for i in range(25)]
    assert pointers==sorted(pointers) and all(TABLE+51<=p<end for p in pointers)
    assert [rom[SEG_E+p:rom.index(0xFF,SEG_E+p)].decode('latin1') for p in pointers]
    assert [i for i,line in enumerate(LINES_25) if not line]==[4,9,14,20,24]
    assert max(map(len,LINES_25))<=13
    changed=[i for i,(a,b) in enumerate(zip(prior,rom)) if a!=b]
    assert all(SEG_E+TABLE<=i<SEG_E+end or i>=len(rom)-2 for i in changed)
    assert rom[:SEG_E+TABLE]==prior[:SEG_E+TABLE]
    assert rom[SEG_E+end:-2]==prior[SEG_E+end:-2]
    report={'passed':True,'base_sha256':sha(base),'hf14_sha256':sha(prior),
      'hf15_sha256':sha(rom),'bps_sha256':sha(patch),'checksum':hex(ws_checksum(rom)),
      'engine_declared_lines':25,'resource_lines':len(LINES_25),'pointers':len(pointers),
      'blank_rows':[4,9,14,20,24],'max_cells':max(map(len,LINES_25)),
      'resource_end':f'E000:{end:04X}','changed_bytes_from_hf14':len(changed),
      'changed_bytes_outside_ending_and_checksum':0,
      'cast_bank_and_other_story_banks_unchanged':True}
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()

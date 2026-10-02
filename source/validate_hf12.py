#!/usr/bin/env python3
"""Verify the cumulative HF12 patch, isolation and native glyph sources."""
from pathlib import Path
import hashlib
import json
import sys

from build_phase4w_hf12 import build, LINES, SEG_E, ATLAS, TABLE, STRINGS, CONSUMER
from build_phase4w_hf2 import ws_checksum, fontword
from verify_bps import apply

ROOT = Path(__file__).resolve().parent.parent


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    if len(sys.argv)!=2:
        raise SystemExit('usage: python3 source/validate_hf12.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes()
    new,old,detail=build(base)
    patch=(ROOT/'patches/Makaimura_EN_US_Phase4W_HF12_CUMULATIVE_FROM_JP.bps').read_bytes()
    allowed=[(SEG_E,SEG_E+2),(CONSUMER+1,CONSUMER+3),
             (SEG_E+ATLAS,SEG_E+int(detail['new_end'].split(':')[1],16)),
             (len(new)-2,len(new))]
    unexpected=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b and not any(lo<=i<hi for lo,hi in allowed)]
    native_bank=all(
        base[0x1F0000+(fontword(ch)<<4):0x1F0000+(fontword(ch)<<4)+16] ==
        new[0x1F0000+(fontword(ch)<<4):0x1F0000+(fontword(ch)<<4)+16]
        and base[0x1F0100+(fontword(ch)<<4):0x1F0100+(fontword(ch)<<4)+16] ==
        new[0x1F0100+(fontword(ch)<<4):0x1F0100+(fontword(ch)<<4)+16]
        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    pointers=[int.from_bytes(new[SEG_E+TABLE+1+2*i:SEG_E+TABLE+3+2*i],'little') for i in range(23)]
    terminators=all(new[SEG_E+p+len(line)]==0xFF for p,line in zip(pointers,LINES))
    checks={
        'base_sha256':sha(base),'hf11_sha256':sha(old),'hf12_sha256':sha(new),
        'bps_sha256':sha(patch),'bps_round_trip':apply(base,patch)==new,
        'checksum_valid':int.from_bytes(new[-2:],'little')==ws_checksum(new),
        'unexpected_changed_offsets':unexpected,'native_A_to_Z_unchanged':native_bank,
        'private_atlas_selector':int.from_bytes(new[SEG_E:SEG_E+2],'little')==ATLAS,
        'private_table_consumer':int.from_bytes(new[CONSUMER+1:CONSUMER+3],'little')==TABLE,
        'other_four_atlas_selectors_unchanged':old[SEG_E+2:SEG_E+10]==new[SEG_E+2:SEG_E+10],
        'other_text_bytes_unchanged':old[SEG_E+0x028C:SEG_E+0x1000]==new[SEG_E+0x028C:SEG_E+0x1000],
        'all_23_strings_terminated':terminators,
        'max_13_cells':max(map(len,LINES))<=13,
    }
    print(json.dumps(checks,indent=2))
    if unexpected or any(v is False for v in checks.values()):raise SystemExit('FAIL')
    print('PASS static and BPS. Runtime and visual approval require in-game capture.',file=sys.stderr)


if __name__=='__main__':main()

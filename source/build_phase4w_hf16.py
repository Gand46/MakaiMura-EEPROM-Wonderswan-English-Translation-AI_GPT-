#!/usr/bin/env python3
"""HF16: revise the ending wording against the 25 original Japanese entries."""
from pathlib import Path
import json
import sys

from build_phase4w_hf15 import build as build_hf15, encode, LINES_25, TABLE, SEG_E, LIMIT, sha
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

EXPECTED_HF15 = '448113002b885d24d1b39d41bbfb35c77f9d961befb5c67777b9afa367d45456'
REVISIONS = {
    10: 'DEMON REALM',
    11: 'MAY REMAIN.',
    13: 'PEACE ENDURES',
    16: 'AND ITS SHADE',
    17: 'CRUMBLED AWAY',
    18: 'CLOUDS PARTED',
    19: 'THE SUN SHONE',
}
LINES_16 = LINES_25.copy()
for index, line in REVISIONS.items(): LINES_16[index] = line
assert len(LINES_16) == 25 and max(map(len, LINES_16)) <= 13
assert [i for i,x in enumerate(LINES_16) if not x] == [4,9,14,20,24]

def build(base):
    old, _, _ = build_hf15(base)
    if sha(old) != EXPECTED_HF15: raise SystemExit('HF15 signature mismatch')
    old_table, old_end = encode(LINES_25)
    if old[SEG_E+TABLE:SEG_E+old_end] != old_table:
        raise SystemExit('HF15 ending precondition mismatch')
    new_table, end = encode(LINES_16)
    if end > LIMIT: raise SystemExit('ending resource exceeds allocated cave')
    if any(v != 0xFF for v in old[SEG_E+old_end:SEG_E+end]):
        raise SystemExit('new ending resource overlaps another asset')
    result = bytearray(old)
    result[SEG_E+TABLE:SEG_E+max(old_end,end)] = new_table + b'\xFF'*max(0,old_end-end)
    result[-2:] = ws_checksum(result).to_bytes(2,'little')
    return bytes(result), old, {'resource_start':f'E000:{TABLE:04X}',
        'resource_end':f'E000:{end:04X}','old_end':f'E000:{old_end:04X}',
        'revised_rows':{str(i):{'before':LINES_25[i],'after':v} for i,v in REVISIONS.items()},
        'lines':LINES_16}

def main():
    if len(sys.argv)<2:
        raise SystemExit('usage: python3 source/build_phase4w_hf16.py CLEAN_JP.ws [OUT.ws] [OUT.bps]')
    base=Path(sys.argv[1]).read_bytes()
    result,old,detail=build(base)
    if len(sys.argv)>2:Path(sys.argv[2]).write_bytes(result)
    patch=bps_create(base,result)
    if bps_apply(base,patch)!=result:raise SystemExit('BPS round-trip mismatch')
    if len(sys.argv)>3:Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base),'hf15_sha256':sha(old),
        'hf16_sha256':sha(result),'bps_sha256':sha(patch),
        'checksum':f'0x{ws_checksum(result):04X}',
        'changed_bytes_from_hf15':sum(x!=y for x,y in zip(old,result)),
        'ending':detail},indent=2))

if __name__=='__main__':main()

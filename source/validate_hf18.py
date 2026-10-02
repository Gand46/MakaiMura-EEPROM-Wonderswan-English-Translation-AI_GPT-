#!/usr/bin/env python3
"""Validate HF18 binary isolation, narration geometry, and cumulative patch."""
from pathlib import Path
import json, sys

from build_phase4w_hf18 import build, LINES_18, sha
from build_phase4w_hf15 import encode, TABLE, SEG_E
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply

EXPECTED_HF18 = '0ee826c9d1c98b3b2e02a525dd9a089a961be48e0cea5c9a2d55b8421e807c25'
EXPECTED_BPS = 'a0528929f8d92c9832e134d8f364b535acbfa4568122024c3cf0b03796a6ffa6'

def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: python3 source/validate_hf18.py CLEAN_JP.ws')
    base = Path(sys.argv[1]).read_bytes()
    current, previous, detail = build(base)
    assert len(base) == len(current) == 0x200000
    assert sha(current) == EXPECTED_HF18
    assert current[-2:] == ws_checksum(current).to_bytes(2,'little')
    patch = bps_create(base,current)
    assert sha(patch) == EXPECTED_BPS and apply(base,patch) == current
    table,end = encode(LINES_18)
    assert current[SEG_E+TABLE:SEG_E+end] == table
    pointers = [int.from_bytes(table[1+i*2:3+i*2],'little') for i in range(25)]
    assert len(set(pointers)) == 25 and all(TABLE+51 <= p < end for p in pointers)
    assert [i for i,s in enumerate(LINES_18) if not s] == [4,9,14,20,24]
    changed = {i for i,(a,b) in enumerate(zip(previous,current)) if a != b}
    old_end = int(detail['old_end'].split(':')[1],16)
    allowed = set(range(SEG_E+TABLE,SEG_E+max(end,old_end))) | {len(current)-2,len(current)-1}
    unexpected = changed-allowed
    assert not unexpected and len(changed) == 106
    print(json.dumps({'passed':True,'base_sha256':sha(base),
        'hf17_sha256':sha(previous),'hf18_sha256':sha(current),
        'bps_sha256':sha(patch),'checksum':f'0x{ws_checksum(current):04X}',
        'changed_bytes':len(changed),'unexpected_changed_offsets':len(unexpected),
        'entry_count':25,'pause_indices':[4,9,14,20,24],
        'max_cells':max(map(len,LINES_18)),'resource_end':detail['new_end']},indent=2))

if __name__=='__main__': main()

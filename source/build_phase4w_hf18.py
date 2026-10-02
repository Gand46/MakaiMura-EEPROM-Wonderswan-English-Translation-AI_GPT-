#!/usr/bin/env python3
"""HF18: correct the ending's ambition and destination within 25 native lines."""
from pathlib import Path
import json
import sys

from build_phase4w_hf17 import build as build_hf17, sha
from build_phase4w_hf16 import LINES_16
from build_phase4w_hf15 import encode, TABLE, SEG_E, LIMIT
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

EXPECTED_HF17 = '90cc07da4db2909d47f131134564d3b1b796823f16f1d30200b17d9059f10715'
REVISIONS = {
    15: 'HIS KEEP FELL',
    16: 'HIS AMBITION',
    21: 'ARTHUR WENT',
    22: 'WITH HER TO',
    23: 'THE CAPITAL.',
}
LINES_18 = LINES_16.copy()
for index, line in REVISIONS.items():
    LINES_18[index] = line
assert len(LINES_18) == 25 and max(map(len, LINES_18)) <= 13
assert [i for i, line in enumerate(LINES_18) if not line] == [4, 9, 14, 20, 24]

def build(base):
    previous, _ = build_hf17(base)
    if sha(previous) != EXPECTED_HF17:
        raise SystemExit('HF17 signature mismatch')
    old_table, old_end = encode(LINES_16)
    new_table, new_end = encode(LINES_18)
    if previous[SEG_E+TABLE:SEG_E+old_end] != old_table:
        raise SystemExit('HF17 ending resource precondition mismatch')
    if new_end > LIMIT:
        raise SystemExit('new ending exceeds reserved cave')
    if any(b != 0xFF for b in previous[SEG_E+old_end:SEG_E+max(old_end,new_end)]):
        raise SystemExit('ending extension overlaps nonempty resource')
    result = bytearray(previous)
    result[SEG_E+TABLE:SEG_E+max(old_end,new_end)] = new_table + b'\xFF' * max(0,old_end-new_end)
    result[-2:] = ws_checksum(result).to_bytes(2, 'little')
    return bytes(result), previous, {'old_end': f'E000:{old_end:04X}',
        'new_end': f'E000:{new_end:04X}',
        'revisions': {str(i): {'before': LINES_16[i], 'after': v} for i,v in REVISIONS.items()}}

def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 source/build_phase4w_hf18.py CLEAN_JP.ws [HF18.ws] [JP_TO_HF18.bps]')
    base = Path(sys.argv[1]).read_bytes()
    result, old, details = build(base)
    patch = bps_create(base, result)
    if bps_apply(base, patch) != result:
        raise SystemExit('cumulative BPS replay mismatch')
    if len(sys.argv) > 2: Path(sys.argv[2]).write_bytes(result)
    if len(sys.argv) > 3: Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256': sha(base), 'hf17_sha256': sha(old),
        'hf18_sha256': sha(result), 'bps_sha256': sha(patch),
        'checksum': f'0x{ws_checksum(result):04X}',
        'changed_bytes_from_hf17': sum(x!=y for x,y in zip(old,result)),
        'ending': details}, indent=2))

if __name__ == '__main__': main()

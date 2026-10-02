#!/usr/bin/env python3
"""HF12: isolate and localize the first E000 story dialogue (23 lines)."""
from pathlib import Path
import hashlib
import json
import sys

from build_phase4w_hf11 import build as build_hf11
from build_phase4w_hf2 import ws_checksum, fontword
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

EXPECTED_JP = 'ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
EXPECTED_HF11 = 'b6379ffbdb8eb5caf8bb587cbc742149b63bfc8f4ac6af920affd29f32e45ff4'
SEG_E = 0x1E0000
ATLAS = 0xCD00
TABLE = 0xCD80
STRINGS = TABLE + 1 + 23 * 2
CONSUMER = 0x14594C

# One original story line per index; <=13 native 8x16 cells per line. Index 17
# preserves the original pause. English line 2 uses a source pause for reflow.
LINES = [
    'ARTHUR...',
    'YOU CAME TO',
    'SAVE ME.',
    'AS YOU ARE',
    'YOU CANNOT',
    'BEAT AZAGOL.',
    'HIS HEART IS',
    'FROZEN SOLID.',
    'TO DEFEAT HIM',
    'YOU NEED THE',
    'GODDESS',
    'BRACELET.',
    '',
    'I ALWAYS WORE',
    'THAT BRACELET',
    'DEMONS HUNTED',
    'ME FOR IT.',
    '',
    'I HID IT WHEN',
    'THEY TOOK ME.',
    'ARTHUR',
    'FIND IT.',
    'YOU CAN WIN.',
]
assert len(LINES) == 23 and max(map(len, LINES)) <= 13


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(base):
    if sha(base) != EXPECTED_JP:
        raise SystemExit('wrong original Japanese ROM')
    old, _, _ = build_hf11(base)
    if sha(old) != EXPECTED_HF11:
        raise SystemExit('HF11 reconstruction mismatch')
    b = bytearray(old)
    if b[SEG_E:SEG_E+2] != b'\x0A\x00':
        raise SystemExit('E000 dialogue atlas selector signature mismatch')
    if b[CONSUMER:CONSUMER+3] != b'\xBE\x8C\x02':
        raise SystemExit('E000 dialogue table consumer signature mismatch')

    glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ .'
    atlas = bytearray(len(glyphs).to_bytes(2, 'little'))
    for ch in glyphs:
        atlas += (0x0005 if ch == ' ' else 0x00E5 if ch == '.' else fontword(ch)).to_bytes(2, 'little')
    if len(atlas) > TABLE-ATLAS:
        raise SystemExit('atlas overlaps table')
    table = bytearray(b'\x00' + b'\x00' * (2 * len(LINES)))
    enc = {ch:idx for idx,ch in enumerate(glyphs)}
    pool = bytearray()
    for i,line in enumerate(LINES):
        ptr = STRINGS + len(pool)
        table[1+2*i:3+2*i] = ptr.to_bytes(2, 'little')
        pool += bytes(enc[ch] for ch in line) + b'\xFF'
    end = STRINGS + len(pool)
    if end > 0xD000:
        raise SystemExit('dialogue cave overflow')
    if any(v != 0xFF for v in b[SEG_E+ATLAS:SEG_E+end]):
        raise SystemExit('private cave is not pristine FF')
    b[SEG_E+ATLAS:SEG_E+ATLAS+len(atlas)] = atlas
    b[SEG_E+TABLE:SEG_E+TABLE+len(table)] = table
    b[SEG_E+STRINGS:SEG_E+end] = pool
    b[SEG_E:SEG_E+2] = ATLAS.to_bytes(2, 'little')
    b[CONSUMER+1:CONSUMER+3] = TABLE.to_bytes(2, 'little')
    b[-2:] = ws_checksum(b).to_bytes(2, 'little')
    return bytes(b), old, {'consumer':hex(CONSUMER), 'old_table':'E000:028C',
        'new_atlas':f'E000:{ATLAS:04X}', 'new_table':f'E000:{TABLE:04X}',
        'new_end':f'E000:{end:04X}', 'line_count':len(LINES),
        'max_cells':max(map(len,LINES)), 'english_lines':LINES}


def main():
    if len(sys.argv) < 2:
        raise SystemExit('usage: python3 source/build_phase4w_hf12.py CLEAN_JP.ws [OUT.ws] [OUT.bps]')
    base = Path(sys.argv[1]).read_bytes()
    result, old, detail = build(base)
    if len(sys.argv) >= 3: Path(sys.argv[2]).write_bytes(result)
    if len(sys.argv) >= 4:
        patch = bps_create(base, result)
        if bps_apply(base,patch) != result:
            raise SystemExit('cumulative BPS round-trip mismatch')
        Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base), 'hf11_sha256':sha(old),
        'hf12_sha256':sha(result), 'checksum':hex(ws_checksum(result)),
        'changed_bytes_from_hf11':sum(x!=y for x,y in zip(old,result)),
        'details':detail},indent=2))


if __name__ == '__main__':main()

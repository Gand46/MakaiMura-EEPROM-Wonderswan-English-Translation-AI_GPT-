#!/usr/bin/env python3
"""Independent HF13 binary isolation and cumulative BPS gate."""
from pathlib import Path
import hashlib
import json
import sys

from build_phase4w_hf13 import build, CONFIG, SEG_E
from build_phase4w_hf2 import ws_checksum, fontword
from verify_bps import apply

ROOT=Path(__file__).resolve().parent.parent
def sha(x):return hashlib.sha256(x).hexdigest()

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: python3 source/validate_hf13.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes()
    rom,old,detail=build(base)
    patch=(ROOT/'patches/Makaimura_EN_US_Phase4W_HF13_CUMULATIVE_FROM_JP.bps').read_bytes()
    allowed=[(len(rom)-2,len(rom))]
    for bank,_,consumer,atlas,_,_ in CONFIG:
        end=int(detail['new_story_banks'][bank-1]['end'].split(':')[1],16)
        allowed += [(SEG_E+bank*2,SEG_E+bank*2+2),(consumer+1,consumer+3),(SEG_E+atlas,SEG_E+end)]
    bad=[hex(i) for i,(a,b) in enumerate(zip(old,rom)) if a!=b and not any(lo<=i<hi for lo,hi in allowed)]
    glyphs='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    font_ok=all(all(base[0x1F0000+(fontword(ch)<<4)+d:0x1F0000+(fontword(ch)<<4)+d+16] ==
                       rom[0x1F0000+(fontword(ch)<<4)+d:0x1F0000+(fontword(ch)<<4)+d+16]
                       for d in (0,0x100)) for ch in glyphs)
    tables=[]
    for bank,_,consumer,atlas,table,lines in CONFIG:
        ptrs=[int.from_bytes(rom[SEG_E+table+1+2*i:SEG_E+table+3+2*i],'little') for i in range(len(lines))]
        tables.append({'bank':bank,'line_count':len(lines),
                       'max_cells':max(map(len,lines)),
                       'all_terminators':all(rom[SEG_E+p+len(line)]==0xFF for p,line in zip(ptrs,lines)),
                       'atlas_selector_correct':int.from_bytes(rom[SEG_E+2*bank:SEG_E+2*bank+2],'little')==atlas,
                       'consumer_table_correct':int.from_bytes(rom[consumer+1:consumer+3],'little')==table})
    report={'base_sha256':sha(base),'hf12_sha256':sha(old),'hf13_sha256':sha(rom),
            'cumulative_bps_sha256':sha(patch),'cumulative_roundtrip':apply(base,patch)==rom,
            'rom_size':len(rom),'checksum_stored':hex(int.from_bytes(rom[-2:],'little')),
            'checksum_recalculated':hex(ws_checksum(rom)),
            'native_AZ_glyphs_byte_identical':font_ok,
            'other_banks_3_and_4_unchanged':old[SEG_E+6:SEG_E+10]==rom[SEG_E+6:SEG_E+10],
            'first_story_resource_and_consumer_unchanged':old[SEG_E+0xCD00:SEG_E+0xCEB0]==rom[SEG_E+0xCD00:SEG_E+0xCEB0] and old[0x14594C:0x14594F]==rom[0x14594C:0x14594F],
            'unexpected_changed_offsets':bad,'tables':tables}
    print(json.dumps(report,indent=2))
    if bad or not (report['cumulative_roundtrip'] and font_ok and report['other_banks_3_and_4_unchanged'] and report['first_story_resource_and_consumer_unchanged'] and report['checksum_stored']==report['checksum_recalculated'] and all(t['all_terminators'] and t['atlas_selector_correct'] and t['consumer_table_correct'] and t['max_cells']<=13 for t in tables)):
        raise SystemExit('FAIL')
    print('PASS static and cumulative BPS; runtime and visual approval still open',file=sys.stderr)

if __name__=='__main__':main()

#!/usr/bin/env python3
"""HF15: repair the ending narration to match its 25-entry runtime consumer."""
from pathlib import Path
import json
import sys

from build_phase4w_hf14 import build as build_hf14, EXPECTED_JP, sha
from build_phase4w_hf2 import ws_checksum
from build_phase4w_hf13 import SEG_E, CONFIG as STORY_CONFIG, LINES_2 as OLD_LINES
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

TABLE=0xD180
ATLAS=0xD100
LIMIT=0xD300
EXPECTED_PRIOR='d4f891ce248bbb49107c1c4825e245c132c00b97a5b61a5b256723db716181c0'
LINES_25=[
    'ARTHUR WORE',
    'THE GODDESS',
    'BRACELET AND',
    'BEAT AZAGOL.',
    '',
    'AZAGOL FELL.',
    'DEMON REALM',
    'VANISHED TOO.',
    'PEACE CAME.',
    '',
    'EVIL MAY YET',
    'STILL REMAIN.',
    'I PRAY THIS',
    'PEACE LASTS.',
    '',
    'THE DARK KEEP',
    'AND THE VEIL',
    'OF NIGHT FELL',
    'AS THE FIRST',
    'SUNLIGHT CAME',
    '',
    'ARTHUR AND',
    'THE PRINCESS',
    'HEADED HOME.',
    '',
]
assert len(LINES_25)==25 and max(map(len,LINES_25))<=13
assert [i for i,x in enumerate(LINES_25) if not x]==[4,9,14,20,24]

def encode(lines):
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ .?'
    enc={ch:i for i,ch in enumerate(alphabet)}
    pos=TABLE+1+2*len(lines)
    table=bytearray(b'\x00'+bytes(2*len(lines)))
    pool=bytearray()
    for i,line in enumerate(lines):
        table[1+i*2:3+i*2]=(pos+len(pool)).to_bytes(2,'little')
        pool+=bytes(enc[ch] for ch in line)+b'\xFF'
    return table+pool,pos+len(pool)

def build(base):
    if sha(base)!=EXPECTED_JP:raise SystemExit('wrong original Japanese ROM')
    prior,_,detail14=build_hf14(base)
    if sha(prior)!=EXPECTED_PRIOR:raise SystemExit('prior HF14 signature mismatch')
    old,old_end=encode(OLD_LINES)
    if prior[SEG_E+TABLE:SEG_E+old_end]!=old:
        raise SystemExit('HF14 ending table signature mismatch')
    if prior[0x145F30:0x145F33]!=b'\xBE\x80\xD1':
        raise SystemExit('ending consumer signature mismatch')
    if prior[SEG_E+4:SEG_E+6]!=ATLAS.to_bytes(2,'little'):
        raise SystemExit('ending atlas selector signature mismatch')
    new,end=encode(LINES_25)
    if end>LIMIT:raise SystemExit('ending narration exceeds reserved cave')
    if any(v!=0xFF for v in prior[SEG_E+old_end:SEG_E+end]):
        raise SystemExit('new ending data overlaps other assets')
    result=bytearray(prior)
    result[SEG_E+TABLE:SEG_E+end]=new
    result[-2:]=ws_checksum(result).to_bytes(2,'little')
    return bytes(result),prior,{'prior':detail14,'old_lines':len(OLD_LINES),
        'new_lines':len(LINES_25),'table':f'E000:{TABLE:04X}',
        'end':f'E000:{end:04X}','lines':LINES_25}

def main():
    if len(sys.argv)<2:
        raise SystemExit('usage: python3 source/build_phase4w_hf15.py CLEAN_JP.ws [OUT.ws] [OUT.bps]')
    base=Path(sys.argv[1]).read_bytes()
    result,prior,detail=build(base)
    if len(sys.argv)>2:Path(sys.argv[2]).write_bytes(result)
    if len(sys.argv)>3:
        patch=bps_create(base,result)
        if bps_apply(base,patch)!=result:raise SystemExit('cumulative BPS round-trip mismatch')
        Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base),'hf14_sha256':sha(prior),
        'hf15_sha256':sha(result),'checksum':hex(ws_checksum(result)),
        'changed_bytes_from_hf14':sum(a!=b for a,b in zip(prior,result)),
        'ending':{k:v for k,v in detail.items() if k!='prior'}},indent=2))

if __name__=='__main__':main()

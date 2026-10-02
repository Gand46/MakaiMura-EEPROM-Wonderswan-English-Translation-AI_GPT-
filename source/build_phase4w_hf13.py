#!/usr/bin/env python3
"""HF13: localize the alternate dialogue and ending narration after HF12."""
from pathlib import Path
import hashlib
import json
import sys

from build_phase4w_hf12 import build as build_hf12, SEG_E
from build_phase4w_hf2 import ws_checksum, fontword
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

EXPECTED_JP='ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
LINES_1=[
    'ARTHUR WHY','DID YOU NOT','FIND THE','BRACELET?',
    'YOU CANNOT','BEAT AZAGOL','WITHOUT IT.',
    'RETURN TO THE','CASTLE GATE.','FIND IT.','',
    'I BELIEVE YOU','CAN BEAT HIM.','I PRAY FOR','YOUR SAFETY.',
]
LINES_2=[
    'ARTHUR WORE','THE GODDESS','BRACELET OF','HIDDEN POWER.',
    'AZAGOL FELL.','DEMON REALM','VANISHED TOO.','PEACE CAME TO',
    'THE WORLD.','','EVIL MAY YET','STILL REMAIN.','I PRAY THIS','PEACE LASTS.',
]
assert len(LINES_1)==15 and len(LINES_2)==14
assert max(map(len,LINES_1+LINES_2))<=13

CONFIG=(
    (1,0x039F,0x145B4B,0xCF00,0xCF80,LINES_1),
    (2,0x0458,0x145F30,0xD100,0xD180,LINES_2),
)

def sha(data):return hashlib.sha256(data).hexdigest()

def integrate(b,bank,old_table,consumer,atlas_addr,table_addr,lines):
    selector=SEG_E+2*bank
    if int.from_bytes(b[selector:selector+2],'little') not in (0x00A0,0x0118):
        raise SystemExit('E000 atlas selector signature mismatch')
    if b[consumer:consumer+3]!=b'\xBE'+old_table.to_bytes(2,'little'):
        raise SystemExit('dialogue consumer signature mismatch')
    glyphs='ABCDEFGHIJKLMNOPQRSTUVWXYZ .?'
    glyph_words=[fontword(ch) if ch.isalpha() else 0x0005 if ch==' ' else 0x00E5 if ch=='.' else 0x00E0 for ch in glyphs]
    atlas=len(glyphs).to_bytes(2,'little')+b''.join(w.to_bytes(2,'little') for w in glyph_words)
    if atlas_addr+len(atlas)>table_addr:raise SystemExit('atlas overlaps table')
    pos=table_addr+1+2*len(lines)
    table=bytearray(b'\x00'+bytes(2*len(lines)))
    pool=bytearray()
    enc={ch:i for i,ch in enumerate(glyphs)}
    for i,line in enumerate(lines):
        table[1+i*2:3+i*2]=(pos+len(pool)).to_bytes(2,'little')
        pool+=bytes(enc[ch] for ch in line)+b'\xFF'
    end=pos+len(pool)
    if end>0xD300 or any(x!=0xFF for x in b[SEG_E+atlas_addr:SEG_E+end]):
        raise SystemExit('dialogue cave overlaps existing data')
    b[SEG_E+atlas_addr:SEG_E+atlas_addr+len(atlas)]=atlas
    b[SEG_E+table_addr:SEG_E+table_addr+len(table)]=table
    b[SEG_E+pos:SEG_E+end]=pool
    b[selector:selector+2]=atlas_addr.to_bytes(2,'little')
    b[consumer+1:consumer+3]=table_addr.to_bytes(2,'little')
    return {'bank':bank,'atlas':f'E000:{atlas_addr:04X}',
        'table':f'E000:{table_addr:04X}','end':f'E000:{end:04X}',
        'consumer':hex(consumer),'lines':lines}

def build(base):
    if sha(base)!=EXPECTED_JP:raise SystemExit('wrong original Japanese ROM')
    previous,_,d12=build_hf12(base)
    b=bytearray(previous)
    details=[]
    for args in CONFIG:details.append(integrate(b,*args))
    b[-2:]=ws_checksum(b).to_bytes(2,'little')
    return bytes(b),previous,{'hf12':d12,'new_story_banks':details}

def main():
    if len(sys.argv)<2:
        raise SystemExit('usage: python3 source/build_phase4w_hf13.py CLEAN_JP.ws [OUT.ws] [OUT.bps]')
    base=Path(sys.argv[1]).read_bytes();result,old,detail=build(base)
    if len(sys.argv)>2:Path(sys.argv[2]).write_bytes(result)
    if len(sys.argv)>3:
        patch=bps_create(base,result)
        if bps_apply(base,patch)!=result:raise SystemExit('cumulative BPS round-trip mismatch')
        Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base),'hf12_sha256':sha(old),
        'hf13_sha256':sha(result),'checksum':hex(ws_checksum(result)),
        'changed_bytes_from_hf12':sum(a!=b for a,b in zip(old,result)),
        'details':detail},indent=2))

if __name__=='__main__':main()

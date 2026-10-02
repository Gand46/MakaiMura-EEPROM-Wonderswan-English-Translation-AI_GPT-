#!/usr/bin/env python3
"""HF14: remove active Japanese phonetic readings from the ending cast cards."""
from pathlib import Path
import hashlib
import json
import sys

from build_phase4w_hf13 import build as build_hf13, SEG_E, EXPECTED_JP
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply as bps_apply

TABLE=0x0579
COUNT=13
# Index 11 contains a third, Latin-only line of character measurements.
KEEP_THIRD=11
FIRST_NAMES=(
    'ZOMBIE','GHOST','FRANKEN ZOMBIE','GHOST FORTRESS','DAGON',
    'EFREETI','NIGHTMARE','RANGDA','TIAMAT','AZAZEL',
    'RED ARREMER','PRINCESS PRIN PRIN','KNIGHT ARTHUR',
)
FIRST_GLYPHS={0: ' ',1:'Z',2:'O',3:'M',4:'B',5:'I',6:'E',
              12:'G',13:'H',14:'S',15:'T',20:'F',21:'R',22:'A',
              23:'N',24:'K',31:'D',42:'L',46:'P',47:'C',55:'U'}
MEASURE_GLYPHS={0:' ',4:'B',13:'H',0x32:'8',0x33:'W',0x34:'5',0x35:'9',0x36:'0'}

def sha(data):return hashlib.sha256(data).hexdigest()

def patch_cast(b):
    if b[SEG_E+TABLE]!=0:
        raise SystemExit('cast table header mismatch')
    pointers=[int.from_bytes(b[SEG_E+TABLE+1+i*2:SEG_E+TABLE+3+i*2],'little') for i in range(COUNT)]
    if pointers != [0x0594,0x05AB,0x05C1,0x05DF,0x05FC,0x0612,0x062A,
                    0x0645,0x065C,0x0677,0x068F,0x06AB,0x06DA]:
        raise SystemExit('cast pointer signature mismatch')
    if int.from_bytes(b[SEG_E+6:SEG_E+8],'little')!=0x01DE:
        raise SystemExit('cast atlas selector mismatch')
    if b[0x1460A8:0x1460AB]!=b'\xBE\x79\x05':
        raise SystemExit('ending cast consumer mismatch')
    details=[]
    for i,p in enumerate(pointers):
        end=b.index(0xFF,SEG_E+p)
        row=bytes(b[SEG_E+p:end])
        parts=row.split(b'\xFE')
        if len(parts)!=(3 if i==KEEP_THIRD else 2):
            raise SystemExit(f'cast row {i} structure changed')
        name=''.join(FIRST_GLYPHS.get(c,'?') for c in parts[0]).strip()
        if name!=FIRST_NAMES[i]:
            raise SystemExit(f'cast row {i} name mismatch: {name!r}')
        if not parts[1] or not any(c>=7 for c in parts[1]):
            raise SystemExit(f'cast row {i} no Japanese reading')
        new=parts[0]
        if i==KEEP_THIRD:
            measure=''.join(MEASURE_GLYPHS.get(c,'?') for c in parts[2]).strip()
            if measure!='B88 W58 H90':
                raise SystemExit(f'cast measurements changed: {measure!r}')
            new+=b'\xFE'+parts[2]
        new+=b'\xFF'
        if len(new)>len(row)+1:
            raise SystemExit('unexpected cast row growth')
        b[SEG_E+p:end+1]=new+b'\xFF'*(len(row)+1-len(new))
        details.append({'row':i,'pointer':f'E000:{p:04X}',
                        'name':name,'measurements_preserved':i==KEEP_THIRD,
                        'bytes_before':len(row)+1,'bytes_after':len(new)})
    return details

def build(base):
    if sha(base)!=EXPECTED_JP:raise SystemExit('wrong original Japanese ROM')
    previous,_,detail13=build_hf13(base)
    result=bytearray(previous)
    cast=patch_cast(result)
    result[-2:]=ws_checksum(result).to_bytes(2,'little')
    return bytes(result),previous,{'hf13':detail13,'cast_cards':cast}

def main():
    if len(sys.argv)<2:
        raise SystemExit('usage: python3 source/build_phase4w_hf14.py CLEAN_JP.ws [OUT.ws] [OUT.bps]')
    base=Path(sys.argv[1]).read_bytes()
    result,previous,detail=build(base)
    if len(sys.argv)>2:Path(sys.argv[2]).write_bytes(result)
    if len(sys.argv)>3:
        patch=bps_create(base,result)
        if bps_apply(base,patch)!=result:raise SystemExit('cumulative BPS round-trip mismatch')
        Path(sys.argv[3]).write_bytes(patch)
    print(json.dumps({'base_sha256':sha(base),'hf13_sha256':sha(previous),
        'hf14_sha256':sha(result),'checksum':hex(ws_checksum(result)),
        'changed_bytes_from_hf13':sum(a!=b for a,b in zip(previous,result)),
        'cast_cards':detail['cast_cards']},indent=2))

if __name__=='__main__':main()

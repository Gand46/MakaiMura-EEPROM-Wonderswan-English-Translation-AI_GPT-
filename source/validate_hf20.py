#!/usr/bin/env python3
"""Verify HF20 resource boundaries, exact rebuild, checksum, and cumulative BPS."""
from pathlib import Path
import json,sys

from build_phase4w_hf20 import build,ROWS,sha
from build_phase4w_hf2 import ws_checksum
from phase2_builder import bps_create
from verify_bps import apply

EXPECTED_HF20='885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51'
EXPECTED_BPS='3fc350fd39cd1c15608c4e9e791487b9d2f8aa535a73482472e11d4c337a796a'

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: validate_hf20.py CLEAN_JP.ws')
    base=Path(sys.argv[1]).read_bytes();current,prior,detail=build(base)
    assert len(base)==len(prior)==len(current)==0x200000
    assert sha(current)==EXPECTED_HF20
    assert current[-2:]==ws_checksum(current).to_bytes(2,'little')
    patch=bps_create(base,current)
    assert sha(patch)==EXPECTED_BPS and apply(base,patch)==current
    allowed={len(current)-2,len(current)-1}
    for start in ROWS:allowed.update(range(start,start+96))
    changed={i for i,(a,b) in enumerate(zip(prior,current)) if a!=b}
    unexpected=changed-allowed
    assert len(changed)==157 and not unexpected
    # Both 8x16 native font tiles are untouched, along with every other resource.
    print(json.dumps({'passed':True,'base_sha256':sha(base),
        'hf19_sha256':sha(prior),'hf20_sha256':sha(current),
        'bps_sha256':sha(patch),'checksum':detail['checksum'],
        'changed_bytes_from_hf19':len(changed),
        'unexpected_changed_offsets':len(unexpected),'heading':detail['heading']},indent=2))

if __name__=='__main__':main()

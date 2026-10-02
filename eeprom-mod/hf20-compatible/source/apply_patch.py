#!/usr/bin/env python3
"""Apply BPS with CRCs and destination SHA-256 validation. Never overwrite inputs."""
from pathlib import Path
import argparse,hashlib
from ws_patch_tools import bps
TARGET='abd2440a261dfd8aa1a01f215c829ea08617536e48909c9be54dbe26e6c4b713'
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('patch',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists() or a.output.resolve() in (a.source.resolve(),a.patch.resolve()):p.error('Choose a new output')
    try:out=bps.apply(a.source.read_bytes(),a.patch.read_bytes())
    except (OSError,ValueError,IndexError) as e:p.error(str(e))
    if hashlib.sha256(out).hexdigest()!=TARGET:p.error('Unexpected destination hash')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(out);print('PASS:',a.output)
if __name__=='__main__':main()

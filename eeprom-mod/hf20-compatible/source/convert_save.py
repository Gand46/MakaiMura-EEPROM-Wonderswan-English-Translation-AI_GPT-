#!/usr/bin/env python3
"""Copy HF20 SRAM 32768 bytes -> cartridge EEPROM 2048 bytes. Never overwrite."""
from pathlib import Path
import argparse,hashlib,json
def convert(data):
    if len(data)!=32768:raise ValueError('Expected HF20 SRAM .sav of exactly 32768 bytes')
    return data[:2048]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    if a.output.exists() or a.source.resolve()==a.output.resolve():p.error('Choose a new output file')
    try:src=a.source.read_bytes();out=convert(src)
    except (OSError,ValueError) as e:p.error(str(e))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(out)
    print(json.dumps({'source_sha256':hashlib.sha256(src).hexdigest(),'output_sha256':hashlib.sha256(out).hexdigest(),'size':len(out),'native_record_preserved':True},indent=2))
if __name__=='__main__':main()

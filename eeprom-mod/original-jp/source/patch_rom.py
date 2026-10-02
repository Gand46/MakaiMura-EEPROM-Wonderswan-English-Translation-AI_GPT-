#!/usr/bin/env python3
"""Apply or create this release's BPS patches; standard Python only."""
from pathlib import Path
import argparse,hashlib
from ws_patch_tools import bps
TARGET='f5652123b1eee5541a4c761c4818e4872a1ca9f00ce7c106708ee7d5f7044217'
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['apply','create'])
    ap.add_argument('source',type=Path)
    ap.add_argument('patch_or_target',type=Path)
    ap.add_argument('output',type=Path)
    a=ap.parse_args()
    if a.output.resolve() in {a.source.resolve(),a.patch_or_target.resolve()}:
        ap.error('La salida no puede sobrescribir las entradas.')
    if a.output.exists():ap.error('La salida ya existe; utiliza otro nombre.')
    src=a.source.read_bytes();second=a.patch_or_target.read_bytes()
    result=bps.apply(src,second) if a.mode=='apply' else bps.create(src,second)
    rom=result if a.mode=='apply' else second
    if hashlib.sha256(rom).hexdigest()!=TARGET:ap.error('La ROM destino no coincide con la release 4.1E-r2.')
    if a.mode=='create' and bps.apply(src,result)!=rom:ap.error('Fallo de verificacion BPS.')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(result)
    print('OK:',a.output);print('SHA256:',hashlib.sha256(result).hexdigest())
if __name__=='__main__':
    try:main()
    except (OSError,ValueError) as e:raise SystemExit('ERROR: '+str(e))

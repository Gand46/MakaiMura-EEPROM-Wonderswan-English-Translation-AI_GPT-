#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, zlib, sys

def sha(b):return hashlib.sha256(b).hexdigest()
def readnum(p,buf):
    data=0;shift=1
    while True:
        x=buf[p];p+=1
        data+=(x&0x7f)*shift
        if x&0x80:return data,p
        shift<<=7;data+=shift

def apply(src,patch):
    if patch[:4]!=b'BPS1':raise ValueError('not BPS1')
    p=4;ss,p=readnum(p,patch);ts,p=readnum(p,patch);ms,p=readnum(p,patch)
    if ss!=len(src):raise ValueError('source size mismatch')
    p+=ms;out=bytearray()
    while len(out)<ts:
        act,p=readnum(p,patch);mode=act&3;ln=(act>>2)+1
        if mode==0:
            s=len(out);out+=src[s:s+ln]
        elif mode==1:
            out+=patch[p:p+ln];p+=ln
        else:raise ValueError(f'unsupported action mode {mode}; this project builder emits only SourceRead/TargetRead')
    if len(out)!=ts:raise ValueError('target size mismatch')
    source_crc=int.from_bytes(patch[p:p+4],'little');target_crc=int.from_bytes(patch[p+4:p+8],'little');patch_crc=int.from_bytes(patch[p+8:p+12],'little')
    if source_crc!=(zlib.crc32(src)&0xffffffff):raise ValueError('source CRC mismatch')
    if target_crc!=(zlib.crc32(out)&0xffffffff):raise ValueError('target CRC mismatch')
    if patch_crc!=(zlib.crc32(patch[:-4])&0xffffffff):raise ValueError('patch CRC mismatch')
    return bytes(out)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('patch');ap.add_argument('--expect-sha256',required=True);ap.add_argument('--output')
    a=ap.parse_args();src=Path(a.source).read_bytes();pat=Path(a.patch).read_bytes();out=apply(src,pat)
    got=sha(out)
    if got!=a.expect_sha256:raise SystemExit(f'FAIL target SHA-256 {got}')
    if a.output:Path(a.output).write_bytes(out)
    print('PASS');print('source_sha256='+sha(src));print('patch_sha256='+sha(pat));print('target_sha256='+got)
if __name__=='__main__':main()

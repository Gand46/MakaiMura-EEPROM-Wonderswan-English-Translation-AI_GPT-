#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
from build_phase4w_hf2 import build as build_hf2, ws_checksum, fontword, decode_tile, encode_tile, SEGD, SEGF, SIZE, EXPECTED_JP

EXPECTED_HF2='c64d4b4a9da93f56158f30f12615ef713aa3e2c50acbd51f9a54ac648cb5dc6e'

def sha(b): return hashlib.sha256(b).hexdigest()

def patch_system_records(b):
    # This screen is the second local-text bank selected by AX=1 through
    # F000:4C80 -> F000:4CDA. It has its own 45-glyph atlas and 14-string table.
    atlas=SEGF+0x4CDA
    count=int.from_bytes(b[atlas:atlas+2],'little')
    if count != 0x2D:
        raise SystemExit(f'System Records atlas count mismatch: {count}')

    # Existing local token map already contains digits, punctuation and most of
    # the Latin letters needed. Repurpose only Japanese-only tokens after all
    # static Japanese strings on this screen are replaced.
    # 24/25/26 originally ク/リ/ア -> P/L/Y
    for code,ch in ((0x24,'P'),(0x25,'L'),(0x26,'Y')):
        b[atlas+2+2*code:atlas+4+2*code]=fontword(ch).to_bytes(2,'little')

    blank_word=0x0005
    # Dynamic suffix tokens. Runtime uses these after numeric values:
    # 0A/0B=時間, 0C=分, 0D=秒, 20=回, 2C=点.
    # Convert to compact English units while retaining field widths.
    b[atlas+2+2*0x0A:atlas+4+2*0x0A]=fontword('H').to_bytes(2,'little')
    b[atlas+2+2*0x0B:atlas+4+2*0x0B]=blank_word.to_bytes(2,'little')
    b[atlas+2+2*0x0C:atlas+4+2*0x0C]=fontword('M').to_bytes(2,'little')
    b[atlas+2+2*0x0D:atlas+4+2*0x0D]=fontword('S').to_bytes(2,'little')
    b[atlas+2+2*0x20:atlas+4+2*0x20]=blank_word.to_bytes(2,'little')
    b[atlas+2+2*0x21:atlas+4+2*0x21]=blank_word.to_bytes(2,'little')
    b[atlas+2+2*0x2C:atlas+4+2*0x2C]=blank_word.to_bytes(2,'little')

    enc={
      '0':0x00,'1':0x01,'2':0x02,'3':0x03,'4':0x04,'5':0x05,'6':0x06,'7':0x07,'8':0x08,'9':0x09,
      ' ':0x11,':':0x12,'H':0x13,'I':0x14,'-':0x15,'S':0x16,'C':0x17,'O':0x18,'R':0x19,'E':0x1A,
      'N':0x1B,'W':0x1C,'G':0x1D,'A':0x1E,'M':0x1F,'T':0x22,'U':0x23,'P':0x24,'L':0x25,'Y':0x26,'B':0x2B,
    }
    labels=[
      'PLAY TIME:',
      'HI-SCORE:',
      'NEW GAMES:',
      'CONTINUES:',
      ' ',                  # native spacer entry
      'CLEAR TIME:',
      'STAGE1:',
      'STAGE2:',
      'STAGE3A:',
      'STAGE3B:',
      'STAGE4:',
      'STAGE5:',
      'STAGE6:',
      'STAGE7:',
    ]
    encoded=[]
    for s in labels:
        try: q=bytes(enc[ch] for ch in s)+b'\xFF'
        except KeyError as e: raise SystemExit(f'unencodable System Records char {e} in {s!r}')
        encoded.append(q)
    ptrbase=SEGF+0x4DB9
    pos=0x4DD6
    end_limit=0x4E59
    if sum(map(len,encoded)) > end_limit-pos:
        raise SystemExit('System Records label block overflow')
    entries=[]
    for i,s in enumerate(encoded):
        po=ptrbase+1+2*i
        b[po:po+2]=pos.to_bytes(2,'little')
        b[SEGF+pos:SEGF+pos+len(s)]=s
        entries.append({'index':i,'text':labels[i].strip(),'offset':f'0x{SEGF+pos:X}'})
        pos += len(s)
    b[SEGF+pos:SEGF+end_limit]=b'\xFF'*(end_limit-pos)
    return {'atlas_offset':f'0x{atlas:X}','atlas_count':count,'entries':entries,'strings_end':f'0x{pos:04X}'}

def patch_system_header(b):
    # Runtime trace: D000:0A34 copies 0x190 bytes from D000:FA9E into tiles
    # 0x1E7..0x1FF. BG0 uses the first 24 tiles as an 8x3 header region.
    base=SEGD+0xFA9E
    pix=[[3]*64 for _ in range(24)]
    for t in range(24):
        tile=decode_tile(b[base+t*16:base+(t+1)*16])
        tx=t%8;ty=t//8
        for y in range(8):
            for x in range(8): pix[ty*8+y][tx*8+x]=tile[y][x]
    # Preserve ornamental pixels at the outer edges and clear the Japanese text.
    for y in range(8,24):
        for x in range(3,61): pix[y][x]=3
    # Same palette conversion used by the native header/Latin font integration.
    palmap={0:3,1:0,2:1,3:2}
    word='RECORDS'
    x0=4
    for i,ch in enumerate(word):
        w=fontword(ch)
        top=decode_tile(b[SEGF+(w<<4):SEGF+(w<<4)+16])
        bot=decode_tile(b[SEGF+(w<<4)+0x100:SEGF+(w<<4)+0x110])
        g=top+bot
        for y in range(16):
            for x in range(8): pix[8+y][x0+i*8+x]=palmap[g[y][x]]
    for t in range(24):
        tx=t%8;ty=t//8
        tile=[[pix[ty*8+y][tx*8+x] for x in range(8)] for y in range(8)]
        b[base+t*16:base+(t+1)*16]=encode_tile(tile)
    return {'offset':f'0x{base:X}','size':24*16,'localized':'RECORDS','source_meaning':'System Records'}

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf2,_,d2=build_hf2(base)
    if sha(hf2)!=EXPECTED_HF2:
        raise SystemExit('HF2 reconstruction mismatch: '+sha(hf2))
    b=bytearray(hf2)
    sysinfo=patch_system_records(b)
    header=patch_system_header(b)
    b[-2:]=(ws_checksum(b)).to_bytes(2,'little')
    return bytes(b),hf2,{'hf2':d2,'system_records':sysinfo,'system_header':header}

def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf3.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes();outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF3_PRIVATE.ws')
    out,hf2,details=build(base);outp.write_bytes(out)
    print(json.dumps({'phase':'Phase4W-HF3','base_sha256':sha(base),'hf2_sha256':sha(hf2),'target_sha256':sha(out),'size':len(out),'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}','checksum_recalc':f'0x{ws_checksum(out):04X}','details':details},indent=2))
if __name__=='__main__':main()

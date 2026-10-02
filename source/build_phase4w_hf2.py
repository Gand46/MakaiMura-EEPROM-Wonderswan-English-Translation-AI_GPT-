#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
from verify_bps import apply as bps_apply

EXPECTED_JP='ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
EXPECTED_HF1='4cbf2ee616103c1b5fa170158a8d6de1053bf7258bc1ef74228949c11dc9fc87'
SIZE=0x200000
SEG4000=0x140000
SEGD=0x1D0000
SEGF=0x1F0000

def sha(b): return hashlib.sha256(b).hexdigest()
def ws_checksum(b): return sum(b[:-2]) & 0xffff

def fontword(ch):
    idx=0x150+(ord(ch)-65)
    row,col=divmod(idx,16)
    return row*0x20+col

def decode_tile(d):
    out=[[0]*8 for _ in range(8)]
    for y in range(8):
        a,c=d[2*y],d[2*y+1]
        for x in range(8):
            bit=7-x
            out[y][x]=((a>>bit)&1)|(((c>>bit)&1)<<1)
    return out

def encode_tile(a):
    out=bytearray()
    for y in range(8):
        p0=p1=0
        for x in range(8):
            v=a[y][x]; bit=7-x
            p0|=(v&1)<<bit
            p1|=((v>>1)&1)<<bit
        out += bytes((p0,p1))
    return bytes(out)

def glyph_8x16(rom,ch):
    w=fontword(ch)
    top=decode_tile(rom[SEGF+(w<<4):SEGF+(w<<4)+16])
    bot=decode_tile(rom[SEGF+(w<<4)+0x100:SEGF+(w<<4)+0x110])
    return top+bot

def patch_contents_numbering(b):
    # HF1 localized CONTENTS has N0001..N0017, but rows 18..22 still
    # dereference zero entries and render binary garbage.  Original runtime
    # proves N0022 is the terminal row. Add only the missing five strings.
    pt=SEG4000+0xFDC0
    expected={
        18: bytes([0x0F,0x10,0x1C,0x1D,0x24,0x26,0xFF]), # N0018:
        19: bytes([0x0F,0x10,0x1C,0x1D,0x25,0x26,0xFF]), # N0019:
        20: bytes([0x0F,0x10,0x1C,0x1E,0x1C,0x26,0xFF]), # N0020:
        21: bytes([0x0F,0x10,0x1C,0x1E,0x1D,0x26,0xFF]), # N0021:
        22: bytes([0x0F,0x10,0x1C,0x1E,0x1E,0x26,0xFF]), # N0022:
    }
    pos=0xFF30
    rows=[]
    for number,s in expected.items():
        idx=number+1 # N0001 uses pointer index 2
        po=pt+1+2*idx
        if b[po:po+2] != b'\x00\x00':
            raise SystemExit(f'CONTENTS pointer {number} is not pristine zero')
        dst=SEG4000+pos
        if any(x!=0xFF for x in b[dst:dst+len(s)]):
            raise SystemExit(f'CONTENTS destination 0x{dst:X} is not pristine FF')
        b[po:po+2]=pos.to_bytes(2,'little')
        b[dst:dst+len(s)]=s
        rows.append({'number':number,'pointer_offset':f'0x{po:X}','string_offset':f'0x{dst:X}'})
        pos += len(s)
    return rows

def patch_arthur_stats(b):
    # Reuse the screen's own 42-glyph atlas; no renderer/code change.
    atlas=SEGF+0x4C84
    count=int.from_bytes(b[atlas:atlas+2],'little')
    if count != 0x2A: raise SystemExit(f'Arthur atlas count mismatch: {count}')
    alpha_codes=[0x0B,0x0C,0x0D,0x10,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x21,0x22,0x23,0x24,0x25,0x26,0x27,0x28,0x29]
    enc={chr(65+i):alpha_codes[i] for i in range(26)}
    enc[' ']=0x0E
    for ch,code in enc.items():
        if ch==' ': continue
        w=fontword(ch)
        b[atlas+2+2*code:atlas+4+2*code]=w.to_bytes(2,'little')
    # blank/spacing tokens
    blank_word=0x0005
    for code in (0x0E,0x0F,0x20):
        b[atlas+2+2*code:atlas+4+2*code]=blank_word.to_bytes(2,'little')
    # Dynamic time suffixes: 時 -> H, 分 -> M. Counts no longer need 回.
    b[atlas+2+2*0x1F:atlas+4+2*0x1F]=fontword('H').to_bytes(2,'little')
    b[atlas+2+2*0x0A:atlas+4+2*0x0A]=fontword('M').to_bytes(2,'little')
    # token 0x11 remains the original colon glyph
    labels=['DEATHS','JUMPS','CROUCH','LADDER','STEPS','PANTS','PANTS TIME','BABY','BABY TIME','ELDER','ELDER TIME','WOMAN','WOMAN TIME']
    encoded=[bytes(enc[ch] for ch in s)+b'\xFF' for s in labels]
    ptrbase=SEGF+0x4D36
    pos=0x4D51
    if sum(map(len,encoded)) > 0x67: raise SystemExit('Arthur label block overflow')
    entries=[]
    for i,s in enumerate(encoded):
        po=ptrbase+1+2*i
        b[po:po+2]=pos.to_bytes(2,'little')
        b[SEGF+pos:SEGF+pos+len(s)]=s
        entries.append({'index':i,'text':labels[i],'offset':f'0x{SEGF+pos:X}'})
        pos += len(s)
    b[SEGF+pos:SEGF+0x4DB8]=b'\xFF'*(0x4DB8-pos)
    return entries, pos

def patch_arthur_header(b):
    # Native header アーサー情報 is a 64x24 2bpp overlay at D000:F8F7.
    # Localize it as concise UI heading "ARTHUR" using the game's own
    # Latin 8x16 glyphs. This preserves the surrounding decorative pixels.
    base=SEGD+0xF8F7
    pix=[[3]*64 for _ in range(24)]
    for t in range(23):
        tile=decode_tile(b[base+t*16:base+(t+1)*16])
        tx=t%8; ty=t//8
        for y in range(8):
            for x in range(8): pix[ty*8+y][tx*8+x]=tile[y][x]
    # Clear only the former text interior; keep ornamental edge pixels.
    for y in range(8,24):
        for x in range(3,61): pix[y][x]=3
    # Header tile palette is reversed relative to the text-font tiles.
    palmap={0:3,1:0,2:1,3:2}
    x0=8
    for i,ch in enumerate('ARTHUR'):
        g=glyph_8x16(b,ch)
        for y in range(16):
            for x in range(8): pix[8+y][x0+i*8+x]=palmap[g[y][x]]
    for t in range(23):
        tx=t%8;ty=t//8
        tile=[[pix[ty*8+y][tx*8+x] for x in range(8)] for y in range(8)]
        b[base+t*16:base+(t+1)*16]=encode_tile(tile)
    return {'offset':f'0x{base:X}','size':23*16,'localized':'ARTHUR','source_meaning':'Arthur information'}

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    root=Path(__file__).resolve().parent.parent
    hf1=bps_apply(base,(root/'reference/Makaimura_EN_US_Phase4W_HF1_CUMULATIVE_FROM_JP.bps').read_bytes())
    if sha(hf1)!=EXPECTED_HF1: raise SystemExit('HF1 reconstruction mismatch: '+sha(hf1))
    b=bytearray(hf1)
    content_rows=patch_contents_numbering(b)
    stat_rows,stat_end=patch_arthur_stats(b)
    header=patch_arthur_header(b)
    b[-2:]=(ws_checksum(b)).to_bytes(2,'little')
    return bytes(b),hf1,{'contents_rows':content_rows,'arthur_stats':stat_rows,'stats_strings_end':f'0x{stat_end:04X}','header':header}

def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf2.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes(); outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF2_PRIVATE.ws')
    out,hf1,details=build(base); outp.write_bytes(out)
    print(json.dumps({'phase':'Phase4W-HF2','base_sha256':sha(base),'hf1_sha256':sha(hf1),'target_sha256':sha(out),'size':len(out),'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}','checksum_recalc':f'0x{ws_checksum(out):04X}','details':details},indent=2))
if __name__=='__main__': main()

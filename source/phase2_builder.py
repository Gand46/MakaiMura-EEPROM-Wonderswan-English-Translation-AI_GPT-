#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, struct, zlib

BASE_SHA256='ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
HOOK_OFF=0x14034E
HOOK_IP=0x034E
HOOK_EXPECT=bytes.fromhex('e82023')
CAVE_OFF=0x14FC90
CAVE_IP=0xFC90
CAVE_CAP=880
GLYPHS="ADEHIMNOPRSTUY'"
# 33 private tiles split across ranges unreferenced by BG0/BG1 in all four
# Library-root and all four first internal-page WRAM snapshots. Tile 0x1F0 is
# intentionally skipped because it is referenced by page content.
TILE_POSITIONS=list(range(0x1D7,0x1F0))+list(range(0x1F1,0x1F9))
assert len(TILE_POSITIONS)==33
CLEAN_TOP=bytes.fromhex('0000ffff00ffff00ff00ff00ff00ff00')
CLEAN_MID=bytes.fromhex('ff00ff00ff00ff00ff00ff00ff00ff00')
CLEAN_BOT=bytes.fromhex('ff00ff00ff00ff00ffffff0000000000')
TITLES=["ARTHUR'S HISTORY","TIPS","ITEMS","DEMONS"]


def sha256(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def ws_checksum(b:bytes)->int: return sum(b[:-2]) & 0xffff

def _bps_num(v:int)->bytes:
    if v < 0: raise ValueError('negative BPS varint')
    out=bytearray()
    while True:
        x=v & 0x7f; v >>= 7
        if v==0:
            out.append(x|0x80); return bytes(out)
        out.append(x); v-=1

def bps_create(source:bytes,target:bytes,metadata:bytes=b'')->bytes:
    out=bytearray(b'BPS1')
    out += _bps_num(len(source)) + _bps_num(len(target)) + _bps_num(len(metadata)) + metadata
    i=0
    while i < len(target):
        same=i < len(source) and source[i]==target[i]
        j=i+1
        if same:
            while j<len(target) and j<len(source) and source[j]==target[j]: j+=1
            mode=0; payload=b''
        else:
            while j<len(target) and not (j<len(source) and source[j]==target[j]): j+=1
            mode=1; payload=target[i:j]
        out += _bps_num(((j-i-1)<<2)|mode)
        if mode==1: out += payload
        i=j
    out += (zlib.crc32(source)&0xffffffff).to_bytes(4,'little')
    out += (zlib.crc32(target)&0xffffffff).to_bytes(4,'little')
    out += (zlib.crc32(out)&0xffffffff).to_bytes(4,'little')
    return bytes(out)

class Emit16:
    def __init__(self, base_ip:int):
        self.base=base_ip; self.b=bytearray(); self.labels={}; self.fix=[]
    @property
    def ip(self): return (self.base+len(self.b)) & 0xffff
    def emit(self,*xs): self.b.extend(x & 0xff for x in xs)
    def emit_bytes(self,x:bytes): self.b.extend(x)
    def label(self,name):
        if name in self.labels: raise ValueError('duplicate label '+name)
        self.labels[name]=self.ip
    def call_abs(self,target):
        src=self.ip; rel=(target-((src+3)&0xffff))&0xffff
        self.emit(0xE8,rel&255,rel>>8)
    def jmp_abs(self,target):
        src=self.ip; rel=(target-((src+3)&0xffff))&0xffff
        self.emit(0xE9,rel&255,rel>>8)
    def jmp(self,label):
        src=self.ip; self.emit(0xE9,0,0); self.fix.append(('rel16',len(self.b)-2,(src+3)&0xffff,label))
    def jcc8(self,op,label):
        src=self.ip; self.emit(op,0); self.fix.append(('rel8',len(self.b)-1,(src+2)&0xffff,label))
    def mov_si_label(self,label):
        self.emit(0xBE,0,0); self.fix.append(('abs16',len(self.b)-2,None,label))
    def mov_ax_cs_bx_label(self,label):
        # mov ax, cs:[bx+disp16]
        self.emit(0x2E,0x8B,0x87,0,0); self.fix.append(('abs16',len(self.b)-2,None,label))
    def resolve(self):
        for typ,pos,origin,label in self.fix:
            if label not in self.labels: raise ValueError('undefined '+label)
            dst=self.labels[label]
            if typ=='rel16':
                rel=(dst-origin)&0xffff; self.b[pos]=rel&255; self.b[pos+1]=rel>>8
            elif typ=='rel8':
                raw=(dst-origin)&0xffff
                signed=raw if raw<0x8000 else raw-0x10000
                if not -128<=signed<=127: raise ValueError(f'short jump {label} out of range {signed}')
                self.b[pos]=signed & 0xff
            else:
                self.b[pos]=dst&255; self.b[pos+1]=dst>>8
        return bytes(self.b)


def glyph_8x16(rom:bytes,ch:str)->bytes:
    if ch=="'":
        out=bytearray(32)
        rows={2:0x18,3:0x18,4:0x10,5:0x20}
        for y,v in rows.items(): out[y*2]=v
        return bytes(out)
    idx=0x150+(ord(ch)-65)
    row,col=divmod(idx,16)
    top=0x1F0000+row*0x200+col*0x10
    return rom[top:top+16]+rom[top+0x100:top+0x110]


def build_cave(rom:bytes):
    e=Emit16(CAVE_IP)
    # Consumer-exact hook for dispatcher state 0x0060 (Library root).
    # It replaces only CALL 2671 in that branch: run the original consumer first,
    # then draw the localized title overlay, and return to 0351.
    e.call_abs(0x2671)
    # Save post-dispatcher machine state, then make string ops deterministic.
    e.emit(0x9C,0x50,0x53,0x51,0x52,0x56,0x57,0x55,0x1E,0x06) # pushf, AX BX CX DX SI DI BP DS ES
    e.emit(0xFC) # cld
    # The dispatcher entered state 0x0060, but the original consumer can change
    # state during A/B transitions.  Overlay only if it is STILL the root state
    # after that consumer returns; this avoids overwriting assets just loaded by a page.
    e.emit_bytes(bytes.fromhex('813e331e6000')) # cmp word [1e33],0060
    e.jcc8(0x74,'state_ok')
    e.jmp('restore')
    e.label('state_ok')
    e.emit_bytes(bytes.fromhex('8a1e781e')) # mov bl,[1e78]
    e.emit_bytes(bytes.fromhex('80fb03'))   # cmp bl,3
    e.jcc8(0x76,'sel_ok') # JBE
    e.jmp('restore')
    e.label('sel_ok')
    # Copy 33 private 2bpp tiles (528 B) into two map-unused tile runs.
    # First 25 tiles -> 0x1D7..0x1EF (WRAM 3D70..3EFF).
    # Remaining 8 -> 0x1F1..0x1F8 (WRAM 3F10..3F8F), skipping used tile 1F0.
    e.emit_bytes(bytes.fromhex('31c08ec0')) # xor ax,ax; mov es,ax
    e.emit(0x0E,0x1F)                     # push cs; pop ds
    e.mov_si_label('tile_data')
    e.emit_bytes(bytes.fromhex('bf703d'))   # mov di,3D70
    e.emit_bytes(bytes.fromhex('b9c800'))   # mov cx,00C8 = 200 words = 400 B
    e.emit_bytes(bytes.fromhex('f3a5'))     # rep movsw
    e.emit_bytes(bytes.fromhex('bf103f'))   # mov di,3F10
    e.emit_bytes(bytes.fromhex('b94000'))   # mov cx,0040 = 64 words = 128 B
    e.emit_bytes(bytes.fromhex('f3a5'))
    e.emit_bytes(bytes.fromhex('31c08ed8')) # xor ax,ax; mov ds,ax
    # Rebuild the entire 24-cell interior of the 4-row title box, preserving its native frame.
    clean_top_idx,clean_mid_idx,clean_bot_idx=TILE_POSITIONS[-3:]
    clear_specs=[
        (0x0800+clean_top_idx,0x1344),
        (0x0800+clean_mid_idx,0x1384),
        (0x0800+clean_mid_idx,0x13C4),
        (0x0800+clean_bot_idx,0x1404),
    ]
    for word,di in clear_specs:
        e.emit(0xB8,word&255,word>>8)
        e.emit(0xBF,di&255,di>>8)
        e.emit(0xB9,0x18,0x00)
        e.emit_bytes(bytes.fromhex('f3ab'))
    e.emit_bytes(bytes.fromhex('ba0008')) # mov dx,0800 (palette/attrs)
    # Select compact slot stream and centered tilemap destination.
    e.emit_bytes(bytes.fromhex('80fb01')); e.jcc8(0x74,'setup1')
    e.emit_bytes(bytes.fromhex('80fb02')); e.jcc8(0x74,'setup2')
    e.emit_bytes(bytes.fromhex('80fb03')); e.jcc8(0x74,'setup3')
    e.label('setup0')
    e.mov_si_label('title0'); e.emit_bytes(bytes.fromhex('bf8c13b91000')); e.jmp('draw')
    e.label('setup1')
    e.mov_si_label('title1'); e.emit_bytes(bytes.fromhex('bf9813b90400')); e.jmp('draw')
    e.label('setup2')
    e.mov_si_label('title2'); e.emit_bytes(bytes.fromhex('bf9613b90500')); e.jmp('draw')
    e.label('setup3')
    e.mov_si_label('title3'); e.emit_bytes(bytes.fromhex('bf9613b90600'))
    e.label('draw')
    e.emit_bytes(bytes.fromhex('2e8a04')) # mov al,cs:[si]
    e.emit(0x46)                          # inc si
    e.emit_bytes(bytes.fromhex('3cff'))   # cmp al,ff
    e.jcc8(0x74,'skip_cell')
    e.emit_bytes(bytes.fromhex('30e4'))   # xor ah,ah
    e.emit_bytes(bytes.fromhex('d1e0'))   # shl ax,1 (word-table index)
    e.emit_bytes(bytes.fromhex('8bd8'))   # mov bx,ax
    e.mov_ax_cs_bx_label('top_index_table')
    e.emit_bytes(bytes.fromhex('09d0'))   # or ax,dx
    e.emit_bytes(bytes.fromhex('8905'))   # mov [di],ax
    e.mov_ax_cs_bx_label('bottom_index_table')
    e.emit_bytes(bytes.fromhex('09d0'))
    e.emit_bytes(bytes.fromhex('894540')) # mov [di+40],ax
    e.label('skip_cell')
    e.emit_bytes(bytes.fromhex('83c702')) # add di,2
    e.jcc8(0xE2,'draw')                   # loop
    e.jmp('restore')
    e.label('restore')
    e.emit(0x07,0x1F,0x5D,0x5F,0x5E,0x5A,0x59,0x5B,0x58,0x9D) # pop ES DS BP DI SI DX CX BX AX; popf
    e.emit(0xC3) # ret to dispatcher after the consumer-specific wrapper

    # Tile-index lookup permits the glyph halves to span two disjoint safe runs.
    e.label('top_index_table')
    for i in range(len(GLYPHS)):
        e.emit_bytes(TILE_POSITIONS[i*2].to_bytes(2,'little'))
    e.label('bottom_index_table')
    for i in range(len(GLYPHS)):
        e.emit_bytes(TILE_POSITIONS[i*2+1].to_bytes(2,'little'))
    # Embedded tile bytes follow the TILE_POSITIONS order: 30 glyph halves + 3 clean frame tiles.
    e.label('tile_data')
    tile_data=b''.join(glyph_8x16(rom,ch) for ch in GLYPHS)+CLEAN_TOP+CLEAN_MID+CLEAN_BOT
    assert len(tile_data)==528
    e.emit_bytes(tile_data)
    gmap={ch:i for i,ch in enumerate(GLYPHS)}
    for ti,title in enumerate(TITLES):
        e.label(f'title{ti}')
        slots=bytes(0xFF if ch==' ' else gmap[ch] for ch in title)
        e.emit_bytes(slots)
    cave=e.resolve()
    layout={
        'runtime_base_ip':f'0x{CAVE_IP:04X}', 'size':len(cave),'capacity':CAVE_CAP,
        'labels':{k:f'0x{v:04X}' for k,v in e.labels.items()},
        'tile_indices':[f'0x{x:03X}' for x in TILE_POSITIONS],'tile_count':33,'tile_ram_ranges':['0x3D70-0x3EFF','0x3F10-0x3F8F'],
        'glyph_order':GLYPHS,'titles':TITLES,
    }
    if len(cave)>CAVE_CAP: raise ValueError(f'cave overflow {len(cave)}/{CAVE_CAP}')
    return cave,layout


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('base'); ap.add_argument('output'); ap.add_argument('--manifest'); ap.add_argument('--cave-bin'); ap.add_argument('--bps')
    a=ap.parse_args()
    src=Path(a.base).read_bytes()
    if sha256(src)!=BASE_SHA256: raise SystemExit('ERROR: base SHA-256 mismatch')
    if src[HOOK_OFF:HOOK_OFF+len(HOOK_EXPECT)]!=HOOK_EXPECT: raise SystemExit('ERROR: hook signature mismatch')
    if any(x!=0xFF for x in src[CAVE_OFF:CAVE_OFF+CAVE_CAP]): raise SystemExit('ERROR: cave is not pristine FF')
    stored=int.from_bytes(src[-2:],'little'); calc=ws_checksum(src)
    if stored!=0x3BA9 or calc!=0x3BA9: raise SystemExit(f'ERROR: base checksum {stored:04X}/{calc:04X}')
    cave,layout=build_cave(src)
    out=bytearray(src)
    # Hook: replace Library-root branch CALL 2671 with CALL FC90.
    rel=(CAVE_IP-((HOOK_IP+3)&0xffff))&0xffff
    hook=bytes([0xE8,rel&255,rel>>8])
    out[HOOK_OFF:HOOK_OFF+len(HOOK_EXPECT)]=hook
    out[CAVE_OFF:CAVE_OFF+len(cave)]=cave
    newcs=ws_checksum(out); out[-2:]=newcs.to_bytes(2,'little')
    out=bytes(out)
    Path(a.output).write_bytes(out)
    bps_info=None
    if a.bps:
        metadata=(
            'Makaimura WonderSwan EN-US Phase 2 Style Pilot; base SHA256 '+BASE_SHA256+
            '; Library root labels only'
        ).encode('utf-8')
        patch=bps_create(src,out,metadata)
        Path(a.bps).write_bytes(patch)
        bps_info={
            'path':str(a.bps),'size':len(patch),'sha256':sha256(patch),
            'source_crc32':f'{zlib.crc32(src)&0xffffffff:08x}',
            'target_crc32':f'{zlib.crc32(out)&0xffffffff:08x}',
            'patch_crc32':f'{int.from_bytes(patch[-4:],"little"):08x}'
        }
    changed=[i for i,(x,y) in enumerate(zip(src,out)) if x!=y]
    # Compress changed offsets into ranges.
    ranges=[]
    if changed:
        s=p=changed[0]
        for x in changed[1:]:
            if x==p+1: p=x
            else: ranges.append([s,p]); s=p=x
        ranges.append([s,p])
    man={
      'schema':1,'phase':'2-style-pilot','base_sha256':sha256(src),'target_sha256':sha256(out),
      'size':len(out),'base_checksum':f'0x{stored:04X}','target_checksum':f'0x{newcs:04X}',
      'target_checksum_recalc':f'0x{ws_checksum(out):04X}',
      'hook_offset':f'0x{HOOK_OFF:X}','hook_before':HOOK_EXPECT.hex(),'hook_after':hook.hex(),
      'cave_offset':f'0x{CAVE_OFF:X}','cave_size':len(cave),'cave_capacity':CAVE_CAP,
      'changed_byte_count':len(changed),'changed_ranges':[[f'0x{s:X}',f'0x{e:X}'] for s,e in ranges],
      'layout':layout,
      'save_type':out[-5] if len(out)>=5 else None,
      'titles':TITLES,
      'bps':bps_info,
      'scope':'Library root carousel overlay only; internal pages intentionally unchanged in this pilot.'
    }
    if a.manifest: Path(a.manifest).write_text(json.dumps(man,indent=2)+"\n")
    if a.cave_bin: Path(a.cave_bin).write_bytes(cave)
    print(json.dumps(man,indent=2))

if __name__=='__main__': main()

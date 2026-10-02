#!/usr/bin/env python3
"""Clean JP -> HF20 + relocated EEPROM 4.1E-r2. Python3 + GNU binutils."""
from pathlib import Path
import argparse,csv,hashlib,json,struct,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path[:0]=[str(ROOT.parents[1]/'source'),str(HERE/'eeprom')]
from build_phase4w_hf20 import build as hf20_build
from build_project import assemble,patch_rel16,patch_word
from ws_patch_tools import bps
from verify_bps import apply as independent_apply
H=lambda b:hashlib.sha256(b).hexdigest()
JP='ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
HF20='885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51'
TARGET='abd2440a261dfd8aa1a01f215c829ea08617536e48909c9be54dbe26e6c4b713'
MAIN=0xE200;AUX=0xDF38;BRIDGE=0xFF60
NATIVE={'sig':0x093B,'init':0x053F,'pause_start':0xA237,'pause_ui':0xA2B2,'keys':0xF724,'finalize':0xF3AA,'redraw':0x122F,'glyph':0xF349}
ENTRIES={'boot':'boot_wrapper','pause_start':'pause_start_wrapper','pause_ui':'pause_ui_wrapper','finalize':'options_render_finalize'}
DISPS={'boot_sig_disp':'sig','pause_start_orig_disp':'pause_start','pause_orig_disp':'pause_ui','key_read_disp':'keys','native_sig_disp':'sig','native_init_disp':'init','options_finalize_disp':'finalize','options_redraw_disp':'redraw','draw_glyph_disp':'glyph'}
def build(jp,work):
    if len(jp)!=0x200000 or H(jp)!=JP:raise ValueError('Expected clean Japanese ROM')
    hf,_,_=hf20_build(jp)
    if H(hf)!=HF20:raise ValueError('HF20 reconstruction mismatch')
    work.mkdir(parents=True,exist_ok=True)
    bridges=bytearray();native_addr={}
    for name,target in NATIVE.items():
        addr=BRIDGE+len(bridges);native_addr[name]=addr
        bridges+=b'\xE8'+struct.pack('<H',(target-(addr+3))&65535)+b'\xCB'
    asm=(HERE/'eeprom/main_shim.S').read_text()+'\n/* HF20: CS-preserving adapters. */\n'
    for name,addr in native_addr.items():
        asm+=f'.global native_{name}\nnative_{name}:\n.byte 0x9A\n.word {addr},0x4000\nret\n'
    for name,target in ENTRIES.items():asm+=f'.global entry_{name}\nentry_{name}:\ncall {target}\nretf\n'
    (work/'main_port.S').write_text(asm)
    aux=(HERE/'eeprom/options_erase_shim.S').read_text()
    if aux.count('.word 0x0000, 0x4000')!=3:raise ValueError('Aux source precondition')
    (work/'aux_port.S').write_text(aux.replace('.word 0x0000, 0x4000','.word 0x0000, 0x5000'))
    main,ms=assemble(work/'main_port.S',MAIN,'main',work);aux,aus=assemble(work/'aux_port.S',AUX,'aux',work)
    if AUX+len(aux)>MAIN or MAIN+len(main)>0x10000:raise ValueError('Bank overlap/overflow')
    for sym,target in DISPS.items():patch_rel16(main,ms,MAIN,sym,ms['native_'+target])
    for sym,target in [('main_reset_off','native_reset_far'),('main_commit_off','eeprom_commit_far'),('main_draw_glyph_off','draw_glyph_far')]:patch_word(aux,aus,AUX,sym,ms[target])
    patch_word(main,ms,MAIN,'aux_render_off',aus['render_options_ui'])
    entry_addr={}
    for name in ENTRIES:
        entry_addr[name]=BRIDGE+len(bridges)
        bridges+=b'\x9A'+struct.pack('<HH',ms['entry_'+name],0x5000)+b'\xC3'
    if BRIDGE+len(bridges)>0x10000:raise ValueError('Bridge overflow')
    out=bytearray(hf);allowed=set();writes=[]
    def put(off,new,expected,role):
        if len(expected)!=len(new) or bytes(out[off:off+len(expected)])!=expected:raise ValueError(f'Precondition {role} at {off:06X}')
        out[off:off+len(new)]=new;allowed.update(range(off,off+len(new)))
        writes.append({'offset':hex(off),'size':len(new),'role':role,'before':H(expected),'after':H(new)})
    rows=list(csv.DictReader((HERE/'eeprom/Makaimura_SRAM_Segment_Patchpoints_Phase2.csv').open()))
    if len(rows)!=127:raise ValueError('Patchpoint count')
    for row in rows:
        off=int(row['file_offset_load'],16)
        if not 0xB8<=out[off]<=0xBF:raise ValueError('MOV precondition')
        put(off+1,b'\x37\x00',b'\x00\x10','SRAM selector -> mirror')
    for addr,data,label in [(0x150000+MAIN,main,'main relocated'),(0x150000+AUX,aux,'options'),(0x140000+BRIDGE,bridges,'CS bridges')]:put(addr,data,b'\xFF'*len(data),label)
    for off,name,old in [(0x140523,'boot','e81504'),(0x146E96,'pause_start','e89e33'),(0x146E99,'pause_ui','e81634'),(0x141274,'finalize','e833e1')]:put(off,b'\xE8'+struct.pack('<H',(entry_addr[name]-((off&65535)+3))&65535),bytes.fromhex(old),name+' hook')
    put(0x141039,b'\xEA'+struct.pack('<HH',aus['options_entry'],0x5000),bytes.fromhex('b837008ec0'),'OPTIONS input')
    put(len(out)-5,b'\x20',b'\x02','EEPROM2K header')
    put(len(out)-2,struct.pack('<H',sum(out[:-2])&65535),hf[-2:],'WS checksum')
    changes={i for i,(a,b) in enumerate(zip(hf,out)) if a!=b};translation={i for i,(a,b) in enumerate(zip(jp[:-2],hf[:-2])) if a!=b}
    if changes-allowed or translation&changes:raise ValueError('Unexpected changes/translation overwritten')
    if H(out)!=TARGET:raise ValueError('Target hash mismatch')
    patch=bps.create(jp,bytes(out));inc=bps.create(hf,bytes(out))
    if bps.apply(jp,patch)!=out or independent_apply(jp,patch)!=out or independent_apply(hf,inc)!=out:raise ValueError('BPS roundtrip')
    manifest={'release':'HF20 + EEPROM v1','jp_sha256':JP,'hf20_sha256':HF20,'target_sha256':H(out),'bps_sha256':H(patch),'hf20_bps_sha256':H(inc),'checksum':hex(sum(out[:-2])&65535),'size':len(out),'save_type':32,'translated_bytes_preserved':len(translation),'translated_bytes_overwritten':0,'changed_bytes_from_hf20':len(changes),'unexpected_changes':0,'main_bytes':len(main),'aux_bytes':len(aux),'bridge_bytes':len(bridges),'program_command_cpu_address':hex(0x50000+ms['program_word_out']),'main_symbols':ms,'aux_symbols':aus,'writes':writes}
    return bytes(out),patch,inc,manifest
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('original',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():p.error('Choose a new output directory')
    a.out.mkdir(parents=True);out,patch,inc,manifest=build(a.original.read_bytes(),a.out/'assembly')
    (a.out/'Makaimura_HF20_EEPROM_v1.ws').write_bytes(out)
    (a.out/'Makaimura_HF20_EEPROM_v1_FROM_JP.bps').write_bytes(patch)
    (a.out/'Makaimura_HF20_EEPROM_v1_FROM_HF20.bps').write_bytes(inc)
    (a.out/'BUILD.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in ('writes','main_symbols','aux_symbols')},indent=2))
if __name__=='__main__':main()

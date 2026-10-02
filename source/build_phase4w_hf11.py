#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys
from build_phase4w_hf10 import build as build_hf10
from build_phase4w_hf2 import ws_checksum, SIZE, EXPECTED_JP
from verify_bps import apply as bps_apply

EXPECTED_HF10='60f9a85690e31f3cd0ce71da7da28db7c553ac68af0fe8773682c47a4a96f6f2'
EXPECTED_PHASE4W='f9ad88e458fd603081bde91cf3f49399307f96e65016b3123410095e7a1d11dd'
SEG_E=0x1E0000
PRIVATE_BASE=0xC700
PRIVATE_MAIN_LEN=0x366A-0x32D0
PRIVATE_OVF_BASE=PRIVATE_BASE+PRIVATE_MAIN_LEN
PRIVATE_OVF_LEN=(0xFFE5-0xFF77)
PRIVATE_PLACEHOLDER=PRIVATE_OVF_BASE+PRIVATE_OVF_LEN
PRIVATE_NAMES_BASE=0xCB20
PRIVATE_NAME_WIDTH=10
PRIVATE_NAMES_COUNT=42
PRIVATE_NAMES_SIZE=PRIVATE_NAMES_COUNT*(PRIVATE_NAME_WIDTH+1)
PRIVATE_TOTAL=(PRIVATE_NAMES_BASE-PRIVATE_BASE)+PRIVATE_NAMES_SIZE
CODE_SEG_IMM=0x143032
CODE_SI_IMM=0x143036
LIST_PRIVATE_SI=PRIVATE_BASE+(0x3388-0x32D0)
LIST_LOAD_SEQS=[0x143222,0x143242,0x14326B]


def sha(b): return hashlib.sha256(b).hexdigest()

def relocate_ptr(v):
    if 0x32D0 <= v < 0x366A:
        return PRIVATE_BASE + (v-0x32D0)
    if 0xFF77 <= v < 0xFFE5:
        return PRIVATE_OVF_BASE + (v-0xFF77)
    raise ValueError(f'pointer 0x{v:04X} outside relocatable ranges')

def patch_private_demon_index(base,b,phase4w):
    dst=SEG_E+PRIVATE_BASE
    if any(x!=0xFF for x in b[dst:dst+PRIVATE_TOTAL]):
        raise SystemExit('HF11 private E000 cave is not pristine FF')

    main=bytearray(phase4w[0x1D32D0:0x1D366A])
    ovf=bytes(phase4w[0x1DFF77:0x1DFFE5])

    # Relocate only known pointer fields; never scan/modify encoded strings blindly.
    ptr_fields=[]
    def rw(orig_off):
        i=orig_off-0x32D0
        old=int.from_bytes(main[i:i+2],'little')
        new=relocate_ptr(old)
        main[i:i+2]=new.to_bytes(2,'little')
        ptr_fields.append({'field':f'0x{orig_off:04X}','old':f'0x{old:04X}','new':f'0x{new:04X}'})

    rw(0x32D0)                           # descriptor -> local atlas
    for i in range(42): rw(0x338B+2*i)  # N0001..N0042 label pointers
    for i in range(43): rw(0x33ED+2*i)  # sentinel + 42 Demon-name pointers

    # Phase4W repurposed atlas token 1 as a duplicate 'N'.  The locked-list
    # renderer uses token 1 for its native '?' placeholder, which is exactly
    # what caused the historical NNNNNNNN corruption.  Preserve the clean/HF10
    # shared token-1 glyph in the private atlas while names continue to use the
    # separate normal N token (0x1A).
    shared_placeholder_word=int.from_bytes(b[0x1D32D6:0x1D32D8],'little')
    main[0x32D6-0x32D0:0x32D8-0x32D0]=shared_placeholder_word.to_bytes(2,'little')

    # Use a private 10-character locked placeholder. Phase4W's 8-char
    # placeholder can leave the tail of longer English names visible underneath
    # because the game draws the real name first and then overlays the lock mask.
    # Table entry 50 is the placeholder pointer (field 0x33ED).
    ph_field=0x33ED-0x32D0
    main[ph_field:ph_field+2]=PRIVATE_PLACEHOLDER.to_bytes(2,'little')

    b[dst:dst+len(main)]=main
    b[SEG_E+PRIVATE_OVF_BASE:SEG_E+PRIVATE_OVF_BASE+len(ovf)]=ovf
    b[SEG_E+PRIVATE_PLACEHOLDER:SEG_E+PRIVATE_PLACEHOLDER+11]=bytes([0x01])*10+b'\xFF'

    # This instruction sequence is the Demon INDEX list consumer only:
    #   mov ax,D000 / mov ds,ax / mov si,32D0 / ... far call D000:087B
    if b[CODE_SEG_IMM] != 0xD0 or b[CODE_SI_IMM:CODE_SI_IMM+2] != b'\xD0\x32':
        raise SystemExit('HF11 Demon INDEX consumer signature mismatch')
    b[CODE_SEG_IMM]=0xE0
    b[CODE_SI_IMM:CODE_SI_IMM+2]=PRIVATE_BASE.to_bytes(2,'little')

    # The scrolling renderer makes three separate calls with SI=3388.
    # Redirect each consumer to the corresponding offset inside the private clone.
    list_consumer_patches=[]
    for off in LIST_LOAD_SEQS:
        sig=b'\xB8\x00\xD0\x8E\xD8\xBE\x88\x33'
        if bytes(b[off:off+8]) != sig:
            raise SystemExit(f'HF11 list consumer signature mismatch at 0x{off:X}: '+bytes(b[off:off+8]).hex())
        b[off+2]=0xE0
        b[off+6:off+8]=LIST_PRIVATE_SI.to_bytes(2,'little')
        list_consumer_patches.append({'offset':f'0x{off:X}','segment':'E000','si':f'0x{LIST_PRIVATE_SI:04X}'})

    # Decode the English names copied from the known Phase4W resource for manifest/audit.
    atlas_count=int.from_bytes(phase4w[0x1D32D2:0x1D32D4],'little')
    atlas=[int.from_bytes(phase4w[0x1D32D4+2*i:0x1D32D6+2*i],'little') for i in range(atlas_count)]
    inv={0x0005:' '}
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        idx=0x150+(ord(ch)-65); row,col=divmod(idx,16); inv[row*0x20+col]=ch
    names=[]
    for i in range(1,43):
        po=0x1D33ED+2*i
        p=int.from_bytes(phase4w[po:po+2],'little')
        off=0x1D0000+p
        chars=[]
        while phase4w[off]!=0xFF:
            tok=phase4w[off]
            chars.append(inv.get(atlas[tok],f'<{tok:02X}>') if tok < len(atlas) else f'[{tok:02X}]')
            off+=1
        names.append(''.join(chars))

    # Repack every Demon name to a fixed 10-cell field. The original renderer
    # does not erase trailing cells when a shorter string replaces a longer one
    # during scrolling; explicit blank-token padding prevents residual glyphs.
    enc={' ':0x00}
    for tok,w in enumerate(atlas):
        ch=inv.get(w)
        if ch and ch!=' ': enc[ch]=tok
    # Force the normal N token rather than token 1 (reserved for '?').
    enc['N']=next(tok for tok,w in enumerate(atlas) if tok!=1 and inv.get(w)=='N')
    for i,name in enumerate(names):
        if len(name)>PRIVATE_NAME_WIDTH:
            raise SystemExit(f'Demon name exceeds fixed width: {name!r}')
        try: data=bytes(enc[ch] for ch in name.ljust(PRIVATE_NAME_WIDTH))+b'\xFF'
        except KeyError as e: raise SystemExit(f'unencodable Demon name char {e} in {name!r}')
        ptr=PRIVATE_NAMES_BASE+i*(PRIVATE_NAME_WIDTH+1)
        b[SEG_E+ptr:SEG_E+ptr+len(data)]=data
        # Name entries are table indices 51..92 in the structure based at 0x3388.
        field=SEG_E+LIST_PRIVATE_SI+1+2*(51+i)
        b[field:field+2]=ptr.to_bytes(2,'little')

    return {
        'consumer_patch':{
            'segment_immediate_offset':f'0x{CODE_SEG_IMM:X}','segment':'E000',
            'si_immediate_offset':f'0x{CODE_SI_IMM:X}','si':f'0x{PRIVATE_BASE:04X}',
            'list_renderer_calls':list_consumer_patches,
        },
        'private_resource':{
            'segment':'E000','main':f'0x{PRIVATE_BASE:04X}-0x{PRIVATE_BASE+PRIVATE_MAIN_LEN-1:04X}',
            'overflow':f'0x{PRIVATE_OVF_BASE:04X}-0x{PRIVATE_OVF_BASE+len(ovf)-1:04X}',
            'bytes':PRIVATE_TOTAL,
            'locked_placeholder':f'0x{PRIVATE_PLACEHOLDER:04X}',
            'locked_placeholder_length':10,
            'fixed_name_pool':f'0x{PRIVATE_NAMES_BASE:04X}-0x{PRIVATE_NAMES_BASE+PRIVATE_NAMES_SIZE-1:04X}',
            'fixed_name_width':PRIVATE_NAME_WIDTH,
        },
        'relocated_pointer_fields':len(ptr_fields),
        'locked_placeholder_token1_word':f'0x{shared_placeholder_word:04X}',
        'names':names,
    }

def build(base):
    if len(base)!=SIZE or sha(base)!=EXPECTED_JP:
        raise SystemExit('wrong original JP ROM; SHA-256='+sha(base))
    hf10,_,d10=build_hf10(base)
    if sha(hf10)!=EXPECTED_HF10:
        raise SystemExit('HF10 reconstruction mismatch: '+sha(hf10))
    root=Path(__file__).resolve().parent.parent
    phase4w=bps_apply(base,(root/'reference/Makaimura_EN_US_Phase4W_CUMULATIVE_FROM_JP.bps').read_bytes())
    if sha(phase4w)!=EXPECTED_PHASE4W:
        raise SystemExit('Phase4W reconstruction mismatch: '+sha(phase4w))
    b=bytearray(hf10)
    idx=patch_private_demon_index(base,b,phase4w)
    b[-2:]=ws_checksum(b).to_bytes(2,'little')
    return bytes(b),hf10,{'hf10':d10,'demon_index_private_names_hf11':idx}

def main():
    if len(sys.argv)<2: raise SystemExit('usage: build_phase4w_hf11.py original_jp.ws [out.ws]')
    base=Path(sys.argv[1]).read_bytes()
    outp=Path(sys.argv[2]) if len(sys.argv)>2 else Path('Makaimura_EN_US_Phase4W_HF11_PRIVATE.ws')
    out,hf10,details=build(base); outp.write_bytes(out)
    print(json.dumps({'phase':'Phase4W-HF11','base_sha256':sha(base),'hf10_sha256':sha(hf10),'target_sha256':sha(out),'size':len(out),'checksum':f'0x{int.from_bytes(out[-2:],"little"):04X}','checksum_recalc':f'0x{ws_checksum(out):04X}','details':details},indent=2))
if __name__=='__main__': main()

#!/usr/bin/env python3
"""Rebuild Makai-Mura WS SRAM->EEPROM2K Phase 4.1E-r2 (START-hold SAVE + OPTIONS ERASE SAVE).

Does not include/download the commercial ROM.
Requirements: Python 3 + GNU as/ld/objcopy/nm.
"""
from pathlib import Path
import argparse, csv, hashlib, re, struct, subprocess, shutil

EXPECTED_SOURCE_SHA = 'ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
EXPECTED_OUTPUT_SHA = 'f5652123b1eee5541a4c761c4818e4872a1ca9f00ce7c106708ee7d5f7044217'
EXPECTED_SIZE = 2097152
MIRROR_SEG = 0x0037
MAIN_FILE = 0x14FC90
MAIN_RUNTIME = 0xFC90
AUX_FILE = 0x15DF38
AUX_RUNTIME = 0xDF38

HERE = Path(__file__).resolve().parent
MAIN_ASM = HERE / 'main_shim.S'
AUX_ASM = HERE / 'options_erase_shim.S'
PATCHPOINTS = HERE / 'Makaimura_SRAM_Segment_Patchpoints_Phase2.csv'

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run(cmd):
    subprocess.run(cmd, check=True, timeout=15)

def symbols(elf: Path):
    txt = subprocess.check_output(['nm','-n',str(elf)], text=True, timeout=15)
    out = {}
    for line in txt.splitlines():
        m = re.match(r'([0-9a-fA-F]+)\s+\w\s+(\S+)$', line)
        if m:
            out[m.group(2)] = int(m.group(1),16)
    return out

def assemble(src: Path, base: int, stem: str, work: Path):
    obj = work / f'{stem}.o'
    elf = work / f'{stem}.elf'
    raw = work / f'{stem}.bin'
    run(['as','--32','-o',str(obj),str(src)])
    run(['ld','-m','elf_i386','-Ttext',hex(base),'-e','aux_start' if stem=='aux' else 'shim_start','-o',str(elf),str(obj)])
    run(['objcopy','-O','binary','-j','.text',str(elf),str(raw)])
    return bytearray(raw.read_bytes()), symbols(elf)

def patch_word(buf: bytearray, table: dict, base: int, sym: str, value: int):
    off = table[sym] - base
    buf[off:off+2] = struct.pack('<H', value & 0xFFFF)

def patch_rel16(buf: bytearray, table: dict, base: int, sym: str, target: int):
    addr = table[sym]
    next_ip = (addr + 2) & 0xFFFF
    disp = (target - next_ip) & 0xFFFF
    patch_word(buf, table, base, sym, disp)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('original_rom', type=Path)
    ap.add_argument('-o','--output', type=Path, default=Path('Makaimura_WS_EEPROM2K_Phase4_1E_r2_EraseSave.ws'))
    ap.add_argument('--work', type=Path, default=Path('.build_phase41e'))
    args = ap.parse_args()

    if args.original_rom.resolve() == args.output.resolve():
        raise SystemExit('ERROR: output must not overwrite original ROM')
    for tool in ('as', 'ld', 'objcopy', 'nm'):
        if not shutil.which(tool):
            raise SystemExit(f'ERROR: required GNU binutils tool not found: {tool}')
    src = args.original_rom.read_bytes()
    if len(src) != EXPECTED_SIZE:
        raise SystemExit(f'ERROR: unexpected ROM size {len(src)}')
    if sha256(src) != EXPECTED_SOURCE_SHA:
        raise SystemExit(f'ERROR: source SHA-256 mismatch: {sha256(src)}')
    for p in (MAIN_ASM,AUX_ASM,PATCHPOINTS):
        if not p.exists():
            raise SystemExit(f'ERROR: missing source file: {p}')

    args.work.mkdir(parents=True, exist_ok=True)
    mainbin, ms = assemble(MAIN_ASM, MAIN_RUNTIME, 'main', args.work)
    auxbin, aus = assemble(AUX_ASM, AUX_RUNTIME, 'aux', args.work)
    if AUX_RUNTIME + len(auxbin) > 0x10000:
        raise SystemExit('ERROR: auxiliary shim crosses a ROM bank')
    if len(mainbin) > 880:
        raise SystemExit(f'ERROR: main shim {len(mainbin)} > 880-byte cave')

    # Runtime near-call displacements inside the main shim.
    for sym,target in [
        ('boot_sig_disp',0x093B),
        ('pause_start_orig_disp',0xA237),
        ('pause_orig_disp',0xA2B2),
        ('key_read_disp',0xF724),
        ('native_sig_disp',0x093B),
        ('native_init_disp',0x053F),
        ('options_finalize_disp',0xF3AA),
        ('options_redraw_disp',0x122F),
        ('draw_glyph_disp',0xF349),
    ]:
        if sym not in ms: raise SystemExit(f'ERROR: missing main symbol {sym}')
        patch_rel16(mainbin, ms, MAIN_RUNTIME, sym, target)

    # Aux shim far-calls exported helpers in 4000h.
    for sym,target_sym in [
        ('main_reset_off','native_reset_far'),
        ('main_commit_off','eeprom_commit_far'),
        ('main_draw_glyph_off','draw_glyph_far'),
    ]:
        if sym not in aus or target_sym not in ms:
            raise SystemExit(f'ERROR: missing symbol {sym}/{target_sym}')
        patch_word(auxbin, aus, AUX_RUNTIME, sym, ms[target_sym])

    patch_word(mainbin, ms, MAIN_RUNTIME, 'aux_render_off', aus['render_options_ui'])

    b = bytearray(src)
    def patch(off, new, expected=None):
        if expected is not None:
            got = bytes(b[off:off+len(expected)])
            if got != expected:
                raise SystemExit(f'ERROR @0x{off:X}: got {got.hex()}, expected {expected.hex()}')
        b[off:off+len(new)] = new

    # Redirect all verified save-segment loads 1000h -> internal mirror 0037h.
    rows = list(csv.DictReader(PATCHPOINTS.open(newline='',encoding='utf-8')))
    if len(rows) != 127:
        raise SystemExit(f'ERROR: expected 127 SRAM segment patchpoints, got {len(rows)}')
    for row in rows:
        off = int(row['file_offset_load'],16)
        if not (0xB8 <= b[off] <= 0xBF):
            raise SystemExit(f'ERROR: not MOV r16,imm16 at 0x{off:X}')
        patch(off+1, struct.pack('<H',MIRROR_SEG), b'\x00\x10')

    # Inject code into verified FF caves.
    if any(x != 0xFF for x in b[MAIN_FILE:MAIN_FILE+len(mainbin)]):
        raise SystemExit('ERROR: main cave not FF-clean')
    if any(x != 0xFF for x in b[AUX_FILE:AUX_FILE+len(auxbin)]):
        raise SystemExit('ERROR: aux cave not FF-clean')
    b[MAIN_FILE:MAIN_FILE+len(mainbin)] = mainbin
    b[AUX_FILE:AUX_FILE+len(auxbin)] = auxbin

    # Phase 4.1D hooks, relocated to current main-shim symbol positions.
    next_ip = 0x0526
    patch(0x140523, b'\xE8'+struct.pack('<H',(ms['boot_wrapper']-next_ip)&0xFFFF), bytes.fromhex('e81504'))
    next_ip = 0x6E99
    patch(0x146E96, b'\xE8'+struct.pack('<H',(ms['pause_start_wrapper']-next_ip)&0xFFFF), bytes.fromhex('e89e33'))
    next_ip = 0x6E9C
    patch(0x146E99, b'\xE8'+struct.pack('<H',(ms['pause_ui_wrapper']-next_ip)&0xFFFF), bytes.fromhex('e81634'))

    # OPTIONS extension hooks.
    patch(0x141039, bytes([0xEA])+struct.pack('<H',aus['options_entry'])+struct.pack('<H',0x5000), bytes.fromhex('b837008ec0'))
    patch(0x141274, b'\xE8'+struct.pack('<H',(ms['options_render_finalize']-0x1277)&0xFFFF),bytes.fromhex('e833e1'))

    # Header SRAM32K -> EEPROM2K, then WonderSwan checksum.
    patch(len(b)-5,b'\x20',b'\x02')
    checksum = sum(b[:-2]) & 0xFFFF
    b[-2:] = struct.pack('<H',checksum)
    got = sha256(b)
    if got != EXPECTED_OUTPUT_SHA:
        raise SystemExit(f'ERROR: build hash mismatch: {got}')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_name(args.output.name + '.tmp')
    tmp.write_bytes(b)
    tmp.replace(args.output)
    print(f'Output: {args.output}')
    print(f'Size: {len(b)}')
    print(f'Main shim: {len(mainbin)} bytes')
    print(f'Aux shim: {len(auxbin)} bytes')
    print(f'WonderSwan checksum: 0x{checksum:04X}')
    print(f'SHA-256: {got}')
    if got != EXPECTED_OUTPUT_SHA:
        raise SystemExit('ERROR: rebuilt ROM does not match validated Phase 4.1E-r2 release')
    print('PASS: byte-identical validated Phase 4.1E-r2 ROM.')

if __name__ == '__main__':
    main()

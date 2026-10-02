#!/usr/bin/env python3
"""Reproduce integration QA in Linux Mesen. Each process bounded; total cap 40 min."""
from pathlib import Path
import argparse,sys,time,subprocess
from run_case import run
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'source'))
from build_combined import build,hf20_build
def main():
    p=argparse.ArgumentParser();p.add_argument('--jp',type=Path,required=True);p.add_argument('--mesen',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--seed',type=Path,required=True,help='Private 2048-byte EEPROM QA fixture');a=p.parse_args()
    if a.out.exists():p.error('Choose a new directory')
    a.out=a.out.resolve();a.out.mkdir(parents=True);start=time.monotonic();jp=a.jp.read_bytes()
    rom,_,_,_=build(jp,a.out/'assembly');hf,_,_=hf20_build(jp)
    combined=a.out/'combined.ws';combined.write_bytes(rom);baseline=a.out/'HF20.ws';baseline.write_bytes(hf);legacy=a.out/'legacy.ws'
    subprocess.run([sys.executable,str(ROOT/'source/eeprom/build_project.py'),str(a.jp.resolve()),'-o',str(legacy),'--work',str(a.out/'legacy_assembly')],check=True,timeout=45)
    seed=a.seed.read_bytes();assert len(seed)==2048,'Expected 2048-byte private EEPROM fixture';src=ROOT/'validation'
    def case(name,script,sd=seed,base=combined,ext='.eeprom',extra=None,timeout=45):
        if time.monotonic()-start+timeout+4>2400:raise RuntimeError('40-minute budget reached')
        run(a.mesen,base,src/script,a.out/name,sd,ext,timeout,extra)
    case('boot_migrated','test_boot_save.lua')
    for name,script in [('modal','test_erase_r2.lua'),('save','test_start_hold_save.lua'),('controls','test_options_controls.lua'),('pause_tips','test_pause_tip_inputs.lua'),('exit','test_options_exit.lua')]:case(name,script)
    saved=(a.out/'save/after.eeprom').read_bytes();erased=(a.out/'modal/after.eeprom').read_bytes()
    case('cold_saved','test_boot_save.lua',saved);case('cold_erased','test_boot_save.lua',erased)
    case('fresh_zero','test_boot_save.lua',bytes(2048),extra={'FRESH':'1'});case('fresh_ff','test_boot_save.lua',bytes([255])*2048,extra={'FRESH':'1'})
    case('newgame_erased','test_newgame_pause.lua',erased);case('continue_saved','test_newgame_pause.lua',saved)
    case('hf20_controls','test_options_controls.lua',seed+bytes(30720),baseline,'.sav')
    for name,script in [('index','qa_natural_arthur_index_hf20.lua'),('index_tail','qa_index_tail.lua'),('ending','qa_ending_25.lua'),('credits','qa_credit_sweep_hf20.lua')]:
        for tag,rr,sd,ex in [('combined',combined,seed,'.eeprom'),('hf20',baseline,seed+bytes(30720),'.sav')]:case(name+'_'+tag,script,sd,rr,ex,timeout=80)
    for st in [0x110,0x160,0x163,0x168,0x171,0x380,0x3b0]:
        for tag,rr,sd,ex in [('combined',combined,seed,'.eeprom'),('hf20',baseline,seed+bytes(30720),'.sav')]:case(f'surface_{st:04x}_{tag}','qa_state_survey.lua',sd,rr,ex,{'QA_STATE':str(st)})
    for mode in [0,10,17]:
        for tag,rr,sd,ex in [('combined',combined,seed,'.eeprom'),('hf20',baseline,seed+bytes(30720),'.sav')]:case(f'mode_{mode:02x}_{tag}','qa_synthetic_modes_hf20.lua',sd,rr,ex,{'QA_MODE':str(mode),'QA_FORCE_STATE':'1'})
    tip=bytearray(seed);tip[0x22B]|=2
    for tag,rr,sd,ex in [('combined',combined,tip,'.eeprom'),('hf20',baseline,tip+bytes(30720),'.sav')]:case('tip10_'+tag,'test_tip10.lua',sd,rr,ex)
    case('legacy_saved','test_start_hold_save.lua',seed,legacy);case('cold_legacy','test_boot_save.lua',(a.out/'legacy_saved/after.eeprom').read_bytes())
    case('fresh_first_save','test_start_hold_save.lua',bytes([255])*2048);case('cold_fresh_save','test_boot_save.lua',(a.out/'fresh_first_save/after.eeprom').read_bytes())
    case('late_save','test_late_save.lua');late=(a.out/'late_save/after.eeprom').read_bytes();case('cold_late','test_boot_save.lua',late);case('continue_late','test_newgame_pause.lua',late)
    case('checkpoint_save','test_checkpoint_save.lua',tip);cp=(a.out/'checkpoint_save/after.eeprom').read_bytes()
    case('cold_checkpoint','test_boot_save.lua',cp);case('continue_checkpoint','test_newgame_pause.lua',cp)
    case('actual_continue_checkpoint','test_cold_continue.lua',cp);case('actual_continue_hf20','test_cold_continue.lua',cp+bytes(30720),baseline,'.sav')
    subprocess.run([sys.executable,str(src/'verify_results.py'),str(a.out),'--seed',str(a.seed)],check=True,timeout=30)
    print('All tests finished; native screenshots remain available for direct review.')
if __name__=='__main__':main()

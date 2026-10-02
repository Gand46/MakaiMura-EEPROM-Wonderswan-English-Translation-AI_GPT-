#!/usr/bin/env python3
"""Bounded Mesen regression suite. Uses an isolated copy of Mesen and of each save.
Requirements: Python 3, Mesen 2.1.1, original ROM, rebuilt r2 ROM, advanced test dump.
No existing Mesen profile, commercial ROM, or input save is modified.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,time,sys
HERE=Path(__file__).resolve().parent
H=lambda b:hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ('mesen','original','rom','seed','out'):ap.add_argument('--'+n,type=Path,required=True)
    ap.add_argument('--timeout',type=int,default=30)
    ap.add_argument('--total-timeout',type=int,default=540)
    a=ap.parse_args()
    if not 5<=a.timeout<=90 or not 60<=a.total_timeout<=600:ap.error('Timeout por prueba 5..90 s; total 60..600 s.')
    if a.out.exists():ap.error('Utiliza una carpeta de salida nueva.')
    for p in (a.mesen,a.original,a.rom,a.seed):
        if not p.is_file():ap.error('No existe: '+str(p))
    seed=a.seed.read_bytes()
    if H(seed)!='95285ceb6032135ec4f894e7095c9c0eb4e14ec6d1ae63fde96ca81af5e9bdfe':ap.error('Esta bateria usa el dump avanzado 95285ceb...; sus contadores esperados son especificos de ese fixture.')
    if H(a.original.read_bytes())!='ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8':ap.error('ROM original incorrecta.')
    if H(a.rom.read_bytes())!='f5652123b1eee5541a4c761c4818e4872a1ca9f00ce7c106708ee7d5f7044217':ap.error('ROM r2 incorrecta.')
    a.out=a.out.resolve(); runtime=a.out/'runtime';runtime.mkdir(parents=True)
    exe=runtime/a.mesen.name;shutil.copy2(a.mesen,exe);exe.chmod(0o755)
    (runtime/'settings.json').write_text('{}\n');saves=runtime/'Saves';saves.mkdir()
    env=os.environ.copy();env.pop('DISPLAY',None)
    if sys.platform.startswith('linux') and shutil.which('g++'):
        lib=subprocess.check_output(['g++','-print-file-name=libstdc++.so.6'],text=True,timeout=5).strip()
        if Path(lib).is_file():env['LD_PRELOAD']=lib
    deadline=time.monotonic()+a.total_timeout; results=[]
    def case(name,script,rom,sd,ext='.eeprom',fresh=False):
        remain=int(deadline-time.monotonic())
        if remain<10:raise RuntimeError('Presupuesto total agotado; resultados parciales conservados.')
        limit=min(a.timeout,remain-5);out=a.out/name;out.mkdir()
        game=out/(name+'.ws');shutil.copyfile(rom,game);save=saves/(name+ext);save.write_bytes(sd)
        e=env.copy();e['OUT']=str(out)+os.sep;e['FRESH']='1' if fresh else '0'
        cmd=[str(exe),'--testRunner',f'--timeout={limit}','--enableStdout','--doNotSaveSettings','--debug.scriptWindow.allowIoOsAccess=true',str(HERE/script),str(game)]
        started=time.monotonic();timed=False
        with (out/'mesen.log').open('w') as log:
            p=subprocess.Popen(cmd,cwd=runtime,env=e,stdout=log,stderr=subprocess.STDOUT,start_new_session=(os.name!='nt'))
            try:p.wait(timeout=limit+3)
            except subprocess.TimeoutExpired:
                timed=True
                if os.name=='nt':subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],stdout=log,stderr=log,timeout=5)
                else:os.killpg(p.pid,signal.SIGKILL)
                p.wait(timeout=3)
        rec={'name':name,'rom_sha256':H(game.read_bytes()),'seed_sha256':H(sd),'returncode':p.returncode,'timed_out':timed,'elapsed_seconds':round(time.monotonic()-started,3),'hard_limit_seconds':limit+3,'command':cmd,'LD_PRELOAD':env.get('LD_PRELOAD'),'mesen_sha256':H(exe.read_bytes())}
        if save.exists():shutil.copyfile(save,out/'after.eeprom');rec['output_save_sha256']=H(save.read_bytes())
        (out/'run.json').write_text(json.dumps(rec,indent=2));results.append(rec)
        (a.out/'results.json').write_text(json.dumps(results,indent=2));print(name,p.returncode,flush=True)
        if p.returncode or timed:raise RuntimeError('Prueba fallida: '+name+'; detener sin reintentos.')
        return out
    case('final_modal','test_erase_r2.lua',a.rom,seed)
    case('final_controls','test_options_controls.lua',a.rom,seed)
    case('original_controls','test_options_controls.lua',a.original,seed+bytes(32768-2048),'.sav')
    case('final_manual_save','test_start_hold_save.lua',a.rom,seed)
    case('final_pause_tips','test_pause_tip_inputs.lua',a.rom,seed)
    fixture=bytearray(seed);fixture[0x22B]|=2  # Isolated synthetic unlock of native Tip 10.
    case('final_tip10','test_tip10.lua',a.rom,fixture)
    case('original_tip10','test_tip10.lua',a.original,fixture+bytes(32768-2048),'.sav')
    erased=(a.out/'final_modal/erased.eeprom').read_bytes()
    case('final_boot_erased','test_boot_save.lua',a.rom,erased)
    case('final_boot_fresh','test_boot_save.lua',a.rom,bytes(2048),fresh=True)
    case('final_newgame','test_newgame_pause.lua',a.rom,erased)
    case('final_exit','test_options_exit.lua',a.rom,seed)
    print('Mesen tests PASS. Inspect screenshots and run compare_pixels.py for visual assertions.')
if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,subprocess.SubprocessError) as e:raise SystemExit('ERROR: '+str(e))

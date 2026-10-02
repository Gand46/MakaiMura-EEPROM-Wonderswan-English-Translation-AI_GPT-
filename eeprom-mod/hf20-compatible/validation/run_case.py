#!/usr/bin/env python3
"""Isolated bounded Linux Mesen execution; supplied ROM/save remain immutable."""
from pathlib import Path
import hashlib,json,os,shutil,signal,subprocess,time
H=lambda b:hashlib.sha256(b).hexdigest()
def run(mesen,rom,script,out,seed=None,ext='.eeprom',timeout=45,extra=None):
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False);runtime=out/'runtime';runtime.mkdir()
    exe=runtime/'Mesen';shutil.copyfile(mesen,exe);exe.chmod(0o755)
    (runtime/'settings.json').write_text('{}\n');(runtime/'Saves').mkdir();game=runtime/'game.ws';shutil.copyfile(rom,game)
    if seed is not None:(runtime/'Saves'/('game'+ext)).write_bytes(seed)
    env=os.environ.copy();env.pop('DISPLAY',None);lib=subprocess.check_output(['g++','-print-file-name=libstdc++.so.6'],text=True).strip()
    env.update(LD_PRELOAD=lib,OUT=str(out)+os.sep,MESEN_CAPTURE_PATH=str(out/'capture.png'),MESEN_LUA_REPORT=str(out/'lua_report.json'));env.update(extra or {})
    cmd=[str(exe),'--testRunner',f'--timeout={timeout}','--enableStdout','--doNotSaveSettings','--debug.scriptWindow.allowIoOsAccess=true',str(Path(script).resolve()),str(game)]
    started=time.monotonic();timed=False
    with (out/'mesen.log').open('w') as f:
        p=subprocess.Popen(cmd,cwd=runtime,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        try:p.wait(timeout=timeout+4)
        except subprocess.TimeoutExpired:timed=True;os.killpg(p.pid,signal.SIGKILL);p.wait()
    r={'rom_sha256':H(game.read_bytes()),'script_sha256':H(Path(script).read_bytes()),'seed_sha256':H(seed) if seed is not None else None,'mesen_sha256':H(exe.read_bytes()),'code':p.returncode,'timed_out':timed,'elapsed':round(time.monotonic()-started,3),'command':cmd,'LD_PRELOAD':lib}
    for s in (runtime/'Saves').glob('*'):shutil.copyfile(s,out/('after'+s.suffix))
    (out/'run.json').write_text(json.dumps(r,indent=2)+'\n');shutil.rmtree(runtime);print(out.name,r['code'],r['elapsed'],flush=True)
    if r['code'] or timed:raise RuntimeError('Failed test: '+out.name)
    return r

#!/usr/bin/env python3
"""Repeat the 18-mode Mesen survey on clean JP or reconstructed HF20."""
import argparse,json,os,subprocess,sys
from concurrent.futures import ThreadPoolExecutor,as_completed
from hashlib import sha256
from pathlib import Path

ROM_SHA={
 'ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8':'JP',
 '885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51':'HF20',
}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom',required=True,type=Path)
    ap.add_argument('--mesen',required=True,type=Path)
    ap.add_argument('--visual',required=True,type=Path,help='mesen_visual.py')
    ap.add_argument('--output',required=True,type=Path)
    ap.add_argument('--modes',default=','.join(str(x) for x in range(18)))
    ap.add_argument('--jobs',type=int,default=1)
    args=ap.parse_args()
    digest=sha256(args.rom.read_bytes()).hexdigest()
    if digest not in ROM_SHA:raise SystemExit('Unexpected ROM SHA-256: '+digest)
    modes=[int(x,0) for x in args.modes.split(',')]
    if len(modes)!=len(set(modes)) or any(x<0 or x>17 for x in modes):
        raise SystemExit('Use unique modes in range 0..17')
    if args.jobs<1 or args.jobs>4:raise SystemExit('--jobs must be 1..4')
    args.output.mkdir(parents=True,exist_ok=True)
    lua=Path(__file__).with_name('qa_synthetic_modes_hf20.lua')
    def capture(mode):
        dest=args.output/f'mode{mode:02d}.png'
        if dest.exists() or dest.with_suffix('.json').exists():
            raise RuntimeError(f'Output exists: {dest}')
        env=os.environ.copy();env.update(QA_MODE=str(mode),QA_FORCE_STATE='1')
        cmd=[sys.executable,str(args.visual),'capture','--mesen',str(args.mesen),
             '--rom',str(args.rom),'--lua',str(lua),'--output',str(dest),'--timeout','25']
        run=subprocess.run(cmd,env=env,capture_output=True,text=True)
        if run.returncode:raise RuntimeError(f'mode {mode}: {run.stderr[-400:]}')
        report=json.loads((args.output/f'mode{mode:02d}.lua.json').read_text())
        assert report['method']=='WRAM_POKE' and report['target_mode']==mode
        return report
    results=[]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for future in as_completed([pool.submit(capture,x) for x in modes]):
            results.append(future.result())
    results.sort(key=lambda x:x['target_mode'])
    summary={'rom':ROM_SHA[digest],'rom_sha256':digest,'emulator':'Mesen 2.1.1',
      'access':'WRAM_POKE plus SYNTHETIC_STATE','input':'START, DOWN, A; mode+0x0170 at frame3400',
      'modes':results}
    (args.output/'MODE_SURVEY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'rom':ROM_SHA[digest],'modes':[x['target_mode'] for x in results],
                      'report':str(args.output/'MODE_SURVEY.json')}))

if __name__=='__main__':main()

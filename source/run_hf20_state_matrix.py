from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import os,subprocess,json,argparse
ROOT=Path(__file__).resolve().parent.parent
PARSER=argparse.ArgumentParser()
PARSER.add_argument('--jp',default='original.ws')
PARSER.add_argument('--hf20',default='hf20.ws')
PARSER.add_argument('--mesen',default='mesen-2.1.1/Mesen')
PARSER.add_argument('--visual',default='mesen_visualization_source_v1.1.0/scripts/mesen_visual.py')
PARSER.add_argument('--output',default='qa/state_matrix_hf20')
ARGS=PARSER.parse_args() if __name__=='__main__' else PARSER.parse_args([])
OUT=ROOT/ARGS.output;OUT.mkdir(parents=True,exist_ok=True)
if __name__!='__main__' and (ROOT/'evidence'/'rc_gate_hf20'/'raw_states').exists():
 OUT=ROOT/'evidence'/'rc_gate_hf20'/'raw_states'
LUA=Path(__file__).resolve().parent/'qa_state_survey.lua'
if not LUA.exists():LUA=ROOT/'Makaimura_PHASE4W_HF20_RC_GATE_AUDIT_2026-09-28'/'source'/'qa_state_survey.lua'
STATES=[0x110,0x111,0x112,0x120,0x131,0x132,0x133,0x134,
        0x140,0x150,*range(0x160,0x16c),0x171,0x1b0,
        0x265,0x267,0x280,0x2b0,0x380,0x3b0]
def run(item):
 name,state=item
 dest=OUT/f'{name}_{state:04x}.png';env=os.environ.copy();env['QA_STATE']=str(state)
 p=subprocess.run(['python3',ARGS.visual,'capture',
  '--mesen',ARGS.mesen,'--rom',ARGS.jp if name=='jp' else ARGS.hf20,
  '--lua',str(LUA),
  '--output',str(dest),'--timeout','30'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=40)
 return {'rom':name,'state':state,'exit':p.returncode,'output':p.stdout[-180:] if p.returncode else None,'error':p.stderr[-500:] if p.returncode else None}
if __name__=='__main__':
 tasks=[(name,state) for state in STATES for name in ('jp','hf20')]
 with ThreadPoolExecutor(max_workers=6) as pool:res=list(pool.map(run,tasks))
 (OUT/'runs.json').write_text(json.dumps(res,indent=2)+'\n')
 print(json.dumps({'states':len(STATES),'runs':len(res),'passed':sum(x['exit']==0 for x in res),'failed':[x for x in res if x['exit']]},indent=2))

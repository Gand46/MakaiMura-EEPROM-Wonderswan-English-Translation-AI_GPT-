from PIL import Image,ImageDraw,ImageChops,ImageFont
from pathlib import Path
import argparse
import json
from run_hf20_state_matrix import STATES
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--input',type=Path,default=ROOT/'evidence'/'rc_gate_hf20'/'raw_states')
OUT=parser.parse_args().input.resolve()
rec=[]
for s in STATES:
 row={'state':s,'frames':{}}
 for f in (240,360,600,900):
  a=Image.open(OUT/f'jp_{s:04x}.png.{f:04d}.png').convert('RGB');b=Image.open(OUT/f'hf20_{s:04x}.png.{f:04d}.png').convert('RGB')
  d=ImageChops.difference(a,b)
  row['frames'][str(f)]={'diff_bbox':d.getbbox(),'pixel_identical':a.tobytes()==b.tobytes()}
 for name in ('jp','hf20'):
  o=json.loads((OUT/f'{name}_{s:04x}.lua.json').read_text())['observations']
  row[name+'_trace']=o
 rec.append(row)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',13)
for frame in (360,900):
 sheet=Image.new('RGB',(6*224,5*184),(21,23,27));d=ImageDraw.Draw(sheet)
 for i,r in enumerate(rec):
  s=r['state'];x=i%6*224;y=i//6*184
  state=next(x['state'] for x in r['hf20_trace'] if x['frame']==frame)
  title=f'{s:04X}->{state:04X} ' + ('=' if r['frames'][str(frame)]['pixel_identical'] else 'DIFF')
  d.text((x+3,y+2),title,font=font,fill='#eeeecc')
  img=Image.open(OUT/f'hf20_{s:04x}.png.{frame:04d}.png').convert('RGB')
  sheet.paste(img,(x,y+24))
 sheet.save(OUT/f'HF20_STATE_MATRIX_f{frame}.png')
(OUT/'audit.json').write_text(json.dumps({'method':'SYNTHETIC_STATE at f180','states':rec},indent=2)+'\n')
print('pairs',len(rec)*4,'identical',sum(q['pixel_identical'] for r in rec for q in r['frames'].values()))
for r in rec:
 if not all(q['pixel_identical'] for q in r['frames'].values()):print(hex(r['state']),[(k,v['diff_bbox']) for k,v in r['frames'].items() if not v['pixel_identical']])

from PIL import Image,ImageDraw,ImageFont,ImageChops
from pathlib import Path
import json,hashlib,shutil
root=Path('Makaimura_PHASE4W_HF20_SYNTHETIC_STAGE_CLEAR_CHECK_2026-09-28')
ev=root/'evidence'/'synthetic_stage_clear_HF20';ev.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
canvas=Image.new('RGB',(1100,900),(25,27,32));d=ImageDraw.Draw(canvas)
d.text((20,12),'MAKAI-MURA  |  HF20  |  stage result surfaces',font=font,fill='white')
d.text((20,43),'Synthetic state injection; native Mesen 224 x 157 capture, scaled 2x',font=small,fill=(180,190,202))
rows=[]
for row,(s,label) in enumerate([(306,'0x0132 - stage selection'),(307,'0x0133 - transition animation')]):
 y=82+row*400
 d.text((24,y),label,font=font,fill=(230,213,149))
 for col,(name,rom) in enumerate([('JP','jp'),('HF20','hf20')]):
  capture_frame=3480 if s==306 else 3900
  src=Path(f'qa/stage_{rom}_{s}.png.{capture_frame:04d}.png');im=Image.open(src).convert('RGB')
  target=ev/f'{rom.upper()}_{s:04X}_f{capture_frame}.png';shutil.copy2(src,target)
  x=24+col*530
  d.text((x,y+34),name,font=small,fill='white')
  canvas.paste(im.resize((448,314),Image.Resampling.NEAREST),(x,y+56))
 a=Image.open(f'qa/stage_jp_{s}.png.{capture_frame:04d}.png').convert('RGB');b=Image.open(f'qa/stage_hf20_{s}.png.{capture_frame:04d}.png').convert('RGB')
 rows.append({'state':s,'label':label,'frame':capture_frame,'difference_bbox':ImageChops.difference(a,b).getbbox(),'pixel_identical':a.tobytes()==b.tobytes()})
canvas.save(ev/'JP_HF20_STAGE_RESULT_CONTACT.png')
for s in (306,307):
 for name in ('jp','hf20'):
  shutil.copy2(f'qa/stage_{name}_{s}.lua.json',ev/f'{name.upper()}_{s:04X}_TRACE.json')
for f in ('qa_stage_clear_probe.lua','qa_stage_exit_object.lua','qa_stage_intro_frames.lua','build_stage_clear_record.py'):
 shutil.copy2(Path('qa')/f,root/'source'/f)
sweep=[]
for m in range(18):
 p=Path(f'qa/stage_{m}_180.lua.json') if m!=5 else Path('qa/stage_05_180.lua.json')
 o=json.loads(p.read_text())['observations'];last=None;trans=[]
 for a in o:
  k=(a['state'],a['mode'])
  if k!=last:trans.append({'frame':a['f'],'state':a['state'],'mode':a['mode']});last=k
 sweep.append({'injected_mode':m,'injected_state':384,'transitions':trans})
(ev/'STATE_0180_SWEEP.json').write_text(json.dumps(sweep,indent=2)+'\n')
(ev/'STAGE_RESULT_VISUAL_QA.json').write_text(json.dumps({'pair_checks':rows,'rom_sha256':{n:hashlib.sha256(Path(p).read_bytes()).hexdigest() for n,p in [('JP','original.ws'),('HF20','hf20.ws')]},'method':'SYNTHETIC_STATE','scope':'state 0x0132/0x0133 surfaces only; no gameplay completion trigger'},indent=2)+'\n')
for name in ('exit_mode0_trace','exit_mode0_70','exit_mode0_sub1','exit_mode0_sub2','exit_mode0_sub4'):
 shutil.copy2(f'qa/{name}.lua.json',ev/f'{name.upper()}_TRACE.json')
print(ev/'JP_HF20_STAGE_RESULT_CONTACT.png')

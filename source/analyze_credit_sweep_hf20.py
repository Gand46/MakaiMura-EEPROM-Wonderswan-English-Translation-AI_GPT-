from PIL import Image,ImageDraw,ImageChops,ImageFont
from pathlib import Path
import json,hashlib
parent=Path(__file__).resolve().parent.parent
root=parent/'evidence'/'rc_gate_hf20'/'raw_credits'
if not root.exists():root=parent/'qa'
frames=list(range(600,24001,600));rows=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',12)
out=Image.new('RGB',(5*224,8*178),(24,26,30));d=ImageDraw.Draw(out)
for i,f in enumerate(frames):
 a=Image.open(root/f'credits_sweep_jp.png.{f:05d}.png').convert('RGB')
 b=Image.open(root/f'credits_sweep_hf20.png.{f:05d}.png').convert('RGB')
 assert a.size==b.size==(224,157)
 box=ImageChops.difference(a,b).getbbox()
 rows.append({'frame':f,'jp_hf20_pixel_identical':box is None,'diff_bbox':box})
 x=i%5*224;y=i//5*178
 d.text((x+3,y+2),f'f{f:05d} '+('JP=HF20' if box is None else 'DIFF'),font=font,fill='white')
 out.paste(b,(x,y+20))
out.save(root/'CREDITS_HF20_40_FRAMES_CONTACT.png')
(root/'CREDITS_HF20_40_FRAMES.json').write_text(json.dumps({'access':'SYNTHETIC_STATE 0x0133 at frame 180','pairs':rows},indent=2)+'\n')
print('frames',len(rows),'identical',sum(x['jp_hf20_pixel_identical'] for x in rows),'diff',[(x['frame'],x['diff_bbox']) for x in rows if not x['jp_hf20_pixel_identical']])

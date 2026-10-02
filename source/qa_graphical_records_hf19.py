#!/usr/bin/env python3
"""Create native JP/HF18/HF19 prompt comparisons and scoped pixel census."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,shutil,sys

BOXES=((64,56,160,72),(64,72,168,88))
FRAMES=(240,360,600,900)
ROM_SHA={'JP':'ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8',
 'HF18':'0ee826c9d1c98b3b2e02a525dd9a089a961be48e0cea5c9a2d55b8421e807c25',
 'HF19':'a924932e2aac1f3350badb3f82fe946d716a6abd1474e4cbd3bc86214227e22b'}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inside(x,y):return any(a<=x<c and b<=y<d for a,b,c,d in BOXES)

def main():
    if len(sys.argv)!=3:raise SystemExit('usage: qa_graphical_records_hf19.py QA_DIR EVIDENCE_DIR')
    src,dst=map(Path,sys.argv[1:]);dst.mkdir(parents=True,exist_ok=True)
    frames={}
    for f in FRAMES:
        ims={};names={};counts={'changed':0,'outside':0}
        for name in ('jp','hf18','hf19'):
            q=src/f'hf19_{name}_prompt.png.{f:04d}.png'
            p=dst/f'{name.upper()}_PROMPT_f{f:04d}.png'
            shutil.copy2(q,p);im=Image.open(p).convert('RGB')
            assert im.size==(224,157)
            ims[name]=im;names[name.upper()]=sha(p)
        assert ims['jp'].tobytes()==ims['hf18'].tobytes()
        for y in range(157):
            for x in range(224):
                if ims['hf18'].getpixel((x,y))!=ims['hf19'].getpixel((x,y)):
                    counts['changed']+=1
                    if not inside(x,y):counts['outside']+=1
        assert counts['changed']>0 and counts['outside']==0
        frames[str(f)]={'pixel_census':counts,'captures_sha256':names}
    sheet=Image.new('RGB',(3*224,177),(30,30,30));d=ImageDraw.Draw(sheet)
    for i,name in enumerate(('jp','hf18','hf19')):
        x=i*224;p=dst/f'{name.upper()}_PROMPT_f0900.png'
        sheet.paste(Image.open(p).convert('RGB'),(x,20))
        d.text((x+5,4),name.upper(),fill='white')
    sheet.save(dst/'JP_HF18_HF19_PROMPT_COMPARISON.png')
    report={'method':'SYNTHETIC_STATE','target':'0x0110','injected_frame':180,
      'rendered_state_at_capture':'0x0010','emulator':'Mesen 2.1.1 Linux x64',
      'native_geometry':[224,157],'rom_sha256':ROM_SHA,
      'changed_boxes_xyxy':BOXES,'frames':frames,
      'note':'Mesen screenshots are native and unscaled. The three-column image is supplemental. This is not a natural route to the confirmation.'}
    (dst/'GRAPHICAL_RECORD_HF19.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'frames':FRAMES,'outside_pixels':[frames[str(f)]['pixel_census']['outside'] for f in FRAMES]},indent=2))

if __name__=='__main__':main()

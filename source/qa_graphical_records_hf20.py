#!/usr/bin/env python3
"""Assemble and verify native Mesen captures for the Arthur book index."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import json

ROOT=Path(__file__).resolve().parent.parent
EVIDENCE=ROOT/'evidence'/'arthur_index_HF20'

def load(name):
    image=Image.open(EVIDENCE/name).convert('RGB')
    assert image.size==(224,157),(name,image.size)
    return image

def pixels(a,b):
    diff=ImageChops.difference(a,b)
    return diff.getbbox(),sum(any(v) for v in diff.get_flattened_data())

def main():
    record={'access':'SCRIPTED_NATURAL','target_state':'0x0161',
            'emulator':'Mesen 2.1.1 Linux x64','capture_geometry':[224,157],
            'bounds_convention':'left/top inclusive, right/bottom exclusive',
            'frames':[],'neighboring_states':[]}
    for frame in (840,860,880):
        jp=load(f'JP_{frame}.png');old=load(f'HF19_{frame}.png');new=load(f'HF20_{frame}.png')
        box,count=pixels(old,new)
        assert box==(32,16,80,29) and count==401
        record['frames'].append({'frame':frame,'hf19_hf20_diff_pixels':count,'bbox':box,
          'diff_pixels_outside_heading':sum(old.getpixel((x,y))!=new.getpixel((x,y))
            for y in range(157) for x in range(224) if not (32<=x<80 and 16<=y<32)),
          'jp_hf19_diff_pixels':pixels(jp,old)[1]})
    assert all(q['diff_pixels_outside_heading']==0 for q in record['frames'])
    for state in ('0160','0162','0163','0168','016B'):
        a=load(f'HF19_state_{state}.png');b=load(f'HF20_state_{state}.png')
        box,count=pixels(a,b)
        assert box is None and count==0
        record['neighboring_states'].append({'state':f'0x{state}','diff_pixels':count,
                                              'access':'SYNTHETIC_STATE'})
    titles=('JP | table of contents','HF19 | broken heading','HF20 | INDEX')
    frames=[load(f'{label}_880.png') for label in ('JP','HF19','HF20')]
    sheet=Image.new('RGB',(672,292),'#242731');draw=ImageDraw.Draw(sheet)
    for i,(im,title) in enumerate(zip(frames,titles)):
        x=i*224;sheet.paste(im,(x,24));draw.text((x+3,5),title,fill='white')
        zoom=im.crop((0,5,112,45)).resize((224,80),Image.Resampling.NEAREST)
        sheet.paste(zoom,(x,205));draw.text((x+3,184),'Native heading, 2x zoom',fill='white')
    sheet.save(EVIDENCE/'JP_HF19_HF20_ARTHUR_INDEX_COMPARISON.png')
    (EVIDENCE/'GRAPHICAL_RECORD_HF20.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()

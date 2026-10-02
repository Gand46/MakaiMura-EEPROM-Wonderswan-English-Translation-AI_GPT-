#!/usr/bin/env python3
"""Verify JP/HF20 paired captures and render native synthetic-mode contacts."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parent.parent
E=ROOT/'evidence'/'synthetic_stage_HF20'
JP_SHA='ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8'
HF20_SHA='885eb8268ad8594c1ee5e229db22b0f639da5498a22f262e0d4c0884a1401b51'

def load(name):
    im=Image.open(E/name).convert('RGB')
    assert im.size==(224,157),(name,im.size)
    return im

def changed(a,b):
    d=ImageChops.difference(a,b)
    return d.getbbox(),sum(any(p) for p in d.get_flattened_data())

def contact(label,frame):
    out=Image.new('RGB',(1344,3*184),'#242731');d=ImageDraw.Draw(out)
    for mode in range(18):
        im=load(f'{label}_mode{mode:02d}_f{frame}.png')
        x=(mode%6)*224;y=(mode//6)*184
        out.paste(im,(x,y+21))
        d.text((x+4,y+3),f'{label} | mode {mode:02X} | f{frame}',fill='white')
    out.save(E/f'{label}_MODES_f{frame}_CONTACT.png')

def story_contact(state):
    frames=(1800,2100,2500,3000)
    out=Image.new('RGB',(896,2*184),'#242731');d=ImageDraw.Draw(out)
    for row,label in enumerate(('JP','HF20')):
        for i,f in enumerate(frames):
            x=i*224;y=row*184
            out.paste(load(f'{label}_story{state:04X}_f{f}.png'),(x,y+21))
            d.text((x+4,y+3),f'{label} | {state:04X} | f{f}',fill='white')
    out.save(E/f'JP_HF20_STORY_{state:04X}_CONTACT.png')

def main():
    report={'method':['WRAM_POKE','SYNTHETIC_STATE'],
      'injection':'mode at WRAM 0x1B74 and state 0x0170 at frame3400 after scripted START/DOWN/A',
      'emulator':'Mesen 2.1.1 Linux x64','native_geometry':[224,157],
      'jp_sha256':JP_SHA,'hf20_sha256':HF20_SHA,'modes':[],
      'story_states':[],'other_high_states':[]}
    for mode in range(18):
        row={'mode':mode,'frames':[]}
        for f in (3800,4200):
            jp=load(f'JP_mode{mode:02d}_f{f}.png')
            en=load(f'HF20_mode{mode:02d}_f{f}.png')
            box,count=changed(jp,en)
            assert box is None and count==0,(mode,f,box,count)
            row['frames'].append({'frame':f,'jp_hf20_diff_pixels':count,
               'jp_png_sha256':sha256((E/f'JP_mode{mode:02d}_f{f}.png').read_bytes()).hexdigest(),
               'hf20_png_sha256':sha256((E/f'HF20_mode{mode:02d}_f{f}.png').read_bytes()).hexdigest()})
        report['modes'].append(row)
    for s in (0x380,0x3b0):
        row={'target_state':f'0x{s:04X}','access':'SYNTHETIC_STATE','frames':[]}
        for f in (900,1800,2100,2500,3000):
            jp=load(f'JP_story{s:04X}_f{f}.png')
            en=load(f'HF20_story{s:04X}_f{f}.png')
            box,count=changed(jp,en)
            assert box is not None and 60<=box[0] and box[2]<=172 and 33<=box[1] and box[3]<=112
            outside=sum(jp.getpixel((x,y))!=en.getpixel((x,y))
                for y in range(157) for x in range(224)
                if not (60<=x<172 and 33<=y<112))
            assert outside==0
            row['frames'].append({'frame':f,'jp_hf20_diff_pixels':count,
                                   'bbox':box,'outside_text_region':outside})
        report['story_states'].append(row)
    for s in (0x265,0x267,0x280,0x2b0,0x365,0x367,0x380,0x3b0):
        box,count=changed(load(f'JP_state{s:04X}_f900.png'),
                          load(f'HF20_state{s:04X}_f900.png'))
        report['other_high_states'].append({'target_state':f'0x{s:04X}',
             'access':'SYNTHETIC_STATE','frame':900,'jp_hf20_diff_pixels':count})
    for label in ('JP','HF20'):
        for f in (3800,4200):contact(label,f)
    for s in (0x380,0x3b0):story_contact(s)
    (E/'GRAPHICAL_SYNTHETIC_RECORD.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'paired_mode_screens':36,'identical_pairs':36,
       'story_frames':20,'other_high_states':8,'record':str(E/'GRAPHICAL_SYNTHETIC_RECORD.json')}))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Preserve native captures and produce a scoped visual change record.

Usage: python3 source/qa_graphical_records_hf17.py JP.png HF16.png HF17.png
       HF16_PREFIX.png HF17_PREFIX.png OUT_DIRECTORY
The two prefixes have .0240.png, .0360.png, .0600.png and .0900.png peers.
Requires Pillow only for the supplemental comparison sheet and pixel census.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,shutil,sys

BOXES={'notice':(32,40,104,104),'move':(8,170,56,192),
       'attack':(80,170,140,190),'jump':(64,190,140,209)}
FRAMES=(240,360,600,900)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def census(a,b):
    a=Image.open(a).convert('RGB');b=Image.open(b).convert('RGB')
    assert a.size==b.size==(157,224)
    counts={k:0 for k in BOXES};counts['outside']=0
    for y in range(224):
        for x in range(157):
            if a.getpixel((x,y))==b.getpixel((x,y)):continue
            key=next((k for k,(x0,y0,x1,y1) in BOXES.items()
                      if x0<=x<x1 and y0<=y<y1),'outside')
            counts[key]+=1
    return counts

def main(args):
    if len(args)!=6:raise SystemExit(__doc__)
    jp,hf16,hf17,p16,p17,dest=map(Path,args)
    dest.mkdir(parents=True,exist_ok=True)
    for name,p in [('JP_f900.png',jp),('HF16_f900.png',hf16),('HF17_f900.png',hf17)]:
        assert Image.open(p).size==(157,224)
        shutil.copy2(p,dest/name)
    sheets=Image.new('RGB',(157*3+32,252),(218,213,199))
    d=ImageDraw.Draw(sheets)
    for i,(label,p) in enumerate([('JAPANESE',jp),('HF16',hf16),('HF17',hf17)]):
        x=8+i*157
        d.text((x+2,4),label,fill=(43,43,38))
        sheets.paste(Image.open(p).convert('RGB'),(x,20))
    sheets.save(dest/'COMPARISON_NATIVE_HF17.png')
    record={'method':'SYNTHETIC_STATE','state':'0x0171','injected_frame':180,
        'capture_frame':900,'Mesen':'2.1.1',
        'Mesen_sha256':'ae43f1438282aaaff90a009aa8ada648bc5d631b070656285d7de9cbff513b41',
        'rom_sha256':{'JP':'ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8',
           'HF16':'1be7103b2c0c5c4577a89706560115196357c8b43db35b835e184a459f68b95a',
           'HF17':'90cc07da4db2909d47f131134564d3b1b796823f16f1d30200b17d9059f10715'},
        'captures_sha256':{'JP':sha(jp),'HF16':sha(hf16),'HF17':sha(hf17)},
        'JP_HF16_identical':jp.read_bytes()==hf16.read_bytes(),
        'changed_region_boxes_xyxy':BOXES,'census_by_frame':{},
        'notes':'Native 157x224 captures remain unscaled. The three-way sheet is supplementary. Natural access to state 0x0171 is not yet established.'}
    for frame in FRAMES:
        a=Path(f'{p16}.{frame:04d}.png');b=Path(f'{p17}.{frame:04d}.png')
        record['census_by_frame'][str(frame)]=census(a,b)
        assert record['census_by_frame'][str(frame)]['outside']==0
    (dest/'GRAPHICAL_RECORD_HF17.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'graphic_record':str(dest),'outside_by_frame':
        {f:v['outside'] for f,v in record['census_by_frame'].items()}},indent=2))

if __name__=='__main__':main(sys.argv[1:])

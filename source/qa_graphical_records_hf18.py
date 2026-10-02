#!/usr/bin/env python3
"""Record all 25 native ending steps and create a three-way comparison sheet.

Usage: python3 source/qa_graphical_records_hf18.py CAPTURE_DIRECTORY OUT_DIRECTORY
CAPTURE_DIRECTORY contains jp.png.line00.png ... hf18.png.line24.png.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, shutil, sys

ROM_SHA = {'JP':'ac0c793b30d2de19ff6504d5a205e33f42aeeac724e7c284b48f48fbfbe53ed8',
           'HF17':'90cc07da4db2909d47f131134564d3b1b796823f16f1d30200b17d9059f10715',
           'HF18':'0ee826c9d1c98b3b2e02a525dd9a089a961be48e0cea5c9a2d55b8421e807c25'}

def main():
    if len(sys.argv)!=3: raise SystemExit(__doc__)
    src,dst=map(Path,sys.argv[1:]);dst.mkdir(parents=True,exist_ok=True)
    records=[]
    for i in range(25):
        files={}
        ims={}
        for name in ('jp','hf17','hf18'):
            q=src/f'{name}.png.line{i:02}.png';p=dst/f'{name.upper()}_ENDING_LINE{i:02}.png'
            shutil.copy2(q,p)
            im=Image.open(p).convert('RGB')
            assert im.size==(224,157)
            files[name.upper()]=hashlib.sha256(p.read_bytes()).hexdigest()
            ims[name]=im
        changed=outside=0
        for y in range(157):
            for x in range(224):
                if ims['hf17'].getpixel((x,y)) != ims['hf18'].getpixel((x,y)):
                    changed+=1
                    if not (108<=x<212):outside+=1
        assert outside==0, (i,outside)
        records.append({'line':i,'native_geometry':[224,157],
                        'changed_pixels_from_hf17':changed,
                        'outside_text_column':outside,'captures_sha256':files})
    sheet=Image.new('RGB',(3*224,5*177),(32,32,32))
    draw=ImageDraw.Draw(sheet)
    for row,i in enumerate((16,18,19,23,24)):
        for col,name in enumerate(('jp','hf17','hf18')):
            x,y=224*col,177*row
            draw.text((x+5,y+4),f'{name.upper()} LINE {i:02}',fill='white')
            sheet.paste(Image.open(dst/f'{name.upper()}_ENDING_LINE{i:02}.png').convert('RGB'),(x,y+20))
    sheet.save(dst/'JP_HF17_HF18_ENDING_COMPARISON.png')
    report={'method':'SYNTHETIC_STATE','injected_state':'0x0134','injected_frame':180,
        'emulator':'Mesen 2.1.1 Linux x64','rom_sha256':ROM_SHA,
        'comparison_region_xy':'108<=x<212, 0<=y<157',
        'note':'Individual native captures are 224x157, with no rescaling; the sheet is supplemental. This does not demonstrate natural progression.',
        'lines':records}
    (dst/'GRAPHICAL_RECORD_HF18.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'captured_lines':len(records),
        'changed_lines':[r['line'] for r in records if r['changed_pixels_from_hf17']],
        'outside_text_column':sum(r['outside_text_column'] for r in records)},indent=2))

if __name__=='__main__':main()

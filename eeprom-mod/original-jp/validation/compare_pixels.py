#!/usr/bin/env python3
"""Compare actual decoded Mesen screenshots, excluding only bottom status bar."""
from pathlib import Path
from PIL import Image
import argparse,json
ap=argparse.ArgumentParser();ap.add_argument('results',type=Path);a=ap.parse_args();R=a.results
rows=[]
def compare(p,q,label):
    def load(f):
        im=Image.open(f).convert('RGB');im.load()
        if im.size not in ((224,144),(224,157)):raise ValueError('Unexpected dimensions '+str(im.size))
        return im.crop((0,0,224,144))
    x,y=load(p),load(q);n=sum(i!=j for i,j in zip(x.getdata(),y.getdata()))
    rows.append({'test':label,'different_pixels':n,'pixels':32256})
for n in (3680,3730,3810,3860,3910,3950,3990,4030):compare(R/f'original_controls/frame{n}.png',R/f'final_controls/frame{n}.png',f'options {n}')
compare(R/'final_modal/exit_normal.png',R/'final_modal/cancel_restored.png','cancel restores native menu')
for n in (3755,3800,3850):compare(R/f'original_tip10/frame{n}.png',R/f'final_tip10/frame{n}.png',f'tip10 {n}')
(R/'pixel_comparison.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
raise SystemExit(0 if all(r['different_pixels']==0 for r in rows) else 2)

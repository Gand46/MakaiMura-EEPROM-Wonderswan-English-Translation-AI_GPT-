#!/usr/bin/env python3
"""Assert runtime results, full native game image comparisons and cold-save bytes."""
from pathlib import Path
import argparse,json,hashlib
from PIL import Image,ImageChops
def check(root,seed_path):
    cases=[]
    for p in sorted(root.glob('*/run.json')):
        r=json.loads(p.read_text());assert r['code']==0 and not r['timed_out'],str(p);cases.append({'name':p.parent.name,**r})
    assert len(cases)==55,'Incomplete runtime set'
    comparisons=[]
    def pair(a,b):
        aa=Image.open(a).convert('RGB');bb=Image.open(b).convert('RGB');assert aa.size==bb.size
        assert aa.size in ((224,157),(157,224))
        box=(0,0,224,144) if aa.size==(224,157) else (0,0,144,224)
        assert ImageChops.difference(aa.crop(box),bb.crop(box)).getbbox() is None,str(a)
        comparisons.append({'candidate':str(a.relative_to(root)),'reference':str(b.relative_to(root)),'native_frame_size':aa.size,'game_box':box,'changed_pixels':0})
    for folder in sorted(root.glob('*_combined')):
        baseline=root/(folder.name[:-9]+'_hf20');assert baseline.is_dir()
        for a in sorted(folder.glob('*.png')):
            if a.name!='capture.png':pair(a,baseline/a.name)
    for a in sorted((root/'controls').glob('frame*.png')):pair(a,root/'hf20_controls'/a.name)
    pair(root/'modal/cancel_restored.png',root/'modal/exit_normal.png')
    for f in [500,700,1400]:pair(root/f'actual_continue_checkpoint/cold{f}.png',root/f'actual_continue_hf20/cold{f}.png')
    a=Image.open(root/'actual_continue_checkpoint/cold1700.png').convert('RGB').crop((0,0,224,144));b=Image.open(root/'actual_continue_hf20/cold1700.png').convert('RGB').crop((0,0,224,144))
    pause_bbox=ImageChops.difference(a,b).getbbox();assert pause_bbox==(92,120,132,128)
    for n in ['actual_continue_checkpoint','actual_continue_hf20']:assert (root/n/'continue.tsv').read_text().strip()=='state=0080 mode=0 pause=2'
    cold=[]
    for boot,origin in [('cold_saved','save'),('cold_erased','modal'),('cold_legacy','legacy_saved'),('cold_fresh_save','fresh_first_save'),('cold_late','late_save'),('cold_checkpoint','checkpoint_save')]:
        a=(root/boot/'mirror_645.bin').read_bytes();b=(root/origin/'after.eeprom').read_bytes();assert len(b)==2048 and a==b[:645],boot
        assert (root/boot/'result.tsv').read_text().strip()=='writes=0\tdiff=0'
        cold.append({'boot':boot,'origin':origin,'native_bytes_equal':645,'eeprom_sha256':hashlib.sha256(b).hexdigest()})
    seed=seed_path.read_bytes();assert len(seed)==2048
    assert (root/'modal/cancel.eeprom').read_bytes()==seed
    assert (root/'modal/erased.eeprom').read_bytes()[645:]==seed[645:]
    for n in ['controls','pause_tips','exit']:assert (root/n/'after.eeprom').read_bytes()==seed,n
    assert (root/'fresh_first_save/after.eeprom').read_bytes()[646:]==bytes([255])*(2048-646)
    r={'runtime_cases':len(cases),'runtime_failed':0,'pixel_comparisons':len(comparisons),'pixel_differences':0,'intentional_pause_difference_bbox':pause_bbox,'cold_roundtrips':cold,'comparisons':comparisons,'cases':cases}
    (root/'VALIDATION_SUMMARY.json').write_text(json.dumps(r,indent=2)+'\n')
    return {k:v for k,v in r.items() if k not in ('comparisons','cases')}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--seed',type=Path,required=True);a=p.parse_args();print(json.dumps(check(a.root,a.seed),indent=2))

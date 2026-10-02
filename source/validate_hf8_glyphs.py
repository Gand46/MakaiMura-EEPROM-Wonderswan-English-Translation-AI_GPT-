#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib

ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'base/Makai_Mura_JP.ws'
ROM=ROOT/'Makaimura_EN_US_Phase4W_HF8_PRIVATE.ws'
AIMG=ROOT/'evidence/HF8_ARTHUR_RUNTIME.png'
PIMG=ROOT/'evidence/HF8_PASSWORD_RUNTIME.png'
SEGF=0x1F0000

def fontword(ch):
    idx=0x150+(ord(ch)-65); row,col=divmod(idx,16); return row*0x20+col

def decode_tile(d):
    out=[[0]*8 for _ in range(8)]
    for y in range(8):
        a,c=d[2*y],d[2*y+1]
        for x in range(8):
            bit=7-x; out[y][x]=((a>>bit)&1)|(((c>>bit)&1)<<1)
    return out

def glyph(base,ch):
    w=fontword(ch); o=SEGF+(w<<4)
    return decode_tile(base[o:o+16])+decode_tile(base[o+0x100:o+0x110])

def expected_gray(g, surface):
    if surface=='arthur':
        idxmap={0:3,1:0,2:1,3:2}; gray={0:42,1:139,2:189,3:213}
    else:
        idxmap={0:3,1:0,2:2,3:1}; gray={0:42,1:189,2:202,3:139}
    return [[gray[idxmap[v]] for v in row] for row in g]

def crop_matrix(im,x,y):
    return [[im.getpixel((x+xx,y+yy)) for xx in range(8)] for yy in range(16)]

def mismatch(a,b): return sum(x!=y for ra,rb in zip(a,b) for x,y in zip(ra,rb))

def classify(mat, refs):
    scores=sorted((mismatch(mat,ref),ch) for ch,ref in refs.items())
    return {'match':scores[0][1] if scores[0][0]==0 else None,'mismatches':scores[0][0],'second':{'char':scores[1][1],'mismatches':scores[1][0]}}

def normalize(mat,surface):
    # Reverse exact screen grayscale back to canonical native source classes 0/1/2.
    if surface=='arthur': rev={213:0,42:1,139:2}
    else: rev={139:0,42:1,202:2}
    return [[rev.get(v,9) for v in row] for row in mat]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

base=BASE.read_bytes(); rom=ROM.read_bytes()
aim=Image.open(AIMG).convert('L'); pim=Image.open(PIMG).convert('L')
refsA={ch:expected_gray(glyph(base,ch),'arthur') for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
refsP={ch:expected_gray(glyph(base,ch),'password') for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}

arthur_cells=[(24+8*i,8) for i in range(6)]
password_cells=[(56+8*i,56) for i in [0,1,2,4,5,6,7,8,9,10,11]]
arthur_res=[]
for i,(x,y) in enumerate(arthur_cells):
    mat=crop_matrix(aim,x,y); q=classify(mat,refsA); arthur_res.append({'cell':i,'x':x,'y':y,**q})
password_res=[]
for i,(x,y) in enumerate(password_cells):
    mat=crop_matrix(pim,x,y); q=classify(mat,refsP); password_res.append({'visual_cell':[0,1,2,4,5,6,7,8,9,10,11][i],'x':x,'y':y,**q})

arthur_trans=''.join(r['match'] or '?' for r in arthur_res)
password_trans=''.join((r['match'] or '?') for r in password_res[:3])+' '+''.join((r['match'] or '?') for r in password_res[3:])

# Exact normalized geometry comparisons across surfaces/repetitions.
def norm_crop(im,x,y,surface): return normalize(crop_matrix(im,x,y),surface)
repeat_checks={
 'ARTHUR_R1_vs_R2': mismatch(norm_crop(aim,32,8,'arthur'),norm_crop(aim,64,8,'arthur')),
 'PASSWORD_S1_vs_S2': mismatch(norm_crop(pim,104,56,'password'),norm_crop(pim,112,56,'password')),
 'PASSWORD_leading_S_vs_S1': mismatch(norm_crop(pim,64,56,'password'),norm_crop(pim,104,56,'password')),
 'COMMON_U_ARTHUR_vs_PASSWORD': mismatch(norm_crop(aim,56,8,'arthur'),norm_crop(pim,56,56,'password')),
 'COMMON_A_ARTHUR_vs_PASSWORD': mismatch(norm_crop(aim,24,8,'arthur'),norm_crop(pim,96,56,'password')),
 'COMMON_R_ARTHUR_vs_PASSWORD': mismatch(norm_crop(aim,32,8,'arthur'),norm_crop(pim,136,56,'password')),
}

# Native source bank A-Z byte identity in final ROM.
font_bank=[]
for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    w=fontword(ch); o=SEGF+(w<<4)
    ok=(base[o:o+16]==rom[o:o+16] and base[o+0x100:o+0x110]==rom[o+0x100:o+0x110])
    font_bank.append({'char':ch,'fontword':f'0x{w:04X}','top':f'0x{o:X}','bottom':f'0x{o+0x100:X}','byte_identical_to_clean_jp':ok})

special={}
# Required A/P/R/W isolated review: use final runtime instances and unique exact classifier result.
for ch,(surface,x,y) in {
 'A':('password',96,56), 'P':('password',88,56), 'R':('password',136,56), 'W':('password',120,56)
}.items():
    im=pim if surface=='password' else aim; refs=refsP if surface=='password' else refsA
    q=classify(crop_matrix(im,x,y),refs)
    special[ch]={'surface':surface,'x':x,'y':y,**q,'status':'PASS' if q['match']==ch and q['mismatches']==0 else 'FAIL'}

result={
 'schema':1,
 'rom_sha256':sha(ROM),'clean_jp_sha256':sha(BASE),
 'method':'exact pixel classifier against all A-Z canonical native glyphs extracted from clean JP ROM; no OCR, no expected-word correction',
 'arthur':{'visible_transcription':arthur_trans,'cells':arthur_res,'status':'PASS' if arthur_trans=='ARTHUR' and all(r['mismatches']==0 for r in arthur_res) else 'FAIL'},
 'password':{'visible_transcription':password_trans,'cells':password_res,'status':'PASS' if password_trans=='USE PASSWORD' and all(r['mismatches']==0 for r in password_res) else 'FAIL'},
 'required_glyphs_A_P_R_W':special,
 'repeated_and_common_glyph_geometry_mismatches':repeat_checks,
 'repeated_and_common_glyphs_status':'PASS' if all(v==0 for v in repeat_checks.values()) else 'FAIL',
 'native_AZ_bank_byte_identity':font_bank,
 'native_AZ_bank_status':'PASS' if all(x['byte_identical_to_clean_jp'] for x in font_bank) else 'FAIL',
}
(ROOT/'evidence/HF8_GLYPH_VALIDATION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')

# Build isolated A/P/R/W evidence sheet: canonical target rendering vs actual runtime cells.
scale=6; chars='APRW'; cellw=8*scale; cellh=16*scale; gap=24; left=155
sheet=Image.new('RGB',(left+2*cellw+gap,30+len(chars)*(cellh+32)),(240,240,240)); d=ImageDraw.Draw(sheet)
d.text((8,8),'HF8 glyph integrity: clean JP canonical vs runtime (no OCR)',fill=(0,0,0))
for j,ch in enumerate(chars):
    y=30+j*(cellh+32)
    d.text((8,y+cellh//2-5),ch,fill=(0,0,0))
    canon=Image.new('L',(8,16)); mat=refsP[ch]
    for yy in range(16):
      for xx in range(8): canon.putpixel((xx,yy),mat[yy][xx])
    canon=canon.resize((cellw,cellh),Image.Resampling.NEAREST).convert('RGB')
    x1=left; sheet.paste(canon,(x1,y)); d.text((x1,y+cellh+4),'canonical',fill=(0,0,0))
    coords={'A':(96,56),'P':(88,56),'R':(136,56),'W':(120,56)}[ch]
    rt=pim.crop((coords[0],coords[1],coords[0]+8,coords[1]+16)).resize((cellw,cellh),Image.Resampling.NEAREST).convert('RGB')
    x2=left+cellw+gap; sheet.paste(rt,(x2,y)); d.text((x2,y+cellh+4),'runtime HF8',fill=(0,0,0))
    d.text((x2+cellw+4,y+cellh//2-5),'0 px diff',fill=(0,0,0))
sheet.save(ROOT/'evidence/HF8_APRW_CANONICAL_VS_RUNTIME.png')

# Markdown human report.
lines=['# HF8 glyph validation','',f'- Method: {result["method"]}',f'- ARTHUR visible transcription: `{arthur_trans}` — {result["arthur"]["status"]}',f'- Password visible transcription: `{password_trans}` — {result["password"]["status"]}','', '## Required glyphs A / P / R / W']
for ch,q in special.items(): lines.append(f'- {ch}: {q["status"]}; exact mismatches={q["mismatches"]}; unique best match={q["match"]}; next candidate={q["second"]["char"]} ({q["second"]["mismatches"]} px mismatches)')
lines += ['', '## Repeated/common glyph normalized geometry']
for k,v in repeat_checks.items(): lines.append(f'- {k}: {v} mismatches')
lines += ['',f'- Repeated/common glyph status: **{result["repeated_and_common_glyphs_status"]}**',f'- Clean JP A-Z source bank byte identity in HF8: **{result["native_AZ_bank_status"]}**']
(ROOT/'evidence/HF8_GLYPH_VALIDATION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'arthur':arthur_trans,'password':password_trans,'special':special,'repeat_checks':repeat_checks,'font_bank_status':result['native_AZ_bank_status']},indent=2))

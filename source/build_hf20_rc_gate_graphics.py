from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys,json,hashlib,shutil
ROOT=Path(__file__).resolve().parent.parent
PACK=ROOT if (ROOT/'source'/'build_phase4w_hf20.py').exists() else ROOT/'Makaimura_PHASE4W_HF20_RC_GATE_AUDIT_2026-09-28'
E=PACK/'evidence'/'rc_gate_hf20';E.mkdir(parents=True,exist_ok=True)
M=E/'raw_states' if (E/'raw_states').exists() else ROOT/'qa'/'state_matrix_hf20'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',13)
states=[0x110,0x131,0x132,0x134,0x160,0x161,0x162,0x164,0x166,0x169,0x380,0x3b0]
labels=['erase prompt','continue','stage selector','ending text','book cover','demon index','entry detail','Arthur stats','game details','item detail','dialogue A','dialogue B']
sheet=Image.new('RGB',(4*224,3*183),(23,24,29));d=ImageDraw.Draw(sheet)
for i,(state,label) in enumerate(zip(states,labels)):
 x=i%4*224;y=i//4*183
 d.text((x+3,y+2),f'{state:04X} {label}',font=font,fill='white')
 if state in (0x380,0x3b0):
  source=PACK/'evidence'/'synthetic_stage_HF20'/f'HF20_story{state:04X}_f1800.png'
 else:source=M/f'hf20_{state:04x}.png.0900.png'
 im=Image.open(source).convert('RGB')
 assert im.size==(224,157)
 sheet.paste(im,(x,y+23))
sheet.save(E/'HF20_12_SURFACES_CONTACT.png')
credit_source=E/'raw_credits' if (E/'raw_credits').exists() else ROOT/'qa'
shutil.copy2(credit_source/'CREDITS_HF20_40_FRAMES_CONTACT.png',E/'JP_HF20_CREDITS_40_FRAMES.png')
shutil.copy2(credit_source/'CREDITS_HF20_40_FRAMES.json',E/'CREDITS_40_FRAME_COMPARISON.json')
shutil.copy2(M/'audit.json',E/'STATE_MATRIX_30_STATES.json')
if (ROOT/'qa'/'ACTIVE_E000_HF20_CENSUS.json').exists():shutil.copy2(ROOT/'qa'/'ACTIVE_E000_HF20_CENSUS.json',E/'ACTIVE_E000_HF20_CENSUS.json')
if (ROOT/'qa'/'atlas_e000_0252.png').exists():shutil.copy2(ROOT/'qa'/'atlas_e000_0252.png',E/'CREDITS_LATIN_ATLAS_DIAGNOSTIC.png')
if (ROOT/'qa'/'atlas_e000_01de.png').exists():shutil.copy2(ROOT/'qa'/'atlas_e000_01de.png',E/'CAST_MIXED_ATLAS_DIAGNOSTIC.png')
for name in ('scan_sjis_hf20.py','render_e000_table.py','run_hf20_state_matrix.py','analyze_hf20_state_matrix.py','qa_credit_sweep_hf20.lua','analyze_credit_sweep_hf20.py','audit_active_e000_hf20.py','build_hf20_rc_gate_graphics.py'):
 src=ROOT/'qa'/name
 if src.exists() and src!=PACK/'source'/name:shutil.copy2(src,PACK/'source'/name)
# Native 8x16 font tiles and exact byte continuity for key glyphs.
sys.path.insert(0,str(PACK/'source'))
from phase2_builder import glyph_8x16
from build_phase4w_hf2 import decode_tile,fontword
jp=(ROOT/'original.ws').read_bytes();hf=(ROOT/'hf20.ws').read_bytes()
letters='APRW';record=[]
fig=Image.new('RGB',(4*120,130),'#202329');draw=ImageDraw.Draw(fig)
for i,c in enumerate(letters):
 a=glyph_8x16(jp,c);b=glyph_8x16(hf,c)
 assert a==b and len(a)==32
 record.append({'glyph':c,'font_word':fontword(c),'jp_hf20_identical':True,'sha256':hashlib.sha256(b).hexdigest()})
 x=i*120;draw.text((x+14,4),f'{c}  native',font=font,fill='white')
 top=decode_tile(b[:16]);bot=decode_tile(b[16:]);p=top+bot
 for y,row in enumerate(p):
  for xx,v in enumerate(row):draw.rectangle((x+32+xx*5,32+y*5,x+36+xx*5,36+y*5),fill=['#999','#222','#ccc','#eee'][v])
fig.save(E/'NATIVE_APRW_GLYPHS.png')
(E/'NATIVE_APRW_GLYPHS.json').write_text(json.dumps(record,indent=2)+'\n')
print('created',E)

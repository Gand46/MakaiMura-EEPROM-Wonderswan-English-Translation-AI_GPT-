"""Structure and glyph references for five E000 tables; not a whole-ROM census."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
if len(sys.argv)!=2:raise SystemExit('usage: python3 audit_active_e000_hf20.py PRIVATE_HF20.ws')
ROM=Path(sys.argv[1]).read_bytes();E=0x1e0000
src=Path(__file__).resolve().parent
if not (src/'build_phase4w_hf12.py').exists():
 src=ROOT/'Makaimura_PHASE4W_HF20_RC_GATE_AUDIT_2026-09-28'/'source'
sys.path.insert(0,str(src))
from build_phase4w_hf12 import LINES as STORY0
from build_phase4w_hf13 import LINES_1 as STORY1
from build_phase4w_hf18 import LINES_18 as STORY2
from build_phase4w_hf14 import FIRST_GLYPHS,MEASURE_GLYPHS,FIRST_NAMES
CASES=[
 ('rescue',0xcd80,23,0,0x14594c,STORY0),
 ('alternate_rescue',0xcf80,15,1,0x145b4b,STORY1),
 ('ending_narration',0xd180,25,2,0x145f30,STORY2),
 ('cast_cards',0x0579,13,3,0x1460a8,None),
 ('staff_credits',0x06f5,165,4,0x146729,None),
]
def w(p):return int.from_bytes(ROM[E+p:E+p+2],'little')
results=[]
for name,table,n,bank,consumer,expected in CASES:
 assert ROM[consumer:consumer+3]==b'\xbe'+table.to_bytes(2,'little')
 atlas=w(bank*2);count=w(atlas)
 words=[w(atlas+2+i*2) for i in range(count)]
 pointers=[w(table+1+i*2) for i in range(n)]
 assert pointers==sorted(pointers) and all(0<=p<0x10000 for p in pointers)
 rows=[];used=set()
 for i,p in enumerate(pointers):
  end=ROM.index(b'\xff',E+p)-E
  assert end-p<64,(name,i,end-p)
  data=ROM[E+p:E+end]
  assert all(x<count or x==0xfe for x in data)
  used.update(x for x in data if x!=0xfe)
  if bank<3:
   decoded=''.join('ABCDEFGHIJKLMNOPQRSTUVWXYZ .?'[v] for v in data)
   assert decoded==expected[i],(name,i,decoded,expected[i])
  elif bank==3:
   parts=data.split(b'\xfe')
   assert len(parts)==(2 if i==11 else 1) # Cast transliteration removed; optional measurements.
   decoded=''.join(FIRST_GLYPHS[v] for v in parts[0]).strip()
   assert decoded==FIRST_NAMES[i]
   if len(parts)==2:
    measure=''.join(MEASURE_GLYPHS[v] for v in parts[1]).strip()
    assert i==11 and measure=='B88 W58 H90'
  else:decoded=None # Rendered Latin atlas classification remains visual evidence.
  rows.append({'index':i,'pointer':f'E000:{p:04X}','token_count':len(data),'text':decoded})
 if bank==3:assert used<=set(FIRST_GLYPHS)|set(MEASURE_GLYPHS)
 results.append({'family':name,'bank':bank,'atlas':f'E000:{atlas:04X}','glyph_count':count,
  'consumer':f'ROM:{consumer:06X}','table':f'E000:{table:04X}',
  'entries':n,'used_token_codes':sorted(used),'all_tokens_in_atlas':True,
  'decoded_exact_source':bank<3,'latin_only_active_cast_codes':bank==3,'rows':rows})
assert sum(x['entries'] for x in results)==241
out={'scope':'five known active E000 atlas/table/consumer families; no claim about other graphic or script sources',
 'hf20_sha256':hashlib.sha256(ROM).hexdigest(),'families':results,'entries_total':241,
 'source_japanese_token_count_in_verified_english_tables':0,
 'caveat':'bank 4 was inspected visually as Latin in the diagnostic atlas; no glyph-level semantic transcription of all 165 credit rows'}
dest=ROOT/'evidence'/'rc_gate_hf20' if (ROOT/'source').exists() else ROOT/'qa'
dest.mkdir(parents=True,exist_ok=True)
(dest/'ACTIVE_E000_HF20_CENSUS.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({x['family']:x['entries'] for x in results},indent=2))

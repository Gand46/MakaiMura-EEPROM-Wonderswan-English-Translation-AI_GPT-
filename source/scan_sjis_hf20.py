from pathlib import Path
import re,json
rom=Path('hf20.ws').read_bytes();orig=Path('original.ws').read_bytes()
# Maximal runs of two-byte Shift-JIS (including punctuation), optional ASCII spaces.
def scan(b):
 out=[];i=0
 while i<len(b)-1:
  start=i; chars=[]; kana=0
  while i<len(b)-1:
   x,y=b[i],b[i+1]
   if (0x81<=x<=0x9f or 0xe0<=x<=0xfc) and (0x40<=y<=0x7e or 0x80<=y<=0xfc):
    try:c=b[i:i+2].decode('cp932')
    except UnicodeDecodeError:break
    chars.append(c);kana+=bool(re.match(r'[\u3040-\u30ff\u4e00-\u9fff]',c));i+=2
   else:break
  if len(chars)>=4 and kana>=3:
   out.append({'offset':start,'length':i-start,'characters':len(chars),'japanese':kana,'text':''.join(chars)})
  if i==start:i+=1
 return out
x=scan(rom);y=scan(orig)
for z in x:z['unchanged_from_jp']=rom[z['offset']:z['offset']+z['length']]==orig[z['offset']:z['offset']+z['length']]
Path('qa/sjis_candidates_hf20.json').write_text(json.dumps({'method':'consecutive strict CP932 double bytes, >=4 chars >=3 Japanese chars; candidates, not confirmed text','hf20':x,'jp_count':len(y)},ensure_ascii=False,indent=2)+'\n')
print('HF20',len(x),'JP',len(y));print('\n'.join(f'{v["offset"]:06x} {v["text"][:70]} ' for v in sorted(x,key=lambda q:-q['characters'])[:45]))

from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
b=Path('hf20.ws').read_bytes();root=0x1e0000
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',14)
def dec_tile(o):
 p=[]
 for y in range(8):
  a,c=b[o+y*2:o+y*2+2]
  p.append([((a>>(7-x))&1)|(((c>>(7-x))&1)<<1) for x in range(8)])
 return p
def glyph(word):
 p=dec_tile(0x1f0000+word*16);q=dec_tile(0x1f0000+word*16+0x100)
 return p+q
for atlas in (0x1de,0x252):
 n=int.from_bytes(b[root+atlas:root+atlas+2],'little')
 words=[int.from_bytes(b[root+atlas+2+i*2:root+atlas+4+i*2],'little') for i in range(n)]
 cols=10;img=Image.new('RGB',(cols*74,((n+cols-1)//cols)*105),'#202020');d=ImageDraw.Draw(img)
 for i,w in enumerate(words):
  xx=(i%cols)*74;yy=(i//cols)*105
  for y,row in enumerate(glyph(w)):
   for x,v in enumerate(row):
    color=['#888888','#242424','#bbbbbb','#eeeeee'][v]
    d.rectangle((xx+20+x*4,yy+26+y*4,xx+23+x*4,yy+29+y*4),fill=color)
  d.text((xx+3,yy+3),f'{i:02x}:{w:03x}',font=font,fill='yellow')
 img.save(f'qa/atlas_e000_{atlas:04x}.png')
 print('atlas',hex(atlas),'count',n)
# pointer table at 0x06F4 until first line
start=0x6f4;n=(0x840-start-1)//2
pts=[int.from_bytes(b[root+start+1+2*i:root+start+3+2*i],'little') for i in range(n)]
print('pointers',len(pts),[hex(v) for v in pts[:12]],'end',hex(pts[-1]))
for i,p in enumerate(pts[:28]):
 if p<0x840 or p>=0x10000:continue
 end=b.find(b'\xff',root+p)
 print(i,hex(p),b[root+p:end].hex(' '))

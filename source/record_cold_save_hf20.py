from PIL import Image,ImageDraw,ImageFont,ImageChops
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parent.parent
P=R/'Makaimura_PHASE4W_HF20_RC_GATE_AUDIT_2026-09-28'/'evidence'/'rc_gate_hf20'
imgs=[('Initial, new save',R/'qa'/'cold_initial_arthur.png'),('Game Over, three deaths',R/'qa'/'cold_gameover.png'),('After cold relaunch',R/'qa'/'cold_after_arthur.png')]
sheet=Image.new('RGB',(672,190),'#1a1c22');d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for i,(title,path) in enumerate(imgs):
 im=Image.open(path).convert('RGB');assert im.size==(224,157)
 x=i*224;sheet.paste(im,(x,26));d.text((x+3,4),title,font=font,fill='white')
 shutil.copy2(path,P/f'COLD_{i}_{path.name}')
sheet.save(P/'COLD_SAVE_HF20_RECORD.png')
a=Image.open(imgs[0][1]).convert('RGB');b=Image.open(imgs[2][1]).convert('RGB')
save=R/'mesen-2.1.1'/'Saves'/'cold_probe_hf20.sav';eeprom=save.with_suffix('.ieeprom')
shutil.copy2(save,P/'cold_probe_hf20.sav');shutil.copy2(eeprom,P/'cold_probe_hf20.ieeprom')
record={'method':'two Mesen processes separated by exit and new launch; scripted natural UI',
 'private_test_rom_sha256':hashlib.sha256((R/'qa'/'cold_probe_hf20.ws').read_bytes()).hexdigest(),
 'initial_deaths':'000000','after_cold_relaunch_deaths':'000003',
 'gameover_state_at_frame_9600':'0x0035','difference_bbox_initial_vs_after':ImageChops.difference(a,b).getbbox(),
 'save_sha256':hashlib.sha256(save.read_bytes()).hexdigest(),
 'ieeprom_sha256':hashlib.sha256(eeprom.read_bytes()).hexdigest(),
 'scope':'cold persistence of Arthur death counter through game-generated .sav; other save flags not exhaustively tested'}
(P/'COLD_SAVE_RECORD.json').write_text(json.dumps(record,indent=2)+'\n')
print(record)

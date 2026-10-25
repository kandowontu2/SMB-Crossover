from pathlib import Path
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;O=D/'ryu-head-oversized-mmc3-v11/zelda-pause-v1/build/verification';sheet=Image.new('RGB',(1536,1540),(21,27,40));draw=ImageDraw.Draw(sheet)
for i,name in enumerate(('upgrades','spells','life-selected','life-upgrade','magic-upgrade','attack-upgrade')):
 p=O/(name+'.rgba');im=Image.frombytes('RGBA',(256,240),p.read_bytes(),'raw','BGRA').convert('RGB').resize((768,720),Image.Resampling.NEAREST);x=(i%2)*768;y=(i//2)*512
 im=im.resize((512,480),Image.Resampling.NEAREST);sheet.paste(im,(x,y+25));draw.text((x+8,y+8),name,fill='white')
sheet=sheet.crop((0,0,1280,1536));sheet.save(O/'panel-review.png')

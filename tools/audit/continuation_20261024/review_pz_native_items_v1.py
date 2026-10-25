from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
Q=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-head-pz');O=Q/'items-visual-v1';O.mkdir(exist_ok=False)
proof=json.loads((Q/'items-v1/proof.json').read_text());selected=[]
for case in proof['runs']:
 folder=Q/'items-v1'/case['name'];receipt=folder/'native-items-result.json'
 if not receipt.exists():continue
 data=json.loads(receipt.read_text())['items'];frames=[data[i] for i in sorted(set([0,len(data)//2,len(data)-1]))]
 selected.append((case['name'],folder,frames))
records=[]
for n in range(0,len(selected),2):
 sheet=Image.new('RGB',(1536,1040),(21,27,40));draw=ImageDraw.Draw(sheet)
 rows=[]
 for y,(name,folder,frames) in enumerate(selected[n:n+2]):
  for x,item in enumerate(frames):
   f=folder/'frames'/f'{item["mature"]:06d}.png';im=Image.open(f).convert('RGB').resize((512,480),Image.Resampling.NEAREST)
   sheet.paste(im,(x*512,y*520+34));draw.text((x*512+8,y*520+10),f'{name} / item {item["id"]} / frame {item["mature"]}',fill='white')
   rows.append(dict(case=name,item=item['id'],frame=item['mature'],path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 dest=O/f'items-{n//2+1:02d}.png';sheet.save(dest);records.append(dict(path=str(dest),frames=rows))
(O/'index.json').write_text(json.dumps(records,indent=2));print(json.dumps(dict(sheets=len(records),cases=len(selected),folder=str(O))))

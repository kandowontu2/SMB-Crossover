"""Lay out native selection and lives captures for a roster-wide visual review."""
from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
cases=list(json.loads((a.input/'results.json').read_text())['results'])
assert len(cases)==32
for start in range(0,32,8):
 page=Image.new('RGB',(2048,608),(32,32,40));d=ImageDraw.Draw(page)
 for i,name in enumerate(cases[start:start+8]):
  folder=a.input/name.lower().replace(' ','-')/'build/verification'
  for file in('selection.png','lives.png'):assert(folder/file).exists(),(name,file)
  x=i%4*512;y=i//4*304
  page.paste(Image.open(folder/'selection.png').crop((0,136,256,214)).resize((512,156),Image.Resampling.NEAREST),(x,y))
  page.paste(Image.open(folder/'lives.png').crop((64,80,192,140)).resize((256,120),Image.Resampling.NEAREST),(x+128,y+176))
  d.text((x+8,y+160),name,fill='white')
 page.save(a.output/f'previews-{start//8+1}.png')
print('32 highlighted previews and32 lives cards prepared from native screenshots')

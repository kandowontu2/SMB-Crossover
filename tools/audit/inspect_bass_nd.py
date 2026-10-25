"""Read-only comparison of Bass source body and separately animated arm."""
from pathlib import Path
import json,sys,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import build_expanded_assets as a
from prepare_crossover import frames
from build_special_art import extract
out=R/'build/verification/new-roster-1-1-nd/bass-source';out.mkdir(exist_ok=True)
items=list(ET.parse(R/'reference/crossover2/main.xml').getroot().iter('item'));symbols={}
for tag in items:
 if tag.get('type')in('SymbolClassTag','ExportAssetsTag')and tag.find('tags')is not None:
  symbols.update({n.text:i.text for i,n in zip(tag.find('tags'),tag.find('names'))})
sprites={i.get('spriteId'):i for i in items if i.get('type')=='DefineSpriteTag'}
timeline=frames(sprites[symbols['MegaMan']])[:17];armtimeline=frames(sprites[symbols['MegaManArm']])
sheet=a.sheet('BASS');bodies=extract(timeline,24,sheet);arms=extract(armtimeline,24,sheet)
report={'body':[],'arm':[]}
page=Image.new('RGBA',(8*192,((len(timeline)+7)//8)*224),(70,100,160,255));d=ImageDraw.Draw(page)
for i,(f,pic)in enumerate(zip(timeline,bodies)):
 arm=next((v for v in f['display'].values()if v.get('characterId')==symbols['MegaManArm']),None)
 report['body'].append(dict(frame=i+1,labels=f['labels'],bbox=pic.getbbox(),arm=arm))
 if arm:
  pic=pic.copy();pic.alpha_composite(arms[0],tuple(round(float(arm['matrix'][k])/40)for k in('translateX','translateY')))
 x=i%8*192;y=i//8*224;page.alpha_composite(pic.resize((192,192)),(x,y));d.text((x+3,y+193),str(i+1)+' '+','.join(f['labels']),fill='white')
for i,(f,pic)in enumerate(zip(armtimeline,arms)):
 report['arm'].append(dict(frame=i+1,labels=f['labels'],bbox=pic.getbbox()))
page.convert('RGB').save(out/'body-normal-arm.png')
(out/'timelines.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))

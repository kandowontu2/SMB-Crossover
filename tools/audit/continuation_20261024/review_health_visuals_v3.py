from pathlib import Path
import argparse,hashlib,json
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('names',nargs='+');a=p.parse_args()
for name in a.names:
 folder=D/(name+'-food-v3-direct-v1');proof=json.loads((folder/'proof.json').read_text());assert proof['passed']and proof['ROM_sha256']=='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
 items=json.loads((folder/'health-result.json').read_text());assert items['passed'];out=D/(name+'-visual-v3');out.mkdir(exist_ok=False);sheet=Image.new('RGB',(1048,len(items['items'])*263),(20,25,35));draw=ImageDraw.Draw(sheet);chosen=[]
 for i,v in enumerate(items['items']):
  for col,(phase,frame)in enumerate([('head hit',v['reveal']+1),('emerging',v['reveal']+20),('mature',v['mature']+2),('collected',v['receipt']+3)]):
   f=folder/'frames'/f'{frame:06d}.png';draw.text((col*262+3,i*263+3),f'{name} kind{v["kind"]} {phase} f{frame}',fill='white');sheet.paste(Image.open(f).convert('RGB'),(col*262+2,i*263+20));chosen.append(dict(kind=v['kind'],phase=phase,frame=frame,path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest()))
 f=out/'moments.png';sheet.save(f);(out/'sampling-manifest.json').write_text(json.dumps(dict(sheet=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),frames=chosen),indent=2)+'\n');print(name,len(chosen))

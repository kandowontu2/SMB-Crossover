from pathlib import Path
import csv,hashlib,json
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;out=D/'copy-visual-review-v1';out.mkdir(exist_ok=False);manifest=[]
for mode in ['easy','hard']:
 folder=D/('copies-'+mode+'-direct-v1');proof=json.loads((folder/'proof.json').read_text());assert proof['passed']
 rows=list(csv.DictReader((folder/'copy-trace.csv').open()));result=json.loads((folder/'copy-result.json').read_text());assert result['passed']
 for start in [0,7]:
  sheet=Image.new('RGB',(1048,7*263),(20,25,35));draw=ImageDraw.Draw(sheet);chosen=[]
  for i,item in enumerate(result['powers'][start:start+7]):
   stage=start+i+1;group=[x for x in rows if int(x['case'])==stage]
   dropped=next(int(x['frame'])for x in group if x['phase']=='drop'and int(x['tick'])==10)
   recovery=next(int(x['frame'])for x in group if x['phase']=='reswallow'and int(x['tick'])==12)
   samples=[('copied',item['copyFrame']+10),('attack',item['attackFrame']+8),('discarded',dropped),('recovered',recovery)]
   for col,(phase,frame)in enumerate(samples):
    p=folder/'frames'/f'{frame:06d}.png';draw.text((col*262+3,i*263+3),f'{mode} copy{item["power"]} {phase} f{frame}',fill='white');sheet.paste(Image.open(p).convert('RGB'),(col*262+2,i*263+20))
    chosen.append(dict(power=item['power'],phase=phase,frame=frame,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
  p=out/(mode+'-'+str(start//7+1)+'.png');sheet.save(p);manifest.append(dict(sheet=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),frames=chosen))
(out/'sampling-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(dict(sheets=len(manifest),sampled_moments=sum(len(x['frames'])for x in manifest))))

"""Index terminal native scenes without changing or crediting failed runs."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
from PIL import Image,ImageDraw


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);report=json.loads((a.evidence/'discover-results.json').read_text())
    rows=[]
    for case in report['runs']:
        if case['passed']:continue
        folder=Path(case['folder']);frames=sorted((folder/'frames').glob('*.png'))
        assert frames
        frame=frames[-1];trace=list(csv.DictReader((folder/'trace.csv').open()))
        actual=next(r for r in trace if int(r['frame'])==int(frame.stem))
        rows.append(dict(identity=case['identity'],mode=case['mode'],failure=case['failure'],terminal_frame=case['frames'],
            screenshot=str(frame),screenshot_sha256=hashlib.sha256(frame.read_bytes()).hexdigest(),sampled_state=actual,last_trace=trace[-5:]))
    pages=[]
    for start in range(0,len(rows),15):
        items=rows[start:start+15];im=Image.new('RGB',(5*256,3*280),(24,28,36));draw=ImageDraw.Draw(im)
        for i,row in enumerate(items):
            x,y=i%5*256,i//5*280;s=row['sampled_state']
            draw.text((x+4,y+3),row['identity']+' '+row['mode']+' '+str(row['failure']),fill='white')
            draw.text((x+4,y+17),'f'+s['frame']+' x'+s['x']+' y'+s['y']+' power'+s['power'],fill='white')
            with Image.open(row['screenshot'])as source:im.paste(source.convert('RGB'),(x,y+40))
        target=a.output/('terminal-scenes-'+str(start//15+1)+'.png');im.save(target)
        pages.append(dict(path=str(target),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    q=dict(ROM_sha256=report['ROM_sha256'],negative_cases=len(rows),scenes=rows,pages=pages,
        visual_review_pending=True,scope='Last retained discovery frame per negative case and exact terminal trace. Sampling is diagnostic only; no failure is removed, weakened or relabeled a pass.')
    (a.output/'index.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(cases=len(rows),pages=pages),indent=2))


if __name__=='__main__':main()

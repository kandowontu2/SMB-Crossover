"""Offline first-input-difference and retained gap illustration; no emulation."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--batch',type=Path,required=True);p.add_argument('--retry',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 old=a.batch/'native/simon-easy';new=a.retry/'discovery';direct=a.retry/'direct';x=rows(old/'inputs.csv');y=rows(new/'inputs.csv');i=next(i for i,(u,v)in enumerate(zip(x,y))if u!=v);assert i==3612 and x[i]['mask']=='1'and y[i]['mask']=='129'
 tx=rows(old/'trace.csv');ty=rows(new/'trace.csv');j=next(j for j,(u,v)in enumerate(zip(tx,ty))if u!=v)
 poses=lambda r:[z for z in r if 3609<=int(z['frame'])<=3700]
 sheet=Image.new('RGB',(1024,520),'#202020');draw=ImageDraw.Draw(sheet);bindings=[]
 for row,folder,kind in[(0,old,'retained discovery'),(1,direct,'independent directPPU')]:
  for col,frame in enumerate([3612,3636,3660,3672]):
   f=folder/'frames'/f'{frame:06d}.png';sheet.paste(Image.open(f).convert('RGB'),(col*256,row*260+20));draw.text((col*256,row*260),kind+' '+str(frame),fill='white');bindings.append(dict(kind=kind,frame=frame,path=str(f),sha256=sha(f)))
 sheet.save(a.output/'gap-before-after.png')
 z=dict(passed=True,offline_only=True,original_failure_retained=True,original_input_sha256=sha(old/'inputs.csv'),retry_input_sha256=sha(new/'inputs.csv'),equal_input_prefix_rows=i,first_differing_input=dict(original=x[i],retry=y[i]),equal_trace_prefix_rows=j,first_differing_trace=dict(original=tx[j],retry=ty[j]),original_gap_trace=poses(tx),retry_gap_trace=poses(ty),illustration_frames=bindings,illustration_sha256=sha(a.output/'gap-before-after.png'),scope='Delayed genuine secondAedge gains height; native physics/ROM unchanged. Input/trace prefix proof plus selected gap illustration. Original discovery PNG is not retagged as lossless independent directPPU, and the mixed-source sheet is not a pixel/epoch-equality assertion. Original failureFALSE remains.')
 (a.output/'proof.json').write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,input_prefix_rows=i,trace_prefix_rows=j,proof_sha256=sha(a.output/'proof.json'),sheet_sha256=sha(a.output/'gap-before-after.png')),indent=2))
if __name__=='__main__':main()

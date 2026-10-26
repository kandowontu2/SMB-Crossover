"""Read-only saved-frame context for genuinely pending cold DMA epochs."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw,ImageFont
from final_item_abilities_static_prepare_v2 import CURRENT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['ROM_sha256']==CURRENT
 records=[];placements=[]
 for profile in ready['profiles']:
  native=Path(profile['output']);proof=json.loads((native/'proof.json').read_text());assert proof['passed'];pending=[];complete={};mask=[]
  for line in(native/'ability-dma-epochs.jsonl').open():
   q=json.loads(line)
   if q['kind']=='startFrame-hardware'and q.get('pending_dma_id'):pending.append(q)
   elif q['kind']=='completed-DMA-before-render-enable':complete[q['id']]=q
   elif q['kind']=='actual-PPUMASK-write':mask.append(q)
  rows=list(csv.DictReader((native/'actual-ppu-index.csv').open()));byframe={int(q['ppu_frame']):q for q in rows}
  with(native/'actual-ppu.argb').open('rb')as raw:
   for q in pending:
    dma=complete[q['pending_dma_id']];assert q['stamp']['mask']&24==0 and dma['source']==dma['hardware']and len(dma['writes'])==256
    assert dma['start']['mask']&24==dma['complete']['mask']&24==0
    record=dict(profile=profile['profile'],pending_startFrame=q,actual_completed_DMA=dma,same_frame_PPUMASK=[v for v in mask if v['stamp']['frame']==q['stamp']['frame']],context=[])
    for frame in range(q['stamp']['frame']-1,q['stamp']['frame']+2):
     r=byframe[frame];ordinal=int(r['ordinal']);raw.seek((ordinal-1)*245760);data=raw.read(245760);assert len(data)==245760
     f=a.output/(profile['profile']+f'-PPU{frame}.png');Image.frombytes('RGBA',(256,240),data,'raw','BGRA').convert('RGB').save(f)
     image=dict(profile=profile['profile'],actual_PPU_index=r,raw_slice_sha256=hashlib.sha256(data).hexdigest(),PNG=str(f),PNG_sha256=sha(f));record['context'].append(image);placements.append(image)
    records.append(record)
 font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',12);sheet=Image.new('RGB',(768,len(records)*270),(240,240,240));draw=ImageDraw.Draw(sheet)
 for i,record in enumerate(records):
  for j,img in enumerate(record['context']):
   x=j*256;y=i*270;draw.text((x+2,y+3),record['profile']+' PPU'+img['actual_PPU_index']['ppu_frame'],font=font,fill='black');sheet.paste(Image.open(img['PNG']),(x,y+30))
 path=a.output/'cold-render-disabled-pending-context.png';sheet.save(path)
 z=dict(passed=True,ROM_sha256=CURRENT,native_run=False,actual_saved_evidence=True,agent_visual_review=False,pending_epochs=len(records),wholeframes=len(placements),records=records,sheet=str(path),sheet_sha256=sha(path),scope='Pending source/hardware is never relabeled completed. All observed pending starts render-disabled; genuine E008 later logs complete256exact. Actual neighbor images require separate agent review; no universal late-NMI claim.')
 (a.output/'proof.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),pending_epochs=len(records),wholeframes=len(placements),sheet=str(path))))
if __name__=='__main__':main()

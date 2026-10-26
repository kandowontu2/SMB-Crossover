"""Actual assembled13cell source/hardware verifier components plus strict negative controls."""
from pathlib import Path
import argparse,copy,csv,hashlib,json
from cv3_remaining_sfx_queue_native_verify_v4 import source_model
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--matrix',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);m=json.loads((a.matrix/'proof.json').read_text());assert m['passed']and m['native_executed']is False;rows=[]
 for cell in m['cells']:
  cp=Path(cell['cpu']['path']).parent;cfg=json.loads((cp.parent.parent/cell['name']/'configuration.json').read_text());cue=cfg['expected_cue']
  for scenario in['none','slot','head']:
   d=cp/scenario;events=[json.loads(s)for s in(d/'queue-owners.jsonl').read_text().splitlines()];images=list(csv.DictReader((d/'source-register-image.csv').open()));apu=list(csv.DictReader((d/'assembled-apu.csv').open()));model=source_model(events,images,apu,cue);failures=[]
   def reject(name,ev,im,ap):
    try:source_model(ev,im,ap,cue)
    except AssertionError as e:failures.append(dict(name=name,error=str(e)));return
    raise AssertionError(('Expected negative was accepted',cell['name'],scenario,name))
   i=next(i for i,r in enumerate(images)if int(r['address'])==0x400f);epoch=int(images[i]['audioEpoch']);h=next(i for i,r in enumerate(apu)if int(r['register'])==0x400f and int(r['audioEpoch'])==epoch)
   x=copy.deepcopy(images);x[i]['value']=str(int(x[i]['value'])^5);reject('raw400F image low bits',events,x,apu)
   x=copy.deepcopy(apu);x[h]['value']=str(int(x[h]['value'])^5);reject('raw400F hardware low bits',events,images,x)
   x=copy.deepcopy(images);del x[i];reject('missing image store',events,x,apu)
   x=copy.deepcopy(apu);x.insert(h,copy.deepcopy(x[h]));reject('duplicate owned hardware store',events,images,x)
   x=copy.deepcopy(images);x[i],x[i+1]=x[i+1],x[i];reject('source emission image sequence swapped',events,x,apu)
   x=copy.deepcopy(events);e=next(e for e in x if e['kind']=='drain-return'and cue in e['cues']);e['cues'][e['cues'].index(cue)]=1 if cue!=1 else 4;reject('wrong consumed event',x,images,apu)
   rows.append(dict(cell=cell['name'],scenario=scenario,event=cell['event'],mode=cell['mode'],epochs=len(model),original_image_order_contract=cue!=6,declared_legacy_adapter_order=[0x400e,0x400f,0x400c]if cue==6 else None,negative_controls=failures,inputs={f:sha(d/f)for f in['queue-owners.jsonl','source-register-image.csv','assembled-apu.csv']}))
 result=dict(passed=True,native_executed=False,matrix_sha256=sha(a.matrix/'proof.json'),actual_assembled_scenarios=len(rows),negative_controls=sum(len(r['negative_controls'])for r in rows),cases=rows,validator_sha256=sha(Path(__file__).with_name('cv3_remaining_sfx_queue_native_verify_v4.py')),scope='Source components only: actual assembled CPU stores, not fabricated native proof. All original bytes/raw400F and hardware compared. New effects require original image order; existing1F has explicitly declared unchanged adapter order. No native140-update gameplay/cadence verdict.',tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,scenarios=len(rows),negative_controls=result['negative_controls']),indent=2))
if __name__=='__main__':main()

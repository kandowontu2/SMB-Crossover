"""Future validator component proof from real assembled stores and historical cadence; no Mesen."""
from pathlib import Path
import argparse,copy,csv,hashlib,json
from cv3_remaining_sfx_queue_native_verify_v2 import source_model,cadence_metrics
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cpu',type=Path,required=True);p.add_argument('--historical',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);receipt=json.loads((a.cpu/'proof.json').read_text());assert receipt['passed']and receipt['native_executed']is False;cases=[]
 for name in['none','slot','head']:
  d=a.cpu/name;ev=[json.loads(l)for l in(d/'queue-owners.jsonl').read_text().splitlines()];im=list(csv.DictReader((d/'source-register-image.csv').open()));ap=list(csv.DictReader((d/'assembled-apu.csv').open()));rows=source_model(ev,im,ap);failed=[]
  def reject(label,events,images,apu):
   try:source_model(events,images,apu)
   except AssertionError as e:failed.append(dict(name=label,error=str(e)));return
   raise AssertionError(('Missing expected failure',label,name))
  i=next(i for i,r in enumerate(im)if int(r['address'])==0x400f);h=next(i for i,r in enumerate(ap)if int(r['register'])==0x400f and int(r['audioEpoch'])>=int(im[0]['audioEpoch']))
  x=copy.deepcopy(im);x[i]['value']=str(int(x[i]['value'])^5);reject('raw400F image low bits changed',ev,x,ap)
  x=copy.deepcopy(ap);x[h]['value']=str(int(x[h]['value'])^5);reject('raw400F hardware low bits changed',ev,im,x)
  x=copy.deepcopy(im);del x[i];reject('missing original image write',ev,x,ap)
  x=copy.deepcopy(ap);x.insert(h,copy.deepcopy(x[h]));reject('duplicate owned hardware store',ev,im,x)
  x=copy.deepcopy(im);x[i],x[i+1]=x[i+1],x[i];reject('noise high/low original store order swapped',ev,x,ap)
  x=copy.deepcopy(ev);c=next(r for r in x if r['kind']=='drain-return'and 5 in r['cues']);c['cues'][c['cues'].index(5)]=4;reject('wrong consumed source event',x,im,ap)
  cases.append(dict(scenario=name,real_assembled_source_and_hardware_epochs=len(rows),image_writes=len(im),negative_controls=failed,inputs={f:sha(d/f)for f in['queue-owners.jsonl','source-register-image.csv','assembled-apu.csv']}))
 base=list(csv.DictReader((a.historical/'baseline50b/cadence.csv').open()));held=list(csv.DictReader((a.historical/'held0802/cadence.csv').open()));same=cadence_metrics(base,base);old=cadence_metrics(held,base);assert same['passed']and not old['passed']and old['candidate_draws']==136 and old['baseline_draws']==137
 bp=json.loads((a.historical/'baseline50b/proof.json').read_text());hp=json.loads((a.historical/'held0802/proof.json').read_text());assert bp['updates']==hp['updates']==140 and bp['draws']==138 and hp['draws']==137
 # An isolated same-total scheduling deferral remains explicitly held.
 synthetic=[dict(updates=1,draws=v)for v in[1,0,1,1]];delayed=[dict(updates=1,draws=v)for v in[0,1,1,1]];phase=cadence_metrics(delayed,synthetic);assert not phase['passed']and phase['candidate_draws']==phase['baseline_draws']and phase['all_draw_prefix_deferrals']
 result=dict(passed=True,native_executed=False,scope='Source-only testing of future native validator components. Actual assembled CPU/NMI stores, not fabricated native proof; original executable raw400F and full owned hardware are compared. Historical real0802 cadence remains rejected. This does not execute the0c45 full140-update fixture or establish native timing/guards.',cpu_receipt=dict(path=str(a.cpu/'proof.json'),sha256=sha(a.cpu/'proof.json')),cases=cases,component_negative_controls=sum(len(r['negative_controls'])for r in cases),historical_baseline_self=same,historical0802_rejection=old,historical_complete_game_proof_totals=dict(baseline=dict(updates=bp['updates'],draws=bp['draws']),held0802=dict(updates=hp['updates'],draws=hp['draws'])),endFrame_CSV_excludes_final_postcallback_update_and_draw=True,synthetic_equal_total_prefix_rejection=phase,validator_sha256=sha(Path(__file__).with_name('cv3_remaining_sfx_queue_native_verify_v2.py')),tool_sha256=sha(__file__))
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,cases=len(cases),negative_controls=result['component_negative_controls'],original0802_cadence_accepted=old['passed']),indent=2))
if __name__=='__main__':main()

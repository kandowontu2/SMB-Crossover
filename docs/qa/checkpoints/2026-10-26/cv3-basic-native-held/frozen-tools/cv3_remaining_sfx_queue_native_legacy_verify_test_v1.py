"""v5 uses exact proven v4 source model and checks full1F hardware; source only."""
from pathlib import Path
import argparse,copy,hashlib,inspect,json
import cv3_remaining_sfx_queue_native_verify_v4 as old
import cv3_remaining_sfx_queue_native_verify_v5 as new
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--control',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);r=json.loads((a.control/'proof.json').read_text());assert r['passed']and r['native_executed']is False;assert inspect.getsource(old.source_model)==inspect.getsource(new.source_model)and inspect.getsource(old.cadence_metrics)==inspect.getsource(new.cadence_metrics);cases=[]
 for c in r['cases']:
  frames=json.loads(Path(c['path']).read_text());rows=[dict(audioEpoch=q['frame']+1,register=at,value=v)for q in frames for at,v in q['complete_hardware']];positive=new.compare_legacy_hardware(rows,rows);negative=[]
  for label,mutate in[('raw400F low bits',lambda x:x[next(i for i,r in enumerate(x)if r['register']==0x400f)].__setitem__('value',13)),('actual audio epoch',lambda x:x[0].__setitem__('audioEpoch',0)),('full host music byte',lambda x:x[0].__setitem__('value',x[0]['value']^1)),('missing ordered hardware store',lambda x:x.pop(0)),('added APUframecounter4017 store',lambda x:x.insert(0,dict(audioEpoch=1,register=0x4017,value=64)))]:
   changed=copy.deepcopy(rows);mutate(changed)
   try:new.compare_legacy_hardware(changed,rows)
   except AssertionError as e:negative.append(dict(name=label,error=str(e)))
   else:raise AssertionError(('Missing failure',label))
  cases.append(dict(mode=c['mode'],actual_assembled_control_sha256=c['sha256'],positive=positive,negative_controls=negative))
 result=dict(passed=True,native_executed=False,v4_source_and_cadence_function_bytes_retained=True,cases=cases,negative_controls=sum(len(c['negative_controls'])for c in cases),v5_sha256=sha(new.__file__),scope='Source component proof only. Whole actual baseline/candidate assembled1F hardware equality is established by the bound legacy-control receipt. This adds unmasked ordered400x/4015/4017+actual epoch comparator and5meaningful failures per mode. No fabricated native proof, no emulator/adoption.',tool_sha256=sha(__file__));(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,native_executed=False,negative_controls=result['negative_controls']),indent=2))
if __name__=='__main__':main()

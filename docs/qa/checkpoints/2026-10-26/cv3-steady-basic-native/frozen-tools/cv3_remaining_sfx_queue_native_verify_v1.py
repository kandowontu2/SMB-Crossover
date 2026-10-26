"""Future explicit-grant0c45 result: actual consumer-timed original source and strict cadence."""
from pathlib import Path
import argparse,csv,hashlib,json
from cv3_primary_sfx_source_v1 import Original,CV3
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def longest(rows,key):
 run=best=0
 for r in rows:
  run=run+1 if int(r[key])==0 else 0;best=max(best,run)
 return best
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);prep=json.loads((a.fixture/'preparation.json').read_text());assert sha(a.fixture/'run.lua')==prep['script_sha256'];proof=json.loads((a.fixture/'proof.json').read_text());assert proof['passed'];case=proof['cases'][0];assert case['modeReadback']==0 and case['durationUpdates']==140 and case['queuePublished']==case['queueConsumed']==case['spawnCalls']==case['requests']==3
 events=[json.loads(s)for s in(a.fixture/'queue-owners.jsonl').read_text().splitlines()];images=list(csv.DictReader((a.fixture/'source-register-image.csv').open()));apu=list(csv.DictReader((a.fixture/'apu.csv').open()));epochs=sorted(set(int(r['audioEpoch'])for r in apu));original=Original(CV3.read_bytes());original.call(0xe227);first=min(e['audioEpoch']for e in events if e['kind']=='drain-return'and 5 in e['cues']);source_rows=[]
 for epoch in[ep for ep in epochs if ep>=first]:
  consumed=[]
  for e in events:
   if e['kind']=='drain-return'and e['audioEpoch']==epoch:
    for cue in e['cues']:
     assert cue==5,'Basic fixture cannot silently cancel/rephase the active source attack';original.call(0xe25f,a=0x1e);consumed.append(cue)
  before=(original.m[0x10a],original.m[0x10d]);original.m.trace=[];original.call(0xe24e)
  expected=[(r['address'],r['value'])for r in original.m.trace if(before[0]and r['address']in[0x4000,0x4001,0x4002,0x4003])or(before[1]and r['address']in[0x400c,0x400e,0x400f])];actual=[(int(r['address']),int(r['value']))for r in images if int(r['audioEpoch'])==epoch];assert actual==expected,('Ordered source register image incl raw400F',epoch,actual,expected)
  for active,registers in[(before[0],[0x4000,0x4001,0x4002,0x4003]),(before[1],[0x400c,0x400e,0x400f])]:
   if active:
    wanted=sorted((at,v)for at,v in expected if at in registers);hardware=[(int(r['register']),int(r['value']))for r in apu if int(r['audioEpoch'])==epoch and int(r['register'])in registers];assert hardware==wanted,('Original complete owned-voice hardware values, no400F mask',epoch,hardware,wanted)
  source_rows.append(dict(audioEpoch=epoch,consumed=consumed,sourceBefore=before,ordered_source=actual))
 cadence=list(csv.DictReader((a.fixture/'cadence.csv').open()));base=list(csv.DictReader((a.baseline/'cadence.csv').open()));prefix=[];ca=cb=0
 for i in range(max(len(cadence),len(base))):
  if i<len(cadence):ca+=int(cadence[i]['draws'])
  if i<len(base):cb+=int(base[i]['draws'])
  if ca<cb:prefix.append(dict(offset=i,candidate_draw_prefix=ca,baseline_draw_prefix=cb))
 metrics=dict(candidate_frames=len(cadence),baseline_frames=len(base),candidate_draws=sum(int(r['draws'])for r in cadence),baseline_draws=sum(int(r['draws'])for r in base),candidate_max_no_draw=longest(cadence,'draws'),baseline_max_no_draw=longest(base,'draws'),candidate_max_no_update=longest(cadence,'updates'),baseline_max_no_update=longest(base,'updates'),all_draw_prefix_deferrals=prefix)
 cadence_pass=len(cadence)<=len(base)and metrics['candidate_draws']>=metrics['baseline_draws']and metrics['candidate_max_no_draw']<=metrics['baseline_max_no_draw']and metrics['candidate_max_no_update']<=metrics['baseline_max_no_update']and not prefix
 result=dict(passed=cadence_pass,accepted=False,ROM_sha256=prep['ROM_sha256'],script_sha256=prep['script_sha256'],actual_numeric_mode=0,actual_actor_cues=3,original_source_ROM_sha256=sha(CV3),strict_ordered_source_and_raw_owned_hardware_frames=len(source_rows),no_raw400F_or_source_store_masks=True,cadence=metrics,status='BOUNDED_NATIVE_SOURCE_AND_STRICT_CADENCE_PASS'if cadence_pass else'HELD_NATIVE_CADENCE_DEFICIT',tool_sha256=sha(__file__),scope='Only the one frozen real0c45 Easy-lightning/basic140 fixture. Original effects are requested on observed actualNMI consumer epochs and compared for full ordered source image plus adapted ascending owned-voice hardware flush. Released voices may restore host music. Strict per-prefix/draw/stall/physical-frame comparison is conservative; any deferral remains HELD for explicit review. No automatic adoption or broader gameplay claim.')
 (a.output/'source-model.json').write_text(json.dumps(source_rows,indent=2)+'\n');(a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()

"""Bind fresh optimized native cases, including every per-case stall and prefix deficit."""
from pathlib import Path
import argparse,csv,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-dmc-complete-v1')
CAND='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
BASE='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
 with Path(p).open(newline='')as f:return list(csv.DictReader(f))
def stats(rs):
 result=dict(physical_frames=len(rs))
 for key in ['updates','draws']:
  run=maximum=zero=0
  for r in rs:
   run=run+1 if int(r[key])==0 else 0;maximum=max(maximum,run);zero+=int(int(r[key])==0)
  result['total_'+key]=sum(int(r[key])for r in rs);result['zero_'+key+'_frames']=zero;result['maximum_consecutive_no_'+key+'_frames']=maximum
 return result
def compare_case(c,b,cr,br):
 assert c['name']==b['name']and c['modeReadback']==b['modeReadback']and c['durationUpdates']==b['durationUpdates']
 assert len(cr)==c['frames']and len(br)==b['frames']
 totals=[dict(updates=0,draws=0),dict(updates=0,draws=0)];low=dict(updates=0,draws=0);high=dict(updates=0,draws=0);deficits=[];allprefix=[]
 for elapsed in range(max(len(cr),len(br))):
  for index,rs in enumerate([br,cr]):
   if elapsed<len(rs):
    for key in totals[index]:totals[index][key]+=int(rs[elapsed][key])
  delta={key:totals[1][key]-totals[0][key]for key in low}
  for key in low:low[key]=min(low[key],delta[key]);high[key]=max(high[key],delta[key])
  record=dict(physical_frame_offset=elapsed,delta=delta,baseline=dict(totals[0]),candidate=dict(totals[1]));allprefix.append(record)
  if any(v<0 for v in delta.values()):deficits.append(record)
 cs,bs=stats(cr),stats(br)
 gates=dict(same_actual_updates=c['durationUpdates']==b['durationUpdates'],no_more_physical_frames=c['frames']<=b['frames'],no_fewer_actual_draws=c['draws']>=b['draws'],no_more_zero_draw_frames=cs['zero_draws_frames']<=bs['zero_draws_frames'],no_more_zero_update_frames=cs['zero_updates_frames']<=bs['zero_updates_frames'],no_worse_longest_draw_stall=cs['maximum_consecutive_no_draws_frames']<=bs['maximum_consecutive_no_draws_frames'],no_worse_longest_update_stall=cs['maximum_consecutive_no_updates_frames']<=bs['maximum_consecutive_no_updates_frames'],prefix_deficits_recovered_by_end=all(totals[1][key]>=totals[0][key]for key in low))
 return dict(name=c['name'],mode=c['modeReadback'],actual_updates=c['durationUpdates'],candidate_actual_draws=c['draws'],baseline_actual_draws=b['draws'],candidate=cs,baseline=bs,prefix_delta_minimum=low,prefix_delta_maximum=high,temporary_prefix_deficit_frames=deficits,all_physical_frame_prefixes=allprefix,gates=gates,metrics_nonregression_pass=all(gates.values()))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);e=a.evidence;names=[]
 for ch in ['grant','sypha','alucard']:names += [f'native-{ch}-basic-v1',f'native-{ch}-basic-baseline-v1']
 names += ['native-grant-controls-v2','native-link-legacy-v2','native-simon-legacy-v1','native-link-legacy-baseline-v1','native-simon-legacy-baseline-v1','native-grant-death-v1','native-grant-character-v1','native-grant-AllOnes-v1']
 for ch in ['grant','sypha','alucard','simon','bill']:names += [f'native-{ch}-pressure-candidate-v1',f'native-{ch}-pressure-baseline-v1']
 data={};manifest={};caseinfo=[];dependencies={}
 for n in names:
  folder=e/n;j=json.loads((folder/'native-proof.json').read_text());b=json.loads((folder/'bindings.json').read_text());config=json.loads((folder/'configuration.json').read_text());expected=BASE if 'baseline'in n else CAND
  assert j['passed']and j['emulator_exit']==0 and j['ROM_sha256']==b['ROM_sha256']==expected and j['bindings_sha256']==sha(folder/'bindings.json')and b['script_sha256']==sha(folder/'run.lua')
  assert not re.search(r'\b(?:True|False)\b',(folder/'run.lua').read_text().splitlines()[0]);assert len(j['cases'])==len(config['cases'])
  for name,digest in b['dependencies'].items():assert sha(folder/'frozen'/name)==digest;dependencies.setdefault(name,set()).add(digest)
  for c,q in zip(j['cases'],config['cases']):
   assert c['q']==q and type(c['modeReadback'])is int and c['modeReadback']==q['mode']and c['sourceExact']
   stream=[]
   for r in c['dmcRecords']:
    d=r['descriptor'];assert 0<=r['reads']<=len(d['payload']);stream.append(dict(sound=d['sound'],bank=d['bank'],address=d['address'],rate=d['rate'],length=len(d['payload']),actual_reads=r['reads'],payload_sha256=hashlib.sha256(bytes(d['payload'])).hexdigest(),actual_final_DAC=r.get('endState',{}).get('apu.dmc.outputLevel')))
   caseinfo.append(dict(run=n,name=c['name'],mode=c['modeReadback'],actual_attacks=c['attacks'],actual_injuries=c['realInjuries'],actual_updates=c['durationUpdates'],frames=c['frames'],draws=c['draws'],streams=stream))
  data[n]=j;manifest[n]={f.name:sha(f)for f in folder.iterdir()if f.is_file()}
 pairs=[]
 for ch in ['grant','sypha','alucard']:pairs.append((f'native-{ch}-basic-v1',f'native-{ch}-basic-baseline-v1'))
 for ch in ['grant','sypha','alucard','simon','bill']:pairs.append((f'native-{ch}-pressure-candidate-v1',f'native-{ch}-pressure-baseline-v1'))
 pairs += [('native-link-legacy-v2','native-link-legacy-baseline-v1'),('native-simon-legacy-v1','native-simon-legacy-baseline-v1')]
 comparisons=[];ordinary=[]
 for cn,bn in pairs:
  ca,ba=data[cn]['cases'],data[bn]['cases'];cr,br=rows(e/cn/'cadence.csv'),rows(e/bn/'cadence.csv');assert len(ca)==len(ba)
  for i,(c,b)in enumerate(zip(ca,ba),1):
   record=compare_case(c,b,[r for r in cr if int(r['case'])==i],[r for r in br if int(r['case'])==i]);record['candidate_run']=cn;record['baseline_run']=bn;comparisons.append(record)
   if 'legacy'in cn:
    signature=lambda x,key:[((r['wall']-x['wallStart'])if key=='physical'else r['age'],r['register'],r['value'])for r in x['apu']if r['register']<=0x4013 or r['register']in[0x4015,0x4017]]
    exact=signature(c,'physical')==signature(b,'physical');assert exact;ordinary.append(dict(run=cn,actual_APU_register_value_physical_frame_sequence_exact=exact,APU_logical_update_age_sequence_exact=signature(c,'age')==signature(b,'age')))
 metrics=all(r['metrics_nonregression_pass']for r in comparisons);strict_prefix=all(not r['temporary_prefix_deficit_frames']for r in comparisons)
 (out/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(out/'per-case-performance.json').write_text(json.dumps(comparisons,indent=2)+'\n')
 result=dict(behavior_checks_passed=True,per_case_performance_nonregression_pass=metrics,all_prefixes_nonnegative=strict_prefix,adoption_ready=False,ROOT_independent_review_required=True,candidate_sha256=CAND,baseline_sha256=BASE,candidate_cases=sum(len(j['cases'])for n,j in data.items()if'baseline'not in n),baseline_cases=sum(len(j['cases'])for n,j in data.items()if'baseline'in n),matched_cases=len(comparisons),temporary_prefix_deficit_cases=[dict(name=r['name'],run=r['candidate_run'],count=len(r['temporary_prefix_deficit_frames']),first=r['temporary_prefix_deficit_frames'][:2])for r in comparisons if r['temporary_prefix_deficit_frames']],performance_summary=[{k:v for k,v in r.items()if k not in['all_physical_frame_prefixes','temporary_prefix_deficit_frames']}for r in comparisons],cases=caseinfo,ordinary=ordinary,guards={k:sum(j[k]for j in data.values())for k in['updates','draws','nmis','irq_scroll_writes','hardware_chr_checks','complete_dma_checks','stack_writes']},min_stack_pointer=min(j['min_sp']for j in data.values()),dependency_versions={n:sorted(v)for n,v in dependencies.items()},evidence_manifest_sha256=sha(out/'evidence-manifest.json'),performance_receipt_sha256=sha(out/'per-case-performance.json'),source_readiness_v3_sha256=sha(D/'source-readiness-optimized-current8ff-v3-r2/readiness.json'),held_e6b_failure_receipt_sha256=sha(D/'native-qualification-current8ff-v1/proof.json'),scope='Fresh exact4c70 real controller primary/contact owners and staged lifecycle/driver controls. Every paired case compares draw/update totals, actual physical frames, zero-draw/update frames, longest stalls and every cumulative prefix. Improvements may change phase; all temporary prefix deficits remain explicit for ROOT review. No full campaign, console hardware, waveform or universal lag claim.')
 (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');frozen=out/'frozen';frozen.mkdir()
 for f in[Path(__file__),ROOT/'tools/audit/cv3_dmc_complete_native_v1.py',ROOT/'tools/audit/cv3_dmc_complete_native_v1.lua']:shutil.copyfile(f,frozen/f.name)
 print(json.dumps({k:result[k]for k in['behavior_checks_passed','per_case_performance_nonregression_pass','all_prefixes_nonnegative','candidate_cases','baseline_cases','matched_cases','temporary_prefix_deficit_cases']},indent=2));print('proof_sha256='+sha(out/'proof.json'))
if __name__=='__main__':main()

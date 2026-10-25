"""Bind bounded native CV3 evidence; performance regressions remain a failed adoption gate."""
from pathlib import Path
import argparse,csv,hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py/cv3-dmc-complete-v1')
CAND='e6baf465a4fb3981dc1d9f1bea64a129f1dbb8d2a8276f934a38eb9c00c0728c'
BASE='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
 with Path(p).open(newline='')as f:return list(csv.DictReader(f))
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path,required=True);q=a.parse_args();out=q.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 names=[]
 for char in ['grant','sypha','alucard']:
  names += [f'native-{char}-basic-v1',f'native-{char}-basic-baseline-v1']
 names += ['native-grant-controls-v2','native-link-legacy-v2','native-simon-legacy-v1','native-link-legacy-baseline-v1','native-simon-legacy-baseline-v1','native-grant-death-v1','native-grant-character-v1','native-grant-AllOnes-v1']
 for char in ['grant','sypha','alucard','simon','bill']:
  names += [f'native-{char}-pressure-candidate-v1',f'native-{char}-pressure-baseline-v1']
 records={};manifest={};cases=[];deps={}
 for n in names:
  p=D/n;j=json.loads((p/'native-proof.json').read_text());b=json.loads((p/'bindings.json').read_text());cfg=json.loads((p/'configuration.json').read_text());expected=BASE if 'baseline'in n else CAND
  assert j['passed']and j['emulator_exit']==0 and j['ROM_sha256']==b['ROM_sha256']==expected
  assert j['bindings_sha256']==sha(p/'bindings.json')and b['script_sha256']==sha(p/'run.lua')
  assert not re.search(r'\b(?:True|False)\b',(p/'run.lua').read_text().splitlines()[0])
  for name,digest in b['dependencies'].items():assert sha(p/'frozen'/name)==digest;deps.setdefault(name,set()).add(digest)
  assert len(cfg['cases'])==len(j['cases'])
  for c,config in zip(j['cases'],cfg['cases']):
   assert c['q']==config and type(c['modeReadback'])is int and c['modeReadback']==config['mode']
   assert c['sourceExact']
   streams=[]
   for r in c['dmcRecords']:
    desc=r['descriptor'];assert 0<=r['reads']<=len(desc['payload'])
    streams.append(dict(sound=desc['sound'],bank=desc['bank'],address=desc['address'],rate=desc['rate'],length=len(desc['payload']),actual_reads=r['reads'],payload_sha256=hashlib.sha256(bytes(desc['payload'])).hexdigest(),final_output_level=r.get('endState',{}).get('apu.dmc.outputLevel'),non_DMC_dummy_reads=r.get('nonDmcReads',0)))
   cases.append(dict(run=n,name=c['name'],mode=c['modeReadback'],frames=c['frames'],updates=c['durationUpdates'],draws=c['draws'],real_attacks=c['attacks'],real_injuries=c['realInjuries'],streams=streams,audio_cycles_min=min(c['audioCycles']),audio_cycles_max=max(c['audioCycles'])))
  manifest[n]={f.name:sha(f)for f in p.iterdir()if f.is_file()};records[n]=j
 pressure=[]
 for ch in ['grant','sypha','alucard','simon','bill']:
  cn=f'native-{ch}-pressure-candidate-v1';bn=f'native-{ch}-pressure-baseline-v1';cr=rows(D/cn/'cadence.csv');br=rows(D/bn/'cadence.csv');assert len(cr)==len(br)
  diff=[dict(row=i,where={k:c[k]for k in ['wall','case','age']},changed={k:dict(baseline=b[k],candidate=c[k])for k in c if c[k]!=b[k]})for i,(c,b)in enumerate(zip(cr,br))if c!=b]
  audio=[]
  for c,b in zip(records[cn]['cases'],records[bn]['cases']):
   assert c['frames']==b['frames']and c['durationUpdates']==b['durationUpdates']and c['draws']==b['draws']
   ds=[u-v for u,v in zip(c['audioCycles'],b['audioCycles'])];assert len(ds)==len(c['audioCycles'])==len(b['audioCycles']);audio.append(dict(mode=c['modeReadback'],cycles_delta_values=sorted(set(ds)),updates=c['durationUpdates'],frames=c['frames'],draws=c['draws']))
  pressure.append(dict(character=ch,all_cadence_rows_exact=not diff,cadence_row_differences=diff,audio=audio))
 owners=[]
 for ch in ['grant','sypha','alucard']:
  cn=f'native-{ch}-basic-v1';bn=f'native-{ch}-basic-baseline-v1'
  for c,b in zip(records[cn]['cases'],records[bn]['cases']):
   assert c['name']==b['name']and c['durationUpdates']==b['durationUpdates']and c['frames']==b['frames']
   ds=[u-v for u,v in zip(c['audioCycles'],b['audioCycles'])]
   owners.append(dict(character=ch,name=c['name'],frames=c['frames'],updates=c['durationUpdates'],baseline_draws=b['draws'],candidate_draws=c['draws'],audio_cycle_delta_min=min(ds),audio_cycle_delta_max=max(ds),cycles_delta_values=sorted(set(ds))))
 ordinary=[]
 for ch,cn in [('link','native-link-legacy-v2'),('simon','native-simon-legacy-v1')]:
  c=records[cn]['cases'][0];b=records[f'native-{ch}-legacy-baseline-v1']['cases'][0]
  signature=lambda x:[(r['age'],r['register'],r['value'])for r in x['apu']]
  assert signature(c)==signature(b)and c['frames']==b['frames']and c['draws']==b['draws']
  ordinary.append(dict(character=ch,APU_register_value_age_exact=True,frames=c['frames'],updates=c['durationUpdates'],draws=c['draws'],audio_cycle_delta_values=sorted(set(u-v for u,v in zip(c['audioCycles'],b['audioCycles'])))))
 gate=all(r['baseline_draws']==r['candidate_draws']for r in owners)and all(r['all_cadence_rows_exact']for r in pressure)
 assert not gate,'Known retained cadence failure must remain visible'
 proof=dict(behavior_checks_passed=True,strict_cadence_gate_passed=gate,adoption_ready=False,candidate_sha256=CAND,baseline_sha256=BASE,candidate_cases=sum(len(v['cases'])for n,v in records.items()if 'baseline'not in n),baseline_cases=sum(len(v['cases'])for n,v in records.items()if 'baseline'in n),cases=cases,matched_no_source_pressure=pressure,matched_real_owners=owners,ordinary_owners=ordinary,guards={k:sum(j[k]for j in records.values())for k in ['updates','draws','nmis','irq_scroll_writes','hardware_chr_checks','complete_dma_checks','stack_writes']},min_stack_pointer=min(j['min_sp']for j in records.values()),dependency_versions={n:sorted(v)for n,v in deps.items()},retained_harness_failures=[dict(run='native-grant-quick-v1',reason='Post-payload RTS dummy read was misclassified as a new DMC fetch; bounded sequential/payload observer corrected, no ROM edit.'),dict(run='native-grant-controls-v1',reason='Pause counter omitted primary-pause fixture kind; actual pause49 frames and138 fetched bytes retained, no ROM edit.'),dict(run='native-link-legacy-v1',reason='Easy existing legacy shrink behavior incorrectly expected Hard source injury; ordinary source route narrowed to Hard, no game behavior change.')],scope='Staged combat and lifecycle arenas after actual cold menu/alternate input; actual controller primary and enemy-contact owners are distinguished from injected driver controls. Full campaign and audio waveform not certified. e6b remains HELD because the native Hard Alucard combined case loses one draw, with an additional one-frame draw deferral under no-source pressure.')
 (out/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');proof['evidence_manifest_sha256']=sha(out/'evidence-manifest.json');(out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 frozen=out/'frozen-tools';frozen.mkdir()
 for f in [Path(__file__),ROOT/'tools/audit/cv3_dmc_complete_native_v1.py',ROOT/'tools/audit/cv3_dmc_complete_native_v1.lua']:shutil.copyfile(f,frozen/f.name)
 (out/'tools-manifest.json').write_text(json.dumps({f.name:sha(f)for f in frozen.iterdir()},indent=2)+'\n')
 print(json.dumps({k:proof[k]for k in ['behavior_checks_passed','strict_cadence_gate_passed','adoption_ready','candidate_cases','baseline_cases']}));print('proof_sha256='+sha(out/'proof.json'))
if __name__=='__main__':main()

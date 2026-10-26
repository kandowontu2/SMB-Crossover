"""Freeze exact twenty lifecycle launches, nine passes and one genuine heldDMA."""
from pathlib import Path
import argparse,csv,hashlib,json
from cv3_remaining_sfx_queue_native_verify_v5 import cadence_metrics

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return dict(path=str(p),sha256=sha(p))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);ready=a.root/'freeze-v1/readiness-source-only.json';assert sha(ready)=='e7102d428cd5a872853094c2d2e3c2651afef092f70432aa8bbfc7d8ae1ebc42';r=json.loads(ready.read_text())
 for f,h in r['all_frozen_bindings'].items():assert sha(f)==h,f
 bindings={};rows=[];cells=[]
 for c in r['future_launches']:
  receipt=a.root/'native-v1'/c['name']/'proof.json';z=json.loads(receipt.read_text());assert z['native_guard_passed']and z['retries']==0 and z['exit_code']==0;assert z['readiness_sha256']==sha(ready)and z['settings_before_sha256']==z['settings_after_sha256']==r['settings']['sha256'];fixture=Path(c['fixture']);g=json.loads((fixture/'proof.json').read_text());assert g['passed']and g['cases'][0]['modeReadback']==c['mode'];assert sha(z['complete_GAMEproof']['path'])==z['complete_GAMEproof']['sha256'];cells.append(dict(name=c['name'],receipt=rec(receipt),GAMEproof=rec(fixture/'proof.json')))
  for folder in[fixture,receipt.parent]:
   for f in folder.rglob('*'):
    if f.is_file():bindings[str(f)]=sha(f)
  if c['version']=='baseline':continue
  base=Path(c['same_input_baseline']);bg=json.loads((base/'proof.json').read_text());comparison=receipt.parent/'comparison/proof.json';cp=json.loads(comparison.read_text());metrics=cadence_metrics(list(csv.DictReader((fixture/'cadence.csv').open())),list(csv.DictReader((base/'cadence.csv').open())));verdict=metrics['passed']and g['draws']>=bg['draws'];assert cp['passed']==verdict
  life=g['cases'][0]['life'];dmcs=[dict(sound=d['descriptor']['sound'],reads=d['reads'],rate=d['descriptor']['rate'],bank=d['descriptor']['bank'],address=d['descriptor']['address'])for d in g['cases'][0]['dmcRecords']]
  rows.append(dict(name=c['name'].removeprefix('candidate-'),mode=c['mode'],passed=verdict,all_source_hardware_and_native_goals_passed=True,comparison=rec(comparison),GAME_draws=dict(baseline=bg['draws'],candidate=g['draws']),actual_DMA_counts=dict(baseline=bg['strict_completed_DMA'],candidate=g['strict_completed_DMA']),native_updates=g['updates'],source_ticks=cp['original_source_frames'],complete_mixer_flushes=cp['complete_mixer_flushes'],strict_per_case_cadence=metrics,actual_lifecycle=life,actual_DMC=dmcs))
 assert len(cells)==20 and len(rows)==10 and sum(q['passed']for q in rows)==9 and [q['name']for q in rows if not q['passed']]==['pressure-fireball-hard']
 boundary=a.root/'held-boundary-v1/proof.json';b=json.loads(boundary.read_text());assert b['passed']and b['status']=='HELD_ONE_ACTUAL_MISSING_DMA_NOT_MERELY_FINAL_COUNTER'
 for f,h in b['frozen_inputs'].items():assert sha(f)==h
 report=Path(__file__).resolve().parents[2]/'docs/qa/cv3-remaining-sfx-lifecycle-native-2026-10-26.txt';bindings[str(report)]=sha(report);bindings[str(boundary)]=sha(boundary)
 for f in Path(__file__).parent.glob('cv3_remaining_sfx_lifecycle_*'):
  if f.is_file():bindings[str(f.resolve())]=sha(f)
 bindings[str(ready)]=sha(ready)
 out=dict(native_completed=True,accepted=False,production_mutated=False,status='HELD_ONE_GENUINE_HARD1F_PRESSURE_DMA_LOSS',native_launches=20,retries=0,worker_released=True,all20_native_hardware_goal_guards_passed=True,all10_source_hardware_oracles_passed=True,strict_cadence_passes=9,strict_cadence_held=1,actual_source_ticks=sum(q['source_ticks']for q in rows),actual_complete_mixer_flushes=sum(q['complete_mixer_flushes']for q in rows),all_draw_prefix_deferrals=sum(len(q['strict_per_case_cadence']['all_draw_prefix_deferrals'])for q in rows),source_ready=rec(ready),boundary=rec(boundary),report=rec(report),cells=cells,profiles=rows,all_new_frozen_bindings=bindings,tool_sha256=sha(__file__),scope='Ten exact real lifecycle profiles, paired fresh baseline/candidate. All strict native/source/hardware goals pass but one actual lostDMA remains; no final-counter or CSV endpoint waiver, no production adoption, no waveform/fullcampaign claim. Earlier BASIC/source receipts remain independently valid within original scopes.')
 (a.output/'qualification-native.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(status=out['status'],native_launches=20,retries=0,worker_released=True,strict_passes=9,held=1,all_new_bindings=len(bindings),qualification=rec(a.output/'qualification-native.json')),indent=2))
if __name__=='__main__':main()

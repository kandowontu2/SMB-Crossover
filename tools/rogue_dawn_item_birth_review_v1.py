"""Compact review of retained native actor chronology and linked origin test."""
from pathlib import Path
import csv,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
O=R/'docs/qa/rogue-dawn-native-item-absence-attribution-2026-10-29.json'
def main():
 assert not O.exists(),'Preserve review'
 D=R/'build/verification/rogue-dawn-actor-birth-chronology-native-v1'
 trace=list(csv.DictReader((D/'trace.csv').open()))
 events=[json.loads(x)for x in (D/'events.jsonl').open()]
 flag=[x for x in events if x['kind']=='native-actor-field-write']
 assert len(flag)==2 and all(x['data']['symbol']=='Enemy_Flag'and x['data']['slot']==0 for x in flag)
 packets=[x for x in events if x['kind']=='policy-read-only-diagnostic']
 assert len(packets)==128 and all(not a['flag']and not a['owner']and not a['pickup'] for x in packets for a in x['data']['actors'])
 assert all(x['data']['tanks']==0 for x in packets)
 anchors=[]
 for frame in[1025,1050,1075,1100,1125,1150,1175,1200,1225,1250,1300]:
  x=next(x for x in trace if int(x['frame'])==frame)
  anchors.append({k:int(x[k])for k in ['frame','loops','x','y','camera','mask','state','vy']})
 sourcepath=R/'docs/qa/rogue-dawn-item-birth-page-counterexample-2026-10-29.json'
 source=json.loads(sourcepath.read_text());positive=[]
 for row in source['rows']:
  if row['camera']==0:
   assert not row['birth'] # player337 lies outside this deliberately fixed viewport
   continue
  a=row['completed_Main_actor_snapshots']
  assert len(a)==85 and all(x['actors'][0]['x']==336 and x['actors'][0]['pickup']==0xd8 for x in a)
  assert a[-1]['actors'][0]['state']==128 and not row['erase_entries']
  ch=row['chronology'];u=row['birth'][0]['update']
  stores=[x for x in ch if x['update']==u and x['kind']=='write'and x['name']in ['Block_X_Position','Block_PageLoc','Enemy_X_Position','Enemy_PageLoc']]
  positive.append(dict(mode=row['mode'],camera=row['camera'],birth_update=u,
   completed_Main_survival=len(a),first=a[0],last=a[-1],origin_writes=stores))
 p=dict(finding='This native run never creates a typed pickup. Its approach reaches question-row worldX336 from ABOVE; later jumps start from the row top, not beneath the question. Native item contact/erase failure is not established.',
  native_negative=dict(directory=str(D),result=json.loads((D/'result.json').read_text()),
   actual_actor_field_changes=flag,actor_packets=len(packets),packet_PPU_interval=[packets[0]['stamp']['ppu_frame'],packets[-1]['stamp']['ppu_frame']],
   all_six_native_flags_and_typed_metadata_zero=True,earned_tanks_zero=True,trace_anchors=anchors),
  source_origin_hypothesis=dict(rejected_for_tested_path=True,actual_compiled_cases=positive,
   explanation='InitBlock_XY_Pos initially reads retained SmHead0/0, but genuine bank9 SophiaHeadBlockOrigin corrects blockX80/page1 at BFA6/BFAA before native SetupPowerUp stores actor world336. Camera225/257 actors mature and survive85 completedMains. No stale-page/offscreen-removal correction is justified.',
   camera0_limit='Fixed camera0 exposes only world0..255; staged player337 is outside loaded-page admission and no head event occurs. This is a viewport rejection, not an actor survival case.'),
  source_vs_native_limits=['The linked source scene stages legal adjacent row cells and player position; it is not a replay of native block RAM.',
   'Native physical block/head/SetupPowerUp PCs were not sampled. The absence of flag/metadata writes rejects born-then-erased in this watched run; exact native row tile remains unobserved.',
   'The source-held jump can reach84px. Generic approach jumps onto the earlier block and then crosses above the target row; changing resource/physics/collision rules is not justified.',
   'Prior selected blue-looking pieces do not establish live pickup art/ownership; their rendering attribution remains separate.',
   'No native successor launched and no ROM/game/controller/shared source changed by this review. ROOT owns any input-only approach correction.'],
  bindings=[v.ref.binding(p)for p in[Path(__file__),R/'tools/rogue_dawn_item_birth_page_v1.py',sourcepath,
   D/'ready.json',D/'launch.json',D/'result.json',D/'trace.csv',D/'inputs.csv',D/'events.jsonl',
   R/'src/bill_native_rare.s',R/'src/level_tiles.s',R/'src/rogue_dawn_host_deferred.s']])
 O.write_text(json.dumps(p,indent=2)+'\n');print(json.dumps(v.ref.binding(O)))
if __name__=='__main__':main()

"""Record verified terrain/performance progress without narrowing the goal."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,stat
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))


def main():
 out=V/'root-current49-progress-at.json';assert not out.exists()
 cp=R/'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json';c=json.loads(cp.read_text());assert len(c['source_hashes'])==442
 for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
 for b in c['builds']:
  for a in b['artifacts'].values():assert sha(R/a['path'])==a['sha256']
 paths=['root49-sophia-source-terrain-ik/implementation-stage-freeze-in.json','agent-lsr-sophia-terrain-ib-native-a/freeze.json','agent-lsr-sophia-feet-source-a/freeze.json','agent-lsr-sophia-feet-source-a/source-review.json','root49-sophia-land-source-io/actual.json','root49-sophia-query-perf-ip/implementation-component-freeze-it.json','root49-sophia-query-perf-ip/remaining-audio-iu.json','root49-shared-music-tail-iv.json']
 records=[rec(V/p)for p in paths]
 total=0;counts={s:0 for s in ['root49-sophia-source-terrain-','root49-sophia-query-perf-ip','agent-lsr-sophia-feet-source-a','agent-lsr-sophia-feet-implementation-a','agent49-e-sophia-union-a']};todo=[R]
 while todo:
  with os.scandir(todo.pop())as entries:
   for e in entries:
    try:s=e.stat(follow_symlinks=False)
    except FileNotFoundError:continue
    if getattr(s,'st_file_attributes',0)&0x400:continue
    if stat.S_ISDIR(s.st_mode):todo.append(e.path)
    elif stat.S_ISREG(s.st_mode):
     total+=s.st_size
     for k in counts:
      if k in e.path:counts[k]+=s.st_size
 assert total<60000000000,total
 private=V/'agent-lsr-sophia-feet-implementation-a';union=V/'agent49-e-sophia-union-a'
 record=dict(status='ACTIVE_GQ_FROZEN_IK_NATIVE_SOURCE_FEET_REPAIR_AND_MEASURED_QUERY_OPTIMIZATION',utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),predecessor=rec(V/'root-current49-progress-as.json'),
  previous_goal_turn='Progress: AS implemented and checked normal head/side/hover/coin correction in private IK, independently rehashed frozen447-source E, and advanced ordinary Samus to2-2. No main installation.',
  this_goal_turn='Progress: root freezes IK with144 exact actual caller reexecutions and real cue consumer; actual source-foot lead establishes42 missed direct landings and6 delayed fractional anchors/map; source landing NSF captured; exact pointer optimization saves31cycles/query in13312 compiled calls and all4builds; specialist new bank5 candidate repairs unchanged74 native source cases onM3 and is undergoing remaining admission.',
  current_checkpoint=rec(cp),main442_sources8_artifacts_exact=True,verified_records=records,
  IK_scope='60 native source terrain+14 cache/next-AirSync cases/map;58+14 full native reexecutions exact AXYP/SP/PC/all10240/every ordered write,2 actual NMI foreign gaps/map in60set retained. Cue consumed by real guarded bank38 ExpandedAudioTick STA$0105 (M3C954/M5C94C). No waveform or whole-source claim.',
  feet_lead='Both maps74cases with200 source diagnostics/map;148 full actual calls reexecuted exactly withzero gaps/native-cycle differences.62 strict DIRECT_ABOVE/map:42 missedlandings (38 sideways clamps),20 native lands (6 old fraction residues),14 fully correct controls;10 disjoint pass,2 real prior corners remain outside direct-axis verdict.',
  landing_audio='Original2.02 MusicInfo SophiaLand NSFtrack46 captured,8 audible updates1..8,pulse2. New candidate appends21B stream+extended25entrytables in oldFFtail; old24streams/tables/codePCs preserved. Actual transition/stream/mixer lifecycle admission pending.',
  performance='IP direct terrain pointer prototype preserves allregisters,all10240RAM exceptonly3 individually decoded removed discarded JSR/PHA residues,every ordered semantic write/livecallerstack. All256X x2pages x13rows/map (13312total) save31CPUcycles each. Both baseline hashes/audio/DPCM/SMC/headerCHR/NMIIRQ/Vine remain literal. Actual new native/frame/lag evidence still required.',
  feet_implementation_records={p.name:rec(p)for p in private.glob('*.json')},
  feet_implementation='New private source-c on exact contextual449 parent. All4builds pass, source floor canonicalization andlandrequest implemented; first unchanged74-caseM3 native source controlsPASS. Initial longbranch andbank3 overflow preserved. Root prior TITLE-free suggestion omittedRENDER; actual bank3tail361, so new optionalbank5tail chosen instead. Head-hook8byte assertion being corrected by explicit target-immediate classification. No main/parent edits.',
  contextual_union_records={p.name:rec(p)for p in union.glob('*snapshot*.json')},
  contextual_union='Pinned source-e449 remains immutable. Original body/raw/flow/reset+consumer native, moved fullspring112/map+224 strict scopes/map, rareAPI/ABI/NMI, Link source controls andmatched-entry profiles pass; final original native liveness/reward/four1780-frameordinary controls remain. Native spring short scopes attained0ISR; compiled per-instructionNMI normal/lag20832cases supplies separate modeled interrupt evidence.',
  contextual_cost='Actual matched empty foreground16256.296 M3/15405.247 M5; +51.901vs frozen447bodyE, +399.592/+430.963vsEC. Seeded6 mean28594.361/25524.304,lag249/158vs prior246/157. No universal optimization claim; timing/AI/interrupt qualification retained.',
  Samus='CurrentGQ MMC3Easy AP genuinely clears2-1 withactual SpringLaunch22189, enters2-2at23472. Later water controllerprogress reaches lasttallcolumns; AW terminal no-death progressbound after6px short highcap jump. AX held-A midairMorph test lastreported live3401; source-grounded bombboost isnextcandidateaffordance. No source defect/fullclear/allarsenal claim. Phase1.25GB,100MB finalauditreserve.',
  root_live_handles=[],phase_ceilings_bytes=dict(global_workspace=60000000000,contextual_E_Sophia=500000000,contextual_final_reserve=50000000,Sophia_feet_implementation=300000000,Sophia_feet_final_reserve=50000000,Sophia_terrain_aggregate=500000000,Samus_GQ=1250000000,Samus_final_reserve=100000000),workspace_bytes=total,owned_buckets_bytes=counts,
  remaining=['Finish contextual E native/ordinary freeze, independent root review and shared QA checkpoint admission.','Finish actual feet/head/side/landing-audio/ABI/ISR/performance admission on new private candidate; later contextual shared adoption.','Full source corner calcAxis/order, rotated/wall/ceiling/vine anchors, source/native firebar positive pixel/phase parity andotherremainingcharacterfidelity.','Fresh through2-2 controller routes onfinal admittedruntime, everycharacter/alternate/weapon/upgrade andlagprofiling.','Final recordedplaythroughs withlosslesscaptures retained; current source/route components do notsatisfythefullgoal.'],
  accepted_release=False,goal_complete=False)
 out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(dict(progress=rec(out),workspace_bytes=total,main_GQ_unchanged=True)))


if __name__=='__main__':main()

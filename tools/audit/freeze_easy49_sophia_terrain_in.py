"""Freeze the scoped IK terrain stage with its actual native caller packet."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
D=V/'root49-sophia-source-terrain-ik';N=V/'agent-lsr-sophia-terrain-ib-native-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=lambda p:dict(path=Path(p).relative_to(R).as_posix(),bytes=Path(p).stat().st_size,sha256=sha(p))


def main():
 out=D/'implementation-stage-freeze-in.json';assert not out.exists()
 native=N/'freeze.json'
 assert sha(native)=='524d4284d45095c2c2b3629dbf4c433b547055edac9213ce2e1c4617deefbb15'
 f=json.loads(native.read_text());assert f['status']=='FROZEN'
 for n,entry in f['files'].items():
  p=N/n;assert p.stat().st_size==entry['bytes']and sha(p)==entry['sha256'],n
 review=json.loads((N/'final-review.json').read_text())
 assert sha(N/'final-review.json')==f['report_sha256']=='6c64625bbc469163f3d1da9ef893a19ace853391f484b71fe73b93654e808dc8'
 assert review['no_runtime_source_edits']and review['no_owned_native_jobs']
 strict=[]
 for n,count,gaps in [('strict-e.json',58,2),('strict-f.json',14,0)]:
  data=json.loads((N/n).read_text());assert len(data['maps'])==2
  for m in data['maps']:
   assert m['native_reexecuted']==count and len(m['gaps'])==gaps,(n,m['mapper'])
   assert all(c['allAXYP_SP_PC']and c['all10240RAM']and c['liveCallerStack']for c in m['cases'])
  strict.append(rec(N/n))
 assert len(review['lifecycle'])==2
 assert all(x['cases']==14 and x['native_cache_prefix']and x['next_AirSync_Q16_exact']and x['post_cue_then_actual_NMI_consumer']for x in review['lifecycle'])
 prep=json.loads((D/'preparation.json').read_text());assert len(prep['source_sha256'])==445
 for n,h in prep['source_sha256'].items():assert sha(D/'source'/n)==h,n
 static=json.loads((D/'static-il.json').read_text());assert static['status']=='PASS_PRIVATE_IK_STATIC_BASELINES_AUDIO_RAM_AND_RESIDENT_CONTINUATIONS'
 for m in static['maps']:
  for a in m['artifacts'].values():assert sha(R/a['path'])==a['sha256']
  a=m['baseline'];assert sha(R/a['path'])==a['sha256']
 record=dict(status='FROZEN_PRIVATE_NORMAL_SOPHIA_TERRAIN_STAGE_NOT_FULL_SOURCE_ADMISSION',utc=datetime.now(timezone.utc).isoformat(),script_sha256=sha(__file__),
  source_catalog=prep['source_sha256'],preparation=rec(D/'preparation.json'),static=rec(D/'static-il.json'),compiled=[rec(D/n)for n in ['compiled-ig.json','brick-none-ik.json']],
  artifacts={m['mapper']:m['artifacts']for m in static['maps']},baselines={m['mapper']:m['baseline']for m in static['maps']},
  native_packet=rec(native),native_packet_files_rehashed=len(f['files']),native_review=rec(N/'final-review.json'),strict_full_callers=strict,
  actual_native_scope='60 original/additive terrain cases per mapper plus14 cache/next-AirSync cases per mapper.58+14 actual uninterrupted calls/map exact AXYP/SP/PC/all10240/every ordered RAM/SMC/mapper/push write; two actual NMI foreign gaps/map in60 set remain explicit.',
  audio_scope='Same post-BG cue02 precedes actual guarded ExpandedAudioTick ClearQueues STA$0105 in bank38 (M3C954/M5C94C); successor+3 observes00 while Q16 persists through next AirSync. This is queue producer/consumer evidence, not waveform equivalence.',
  source_scope=prep['scope'],added_RAM=0,main_changed=False,accepted_release=False,goal_complete=False,
  remaining=['Full source foot span/direct-above and corner calcAxis/order.','Rotated wall/ceiling/vine anchors and last rectangle epochs.','Source/native firebar positive pixel/phase/birth parity.','Contextual E full native/ABI/interrupt/moved spring admission and profiling.','Fresh complete controller-only through2-2 routes, all weapons/upgrades/alternates and final recordings.'])
 out.write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(dict(status=record['status'],freeze=rec(out),native_files=len(f['files']),actual_strict_calls=144)))


if __name__=='__main__':main()

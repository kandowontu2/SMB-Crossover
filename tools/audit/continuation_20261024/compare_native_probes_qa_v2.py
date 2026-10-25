from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;Q=D.parent/'2026-10-24-native-head-pz';P=D/'native-probes-qa-v2';O=P/'comparison-v1';O.mkdir(exist_ok=False)
old=json.loads((Q/'full-roster-aggregate-v2/proof.json').read_text())['runs'];new=json.loads((P/'direct-v1/proof.json').read_text());assert new['passed']and new['complete']
rows=[]
for r in new['runs']:
 p=Path(r.get('guarded_review',r['review']))/'proof.json';n=json.loads(p.read_text())['strict_route'];before=next(x for x in old if x['identity']==r['identity']and x['mode']==r['mode'])
 z=dict(identity=r['identity'],mode=r['mode'],parent_frames=before['frames'],new_frames=n['frames'],parent_lag_NMIs=before['measured_lag_NMIs'],new_lag_NMIs=n['measured_lag_NMIs'],parent_measured_video_frames=before['measured_gameplay_video_frames'],new_measured_video_frames=n['measured_gameplay_video_frames'],parent_policy='retained PZ controller',candidate_policy='same retained controller'if r['identity']!='proto'else'pre-existing MegaMan ledge wrapper, also valid for Proto selector',parent_proof=before['proof'],candidate_proof=str(p));rows.append(z)
a=json.loads((Q/'profile-megaman-v5/proof.json').read_text())['scopes'];b=json.loads((P/'profile-v1/proof.json').read_text())['scopes']
scopes={n:dict(parent_median=a[n]['median'],candidate_median=b[n]['median'])for n in ('CrossoverHeadProbe','CrossoverSourceSideProbe','PlayerBGCollision','PlayerCtrlRoutine','GameLoop')}
q=dict(passed=True,goal_complete=False,rows=rows,profiled_scopes=scopes,scope='Independent adaptive discoveries and exact same-hash physical replays; changed controller timing and enemy mixtures are declared, so whole-route medians/lag are descriptive, not identical-input universal FPS or pure causal workload benchmarks. The separate actual query CPU differentials isolate exact per-invocation savings. Full roster/item/source/performance completion remains open.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))

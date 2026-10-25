from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;Q=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-head-pz');O=Q/'full-roster-aggregate-v2';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
finished=json.loads((Q/'finish-v2/progress.json').read_text());assert finished['complete']and finished['passed']
runs=[]
for batch in (Q/'direct-v2-34',Q/'finish-v2/direct-last-two'):
 data=json.loads((batch/'progress.json').read_text());assert data['complete']and data['passed']
 for run in data['runs']:
  path=Path(run.get('guarded_review',run['review']))/'proof.json';proof=json.loads(path.read_text());assert proof['passed']and proof['ROM_sha256']==finished['ROM_sha256']
  route=proof['strict_route'];assert route['deaths']==0
  runs.append(dict(identity=run['identity'],mode=run['mode'],proof=str(path),proof_sha256=sha(path),raw_review_exit=run['raw_review_exit'],qualified_temporary_probe_observation=bool(run.get('guarded_review')),**route))
for mode in ('easy','hard'):
 path=D/'ryu-head-review-v5'/mode/'proof.json';proof=json.loads(path.read_text())
 # Ryu's exact original proof predates the common streaming wrapper.
 runs.append(dict(identity='ryu',mode=mode,proof=str(path),proof_sha256=sha(path),original_proof=proof))
identities=sorted(set(r['identity']for r in runs));assert len(identities)==37 and len(runs)==38
report=dict(passed=True,goal_complete=False,ROM_sha256=finished['ROM_sha256'],identities=identities,identity_count=37,native_route_cases=38,runs=runs,known_limitations=['Some identities are checked in one selected mode; Ryu both modes. This is not the both-mode/shortcut campaign matrix.','Physical frames and controller/CPU traces are retained and checked, but sampled overviews are not exhaustive human visual inspection.','Measured lag remains. These route proofs do not complete every item, weapon, source fidelity, music or mapper qualification.'])
(O/'proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(identities=len(identities),native_route_cases=len(runs),proof=str(O/'proof.json'))))
for row in sorted((r for r in runs if 'measured_lag_NMIs'in r),key=lambda r:r['measured_lag_NMIs']/r['measured_gameplay_video_frames'],reverse=True)[:10]:print(row['identity'],row['mode'],row['measured_lag_NMIs'],row['measured_gameplay_video_frames'])


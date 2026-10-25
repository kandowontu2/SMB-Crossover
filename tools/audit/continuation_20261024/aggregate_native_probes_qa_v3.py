from pathlib import Path
import collections,hashlib,json,statistics
D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'full-roster-aggregate-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();digest=sha(P/'candidate.nes');rows=[];parents=[]
for folder in ('direct-v1','remaining-direct-v1','corrected-direct-v1','gap-direct-v1','landing-direct-v1'):
 path=P/folder/'proof.json';q=json.loads(path.read_text());assert q['passed']and q['complete']and q['ROM_sha256']==digest
 parents.append(dict(path=str(path),sha256=sha(path)))
 for row in q['runs']:
  assert row['passed'];path=Path(row.get('guarded_review',row['review']))/'proof.json';proof=json.loads(path.read_text());assert proof['passed']and proof['ROM_sha256']==digest and sha(path)==row['strict_proof_sha256']
  discovery=Path(row['discovery'])/'manifest.json';m=json.loads(discovery.read_text());assert m['result']['cleared']and m['result']['deaths']==0 and sha(discovery)==row['discovery_manifest_sha256']
  rows.append(dict(identity=row['identity'],mode=row['mode'],review=str(path),review_sha256=sha(path),discovery=str(discovery),discovery_sha256=sha(discovery),frames=m['result']['frames'],capture=row['capture']))
assert len(rows)==len({(r['identity'],r['mode'])for r in rows})==38
identities=sorted(set(r['identity']for r in rows));assert len(identities)==37
baseline=json.loads((D.parent/'2026-10-24-native-head-pz/full-roster-aggregate-v2/proof.json').read_text());assert identities==baseline['identities']
report=dict(passed=True,goal_complete=False,ROM_sha256=digest,identities=identities,cases=len(rows),runs=rows,parents=parents,scope='All37 identities have independently replayed zero-death1-1 clears on this exact ROM; Ryu has both modes, other identities retain selected modes. Every actual PPU frame retained losslessly and strict original motion/CHR/split bounds retained. Prior failed discoveries remain failures; no both-mode/shortcut/all-item/fidelity completion claim.')
(O/'proof.json').write_text(json.dumps(report,indent=2))
bench=P/'matched-benchmark-v2';q=json.loads((bench/'proof.json').read_text());assert q['passed']and q['complete'];comparisons=[]
for name in ('megaman','samus','bill','raphael'):
 pair={r['version']:r for r in q['runs']if r['identity']==name};assert set(pair)=={'pz','qa'}
 classes={}
 for version,row in pair.items():
  fixture=row['fixture'];groups=collections.defaultdict(list)
  for line in(Path(row['folder'])/'ordinary-profile.jsonl').open():
   z=json.loads(line)
   if z['name']=='GameLoop'and fixture['start_frame']+60<=z['frame']and z['return_frame']<fixture['end_frame']-1:groups[z['skip']].append(z['exclusive_cycles'])
  classes[version]={str(skip):dict(calls=len(v),mean=statistics.mean(v),median=statistics.median(v))for skip,v in groups.items()}
 comparisons.append(dict(identity=name,physical_frames=1200,mean_GameLoop_cycles={v:r['metrics']['GameLoop']['mean']for v,r in pair.items()},completed_logical_updates={v:r['fixture']['logical_updates']for v,r in pair.items()},skipped_NMIs={v:r['fixture']['skipped_NMIs']for v,r in pair.items()},GameLoop_by_native_draw_skip=classes))
result=dict(passed=True,goal_complete=False,source_proof_sha256=sha(bench/'proof.json'),cases=comparisons,scope='Scoped matched stationary three-Goomba fixtures with original audio enabled. Mega/Samus use less foreground CPU; Raphael adds116cycles/update from the fallback gates. These fixtures show no material change in logical throughput/skipped-NMI counts. Mixtures of normal/catch-up draw work can shift medians, so compare means and native skip classes. Do not claim a universal or measured display-FPS gain.')
(O/'matched-comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(passed=True,cases=len(rows),identities=len(identities),matched=comparisons)),flush=True)

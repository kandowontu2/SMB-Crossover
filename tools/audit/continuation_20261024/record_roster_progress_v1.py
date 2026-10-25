from pathlib import Path
import datetime,hashlib,json
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;digest='70480630828a92839938b18b3e4f73acd8f9255879b2174df00f41c2e6cf98c9'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
tags=['known-routes-v3','remaining-routes-v1','remaining-routes-v2','remaining-routes-v3','remaining-routes-v4','remaining-routes-v5','bass-routes-v6','bass-routes-v7','turtle-routes-v1'];pairs={};indexes=[]
for tag in tags:
 p=D/tag/'discover-results.json';q=json.loads(p.read_text());assert q['complete']and q['ROM_sha256']==digest;indexes.append(dict(path=str(p),sha256=sha(p),aggregate_passed=q['passed']))
 for row in q['runs']:
  if row['passed']:pairs.setdefault((row['identity'],row['mode']),Path(row['folder']))
p=D/'megaman-ledge-v1';pairs[('megaman','easy')]=p
rows=[]
for (name,mode),folder in sorted(pairs.items()):
 p=folder/'manifest.json';m=json.loads(p.read_text());assert m['ROM_sha256']==digest and m['exit']==0 and not m['fixed_replay']and m['result']['cleared']and m['result']['deaths']==0 and m['chr_commit']['passed']
 rows.append(dict(identity=name,mode=mode,passed=True,frames=m['result']['frames'],folder=str(folder),manifest_sha256=sha(p),policy_sha256=sha(folder/'policy.lua'),inputs_sha256=sha(folder/'inputs.csv'),trace_sha256=sha(folder/'trace.csv')))
names={x['identity']for x in rows};assert len(names)==37 and len(rows)==71
missing=sorted(set((n,m)for n in names for m in ['easy','hard'])-set(pairs));assert missing==[('bass','easy'),('dale','easy'),('mario','hard')]
parent=json.loads((D/'current-37-bindings-v1.json').read_text());assert parent['passed']and parent['ROM_sha256']==digest
strict=json.loads((D/'current-roster-direct-v1/progress.json').read_text());assert strict['ROM_sha256']==digest;qualified=[]
for row in strict['runs']:
 if not row['passed']:continue
 p=Path(row.get('guarded_review',row['review']))/'proof.json';q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==digest and sha(p)==row['strict_proof_sha256'];qualified.append(dict(identity=row['identity'],mode=row['mode'],proof=str(p),sha256=sha(p)))
for relative in ['megaman-ledge-replay-v1/review-megaman-easy/proof.json','bass-direct-v1/guarded-review-bass-hard/proof.json']:
 p=D/relative;q=json.loads(p.read_text());assert q['passed']and q['ROM_sha256']==digest;qualified.append(dict(identity=q['identity'],mode=q['mode'],proof=str(p),sha256=sha(p)))
assert len({x['identity']for x in qualified})==len(qualified)
proof=dict(goal_complete=False,inventory_complete=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),ROM_sha256=digest,zero_death_identity_count=37,zero_death_mode_pairs=71,required_mode_pairs=74,remaining_mode_pairs=missing,all_37_binding=dict(path=str(D/'current-37-bindings-v1.json'),sha256=sha(D/'current-37-bindings-v1.json')),source_indexes=indexes,runs=rows,strict_qualified_at_snapshot=len(qualified),strict_qualified=qualified,strict_35_case_batch_complete=strict['complete'],strict_batch_progress_path=str(D/'current-roster-direct-v1/progress.json'),strict_batch_progress_sha256_at_snapshot=sha(D/'current-roster-direct-v1/progress.json'),human_reviewed_current_overviews=['mario-easy','luigi-easy','megaman-easy','bass-hard'],native_Z2_numeric_proof=dict(path=str(D/'zelda-rpg-final-v3/proof.json'),sha256=sha(D/'zelda-rpg-final-v3/proof.json'))if(D/'zelda-rpg-final-v3/proof.json').exists()else None,right_edge_false_lead=dict(path=str(D/'mario-edge-observer-v1/diagnosis.json'),sha256=sha(D/'mario-edge-observer-v1/diagnosis.json')),driver_sha256=sha(Path(__file__)),scope='Actual current-ROM native zero-death1-1discoveries cover all37identities and71of74difficulty pairs. Failed aggregates and attempts are preserved; only independently validated individual successes are selected. Strict current-hash direct replay is still running for35selected identities; Mega Man and Bass are already separate qualified runs. Human review is explicitly sampled. Remaining every-item uses/SFX/expiry/refill, shortcuts, palette/music/performance/mapper/guide work remain open. Heavy Mega Man/Bass lag is measured, not represented as60Hz. No public ROM replacement.')
out=D/'current-roster-progress-v1.json';out.write_text(json.dumps(proof,indent=2)+'\n');qdir=R/'build/verification/native-rest-py';(qdir/'roster-progress-v1.json').write_bytes(out.read_bytes());print(json.dumps(dict(identities=37,mode_pairs=71,remaining=missing,strict_qualified=len(qualified),strict_batch_complete=strict['complete'])))

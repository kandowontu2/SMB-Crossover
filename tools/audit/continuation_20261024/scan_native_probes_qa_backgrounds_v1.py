from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;P=D/'native-probes-qa-v2';O=P/'background-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=P/'full-roster-aggregate-v1/proof.json';q=json.loads(source.read_text());assert q['passed']and q['cases']==38
driver=R/'tools/audit/scan_direct_background_ox.py';original=R/'tools/audit/scan_background_transients_oq.py'
report=dict(scan_complete=False,goal_complete=False,ROM_sha256=q['ROM_sha256'],source_proof_sha256=sha(source),driver_sha256=sha(driver),original_sha256=sha(original),runs=[],scope='Narrow diagnostic background scan over all38 verified native streams: same-before/after middle-frame clusters, with original sprite/border masks. Persistent/longer defects, sprite omissions, missing actors and source fidelity remain outside scope. Any candidate requires investigation, not automatic game-failure attribution.')
for run in q['runs']:
 key=run['identity']+'-'+run['mode'];out=O/key
 with(O/(key+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(driver),'--capture',run['capture'],'--output',str(out)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,key
 path=out/'proof.json';z=json.loads(path.read_text());assert z['scan_complete']and z['ROM_sha256']==report['ROM_sha256']
 row=dict(identity=run['identity'],mode=run['mode'],proof=str(path),proof_sha256=sha(path),frames=z['retained_PNGs'],triples=z['admitted_adjacent_triples'],candidate_events=z['candidate_events'],sheets=z['sheets']);report['runs'].append(row);(O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
assert len(report['runs'])==38 and sha(driver)==report['driver_sha256']and sha(original)==report['original_sha256']
report.update(scan_complete=True,candidate_events=sum(r['candidate_events']for r in report['runs']));report['human_candidates_pending']=report['candidate_events']>0
(O/'proof.json').write_text(json.dumps(report,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2))

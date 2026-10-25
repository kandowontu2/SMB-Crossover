from pathlib import Path
import json,subprocess,hashlib,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');Q=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-head-pz');O=Q/'background-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
driver=R/'tools/audit/scan_direct_background_ox.py';original=R/'tools/audit/scan_background_transients_oq.py'
report=dict(scan_complete=False,goal_complete=False,ROM_sha256='675c57f4abd94d51d0f48a54f0a1d661ed75ef18b153de32a29d94145ba1d47d',driver_sha256=sha(driver),original_sha256=sha(original),runs=[],scope='Diagnostic transient-background checks on every verified direct physical PPU frame; narrow same-before/after middle-frame clusters only, masked sprites and borders excluded. Candidates require human/source investigation. Not an all-graphics or source-fidelity pass.')
for batch in (Q/'direct-v2-34',Q/'finish-v2/direct-last-two'):
 data=json.loads((batch/'proof.json').read_text());assert data['passed']and data['complete']and data['ROM_sha256']==report['ROM_sha256']
 for run in data['runs']:
  key=run['identity']+'-'+run['mode'];out=O/key
  with(O/(key+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(driver),'--capture',run['capture'],'--output',str(out)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode==0,key
  path=out/'proof.json';q=json.loads(path.read_text());assert q['scan_complete']and q['ROM_sha256']==report['ROM_sha256']
  row=dict(identity=run['identity'],mode=run['mode'],proof=str(path),proof_sha256=sha(path),frames=q['retained_PNGs'],triples=q['admitted_adjacent_triples'],candidate_events=q['candidate_events'],sheets=q['sheets']);report['runs'].append(row)
  (O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(row),flush=True)
assert len(report['runs'])==36 and sha(driver)==report['driver_sha256']and sha(original)==report['original_sha256']
report['scan_complete']=True;report['candidate_events']=sum(r['candidate_events']for r in report['runs']);report['human_candidates_pending']=report['candidate_events']>0
(O/'progress.json').write_text(json.dumps(report,indent=2));(O/'proof.json').write_text(json.dumps(report,indent=2))

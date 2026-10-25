"""Current-hash native item/copy fixtures, with complete actual PPU retention."""
from pathlib import Path
import hashlib,json,importlib.util,re,sys,time
D=Path(__file__).resolve().parent;O=D.parent/'2026-10-24-native-head-pz/items-v1';O.mkdir(parents=True,exist_ok=False)
PX=D.parent/'2026-10-24-native-items-px';ROM=D/'ryu-head-candidate-v5/candidate.nes'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
digest='675c57f4abd94d51d0f48a54f0a1d661ed75ef18b153de32a29d94145ba1d47d';assert sha(ROM)==digest
# Rebind host destinations only; the observer, geometry and fixture assertions
# stay literal. The written bound driver is itself hashed by every receipt.
t=(D/'capture_food_v4.py').read_text()
assert t.count("out=BASE/(name+'-food-v3-direct-v1')")==1;t=t.replace("out=BASE/(name+'-food-v3-direct-v1')","out=BASE/name")
assert t.count("rom=BASE/'food-candidate-v3/candidate.nes'")==1;t=t.replace("rom=BASE/'food-candidate-v3/candidate.nes'","rom=Path("+repr(ROM.as_posix())+")")
bound=O/'capture.py';bound.write_text(t)
spec=importlib.util.spec_from_file_location('current_component_capture',bound);cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
selected=[]
old=PX/'head-v3-native-results.json'
for row in json.loads(old.read_text()):
 assert row['passed']and row['exit']==0
 source=PX/(row['name']+'-head-v3-native/run.lua');assert sha(source)==row['fixture_sha256']
 selected.append((row['name'],source,old))
old=PX/'zelda2-native-items-v1-results.json'
for row in json.loads(old.read_text()):
 assert row['exit']==0
 source=PX/('zelda2-'+row['mode']+'-native-v1/run.lua');assert sha(source)==row['script_sha256']
 selected.append(('zelda2-'+row['mode'],source,old))
for family,file,prefix in [('health','health-food-final-v3/results.json','health-food-final-v3'),('copy','kirby-copies-final-v3/results.json','kirby-copies-final-v3')]:
 old=D/file;q=json.loads(old.read_text());assert q['passed']
 for row in q['runs']:
  assert row['exit']==0
  name=row.get('name')or row['mode'];source=D/prefix/name/'run.lua';assert sha(source)==row.get('fixture_sha256',row.get('script_sha256'))
  selected.append((family+'-'+name,source,old))
assert len(selected)==26
report=dict(ROM_sha256=digest,passed=False,complete=False,goal_complete=False,bound_capture_driver_sha256=sha(bound),source_capture_driver_sha256=sha(D/'capture_food_v4.py'),cases=26,runs=[],native_workers=1,scope='Fresh current-hash execution of retained native physical-item/copy assertions. Full direct actual PPU pixels, inputs/state and hardware audio writes retained. Staged maps/status/actors remain declared, not untouched campaigns. These26cases do not cover every roster identity or every requested final mechanic.')
def save():(O/'progress.json').write_text(json.dumps(report,indent=2)+'\n')
save()
for name,original,parent in selected:
 fixture=O/'fixtures'/name;fixture.mkdir(parents=True)
 text=original.read_text();dependencies=[]
 for i,path in enumerate(re.findall(r'dofile\("([^"\n]+)"\)',text)):
  source=Path(path);target=fixture/('dependency-'+str(i)+'.lua');target.write_bytes(source.read_bytes());dependencies.append(dict(original=str(source),sha256=sha(source),frozen=str(target)))
  text=text.replace(json.dumps(path),json.dumps(target.as_posix()))
 (fixture/'run.lua').write_text(text)
 row=dict(name=name,source_fixture=str(original),source_fixture_sha256=sha(original),parent_receipt=str(parent),parent_receipt_sha256=sha(parent),frozen_fixture_sha256=sha(fixture/'run.lua'),dependencies=dependencies,passed=False)
 report['runs'].append(row);save();start=time.monotonic()
 try:
  q=cap.run(name,fixture);row['passed']=q['passed']and q['ROM_sha256']==digest
  row.update(frames=q['direct_physical_frames'],proof_sha256=sha(O/name/'proof.json'))
 except BaseException as error:
  row['error']=repr(error);row['seconds']=round(time.monotonic()-start,2);save();print(json.dumps(row),flush=True);raise
 assert sha(original)==row['source_fixture_sha256']and all(sha(Path(x['original']))==x['sha256']for x in dependencies)
 row['seconds']=round(time.monotonic()-start,2);save();print(json.dumps(dict(completed=len(report['runs']),total=26,**row)),flush=True)
report.update(complete=True,passed=all(x['passed']for x in report['runs']));save();(O/'proof.json').write_text(json.dumps(report,indent=2)+'\n')

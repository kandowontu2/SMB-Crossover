"""Freeze two UNRUN5354 lifecycle fixtures; no emulator or production mutation."""
from pathlib import Path
import argparse,hashlib,json,shutil,re

ROOT=Path(__file__).resolve().parents[2]
SHA='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','observer-source','transition-cpu','buffer-cpu','dmc-source','menu-final','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.preparation/'proof.json').read_text());assert z['ROM_sha256']==SHA and z['native_run']is False and{k['kind']for k in z['profiles']}=={'death','area'}
 files=set();receipts={}
 for name,folder in [('observer',a.observer_source),('transition',a.transition_cpu),('buffer',a.buffer_cpu),('DMC_source_model',a.dmc_source)]:
  q=json.loads((folder/'proof.json').read_text());assert q['passed']and not q['native_run']and q['ROM_sha256']==SHA;receipts[name]=dict(path=str(folder/'proof.json'),sha256=sha(folder/'proof.json'));files.update(f.resolve()for f in folder.rglob('*')if f.is_file())
 old=json.loads((a.menu_final/'proof.json').read_text());assert old['passed']and old['ROM_sha256']==SHA
 m=json.loads((a.menu_final/'manifest.json').read_text());assert all(sha(f)==h for f,h in m.items());files.update(Path(f).resolve()for f in m);files.update(f.resolve()for f in a.menu_final.iterdir()if f.is_file())
 files.update(f.resolve()for f in a.preparation.rglob('*')if f.is_file());static=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';bridge=ROOT/'tools/audit/parodius_visibility_hud_lifecycle_bridge_v4.lua'
 profiles=[]
 for v in z['profiles']:
  packet=Path(v['packet']);q=json.loads((packet/'preparation.json').read_text());script=Path(q['script']);text=script.read_text();config=json.loads(script.with_name('config.json').read_text())
  assert sha(script)==q['script_sha256']and sha(script.with_name('candidate.nes'))==SHA
  assert config['mode']==0 and config['variant']==1 and config['limit']==v['limit']
  assert text.count(static.read_text())==1 and text.count(bridge.read_text())==1 and not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',text)
  assert not(script.parent/'proof.json').exists()and not(script.parent/'lifecycle-proof.json').exists()
  for f,h in q['dependencies'].items():assert sha(f)==h;files.add(Path(f).resolve())
  profiles.append(dict(kind=v['kind'],limit=v['limit'],actual_mode_required=0,actual_variant_required=1,script_sha256=sha(script),packet=str(packet),preparation_sha256=sha(packet/'preparation.json')))
 # Bind fresh actual settings independently, without changing either file.
 prior=json.loads((a.menu_final/'manifest.json').read_text());envpath=next(Path(f)for f in prior if Path(f).name=='environment.json'and Path(f).parent.name=='parodius-menu-terminal-phase-ready-v1');environment=json.loads(envpath.read_text());envdir=a.output/'environment';envdir.mkdir()
 for field in ['emulator','core','worker_settings','user_settings']:
  f=Path(environment[field]);assert sha(f)==environment[field+'_sha256'];files.add(f.resolve())
  if field.endswith('settings'):shutil.copy2(f,envdir/(field+'.json'));files.add((envdir/(field+'.json')).resolve())
 environment['settings_untouched']=True;(a.output/'environment.json').write_text(json.dumps(environment,indent=2)+'\n');files.add((a.output/'environment.json').resolve())
 for name in ['parodius_visibility_hud_transition_ready_v1.py','parodius_visibility_hud_transition_prepare_v1.py','parodius_visibility_hud_transition_run_v1.py','parodius_visibility_hud_transition_v1.lua','parodius_visibility_hud_transition_cpu_v1.py','parodius_visibility_hud_transition_buffer_cpu_v1.py','parodius_visibility_hud_transition_dmc_v1.py']:
  files.add((ROOT/'tools/audit'/name).resolve())
 for name in ['parodius-hud-transition-cpu-v1','parodius-hud-transition-cpu-v2','parodius-hud-transition-buffer-cpu-v1','parodius-hud-transition-buffer-cpu-v2','parodius-hud-transition-buffer-cpu-v3']:
  folder=a.output.parent/name
  if folder.exists():files.update(f.resolve()for f in folder.rglob('*')if f.is_file())
 report=ROOT/'docs/qa/parodius-hud-transition-readiness-2026-10-26.txt';files.add(report.resolve())
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,profiles=profiles,preparation_sha256=sha(a.preparation/'proof.json'),receipts=receipts,qualified_menu_final_sha256=sha(a.menu_final/'proof.json'),original_static_guard_sha256=sha(static),terminal_bridge_sha256=sha(bridge),environment=environment,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),tool_sha256=sha(Path(__file__)),limits='Two finite UNRUN numericEasy0/Octopus controllers: natural death/restart2200 and physical pipe/area2600. No staged arena/resources/queues/audio/outcome writes. Actual current-area identity comes from observed assembled loader, not mutable destinationAreaPointer. Native death/loaded-area/current-generation45 and real pending Buffer2 hold/catch-up remain required; reachability is unproved, and missing overlap must stay coverage failure rather than game defect. Character18 DMC eligibility is source-closed;32cycle bound is an explicit synthetic steady-sample model, not a native DMC/global hardware verdict. No grant/worker reservation/production/settings/adoption changes.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(manifest),profiles=profiles),indent=2))


if __name__=='__main__':main()

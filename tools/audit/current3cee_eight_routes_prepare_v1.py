"""Freeze eight existing controller policies and one-worker current3cee tools."""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def once(s,old,new):assert s.count(old)==1,old;return s.replace(old,new)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 parent=D/'root-current-brothers-6c69-v1';candidate=D/'root-chip-hud-composed-v1';rom=candidate/'candidate.nes';assert sha(rom)==SHA
 assert sha(Path('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes'))==SHA
 old=json.loads((parent/'readiness.json').read_text());env=D/'parodius-menu3cee-ready-v1/environment.json';e=json.loads(env.read_text())
 for n in['emulator','core','worker_settings','user_settings']:assert sha(e[n])==e[n+'_sha256'],n
 aggregate=D/'native-probes-qa-v2/full-roster-aggregate-v1/proof.json';original=json.loads(aggregate.read_text());selected=[]
 cases=['megaman:easy','proto:easy','samus:easy','bill:easy','lance:easy','bass:hard','roll:easy','ryu:easy']
 for case in cases:
  name,mode=case.split(':');row=next(z for z in original['runs']if z['identity']==name and z['mode']==mode).copy()
  if name=='bass':row['discovery']=str(D/'current8ff-bass-retry-v1/discovery/manifest.json')
  manifest=Path(row['discovery']);m=json.loads(manifest.read_text());assert m['result']['cleared']and m['result']['deaths']==0
  policy=manifest.parent/'policy.lua';assert not re.search(r'\bemu\.(?:write|setState|loadSavestate|reset)\s*\(',policy.read_text())
  selected.append(row)
 put(out/'selected-aggregate.json',dict(passed=True,source_selection_only=True,runs=selected,parent_index_sha256=sha(aggregate),Bass_latest_passing_controller_reused=True))
 for name in['runner.py','capture.py']:(out/name).write_bytes((parent/name).read_bytes())
 coordinator=(parent/'coordinator.py').read_text()
 coordinator=once(coordinator,str(parent/'runner.py').replace('\\','\\\\'),str(out/'runner.py').replace('\\','\\\\'))
 coordinator=once(coordinator,str(parent/'capture.py').replace('\\','\\\\'),str(out/'capture.py').replace('\\','\\\\'))
 coordinator=once(coordinator,"aggregate_path = d / 'native-probes-qa-v2/full-roster-aggregate-v1/proof.json'",'aggregate_path = Path('+repr(str(out/'selected-aggregate.json'))+')')
 (out/'coordinator.py').write_text(coordinator)
 for f in out.glob('*.py'):compile(f.read_text(),str(f),'exec')
 dependencies={rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),candidate/'proof.json',candidate/'source-manifest.json',aggregate,env,Path(__file__)}
 for rel,h in json.loads((candidate/'source-manifest.json').read_text()).items():
  f=candidate/'source'/rel;assert sha(f)==h;dependencies.add(f)
 for row in selected:
  f=Path(row['discovery']);dependencies|={f,f.parent/'policy.lua'}
 dependencies|={D/'current8ff-bass-retry-v1/proof.json',D/'current8ff-bass-retry-v1/direct/proof.json'}
 for name in['emulator','core','worker_settings','user_settings']:dependencies.add(Path(e[name]))
 extra=['tools/audit/current_roster_recheck_routes.py','tools/audit/check_tmnt_render_oa.py','tools/audit/observe_chip_committed_write.py',
  'tools/audit/run_mesen_isolated.py','tools/run_mesen.py','tools/playthroughs/roster_harness.lua','tools/playthroughs/roster_audit.lua',
  'tools/audit/legacy_chr_observer_of.lua','tools/audit/chr_commit_observer.lua','tools/audit/roll_render_observer.lua']
 dependencies|={ROOT/n for n in extra}|{parent/n for n in['runner.py','capture.py','coordinator.py','readiness.json']}|{D/'mmc3-static-call-v37/full-roster-v1/native-guard.lua'}
 dependencies|={f for f in out.iterdir()if f.is_file()};bindings={str(f.resolve()):sha(f)for f in sorted(dependencies,key=str)}
 command=[sys.executable,'-B',str(out/'coordinator.py'),'--rom',str(rom),'--archive',str(D),'--output',str(out/'native'),'--cases',*cases,'--replay','--frames','18000']
 proof=dict(passed=True,native_executed=False,ROM_sha256=SHA,native_workers=1,cases=cases,command=command,bindings=bindings,
  parent_coordinator_paths_and_source_index_only_changed=True,runner_and_direct_capture_exact_frozen_brothers_bytes=True,
  settings_no_save_AllZeros_nonrandom_hardware8sprite_exact=True,environment=e,
  scope='Exactly eight requested identities, seven Easy plus latest qualified BassHard. Fresh cold-menu discovery and independent directPPU replay sequentially. Original zero-death/CHR/completed-loop guards unchanged. No outcome/resource/physics/state injections. Existing known policies only; failed originals retained. No every-item/fullroster/fidelity/Hardmatrix/performance/adoption claim.')
 put(out/'readiness.json',proof);print(json.dumps(dict(passed=True,native_executed=False,bindings=len(bindings),ROM_sha256=SHA,readiness_sha256=sha(out/'readiness.json'),cases=cases),indent=2))
if __name__=='__main__':main()

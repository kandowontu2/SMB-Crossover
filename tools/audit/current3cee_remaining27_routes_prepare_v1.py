"""Prepare exactly27 frozen Easy policies; never start an emulator."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
NAMES=['mario','luigi','link','zelda2','simon','grant','sypha','alucard','pit','rygar','scrooge','darkwing','sophia','kirby','meta','mac','mike','mario3','luigi3','vic','octopus','twinbee','pentarou','leonardo','raphael','michelangelo','donatello']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def once(s,old,new):assert s.count(old)==1,old;return s.replace(old,new)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 parent=D/'current3cee-eight-routes-v1';candidate=D/'root-chip-hud-composed-v1';rom=candidate/'candidate.nes';assert sha(rom)==SHA and sha('C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes')==SHA
 old=get(parent/'readiness.json');assert all(sha(f)==h for f,h in old['bindings'].items())
 env=D/'parodius-menu3cee-ready-v1/environment.json';e=get(env)
 for n in['emulator','core','worker_settings','user_settings']:assert sha(e[n])==e[n+'_sha256'],n
 aggregate=D/'native-probes-qa-v2/full-roster-aggregate-v1/proof.json';original=get(aggregate);historical=D/'current8ff-roster-reconciled-v1/proof.json';h=get(historical);assert h['passed']
 selected=[]
 for name in NAMES:
  row=next(z for z in original['runs']if z['identity']==name and z['mode']=='easy').copy();f=Path(row['discovery']);m=get(f);assert m['result']['cleared']and m['result']['deaths']==0
  policy=f.parent/'policy.lua';assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(',policy.read_text())
  prior=next(z for z in h['runs']if z['identity']==name and z['mode']=='easy');assert prior['passed']and prior['replay']['passed']and sha(policy)==prior['source_policy_sha256']
  selected.append(row)
 put(out/'selected-aggregate.json',dict(passed=True,source_selection_only=True,runs=selected,parent_index_sha256=sha(aggregate),historical_8ff_qualified_controller_only=True))
 for n in['runner.py','capture.py']:(out/n).write_bytes((parent/n).read_bytes())
 c=(parent/'coordinator.py').read_text()
 for n in['runner.py','capture.py']:c=once(c,str(parent/n).replace('\\','\\\\'),str(out/n).replace('\\','\\\\'))
 c=once(c,repr(str(parent/'selected-aggregate.json')),repr(str(out/'selected-aggregate.json')))
 (out/'coordinator.py').write_text(c)
 for f in out.glob('*.py'):compile(f.read_text(),str(f),'exec')
 sys.path.insert(0,str(ROOT/'tools/audit'));spec=importlib.util.spec_from_file_location('remaining27_frozen_coordinator',out/'coordinator.py');co=importlib.util.module_from_spec(spec);spec.loader.exec_module(co);bundle=co.load(rom)
 preview=out/'expected-policies';preview.mkdir();native=out/'native';guard=native/'native-guard.lua';original_guard=D/'mmc3-static-call-v37/full-roster-v1/native-guard.lua'
 names=['OperMode','OperMode_Task','GameEngineSubroutine','WorldNumber','LevelNumber','Player_X_Position','Player_PageLoc','Player_Y_Position','ScreenLeft_X_Pos','ScreenLeft_PageLoc']
 delta=int(bundle['syms']['GameLoop']['size'],0)-1;offset=co.location(bundle,'GameLoop')+delta;assert bundle['raw'][offset]==0x60
 hook=dict(address=co.address(bundle,'GameLoop')+delta,physical_bank=(offset-16)//8192,bytes=list(bundle['raw'][offset:offset+8]))
 guard_text='OUTPUT=ROSTER_CONFIG.out\nMOTION_RAM='+co.lua({n:co.address(bundle,n)for n in names})+'\nMOTION_HOOK='+co.lua(hook)+'\nlocal checks,maxWorld,maxCamera='+original_guard.read_text().split('local checks,maxWorld,maxCamera=',1)[1]
 (preview/'native-guard.lua').write_text(guard_text);mapping=[]
 for row in selected:
  name=row['identity'];f=Path(row['discovery']);source=f.parent/'policy.lua';body=source.read_text();body=body.split('\n',1)[1]if body.startswith('dofile(')else body;bindings=[]
  def bind(match):
   symbol,oldaddr=match[1],int(match[2])
   if symbol not in bundle['syms']:return match[0]
   actual=co.address(bundle,symbol);bindings.append(dict(symbol=symbol,old=oldaddr,actual=actual));return 'L.'+symbol+'='+str(actual)
  body=re.sub(r'^L\.(\w+)=(\d+)\s*$',bind,body,flags=re.M)
  if name=='zelda2':body=co.stair_controller(body)
  planned=preview/(name+'-easy-policy.lua');planned.write_text('dofile('+co.lua(guard.as_posix())+')\n'+body)
  prior=next(z for z in h['runs']if z['identity']==name and z['mode']=='easy');priorpolicy=D/'current8ff-roster-v1'/(name+'-easy-policy.lua');priorbody=priorpolicy.read_text().split('\n',1)[1]
  assert body==priorbody,(name,'Unexpected policy body change versus already qualified8ff')
  mapping.append(dict(case=name+':easy',identity=name,actual_expected_numeric_mode=0,source_manifest=str(f),source_manifest_sha256=sha(f),source_policy=str(source),source_policy_sha256=sha(source),current_expected_policy=str(planned),current_expected_policy_sha256=sha(planned),actual_symbol_bindings=bindings,qualified_8ff_policy=str(priorpolicy),qualified_8ff_policy_sha256=sha(priorpolicy),controller_body_exact_8ff_after_path_rebinding=True,top_step_wrapper=name=='zelda2',prior_native_folder=prior['folder'],prior_replay=prior['replay']))
 put(out/'policy-map.json',mapping)
 cases=[n+':easy'for n in NAMES];command=[sys.executable,'-B',str(out/'coordinator.py'),'--rom',str(rom),'--archive',str(D),'--output',str(native),'--cases',*cases,'--replay','--frames','18000']
 report=ROOT/'docs/qa/current3cee-remaining27-readiness-2026-10-26.txt'
 lines=['Current3cee remaining27 ordinary1-1: SOURCE/PREPARATION ONLY','',f'ROM SHA256 {SHA}',f'External preparation {out}','Native launches: ZERO. A fresh explicit ROOT grant is required before the stable runner is used. One sequential worker maximum. All27 select actual numericEasy0; no Hard coverage is claimed.','', 'Exact policy mappings (all source policies and current generated previews have SHA256s in policy-map.json):']
 lines += [f"{z['identity']}: Easy0; {z['source_policy']}; SHA{z['source_policy_sha256']}; current preview SHA{z['current_expected_policy_sha256']}"+('; retained qualified ZeldaII top-step wrapper'if z['top_step_wrapper']else'')for z in mapping]
 lines += ['', 'All27 complete source controller bodies match their historical8ff passing discovery/replay controllers after isolated guard-path rebinding. RAM-symbol rebinding is recorded; ZeldaII retains the previously qualified stair wrapper. This reuses a historical control, not historical gameplay results on3cee. Fresh discovery and independent directPPU replay remain required.', 'Frozen coordinator instruction/control logic, runner and direct capture bytes are unchanged from the completed8route pipeline; only paths and selected-case index differ. Current generated policies and completed-loop guard are previewed/hash-bound before launch. Original zero-death/real1-1to1-2/completed-loop/bodyCHR/input/replay assertions remain. No outcome/resource/RNG/tier/position injection or settings/production edit.', 'Hardware8sprite, RAMAllZeros/nonrandom/no-save/adaptiveoff/runahead0/noextraPPUlines runtime is bound in the environment. Actual mode readback is required by existing menu guard; trace.mode alone is not difficulty evidence.', 'All originals and failures must remain. A failure does not authorize an automatic retry or a source fix. Any later controller correction requires actual evidence and a separate packet. Captures/lossless archives remain external.', 'Scope remains27 named identities in this unit, not everyitem/allmode/audio/flicker/sourcefidelity/fullroster completion. Existing route observer does not provide a complete5SMC/SP/NMI ownership oracle. Original Parodius areaFALSE/Buffer2-overlap and mixed bodyvisibility limits remain independent.', '', 'Stable one-shot command (not yet authorized to run):', f'python -B tools/audit/current3cee_remaining27_routes_run_v1.py --packet "{out}" --native-grant']
 report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 dependencies={rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),candidate/'proof.json',candidate/'source-manifest.json',aggregate,historical,env,Path(__file__),ROOT/'tools/audit/current3cee_remaining27_routes_run_v1.py',report,original_guard,parent/'readiness.json'}
 for rel,v in get(candidate/'source-manifest.json').items():f=candidate/'source'/rel;assert sha(f)==v;dependencies.add(f)
 for z in mapping:
  dependencies|={Path(z[n])for n in['source_manifest','source_policy','current_expected_policy','qualified_8ff_policy']}
  dependencies|={Path(z['prior_native_folder'])/'manifest.json',Path(z['prior_replay']['folder'])/'proof.json'}
 for n in['emulator','core','worker_settings','user_settings']:dependencies.add(Path(e[n]))
 extra=['tools/audit/current_roster_recheck_routes.py','tools/audit/check_tmnt_render_oa.py','tools/audit/observe_chip_committed_write.py','tools/audit/run_mesen_isolated.py','tools/run_mesen.py','tools/playthroughs/roster_harness.lua','tools/playthroughs/roster_audit.lua','tools/audit/legacy_chr_observer_of.lua','tools/audit/chr_commit_observer.lua','tools/audit/roll_render_observer.lua']
 dependencies|={ROOT/n for n in extra}|{parent/n for n in['runner.py','capture.py','coordinator.py']}|{f for f in out.iterdir()if f.is_file()}|{preview/'native-guard.lua'}
 b={str(f.resolve()):sha(f)for f in sorted(dependencies,key=str)}
 q=dict(passed=True,native_executed=False,native_grant=False,ROM_sha256=SHA,native_workers=1,cases=cases,command=command,bindings=b,environment=e,policy_map_sha256=sha(out/'policy-map.json'),generated_policy_previews_match_historical_8ff_bodies=True,expected_native_guard_sha256=sha(preview/'native-guard.lua'),coordinator_paths_and_case_index_only_changed=True,runner_capture_byte_exact=True,source_report_sha256=sha(report),scope='Exactly27Easy source-prepared existing policies; no native run or result reuse. Preserve all runtime/mode/completed-loop/CHR/replay/lossless guards and all original failures.')
 put(out/'readiness.json',q);print(json.dumps(dict(passed=True,native_executed=False,profiles=len(cases),bindings=len(b),readiness=str(out/'readiness.json'),readiness_sha256=sha(out/'readiness.json'),policy_map_sha256=sha(out/'policy-map.json'),report_sha256=sha(report)),indent=2))
if __name__=='__main__':main()

"""Freeze one unrun clean-menu1800 fixture; never grant or launch native work."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil,sys
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','source-ready','preparation','static','dma-mock','timing-mock','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--expected-sha256',required=True);p.add_argument('--preflight',type=Path)
 a=p.parse_args();P=a.candidate;SHA=a.expected_sha256;a.output.mkdir(parents=True,exist_ok=False)
 assert not a.output.resolve().is_relative_to(R)
 z=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(z['script']);assert z['ROM_sha256']==SHA and sha(script)==z['script_sha256']and sha(script.with_name('candidate.nes'))==SHA
 assert not(script.parent/'launch.json').exists()and not(script.parent/'native-result.json').exists()
 assert z['original3cee_shot_source_exact']and z['no_MM_PROTO_SHOT_MUX_segment']
 st,dm,tm=[json.loads((f/'proof.json').read_text())for f in[a.static,a.dma_mock,a.timing_mock]]
 for q in [st,dm,tm]:assert q['passed']and not q['native_run']and q['ROM_sha256']==SHA and q['script_sha256']==sha(script)
 assert(st['memory_callbacks'],st['complete_generated_mock_frames'],st['timing_finalizer_event_index'],st['additional_finalizer_event_index'],st['original_stop_event_index'])==(73,439,1,5,6)
 assert dm['cases']==38 and dm['intentional_rejections']==34 and dm['E005_no_completion_and_E008_after_LDA_before_enable']
 assert tm['cases']==35 and tm['intentional_rejections']==26 and tm['ROOT_preflight_deadline_predicate_exact']
 assert z['config_deltas']==['ROM_sha256','output','early_timing']and z['changed_hook_count']==0
 files=set()
 for path,h in z['dependencies'].items():assert sha(path)==h,path;files.add(Path(path))
 for path,h in json.loads((P/'source-manifest.json').read_text()).items():assert sha(P/'source'/path)==h;files.add(P/'source'/path)
 for folder in [a.preparation,a.static,a.dma_mock,a.timing_mock]:files.update(f for f in folder.rglob('*')if f.is_file())
 for f in P.iterdir():
  if f.is_file():files.add(f)
 files.add(a.source_ready)
 source=json.loads(a.source_ready.read_text());assert source['passed']and not source.get('native_run',False)
 if isinstance(source.get('bindings'),dict):
  for n,h in source['bindings'].items():
   expected=h['sha256']if isinstance(h,dict)else h
   assert sha(n)==expected,n;files.add(Path(n))
 adjacent=a.source_ready.parent/'manifest.json'
 if adjacent.is_file():
  if 'manifest_sha256'in source:assert sha(adjacent)==source['manifest_sha256']
  files.add(adjacent)
  for n,h in json.loads(adjacent.read_text()).items():
   expected=h['sha256']if isinstance(h,dict)else h
   assert sha(n)==expected,n;files.add(Path(n))
 catalog=a.source_ready.parent/'catalog.json'
 if catalog.is_file():
  assert sha(catalog)==source['catalog_sha256'];files.add(catalog)
  for n,h in json.loads(catalog.read_text()).items():
   expected=h['sha256']if isinstance(h,dict)else h
   assert sha(n)==expected,n;files.add(Path(n))
  files.update(f for f in a.source_ready.parent.iterdir()if f.is_file())
 # Bind every file in the clean freeze's own declared manifest if present.
 for key in ['manifest','manifest_path']:
  if key in source and isinstance(source[key],str):
   f=Path(source[key])
   if f.exists():files.add(f)
 runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';exe=runtime/'Mesen.exe';core=runtime/'MesenCore.dll';worker=runtime/'settings.json';user=Path('C:/Mesen2/settings.json')
 settings=json.loads(worker.read_bytes().decode('utf-8-sig'));names=['Region','DisableSprites','DisableBackground','RemoveSpriteLimit','AdaptiveSpriteLimit','RandomizeMapperPowerOnState','RandomizeCpuPpuAlignment','RamPowerOnState','PpuExtraScanlinesBeforeNmi','PpuExtraScanlinesAfterNmi'];effective={n:settings['Nes'][n]for n in names};effective['RunAheadFrames']=settings['Emulation']['RunAheadFrames']
 assert all(effective[k]==v for k,v in dict(Region='Auto',DisableSprites=False,DisableBackground=False,RemoveSpriteLimit=False,AdaptiveSpriteLimit=False,RandomizeMapperPowerOnState=False,RandomizeCpuPpuAlignment=False,PpuExtraScanlinesBeforeNmi=0,PpuExtraScanlinesAfterNmi=0,RunAheadFrames=0).items())
 env=dict(emulator=str(exe),emulator_sha256=sha(exe),core=str(core),core_sha256=sha(core),worker_settings=str(worker),worker_settings_sha256=sha(worker),user_settings=str(user),user_settings_sha256=sha(user),persisted_worker_conditions=effective,actual_command_overrides=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 (a.output/'environment').mkdir();shutil.copy2(worker,a.output/'environment/worker-settings.json');shutil.copy2(user,a.output/'environment/user-settings.json');put(a.output/'environment.json',env)
 files.update([exe,core,worker,user]);files.update(runtime.glob('*.dll'));files.add(Path(sys.executable))
 for folder in [D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1',D/'final-tmnt-items-v1/lua-parser-deps-v1']:
  files.update(f for f in folder.rglob('*')if f.is_file()and'__pycache__'not in f.parts)
 context=[D/'parodius-menu-budget-c9-source-ready-v1/proof.json',D/'parodius-menu-budget-c9-source-ready-v1/manifest.json',D/'parodius-menub0-native-final-v1/proof.json',D/'parodius-menu3cee-native-final-v1/proof.json',D/'parodius-menu3cee-native-final-v1/manifest.json',D/'root-presentation450-59-v1/ROOT-review-v1/proof.json']
 for f in context:assert f.is_file();files.add(f)
 preflight=None
 if a.preflight:
  preflight=json.loads(a.preflight.read_text());assert preflight['passed']and preflight['ROM_sha256']==SHA and preflight['native_run'];files.add(a.preflight)
  files.update(f for f in a.preflight.parent.iterdir()if f.is_file())
  if isinstance(preflight.get('bindings'),dict):
   for n,h in preflight['bindings'].items():
    expected=h['sha256']if isinstance(h,dict)else h
    assert sha(n)==expected,n;files.add(Path(n))
 pending=list((R/'tools/audit').glob('parodius_visibility_menu_clean_*.py'))+[R/'tools/audit'/n for n in ['parodius_visibility_menu59_prepare_v1.py','parodius_visibility_menu59_prepare_v2.py','parodius_visibility_menu59_static_v1.py','parodius_visibility_menu59_timing_mock_v1.py','parodius_visibility_menu59_timing_v1.lua','parodius_visibility_menu59_timing_v2.lua','parodius_visibility_menub0_dma_mock_v1.py','presentation_timing_preflight_v1.lua','parodius_visibility_run.py','run_mesen_isolated.py']]
 seen=set()
 while pending:
  f=pending.pop()
  if f in seen:continue
  seen.add(f);files.add(f)
  if f.suffix!='.py':continue
  for node in ast.walk(ast.parse(f.read_text(encoding='utf-8-sig'))):
   mods=[node.module]if isinstance(node,ast.ImportFrom)else[q.name for q in node.names]if isinstance(node,ast.Import)else[]
   for name in mods:
    if name:
     dep=R/'tools/audit'/(name.split('.')[0]+'.py')
     if dep.is_file():pending.append(dep)
 command='python -B tools/audit/parodius_visibility_menu_clean_run_v1.py --ready "'+a.output.as_posix()+'" --profile menu --native-grant'
 report=R/'docs/qa/parodius-menu-clean-timing-source-2026-10-26.txt';assert not report.exists()
 report.write_text(f'''Clean menu/NMI all-four-variant menu1800 source readiness, 2026-10-26

PREPARED ONLY; no grant, native launch, adoption or production/settings edit.
Candidate {SHA}
Candidate/source {P}
Preparation {a.preparation}
Ready {a.output}
Source freeze {a.source_ready} SHA{sha(a.source_ready)}

Same qualified3cee/b0 all4variant Easy0 menu1800 controller: cancel/title/reentry,
current-generation publication, actual physical OAM/CHR, HUD5376pixel references,
IRQ31,5SMC/banks/stack, scroll, init-owner and all-life HUD/font pairs remain.
The complete original generated tail normalizes byte-exact after isolated-path
substitution. No input policy, outcome, resource, art or SRAM setup is changed.
Actual clean source restores original3cee shots/removes MM_PROTO_SHOT_MUX only.
The intentional static20cell SELECT ALTERNATES legend is the source-qualified
product change; all other native name/cursor/palette/preview values remain.

Actual E005 eight-byte sequence and E008 completion protocol remain exact.
Original6 semantic components are still mandatory; unchanged original observer
body mocks pass38cases/34rejections. Full generated startup executes439inactive
mock epochs with73callbacks, no runtime registration/removal. Dispatcher last.
Finalizer order: additive timing slot1, pair slot5, original stop slot6.

Added module is READ ONLY and ungated by character/wall threshold: every real
DMA source256/data-writecount/physicalhardware256 at E008, every render-enable
stamp, actual NMI/parser packet ownership, menu start-frame t/v/fineX/w plus
4096NT/12CHR/32palette/256physicalOAM. Scoped enables use exactly ROOT's native
preflight deadline: lines241..260 or pre-render<=274. Meaningful final counts
are mandatory, not silent sampling. Synthetic module checks35cases/26negative
controls, including bad bytes/counts/physicaldata/late enable and snapshot shape.
No mock state/counter setters are present in the prepared native fixture.

This is not a whole-background pixel oracle. After any separately granted run,
actual menu pixels outside physical OAM rectangles and the authorized20cell
legend region must be compared to3cee only when NT/name/cursor ownership is
matched. Otherwise every changed whole-menu frame needs agent image review.
Timing assertions and six mechanical component passes alone cannot clear the
previous b0 visualFAIL. All1651 existing actual full-frame captures150..1800
remain enabled, with actual hardware/source snapshots for owner attribution.

ROOT's old59 Mega450 is prototype context only; no retagging to clean candidate.
Clean preflight bound: {a.preflight if a.preflight else 'NOT YET BOUND; ROOT review/grant required'}.
Current exact source/CPU packets retain full caller/PPU/control limits, material
highlightforeground+4197CPU,0..619NMI savings and no universal DMC/campaign claim.
The1481 helper-boundary NMI controls use the real GameLoop-private FF lag/audio
path (GameLoop sets FF until PauseSkip publishes0). Separate1368+74 complete
normal NMI/PPU cases execute after publication; these scopes are not conflated.
OriginalareaFALSE/natural pendingBuffer2 overlap, body starvation/readability,
tinyfont limitations and b0 seven wrap frames remain immutable and explicit.

Runtime Mesen {env['emulator_sha256']}
Core {env['core_sha256']}
Worker {env['worker_settings_sha256']}
User context {env['user_settings_sha256']}
No config writes; isolated portable worker, AllZeros/nonrandom/doNotSave,
hardware8sprites/adaptiveoff/noextraPPUlines/runahead0 retained.

ONE-SHOT COMMAND, DO NOT RUN UNTIL ROOT REVIEWS AND GRANTS:
{command}
Missing any original6 or additive timing output remains FALSE; no retry,
death/area/Hard matrix or controller/source optimization is authorized.
''',encoding='utf-8')
 files.add(report)
 put(a.output/'review-files.json',{str(f.resolve()):sha(f)for f in sorted(seen|{report},key=str)})
 files.update(f for f in a.output.rglob('*')if f.is_file());manifest={str(f.resolve()):sha(f)for f in sorted(files,key=str)};put(a.output/'manifest.json',manifest)
 proof=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,clean_original_shots_required=True,
  profiles=[dict(kind='menu',limit=1800,actual_mode_required=0,actual_variant_required=1,packet=str((a.preparation/'menu').resolve()),preparation_sha256=sha(a.preparation/'menu/preparation.json'),script_sha256=sha(script))],
  required_native_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],additional_required_native_components=['menu-timing-native-result.json'],
  original_controller_and_six_guards_exact=True,all131_bodies_RAM_HUDfont5376references_exact=True,ungated_early_timing_and_actual_menu_owner_snapshots=True,whole_BG_pixel_oracle_exists=False,
  source_readiness_sha256=sha(a.source_ready),static_proof_sha256=sha(a.static/'proof.json'),DMA_mock_sha256=sha(a.dma_mock/'proof.json'),timing_mock_sha256=sha(a.timing_mock/'proof.json'),clean_native_preflight_sha256=sha(a.preflight)if a.preflight else None,
  environment=env,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),review_files_sha256=sha(a.output/'review-files.json'),stable_command=command,
  limits='Source readiness ONLY. No native grant/run, retry, profile/mode/area/death/campaign or adoption. Mechanical components alone cannot clear wholeBG visualFAIL; actual owner-bound wholemenu image review required. OriginalareaFALSE/Buffer2 overlap, mixed bodyvisibility/tinyfont/globalDMC limits retained.')
 put(a.output/'proof.json',proof)
 for n,h in manifest.items():assert sha(n)==h,n
 print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(manifest),script_sha256=sha(script),report_sha256=sha(report),stable_command=command),indent=2))
if __name__=='__main__':main()

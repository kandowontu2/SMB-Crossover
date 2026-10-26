"""Freeze one unrun b0 menu1800 fixture, exact source/current runtime and protocol mocks."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'mm-proto-postdma-composed-v1'
SHA='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','static','dma-mock','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']and sha(script.with_name('candidate.nes'))==SHA and not(script.parent/'launch.json').exists()and not(script.parent/'native-result.json').exists()
 st=json.loads((a.static/'proof.json').read_text());dm=json.loads((a.dma_mock/'proof.json').read_text())
 for q in [st,dm]:assert q['passed']and not q['native_run']and q['ROM_sha256']==SHA and q['script_sha256']==sha(script)
 assert st['memory_callbacks']==67 and st['complete_generated_mock_frames']==439 and st['additional_finalizer_event_index']==4 and st['original_stop_event_index']==5
 assert dm['cases']==38 and dm['intentional_rejections']==34 and dm['E005_no_completion_and_E008_after_LDA_before_enable']
 assert z['config_deltas']==['ROM_sha256','hooks','output','dma_protocol']and z['changed_hook_count']==1
 files=set()
 for name in ['catalog.json','dependencies.json']:
  f=P/'ready-v1'/name;files.add(f)
  for path,h in json.loads(f.read_text()).items():assert sha(path)==h,path;files.add(Path(path))
 for path,h in json.loads((P/'source-manifest.json').read_text()).items():assert sha(P/'source'/path)==h;files.add(P/'source'/path)
 for path,h in z['dependencies'].items():assert sha(path)==h,path;files.add(Path(path))
 for folder in [a.preparation,a.static,a.dma_mock]:files.update(f for f in folder.rglob('*')if f.is_file())
 runtime=D/'mmc3-flag-fix-v23/script-budget-probe-v2/emulator';exe=runtime/'Mesen.exe';core=runtime/'MesenCore.dll';worker=runtime/'settings.json';user=Path('C:/Mesen2/settings.json')
 settings=json.loads(worker.read_bytes().decode('utf-8-sig'));wanted=['Region','DisableSprites','DisableBackground','RemoveSpriteLimit','AdaptiveSpriteLimit','RandomizeMapperPowerOnState','RandomizeCpuPpuAlignment','RamPowerOnState','PpuExtraScanlinesBeforeNmi','PpuExtraScanlinesAfterNmi'];effective={k:settings['Nes'][k]for k in wanted};effective['RunAheadFrames']=settings['Emulation']['RunAheadFrames']
 assert all(effective[k]==v for k,v in dict(Region='Auto',DisableSprites=False,DisableBackground=False,RemoveSpriteLimit=False,AdaptiveSpriteLimit=False,RandomizeMapperPowerOnState=False,RandomizeCpuPpuAlignment=False,PpuExtraScanlinesBeforeNmi=0,PpuExtraScanlinesAfterNmi=0,RunAheadFrames=0).items())
 env=dict(emulator=str(exe),emulator_sha256=sha(exe),core=str(core),core_sha256=sha(core),worker_settings=str(worker),worker_settings_sha256=sha(worker),user_settings=str(user),user_settings_sha256=sha(user),persisted_worker_conditions=effective,actual_command_overrides=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
 (a.output/'environment').mkdir();shutil.copy2(worker,a.output/'environment/worker-settings.json');shutil.copy2(user,a.output/'environment/user-settings.json');put(a.output/'environment.json',env)
 files.update([exe,core,worker,user]);files.update(runtime.glob('*.dll'))
 for folder in [D/'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1',D/'final-tmnt-items-v1/lua-parser-deps-v1']:
  files.update(f for f in folder.rglob('*')if f.is_file()and'__pycache__'not in f.parts)
 bound_context=[P/'ready-v1/receipt.json',P/'source-manifest.json',D/'parodius-menu3cee-native-final-v1/proof.json',D/'parodius-menu3cee-native-final-v1/manifest.json',D/'root-postdma-b0-hard1f-v1/ROOT-review.json',D/'current3cee-postdma-mask-v1/canonical-v2/proof.json',D/'current3cee-postdma-mask-v1/NMI-CPU-v4/proof.json']
 for f in bound_context:assert f.exists(),f;files.add(f)
 # Preserve all three source-tool failures separately from ROM/native evidence.
 failure_paths=[]
 for name in ['parodius-menub0-preparation-v1','parodius-menub0-preparation-v2','parodius-menub0-static-v1']:
  folder=D/name;files.update(f for f in folder.rglob('*')if f.is_file());failure_paths.append(str(folder))
 put(a.output/'source-failure-ledger.json',dict(source_only=True,native_run=False,failures=failure_paths,game_defect=False,notes=['First source-prep whole-bank116 claim omitted genuine relocated JMP operand C05052->58; corrected exact source delta.', 'Second source-prep opcode check expected JSR instead of actual JMP4C; corrected without observer/native emission.', 'First static attempt used nonexistent historical lupa root; corrected to already-pinned existing dependency.']))
 put(a.output/'static-wording-erratum.json',dict(source_only=True,native_run=False,frozen_static_proof_sha256=sha(a.static/'proof.json'),field='all_original_native_scroll_HUD_bridge_guard_bodies_exact',meaning='The static tool checks full exact bodies of the explicitly declared new postDMA observers, plus original scroll/HUD. Original transfer semantics remain full256/source equality/count/visible/body/stack/bank predicates; old LDX two-byte ABI alone is replaced by exact actual eight-byte sequence and E008 completion. This is not a claim the old and new observer text is identical.',new_protocol_mock_sha256=sha(a.dma_mock/'proof.json')))
 report=R/'docs/qa/parodius-menub0-source-2026-10-26.txt'
 command='python -B tools/audit/parodius_visibility_menub0_run_v1.py --ready "'+a.output.as_posix()+'" --profile menu --native-grant'
 report.write_text(f'''b0 all-four-variant menu1800 source readiness, 2026-10-26

PREPARED ONLY. No native grant, emulator launch, production/default/settings
change or adoption. Exactly one separately authorized Easy0 menu1800 run is
prepared on {SHA}.
Candidate/source: {P}
Preparation: {a.preparation}
Static: {a.static}
Transfer protocol mocks: {a.dma_mock}
Ready: {a.output}

This is the same qualified current3cee all4variant menu/cancel/title/reentry
controller, body metadata and six semantic guard layers. No outcome/state,
resource, input-policy or source-art mutation occurs. Config changes are ROM,
isolated output, one real moved NonMaskableInterrupt entry E336->E33C, and
the explicit new transfer protocol. The old public and body aliases are not
faked: parent moved-symbol/layout receipt separately discloses58 real+6 moves.
All131 body source records, all RAM, three3072-byte HUD fonts,84cell bytes,
all5376foreground/backdrop reference pixels and CHR remain actual/exact.

The old observer assumed LDX#1 immediately after STA4014. The new assembled
sequence is E005: AD7A078D0120A201 (LDA Mirror_PPUMASK; STA2001; LDX#1).
Mesen execE005 is before DMA halt. Completion MUST occur at genuine E008,
after actual LDA and before STA2001. Both live and init observer closures now
require exact PC/eight-byte sequence,256actual writes, complete256hardware
identity to the immutable publication and rendering disabled at start and
completion. Pending/wrong-bank semantics, visible epoch/generation, body-row,
source-CHR/actual mapper, IRQ31,5SMC/stack/font/palette assertions remain.
Only these declared observer protocol hunks and isolated paths differ; reverse
normalization proves the entire generated original tail/controller exact.
No runtime host callback registration/removal is introduced.

Full script parsed;439inactive source-mock epochs execute with67callbacks,
full-range static return dispatcher last and pair-finalizer slot4 before
original stop slot5. Insufficient scope rejects, sufficient mock scope emits,
nonterminal does not emit. Both actual new transfer callback bodies pass38
finite mock cases (34intentional rejections): each of8wrong bytes, wrongPC,
wrong256count, first/middle/last hardware corruption, premature rendering,
and wrong-bank deferral. Synthetic mocks are absent from native fixture.
The old static proof's broad exact-body field is clarified additively; it
means current declared bodies, not an unmodified old two-byte DMA protocol.
Three prelaunch source-tool failures remain immutable and are not game bugs.

ROOT's separately frozen900 CPU controls and b0 HeavyDMC Hard1F240 results
are bound context, not this unrun menu verdict. ROOT reports893wholeNMI,
512input,442IRQ controls with0cycle delta; postDMA pair bootstrap fixes the
actual184title transfer. The current b0 Hard1F packet reports240updates,
168completed draws, full256hardware and native source/APU/IRQ/bank/stack
controls. None proves this all4variant menu or universal late-NMI safety.

Runtime is rebound now without modifying actual or copied settings:
Mesen {env['emulator_sha256']}
Core {env['core_sha256']}
Worker {env['worker_settings_sha256']}
User context {env['user_settings_sha256']}
AllZeros/nonrandom/doNotSave overrides, real hardware8sprite limit, adaptive
off, noextraPPUlines/runahead0 retained. No worker is launched or reserved.

Required future native files (all six required; missing stays FALSE):
native-result.json, hud-native-result.json, scroll-native-result.json,
lifecycle-native-result.json, lifecycle-init-native-result.json,
hud-lease-native-result.json. Original all4variants/cancel/title/reentry,
current-generation/font/CHR/OAM/IRQ/stack conditions stay mandatory.
No automatic retry, Hard/death/area/overlap/campaign/native broadening.
OriginalareaFALSE/missing natural pendingBuffer2 overlap, mixed body-starvation
visibility, tinyfont/readability and source-vs-published-fairness limits stay
open and are not relabeled by the title repair or this source preparation.

ONE-SHOT command, DO NOT RUN until ROOT reviews/grants:
{command}
''',encoding='utf-8')
 tools=[R/'tools/audit'/n for n in ['parodius_visibility_menub0_prepare_v1.py','parodius_visibility_menub0_prepare_v2.py','parodius_visibility_menub0_prepare_v3.py','parodius_visibility_postdma_static_observer_v1.lua','parodius_visibility_postdma_bridge_v1.lua','parodius_visibility_menub0_static_v1.py','parodius_visibility_menub0_dma_mock_v1.py','parodius_visibility_menub0_ready_v1.py','parodius_visibility_menub0_run_v1.py']]
 files.update(tools);files.add(report);put(a.output/'review-files.json',{str(f.resolve()):sha(f)for f in tools+[report]})
 files.update(f for f in a.output.rglob('*')if f.is_file());manifest={str(f.resolve()):sha(f)for f in sorted(files,key=str)};put(a.output/'manifest.json',manifest)
 q=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,parent_ROM_sha256='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99',profiles=[dict(kind='menu',limit=1800,actual_mode_required=0,actual_variant_required=1,packet=str((a.preparation/'menu').resolve()),preparation_sha256=sha(a.preparation/'menu/preparation.json'),script_sha256=sha(script))],required_native_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],all_original_policy_controller_and_guard_bodies_exact_except_declared_DMA_ABI=True,all131body_records_and_actual_current_HUD_art_exact=True,full5376_HUDpixel_positions_including_backdrop_retained=True,E008_completed_transfer_before_render_enable=True,original3cee_menu_final_sha256=sha(bound_context[2]),composition_readiness_sha256=sha(P/'ready-v1/receipt.json'),static_proof_sha256=sha(a.static/'proof.json'),protocol_mock_sha256=sha(a.dma_mock/'proof.json'),environment=env,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),review_files_sha256=sha(a.output/'review-files.json'),stable_command=command,limits='Source readiness ONLY. No native launch, grant, retry, otherprofile/mode/area/death/campaign or adoption. OriginalareaFALSE/Buffer2overlap, mixed bodyvisibility/tinyfont and broad lateNMI/DMC limits retained.')
 put(a.output/'proof.json',q);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(manifest),script_sha256=sha(script),report_sha256=sha(report),runner_sha256=sha(tools[-1]),stable_command=command),indent=2))
if __name__=='__main__':main()

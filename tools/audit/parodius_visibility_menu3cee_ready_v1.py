"""Freeze unrun3cee menu preparation/static observer/runtime bindings for review."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SHA='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['candidate','preparation','static','parent-final','environment-ready','failed-preparation','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 cp=json.loads((a.candidate/'proof.json').read_text());assert cp['passed']and cp['candidate_ROM_sha256']==SHA and sha(a.candidate/'candidate.nes')==SHA
 files={a.candidate/'proof.json',a.candidate/'source-manifest.json'}
 for rel,h in json.loads((a.candidate/'source-manifest.json').read_text()).items():
  f=a.candidate/'source'/rel;assert sha(f)==h;files.add(f)
 z=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']and sha(script.with_name('candidate.nes'))==SHA
 assert z['original_controller_all6guards_finalizer_order_exact_after_path_normalization']and z['exact_compiled_font_and84cell_table_bound']
 assert z['config_only_deltas']==['ROM_sha256','output','hud_labels']
 assert not(script.parent/'lifecycle-proof.json').exists()and not(script.parent/'native-result.json').exists()
 for f,h in z['dependencies'].items():assert sha(f)==h;files.add(Path(f))
 files|={f for f in a.preparation.rglob('*')if f.is_file()}
 st=json.loads((a.static/'proof.json').read_text());assert st['passed']and not st['native_run']and st['ROM_sha256']==SHA and st['script_sha256']==sha(script)
 assert st['additional_finalizer_event_index']==4 and st['original_stop_event_index']==5 and st['memory_callbacks']==67
 files|={f for f in a.static.rglob('*')if f.is_file()}
 art=json.loads((a.preparation/'expected-hud-art.json').read_text());assert art['full_pixel_reference_positions']==5376 and art['backdrop_pixels_included']and art['mask_predicate_not_weakened']
 assert len((a.preparation/'expected-all5376-HUD-pixels.bin').read_bytes())==5376
 env=json.loads((a.environment_ready/'environment.json').read_text());ed=a.output/'environment';ed.mkdir()
 for name in ['emulator','core','worker_settings','user_settings']:
  f=Path(env[name]);assert sha(f)==env[name+'_sha256'],('Runtime changed; fresh binding required',name);files.add(f)
  if name.endswith('settings'):shutil.copy2(f,ed/(name+'.json'))
 put(a.output/'environment.json',env)
 failure=dict(source_only=True,native_run=False,game_defect=False,preserved_tool=str(a.failed_preparation/'failed-tool.py'),preserved_tool_sha256=sha(a.failed_preparation/'failed-tool.py'),
  failure="Initial preparation assumed semantic hook alias NmiReturn was a standalone compiled label; KeyError before generated fixture. Corrected source check retains exact actual bank/address/opcode bytes for all hooks, and requires exact symbol values where real labels exist. No native assertion or observer guard changed.")
 put(a.output/'preserved-preparation-failure.json',failure);files.add(a.failed_preparation/'failed-tool.py')
 report=ROOT/'docs/qa/parodius-menu3cee-source-2026-10-26.txt'
 report.write_text(f'''Unrun composed3cee Parodius menu1800 readiness, 2026-10-26

SOURCE/STATIC READY ONLY. No Mesen launch, native grant, production/settings
mutation or adoption. ROOT's composed ROM is {SHA}.
Frozen candidate/source: {a.candidate}
Preparation: {a.preparation}
Ready: {a.output}

The same passed6c69 Easy0/Octopus1 menu1800 fixture is rebound. Only three
configuration fields change: ROM_sha256, isolated output path, and hud_labels
from the actual compiled new84-byte PnHudCells table. Complete controller,
input policy, all six guard bodies, terminal phase, finalizer order, real
hardware eight-sprite limit, pending-bank/stack/SMC/CHR/IRQ/DMA assertions,
all131 source-body records and all hook opcodes/addresses stay exact.
The entire generated tail is byte-exact after isolated-path normalization.
No emulated write/setState/loadSavestate/reset call is added.

Actual current pages396..398 match the reviewed positive-letter3072byte font
d278c3e3f04aa95504099d6f4b6d4ffc932e745c2c8045b7227763b493fba2d0.
All3x1792HUD pixel positions, including every backdrop/zero pixel, are in the
separate source reference. Labels/font pages derive from actual current ROM
and frozen source; no pixel deletion/exclusion or weaker native mask is used.
Current palette values remain actual runtime observations combined with the
unchanged attributes. Source-art equality/mismatch checks are source controls,
not emulated publication or a new actual capture. A later native RGB review
must compare all224x8pixels against current fonts and actual observed palette.

Complete generated Lua parser and439inactive startup/mock frames PASS.
67 static callbacks; full0..FFFFreturn dispatcher registered last; zero runtime
registration/removal attempts. All original guard bodies remain exact.
Sixth pair finalizer endFrame slot4 precedes original stop slot5. Insufficient
pair scope rejects, sufficient mock scope writes at terminal, nonterminal does
not finalize. These synthetic source counters are absent from native script.

The first preparation attempt's false standalone NmiReturn-symbol assumption
is retained separately. This hook is a semantic alias inside actual assembled
code; its original bank/address/opcode evidence stays mandatory. It was a
source-tool KeyError, never a game defect or native run.

Runtime/context actual hashes checked afresh without changes:
Mesen {env['emulator_sha256']}
Core {env['core_sha256']}
Portable worker settings {env['worker_settings_sha256']}
User context settings {env['user_settings_sha256']}
Original command overrides AllZeros/nonrandom/doNotSaveSettings, hardware8sprite
limit; zero extra PPU lines/runahead0/adaptiveoff conditions are retained.

Still requires one separately granted current3cee native menu1800 run with all
four variants, cancel/title/reentry, current-generation font/CHR/OAM/IRQ/stack
and all six result components. No death/area/Hard/otherprofile broadening.
Original areaFALSE/missing natural Buffer2 overlap and body visibility remain
unchanged. Positive font remains small and actual play readability unqualified.

Stable one-shot command, DO NOT RUN without ROOT grant:
python -B tools/audit/parodius_visibility_menu3cee_run_v1.py --ready "{a.output}" --profile menu --native-grant
''',encoding='utf-8')
 tools=[ROOT/'tools/audit'/n for n in ['parodius_visibility_menu3cee_prepare_v1.py','parodius_visibility_menu3cee_ready_v1.py','parodius_visibility_menu3cee_run_v1.py','parodius_visibility_menu4285_static_v1.py','parodius_visibility_hud_static_startup_v1.py','parodius_visibility_hud_cancel_observer_cpu_v1.py','parodius_visibility_menu_hint_observer_cpu_v3.py','link_pit_rygar_sophia_audit_cpu.py','check_tmnt_render_oa.py','check_nmi_vram_fast_cpu_v1.py','final_roll_items_prepare.py']]
 files.update(tools);files.add(report);files|={a.parent_final/'proof.json',a.parent_final/'manifest.json'}
 owned=tools[:3]+[report];put(a.output/'review-files.json',{str(f.resolve()):sha(f)for f in owned})
 files|={f for f in a.output.rglob('*')if f.is_file()};manifest={str(f.resolve()):sha(f)for f in sorted(files,key=str)};put(a.output/'manifest.json',manifest)
 result=dict(prepared=True,source_checks_passed=True,native_run=False,native_granted=False,goal_complete=False,ROM_sha256=SHA,
  profiles=[dict(kind='menu',limit=1800,actual_mode_required=0,actual_variant_required=1,packet=str((a.preparation/'menu').resolve()),preparation_sha256=sha(a.preparation/'menu/preparation.json'),script_sha256=sha(script))],
  required_native_components=['native-result.json','hud-native-result.json','scroll-native-result.json','lifecycle-native-result.json','lifecycle-init-native-result.json','hud-lease-native-result.json'],
  composition_proof_sha256=sha(a.candidate/'proof.json'),parent_passed6c69_menu_final_sha256=sha(a.parent_final/'proof.json'),source_static_proof_sha256=sha(a.static/'proof.json'),
  original_controller_all6guards_finalizer_order_exact=True,all131body_records_and_genuine_hook_bytes_exact=True,actual_current_font_and_cell_table_bound=True,
  full5376_HUDpixel_positions_including_backdrop_retained=True,source_art_reference_sha256=sha(a.preparation/'expected-hud-art.json'),
  environment=env,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),review_files_sha256=sha(a.output/'review-files.json'),
  stable_command='python -B tools/audit/parodius_visibility_menu3cee_run_v1.py --ready "'+a.output.as_posix()+'" --profile menu --native-grant',
  limits='Unrun source/static readiness only; no actual/native pass or new grant. Same menu1800 only; no retries/death/area/Hard/body/global/audio/adoption claim. OriginalareaFALSE/Buffer2overlap and visibility limitations remain.')
 put(a.output/'proof.json',result);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(manifest),script_sha256=sha(script),report_sha256=sha(report),runner_sha256=sha(tools[2])),indent=2))
if __name__=='__main__':main()

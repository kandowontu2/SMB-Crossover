"""Freeze bounded clean731 native/agent-visual evidence and compact checkpoint."""
from pathlib import Path
import argparse,hashlib,json,shutil
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SHA='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.resolve().is_relative_to(R);a.output.mkdir(parents=True,exist_ok=False)
 run=D/'parodius-menu-clean731-preparation-v1/menu/baseline-early';ready=D/'parodius-menu-clean731-ready-v1';review=D/'parodius-menu-clean731-native-review-v2';bg=D/'parodius-menu-clean731-background-v1';visual=D/'parodius-menu-clean731-visual-v1';extra=D/'parodius-menu-clean731-extra183-v1';failure=D/'parodius-menu-clean731-native-review-source-failure-v1'
 proofs=[json.loads((f/'proof.json').read_text())for f in[review,bg]]
 assert all(q['passed']and q['ROM_sha256']==SHA for q in proofs)
 native=json.loads((run/'lifecycle-proof.json').read_text());assert native['passed']and all(q['passed']for q in native['components'].values())and native['additive_timing']['passed']
 frames=json.loads((bg/'all-owned-menu-static-pixels.json').read_text());pages=json.loads((bg/'whole-menu-review-pages.json').read_text());required=[184,194,206,218,230,242,254,266]
 assert len(frames)==164 and len(pages)==6 and all(q['static_mismatches']==0 for q in frames)
 assert sorted(q['frame']for q in frames)==sorted(n for page in pages for n in page['frames'])
 evidence=json.loads((review/'evidence.json').read_text());changed=evidence['parent3cee_same_controller_comparison']['changed_frames']
 assert sorted(changed)==sorted([q['frame']for q in frames]+[183])
 assert evidence['parent3cee_same_controller_comparison']['CSV']['inputs.csv']['parsed_equal']and evidence['parent3cee_same_controller_comparison']['CSV']['trace.csv']['parsed_equal']
 assert evidence['parent3cee_same_controller_comparison']['source_OAM_epoch_differences']==0
 assert json.loads((bg/'scoped-enable-without-same-frame-start-owner.json').read_text())['frames']==[]
 files=set()
 def check_manifest(folder):
  f=folder/'manifest.json';data=json.loads(f.read_text());files.add(f)
  for n,h in data.items():
   expected=h['sha256']if isinstance(h,dict)else h
   assert sha(n)==expected,n;files.add(Path(n))
 for folder in [ready,review,bg,visual]:check_manifest(folder)
 for folder in [ready,review,bg,visual,extra,failure]:files.update(f for f in folder.iterdir()if f.is_file())
 # Agent inspected all six actual whole-menu pages (164 frames), the separate
 # changed183 transition, both selected actual sheets, and the eight triples.
 # This records agent inspection, never a human reviewer or all-pixel verdict.
 visual_bindings={str(f.resolve()):sha(f)for f in list(bg.glob('all-owned-menu-wholeframes-*.png'))+[bg/'two-baseline-references-and-mask.png',bg/'proof.json',bg/'source-derived-mask.json',bg/'all-owned-menu-static-pixels.json',bg/'known-seven-b0-rejection-controls.json',visual/'eight-actual-menu-before-held-after.png',visual/'eight-frame-bindings.json',visual/'actual-eight-frame-DMA-enable.json',visual/'selected-actual-whole-PPU-01.png',visual/'selected-actual-whole-PPU-02.png',extra/'extra-changed183-actual.png',extra/'bindings.json']}
 put(a.output/'visual-manifest.json',visual_bindings)
 v=dict(passed=True,ROM_sha256=SHA,agent_visual_review=True,human_review_claim=False,native_launched_by_this_tool=False,
  actual_owned_selection_frames_reviewed=[q['frame']for q in frames],actual_owned_selection_frame_count=164,
  all_changed_wholeframe_values_reviewed=changed,additional_changed_transition_reviewed=183,
  actual_eight_counterpart_frame_values_reviewed=required,all_static_mask_failure_frames=[],
  eight_counterpart_sheet=str((visual/'eight-actual-menu-before-held-after.png').resolve()),eight_counterpart_sheet_sha256=sha(visual/'eight-actual-menu-before-held-after.png'),
  static_mask=dict(actual_baseline_frames=[185,200],baseline_mismatches=0,known_b0_wrap_frames_rejected=7,owned_frames=164,included_pixels_per_frame=51712,total_compared_pixels=8480768,excluded_pixels_per_frame=9728,mismatches=0,full_background_or_dynamic_preview_oracle=False),
  observations=['The seven saved b0 background-wrap/duplicate-portrait examples are absent in the clean731 counterpart frames; first184 preview is visible.',
   'All164 owned selection wholeframes show stable header/yellow line/gray roster/backdrop. Dynamic names, cursors, native previews and static SELECT ALTERNATES legend were inspected in the full images.',
   'Changed183 is the title-to-menu blanking transition, separately inspected; it is not included in the normal menu static mask.',
   'Selected cancel/title/reentry, initial HUD publication and active frames were inspected. No displaced background strip was apparent there.',
   'Actual674 still shows severely partial player visibility among effects; crowded-body starvation/flicker remains open. Tiny gameplay labels remain dense.'],
  manifest_sha256=sha(a.output/'visual-manifest.json'),bindings=visual_bindings,
  limits='Bounded agent image inspection plus an exact51,712pixel static subset per owned menu frame. Explicit9,728pixel dynamic/preview exclusions; no wholeBG/all-pixel/source-fidelity/body-visibility/globaltiming/campaign/adoption claim. Originalb0visualFALSE and originalareaFALSE/natural pendingBuffer2 overlap stay preserved.')
 put(a.output/'visual-proof.json',v)
 report=R/'docs/qa/parodius-menu-clean731-native-2026-10-26.txt';assert not report.exists()
 report.write_text(f'''Clean731 menu1800: bounded native and agent visual qualification, 2026-10-26

Exact ROM {SHA}
Source D/mm-proto-clean-menu-candidates-v1/clean-menu-irq (D is the external
2026-10-24-native-rest-py archive). One authorized native launch; exit0,
no retry. Worker explicitly released immediately after completion. ROOT owns
production/adoption; this task did not edit production/default/Git/settings.

All original6 semantic components and additive timing PASS: actualEasy0,
terminalOctopus1, actual menu variants0/1/2/3, cancel/title/reentry/current-life
publication and displayed HUD/font pairing. 1122updates/797publications,
1000semanticDMAs, minSP197,1257actualIRQ31,1256visible-scroll checks,
15072sourceCHR checks. Independent reaggregation verifies1000semantic complete
hardware transfers and1487real completed publication epochs. The ungated layer
verifies1300full256-byte transfers and945scoped render enables,0late,
0hardware mismatches. All actual DMA data/complete/enable stamps are retained.
IRQ return hook records RTI entry plus later endFrame evidence, not a callback
pretending to execute after RTI. No physical worst-DMC/globaltiming claim.

Source and RGB: all5376compiled HUD reference pixels/3072fontbytes/84cellbytes
match;1258actual displayed pair frames compare2254336glyph+background pixels,
0mismatches, calibrated independently against immutable actual3cee548.
All1799input rows and1799trace rows are exactly3cee; all1121completed-motion
rows byte-exact. All1487same-frame source OAM epochs are unchanged. Of1651
actual full RGB frames,1486are byte-exact3cee;165differ:164owned menu frames
plus the separately inspected183blanking transition. This is a measured finite
same-input result, not a source-frame/cadence improvement or all-pixel claim.

Independent STATIC MENU check: actual3cee185 is the fixed RGB reference;
actual3cee200 validates the source-derived mask with0differences. All seven
known bad b0 images194/206/218/230/242/254/266 reject that same mask. Every
actual owned clean selection frame (164) compares51712pixels:8480768total,
0mismatches.9728pixels per frame are explicitly excluded: authorized20cell
legend at2346,16cellname at linkedX5MenuNameAddress,19cursorcells from actual
linkedLo/Hi tables, and conservative preview box80..176x136..208. No fullBG,
dynamic-name/cursor/preview or background-reconstruction oracle is claimed.
No scoped menu-enable frame lacks its same-frame full start-owner snapshot.
All NT/CHR/palette/OAM/t/v/fineX/w snapshots and actual rawRGB remain external.

AGENT IMAGE REVIEW (not human review): all164owned wholeframes across six
sheets, all8required184/194/206/218/230/242/254/266before/b0-held/clean triples,
extrachanged183, and32selected wholeframes spanning title/cancel/reentry/first
HUD/active play. The seven wrap/duplicate-background examples are gone in this
run; the184preview is retained. Menu names/cursor/previews and static SELECT
ALTERNATES legend remain readable in these images.183is an explicitly reviewed
blanking carry transition, outside the stable menu mask. At674the hero is still
severely partial amid effects; body starvation/flicker is not fixed. Gameplay
bar lettering remains tiny/dense; exact source pixels do not close readability.

Source/CPU context is exact and separately bound: A's clean freeze restores the
original shots/removes only the unqualified budget experiment (144bytes bank66),
retaining BB50 menu helper. Fresh clean-pair1786NMI/512input/1042IRQ controls,
ROOT fresh731menu1368+74caller/PPU and2962helper-boundary controls are separate
source evidence.1481helperNMI boundaries use the actual GameLoop-privateFF
lag/audio owner; complete flushing-NMI cases run after publication. Source menu
foreground adds0..4197CPU on highlights, idle0; NMI saves0..619. No universal
speed/60Hz claim. ROOT's separate clean450 and heavyHard1F240 observations are
context, not additional menu runs or relabeled historical731results.

Original b0 native programmed components remain mechanicallyPASS but actual
visualFAILED; the saved seven wraps,900/59prototypes and originalareaFALSE/
missing natural pending-fullHUD+Buffer2 overlap stay immutable. The menu run
observes195actualBuffer2flushes but0pending-fullHUD holds; this does NOT clear
the original conditional overlap coverage gap. No fresh death/area/HardParodius
matrix/campaign/flicker/full-roster every-item/source-fidelity completion.

One offline postprocessor v1 had an indentation error before main; exact failed
tool/receipt is preserved separately. v2 only fixes that source formatting and
passes the saved native reaggregation. No emulator retry or receipt backfill.

Native run {run}
Readiness {ready}
Native reaggregation {review}
Static mask {bg}
Actual comparison sheets {visual}
Final native/visual packets {a.output}
Stable native command is SPENT; its launch.json guard prevents reuse. Any new
native launch requires fresh ROOT authorization and a fresh frozen output.
''',encoding='utf-8')
 shutil.copy2(report,a.output/'report.txt')
 tools=[R/'tools/audit'/n for n in ['parodius_visibility_menu_clean_prepare_v1.py','parodius_visibility_menu59_timing_v2.lua','parodius_visibility_menu59_static_v1.py','parodius_visibility_menu59_timing_mock_v1.py','parodius_visibility_menub0_dma_mock_v1.py','parodius_visibility_menu_clean_ready_v1.py','parodius_visibility_menu_clean_run_v1.py','parodius_visibility_menu_clean_native_review_v2.py','parodius_visibility_menu_clean_background_v1.py','parodius_visibility_menu_clean_visual_v1.py','parodius_visibility_menu_clean_final_v1.py']]
 context=[D/'mm-proto-clean-menu-candidates-v1/freeze-v1/receipt.json',D/'root-presentation450-731-v1/ROOT-review-v1/proof.json',D/'root-clean731-hard1f-v1/native-launch-v1/proof.json',D/'root-clean731-hard1f-v1/native-launch-v1/comparison/proof.json']
 for f in context:assert f.is_file(),f;files.add(f)
 for f in [D/'root-clean731-menu-caller-v1/proof.json',D/'root-clean731-menu-interrupt-v1/proof.json']:
  assert f.is_file(),f;files.add(f)
 files.update(tools);files.add(report)
 put(a.output/'review-files.json',{str(f.resolve()):sha(f)for f in tools+[report]+context+[a.output/'visual-proof.json',bg/'proof.json',review/'proof.json']})
 files.update(f for f in a.output.iterdir()if f.is_file());manifest={str(f.resolve()):sha(f)for f in sorted(files,key=str)};put(a.output/'manifest.json',manifest)
 proof=dict(passed=True,native_run=True,component_only=True,goal_complete=False,ROM_sha256=SHA,launches=1,retries=0,worker_released=True,
  actual_mode=0,actual_menu_variants=[0,1,2,3],actual_terminal_variant=1,all_original6_and_additive_timing_passed=True,
  updates=1122,semantic_DMAs=1000,ungated_completed_full256_DMAs=1300,scoped_safe_render_enables=945,late_render_enables=0,hardware_mismatches=0,minimum_sampled_SP=197,
  source_epoch_checks=1487,source_OAM_epoch_differences=0,inputs_rows_exact3cee=1799,trace_rows_exact3cee=1799,completed_motion_rows_exact3cee=1121,
  compiled_HUD_reference_pixels=5376,actual_HUD_RGB_pixels=2254336,actual_HUD_RGB_mismatches=0,actual_full_RGB_frames=1651,exact3cee_full_RGB_frames=1486,changed_full_RGB_frames=165,
  bounded_static_menu_pixels=8480768,bounded_static_menu_mismatches=0,visual_proof=str((a.output/'visual-proof.json').resolve()),visual_proof_sha256=sha(a.output/'visual-proof.json'),agent_visual_review=True,
  native_result_sha256=sha(run/'lifecycle-proof.json'),native_review_sha256=sha(review/'proof.json'),static_mask_proof_sha256=sha(bg/'proof.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),review_files_sha256=sha(a.output/'review-files.json'),
  no_production_or_settings_changes=True,original_b0_visual_FAILURE_preserved=True,original_area_coverage_FALSE_preserved=True,
  limits='One bounded actualEasy all4variant menu lifecycle plus explicit static-subset and agent wholeframe review only.9,728dynamic/previewpixels excluded per static frame; no fullBG/all-pixel/bodyflicker/tinyfont/globalDMC/death/area/HardParodius/everyitem/campaign/adoption verdict. ROOT separate450/Hard1F remain separate context; no relabeling historical evidence.')
 put(a.output/'proof.json',proof)
 for n,h in manifest.items():assert sha(n)==h,n
 checkpoint=R/'docs/qa/checkpoints/2026-10-26/parodius-menu-clean731-native';checkpoint.mkdir(parents=True,exist_ok=False)
 for n in ['proof.json','visual-proof.json','visual-manifest.json','manifest.json','review-files.json','report.txt']:shutil.copy2(a.output/n,checkpoint/n)
 for name,folder in [('native-review',review),('static-menu',bg),('readiness',ready)]:shutil.copy2(folder/'proof.json',checkpoint/(name+'-proof.json'))
 for name,folder in [('mask-layout',bg),('native-source-failure',failure)]:
  f=folder/('source-derived-mask.json'if name=='mask-layout'else'failure.json');shutil.copy2(f,checkpoint/(name+'.json'))
 (checkpoint/'README.txt').write_text('''Exact731 bounded menu native/visual checkpoint; no binaries/settings/captures.
All raw evidence and actual wholeframe sheets stay in the external archive.
proof.json is the bound one-shot result; visual-proof.json records AGENT image
inspection and51,712staticpixels per owned menu frame, not a wholeBG verdict.
manifest.json binds exact source/runtime/native images and all prior receipts.
Original b0 visualFAIL and originalareaFALSE/naturalBuffer2 gap remain held.
One worker was released; no more native launches or production/Git edits.
''',encoding='utf-8')
 cp={str(f.resolve()):sha(f)for f in checkpoint.iterdir()if f.is_file()};put(checkpoint/'checkpoint-manifest.json',cp)
 print(json.dumps(dict(proof=str((a.output/'proof.json').resolve()),proof_sha256=sha(a.output/'proof.json'),visual_proof_sha256=sha(a.output/'visual-proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(manifest),report_sha256=sha(report),review_files_sha256=sha(a.output/'review-files.json'),checkpoint=str(checkpoint),checkpoint_manifest_sha256=sha(checkpoint/'checkpoint-manifest.json')),indent=2))
if __name__=='__main__':main()

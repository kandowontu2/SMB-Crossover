"""Freeze held b0 menu outcome: mechanical pass plus real seven-frame visual failure."""
from pathlib import Path
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--checkpoint',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);a.checkpoint.mkdir(parents=True,exist_ok=False)
 native=D/'parodius-menub0-native-v1';negative=D/'parodius-menub0-visual-negative-v1';ready=D/'parodius-menub0-ready-v1';run=D/'parodius-menub0-preparation-v3/menu/baseline-early'
 n=json.loads((native/'proof.json').read_text());v=json.loads((negative/'proof.json').read_text());assert n['passed']and n['all6native_components_passed']and not v['passed']and v['visual_failure']
 files={}
 for folder in[native,negative]:
  for f,h in json.loads((folder/'manifest.json').read_text()).items():assert sha(f)==h,f;files[f]=h
  for f in folder.rglob('*'):
   if f.is_file():files[str(f.resolve())]=sha(f)
 review=dict(agent_visual_review=True,human_visual_review=False,selected_current_whole_frames=31,matched_old_current_pairs=12,current_frame_selection='24fullframes in native-v1 sheet plus sevenbad highlights from all-eight-changed sheet;184overlap',held=True,overall_visual_pass=False,actual_regression_frames=[194,206,218,230,242,254,266],actual_preview_restoration_frame=184,diagnosis='Actual images show whole-menu vertical wrap/duplicate portraits/text on sevenhighlight frames. Existing selected-Parodius semantic guards do not own these earlier other-character frames. Source-CPU prediction misses verticalreload280..304, but actual earlyE008/mask stamps are absent and remain explicitly unclaimed.',native_six_components_passed=True,original_native_pass_does_not_mean_global_visual_acceptance=True,source_5376pixel_reference_exact=True,actual_1258_displayed_HUDpairs_2254336pixels_exact=True,original_area_false_natural_Buffer2_and_bodyvisibility_tinyfont_limits_remain=True,sheet_bindings={str(f):sha(f)for f in[native/'selected-full-PPU.png',native/'changed-frames-before-after.png',negative/'all-eight-changed-actual-frames.png']})
 put(a.output/'agent-visual-review.json',review)
 reviewfiles=json.loads((ready/'review-files.json').read_text())
 for f,h in reviewfiles.items():assert sha(f)==h,f
 added=[R/'tools/audit/parodius_visibility_menub0_native_freeze_v1.py',R/'tools/audit/parodius_visibility_menub0_failure_attribution_v1.py',Path(__file__).resolve(),R/'docs/qa/parodius-menub0-native-held-2026-10-26.txt',R/'docs/qa/parodius-menub0-source-wording-erratum-2026-10-26.txt']
 for f in added:reviewfiles[str(f.resolve())]=sha(f)
 put(a.output/'review-files.json',reviewfiles);files.update(reviewfiles)
 for folder in[ready,D/'parodius-menub0-wording-v1']:
  for name in ['proof.json','manifest.json']:
   f=folder/name
   if f.exists():files[str(f)]=sha(f)
 cp={'ready':ready/'proof.json','mechanical-pass':native/'proof.json','visual-failure':negative/'proof.json','actual-and-modeled-timings':negative/'actual-and-modeled-timings.json','agent-visual-review':a.output/'agent-visual-review.json','source-failure-ledger':ready/'source-failure-ledger.json','static-wording-erratum':ready/'static-wording-erratum.json'}
 for name,f in cp.items():shutil.copy2(f,a.checkpoint/(name+'.json'))
 shutil.copy2(R/'docs/qa/parodius-menub0-native-held-2026-10-26.txt',a.checkpoint/'report.txt')
 put(a.checkpoint/'review-files.json',reviewfiles)
 put(a.checkpoint/'external-bindings.json',{str(f):sha(f)for folder in[native,negative,ready]for f in[folder/'proof.json',folder/'manifest.json']})
 (a.checkpoint/'README.txt').write_text('B0 MENU1800 HELD / OVERALL VISUAL FAILURE\n\nONE granted Easy/all4variant menu run, no retry; worker released. Six programmed components pass;1000observed completed transfers exact;1258HUDpairs/2254336pixels exact;inputs/trace/completedmotion exact3cee. BUT sevenearlier other-character menu highlights verticallywrap/duplicate backgrounds. Actual184previewrestores. All8changed pairs independentlyagent-reviewed; directearlyDMA/enable stamps ABSENT, source-only exactcommand/tailmodel explicitlydisclosed. OriginalnativePASS bytes retained; additiveoverallFALSE. No adoption/newnative/source/default/settings/Git changes. Captures/settings/binaries external only.\n',encoding='utf-8')
 put(a.checkpoint/'manifest.json',{f.relative_to(a.checkpoint).as_posix():sha(f)for f in sorted(a.checkpoint.rglob('*'))if f.is_file()})
 for folder in[a.output,a.checkpoint]:
  for f in folder.rglob('*'):
   if f.is_file():files[str(f.resolve())]=sha(f)
 put(a.output/'manifest.json',files)
 final=dict(passed=False,native_run=True,held=True,visual_failure=True,goal_complete=False,ROM_sha256=n['ROM_sha256'],launches=1,retries=0,worker_released=True,all6programmed_semantic_components_passed=True,observed_completed_transfers_exact=1000,observed_complete_visible_init_epochs_exact=1487,actual_full_HUD_pixels_exact=2254336,source_full_reference_pixels_exact=5376,actual_inputs_and_trace_and1121completed_motion_rows_exact_parent=True,actual_regression_frames=v['actual_regression_frames'],actual_preview_restored_frame=184,agent_visual_review=True,source_model_not_actual_mask_timestamps=True,earlier_passed_native_packet_unchanged=True,native_proof_sha256=sha(native/'proof.json'),visual_negative_sha256=sha(negative/'proof.json'),visual_review_sha256=sha(a.output/'agent-visual-review.json'),review_files_sha256=sha(a.output/'review-files.json'),report_sha256=sha(R/'docs/qa/parodius-menub0-native-held-2026-10-26.txt'),manifest_bindings=len(files),manifest_sha256=sha(a.output/'manifest.json'),checkpoint_manifest_sha256=sha(a.checkpoint/'manifest.json'),limits='HELD; no global menu visual pass, adoption, native retry, additional character/mode/campaign or new source change. Seven actual regressions remain unresolved. OriginalareaFALSE/naturalBuffer2, mixed bodyvisibility/tinyfont, broad timing/DMC limits retained.')
 put(a.output/'proof.json',final);print(json.dumps(final,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))
if __name__=='__main__':main()

"""Freeze the reviewed F35 observation and independent offline scope without backfill."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['native','rgb','cadence','failed-cadence','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 n=json.loads((a.native/'proof.json').read_text());r=json.loads((a.rgb/'proof.json').read_text());c=json.loads((a.cadence/'proof.json').read_text())
 assert not n['passed']and n['original_five_passed']and n['sixth_native_receipt_missing']and n['worker_released']
 assert r['passed']and not r['native_run']and r['observed_frames']==1574 and r['mask_mismatches']==0
 assert c['passed']and c['pre_divergence_actual_epoch_comparisons']==237 and c['total_actual_epochs']==1923
 report=ROOT/'docs/qa/parodius-hud-cancellation-native-2026-10-26.txt'
 reviewed=dict(human_visual_review=True,selected_actual_whole_PPU_frames=24,
               selected_sheet_sha256=sha(a.native/'selected-full-PPU.png'),selected_frame_bindings_sha256=sha(a.native/'selected-frames.json'),
               whole_before_after_frames=4,before_after_sheet_sha256=sha(a.rgb/'before-after-full-PPU.png'),
               finding='Observed repaired death515 custom labels/font396 and restart813 native blank/font0; full customHUD814. Dense tiny labels and crowded body visibility remain open. Selected whole frames show coherent native death/restart; no exhaustive visual clearance.',
               missing_sixth_native_receipt_not_backfilled=True,report_sha256=sha(report))
 (a.output/'visual-review.json').write_text(json.dumps(reviewed,indent=2)+'\n')
 owned=[ROOT/'tools/audit'/x for x in ['parodius_visibility_hud_cancel_native_freeze_v1.py','parodius_visibility_hud_cancel_rgb_v1.py',
        'parodius_visibility_hud_cancel_cadence_v1.py','parodius_visibility_hud_cancel_cadence_v2.py','parodius_visibility_hud_cancel_native_final_v1.py']]+[report]
 (a.output/'review-files.json').write_text(json.dumps({str(f):sha(f)for f in owned},indent=2)+'\n')
 files=set();m=json.loads((a.native/'manifest.json').read_text())
 for f,h in m.items():assert sha(f)==h;files.add(Path(f).resolve())
 for d in [a.native,a.rgb,a.cadence,a.failed_cadence,a.output]:files.update(f.resolve()for f in d.iterdir()if f.is_file())
 files.update(f.resolve()for f in owned)
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=n['ROM_sha256'],
        original_six_component_aggregate_false=True,original_five_native_components_passed=True,sixth_native_receipt_missing=True,
        independent_saved_pair_and_RGB_reaggregation_passed=True,observed_death_restart_visible_repair=True,
        native_outcome_sha256=sha(a.native/'proof.json'),RGB_replay_sha256=sha(a.rgb/'proof.json'),cadence_sha256=sha(a.cadence/'proof.json'),
        visual_review_sha256=sha(a.output/'visual-review.json'),report_sha256=sha(report),review_files_sha256=sha(a.output/'review-files.json'),
        manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),
        limits='Original aggregateFALSE/absent sixth receipt unchanged. One nativeEasy0Oct1death2200 and separate saved1574pair/RGB scope. No rerun, Hard/area/pendingBuffer2/DMC/globalperformance/bodyreadability/adoption/fullgoal verdict.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

"""Freeze reviewed area negative and a small text-only boundary checkpoint."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['negative','ready','output','checkpoint']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);a.checkpoint.mkdir(parents=True,exist_ok=False)
 n=json.loads((a.negative/'proof.json').read_text());assert not n['passed']and n['worker_released']and n['all6terminal_outputs_absent_preserved']
 report=ROOT/'docs/qa/parodius-area-native-boundary-2026-10-26.txt'
 review=dict(human_visual_review=True,selected_actual_whole_PPU_frames=24,selected_sheet_sha256=sha(a.negative/'selected-full-PPU.png'),
             selected_frames_sha256=sha(a.negative/'selected-frames.json'),
             finding='Natural pipe descent, blanking and bonus-room transition occur. Native blank HUD1458 then correct customHUD1459; selected later background/HUD/source art coherent. Tiny denseHUD and crowded-body dropout remain open. No exhaustive every-frame visual clearance.',
             native_aggregate_still_false=True,original6missing_outputs_not_backfilled=True,report_sha256=sha(report))
 (a.output/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
 owned=json.loads((a.ready/'review-files.json').read_text())
 for f,h in owned.items():assert sha(f)==h
 for f in [Path(__file__),ROOT/'tools/audit/parodius_visibility_area4285_native_freeze_v1.py',report]:owned[str(f.resolve())]=sha(f)
 (a.checkpoint/'review-files.json').write_text(json.dumps(owned,indent=2)+'\n')
 external={}
 for d in [a.ready,a.negative]:
  for name in ['proof.json','manifest.json']:
   f=d/name;external[str(f.resolve())]=sha(f)
  shutil.copy2(d/'proof.json',a.checkpoint/(d.name+'-proof.json'))
 for d in ['parodius-area-controller4285-cpu-v2','parodius-area4285-static-v2']:
  f=a.output.parent/d/'proof.json';external[str(f.resolve())]=sha(f);shutil.copy2(f,a.checkpoint/(d+'-proof.json'))
 shutil.copy2(a.output/'visual-review.json',a.checkpoint/'visual-review.json')
 (a.checkpoint/'external-packet-bindings.json').write_text(json.dumps(external,indent=2)+'\n')
 (a.checkpoint/'README.txt').write_text('FROZEN ACTUAL AREA NEGATIVE - NO RETRY\n\nPrivate4285 nativeEasy0Oct1area2600 genuinely enters pipe/loads changed area/resets and publishes >45fresh-area draws. Original six-component aggregateFALSE: required natural fullHUD/nonemptyBuffer2 hold/catchup absent; all6terminal files stay missing.\nIndependent actual2322completedDMAepochs/2118savedRGBHUDframes pass their bounded checks. 24selectedwholePPUframes reviewed. ConditionalBuffer2source/CPU evidence stays separate; global natural reachability/impossibility is not claimed.\nThis text-only checkpoint contains small proofs, visual-review metadata, external packet hashes and a bounded source/tool review list. No ROM/settings/capture binaries. Source and raw evidence remain external.\nBoundary report: '+report.as_posix()+'\n',encoding='utf-8')
 cm={f.relative_to(a.checkpoint).as_posix():sha(f)for f in a.checkpoint.rglob('*')if f.is_file()};(a.checkpoint/'manifest.json').write_text(json.dumps(cm,indent=2)+'\n')
 files=set()
 for f,h in json.loads((a.negative/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 for d in [a.negative,a.output,a.checkpoint]:files.update(f.resolve()for f in d.rglob('*')if f.is_file())
 files.update(Path(f).resolve()for f in owned)
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=n['ROM_sha256'],
        original_aggregate_false_and_6missing_files_preserved=True,genuine_pipe_area_reset_observed=True,natural_pending_fullHUD_Buffer2_hold_not_covered=True,
        independent_saved_DMA_and_RGB_prefix_checks_passed=True,visual_review_sha256=sha(a.output/'visual-review.json'),
        original_negative_sha256=sha(a.negative/'proof.json'),report_sha256=sha(report),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),
        checkpoint_manifest_sha256=sha(a.checkpoint/'manifest.json'),review_files_sha256=sha(a.checkpoint/'review-files.json'),
        limits='Bounded HUD visual-repair evidence and explicit native conditional-overlap coverage failure. No retry, weakened guard, backfill, universal no-overlap proof, CV3/globaltiming/bodyvisibility/allgoal/adoption clearance.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

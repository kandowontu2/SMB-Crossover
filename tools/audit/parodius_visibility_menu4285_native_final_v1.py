"""Freeze compact reviewed menu success while retaining independent held negatives."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['native','ready','failed-aggregation','output','checkpoint']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);a.checkpoint.mkdir(parents=True,exist_ok=False)
 n=json.loads((a.native/'proof.json').read_text());assert n['passed']and n['all6native_components_passed']and n['worker_released']
 report=ROOT/'docs/qa/parodius-menu4285-native-2026-10-26.txt'
 review=dict(agent_visual_review=True,selected_actual_whole_PPU_frames=24,selected_sheet_sha256=sha(a.native/'selected-full-PPU.png'),
             selected_frames_sha256=sha(a.native/'selected-frames.json'),
             finding='Actual all4variant names/portraits, cancelblanking/reentry, blank547/customHUD548 and late1800 appear coherent in selected wholePPU. Tiny denseHUD and crowdedbody limits remain open. Agent tool-based image inspection, not human review.',
             original_area_false_unchanged=True,independent_merged_Hard1F_deadline_negative_not_cleared=True,report_sha256=sha(report))
 (a.output/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
 owned=json.loads((a.ready/'review-files.json').read_text())
 for f,h in owned.items():assert sha(f)==h
 for f in [Path(__file__),ROOT/'tools/audit/parodius_visibility_menu4285_native_freeze_v1.py',ROOT/'tools/audit/parodius_visibility_menu4285_native_freeze_v2.py',report]:owned[str(f.resolve())]=sha(f)
 (a.checkpoint/'review-files.json').write_text(json.dumps(owned,indent=2)+'\n')
 external={}
 for d in [a.ready,a.native]:
  for name in ['proof.json','manifest.json']:
   f=d/name;external[str(f.resolve())]=sha(f)
  shutil.copy2(d/'proof.json',a.checkpoint/(d.name+'-proof.json'))
 shutil.copy2(a.output/'visual-review.json',a.checkpoint/'visual-review.json')
 (a.checkpoint/'external-packet-bindings.json').write_text(json.dumps(external,indent=2)+'\n')
 (a.checkpoint/'README.txt').write_text('ONE FOCUSED4285 MENU NATIVE PASS - GLOBAL COMPOSITION HELD\n\nAll6current native components pass Easy0Oct1menu1800, all4variants/cancel/title-return/reentry/current-generationHUD/OAM/IRQ guards. One launch, no retry, worker released. All1651actual RGBframes and1799input/trace rows match historical5354menu; that is finite comparison, not additional current coverage.\nSeparateareaFALSE/6missing outputs and naturalBuffer2hold gap remain unchanged. ROOT independentHard1Fdeadline166vs167negative is not cleared; merged4285not adopted/timing safe.\n24selectedwholePPUframes received agent tool-based visual inspection. No human reviewer claim. This checkpoint has only small proof/review/hash metadata and tool/source review list; ROM/captures/settings stay external.\nReport: '+report.as_posix()+'\n',encoding='utf-8')
 cm={f.relative_to(a.checkpoint).as_posix():sha(f)for f in a.checkpoint.rglob('*')if f.is_file()};(a.checkpoint/'manifest.json').write_text(json.dumps(cm,indent=2)+'\n')
 files=set()
 for f,h in json.loads((a.native/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 for d in [a.native,a.output,a.checkpoint,a.failed_aggregation]:files.update(f.resolve()for f in d.rglob('*')if f.is_file())
 files.update(Path(f).resolve()for f in owned)
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=True,native_run=True,component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=n['ROM_sha256'],
        current_menu_all6native_components_passed=True,original_area_false_and_pendingBuffer2limitation_unchanged=True,independent_global_deadline_negative_not_cleared=True,
        agent_visual_review=True,visual_review_sha256=sha(a.output/'visual-review.json'),native_packet_sha256=sha(a.native/'proof.json'),report_sha256=sha(report),
        manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),checkpoint_manifest_sha256=sha(a.checkpoint/'manifest.json'),review_files_sha256=sha(a.checkpoint/'review-files.json'),
        limits='One focused current4285Easy menu1800 pass only. No death/Hard/area retry/globaltiming/DMC/bodyreadability/fullgoal/adoption clearance. ROOT independentHard1Fdeadline negative keeps merged4285HELD; originalareaFALSE untouched.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

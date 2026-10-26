"""Additive final5354 selected-frame review and immutable binding packet."""
from pathlib import Path
import argparse,hashlib,json

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['ready','outcome','output']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--selected-review-complete',action='store_true',required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.outcome/'proof.json').read_text());assert z['passed']and z['component_results_present']==z['component_results_required']==5 and z['native_worker_released']
 files=set()
 for packet in [a.ready,a.outcome]:
  m=json.loads((packet/'manifest.json').read_text());assert all(sha(f)==h for f,h in m.items());files.update(Path(f).resolve()for f in m)
  files.update(f.resolve()for f in packet.iterdir()if f.is_file())
 report=ROOT/'docs/qa/parodius-menu-terminal-phase-native-2026-10-26.txt'
 review=dict(reviewed=True,scope='Selected actual fullPPU frames only, not exhaustive visual/source-fidelity QA',frames=z['selected_actual_full_PPU_frames'],sheet_sha256=sha(a.outcome/'selected-actual-full-PPU.png'),review_notes='Fourvariant menus/title/cancel/rebuild, firstactive/prelease/firstcustomHUD and late1800 reviewed. No obvious new tile/CHR/background/scroll corruption in selected frames.349 black and375 partially cleared transition retained. Tiny dense labels and Octopus/Sophia crowded-body visibility remain open. Actual font396 at HUDstart and native IRQ31 worldfont0 are separately bound.',report_sha256=sha(report),IRQ_wording='Native hook reaches real RTI-entry8043, before RTI; laterendFrame and separatecompiledIRQ continuation proof are distinct.',original_negative_retained=True)
 (a.output/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
 for f in [report,Path(__file__),a.output/'visual-review.json']:files.add(f.resolve())
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 proof=dict(passed=True,native_run=True,component_only=True,goal_complete=False,ROM_sha256=z['ROM_sha256'],launches=1,retries=0,worker_released=True,readiness_sha256=sha(a.ready/'proof.json'),outcome_sha256=sha(a.outcome/'proof.json'),visual_review_sha256=sha(a.output/'visual-review.json'),report_sha256=sha(report),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),tool_sha256=sha(Path(__file__)),limits='One actualEasy0 Octopus menu1800 control, fivecomponents plus18selectedframes only. Original false receipts preserved; no source/ROM/settings/adoption changes, no death/area/body/otherprofile launch, no broad completion or worstDMC/visibility closure.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

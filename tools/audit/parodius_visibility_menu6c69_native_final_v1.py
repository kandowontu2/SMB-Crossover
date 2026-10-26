"""Freeze agent-reviewed6c69 menu success, with mixed visibility/old negatives explicit."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['native','ready','parent-run','output','checkpoint']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);a.checkpoint.mkdir(parents=True,exist_ok=False)
 n=json.loads((a.native/'proof.json').read_text());assert n['passed']and n['all6native_components_passed']and n['worker_released']
 ready=json.loads((a.ready/'proof.json').read_text());current=Path(ready['profiles'][0]['packet'])/'baseline-early'
 report=ROOT/'docs/qa/parodius-menu6c69-native-2026-10-26.txt';overload=[]
 for label,r in [('4285',a.parent_run),('6c69',current)]:
  epochs=rows(r/'epochs.jsonl')
  for frame in [674,1554]:
   e=next(q for q in epochs if q['start']['frame']==frame);b=e['dma']['publication']['body'];o=e['start_hardware']
   ys={y for part in b['parts']if part[0]<239 for y in range(part[0]+1,min(part[0]+17,240))}
   peak=max(sum(1 for i in range(64)if o[4*i]<239 and o[4*i]<y<=o[4*i]+16)for y in ys)
   overload.append(dict(ROM=label,frame=frame,body_parts=len(b['parts']),peak_body_row_OAM_entries=peak,rotation=e['dma']['publication']['rotation'],DMA=e['dma']['id'],publication=e['dma']['publication']['id']))
 (a.output/'body-overload-samples.json').write_text(json.dumps(overload,indent=2)+'\n')
 review=dict(agent_visual_review=True,selected_main_current_whole_PPU_frames=24,matched_old_new_pairs=5,
             selected_sheet_sha256=sha(a.native/'selected-full-PPU.png'),selected_frame_bindings_sha256=sha(a.native/'selected-frames.json'),
             changed_comparison_sheet_sha256=sha(a.native/'changed-frames-before-after.png'),changed_frame_bindings_sha256=sha(a.native/'changed-frame-bindings.json'),
             finding='Menu all4names/portraits/cancel/reentry and blank547/custom548 correct in selected actual images. Mixed bodyvisibility674worse/1554fuller; saturated sourceOAMrows confirmed. No allchangedpixelsimprove/flickerclosure claim. Dense tinyHUD remainsopen. Agent image inspection, not human review.',
             report_sha256=sha(report))
 (a.output/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
 owned=json.loads((a.ready/'review-files.json').read_text())
 for f,h in owned.items():assert sha(f)==h
 for f in [Path(__file__),ROOT/'tools/audit/parodius_visibility_menu6c69_native_freeze_v1.py',report]:owned[str(f.resolve())]=sha(f)
 (a.checkpoint/'review-files.json').write_text(json.dumps(owned,indent=2)+'\n')
 external={}
 for d in [a.ready,a.native]:
  for name in ['proof.json','manifest.json']:f=d/name;external[str(f.resolve())]=sha(f)
  shutil.copy2(d/'proof.json',a.checkpoint/(d.name+'-proof.json'))
 for f in [a.output/'visual-review.json',a.output/'body-overload-samples.json']:shutil.copy2(f,a.checkpoint/f.name)
 (a.checkpoint/'external-packet-bindings.json').write_text(json.dumps(external,indent=2)+'\n')
 (a.checkpoint/'README.txt').write_text('ONE FINAL TARGETED6c69 MENU PASS\n\nOne Easy0Oct1menu1800, all6current native components pass. No retry, worker released. Same1122updates/1121byte-exact completedmotion rows/1799sameinputs as4285;997DMAs/794publications versus993/790.1181equal/470changed actualRGBframes.24current wholeframes plus5old/newpairs inspected by agent. Mixed saturatedbodyvisibility/tinyHUD remainopen; no universal improvement/timing claim.\nOriginalareaFALSE/6missingoutputs/naturalBuffer2gap and4285deadline negative remain exact-ROM evidence. ROOT independent6c69Hard1Fcontrol is separate. No sourceedit/adoption/fullgoal verdict.\nOnly small proof/review/hash metadata and tool/source list; allbinaries/settings/captures external.\nReport: '+report.as_posix()+'\n',encoding='utf-8')
 cm={f.relative_to(a.checkpoint).as_posix():sha(f)for f in a.checkpoint.rglob('*')if f.is_file()};(a.checkpoint/'manifest.json').write_text(json.dumps(cm,indent=2)+'\n')
 files=set()
 for f,h in json.loads((a.native/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 for d in [a.native,a.output,a.checkpoint]:files.update(f.resolve()for f in d.rglob('*')if f.is_file())
 files.update(Path(f).resolve()for f in owned);manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=True,native_run=True,component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=n['ROM_sha256'],
        all6native_components_passed=True,completed_motion_byte_exact_to4285=True,four_more_DMA_publications=True,
        agent_visual_review=True,mixed_body_visibility_remains_open=True,original_area_false_and_overlap_limitation_unchanged=True,
        old4285_deadline_negative_preserved=True,native_packet_sha256=sha(a.native/'proof.json'),visual_review_sha256=sha(a.output/'visual-review.json'),report_sha256=sha(report),
        manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),checkpoint_manifest_sha256=sha(a.checkpoint/'manifest.json'),review_files_sha256=sha(a.checkpoint/'review-files.json'),
        limits='One final focused6c69Easy menu1800 pass only. No retry/death/Hard/area attempt/sourceoptimization/adoption. ROOT independentHard1Fcontrol separate; no globaltiming/DMC/bodyreadability/fullgoal verdict. Originalfalse packets retained.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

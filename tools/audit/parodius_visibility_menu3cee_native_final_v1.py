"""Freeze offline agent review of ROOT's one3cee menu control; no launch/edit."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['native','ready','parent-run','output','checkpoint']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);a.checkpoint.mkdir(parents=True,exist_ok=False)
 n=json.loads((a.native/'proof.json').read_text());assert n['passed']and n['all6native_components_passed']
 ready=json.loads((a.ready/'proof.json').read_text());current=Path(ready['profiles'][0]['packet'])/'baseline-early'
 evidence=json.loads((a.native/'evidence.json').read_text());compare=evidence['parent6c69_same_controller_comparison'];rgb=json.loads((a.native/'actual-pair-RGB.json').read_text())
 assert len(rgb)==1258 and sum(x['all_glyph_and_background_pixels']for x in rgb)==2254336 and all(x['exact_RGB_mismatches']==0 for x in rgb)
 assert compare['CSV']['inputs.csv']['parsed_equal']and compare['completed_motion_all5columns_byte_exact']
 overload=[]
 for label,r in [('6c69',a.parent_run),('3cee',current)]:
  epochs=rows(r/'epochs.jsonl')
  for frame in [674,1554]:
   e=next(q for q in epochs if q['start']['frame']==frame);b=e['dma']['publication']['body'];o=e['start_hardware'];ys={y for part in b['parts']if part[0]<239 for y in range(part[0]+1,min(part[0]+17,240))}
   peak=max(sum(1 for i in range(64)if o[4*i]<239 and o[4*i]<y<=o[4*i]+16)for y in ys)
   overload.append(dict(ROM=label,actual_PPU_frame=frame,body_source_parts=len(b['parts']),peak_OAM_entries_on_body_rows=peak,rotation=e['dma']['publication']['rotation'],DMA=e['dma']['id'],publication=e['dma']['publication']['id'],limit='OAM entry occupancy, not opaque-pixel admission or full causal visibility model.'))
 put(a.output/'body-overload-samples.json',overload)
 review=dict(agent_visual_review=True,human_visual_review=False,selected_current_whole_PPU_frames=24,matched_pairs=5,
  selected_sheet_sha256=sha(a.native/'selected-full-PPU.png'),selected_bindings_sha256=sha(a.native/'selected-frames.json'),
  comparison_sheet_sha256=sha(a.native/'changed-frames-before-after.png'),comparison_bindings_sha256=sha(a.native/'changed-frame-bindings.json'),
  finding='Actual menu variants0/1/2/3 show expected names/portraits, cancel/reentry coherent. Selected349/360 are black display-off transition frames, not a claim of fully painted title after cancel. Native blank547 and new positive-source bar548 stable; foreground5pixel-high letters separate from the former plate. Selected674 retains partial/tiny visible body while1554/1800 show fuller body. Mixed player visibility remains open. No every-frame visual inspection or all-pixel improvement claim.',
  exact_pixel_review='All1258saved pair frames independently check all224x8foreground/background RGB positions against current ROM and actual palette, calibrated with immutable6c69frame548. This is stronger than foreground-only mask matching, but not a comfortable-reading/user test.')
 put(a.output/'visual-review.json',review)
 report=ROOT/'docs/qa/parodius-menu3cee-native-2026-10-26.txt'
 report.write_text(f'''Composed3cee menu1800: bounded post-run review/freeze, 2026-10-26

ROOT executed one Easy0/Octopus1 menu1800 run, no retry. This work only reads
the saved artifacts; it launches no emulator and changes no game/source/settings.
ROM {n['ROM_sha256']}
Run {current}
Six native components PASS;1122updates/1000DMAs/797publications/minSP197.
Compared6c69 has997DMAs/794publications with the same1122updates. These are
observed counts, not a global60Hz/performance or every-roster claim.

Independent actual pixel checks PASS on1258saved displayed HUD pairs:
1253custom font396 frames and5native blank/font0 frames. Every224x8position,
including all background/zero pixels, is compared to current3cee font/table,
actual recorded attribute/palette selection and an independent RGB calibration
from immutable6c69frame548/oldcompiledfont/recordedpalette.
2254336actual RGB pixels,0mismatches. No current output is used to calibrate
its own expected glyph color. Custom frames have345foreground and1447background
pixels; native blank frames have1792background pixels. All current native
meter values are0; physical selected-highlight/powerup coverage is not claimed.
Source all128meter/static CPU controls remain separately bound.

All1799recorded input rows and all1121completed-motion rows/all5columns are
byte-exact to6c69. Frame-end trace differs only in cumulative nmiSkipped on849
rows. Of1651actual RGB frames,398are exact and1253change, starting548where the
intended positive-font publication occurs. Outside the HUD bar1452frames are
exact and199differ. This separates comparison regions; it does not exclude
any pixel from the strict full-HUD check or call all other changes improvements.
Saved hardware OAM differs in835of1487matched visible/init epochs.

All1487saved DMA epochs have exact complete256-byte hardware/source snapshots,
OAMADDR0,256data writes and actual transfer completion before startFrame;
recorded body-row source matches too. Actual PPU frame/scanline/cycle, DMA and
publication IDs and last-write completion margins are retained. Minimum margin
is6CPUcycles, narrow: no global timing/DMC guarantee follows.
Native2555boot UpdateScreen C116 owners,1256NMI/DMA checks,15072CHR checks,
1257IRQ31 checks, zero partial-visible/source/body-raster mismatches pass.
All4menu variant readbacks and cancel/title-owner/reentry/current-generation
guards pass. First fresh native blank remains547, positive custom font548.
Terminal HUD-start font396/current generation is followed by intended IRQ31
worldfont0 takeover, real RTI instruction entry and subsequent endFrame. An
RTI-entry callback is not described as occurring after RTI execution.

Agent inspected24current wholePPU frames and five matched pairs at547/548/674/
1554/1800. Menus/names/portraits, cancel/reentry and selected background/HUD
publications are coherent.349/360are actual black display-off frames, not a
claim of a fully painted title after cancel. Tiny positive letters are clearer
as separated shapes, but remain fivepixels high; no user readability verdict.
Selected674stillhaspartialbody while1554/1800arefuller: mixed crowding/visibility
remains open. Entry-occupancy samples are retained, not substituted for opaque
pixel or actor-fairness proof. No sprite limit bypass or pixel/art deletion.
No all-pixel improvement, full-flicker repair or exhaustive visual claim.

Original areaFALSE/six missing terminal outputs/natural pending-fullHUD plus
nonempty Buffer2 overlap limitation remain exact historical evidence. No area,
death or Hardmatrix rerun was made here. ROOT's independent3ceeHard1F168draw
control is separate evidence and is not counted as menu coverage. No adoption
or production permission is inferred from this bounded result.

Initial independent packet {a.native}
Final packet {a.output}
Actual sheets {a.native/'selected-full-PPU.png'}
             {a.native/'changed-frames-before-after.png'}
''',encoding='utf-8')
 for f in [a.output/'visual-review.json',a.output/'body-overload-samples.json',report]:shutil.copy2(f,a.checkpoint/f.name)
 for d in [a.ready,a.native]:shutil.copy2(d/'proof.json',a.checkpoint/(d.name+'-proof.json'))
 external={str(d/name):sha(d/name)for d in[a.ready,a.native]for name in['proof.json','manifest.json']};put(a.checkpoint/'external-packet-bindings.json',external)
 owned=json.loads((a.ready/'review-files.json').read_text())
 for f,h in owned.items():assert sha(f)==h
 for f in[Path(__file__),ROOT/'tools/audit/parodius_visibility_menu3cee_native_freeze_v1.py',report]:owned[str(f.resolve())]=sha(f)
 put(a.checkpoint/'review-files.json',owned)
 (a.checkpoint/'README.txt').write_text('ONE ROOT-EXECUTED3cee EASY MENU1800 PASS; OFFLINE POST-RUN REVIEW ONLY\n\nAll6native components PASS;1258actualRGBpairs/all2254336foreground+backgroundpixels exact. Inputs/completedmotion exact6c69;3extraDMA/publications.24wholeframes+5matchedpairs agent-inspected. Mixedbodyvisibility/tinyfont/originalareaFALSE+naturalBuffer2overlap limits remain. No retry/sourceedit/newnative/adoption/fullgoal claim. Only compact proofs/report/hashmetadata tracked; captures/binaries/settings external.\n',encoding='utf-8')
 put(a.checkpoint/'manifest.json',{f.relative_to(a.checkpoint).as_posix():sha(f)for f in sorted(a.checkpoint.rglob('*'))if f.is_file()})
 files={Path(f)for f,h in json.loads((a.native/'manifest.json').read_text()).items()if sha(f)==h}
 assert len(files)==n['manifest_bindings']
 for d in[a.native,a.output,a.checkpoint]:files|={f for f in d.rglob('*')if f.is_file()}
 files|={Path(f)for f in owned};manifest={str(f.resolve()):sha(f)for f in sorted(files,key=str)};put(a.output/'manifest.json',manifest)
 final=dict(passed=True,native_run=True,offline_post_run_review_only=True,native_executed_by='ROOT',component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=n['ROM_sha256'],
  all6native_components_passed=True,exact_completed_motion_to6c69=True,exact_inputs_to6c69=True,three_more_DMA_publications=True,
  independently_checked_full_HUD_RGB_pixels=2254336,foreground_and_background_RGB_mismatches=0,complete_source_DMA_epochs=1487,
  agent_visual_review=True,mixed_body_visibility_and_tinyfont_open=True,original_area_false_and_natural_overlap_limitation_unchanged=True,
  report_sha256=sha(report),visual_review_sha256=sha(a.output/'visual-review.json'),native_packet_sha256=sha(a.native/'proof.json'),
  manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),checkpoint_manifest_sha256=sha(a.checkpoint/'manifest.json'),review_files_sha256=sha(a.checkpoint/'review-files.json'),
  limits='One ROOT-run current3ceeEasyOctmenu1800 only, offline review by this agent. No retry/newnative/source/production/area/death/Hardmatrix/globalDMC/60Hz/visibility/fidelity/adoption/wholegoal verdict. ROOT Hard1F separate.')
 put(a.output/'proof.json',final);print(json.dumps(final,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))
if __name__=='__main__':main()

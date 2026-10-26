"""Freeze5354 terminal font-phase fixture failure; no outcome retagging."""
from pathlib import Path
import argparse,collections,hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);receipt=json.loads((a.run/'lifecycle-proof.json').read_text());assert not receipt['passed']and receipt['ROM_sha256']=='5354161f339548f2e12b955f5fc1481b9956fe83a63263a04f4b2816edbbdf30';assert all(x is None for x in receipt['component_bindings'].values())
 assert'Final live Octopus actual HUD lease'in(a.run/'host.log').read_text()
 hud=[json.loads(s)for s in(a.run/'hud-frames.jsonl').open()];scroll=[json.loads(s)for s in(a.run/'scroll-events.jsonl').open()];life=[json.loads(s)for s in(a.run/'lifecycle-events.jsonl').open()]
 counts=collections.Counter();phase=[];oldsites=[];completions=0;invalid=0
 for s in(a.run/'oam-bus.jsonl').open():
  q=json.loads(s);counts[q['kind']]+=1
  if q['kind']=='4014-complete-after-next-LDX':completions+=1;assert q['exact_source']and q['completed_2004_writes']==256
  if q['kind']=='lifecycle-init-start-before-assertion'and q.get('sprites_enabled')and(not q['DMA_complete']or not q['hardware_exact_source']):invalid+=1
  if q.get('ppu',{}).get('frame')==1800 and(q['kind'].startswith('IRQ')or q['kind']=='CHR-write'and q['address']==0x5128):phase.append(q)
  if q.get('ppu',{}).get('frame')in [278,376]and q['kind']=='lifecycle-init-start-before-assertion':oldsites.append(q)
 assert invalid==0 and len(oldsites)==2 and all(q['DMA_complete']and q['hardware_exact_source']for q in oldsites)
 assert [q['physical']for q in phase if q['kind']=='CHR-write']==[396,396,0]
 assert next(q for q in phase if q['kind']=='IRQ-entry')['ppu']['scanline']==31
 lastfont=next(q for q in reversed(phase)if q['kind']=='CHR-write');assert lastfont['ppu']==dict(scanline=31,cpu=53578701,cycle=128,frame=1800)
 start=next(q for q in scroll if q['kind']=='visible-start'and q['state']['ppu']['frame']==1800);assert start['state']['font']==396 and start['state']['active']==3
 frames=sorted(int(f.stem.removeprefix('frame-'))for f in a.run.glob('frame-*.argb'));assert frames==list(range(150,1800))
 active=next(q['finished']['frame']for q in hud if q['start']['ram']['OperMode']==1 and q['start']['ram']['GameEngineSubroutine']==8)
 font=next(q['finished']['frame']for q in hud if q['start']['ram']['InvHudActive']==3 and q['start']['ram']['OperMode']==1 and q['start']['chr'][8]==396)
 capture=next(q['capture']['ppu']['frame']for q in scroll if q['kind']=='capture-visible-frame')
 selected=sorted(set([266,278,290,302,314,326,349,369,375,376,active,capture,capture+1,font,font+1,1797,1798,1799]));sheet=Image.new('RGB',(6*256,((len(selected)+5)//6)*260),'#151515');draw=ImageDraw.Draw(sheet);bindings=[]
 for i,n in enumerate(selected):
  raw=a.run/f'frame-{n:06}.argb';image=Image.frombytes('RGBA',(256,240),raw.read_bytes(),'raw','BGRA').convert('RGB');dest=a.output/f'actual-PPU-{n}.png';image.save(dest);sheet.paste(image,(i%6*256,i//6*260+20));draw.text((i%6*256,i//6*260),f'Actual PPU {n}',fill='white');bindings.append(dict(frame=n,raw_sha256=sha(raw),PNG_sha256=sha(dest)))
 sheet.save(a.output/'selected-actual-full-PPU.png');(a.output/'selected-frame-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
 evidence=dict(classification='FIXTURE_TERMINAL_CHR_PHASE_MISMATCH',game_defect_proven=False,failed_predicate='At endFrame1800 require live mapper.chrBanks8==396, after native IRQ31 intentionally restores worldfont0',actual_HUD_start=start,actual_NMI_IRQ_font_writes=phase,last_hardware_font_write=lastfont,old278_376_completed_starts=oldsites,preceding_all4_cancel_reentry_fresh45_assertion_passed=True,exact_fresh_update_count_not_logged=True,current_terminal_RAM_tuple_not_logged=True,last_saved_HUD_start=hud[-1]['start'],missing_final_capture1800=True,required_terminal_components_absent=5)
 (a.output/'phase-failure-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 report=ROOT/'docs/qa/parodius-menu-initial-hint-native-hold-2026-10-26.txt';manifest={str(f.resolve()):sha(f)for f in a.run.rglob('*')if f.is_file()}
 for f in [a.ready/'proof.json',a.ready/'manifest.json',Path(__file__),report]:manifest[str(f.resolve())]=sha(f)
 for f in a.output.iterdir():
  if f.is_file():manifest[str(f.resolve())]=sha(f)
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 proof=dict(passed=False,native_run=True,classification=evidence['classification'],native_worker_released=True,launches=1,retries=0,ROM_sha256=receipt['ROM_sha256'],readiness_sha256=sha(a.ready/'proof.json'),raw_ARGB_frames=frames,component_results_present=0,component_results_required=5,actual_HUD_font_at_start1800=396,actual_font_after_IRQ31=0,old278_376_DMA_completed_exact=True,completed_DMA_count=completions,enabled_init_incomplete_starts=invalid,all4_cancel_reentry_fresh45_condition_passed=True,first_active_frame=active,first_palette_capture_frame=capture,first_saved_font396_frame=font,bus_counts=dict(counts),phase_evidence_sha256=sha(a.output/'phase-failure-evidence.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),tool_sha256=sha(Path(__file__)),limits='ONE nativeattempt failed terminal fixture predicate; no native pass inferred from partial guards or phase analysis. No frame1800 capture/terminalstate tuple, exact freshcounter unlogged. Source-backed IRQ takeover explains wrong-time396 comparison. All original raw/results untouched, no retry/adoption. New oracle requires separate version/review/grant.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=proof['manifest_sha256'],bindings=len(manifest),selected=selected),indent=2))


if __name__=='__main__':main()

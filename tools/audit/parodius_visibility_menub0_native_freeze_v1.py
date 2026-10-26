"""Offline review/freeze of ROOT's one3cee menu run; no native launch."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw,ImageChops
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]
SHA='b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99'


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','ready','historical-run','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.run/'lifecycle-proof.json').read_text());assert z['passed']and z['runner_exit']==0 and z['ROM_sha256']==SHA
 assert len(z['components'])==6 and all(q['passed']for q in z['components'].values())
 life=rows(a.run/'lifecycle-events.jsonl');terminal=next(x for x in life if x['kind']=='terminal-fixture-state')
 assert terminal['menu_return']and terminal['menu_reentry']and terminal['fresh_current_generation_updates']>=45
 variant_frames=rows(a.run/'hud-frames.jsonl')
 actual_variants=sorted({x['start']['ram']['VvVariant']for x in variant_frames if 250<=x['finished']['frame']<=336 and x['start']['ram']['OperMode']==0})
 assert actual_variants==[0,1,2,3]
 trace={}
 for name in ['inputs.csv','trace.csv']:
  with(a.run/name).open()as f:new=list(csv.DictReader(f))
  with(a.historical_run/name).open()as f:old=list(csv.DictReader(f))
  assert len(new)==len(old)
  fields=Counter(k for x,y in zip(new,old)for k in x if x[k]!=y[k])
  if name=='inputs.csv':assert new==old
  else:assert set(fields)<=set(['nmiSkipped','x','camera'])
  trace[name]=dict(rows=len(new),parsed_equal=new==old,different_rows=sum(x!=y for x,y in zip(new,old)),different_fields=dict(fields),current_sha256=sha(a.run/name),historical_sha256=sha(a.historical_run/name))
 motion=a.run/'completed-loop-motion.csv';assert motion.read_bytes()==(a.historical_run/motion.name).read_bytes()
 with motion.open()as f:motion_rows=list(csv.DictReader(f))
 rgb_bind=[]
 for f in sorted(a.run.glob('frame-*.argb')):
  current=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');historical=Image.frombytes('RGBA',(256,240),(a.historical_run/f.name).read_bytes(),'raw','BGRA').convert('RGB')
  difference=ImageChops.difference(current,historical);ImageDraw.Draw(difference).rectangle((16,8,239,15),fill=(0,0,0))
  rgb_bind.append(dict(frame=int(f.stem.split('-')[1]),current=str(f.resolve()),historical=str((a.historical_run/f.name).resolve()),sha256=sha(f),historical_sha256=sha(a.historical_run/f.name),equal=sha(f)==sha(a.historical_run/f.name),outside_HUD_equal=difference.getbbox()is None))
 assert len(rgb_bind)==1651
 (a.output/'all1651-RGB-comparison.json').write_text(json.dumps(rgb_bind,indent=2)+'\n')
 hfr={q['finished']['frame']:q for q in rows(a.run/'hud-frames.jsonl')};pairs=rows(a.run/'hud-lease-frames.jsonl');raw=(a.run/'candidate.nes').read_bytes();rgb=[]
 # Independent RGB calibration comes from the immutable actual3cee frame548,
 # its old compiled font, recorded hardware palette and whole old bar. It is
 # not inferred from the new3cee output that is being checked.
 oldrows={q['finished']['frame']:q for q in rows(a.historical_run/'hud-frames.jsonl')};s=oldrows[548]['start'];oldraw=(a.historical_run/'candidate.nes').read_bytes()
 calibration_image=Image.frombytes('RGBA',(256,240),(a.historical_run/'frame-000548.argb').read_bytes(),'raw','BGRA').convert('RGB');calibration={}
 for col,t in enumerate(s['labels']):
  at=1048592+s['chr'][8+t//64]*1024+(t%64)*16;data=oldraw[at:at+16];pal=(s['attrs'][(col+2)//4]>>((col+2)&2))&3
  for y in range(8):
   for x in range(8):
    px=(data[y]>>(7-x)&1)|((data[y+8]>>(7-x)&1)<<1);color=s['palette'][0 if px==0 else pal*4+px]&63
    calibration.setdefault(color,set()).add(calibration_image.getpixel((16+col*8+x,8+y)))
 assert all(len(v)==1 for v in calibration.values());calibration={k:next(iter(v))for k,v in calibration.items()}
 (a.output/'independent3cee-RGB-calibration.json').write_text(json.dumps(dict(frame=548,capture_sha256=sha(a.historical_run/'frame-000548.argb'),old_ROM_sha256=sha(a.historical_run/'candidate.nes'),observed_color_to_RGB={str(k):list(v)for k,v in calibration.items()},whole_bar_pixels=1792),indent=2)+'\n')
 for q in pairs:
  assert q['passed']and q['mode']==0 and q['variant']==1
  n=q['ppu']['frame'];s=hfr[n]['start'];assert q['ppu']==s['ppu']and q['labels']==s['labels']and q['font']==s['chr'][8]
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');bg=im.getpixel((0,8));assert bg==im.getpixel((255,8));bad=[];foreground=0
  for tile,t in enumerate(s['labels']):
   at=1048592+s['chr'][8+t//64]*1024+(t%64)*16;data=raw[at:at+16];pal=(s['attrs'][(tile+2)//4]>>(((tile+2)&2)))&3
   for y in range(8):
    for x in range(8):
     px=(data[y]>>(7-x)&1)|((data[y+8]>>(7-x)&1)<<1);color=s['palette'][0 if px==0 else pal*4+px]&63;actual=im.getpixel(((tile+2)*8+x,8+y))
     assert color in calibration,('New palette color needs independent calibration',n,color)
     foreground+=int(px!=0)
     if actual!=calibration[color]:bad.append([(tile+2)*8+x,8+y,color,list(calibration[color]),list(actual)])
  if bad:(a.output/'first-full-RGB-failure.json').write_text(json.dumps(dict(frame=n,bad=bad),indent=2)+'\n')
  assert not bad,(n,bad[:8]);rgb.append(dict(frame=n,classification=q['classification'],font=q['font'],all_glyph_and_background_pixels=1792,foreground_pixels=foreground,background_pixels=1792-foreground,exact_RGB_mismatches=0))
 (a.output/'actual-pair-RGB.json').write_text(json.dumps(rgb,indent=2)+'\n')
 epochs=rows(a.run/'epochs.jsonl');summaries=[]
 for e in epochs:
  d=e['dma'];pub=d['publication'];assert e['start_hardware_exact_source']and e['dma_finished_before_start']and d['data_writes']==256 and d['complete']
  assert e['start_hardware']==pub['oam']and len(pub['oam'])==256 and d['oam_address']==0
  assert d['complete']['hardware']==pub['oam']and d['complete']['completed_2004_writes']==256
  assert d['mask']&24==0 and d['complete']['mask']&24==0
  if e.get('body_row'):assert e['body_row']['exact_source']
  summaries.append(dict(frame=e['start']['frame'],start=e['start'],DMA=d['id'],publication=pub['id'],generation=pub.get('generation'),exact256=True,
                        actual_DMA_write=d['ppu'],last_data_write=d['last_data_write'],completion_margin_CPU=e['start']['cpu']-d['last_data_write']['cpu']))
 (a.output/'actual-DMA-epochs.json').write_text(json.dumps(summaries,indent=2)+'\n')
 # Independently rederive all3 source variants/5376 reference pixels, while
 # actual displayed custom HUD checks above cover Octopus1 only.
 prep=a.run.parent.parent;bundle=scoped_load(a.run/'candidate.nes');font=raw[1048592+396*1024:1048592+399*1024];assert len(font)==3072 and font==(prep/'expected-hud-fonts.bin').read_bytes()
 table=list(raw[location(bundle,'PnHudCells'):location(bundle,'PnHudCells')+84]);pixels=[]
 for variant in range(3):
  for y in range(8):
   for x in range(224):
    t=table[variant*28+x//8];at=variant*1024+t*16;pixels.append((font[at+y]>>(7-x%8)&1)|((font[at+y+8]>>(7-x%8)&1)<<1))
 assert bytes(pixels)==(prep/'expected-all5376-HUD-pixels.bin').read_bytes()and len(pixels)==5376
 completed=[];bus_counts=Counter()
 for line in(a.run/'oam-bus.jsonl').open():
  if '"kind":"4014-complete-after-postDMA-LDA"'in line:
   q=json.loads(line);assert q['completed_2004_writes']==256 and q['exact_source']and len(q['source'])==256 and q['hardware']==q['source']and q['mask']&24==0
   completed.append(dict(DMA=q['dma_id'],ppu=q['ppu'],mask=q['mask'],exact256=True,hardware_sha256=hashlib.sha256(bytes(q['hardware'])).hexdigest()))
  for kind in ['NMI-entry','NMI-return','IRQ-entry','IRQ-return-before-RTI','UpdateScreen-owner']:
   if '"kind":"'+kind+'"'in line:bus_counts[kind]+=1
 assert len(completed)==z['components']['native-result.json']['DMAs']and len({q['DMA']for q in completed})==len(completed)
 (a.output/'all-completed-hardware-transfers.json').write_text(json.dumps(completed,indent=2)+'\n')
 (a.output/'source-reference-and-bus-checks.json').write_text(json.dumps(dict(passed=True,source_reference_pixels=5376,font_bytes=3072,table_bytes=84,all3source_variants_exact=True,actual_displayed_custom_variant=1,all_unique_complete_transfers=len(completed),bus_counts=dict(bus_counts),original_native_guard_checks=z['components']['native-result.json']),indent=2)+'\n')
 chosen=[180,184,185,252,274,278,290,302,314,326,336,341,348,349,388,392,544,545,546,547,548,674,1554,1800]
 sheet=Image.new('RGB',(1536,1040),'#202020');draw=ImageDraw.Draw(sheet);samples=[]
 for i,n in enumerate(chosen):
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');x,y=i%6*256,i//6*260;sheet.paste(im,(x,y+20));draw.text((x,y),str(n),fill='white');samples.append(dict(frame=n,path=str(f.resolve()),sha256=sha(f)))
 sheet.save(a.output/'selected-full-PPU.png');(a.output/'selected-frames.json').write_text(json.dumps(samples,indent=2)+'\n')

 changed=[q['frame']for q in rgb_bind if not q['equal']]
 compare_frames=[184,547,548,674,1800]
 comparison=Image.new('RGB',(len(compare_frames)*256,520),'#202020');cd=ImageDraw.Draw(comparison);cb=[]
 for i,n in enumerate(compare_frames):
  for row,(label,folder)in enumerate([('3cee',a.historical_run),('b0',a.run)]):
   f=folder/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');comparison.paste(im,(i*256,row*260+20));cd.text((i*256,row*260),label+' '+str(n),fill='white');cb.append(dict(label=label,frame=n,path=str(f.resolve()),sha256=sha(f)))
 comparison.save(a.output/'changed-frames-before-after.png');(a.output/'changed-frame-bindings.json').write_text(json.dumps(cb,indent=2)+'\n')
 oldepochs=rows(a.historical_run/'epochs.jsonl');oldby={q['start']['frame']:q for q in oldepochs}
 oam_differences=sum(e['dma']['publication']['oam']!=oldby[e['start']['frame']]['dma']['publication']['oam']for e in epochs)

 evidence=dict(passed=True,native_run=True,component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
               six_component_result=z,actual_lifecycle_events=life,actual_terminal=terminal,actual_menu_variant_values=actual_variants,
               legacy_terminal_variant_readbacks_JSON_array_note='Original serializer emits ipairs for tables with#>0, omitting numeric key0. Original native guard explicitly requiresvariants[0..3]; actual menu-state values and selected PPUs independently include0. No frozen serializer/receipt is changed.',
               parent3cee_same_controller_comparison=dict(actual_RGB_frames_equal=sum(q['equal']for q in rgb_bind),actual_RGB_frames_changed=len(changed),outside_HUD_equal_frames=sum(q['outside_HUD_equal']for q in rgb_bind),changed_frames=changed,CSV=trace,completed_motion_rows=len(motion_rows),completed_motion_all5columns_byte_exact=True,completed_motion_sha256=sha(motion),source_OAM_epoch_differences=oam_differences),
               saved_pair_rows=len(pairs),independent_actual_RGB_pair_frames=len(rgb),RGB_mask_pixels=len(rgb)*1792,RGB_mask_mismatches=0,exact_full_glyph_and_background_RGB_pixels=len(rgb)*1792,
               independent_RGB_calibration_source='Actual3ceeframe548+its compiled oldfont+recorded palette. Every224x8pixel compared; no foreground-only predicate or zero-pixel deletion.',
               all_unique_completed_DMA_transfers=len(completed),compiled_source_reference_pixels=5376,observed_exact_completed_DMA_epochs=len(epochs),all_epochs_completed_before_render_enable=True,minimum_observed_completion_margin=min(q['completion_margin_CPU']for q in summaries),
               native_pair_classifications=dict(Counter(q['classification']for q in pairs)),
               limits='This agent executed oneb0Easy0Oct1menu1800; this tool only reviews existing immutable outputs. All6native components pass; parent3cee images/inputs are comparison evidence, not extra current runs. Source motion rows exact; all recorded presentation differences disclosed; no claim every changed pixel improves. OriginalareaFALSE/6missingoutputs/naturalBuffer2hold limitation stay unchanged. ROOT independentHard1F is separate. No additional death/Hardmatrix/globalDMC/60Hz/bodyreadability/fullcampaign/adoption/wholegoal verdict. FullRGBHUDchecks do not establish comfortable tiny-label reading.')
 (a.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 files={f.resolve()for f in a.run.iterdir()if f.is_file()}|{f.resolve()for f in a.output.iterdir()if f.is_file()}
 for f,h in json.loads((a.ready/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update([Path(__file__).resolve(),(a.ready/'proof.json').resolve(),(a.ready/'manifest.json').resolve()])
 files.update((a.historical_run/q).resolve()for q in ['inputs.csv','trace.csv','epochs.jsonl','completed-loop-motion.csv','native-result.json'])
 files.update(f.resolve()for f in a.historical_run.glob('frame-*.argb'))
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=True,native_run=True,component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
        actual_mode=0,actual_terminal_variant=1,actual_menu_variant_values=actual_variants,all6native_components_passed=True,
        native_result_sha256=sha(a.run/'lifecycle-proof.json'),same_parent_RGB_frames=sum(q['equal']for q in rgb_bind),changed_RGB_frames=len(changed),completed_motion_rows=len(motion_rows),completed_motion_byte_exact=True,independent_RGB_pair_frames=len(rgb),RGB_mask_mismatches=0,
        all_unique_completed_DMA_transfers=len(completed),compiled_source_reference_pixels=5376,observed_exact_DMA_epochs=len(epochs),selected_whole_PPU_frames=len(chosen),agent_visual_review=False,
        evidence_sha256=sha(a.output/'evidence.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),limits=evidence['limits'])
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

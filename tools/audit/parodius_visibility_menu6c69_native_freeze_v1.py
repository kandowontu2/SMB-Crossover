"""Freeze six-component current6c69menu success and finite historical comparison."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]
SHA='6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'


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
  rgb_bind.append(dict(frame=int(f.stem.split('-')[1]),current=str(f.resolve()),historical=str((a.historical_run/f.name).resolve()),sha256=sha(f),historical_sha256=sha(a.historical_run/f.name),equal=sha(f)==sha(a.historical_run/f.name)))
 assert len(rgb_bind)==1651
 (a.output/'all1651-RGB-comparison.json').write_text(json.dumps(rgb_bind,indent=2)+'\n')
 hfr={q['finished']['frame']:q for q in rows(a.run/'hud-frames.jsonl')};pairs=rows(a.run/'hud-lease-frames.jsonl');raw=(a.run/'candidate.nes').read_bytes();rgb=[]
 for q in pairs:
  assert q['passed']and q['mode']==0 and q['variant']==1
  n=q['ppu']['frame'];s=hfr[n]['start'];assert q['ppu']==s['ppu']and q['labels']==s['labels']and q['font']==s['chr'][8]
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');bg=im.getpixel((0,8));assert bg==im.getpixel((255,8));bad=[]
  for tile,t in enumerate(s['labels']):
   at=1048592+s['chr'][8+t//64]*1024+(t%64)*16;data=raw[at:at+16];pal=(s['attrs'][(tile+2)//4]>>(((tile+2)&2)))&3
   for y in range(8):
    for x in range(8):
     px=(data[y]>>(7-x)&1)|((data[y+8]>>(7-x)&1)<<1);color=s['palette'][0 if px==0 else pal*4+px]&63;actual=im.getpixel(((tile+2)*8+x,8+y))
     if(color!=(s['palette'][0]&63))!=(actual!=bg):bad.append([(tile+2)*8+x,8+y,color,list(actual)])
  assert not bad,(n,bad[:8]);rgb.append(dict(frame=n,classification=q['classification'],font=q['font'],mask_pixels=1792,mask_mismatches=0))
 (a.output/'actual-pair-RGB.json').write_text(json.dumps(rgb,indent=2)+'\n')
 epochs=rows(a.run/'epochs.jsonl');summaries=[]
 for e in epochs:
  d=e['dma'];pub=d['publication'];assert e['start_hardware_exact_source']and e['dma_finished_before_start']and d['data_writes']==256 and d['complete']
  assert e['start_hardware']==pub['oam']and len(pub['oam'])==256 and d['oam_address']==0
  if e.get('body_row'):assert e['body_row']['exact_source']
  summaries.append(dict(frame=e['start']['frame'],start=e['start'],DMA=d['id'],publication=pub['id'],generation=pub.get('generation'),exact256=True,
                        actual_DMA_write=d['ppu'],last_data_write=d['last_data_write'],completion_margin_CPU=e['start']['cpu']-d['last_data_write']['cpu']))
 (a.output/'actual-DMA-epochs.json').write_text(json.dumps(summaries,indent=2)+'\n')
 chosen=[180,252,274,278,290,302,314,326,336,341,348,349,360,384,385,388,392,544,545,546,547,548,549,1800]
 sheet=Image.new('RGB',(1536,1040),'#202020');draw=ImageDraw.Draw(sheet);samples=[]
 for i,n in enumerate(chosen):
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');x,y=i%6*256,i//6*260;sheet.paste(im,(x,y+20));draw.text((x,y),str(n),fill='white');samples.append(dict(frame=n,path=str(f.resolve()),sha256=sha(f)))
 sheet.save(a.output/'selected-full-PPU.png');(a.output/'selected-frames.json').write_text(json.dumps(samples,indent=2)+'\n')

 changed=[q['frame']for q in rgb_bind if not q['equal']]
 compare_frames=sorted(set([changed[0]-1,changed[0],changed[0]+1,changed[len(changed)//2],changed[-1],1800]))if changed else[547,548,1800]
 comparison=Image.new('RGB',(len(compare_frames)*256,520),'#202020');cd=ImageDraw.Draw(comparison);cb=[]
 for i,n in enumerate(compare_frames):
  for row,(label,folder)in enumerate([('4285',a.historical_run),('6c69',a.run)]):
   f=folder/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');comparison.paste(im,(i*256,row*260+20));cd.text((i*256,row*260),label+' '+str(n),fill='white');cb.append(dict(label=label,frame=n,path=str(f.resolve()),sha256=sha(f)))
 comparison.save(a.output/'changed-frames-before-after.png');(a.output/'changed-frame-bindings.json').write_text(json.dumps(cb,indent=2)+'\n')
 oldepochs=rows(a.historical_run/'epochs.jsonl');oldby={q['start']['frame']:q for q in oldepochs}
 oam_differences=sum(e['dma']['publication']['oam']!=oldby[e['start']['frame']]['dma']['publication']['oam']for e in epochs)

 evidence=dict(passed=True,native_run=True,component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
               six_component_result=z,actual_lifecycle_events=life,actual_terminal=terminal,actual_menu_variant_values=actual_variants,
               legacy_terminal_variant_readbacks_JSON_array_note='Original serializer emits ipairs for tables with#>0, omitting numeric key0. Original native guard explicitly requiresvariants[0..3]; actual menu-state values and selected PPUs independently include0. No frozen serializer/receipt is changed.',
               parent4285_same_controller_comparison=dict(actual_RGB_frames_equal=sum(q['equal']for q in rgb_bind),actual_RGB_frames_changed=len(changed),changed_frames=changed,CSV=trace,completed_motion_rows=len(motion_rows),completed_motion_all5columns_byte_exact=True,completed_motion_sha256=sha(motion),source_OAM_epoch_differences=oam_differences),
               saved_pair_rows=len(pairs),independent_actual_RGB_pair_frames=len(rgb),RGB_mask_pixels=len(rgb)*1792,RGB_mask_mismatches=0,
               observed_exact_completed_DMA_epochs=len(epochs),minimum_observed_completion_margin=min(q['completion_margin_CPU']for q in summaries),
               native_pair_classifications=dict(Counter(q['classification']for q in pairs)),
               limits='One current6c69Easy0Oct1menu1800 only. All6native components pass; parent4285 images/inputs are comparison evidence, not extra current runs. Source motion rows exact; wall-frame presentation differs; no claim every changed pixel improves. SeparateareaFALSE/6missingoutputs/naturalBuffer2hold limitation stay unchanged. No death/Hard/globalDMC/60Hz/bodyreadability/fullcampaign/adoption/wholegoal verdict. ActualRGBHUDmasks do not certify dense-label readability.')
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
        observed_exact_DMA_epochs=len(epochs),selected_whole_PPU_frames=len(chosen),agent_visual_review=False,
        evidence_sha256=sha(a.output/'evidence.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),limits=evidence['limits'])
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

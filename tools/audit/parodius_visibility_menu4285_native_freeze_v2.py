"""Freeze six-component current4285menu success and finite historical comparison."""
from pathlib import Path
from collections import Counter
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]
SHA='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'


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
  assert new==old;trace[name]=dict(rows=len(new),parsed_equal=True,current_sha256=sha(a.run/name),historical_sha256=sha(a.historical_run/name))
 rgb_bind=[]
 for f in sorted(a.run.glob('frame-*.argb')):
  assert sha(f)==sha(a.historical_run/f.name),f.name;rgb_bind.append(dict(frame=int(f.stem.split('-')[1]),current=str(f.resolve()),historical=str((a.historical_run/f.name).resolve()),sha256=sha(f)))
 assert len(rgb_bind)==1651
 (a.output/'all1651-RGB-equality.json').write_text(json.dumps(rgb_bind,indent=2)+'\n')
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
 evidence=dict(passed=True,native_run=True,component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
               six_component_result=z,actual_lifecycle_events=life,actual_terminal=terminal,actual_menu_variant_values=actual_variants,
               legacy_terminal_variant_readbacks_JSON_array_note='Original serializer emits ipairs for tables with#>0, omitting numeric key0. Original native guard explicitly requiresvariants[0..3]; actual menu-state values and selected PPUs independently include0. No frozen serializer/receipt is changed.',
               historical5354_same_controller_comparison=dict(actual_RGB_frames_identical=1651,CSV=trace),
               saved_pair_rows=len(pairs),independent_actual_RGB_pair_frames=len(rgb),RGB_mask_pixels=len(rgb)*1792,RGB_mask_mismatches=0,
               observed_exact_completed_DMA_epochs=len(epochs),minimum_observed_completion_margin=min(q['completion_margin_CPU']for q in summaries),
               native_pair_classifications=dict(Counter(q['classification']for q in pairs)),
               limits='One current4285Easy0Oct1menu1800 only. All6native components pass; historical5354 images/inputs are comparison evidence, not extra current runs. SeparateareaFALSE/6missingoutputs/naturalBuffer2hold limitation stay unchanged. No death/Hard/globalDMC/60Hz/bodyreadability/fullcampaign/adoption/wholegoal verdict. ActualRGBHUDmasks do not certify dense-label readability.')
 (a.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 files={f.resolve()for f in a.run.iterdir()if f.is_file()}|{f.resolve()for f in a.output.iterdir()if f.is_file()}
 for f,h in json.loads((a.ready/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update([Path(__file__).resolve(),(a.ready/'proof.json').resolve(),(a.ready/'manifest.json').resolve()])
 files.update((a.historical_run/q).resolve()for q in ['inputs.csv','trace.csv'])
 files.update(f.resolve()for f in a.historical_run.glob('frame-*.argb'))
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=True,native_run=True,component_only=True,goal_complete=False,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
        actual_mode=0,actual_terminal_variant=1,actual_menu_variant_values=actual_variants,all6native_components_passed=True,
        native_result_sha256=sha(a.run/'lifecycle-proof.json'),same_historical_RGB_frames=1651,independent_RGB_pair_frames=len(rgb),RGB_mask_mismatches=0,
        observed_exact_DMA_epochs=len(epochs),selected_whole_PPU_frames=len(chosen),agent_visual_review=False,
        evidence_sha256=sha(a.output/'evidence.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),limits=evidence['limits'])
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

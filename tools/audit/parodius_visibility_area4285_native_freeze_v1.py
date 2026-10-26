"""Freeze the actual4285 pipe success plus unmet naturalBuffer2hold, without retry."""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows=lambda p:[json.loads(s)for s in Path(p).read_text().splitlines()]
SHA='4285d35db234ecdaf7c561f721c0aa8798545f9937e933acf5ab3e3f0b642682'


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 z=json.loads((a.run/'lifecycle-proof.json').read_text());assert not z['passed']and z['ROM_sha256']==SHA
 assert all(x is None for x in z['component_bindings'].values())and len(z['component_bindings'])==6
 assert 'Actual pipe area transition and pending full HUD retained through real nonempty Buffer2 then catch-up'in(a.run/'candidate-run.log').read_text()
 life=rows(a.run/'lifecycle-events.jsonl');hud=rows(a.run/'hud-events.jsonl');epochs=rows(a.run/'epochs.jsonl');pairs=rows(a.run/'hud-lease-frames.jsonl')
 hfr={q['finished']['frame']:q for q in rows(a.run/'hud-frames.jsonl')};cfg=json.loads((a.run/'config.json').read_text());raw=(a.run/'candidate.nes').read_bytes()
 counts=Counter(x['kind']for x in life);terminal=next(x for x in life if x['kind']=='terminal-fixture-state')
 assert counts['actual-native-pipe-request']==counts['actual-native-vertical-pipe-owner']==counts['actual-area-change']==1
 assert terminal['area_changes']==1 and terminal['area_loads']==2 and terminal['vertical_pipe_frames']==48 and terminal['deaths']==0
 assert counts['pending-full-labels-meet-Buffer2']==counts['actual-Buffer2-pending-retained']==0
 pipe=next(x for x in life if x['kind']=='actual-native-pipe-request');change=next(x for x in life if x['kind']=='actual-area-change')
 b2=[x for x in life if x['kind']=='genuine-Buffer2-flush']
 full=[x for x in hud if x['kind']=='entry-PnHudPreUpdateScreen'and x['ram']['X5HudChrUpper']&128 and x['ram']['InvHudActive']==0]
 assert len(full)==2 and all(x['ram']['VRAM_Buffer_AddrCtrl']==0 and x['ram']['VRAM_Buffer2_Offset']==0 for x in full)
 full_summary=[]
 for x in full:
  last=max((q for q in b2 if q['ppu']['cpu']<x['ppu']['cpu']),key=lambda q:q['ppu']['cpu'])
  full_summary.append(dict(actual_full_pending_NMI=x,last_prior_Buffer2=last,frame_gap=x['ppu']['frame']-last['ppu']['frame']))
 assert [x['frame_gap']for x in full_summary]==[10,24]
 assert not any(x['ppu']['frame']>=change['ppu']['frame']for x in b2)
 fresh=[];dma=[]
 for e in epochs:
  d=e['dma'];pub=d['publication'];assert e['start_hardware_exact_source']and e['dma_finished_before_start']and d['data_writes']==256 and d['complete']
  assert e['start_hardware']==pub['oam']and len(pub['oam'])==256 and d['oam_address']==0
  if e.get('body_row'):assert e['body_row']['exact_source']
  q=dict(frame=e['start']['frame'],start=e['start'],DMA=d['id'],publication=pub['id'],generation=pub.get('generation'),
         exact256=True,actual_DMA_write=d['ppu'],last_data_write=d['last_data_write'],completion_margin_CPU=e['start']['cpu']-d['last_data_write']['cpu'])
  dma.append(q)
  if e['start']['frame']>change['ppu']['frame']and pub.get('generation')==terminal['phase']['start']['game_generation']and pub.get('transaction'):
   fresh.append(pub['transaction']['id'])
 fresh_count=len(set(fresh));assert fresh_count>=45
 (a.output/'actual-DMA-epochs.json').write_text(json.dumps(dma,indent=2)+'\n')
 # Reconstruct saved actual display checks independently; final2600 has a
 # start/terminal metadata observation but no endFrame capture after assertion.
 rgb=[];colors=defaultdict(Counter);metadata_only=[]
 for q in pairs:
  assert q['passed']and q['mode']==0 and q['variant']==1
  custom=q['labels']==cfg['hud_labels']['1']and q['font']==396;blank=q['labels']==[36]*28 and q['font']==0
  assert custom or blank
  n=q['ppu']['frame']
  if n not in hfr:
   assert n==2600;metadata_only.append(q);continue
  s=hfr[n]['start'];assert s['ppu']==q['ppu']and s['labels']==q['labels']and s['chr'][8]==q['font']
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');bg=im.getpixel((0,8));assert bg==im.getpixel((255,8));bad=[]
  for tile,t in enumerate(s['labels']):
   data=raw[1048592+s['chr'][8+t//64]*1024+(t%64)*16:1048592+s['chr'][8+t//64]*1024+(t%64)*16+16]
   pal=(s['attrs'][(tile+2)//4]>>(((tile+2)&2)))&3
   for y in range(8):
    for x in range(8):
     px=(data[y]>>(7-x)&1)|((data[y+8]>>(7-x)&1)<<1);color=s['palette'][0 if px==0 else pal*4+px]&63;actual=im.getpixel(((tile+2)*8+x,8+y));colors[color][actual]+=1
     if(color!=(s['palette'][0]&63))!=(actual!=bg):bad.append([(tile+2)*8+x,8+y,color,list(actual)])
  assert not bad,(n,bad[:8]);rgb.append(dict(frame=n,classification=q['classification'],font=q['font'],raw_sha256=sha(f),mask_pixels=1792,mask_mismatches=0))
 assert len(metadata_only)==1
 (a.output/'actual-pair-RGB.json').write_text(json.dumps(rgb,indent=2)+'\n')
 selected=[1221,1222,1261,1361,1362,1363,1364,1380,1400,1413,1414,1416,1424,1435,1457,1458,1459,1460,1461,1500,1600,2000,2598,2599]
 sheet=Image.new('RGB',(1536,1040),'#202020');draw=ImageDraw.Draw(sheet);samples=[]
 for i,n in enumerate(selected):
  f=a.run/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');x,y=i%6*256,i//6*260;sheet.paste(im,(x,y+20));draw.text((x,y),str(n),fill='white');samples.append(dict(frame=n,path=str(f.resolve()),sha256=sha(f)))
 sheet.save(a.output/'selected-full-PPU.png');(a.output/'selected-frames.json').write_text(json.dumps(samples,indent=2)+'\n')
 evidence=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,original_aggregate=z,
       actual_terminal_event=terminal,actual_pipe_request=pipe,actual_area_change=change,all_lifecycle_events=life,
       exact_failed_requirements=dict(pending_full_HUD_Buffer2_holds=0,new_area_pending_holds=0,catchup_after_hold=False),
       other_coverage_observed=dict(pipe_requests=1,vertical_pipe_updates=48,actual_area_loads=2,changed_area=True,
             post_pipe_resets=sum(x['kind']=='publication-generation-changed'and x.get('reason')=='VvReset-native-entry'and x['ppu']['cpu']>pipe['ppu']['cpu']for x in life),
             fresh_post_area_draw_transaction_lower_bound=fresh_count,actual_Buffer2_flushes=len(b2),deaths=0),
       full_HUD_NMI_chronology=full_summary,new_area_nonempty_Buffer2_flushes=0,
       all_observed_epochs_exact256=len(epochs),minimum_observed_completion_margin=min(x['completion_margin_CPU']for x in dma),
       pair_rows=len(pairs),all_pair_predicates_passed=True,actual_RGB_pair_frames=len(rgb),RGB_mask_pixels=len(rgb)*1792,RGB_mask_mismatches=0,
       terminal2600_start_metadata_only=metadata_only,raw_RGB_frames=len(list(a.run.glob('frame-*.argb'))),last_raw_RGB_frame=2599,
       interpretation='Genuine natural pipe/load/area/reset and meaningful fresh-area publication occurred. Only required natural pending-fullHUD/nonemptyBuffer2 hold/catchup is missing; terminal assertion stops before all6finalizers. No ROM fault is demonstrated by an absent conditional event. Source allows ctrl6 deferral when those owners coincide, but this replay has only2fullpendingNMIs, bothctrl0; global natural reachability or impossibility is not proved.',
       adoption_boundary='Keep originalaggregateFALSE. Observed native menu/death/area behavior and independent source/CPU conditionalBuffer2protocol are separately usable evidence. Do not claim naturalBuffer2hold coverage, all6native pass, globaltiming or fullgoal. No scheduling/game-source change or further controller campaign is justified merely to manufacture this event; ROOT may assess adoption with this explicit finite scope.',
       limits='One failed coverage profile, no retry. Original6missing outputs remain missing. Independent saved observations do not backfill terminal receipts. ActualRGBHUDmask scope only; selectedwholePPUreview separate. Hard/othervariants/globalDMC/60Hz/bodyvisibility/fullcampaign remain open.')
 (a.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
 files={f.resolve()for f in a.run.iterdir()if f.is_file()}|{f.resolve()for f in a.output.iterdir()if f.is_file()}
 for f,h in json.loads((a.ready/'manifest.json').read_text()).items():assert sha(f)==h;files.add(Path(f).resolve())
 files.update([Path(__file__).resolve(),(a.ready/'proof.json').resolve(),(a.ready/'manifest.json').resolve()])
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=SHA,
        actual_natural_pipe_and_changed_area_observed=True,missing_pending_Buffer2_hold_coverage=True,all6terminal_outputs_absent_preserved=True,
        fresh_post_area_draw_transaction_lower_bound=fresh_count,actual_Buffer2_flushes=len(b2),full_pending_NMIs=len(full),
        observed_DMA_epochs=len(epochs),pair_rows=len(pairs),independent_RGB_frames=len(rgb),RGB_mask_mismatches=0,
        saved_actual_RGB_frames=evidence['raw_RGB_frames'],last_raw_RGB_frame=2599,selected_whole_PPU_frames=len(selected),human_visual_review=False,
        evidence_sha256=sha(a.output/'evidence.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),
        ready_sha256=sha(a.ready/'proof.json'),limits=evidence['limits'])
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()

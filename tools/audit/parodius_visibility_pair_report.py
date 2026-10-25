"""Bind the strict private pilot to the failed same-controller DMA baseline."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from PIL import Image
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def lines(p):return [json.loads(s)for s in p.read_text(encoding='utf-8').splitlines()]
def brief(x):return {k:v for k,v in x.items()if k not in ['state','hardware','source','ram','packet']}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 paths=[a.baseline,a.candidate];proofs=[read(x/'proof.json')for x in paths];native=[read(x/'native-result.json')for x in paths];assert not proofs[0]['passed']and proofs[1]['passed'];configs=[read(x/'config.json')for x in paths];assert configs[0]['diagnostic']is True and configs[1]['diagnostic']is False
 buses=[lines(x/'oam-bus.jsonl')for x in paths];epochs=[lines(x/'epochs.jsonl')for x in paths];pubs=[{x['dma']['publication']['id']:x['dma']['publication']for x in es}for es in epochs];common=sorted(set(pubs[0])&set(pubs[1]));assert all(pubs[0][i]['oam']==pubs[1][i]['oam']for i in common)
 def hardware_trace(bus,kind,keys):return [{k:x[k]for k in keys}for x in bus if x['kind']==kind]
 for kind,keys in [('2007-data',['value','vram_address']),('CHR-write',['address','value','upper','physical']),('2001-mask',['value'])]:assert hardware_trace(buses[0],kind,keys)==hardware_trace(buses[1],kind,keys),kind
 for x in native[0]:
  if x in ['updates','publications','DMAs','nmis','wall','actual_mode','actual_variant','min_sampled_SP']:assert native[0][x]==native[1][x],x
 assert {x['ppu']['scanline']for x in buses[1]if x['kind']=='IRQ-entry'}=={31}
 times=[]
 for ident in [2,64,109]:
  pair=[]
  for bus in buses:
   start=next(x for x in bus if x['kind']=='4014-start'and x['dma_id']==ident);complete=next(x for x in bus if x['kind']=='4014-complete-after-next-LDX'and x['dma_id']==ident);frame=start['ppu']['frame'];wrapper=next(x for x in bus if x['kind']=='routine-return'and x['name']=='SamusFreezeUpdateScreen'and x['ppu']['frame']==frame);pair.append(dict(start=brief(start),complete=brief(complete),wrapper=brief(wrapper)))
  times.append(dict(DMA=ident,baseline=pair[0],candidate=pair[1]))
 rgb=[]
 for frame in range(570,621):
  old=np.fromfile(a.baseline/f'frame-{frame:06}.argb',dtype='<u4').reshape(240,256);new=np.fromfile(a.candidate/f'frame-{frame:06}.argb',dtype='<u4').reshape(240,256);diff=old!=new;coverage=np.zeros((240,256),bool);es=[next(x for x in ee if x['start']['frame']==frame)for ee in epochs];oams=[es[0]['body_row']['hardware'],es[1]['body_row']['hardware']]
  for index in range(64):
   parts=[oam[index*4:index*4+4]for oam in oams]
   if parts[0]==parts[1]:continue
   for y,tile,attr,x in parts:
    if y<239:coverage[y+1:min(240,y+17),x:min(256,x+8)]=True
  assert not np.any(diff&~coverage),('RGB change outside changed OAM records',frame)
  yy,xx=np.where(diff);q=dict(frame=frame,changed_pixels=int(diff.sum()),outside_changed_OAM_footprints=0,raw_baseline_sha256=sha(a.baseline/f'frame-{frame:06}.argb'),raw_candidate_sha256=sha(a.candidate/f'frame-{frame:06}.argb'))
  if diff.any():q['bbox']=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
  rgb.append(q)
  if frame in [585,586,587,612,613,614,615]:
   for side,image in [('baseline',old),('candidate',new)]:
    dest=a.output/f'{side}-actual-PPU-{frame:06}.png';Image.frombytes('RGBA',(256,240),image.tobytes(),'raw','BGRA').convert('RGB').save(dest)
 (a.output/'matched-timings.json').write_text(json.dumps(times,indent=2)+'\n',encoding='utf-8');(a.output/'actual-RGB-comparison.json').write_text(json.dumps(rgb,indent=2)+'\n',encoding='utf-8')
 complete=[x for x in buses[1]if x['kind']=='4014-complete-after-next-LDX'];latest=max(complete,key=lambda x:x['ppu']['scanline']*341+x['ppu']['cycle']);assert all(x['exact_source']and x['completed_2004_writes']==256 for x in complete)
 q=dict(passed=True,goal_complete=False,ROM_before=native[0]['ROM_sha256'],ROM_after=native[1]['ROM_sha256'],baseline_failed_proof_sha256=sha(a.baseline/'proof.json'),candidate_strict_proof_sha256=sha(a.candidate/'proof.json'),script_sha256=sha(Path(__file__)),strict_config_verified=True,native_result_diagnostic_tag_correction='native-result diagnostic=true is an old hardcoded descriptive tag. Actual frozen candidate config diagnostic=false; source/DMA/body-row assertions were fatal. No native receipt edited.',common_publication_OAM_images_exact=len(common),PPUDATA_values_addresses_exact=True,CHR_order_values_exact=True,PPUMASK_value_order_exact=True,all_updates_publications_DMA_NMI_counts_exact=True,physical_IRQ_scanlines=[31],candidate_latest_completed_DMA=brief(latest),latest_completion_margin_before_prerender_PPU_cycles=341-latest['ppu']['cycle'],candidate_native=native[1],changed_actual_PPU_frames=[x for x in rgb if x['changed_pixels']],scope='Matched Octopus Easy variant1 controller640 pilot only. Full51-frame actual RGB comparison changes only613/614,88pixels each, entirely within the changed hardware OAM record footprints; remaining49 frames byte-exact. Source art/OAM publication/VRAM/CHR values are unchanged. No all-packet budget, other-mode/variant, stage-clear or sprite-limit/priority closure. Latest DMA finishes260:311, only30PPUcycles beforepreRender. Future broader fixtures must retain that narrow measured limit.',bindings={p.name:sha(p)for p in sorted(a.output.iterdir())if p.is_file()})
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,proof_sha256=sha(a.output/'proof.json'),changed_frames=q['changed_actual_PPU_frames'])))
if __name__=='__main__':main()

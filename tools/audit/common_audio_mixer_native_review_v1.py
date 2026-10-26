"""Saved same-controller f4efd/3b450 integrity, DMA cadence and image review."""
from pathlib import Path
import argparse,bisect,json,traceback
import numpy as np
from PIL import Image,ImageDraw
from smb3_host_current3b_cpu_v1 import D,sha,put
from mm_proto_priority450_review_v1 import load,rawbytes

BASE=D/'root-presentation450-3b112-v1';EXPECTED='f4efd9ccb222501877dfc77c5189841aa9dc500756736f15aaf02a6994ae8c0f'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 try:
  old,new=[load(q)for q in [BASE,a.candidate]];assert old['result']['ROM_sha256']=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287'and new['result']['ROM_sha256']==EXPECTED
  assert len(old['DMAs'])==402 and len(old['index'])==275
  assert(BASE/'prefix.csv').read_bytes()==(a.candidate/'prefix.csv').read_bytes()
  inputs=lambda z:[(q['poll'],q['ppu']['frame'],q['mask'])for q in z['logs']if q['kind']=='input'];left,right=inputs(old),inputs(new);same_inputs=left==right;assert len(left)==449
  times=[[q['complete']['cpu']for q in z['DMAs']]for z in [old,new]];assert all(t==sorted(t)for t in times)
  rows=[]
  for i,(l,r)in enumerate(zip(old['index'],new['index'])):
   f=int(l['ppuFrame']);assert f==int(r['ppuFrame']);counts=[bisect.bisect_right(t,int(s['cpuCycle']))for t,s in zip(times,[l,r])];snapshots=[z['DMAs'][n-1]if n else None for z,n in zip([old,new],counts)];different=np.any(old['rgb'][i]!=new['rgb'][i],axis=2);yy,xx=np.nonzero(different)
   rows.append(dict(frame=f,baseline_completed_DMA=counts[0],candidate_completed_DMA=counts[1],DMA_delta=counts[1]-counts[0],baseline_capture_cpu=int(l['cpuCycle']),candidate_capture_cpu=int(r['cpuCycle']),baseline_last_DMA=snapshots[0]['complete']if snapshots[0]else None,candidate_last_DMA=snapshots[1]['complete']if snapshots[1]else None,raw_OAM_equal=(rawbytes(snapshots[0]['source'])if snapshots[0]else None)==(rawbytes(snapshots[1]['source'])if snapshots[1]else None),different_RGB_pixels=int(different.sum()),difference_box=None if not len(xx)else[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]))
  deficits=[r for r in rows if r['DMA_delta']<0];different=[r for r in rows if r['different_RGB_pixels']];cadence=len(new['DMAs'])>=len(old['DMAs'])and not deficits and same_inputs
  selected=[184,372,403,438,444,450];gap=12;panelW,panelH=256,258;sheet=Image.new('RGB',(2*panelW+3*gap,len(selected)*(panelH+gap)+gap),'#35354a');draw=ImageDraw.Draw(sheet)
  for row,frame in enumerate(selected):
   for col,(z,label)in enumerate([(old,'3bbaseline'),(new,'f4efdcandidate')]):
    x=gap+col*(panelW+gap);y=gap+row*(panelH+gap);draw.text((x,y),f'{label} actual{frame}',fill='white');sheet.paste(Image.fromarray(z['rgb'][frame-176]),(x,y+18))
  sheet.save(a.output/'paired-selected-wholeframes.png')
  if different:
   frame=different[0]['frame']
   for z,label in[(old,'baseline'),(new,'candidate')]:Image.fromarray(z['rgb'][frame-176]).save(a.output/f'first-difference-{label}-{frame}.png')
  summary=dict(passed=cadence,review_complete=True,native_run=True,adopted=False,baseline_ROM_sha256=old['result']['ROM_sha256'],candidate_ROM_sha256=EXPECTED,baseline_actual_DMAs=len(old['DMAs']),candidate_actual_DMAs=len(new['DMAs']),candidate_all256_hardware_destination_and_disabled_timing_exact=True,scoped_safe_enables=new['result']['scoped_enables'],original_all_NMI_IRQ_SMC_guards_passed=True,actual_input_poll_frame_masks_equal=same_inputs,actual_input_polls=[len(left),len(right)],input_differences=[dict(index=i,baseline=x,candidate=y)for i,(x,y)in enumerate(zip(left,right))if x!=y],total_DMA_delta=len(new['DMAs'])-len(old['DMAs']),visible_prefix_deficit_frames=len(deficits),first_visible_prefix_deficit=deficits[0]if deficits else None,native_no_harm_cadence_pass=cadence,lossless_pairs=len(rows),RGB_byte_identity_pass=not different,different_RGB_pairs=len(different),first_RGB_difference=different[0]if different else None,selected_wholeframe_pairs=selected,manual_image_review_required=True,checker_sha256=sha(__file__),limits='One exactMegaEasy450 shared-audio regression only. Qualified original observer/guards remain; independent full256DMAs and275PPU pairs. No actual APU waveform logging, source-music integration, allroster/routes/everyitem or sprite-fairness claim. RGB identity is separate; any difference/deficit remains explicit, never assumed harmless.')
  put(a.output/'proof.json',summary);put(a.output/'all275-paired-observations.json',rows)
  files={Path(__file__)}|{z['root']/n for z in [old,new]for n in ['direct.argb','direct-index.csv','timing.jsonl','prefix.csv','native-receipt.json','result.json','launch.json','readiness.json']}|{q for q in a.output.iterdir()if q.is_file()};put(a.output/'bindings.json',{str(q.resolve()):sha(q)for q in sorted(files)})
  print(json.dumps({k:summary[k]for k in['passed','candidate_actual_DMAs','total_DMA_delta','visible_prefix_deficit_frames','actual_input_poll_frame_masks_equal','RGB_byte_identity_pass','different_RGB_pairs']}))
 except Exception as e:put(a.output/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()

"""Freeze ONE menu result and compare existing raw frames; no new captures/sheets."""
from pathlib import Path
import argparse, hashlib, json
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(p.read_text(encoding='utf-8'))
def put(p,z):assert not p.exists(),p;p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=a.ready/'readiness.json';assert sha(ready)=='d093f142f4301dab015bc2d4f4483a2f66561d774c97d74555d3be10d4b24b33';r=get(ready);bindings=get(a.ready/'bindings.json');assert len(bindings)==1156 and all(sha(f)==h for f,h in bindings.items())
 grant=a.ready/'ROOT-menu-grant.json';assert sha(grant)=='c2c6f94bceed891097278a30614aab6b813f9b52c2ea4bbb97eea28f8f8b877d'
 out=Path(next(c for c in r['profiles']if c['name']=='menu')['output']);result=get(out/'regression-result.json');assert result['profile']=='menu'and result['ROM_sha256']==r['ROM_sha256'];old=D/'parodius-menu-clean731-preparation-v1/menu/baseline-early'
 frame_rows=[];different=[]
 for frame in range(150,1801):
  before=old/f'frame-{frame:06d}.argb';after=out/before.name
  row=dict(frame=frame,baseline=str(before),candidate=str(after),baseline_exists=before.is_file(),candidate_exists=after.is_file())
  if before.is_file()and after.is_file():
   x,y=before.read_bytes(),after.read_bytes();assert len(x)==len(y)==256*240*4;row.update(baseline_sha256=hashlib.sha256(x).hexdigest(),candidate_sha256=hashlib.sha256(y).hexdigest(),raw_equal=x==y)
   if x!=y:row['different_RGB_pixels']=sum(x[i:i+3]!=y[i:i+3]for i in range(0,len(x),4));different.append(frame)
  else:row['raw_equal']=False;different.append(frame)
  frame_rows.append(row)
 native=get(out/'native-result.json')if(out/'native-result.json').exists()else{};timing=get(out/'menu-timing-native-result.json')if(out/'menu-timing-native-result.json').exists()else{};life=get(out/'lifecycle-native-result.json')if(out/'lifecycle-native-result.json').exists()else{}
 bn=get(old/'native-result.json');bt=get(old/'menu-timing-native-result.json')
 counters={key:dict(baseline=bn[key],candidate=native.get(key))for key in ['updates','publications','DMAs','nmis','dma_checks','chr_checks','min_sampled_SP','all_boot_UpdateScreen_C116_owner_checks']}
 timings={key:dict(baseline=bt[key],candidate=timing.get(key))for key in ['all_identity_completed_DMAs','scoped_render_enables','late_enables','hardware_mismatches','menu_start_owner_frames']}
 equal_csv={name:sha(out/name)==sha(old/name)for name in ['inputs.csv','trace.csv']if(out/name).exists()and(old/name).exists()}
 put(a.output/'raw-frame-comparison.json',frame_rows);put(a.output/'counts-and-timing.json',dict(counters=counters,timing=timings,original_input_and_trace_byte_equality=equal_csv))
 all_frames_equal=len(frame_rows)==1651 and not different
 all_original_guards=result.get('passed',False)and result.get('all_original_six_and_additive_timing',False)
 proof=dict(passed=all_original_guards and all_frames_equal,native_run=True,component_only=True,adopted=False,ROM_sha256=r['ROM_sha256'],launches=1,retries=0,worker_released=True,all_original_six_and_additive_timing_pass=all_original_guards,actual_mode=native.get('actual_mode'),actual_terminal_variant=native.get('actual_variant'),all1651_raw_frames_equal_historical731=all_frames_equal,different_frames=different,whole_frame_comparison_scope='Existing captured BGRA256x240 frames150..1800 inclusive. Raw equality covers every pixel/channel; this proves no new image difference against the historically reviewed731 capture, not that every old sprite/art detail is ideal.',actual_counters=counters,actual_timing=timings,menu_cancel=life.get('menu_return'),menu_reentry=life.get('menu_reentry'),source_epoch_full256_SMC_stack_CHR_and_IRQ_guards='Original unchanged native components; do not replace these with pixel equality.',Hard1F_native_run=False,report='No image or screenshot bundle generated; original old and new raw images retained. Hard1F remains ungranted/unrun.',tool_sha256=sha(__file__))
 files=[ready,a.ready/'bindings.json',a.ready/'command.json',grant,Path(__file__).resolve(),a.output/'raw-frame-comparison.json',a.output/'counts-and-timing.json']
 files+=list(f for f in out.iterdir()if f.is_file())
 files+=list(f for f in a.ready.glob('menu-host.*')if f.is_file())
 for f in files:bindings[str(f.resolve())]=sha(f)
 for row in frame_rows:
  if row['baseline_exists']:bindings[row['baseline']]=row['baseline_sha256']
 put(a.output/'bindings.json',bindings);proof.update(bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json'),readiness_sha256=sha(ready),raw_frame_comparison_sha256=sha(a.output/'raw-frame-comparison.json'),counters_sha256=sha(a.output/'counts-and-timing.json'))
 put(a.output/'proof.json',proof);print(json.dumps(proof,indent=2))
if __name__=='__main__':main()

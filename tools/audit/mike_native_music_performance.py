"""Compare completed work, physical frames and draws for two exact native runs."""
from pathlib import Path
from collections import defaultdict
import argparse,csv,hashlib,json

def rows(p):
 with p.open(newline='')as f:return list(csv.DictReader(f))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();result=dict(passed=False,scope='Same arranged mode-verified600 completed game updates; explicitly compares update work, physical frames and draw counts. Not a whole-level or universal lag proof.',tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 runs=[]
 for folder in [a.baseline,a.candidate]:
  proof=json.loads((folder/'native-result.json').read_text());assert proof['passed']
  frames=rows(folder/'tmnt-performance-frames.csv');calls=rows(folder/'tmnt-performance-calls.csv');game=rows(folder/'gameplay.csv');assert len(game)==600 and proof['proof.json']['completed_game_updates']==600
  loops=[v for v in calls if v['name']=='GameLoop'];assert len(loops)==600
  # A GameLoop enters before its movement hook advances the phase. Assign
  # its completed work by the corresponding actual movement-log row.
  for i,row in enumerate(loops):row['work_phase']=game[i]['phase']
  phases={}
  for name in ['idle','walk','enemies','primary','special']:
   f=[v for v in frames if v['phase']==name];c=[v for v in loops if v['work_phase']==name];draw=[v for v in calls if v['name']=='DrawAllMetasprites'and v['phase']==name]
   phases[name]=dict(completed_game_loops=len(c),draw_calls=len(draw),physical_frame_rows=len(f),frame_movement_updates=sum(int(v['updates'])for v in f),frame_draw_calls=sum(int(v['draws'])for v in f),lag_NMIs=sum(int(v['lagNmis'])for v in f),game_loop_mean_CPU_cycles=sum(int(v['cpuCycles'])for v in c)/len(c),game_loop_mean_ISR_cycles=sum(int(v['isrCycles'])for v in c)/len(c),game_loop_peak_CPU_cycles=max(int(v['cpuCycles'])for v in c))
  runs.append(dict(ROM_sha256=proof['ROM_sha256'],native_receipt_sha256=hashlib.sha256((folder/'native-result.json').read_bytes()).hexdigest(),all_native_frames=proof['proof.json']['frames'],completed_work_rows=len(game),phases=phases))
 old,new=[rows(x/'gameplay.csv')for x in [a.baseline,a.candidate]]
 def work(v):return {k:x for k,x in v.items()if k!='wall'}
 assert list(map(work,old))==list(map(work,new)),'Actual movement/combat/enemy work diverged'
 keys=['completed_game_loops','draw_calls','physical_frame_rows','frame_movement_updates','frame_draw_calls','lag_NMIs']
 extra=[];regressions=[]
 for name in runs[0]['phases']:
  x,y=[r['phases'][name]for r in runs]
  assert x['completed_game_loops']==y['completed_game_loops']==120
  for k in keys:
   if x[k]!=y[k]:
    row=dict(phase=name,measure=k,baseline=x[k],candidate=y[k]);extra.append(row)
    # Better draw/lag counts are reported, not classified as regressions.
    bad=(y[k]<x[k])if k in ['draw_calls','frame_draw_calls']else(y[k]>x[k])if k in ['physical_frame_rows','lag_NMIs']else True
    if bad:regressions.append(row)
 if runs[1]['all_native_frames']>runs[0]['all_native_frames']:regressions.append(dict(measure='total_physical_frames',baseline=runs[0]['all_native_frames'],candidate=runs[1]['all_native_frames']))
 result.update(passed=not regressions,baseline=runs[0],candidate=runs[1],exact_gameplay_work_excluding_wall=True,count_differences=extra,regressions=regressions,no_extra_skipped_draws_or_lag=not regressions)
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed']else 1)
if __name__=='__main__':main()

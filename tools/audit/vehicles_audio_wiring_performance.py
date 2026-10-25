"""Compare one bounded 600-update current-source native TMNT music arena."""
from pathlib import Path
import argparse,csv,hashlib,json,statistics


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(p):
 with p.open()as f:return list(csv.DictReader(f))


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['baseline','candidate','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();assert not a.output.exists()
 old=json.loads((a.baseline/'native-result.json').read_text());new=json.loads((a.candidate/'native-result.json').read_text())
 assert old['passed']and new['passed']and old['variant']==new['variant']and old['hard']==new['hard']
 assert old['dependencies']==new['dependencies'],'Same bound controller and observers'
 states=[rows(d/'gameplay.csv')for d in [a.baseline,a.candidate]]
 assert all(len(s)==600 for s in states)
 differences=[];valid=True
 for i,(x,y)in enumerate(zip(*states)):
  diff={k:[x[k],y[k]]for k in x if x[k]!=y[k]}
  if any(k!='input'for k in diff):valid=False
  if diff:differences.append(dict(update=i,fields=diff))
 phases={};no_added=True
 for phase in ['idle','walk','enemies','primary','secondary']:
  result={}
  for label,folder,state in zip(['old','new'],[a.baseline,a.candidate],states):
   assert sum(q['phase']==phase for q in state)==120
   if phase=='enemies':assert sum(q['phase']==phase and(int(q['enemy0'])or int(q['enemy1']))>0 for q in state)==120
   spans=[q for q in rows(folder/'tmnt-performance-calls.csv')if q['phase']==phase]
   frames=[q for q in rows(folder/'tmnt-performance-frames.csv')if q['phase']==phase]
   r=dict(lag_NMIs=sum(int(q['lagNmis'])for q in frames),physical_frames=len(frames),
          draws=sum(q['name']=='DrawAllMetasprites'for q in spans))
   for name in ['GameLoop','DrawAllMetasprites','TnDrawEquipment']:
    r[name+'_mean_foreground_cycles']=statistics.mean(int(q['cpuCycles'])for q in spans if q['name']==name)
   result[label]=r
  result['added_lag_NMIs']=result['new']['lag_NMIs']-result['old']['lag_NMIs']
  no_added&=result['added_lag_NMIs']<=0;phases[phase]=result
 q=dict(passed=valid and no_added,measurement_valid=valid,performance_gate_passed=valid and no_added,
        ROM_sha256=new['ROM_sha256'],baseline_ROM_sha256=old['ROM_sha256'],variant=new['variant'],hard=new['hard'],
        phases=phases,all_recorded_state_differences=differences,
        trace_hashes=[sha(d/'gameplay.csv')for d in [a.baseline,a.candidate]],
        native_result_hashes=[sha(d/'native-result.json')for d in [a.baseline,a.candidate]],
        scope='One representative arranged 600-update component, 120 updates per phase. '
              'Every non-input gameplay difference invalidates the comparison; all controller samples retained. '
              'Foreground cycles exclude ISR bodies and include real DMA stalls. No campaign or universal60Hz claim.')
 a.output.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));return 0 if q['passed']else 2


if __name__=='__main__':raise SystemExit(main())

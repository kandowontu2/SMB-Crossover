"""Summarize measured foreground CPU spans and native updates per video frame."""
from pathlib import Path
import argparse,csv,hashlib,json,statistics


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 summaries={};bindings={}
 for label,path in(('before',args.before),('after',args.after)):
  path=path.resolve();binding=json.loads((path/'results.json').read_text());assert binding['exit']==0 and binding['behavior']=='easy'and not binding['outlines']
  f=path/'build/verification';call_path=f/'roll-performance-calls.csv';frame_path=f/'roll-performance-frames.csv'
  calls=list(csv.DictReader(call_path.open()));frames=list(csv.DictReader(frame_path.open()));phases={}
  for phase in sorted({r['phase']for r in frames}):
   sequence=[r for r in frames if r['phase']==phase];routines={}
   for name in sorted({r['name']for r in calls}):
    values=[int(r['cpuCycles'])for r in calls if r['phase']==phase and r['name']==name]
    if values:routines[name]=dict(samples=len(values),mean_cpu_cycles=statistics.mean(values),maximum_cpu_cycles=max(values))
   phases[phase]=dict(video_frames=len(sequence),movement_updates=sum(int(r['updates'])for r in sequence),sprite_draws=sum(int(r['draws'])for r in sequence),lag_nmis=sum(int(r['lagNmis'])for r in sequence),routines=routines)
  summaries[label]=dict(rom_sha256=binding['ROM_sha256'],phases=phases,calls_sha256=sha(call_path),frames_sha256=sha(frame_path));bindings[label]=binding
 for name in('test_sha256','menu_sha256','observer_sha256','profiler_sha256'):assert bindings['before'][name]==bindings['after'][name],('Matched current test dependencies',name)
 old,new=[summaries[k]['phases']['pellets']for k in('before','after')]
 assert old['video_frames']==new['video_frames']and old['movement_updates']==new['movement_updates']
 assert new['sprite_draws']>old['sprite_draws']and new['lag_nmis']<old['lag_nmis']
 old_cost=old['routines']['RlWeapons']['mean_cpu_cycles'];new_cost=new['routines']['RlWeapons']['mean_cpu_cycles']
 report=dict(passed=True,measurements=summaries,normal_shot_weapon_cost_reduction_percent=100*(old_cost-new_cost)/old_cost,scope='Same authored controller arena and test/observer dependencies. Foreground CPU spans subtract NMI/IRQ duration but remain inclusive of nested foreground calls; do not sum routine costs. Video counts are separate update/draw/lag measurements. This proves the bounded rapid-fire improvement, not constant60Hz or a full-campaign performance pass.')
 out=args.output.resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('PASS rapid-fire weapon CPU reduction',round(report['normal_shot_weapon_cost_reduction_percent'],1),'percent; lag NMIs',old['lag_nmis'],'to',new['lag_nmis'])


if __name__=='__main__':main()

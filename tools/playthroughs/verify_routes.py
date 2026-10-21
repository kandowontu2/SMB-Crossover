"""Fresh power-on, fixed-controller replays of the twelve solved 1-1 routes."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PREFIXES={
 route:[f'palette-fixed-{character}-{route}' for character in range(6)]
 for route in ('surface','pipe')
}
def main():
 p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=3);p.add_argument('--tag',default='final-qa');p.add_argument('--mapper',default='mmc3',choices=('mmc3','mmc5'));p.add_argument('--characters',default='0,1,2,3,4,5');p.add_argument('--routes',default='surface,pipe');p.add_argument('--discover',action='store_true');p.add_argument('--current-policy',action='store_true');p.add_argument('--prefix-tag');a=p.parse_args()
 assert not a.current_policy or a.discover,'Current policy is for discovery; proofs require fixed inputs'
 routes=a.routes.split(',');assert all(r in PREFIXES for r in routes),'Unknown route'
 def replay(character,route):
  name=f'{a.prefix_tag}-{character}-{route}' if a.prefix_tag else (PREFIXES[route][character] if character<6 else None)
  if a.current_policy:name=None
  prefix=ROOT/'build/playthroughs'/name if name else None
  command=[sys.executable,'tools/playthroughs/run.py','--character',str(character),'--route',route,'--mapper',a.mapper,'--tag',a.tag]
  if a.discover:
   if prefix:command+=['--policy',str(prefix/'policy.lua')]
  else:
   if not prefix:raise ValueError('Run discovery first, then supply --prefix-tag')
   inputs=prefix/'applied-inputs.csv'
   if not inputs.exists():inputs=prefix/'inputs.csv'
   command+=['--record','--exit-tail','--replay',str(inputs),'--policy',str(prefix/'policy.lua')]
  completed=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
  out=ROOT/'build/playthroughs'/f'{a.tag}-{character}-{route}'
  (out/'runner.log').write_text(completed.stdout+completed.stderr)
  manifest=json.loads((out/'manifest.json').read_text())
  clear=manifest.get('result',{});audit=manifest.get('audit',{})
  candidate=bool(clear.get('cleared') and clear.get('goals')==(5 if route=='surface' else 1) and not clear.get('died') and audit.get('enemies_defeated')==(17 if route=='surface' else 6) and audit.get('unconfirmed_despawns')==0 and audit.get('next_level_control'))
  result={'character':character,'route':route,'exit':completed.returncode,'candidate_coverage':candidate,'full_coverage':manifest.get('verified_full_coverage',False),'output':str(out),'result':manifest.get('result'),'audit':manifest.get('audit')}
  print(json.dumps(result),flush=True);return result
 with ThreadPoolExecutor(max_workers=a.jobs) as pool:
  jobs=[pool.submit(replay,int(c),route) for route in routes for c in a.characters.split(',')]
  results=[future.result() for future in as_completed(jobs)]
 (ROOT/'build/playthroughs'/f'{a.tag}-summary.json').write_text(json.dumps(sorted(results,key=lambda r:(r['route'],r['character'])),indent=2)+'\n')
 return int(any(r['exit'] or not r['candidate_coverage' if a.discover else 'full_coverage'] for r in results))
if __name__=='__main__':raise SystemExit(main())

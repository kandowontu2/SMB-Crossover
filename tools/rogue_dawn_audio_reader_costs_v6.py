"""Seven paired initialized full-NMI cost samples; no source/ROM/native changes."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
O=R/'build/rogue-dawn-audio-readers-v6';P=R/'build/rogue-dawn-backdrop-v1'

def main():
 assert not(O/'costs.json').exists()
 old=v.scoped_load(P/'candidate.nes');new=v.scoped_load(O/'candidate.nes');rows=[]
 for area,ticks in [(1,4),(0,3)]:
  hosts=[v.prepared(b,area)for b in[old,new]]
  for tick in range(ticks):
   results=[]
   for m in hosts:
    v.put(m,NmiDisable=255);m[0x5fb6]=2*(tick%3 if tick else 0)
    results.append(v.nmi(m))
   assert results[0]['requests']==results[1]['requests']
   rows.append(dict(area=area,tick=tick,old_fullNMI_CPU=results[0]['CPU'],new_fullNMI_CPU=results[1]['CPU'],saved_CPU=results[0]['CPU']-results[1]['CPU']))
 result=dict(passed=True,source_CPU_only=True,native_run=False,cases=rows,
  limits='Seven paired initialized lagNMI samples, every original cue/clock retained. No DMA514/DMC-steal/PPUdeadline/nativeFPS claim.',
  bindings=[v.ref.binding(p)for p in[Path(__file__),P/'handoff.json',O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',R/'tools/rogue_dawn_scheduler_controls_v3.py']])
 (O/'costs.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))
if __name__=='__main__':main()

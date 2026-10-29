"""Fresh actual full foreign Main/NMI comparison after A95 relocation."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
from sunny_integrated_controls_v1 import app,registers
q,put=v.q,v.put
O=R/'build/rogue-dawn-backdrop-v1';P=R/'build/rogue-dawn-scheduler-v5'

def main():
 assert not(O/'foreign-controls.json').exists()
 old=v.scoped_load(P/'candidate.nes');new=v.scoped_load(O/'candidate.nes');rows=[]
 for char,mode in itertools.product(range(24),[0,1]):
  pair=[]
  for b in [old,new]:
   m=q.make(b,mode);put(m,SelectedCharacter=char,RdVariant=0,SavedJoypadBits=1)
   c,z=q.mainstep(m);nm=q.wake(m)
   class Q:pass
   a=Q();a.b=b;a.m=m
   pair.append((registers(c),app(a),q.physical(m),z['CPU'],nm['CPU']))
  assert pair[0][:3]==pair[1][:3],('actual foreign fullMain/NMI',char,mode)
  rows.append(dict(character=char,mode=mode,Main_CPU_delta=pair[1][3]-pair[0][3],NMI_CPU_delta=pair[1][4]-pair[0][4]))
 out=dict(passed=True,native_run=False,source_CPU_only=True,cases=48,rows=rows,
  scope='Actual complete foreign Main plus genuine regular NMI, relative frozenf467. Exact returnedAXYP/SP/applicationRAM/banks; existing explicit deadstack/5SMC comparison helper only.',
  bindings=[v.ref.binding(p)for p in[Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'handoff.json',R/'tools/rogue_dawn_scheduler_controls_v1.py',R/'tools/audit/sunny_integrated_controls_v1.py']])
 (O/'foreign-controls.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(dict(passed=True,cases=48,Main_deltas=sorted(set(x['Main_CPU_delta']for x in rows)),NMI_deltas=sorted(set(x['NMI_CPU_delta']for x in rows)))))
if __name__=='__main__':main()

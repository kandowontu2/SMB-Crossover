"""Actual changed side instructions interrupted by full NMI and genuine IRQ."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_side_controls_v1 as t
v,q,put,get,address,deep=t.v,t.q,t.put,t.get,t.address,t.deep
O=t.O

def main():
 assert not(O/'edges.json').exists()
 b=v.scoped_load(O/'candidate.nes');first=address(b,'RdHsGeometry::YPlus')
 # LDAabs/CLC/ADCabs/SEC/SBCimm/STAabs: all true new/adjacent seams.
 sites=[first+i for i in[0,3,4,7,8,10]];rows=[]
 for left in[False,True]:
  def scene():
   m=t.ready(b)
   for i in range(8):
    put(m,SavedJoypadBits=2 if left else 1);q.mainstep(m);v.nmi(m)
   put(m,NmiDisable=255,SavedJoypadBits=2 if left else 1)
   return m
  m=scene();plain=deep.execute(m,'IdleLoop',253)
  for pc in sites:
   candidates=[k for k in plain['trace']if k[:2]==(pc,95)]
   assert candidates,('actual Main omitted changed endpoint',left,hex(pc))
   cut=min(candidates,key=lambda k:k[2]);m=scene()
   z=deep.execute(m,'IdleLoop',253,cut,IRQ=(address(b,'RdaReadRomValue'),97,cut[2]-29))
   assert z['minimum_SP']>=128
   rows.append(dict(left=left,entry='actual IdleLoop/GameLoop',cut=[hex(cut[0]),cut[1],cut[2]],
    minimum_SP=z['minimum_SP'],real_NMI_and_IRQ=z['interrupt'],final=t.base.state(m)))
 out=dict(passed=True,source_CPU_only=True,native_run=False,cases=len(rows),rows=rows,
  minimum_SP=min(r['minimum_SP']for r in rows),
  scope='Every changed/adjacent horizontal-bottom instruction reached through actual Main; genuine full lagNMI and actual existing IRQ, no IRQ stub or NMI-in-NMI.',
  bindings=[v.ref.binding(p)for p in[Path(__file__),R/'tools/rogue_dawn_side_controls_v1.py',O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',R/'tools/rogue_dawn_scheduler_deep_edges_v1.py']])
 (O/'edges.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),minimum_SP=out['minimum_SP'])))
if __name__=='__main__':main()

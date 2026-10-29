"""Compact retained typed stack counterexamples; never native/game failures."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_floor_controls_v1 as base
import rogue_dawn_scheduler_controls_v3 as v
import rogue_dawn_scheduler_deep_edges_v1 as deep
q=v.q;OUT=R/'build/rogue-dawn-floor-v4/retained-stack-negatives.json'

def main():
 assert not OUT.exists()
 rows=[];bound=[]
 for folder,action,vy,ry,y in [
  ('rogue-dawn-floor-v1',1,1,15,192),
  ('rogue-dawn-floor-v2',0,0,15,192),
  ('rogue-dawn-floor-v3',3,0,8,192),
  ('rogue-dawn-audio-readers-v6',3,0,8,192)]:
  p=R/'build'/folder;b=v.scoped_load(p/'candidate.nes')
  def scene():
   m=base.ready(b);v.nmi(m);v.put(m,NmiDisable=255,RdAction=action,RdVY=vy,RdRadiusY=ry,RdY=y,RdClock=0)
   if action==1:v.put(m,RdGravity=26)
   if action==3:v.put(m,RdAnimFrame=27,RdAnimReset=22,RdAnimIndex=22)
   return m
  m=scene();plain=deep.execute(m,'RdControlStep',192);cut=min(plain['trace'],key=lambda a:a[2])
  row=dict(candidate=v.ref.binding(p/'candidate.nes'),context=dict(action=action,VY=vy,radius=ry,centerY=y),cut=[hex(cut[0]),cut[1],cut[2]])
  original=q.interrupt
  def irq(memory,cpu,kind='NMI',nested_irq=None):
   before=q.image(memory)
   try:return original(memory,cpu,kind,nested_irq)
   finally:
    row['actual_IRQ_SMC_before']=before.hex();row['actual_IRQ_SMC_after']=q.image(memory).hex()
    row['actual_IRQ_SMC_exact']=before==q.image(memory)
  q.interrupt=irq
  try:
   m=scene();z=deep.execute(m,'RdControlStep',192,cut,IRQ=(v.address(b,'RdaReadRomValue'),97,cut[2]-29))
   row['minimum_SP']=z['minimum_SP'];row['guard_failed']=z['minimum_SP']<128
  except AssertionError as e:
   row.update(actual_restoration_failure=True,error_prefix=str(e)[:160],guard_failed=True)
  finally:q.interrupt=original
  assert row['guard_failed']
  rows.append(row)
  bound.extend(v.ref.binding(p/('candidate.'+s))for s in['nes','dbg','lbl'])
 proof=dict(source_CPU_only=True,native_run=False,all_expected_negatives_preserved=True,rows=rows,
  distinction='56e3 and parent69a airborneMorph actualIRQ changedSMC;1ad1/950c failed128guard without changedSMC. These are explicit standaloneControl192 CPU contexts, never a claimed native product failure. Finaldf44 passes the same expanded12action/pad stress at>=128.',
  bindings=bound+[v.ref.binding(Path(__file__))])
 OUT.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(expected_negatives=len(rows),report=v.ref.binding(OUT)),indent=2))
if __name__=='__main__':main()

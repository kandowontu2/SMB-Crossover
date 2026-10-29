"""Read-only complete-Main run/ground diagnosis; no native or gameplay edits."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
q=v.q
O=R/'build/rogue-dawn-backdrop-v1'
OUT=R/'docs/qa/rogue-dawn-run-support-trace-2026-10-29.json'

def snap(m):
 return {n:v.get(m,n) for n in ['RdAction','RdGravity','RdVY','RdVerticalFraction',
  'RdVerticalPhase','RdFresh','RdHeld','RdX','RdRoomHi','RdY','RdRadiusY',
  'RdAnimFrame','Player_State','Player_X_Position','Player_PageLoc','Player_Y_Position']}

def main():
 assert not OUT.exists(),'Preserve diagnosis'
 b=v.scoped_load(O/'candidate.nes');m=q.make(b,0);v.nmi(m)
 # Same native solid-floor type observed by ROOT:54/attribute41. This is a
 # disclosed legal CPU scene, not a claim to have loaded native saved RAM.
 for x in range(0,512,16):q.w.life.body.pipe.d.old.tile(m,x,208,0x54)
 names=['RdControlStep','RdC_CCC4','RdC_CD23','RdC_CD3C','RdC_CD59',
  'RdControlPhysics','RdControlVerticalAdmission','RdVerticalAccelerate',
  'RdGroundCollisionResponse','RdStartJump','RdHsExportPosition','RdBodyBoxOwn']
 targets={(v.address(b,n),(v.q.location(b,n)-16)//8192):n for n in names}
 events=[];rows=[];index=-1
 oldstep=q.NesMPU.step
 def step(c):
  if c.memory is m:
   pc,bank=q.key(m,c);tag=targets.get((pc,bank));before=m[0x5c14]
   if tag:events.append(dict(update=index,entry=tag,pc=hex(pc),bank=bank,SP=c.sp,A=c.a,P=c.p,**snap(m)))
   result=oldstep(c)
   if m[0x5c14]!=before:events.append(dict(update=index,write_gravity=[before,m[0x5c14]],pc=hex(pc),bank=bank,SP=c.sp,**snap(m)))
   return result
  return oldstep(c)
 q.NesMPU.step=step
 try:
  pads=[0]*4+[1]*34+[0]*16+([128]*3+[0]*4)*6
  for index,pad in enumerate(pads):
   v.put(m,SavedJoypadBits=pad);c,z=q.mainstep(m)
   rows.append(dict(update=index,pad=pad,CPU=z['CPU'],Mains=z['actual_Main_calls'],**snap(m)))
   v.nmi(m)
 finally:q.NesMPU.step=oldstep
 proof=dict(source_CPU_only=True,native_run=False,scene='Existing real initialized q.make floor arena, native solid54 at208, no action/gravity/velocity outcomes seeded; walk then release and3hold/4release physical A.',
  rows=rows,events=events,bindings=[v.ref.binding(p)for p in[Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'handoff.json',R/'src/rogue_dawn_control.s',R/'src/rogue_dawn_core.s',R/'tools/rogue_dawn_scheduler_controls_v1.py']])
 OUT.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(report=str(OUT),rows=len(rows),events=len(events),tail=rows[-12:]),indent=2))
if __name__=='__main__':main()

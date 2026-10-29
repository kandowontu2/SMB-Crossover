"""Finite f467 complete-Main floor/readback proof; typed legal CPU arena, no native."""
from pathlib import Path
import json
import sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
q,get,put,address=v.q,v.get,v.put,v.address
O=R/'build/rogue-dawn-scheduler-v5'
OUT=R/'docs/qa/rogue-dawn-ground-support-source-2026-10-29.json'

def snapshot(m):
 return {n:get(m,n) for n in ['Player_X_Position','Player_PageLoc','Player_Y_Position',
  'Player_Y_HighPos','Player_State','RdAction','RdGravity','RdVY','RdFresh','RdHeld',
  'RdX','RdRoomHi','RdY','RdRadiusX','RdRadiusY']}

def main():
 assert not OUT.exists(),'Frozen source control'
 b=v.scoped_load(O/'candidate.nes');m=q.make(b,0);v.nmi(m)
 rows=[];ready=None
 for update in range(40):
  put(m,SavedJoypadBits=0)
  cpu,z=q.mainstep(m)
  s=snapshot(m)
  rows.append(dict(update=update,**s,actual_down_collision=any(pc==address(b,'RdGroundCollisionResponse') and bank==124 for pc,bank,sp in z['trace'])))
  if s['RdAction']==0 and s['Player_State']==1 and s['RdVY']==0 and ready is None:
   ready=dict(update=update,before=s)
   v.nmi(m);put(m,SavedJoypadBits=128)
   cpu,jump=q.mainstep(m)
   ready.update(after=snapshot(m),actual_RdStartJump=any(pc==address(b,'RdStartJump') and bank==124 for pc,bank,sp in jump['trace']))
   assert ready['actual_RdStartJump'] and ready['after']['RdVY']>=128
   v.nmi(m)
   # Finish the same real landing chain rather than resetting resource/pose.
  else:v.nmi(m)
 assert ready is not None,rows
 proof=dict(passed=True,source_CPU_only=True,native_run=False,
  arena='Existing qualified typed floor arena in q.make/body.pipe.base: real block-buffer floor at208, native unmodified completeIdleLoop->GameLoop and genuine NMI betweenMains. Not an observed native source-RAM snapshot.',
  rows=rows,actual_standing_fresh_A_while_PlayerState1=ready,
  controller_contract='RdGravity0 is a true just-landed source event but not a stable support boolean. Action0/4 admit freshA with real current foot support; running1 requiresGravity0. Air2/6 withGravity0 first transitions tostand/aim and does not consume freshA on that same handler.',
  geometry='Native source down probe samples current center+radius+1 at Xcenter-radius/center/center+radius. Solid requires actualMTileAttribute&(SOLID|CLIMB)==SOLID;5F/60head-only andC2/C3/C5non-support. Moving-platform support is a separate actualactor mechanism.',
  limits=['No native/controllerclear/deadline claim.','Input-only controller remains ROOT-owned; no source fixes or outcome seeds.'],
  bindings=[v.ref.binding(p)for p in [Path(__file__),O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'handoff.json',R/'src/rogue_dawn_core.s',R/'src/rogue_dawn_control.s',R/'src/rogue_dawn_host_services.s',R/'tools/rogue_dawn_scheduler_controls_v1.py',R/'tools/rogue_dawn_host_pipeline_controls_v1.py']])
 OUT.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,report=v.ref.binding(OUT),standing_case=ready),indent=2))
if __name__=='__main__':main()

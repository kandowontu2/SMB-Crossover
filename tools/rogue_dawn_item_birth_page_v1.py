"""Read-only linked head -> item world origin/lifetime counterexample; no native."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_side_controls_v1 as scene
import rogue_dawn_scheduler_controls_v3 as v
q,get,put,address=v.q,v.get,v.put,v.address
P=R/'build/rogue-dawn-side-v1'
O=R/'docs/qa/rogue-dawn-item-birth-page-counterexample-2026-10-29.json'

def main():
 assert not O.exists(),'Preserve original counterexample'
 b=v.scoped_load(P/'candidate.nes');rows=[]
 names=['RdTxAfterMovement','NativeRarePlayerHeadCollisionCore','InitBlock_XY_Pos',
        'SetupPowerUp','OffscreenBoundsCheck','EraseEnemyObject']
 sites={(address(b,n),(q.w.life.body.pipe.d.old.location(b,n)-16)//8192):n for n in names}
 for mode,camera in itertools.product([0,1],[0,225,257]):
  m=scene.ready(b,mode,337)
  put(m,ScreenLeft_PageLoc=camera//256,ScreenLeft_X_Pos=camera%256)
  q.invoke(m,'GetScreenPosition')
  tiles={x:q.w.life.body.pipe.d.old.tile(m,x,144,t)for x,t in
         [(320,0x51),(336,0xc1),(352,0x51),(368,0xc0),(384,0x51)]}
  watched={address(b,n)+i:(n,i)for n in ['Enemy_Flag','Enemy_ID','Enemy_PageLoc',
           'Enemy_X_Position','InvPickupOwner','InvPickup']for i in range(6)}
  watched.update({address(b,n)+i:(n,i)for n in ['Block_PageLoc','Block_X_Position']for i in range(2)})
  watched.update({address(b,n):(n,0)for n in ['SmHeadX','SmHeadPage']})
  chronology=[];snapshots=[];i=-1;oldstep=q.NesMPU.step
  def actors():
   return [dict(slot=s,flag=m[address(b,'Enemy_Flag')+s],id=m[address(b,'Enemy_ID')+s],
       x=m[address(b,'Enemy_X_Position')+s]+256*m[address(b,'Enemy_PageLoc')+s],
       y=m[address(b,'Enemy_Y_Position')+s],state=m[address(b,'Enemy_State')+s],
       owner=m[address(b,'InvPickupOwner')+s],pickup=m[address(b,'InvPickup')+s])
      for s in range(6)if m[address(b,'Enemy_Flag')+s]or m[address(b,'Enemy_ID')+s]==0x2e]
  def step(c):
   if c.memory is not m:return oldstep(c)
   key=q.key(m,c);n=sites.get(key);before=len(m.writes)
   if n and (n not in ['OffscreenBoundsCheck','EraseEnemyObject']or c.x<6 and m[address(b,'Enemy_ID')+c.x]==0x2e):
    chronology.append(dict(update=i,kind='entry',name=n,PC=hex(c.pc),bank=key[1],SP=c.sp,X=c.x,
     camera=get(m,'ScreenLeft_X_Pos')+256*get(m,'ScreenLeft_PageLoc'),
     SmHead=[get(m,'SmHeadX'),get(m,'SmHeadPage')],MmBlockAttack=get(m,'MmBlockAttack'),
     cell=get(m,'R6')+256*get(m,'R7')+get(m,'R2'),actors=actors()))
   z=oldstep(c)
   for a,value in m.writes[before:]:
    if a in watched:
     name,slot=watched[a]
     chronology.append(dict(update=i,kind='write',PC=hex(key[0]),bank=key[1],SP=c.sp,
      name=name,slot=slot,value=value))
   return z
  q.NesMPU.step=step
  try:
   for i,pad in enumerate([0]*8+[128]*25+[0]*65):
    put(m,SavedJoypadBits=pad);c,z=q.mainstep(m)
    if actors():snapshots.append(dict(update=i,actors=actors()))
    v.nmi(m)
  finally:q.NesMPU.step=oldstep
  birth=[e for e in chronology if e.get('name')=='Enemy_Flag'and e.get('value')==1]
  erased=[e for e in chronology if e.get('name')=='EraseEnemyObject']
  rows.append(dict(mode=mode,camera=camera,actual_Mains=i+1,question_after=m[tiles[336]],
   birth=birth,erase_entries=erased,chronology=chronology,completed_Main_actor_snapshots=snapshots,
   final_tanks=get(m,'RdTanks'),final_status=get(m,'PlayerStatus')))
  print('mode',mode,'camera',camera,'birth',len(birth),'erase',len(erased),
        'survivingMainRecords',len(snapshots),flush=True)
 proof=dict(source_CPU_only=True,native_run=False,game_or_ROM_edits=False,
  actual_ROM=v.ref.binding(P/'candidate.nes'),rows=rows,
  scope='Genuine compiled complete Main/NMI in a staged source-derived local opening row. Actual native actor chronology remains separately ROOT-owned; no claimed native RAM replay.',
  finding='Read-only hypothesis test. Raw Samus InitBlock_XY_Pos consumes SmHeadX/SmHeadPage. Inspect actual retained values, constructor branches and actor coordinates before concluding whether the deferred flush supplies the correct world origin.',
  bindings=[v.ref.binding(p)for p in[Path(__file__),P/'handoff.json',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',
   R/'src/rogue_dawn_host_deferred.s',R/'src/level_tiles.s',R/'src/object.s',
   R/'docs/qa/rogue-dawn-opening-head-target-source-v2-2026-10-29.json']])
 O.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(report=v.ref.binding(O))))
if __name__=='__main__':main()

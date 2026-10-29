"""Actual Main local opening-row target control; no gameplay/controller edit."""
from pathlib import Path
import itertools,json,sys
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_floor_controls_v1 as base
import rogue_dawn_scheduler_controls_v3 as v
q,get,put,address=v.q,v.get,v.put,v.address
O=R/'docs/qa/rogue-dawn-opening-head-target-source-v2-2026-10-29.json'
P=R/'build/rogue-dawn-floor-v4'

def main():
 assert not O.exists(),'Preserve source control'
 b=v.scoped_load(P/'candidate.nes');rows=[]
 for mode,px in itertools.product([0,1],[330,336,338]):
  m=base.ready(b,mode)
  # Genuine native scene-pointer constructor. The old short arena had zero
  # EnemyData; longerHard parsing interpreted mutableZP as enemy records.
  put(m,AreaPointer=0x25)
  q.invoke(m,'GetAreaDataAddrs')
  put(m,EnemyDataOffset=0,EnemyObjectPageLoc=0,EnemyObjectPageSel=0)
  assert get(m,'EnemyDataLow')+256*get(m,'EnemyDataHigh')==address(b,'E_GroundArea6')
  v.nmi(m)
  put(m,Player_X_Position=px&255,Player_PageLoc=px//256)
  # Source level1-1 local row: normalbrick320, mushroomquestion336,
  # normalbrick352, coinquestion368, normalbrick384, all visibleY144.
  # This is an explicit source-derived legal scene, not native RAM replay.
  tiles={x:q.w.life.body.pipe.d.old.tile(m,x,144,t)for x,t in[(320,0x51),(336,0xc1),(352,0x51),(368,0xc0),(384,0x51)]}
  heads=[];actors=[];index=-1;oldstep=q.NesMPU.step
  def step(c):
   if c.memory is m and q.key(m,c)==(address(b,'NativeRarePlayerHeadCollisionCore'),9):
    ptr=get(m,'R6')+256*get(m,'R7');row=get(m,'R2');cell=ptr+row
    heads.append(dict(update=index,actual_native_head_PC=hex(c.pc),bank=9,SP=c.sp,
     native_R2=row,native_R6R7=hex(ptr),cell_address=hex(cell),cell_value=m[cell],
     selected_world_cell=next((x for x,a in tiles.items()if a==cell),None),
     source_centerX=get(m,'RdX')+256*get(m,'RdRoomHi'),radius=get(m,'RdRadiusX')))
   return oldstep(c)
  q.NesMPU.step=step
  try:
   for index,pad in enumerate([0]*8+[128]*25+[0]*65):
    put(m,SavedJoypadBits=pad)
    try:c,z=q.mainstep(m)
    except Exception as e:
     negative=O.with_name('rogue-dawn-opening-head-context-negative-2026-10-29.json')
     if not negative.exists():negative.write_text(json.dumps(dict(source_CPU_only=True,native_run=False,mode=mode,playerX=px,update=index,error=str(e),heads=heads,actors=actors,source=base.state(m)),indent=2)+'\n')
     raise
    for slot in range(6):
     if m[address(b,'Enemy_Flag')+slot]and m[address(b,'Enemy_ID')+slot]==0x2e:
      if not actors:actors.append(dict(update=index,slot=slot,
       native_x=m[address(b,'Enemy_X_Position')+slot]+256*m[address(b,'Enemy_PageLoc')+slot],
       native_y=m[address(b,'Enemy_Y_Position')+slot],native_state=m[address(b,'Enemy_State')+slot],
       InvPickup=m[address(b,'InvPickup')+slot],InvOwner=m[address(b,'InvPickupOwner')+slot]))
    v.nmi(m)
  finally:q.NesMPU.step=oldstep
  expected=320 if px==330 else 336
  assert heads and heads[0]['selected_world_cell']==expected,(mode,px,heads)
  if px==330:assert not actors and m[tiles[336]]==0xc1
  else:assert actors and actors[0]['InvOwner']==2 and m[tiles[336]]!=0xc1
  cx=px+8
  rows.append(dict(mode=mode,playerX=px,source_head_samples=[cx-4,cx,cx+4],
   native_head_calls=heads,actual_powerup_birth=actors,
   final_cells={str(x):m[a]for x,a in tiles.items()},final_status=get(m,'PlayerStatus'),
   final_tanks=get(m,'RdTanks'),actual_Mains=index+1))
 proof=dict(passed=True,source_CPU_only=True,native_run=False,cases=len(rows),rows=rows,
  finding='Actual completeMain atPlayerX330 first hits ordinarybrick320 (samples334/338/342), mushroomquestion336 remainsunbumped/noactor. AtX336 or338 every sample staysinside336..351, real nativehead selectsC1, real constructor creates source-owned typedpowerup. Original jump/action/first-solid code unchanged.',
  limits=['Source-derived local adjacentrow CPU scene; native trace supplies actualX330/Y159 endpoint but native blockRAM was not sampled.',
   'Proves input target admission, genuine actor birth and98completeMains with correctly initialized native enemy stream, not native collection or routeclear. ROOT owns immutablecontroller successor.',
   'Frozen six underside controls contained a singleC1 target with adjacentemptycells; they remain valid for that disclosed scene and did not qualify native rowtargeting.'],
  corrected_context='Prior extendedHard BRK came from uninitialized EnemyData0000: actual bank2:A731 StrID parsedRAM[00C3]=84 into unusedID04 atMain25; original EnemyGraphicsEngine then intentionallyBRKs at0:BB1A. Actual GetAreaDataAddrs(AreaPointer25) initializes authentic E_GroundArea6 AA3F, and all6cases complete98Mains without this fault. This is a typed arena correction, no game change.',
  retained_negative='docs/qa/rogue-dawn-opening-head-context-negative-2026-10-29.json; build/rogue-dawn-floor-v4/hard-rise-firstbad-trace.json',
  bindings=[v.ref.binding(p)for p in[Path(__file__),P/'handoff.json',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl',
   R/'src/level_tiles.s',R/'tools/playthroughs/roster_samus_contra.lua',
   R/'build/verification/rogue-dawn-floor-native-easy-v1/trace.csv',
   R/'build/verification/rogue-dawn-floor-native-easy-v1/result.json',R/'docs/qa/rogue-dawn-opening-head-context-negative-2026-10-29.json',R/'build/rogue-dawn-floor-v4/hard-rise-firstbad-trace.json']])
 O.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,report=v.ref.binding(O),targets=[dict(mode=r['mode'],x=r['playerX'],firsthead=r['native_head_calls'][0]['selected_world_cell'],actor=bool(r['actual_powerup_birth']))for r in rows]),indent=2))
if __name__=='__main__':main()

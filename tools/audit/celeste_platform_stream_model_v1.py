"""Executable proposal model + actual unchanged native helper ownership tests.

No proposed selector is assembled here; no map or shared source is changed.
"""
from dataclasses import dataclass,replace
from pathlib import Path
import itertools,json,re,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from celeste_host_controls_v4 import *

@dataclass(frozen=True)
class Cell:
 record:int
 center:int
 phase:int=0
 permanent:bool=False
 live:bool=False
 supported:bool=False
 axis:int=0
 width:int=16

def step(cells,catalog,camera,tier=0,owner=True,pause=False):
 """Dense3-cell reference. Retained cells keep exact phase/actor identity."""
 if not owner or pause:return list(cells),[]
 keep=[]
 for c in cells:
  safely_behind=c.center+c.width//2+(30 if c.axis==0 else 0)<camera-56
  unspawned_retire=tier>0 and not c.live
  if c.permanent or c.supported or not(safely_behind or unspawned_retire):keep.append(c)
 if tier:return keep,[]
 ids={c.record for c in keep};ready=[c for c in catalog if c.record not in ids and camera-56<=c.center<=camera+288]
 return keep+ready[:3-len(keep)],ready[3-len(keep):]

ARRAYS=['HpRecord','HpPhaseLo','HpPhaseMid','HpPhaseHi','HpXLo','HpXHi','HpY','HpPreviousXLo','HpPreviousXHi','HpPreviousY','HpVisible','HpActorSlot','HpWidth','HpKind']
def install(q,record,slot,actor,records):
 r=records[record];x=r['center_x'];q.put(HpValid=1,HpKey=0,HpArea=37,HpCharacter=0,HpMode=0,HpCount=3)
 for name,v in[('HpRecord',record),('HpXLo',x&255),('HpXHi',x>>8),('HpY',r['top_y']),('HpPreviousXLo',x&255),('HpPreviousXHi',x>>8),('HpPreviousY',r['top_y']),('HpWidth',r['width_tiles']),('HpKind',r['axis']),('HpVisible',1),('HpActorSlot',actor+1)]:q.set(name,v,slot)
 q.set('HpActorOwner',slot+1,actor);q.set('Enemy_Flag',1,actor);q.set('Enemy_ID',0x25 if r['axis'] else 0x28,actor);q.set('Enemy_State',0x60 if r['width_tiles']==2 else 0x40,actor);q.set('Enemy_Y_HighPos',1,actor);q.set('ObjectOffset',actor);q.set('PlatformCollisionFlag',255,actor)

def static_1_1_approach(b,x,y,columns,delay):
 q=cmseed(b,0);q.put(AreaPointer=0x25,Hidden1UpFlag=1);run(q,'GetAreaDataAddrs')
 for j in range(3):q.set('AreaObjectLength',255,j)
 for col in range(columns):run(q,'AreaParserCore');run(q,'IncrementColumnPos')
 q.put(Player_PageLoc=x>>8,Player_X_Position=x&255,Player_Y_Position=y,Player_Y_HighPos=1,ScreenLeft_PageLoc=(x-96)>>8,ScreenLeft_X_Pos=(x-96)&255,Player_State=0,CmState=0,Player_X_Speed=32,Player_XSpeedAbsolute=32,Player_MovingDir=1,PlayerFacingDir=1,CrouchingFlag=0,CmPreviousAB=0,CmCoyote=0,CmJumpInterval=0,CmJumpBuffer=0,Player_CollisionBits=255,DisableCollisionDet=0,TimerControl=0,GameEngineSubroutine=8)
 rows=[]
 for t in range(90):
  a=128 if t>=delay else 0;q.put(SavedJoypadBits=1+a,A_B_Buttons=a,Left_Right_Buttons=1)
  run(q,'CmHostMovement');run(q,'PlayerBGCollision');q.m.page(1,1);q.set('CurrentBank',129);run(q,'RyuSourceBodyAfterBGBridge')
  rows.append([q.get('Player_PageLoc')*256+q.get('Player_X_Position'),q.get('Player_Y_Position'),q.get('Player_State')])
 return rows

def main():
 out=R/'build/celeste_platform_stream_model_v1.json';assert not out.exists()
 rom=R/'build/celeste-host-final.nes';b=scoped_load(rom);records=json.loads((R/'src/crossover_helper_data.json').read_text())['records']
 cases=0;catalog=[Cell(100+i,320+i*640)for i in range(9)]
 for permanent,tier,pause,owner in itertools.product([0,1],[0,1],[False,True],[False,True]):
  cells=[Cell(33,4472,phase=0x123456,permanent=True)]if permanent else[]
  for camera in range(0,5600,8):
   old=list(cells);cells,deferred=step(cells,catalog,camera,tier,owner,pause)
   assert len(cells)<=3 and len({c.record for c in cells})==len(cells)
   if not owner or pause:assert cells==old
   for c in old:
    if c.permanent or c.supported:assert c in cells
    if c in cells:assert cells[cells.index(c)]==c
   if tier:assert set(c.record for c in cells)<=set(c.record for c in old)
   assert not deferred;cases+=1
 # Count0 must still reach the owned manager before the original count gate.
 first,_=step([],catalog,32);assert first==[catalog[0]]
 pinned=Cell(100,100,phase=739,live=True,supported=True);assert pinned in step([pinned],catalog,1500)[0]
 retired,_=step([Cell(100,320,live=False)],catalog,200,tier=1);assert not retired
 crowded=[Cell(200+i,320+i*8)for i in range(4)];_,overflow=step([],crowded,128);assert len(overflow)==1
 # Catalogs whose required simultaneous supports exceed3 (or2 plus an
 # authored permanent cell) are rejected before allocation, not discarded.
 qrows=[]
 for slot,actor,change in itertools.product(range(3),range(6),['valid','wrong_owner','wrong_ID','wrong_flag','wrong_marker']):
  q=cmseed(b,0);install(q,0,slot,actor,records)
  if change=='wrong_owner':q.set('HpActorOwner',(slot+1)%3+1,actor)
  if change=='wrong_ID':q.set('Enemy_ID',6,actor)
  if change=='wrong_flag':q.set('Enemy_Flag',2,actor)
  if change=='wrong_marker':q.set('Enemy_State',0x80,actor)
  before=[q.get(n,actor)for n in['Enemy_Flag','Enemy_ID','Enemy_State']]
  c,_,_=run(q,'HpFindActor',x=slot);assert bool(c.p&1)==(change=='valid')
  c,w,_=run(q,'HpReleaseActor',x=slot)
  after=[q.get(n,actor)for n in['Enemy_Flag','Enemy_ID','Enemy_State']]
  if change=='valid':assert after[0]==0
  else:assert after==before,('foreign actor erased',slot,actor,change)
  qrows.append(dict(slot=slot,actor=actor,case=change,valid_owned_erase=change=='valid',CPU=c.processorCycles))
 compact=0;carry=[]
 for record,destination,actor in itertools.product([0,4],[0,1],range(6)):
  q=cmseed(b,0);install(q,record,2,actor,records)
  for i,n in enumerate(['HpPhaseLo','HpPhaseMid','HpPhaseHi']):q.set(n,17+i,2)
  saved=[q.get(n,2)for n in ARRAYS]
  for n,v in zip(ARRAYS,saved):q.set(n,v,destination)
  q.set('HpActorOwner',destination+1,actor);q.set('HpCount',2)
  c,_,_=run(q,'HpFindActor',x=destination);assert c.p&1 and c.y==actor
  assert[q.get(n,destination)for n in ARRAYS]==saved
  # Run genuine native platform dispatch after remapping ownership. The
  # real projection/carry functions execute; no synthetic playerY writer.
  q.set('HpPhaseLo',0,destination);q.set('HpPhaseMid',0,destination);q.set('HpPhaseHi',0,destination)
  r=records[record];q.put(Player_PageLoc=r['center_x']>>8,Player_X_Position=r['center_x']&255,Player_Y_Position=r['top_y']-32,Player_State=0,Player_Y_Speed=0)
  q.set('PlatformCollisionFlag',actor,actor)
  c,_,_=run(q,'HpNativePlatformDispatch',x=actor)
  assert q.get('Player_Y_Position')==(q.get('Enemy_Y_Position',actor)-32)&255 and q.get('Player_Y_Speed')==0
  carry.append(dict(record=record,axis=r['axis'],slot=destination,actor=actor,CPU=c.processorCycles,Player_Y=q.get('Player_Y_Position')));compact+=1
 approaches=[]
 for x,y,columns in[(632,128,64),(896,176,64),(2224,176,160)]:
  for delay in range(7):
   rs=static_1_1_approach(b,x,y,columns,delay);third=any(724<=xx<=768 and yy==112 and state==0 for xx,yy,state in rs)
   if x==632:assert third==(delay>=4)
   else:assert max(z[0]for z in rs)<x+4 and min(z[1]for z in rs)>=125
   approaches.append(dict(start_X=x,start_Y=y,press_A_after_updates=delay,updates=90,max_X=max(z[0]for z in rs),min_Y=min(z[1]for z in rs),third_pipe_landing=third))
 sources=['src/crossover_helpers.s','src/crossover_helper_ram.s','src/game.s','src/collision.s','src/object.s','src/level_tiles.s','src/celeste_mario_core.s','src/celeste_mario_kernel.inc']
 # The proposed four fields are explicitly already-reserved helper bytes,
 # with no current direct consumer apart from their declarations/91B clear.
 reserved={}
 for name in['HpDeferred','HpCountDown','HpSupport','HpAxis']:
  uses=[]
  for p in(R/'src').glob('*'):
   if p.suffix not in['.s','.inc']:continue
   for ln,line in enumerate(p.read_text(errors='replace').splitlines(),1):
    if re.search(r'\b'+name+r'\b',line):uses.append([p.name,ln,line.strip()])
  assert len(uses)==1 and uses[0][0]=='crossover_helper_ram.s',(name,uses)
  reserved[name]=dict(address=address(b,name),current_direct_uses=uses,indirect_owner='Existing HpConfigure full91-byte HpRamStart..HpRamEnd clear; no claim to globally free foreign RAM.')
 proof=dict(passed=True,proposal_only=True,new_selector_assembled=False,native_run=False,ROM_sha256=sha(rom),selection_model_cases=cases,actual_native_owner_release_cases=len(qrows),release_rows=qrows,compaction_rebinding_and_actual_carry_cases=compact,carry_rows=carry,actual_1_1_geometry_pipelines=approaches,explicit_overcapacity_rejection=True,original_zero_count_gate_counterexample=True,proposed_existing_reserved_fields=reserved,bindings={str(p):sha(p)for p in[Path(__file__),rom,rom.with_suffix('.dbg'),R/'docs/qa/celeste-unpowered-traversal-2026-10-28.json']+[R/n for n in sources]},limits=['Model selections are metadata plans, not installed map placements or assembled-selector/cycle/ABI qualification.','Actual native helper functions are executed unchanged for owner/release/remap/carry controls; Python performs the proposed metadata compaction.','Mandatory subset cannot be inferred from145 geometric candidates alone; existing native lifts/springs, hidden-block reveals and maze/transport paths need continuous route closure.','The21actual1-1 movement/BG/AfterBG arenas use typed standing start poses and no enemy or platform actors. They prove local coyote approach and failed ordinary51px attempts, not a native unpowered clear or a minimum fullcampaign placement set.'])
 out.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,sha256=sha(out),model_cases=cases,native_cases=len(qrows)+compact)))
if __name__=='__main__':main()

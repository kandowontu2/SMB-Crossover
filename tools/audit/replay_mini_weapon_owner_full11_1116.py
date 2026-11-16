"""Actual e32f full1-1, retained ordinary lift policy, strong returned1-2 end."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_oneup_head_query_1327_1116 as Previous
import replay_mini_oneup_manual_ctor_1327_1116 as Bind
import current_mini_weapon_owner_1116 as Current
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H=Current.R,Current.ROM,Current.PIN,Current.W,Current.N,Current.H
C=Current.Compose
BASE_SHA='3e606f490a99f027506bab24f37018058408e7ef38ab58a0c4a4994c22dd2c7a'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def bindings(raw):
    parent=Current.reference(raw);c=deepcopy(Bind.bindings(parent));c['sha']=PIN;c['kind']='full11';b=Current.bindings(raw)['bundle']
    for n in('AreaAddrsLOffset','OperMode_Task','StarInvincibleTimer'):c['ram'][n]=W.address(b,n)
    pc,at=W.address(b,'FlagpoleRoutine'),W.location(b,'FlagpoleRoutine');bank=(at-16)//8192
    c['hooks']['FlagpoleRoutine']=dict(pc=pc,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    return c

@lru_cache(maxsize=1)
def controller(raw,key='full11'):
    assert key=='full11'and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    parent=Current.reference(raw);_,body=Previous.controller(parent).split('\n',1)
    body=once(body,'local M=item;','local full={next_updates=0,max_x=0,checkpoints={},clears={},jumps={},wall_restarts=0};local fullEndpoint;local M=item;')
    body=once(body,'M=M,item=item,route=route,','M=M,item=item,full=full,route=route,')
    body=once(body,'full_stage_claim=false','full_stage_claim=full.complete or false')
    body=once(body,"lives=r('NumberofLives'),engine=","world=r('WorldNumber'),level=r('LevelNumber'),area=r('AreaNumber'),area_type=r('AreaType'),area_offset=r('AreaAddrsLOffset'),lives=r('NumberofLives'),engine=")
    body=once(body,"r('LevelNumber')==0 and r('NumberofLives')==(item.life_credit and 3 or 2)","r('LevelNumber')<=(M.scope_passed and 1 or 0)and r('NumberofLives')==2 ")
    body=once(body,"local route_index=1;local route_obstacles={{left=448,right=480,top=176},{left=608,right=640,top=160},{left=736,right=768,top=144},{left=912,right=944,top=144}}", "local route_index=1;local route_obstacles={{kind='pipe',left=448,right=480,top=176},{kind='pipe',left=608,right=640,top=160},{kind='pipe',left=736,right=768,top=144},{kind='pipe',left=912,right=944,top=144},{kind='pit',left=1104,right=1136},{kind='pit',left=1376,right=1424},{kind='pit',left=2448,right=2480}}")
    start=body.index(' if M.scope_passed then\n  assert(');end=body.index('\n local s=state();local x,y=',start)
    new=""" if M.scope_passed then
  local s=state();local x,y=s.sourceX16/16,s.sourceY16/16;updates=steps
  if s.level==1 then buttons={};return end
  local slot=work(0xc30d)-1
  if slot>=0 and slot<6 then local e=actor(slot);if e.flag==1 and e.id==37 then
   local key=tostring(e.x);local row=route.support[key]or{slot=slot,left=e.x,samples=0,moving_matches=0};route.support[key]=row;row.samples=row.samples+1
   if row.last and e.y~=row.last.top and s.y-row.last.y==e.y-row.last.top then row.moving_matches=row.moving_matches+1;row.first_motion=row.first_motion or{before=row.last,after={state=s,top=e.y}}end
   row.last={y=s.y,top=e.y,Main=mains,step=steps};row.first=row.first or{state=s,actor=e}
  end end
  local ob=route_obstacles[route_index]
  if ob and x>=ob.right+8 then
   local prior=#full.clears>0 and full.clears[#full.clears].jumps or 0
   assert(#full.jumps>prior,'Each pipe/pit has a real original queued jump')
   full.clears[#full.clears+1]={kind=ob.kind,left=ob.left,right=ob.right,state=s,jumps=#full.jumps};route_index=route_index+1;ob=route_obstacles[route_index]
  end
  route.guards=route.guards or{}
  if route.active_guard then
   local g=route.active_guard;local n=steps-g.since;assert(n<160,'Bounded original lift-wait guard')
   if not g.admitted and(s.queued==12 or s.current==12 or s.current==13 or s.vy<0)then g.admitted=state()end
   if supported(s)and n>6 then g.landed=state();route.active_guard=nil;buttons={};return end
   buttons={a=n<36};return
  end
  if ob and ob.kind=='pipe'and supported(s)and s.y>=160 and work(0xc30d)==0 and s.held&128==0 then
   for i=0,5 do local e=actor(i);local dx=e.x-s.x;local vx=r('Enemy_X_Speed',i)
    if e.flag==1 and e.id==6 and e.state==0 and math.abs(e.y-(s.y+8))<=12 and math.abs(dx)<=48 and((dx<0 and vx>0 and vx<128)or(dx>=0 and vx>=128))then
     assert(#route.guards<8);local g={since=steps,request=s,actor=e,vx=vx,direction=r('Enemy_MovingDir',i)};route.guards[#route.guards+1]=g;route.active_guard=g;buttons={a=true};return
    end
   end
  end
  local lift=mini_lift_inputs(s,ob,x);if lift then buttons=lift;return end
  local floor=supported(s)
  local want=solid(math.floor(x+24),math.floor(y+1))or solid(math.floor(x+24),math.floor(y+7))or not solid(math.floor(x+22),math.floor(y+8))or nearbyEnemy(x,y)
  buttons={right=true,b=true}
  if s.queued==12 then buttons.a=true elseif floor then buttons.a=want and s.held&128==0 else buttons.a=true end
  return
 end"""
    body=body[:start]+new+body[end:]
    body=once(body,'if M.scope_passed then stockEndpoint();return end','if M.scope_passed then fullEndpoint();return end')
    body=once(body,"hook('HandlePowerUpCollision',function()\n", "hook('HandlePowerUpCollision',function()\n if M.scope_passed then return end\n")
    body=once(body,"frame<14000 and mainEntries<4200,'Bounded natural Mini M/hidden1UP'","frame<24000 and mainEntries<8500,'Bounded actual Mini full1-1'")
    observer="""hook('MiniStep',function()
 if not M.scope_passed or r('LevelNumber')~=0 then return end
 local q=work(0xc228)
 if q==12 and full.last_queued~=12 then
  assert(#full.jumps<200);local s=state();full.jumps[#full.jumps+1]=s
  if s.contacts&8~=0 and s.contacts&1==0 then full.wall_restarts=full.wall_restarts+1 end
 end
 full.last_queued=q
end)
hook('FlagpoleRoutine',function()
 if M.scope_passed and r('WorldNumber')==0 and r('LevelNumber')==0 and r('GameEngineSubroutine')==4 and pos('Player_X_Position','Player_PageLoc')>=3000 then full.flag=full.flag or state()end
end)
fullEndpoint=function()
 if pendingMain or pendingMove or pendingStep or pendingCollect or pendingLeaf or pendingScore or pendingPower then return end
 local s=state();identity();full.first=full.first or s
 if s.level==0 then
  full.max_x=math.max(full.max_x,s.x)
  if s.x>=256+#full.checkpoints*256 and#full.checkpoints<13 then full.checkpoints[#full.checkpoints+1]=s end
  if s.engine==5 and s.x>=3160 then full.castle=full.castle or s end
 end
 if s.level==1 then
  assert(full.flag and full.castle,'Actual flag/castle before next level')
  if s.engine==0 then full.entrance=full.entrance or s end
  if s.area==2 and s.area_type==2 and s.area_offset==0 and s.engine==0 then full.underground_entrance=full.underground_entrance or s end
 end
 local grounded=full.flag and full.castle and full.entrance and full.underground_entrance and s.world==0 and s.level==1 and s.area==2 and s.area_type==2 and s.area_offset==0 and s.engine==8 and s.high==1 and s.native==0 and s.y==176 and supported(s)and s.ready==2
 if grounded then
  if not full.last_end_step or steps>full.last_end_step then
   if full.last_end_step then assert(steps==full.last_end_step+1 and moves>=full.last_end_move+1)end
   full.next_updates=full.next_updates+1;full.last_end_step=steps;full.last_end_move=moves
  end
 else full.next_updates=0;full.last_end_step=nil;full.last_end_move=nil end
 if full.next_updates==25 then
  for _,left in ipairs({560,688,864})do local lift=mini_lift_runs[left];assert(lift and lift.boarded and lift.departed,'All three actual native lifts crossed')end
  assert(full.wall_restarts==0 and#full.clears==7 and full.max_x>=3260,'Four pipes/three pits/no wall restart/fullcastle')
  assert(mainEntries==mains and moveEntries==moves and stepEntries==steps)
  full.complete=true;full.actual_Main_return={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=s}
  finish(true,'Actual Mini fullnonshortcut1-1 flag/castle/bothentrances then25 livinggrounded returned MiniStep/public1-2')
 end
end
"""
    body=once(body,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='full11'):
    q=Previous.metadata(Current.reference(raw));q.update(ROM_SHA256=PIN,factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),grant_SHA256=C.GRANT_SHA,
        game_bytes_changed=20,scope='Actual e32f compiled Mini/M prefix then retained ordinary d20 lift policy + guarded waits, all4pipes/3pits/flag/castle/bothentrances/25 actuallivinggroundedMiniStep+public atMain return; helpers unchanged, no wallgrab');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))

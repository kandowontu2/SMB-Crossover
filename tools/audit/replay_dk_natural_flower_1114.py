"""Exact571 DK earned M then ordinary second-block Flower, no game writes."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_dk_earned_mushroom_full11_1114 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
OLD_SOURCE_SHA='0e676063ef8bbf7cc8f2ab576662eb3aac697286a29326034f52788891d21438'
OLD_LUA_SHA='4601d3a2e38181a865436dda92101aa47f15bac56b58c382aaaacc3bea50289f'


@lru_cache(maxsize=1)
def controller(raw,key='donkey_kong'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==OLD_SOURCE_SHA
    text=Previous.controller(raw,key);assert sha256(text.encode()).hexdigest()==OLD_LUA_SHA
    once=Previous.Previous.once
    text=once(text,'local function finish(reason)',r'''
local dkFlower={phase='approach',age=0,resume=0}
local dkFlowerPending,dkFlowerGrantPending,dkFlowerCollector
local function finish(reason)''')
    old=next(line for line in text.splitlines()if line.startswith(' local ok='))
    new=" local ok=reason=='natural-flower-tier2-and25-resume'and dkMush.ready and dkFlower.born and dkFlower.mature and dkFlower.before and dkFlower.grant and dkFlower.collected and dkFlower.erase and dkFlower.score and dkFlower.cue and dkFlower.resume==25 and identity()and r('NumberofLives')==2 and r('DkTier')==2 and r('PlayerStatus')==2 and r('GuestPowerupActive')==0"
    text=once(text,old,new)
    text=once(text,'natural_mushroom=dkMush,','natural_mushroom=dkMush,natural_flower=dkFlower,')
    insert=r'''
hook('NrPickup',function()
 if not first or not identity()or not active()or not dkMush.ready or dkFlower.collected then return end
 local i=emu.getState()['cpu.x'];local a=dkItem(i)
 if a.x~=1248 then return end
 assert(not dkFlowerCollector and a.flag==1 and a.id==46 and a.kind==1 and a.state>=128,'Actual mature second-block Flower at native collector')
 dkFlowerCollector={state=state(),actor=a,score=dkScore(),player_box=dkBox('BoundingBox_UL_Corner'),item_box=dkBox('EnemyBoundingBoxCoord',i)}
end)
hook('DkHostCollect',function()
 if not first or not identity()or not active()or not dkFlowerCollector or dkFlower.collected then return end
 assert(dkFlower.born and dkFlower.mature and not dkFlowerPending,'Real final-kind Flower precedes collector')
 local sp,ret=dkCall();dkFlowerPending={sp=sp,ret=ret,slot=emu.getState()['cpu.x']}
 dkFlower.before={native=dkFlowerCollector,state=state(),tier=r('DkTier'),power=r('PlayerStatus'),score=dkScore(),DK_moves=dkMoves}
 assert(dkMush.ready and dkFlower.born.state.tier==1 and dkFlower.born.state.power==1
  and r('DkTier')<=1 and r('PlayerStatus')==r('DkTier'),'Real powered Flower birth survives an ordinary spent shield')
end)
hook('DkGrant',function()
 if not dkFlowerPending then return end
 assert(emu.getState()['cpu.a']==1 and not dkFlowerGrantPending,'Actual physical Flower callback kind1')
 local sp,ret=dkCall();dkFlowerGrantPending={sp=sp,ret=ret}
end)
hook('EraseEnemyObject',function()
 if dkFlowerPending and emu.getState()['cpu.x']==dkFlowerPending.slot then dkFlower.erase={state=state(),slot=dkFlowerPending.slot}end
end)
hook('SetupFloateyNumber',function()
 if dkFlowerPending then assert(emu.getState()['cpu.a']==6,'Real Flower score control6');dkFlower.score={state=state(),control=6}end
end)
for name in pairs(C.hooks)do
 if name:match('^DkGrantExit')then hook(name,function()
  if not dkFlowerGrantPending then return end
  local sp,ret=dkCall();assert(sp==dkFlowerGrantPending.sp and ret==dkFlowerGrantPending.ret,'Actual Flower grant caller')
  assert(emu.getState()['cpu.ps']&1~=0 and r('DkTier')==2 and r('PlayerStatus')==2,'Physical Flower earns tier2')
  dkFlower.grant={state=state(),returnPC=ret,returnSP=sp};dkFlowerGrantPending=nil
 end)
 elseif name:match('^DkHostCollectExit')then hook(name,function()
  if not dkFlowerPending then return end
  local sp,ret=dkCall();assert(sp==dkFlowerPending.sp and ret==dkFlowerPending.ret,'Actual Flower collector caller')
  assert(dkFlower.grant and dkFlower.erase and dkFlower.score and r('Enemy_Flag',dkFlowerPending.slot)==0,'Actual Flower erase and score')
  assert(r('Square2SoundQueue')&32~=0 and r('GuestPowerupActive')==1,'Real Flower cue32 and hosted freeze')
  dkFlower.cue={state=state(),queue=r('Square2SoundQueue'),code=32}
  dkFlower.collected={state=state(),returnPC=ret,returnSP=sp,DK_moves=dkMoves};dkFlower.lastMoves=dkMoves;dkFlowerPending=nil
 end)end
end
'''
    text=once(text,"hook('DkMovement',function()",insert+"hook('DkMovement',function()")
    point=' pendingReturn=nil;updates=updates+1'
    text=once(text,point,point+r'''
 if first and identity()and dkMush.ready then
  for i=0,5 do local a=dkItem(i);if a.flag==1 and a.id==46 and a.x==1248 then
   assert(a.kind==1,'Final complete ordinary second-block spawn chain yields Flower')
   dkFlower.born=dkFlower.born or{state=state(),actor=a}
   if a.state>=128 then dkFlower.mature=dkFlower.mature or{state=state(),actor=a}end
  end end
  if dkFlower.collected and dkMoves~=dkFlower.lastMoves and active()then
   assert(dkMoves==dkFlower.lastMoves+1,'Actual resumed DK steps after Flower')
   dkFlower.lastMoves=dkMoves;dkFlower.resume=dkFlower.resume+1;dkFlower.final_score=dkScore()
   assert(dkScore()>=dkFlower.before.score+1000,'Actual Flower score1000')
   if dkFlower.resume==25 then finish('natural-flower-tier2-and25-resume');return end
  end
 end''')
    text=once(text,'local function controls(c)','local function dkEarnedControls(c)')
    policy=r'''
local function controls(c)
 if not dkMush.ready or(c.x<1190 and dkFlower.phase=='approach')then return dkEarnedControls(c)end
 if dkFlower.collected then return{}end
 dkFlower.age=dkFlower.age+1;assert(dkFlower.age<800,'Bounded ordinary second-block Flower route')
 local v=c.vx;if v>=128 then v=v-256 end
 local function floor(x)local t=c.block(x,208);return t~=0 and t~=0x23 and t~=0xc2 and t~=0xc3 end
 if dkFlower.phase=='approach'then dkFlower.phase='align'end
 if dkFlower.phase=='align'then
  local stopping=c.x+v*math.abs(v)/64
  if stopping<1245 then return{right=true}elseif stopping>1249 then return{left=true}end
  if not c.grounded or math.abs(v)>4 then return{left=v>0,right=v<0}end
  if c.lastA then return{}end
  assert(c.x>=1240 and c.x<=1255 and floor(c.x-13)and floor(c.x+29),'Actual ground below second powerup block')
  dkFlower.phase='spawn-request';dkFlower.request=state();dkFlower.wait=0;return{a=true}
 elseif dkFlower.phase=='spawn-request'then
  dkFlower.wait=dkFlower.wait+1;assert(dkFlower.wait<32,'Actual second-block jump admission')
  if c.state==1 and c.vy>=128 then dkFlower.phase='spawn-rise';dkFlower.spawn_admission=state()end
  return{a=true}
 elseif dkFlower.phase=='spawn-rise'then
  if not dkFlower.born then return{a=c.vy>=128}end
  dkFlower.phase='retreat'
 end
 if dkFlower.phase=='retreat'then
  assert(c.x>=1160,'Retreat stays clear of real first pit')
  if not c.grounded or c.x>1184 then return{left=true}end
  if not dkFlower.mature then return{}end
  if v<16 or r('PlayerFacingDir')~=1 then return{right=true}end
  assert(c.x>=1170 and c.x<=1188 and floor(c.x-13)and floor(c.x+29),'Actual whole-body run-up floor before Flower roof jump')
  if c.lastA then return{right=true}end
  dkFlower.phase='cross-request';dkFlower.cross_request=state();dkFlower.wait=0;return{right=true,b=true,a=true}
 elseif dkFlower.phase=='cross-request'then
  dkFlower.wait=dkFlower.wait+1;assert(dkFlower.wait<32,'Actual native Flower approach jump admission')
  if c.state==1 and c.vy>=128 then
   assert((r('SavedJoypadBits')&128)~=0 and(r('A_B_Buttons')&128)~=0 and(r('PreviousA_B_Buttons')&128)~=0 and(r('DkPrevious')&128)~=0,'Actual native A consumed for Flower approach')
   dkFlower.phase='cross';dkFlower.cross_admission=state()
  end
  return{right=true,b=true,a=true}
 elseif dkFlower.phase=='cross'then
  assert(not c.grounded or c.y<=112,'Actual raised approach must reach Flower roof')
  return{right=true,b=true,a=c.vy>=128}
 end
 return{}
end
'''
    text=once(text,'dkDecide=function()',policy+'\ndkDecide=function()')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='donkey_kong'):
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_earned_M_full_SHA256=OLD_LUA_SHA,normal_controls_only=True,gameplay_seeds=0,outputs=0,Mesen_run=False,
        scope='Genuine first M and powered Flower birth at1248/Y144, physical kind1 collector sets tier2 even after ordinary shield loss, erase/score/cue/freeze/+25 resume; no S/L claim')

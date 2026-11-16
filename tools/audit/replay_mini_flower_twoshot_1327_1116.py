"""Genuinely earned Mini Flower, then original two-slot weapon controls."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_mini_flower_1327_1116 as Previous
import replay_smb1_alts_full11_1114 as Text
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,H,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.H,Previous.Current
BASE_SHA='615aab6e088b9bfd5f632a10121ddd55df38f003059b99d8ca8613b5b2609ebe'

def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)

@lru_cache(maxsize=1)
def bindings(raw):
    c=deepcopy(Previous.bindings(raw));b=Current.bindings(raw)['bundle']
    for n in('Fireball_State','Fireball_X_Position','Fireball_PageLoc','Fireball_Y_Position','Fireball_Y_Speed','Fireball_X_Speed','FireballBouncingFlag','Fireball_BoundBoxCtrl','A_B_Buttons','PreviousA_B_Buttons'):c['ram'][n]=W.address(b,n)
    for name,pc,at in(('MiniFireballTail',0xbcc0,16+89*8192+(0xbcc0&8191)),('FireballObjCore',W.address(b,'FireballObjCore'),W.location(b,'FireballObjCore'))):
        bank=(at-16)//8192;c['hooks'][name]=dict(pc=pc,offset=at-16,work=False,bytes=list(raw[at:at+8]),bank_SHA256=H(raw[16+bank*8192:16+(bank+1)*8192]))
    assert bytes(c['hooks']['MiniFireballTail']['bytes'])==bytes.fromhex('08488a489848ad5b');return c

@lru_cache(maxsize=1)
def controller(raw,key='flower'):
    assert key=='flower' and H(Path(Previous.__file__).read_bytes())==BASE_SHA
    _,body=Previous.controller(raw,key).split('\n',1)
    body=once(body,'local M=item;','local shots,shotEndpoint;local M=item;')
    body=once(body,'item=item,route=route,','item=item,two_shot=shots,route=route,')
    controls="""local function ball(i)return{slot=i,state=r('Fireball_State',i),x=pos('Fireball_X_Position','Fireball_PageLoc',i),y=r('Fireball_Y_Position',i),vx=r('Fireball_X_Speed',i),vy=r('Fireball_Y_Speed',i),bounce=r('FireballBouncingFlag',i),box=r('Fireball_BoundBoxCtrl',i)}end
local function shotDrive()
 assert(r('PlayerStatus')==2 and work(0xc244)==2 and r('NumberofLives')==2,'Keep genuinely earned shot tier')
 assert(steps-shots.since<180,'Finite two-slot ordinary B controls')
 local n=#shots.spawns
 if shots.phase=='release1'and steps-shots.phase_since>=2 then shots.phase='press1'
 elseif shots.phase=='press1'and n>=1 then shots.phase='release2';shots.phase_since=steps
 elseif shots.phase=='release2'and steps-shots.phase_since>=2 then shots.phase='press2'
 elseif shots.phase=='press2'and n>=2 then shots.phase='release3';shots.phase_since=steps
 elseif shots.phase=='release3'and steps-shots.phase_since>=2 then shots.phase='press3'
 elseif shots.phase=='press3'and shots.rejected then shots.phase='observe';shots.phase_since=steps end
 buttons={b=shots.phase=='press1'or shots.phase=='press2'or shots.phase=='press3'}
end
"""
    body=once(body,'local function drive()',controls+'local function drive()')
    body=once(body,'local function drive()\n if not menuDone then return end;identity()','local function drive()\n if not menuDone then return end;identity()\n if shots then shotDrive();return end')
    body=once(body,'local function endpoint()\n','local function endpoint()\n if shots then shotEndpoint();return end\n')
    body=once(body,"finish(true,'Natural Mini M then matureFlower/wholeC1/1000/60growth/25 original+public returns')","shots={phase='release1',since=steps,phase_since=steps,spawns={},attempts={},core_entries=0,core_returns=0,motion=0,bounces=0,F_return=item.actual_Main_return};buttons={}")
    observer="""hook('MiniFireballTail',function()
 if not shots then return end
 local fresh=r('A_B_Buttons')&64~=0 and r('PreviousA_B_Buttons')&64==0
 if fresh then
  local z=emu.getState();local q={PC=z['cpu.pc'],SP=z['cpu.sp'],state=state(),pool={ball(0),ball(1)},spawns=#shots.spawns};shots.attempts[#shots.attempts+1]=q;assert(#shots.attempts<=3,'Exactly three original fresh-B attempts')
  if #shots.attempts==3 then assert(#shots.spawns==2 and q.pool[1].state==1 and q.pool[2].state==1,'Third original attempt sees both live slots')end
  returning(function(t)
   q.returned={PC=t.pc,SP=t.sp,pool={ball(0),ball(1)},spawns=#shots.spawns}
   if #shots.attempts==3 then assert(#shots.spawns==2,'Original full pool rejects third spawn');shots.rejected=q end
  end)
 end
end)
for i=0,1 do emu.addMemoryCallback(guard(function(_,v)
 if shots and v==1 and r('Fireball_State',i)==0 then
  local z=emu.getState();shots.spawns[#shots.spawns+1]={slot=i,PC=z['cpu.pc'],SP=z['cpu.sp'],state=state()};assert(#shots.spawns<=2)
 end
end),emu.callbackType.write,C.ram.Fireball_State+i)end
hook('FireballObjCore',function()
 if not shots then return end;local z=emu.getState();local i=z['cpu.x'];assert(i==0 or i==1);local before=ball(i);shots.core_entries=shots.core_entries+1
 returning(function(t)
  shots.core_returns=shots.core_returns+1;local after=ball(i)
  if after.x~=before.x or after.y~=before.y then shots.motion=shots.motion+1;shots.first_motion=shots.first_motion or{PC=z['cpu.pc'],SP=z['cpu.sp'],before=before,after=after,returned={PC=t.pc,SP=t.sp}}end
  if before.vy<128 and after.vy>=128 and after.state==1 then shots.bounces=shots.bounces+1;shots.first_bounce=shots.first_bounce or{before=before,after=after,returned={PC=t.pc,SP=t.sp}}end
 end)
end)
shotEndpoint=function()
 if pendingMain or pendingMove or pendingStep or pendingCollect or pendingLeaf or pendingScore or pendingPower then return end
 if shots.phase~='observe'or steps-shots.phase_since<48 then return end
 assert(#shots.spawns==2 and shots.spawns[1].slot==0 and shots.spawns[2].slot==1 and#shots.attempts==3 and shots.rejected)
 assert(shots.core_entries==shots.core_returns and shots.motion>4 and shots.bounces>0,'Real original motion and floor bounce')
 assert(mainEntries==mains and moveEntries==moves and stepEntries==steps)
 shots.actual_Main_return={PC=emu.getState()['cpu.pc'],SP=emu.getState()['cpu.sp'],state=state()}
 finish(true,'Natural Mini M/F/60/credit25 then two original fireball slots, third rejection, actual motion+bounce')
end
"""
    body=once(body,"hook('GameLoop',function()",observer+"hook('GameLoop',function()")
    text='local C='+Text.lua(bindings(raw))+'\n'+body;LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return text

def metadata(raw,key='flower'):
    q=Previous.metadata(raw,key);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,key).encode()),parent_F_factory_SHA256=BASE_SHA,scope='Same genuine M/F/60/credit25 then three freshB attempts: two original live slots, third refusal, actual native motion and floor bounce; no art/fidelity change');return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))

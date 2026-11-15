"""Strict590 four-pipe diagnostic with polled/consumed ordinary input edges."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_gimmick_flower_board_prince_current_1115 as Previous
import replay_mr_gimmick_full11_current_1114 as Stage
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
PARENT_SOURCE='4d275416f5eca9162260747b6314cb48333745bac7aa8e1680b942916488eef2'
PARENT_LUA='061b6d454717b97643f894b3cc22c79d402c7e27c58008ad0e3901beeeb3325c'
once=Stage.once

TRAVEL=r'''
local heldJump,release,seenSupport,starPhase,starGate=nil,nil,0,'clear',nil
local function gate(c)return{poll=gmTravel.polls,read=gmTravel.reads,Main=c.frame}end
local function elapsed(g,c)return c.frame-g.Main end
local function ready(g,bit)
 return gmTravel.polls-g.poll>=2 and(gmTravel.last_clear[tostring(bit)]or 0)>g.read
end
return function(c)
 gmTravel.active=true
 if not gmTravel.start then gmTravel.start={Main=c.frame,x=c.x,y=c.y}end
 if c.x>=976 and c.x<=1040 and c.grounded and c.y==176 and c.yHigh==1 and c.r('GmRam036E')==128 then
  gmTravel.arrived=gmTravel.arrived or{Main=c.frame,x=c.x,y=c.y,read=gmTravel.reads}
 end
 if gmTravel.arrived then
  if c.grounded and c.y==176 and c.yHigh==1 then
   gmTravel.quiet=gmTravel.reads-gmTravel.arrived.read
   assert(gmTravel.quiet<=25,'Bounded grounded input-consumed endpoint')
   if gmTravel.quiet==25 then gmTravel.done=true end
  else error('Four-pipe quiet endpoint lost genuine ground')end
  return{}
 end
 local star=c.r('GmRam0091');local b={right=true}
 starGate=starGate or gate(c)
 if starPhase=='clear'then
  if ready(starGate,64)and c.r('GmPrevious')&64==0 then starPhase='charge';starGate=gate(c);b.b=true end
 elseif starPhase=='charge'then
  b.b=true
  if star>=169 then starPhase='wait-shot';starGate=gate(c);b.b=false
  elseif star==0 and gmTravel.polls-starGate.poll>=2 and(gmTravel.last_set['64']or 0)>starGate.read then
   gmTravel.B_retries=gmTravel.B_retries+1;starPhase='clear';starGate=gate(c);b.b=false
  end
 else
  if star==0 then starPhase='clear';starGate=gate(c)end
 end
 local ground=c.r('GmRam036E')>=128
 local rising=c.r('GmRam00C2')>=128
 local freshSupport=gmTravel.support_serial>seenSupport and gmTravel.last_support and gmTravel.last_support.read==gmTravel.reads
 if freshSupport then seenSupport=gmTravel.support_serial end
 if heldJump then
  local consumed=(gmTravel.last_set['128']or 0)>heldJump.read
  local polled=gmTravel.polls-heldJump.poll>=2
  if heldJump.accepted then
   b.a=not(polled and consumed and not rising)
   if not b.a then heldJump=nil;gmTravel.request=nil;release=gate(c)end
   return b
  end
  b.a=true
  if polled and consumed and(gmTravel.last_fresh_read or 0)>heldJump.read then
   gmTravel.A_retries=gmTravel.A_retries+1
   gmTravel.record('consumed-press-no-admission',gmTravel.snapshot())
   heldJump=nil;gmTravel.request=nil;release=gate(c);b.a=false
  elseif elapsed(heldJump,c)>48 then error('Held ordinary A lacked actual input consumption/admission')end
  return b
 end
 release=release or gate(c)
 local function solid(x,y)local t=c.block(x,y);return t~=0 and t~=0x23 and t~=0x26 and t~=0xc2 and t~=0xc3 and t~=0x5f end
 local support=false
 for y=math.min(c.y+40,232),232,16 do if solid(c.x+10,y)then support=true;break end end
 local e=c.enemy();local obstacle=solid(c.x+42,c.y+24)or solid(c.x+42,c.y+18)
 local danger=e and e.dx>0 and e.dx<56 and math.abs(e.y-c.y)<56
 local reason=freshSupport and'current-real-star-support'or obstacle and'actual-solid-ahead'or not support and'actual-gap'or danger and'live-enemy'
 if ground and reason and ready(release,128)and c.r('GmPrevious')&128==0 and c.r('SavedJoypadBits')&128==0 then
  heldJump=gate(c);heldJump.reason=reason;heldJump.support_serial=freshSupport and gmTravel.support_serial or nil
  gmTravel.request=heldJump;gmTravel.A_requests=gmTravel.A_requests+1
  gmTravel.record('request-A',gmTravel.snapshot());b.a=true
 end
 return b
end
'''


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    for name in('SavedJoypadBits','A_B_Buttons','PreviousA_B_Buttons'):
        q['ram'][name]=W.address(b,name)
    for alias,name in(('TravelPadRead','GmN30_8026'),('TravelFreshRead','GmN30_8199'),('TravelJumpAccepted','GmN30_81A2')):
        at=W.location(b,name);q['hooks'][alias]=dict(pc=W.address(b,name),offset=at-16,bytes=list(raw[at:at+8]),bank=(at-16)//8192)
        start=16+q['hooks'][alias]['bank']*8192;q['hooks'][alias]['bank_SHA256']=sha256(raw[start:start+8192]).hexdigest()
    return q


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    old=Previous.controller(raw,key);assert sha256(old.encode()).hexdigest()==PARENT_LUA
    prefix='local C='+Text.lua(Previous.bindings(raw,key))+'\n';assert old.startswith(prefix)
    body=old[len(prefix):]
    body="local travelReport\nlocal gmTravel={polls=0,reads=0,last_clear={},last_set={},support_serial=0,A_requests=0,A_admissions=0,A_retries=0,B_retries=0,trace={}}\n"+body
    body=once(body,Stage.POLICY,TRAVEL)
    start=body.index(' local ok=reason==');end=body.index('\n print(',start)
    body=body[:start]+" local ok=reason=='four-pipes-and25-grounded-input-consumptions'and firstMReady and gmTravel.done and gmTravel.quiet==25 and identity()and r('NumberofLives')==2 and r('GmRam0346')>0 and r('Player_State')==0 and r('Player_Y_Position')==176\n"+body[end:]
    body=once(body,'natural_flower=flower,','pipe_input_diagnostic=travelReport(),natural_flower=flower,')
    # Do not call an arbitrary later jump a Flower-support jump.
    body=once(body," if not flower.real_support then return end\n assert(emu.getState()['cpu.a']==172",
        " if not flower.support_baseline or not flower.wall_reflection or not flower.real_support or(flower.support_count or 0)<=flower.support_baseline then return end\n assert(emu.getState()['cpu.a']==172")
    observe=r'''
local function travelRegion()local x=pos('Player_X_Position','Player_PageLoc');return firstMReady and x>=418 and x<1212 end
gmTravel.record=function(kind,q)
 q.kind=kind
 local t=gmTravel.trace;t[#t+1]=q;if#t>32 then table.remove(t,17)end
end
gmTravel.snapshot=function()
 local s=state();local cpu=emu.getState()
 s.polls=polls;s.poll_serial=gmTravel.polls;s.read_serial=gmTravel.reads;s.entries=entries;s.pending_Main=not not pendingReturn
 s.decision_Main=gmTravel.decision_Main or-1;s.PC=cpu['cpu.pc'];s.SP=cpu['cpu.sp']
 s.SavedJoypadBits=r('SavedJoypadBits');s.A_B_Buttons=r('A_B_Buttons');s.PreviousAB=r('PreviousA_B_Buttons')
 s.GmPrevious=r('GmPrevious');s.GmFresh=r('GmFresh');s.GmClock=r('GmClock');s.GmVX=r('GmRam00CC')
 s.requested_bits=gmTravel.requested_bits or 0;s.last_polled_bits=gmTravel.last_polled_bits or 0
 return s
end
travelReport=function()
 local q={};for k,v in pairs(gmTravel)do if type(v)~='function'then q[k]=v end end;return q
end
local function inWindow()local x=pos('Player_X_Position','Player_PageLoc');return x>=640 and x<=760 end
hook('TravelPadRead',function()
 if not travelRegion()then return end
 gmTravel.reads=gmTravel.reads+1
 local bits=r('SavedJoypadBits')
 for _,bit in ipairs({64,128})do if bits&bit==0 then gmTravel.last_clear[tostring(bit)]=gmTravel.reads else gmTravel.last_set[tostring(bit)]=gmTravel.reads end end
 if inWindow()then gmTravel.first_consumption=gmTravel.first_consumption or gmTravel.snapshot();gmTravel.record('source-SavedJoypad-read',gmTravel.snapshot())end
end)
hook('TravelFreshRead',function()
 if not travelRegion()then return end
 gmTravel.last_fresh_read=gmTravel.reads
 if inWindow()then gmTravel.record('source-fresh-ground-test',gmTravel.snapshot())end
end)
hook('TravelJumpAccepted',function()
 if not travelRegion()or not gmTravel.request then return end
 assert(emu.getState()['cpu.a']==172,'Actual original accepted jump writer')
 gmTravel.A_admissions=gmTravel.A_admissions+1;gmTravel.request.accepted=true
 local q=gmTravel.snapshot();q.reason=gmTravel.request.reason
 q.current_support=gmTravel.last_support and gmTravel.last_support.read>=gmTravel.reads-1 or false
 gmTravel.first_admission=gmTravel.first_admission or q;gmTravel.last_admission=q;gmTravel.record('actual-jump-admission',q)
end)
local travelRide
hook('GmRideStar',function()
 if not travelRegion()then travelRide=nil;return end
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 travelRide={sp=(sp+2)&255,ret=emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1,
  before=gmTravel.snapshot()}
end)
hook('GmRideStarReturn',function()
 if not travelRide then return end
 local cpu=emu.getState();assert(cpu['cpu.sp']==travelRide.sp and cpu['cpu.pc']==travelRide.ret,'Exact actual star-support caller PC/SP')
 local b=travelRide.before;travelRide=nil
 if b.source_ground<128 and b.source_vy<128 and b.star_flags&64~=0 and b.star_status>0 and b.star_status<128 and r('GmRam036E')==128 and r('GmRam00C2')==0 then
  gmTravel.support_serial=gmTravel.support_serial+1
  local q=gmTravel.snapshot();q.before=b;q.read=gmTravel.reads;gmTravel.last_support=q
  gmTravel.first_support=gmTravel.first_support or q;gmTravel.record('actual-current-star-support',q)
 end
end)
'''
    body=once(body,"hook('GmMovement',function()",observe+"hook('GmMovement',function()")
    body=once(body,'gmInput=controls(context())',"""gmInput=controls(context())
  gmTravel.decision_Main=updates
  gmTravel.requested_bits=(gmInput.right and 1 or 0)|(gmInput.left and 2 or 0)|(gmInput.a and 128 or 0)|(gmInput.b and 64 or 0)
  if gmTravel.done then finish('four-pipes-and25-grounded-input-consumptions');return end
 """)
    body=once(body,'lastA=not not b.a;emu.setInput(b,0)',r'''
 if firstMReady then
  gmTravel.polls=gmTravel.polls+1;gmTravel.last_polled_bits=(b.right and 1 or 0)|(b.left and 2 or 0)|(b.a and 128 or 0)|(b.b and 64 or 0)
  if travelRegion()and inWindow()then
   local q=gmTravel.snapshot();gmTravel.first_poll=gmTravel.first_poll or q
   if pendingReturn then gmTravel.first_pending_poll=gmTravel.first_pending_poll or q end
   gmTravel.record('actual-inputPolled-cached-decision',q)
  end
 end
 lastA=not not b.a;emu.setInput(b,0)''')
    result='local C='+Text.lua(bindings(raw,key))+'\n'+body
    Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),parent_frozen061b_source_SHA256=PARENT_SOURCE,
        parent_frozen061b_Lua_SHA256=PARENT_LUA,
        exact_frozen_control_and_observer_body=False,first_mushroom_prefix_unchanged=True,
        diagnostic_hooks={label:bindings(raw,key)['hooks'][label]for label in('TravelPadRead','TravelFreshRead','TravelJumpAccepted','GmRideStar','GmRideStarReturn')},
        scope='Diagnostic only: genuine M then four ordinary pipes and25 living grounded original input consumptions.2physicalpoll/source-consumption A/B handshake, actual current star PC/SP and original jump admission; no Flower/fullstage claim')
    return q

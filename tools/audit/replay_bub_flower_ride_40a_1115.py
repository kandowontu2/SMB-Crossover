"""Measured Flower boarding alignment with real support/ceiling observers."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import inspect
import replay_bob_flower_close_defence_40a_1115 as Previous
import replay_bub_flower_7a80_1115 as Witness

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN
PARENT='40c7e3035c85a76110d685b21793cb9cda504a7d918ea6d32170e6f30bad8489'

@lru_cache(maxsize=2)
def observe_bindings(raw,identity=0):
    old=Previous.Previous.Previous.reference(raw)
    image=b''.join(raw[1048592+p*1024:1048592+(p+1)*1024]for p in B.PAGES)
    y=W.address(dict(W.Symbols.bundle(),raw=raw),'Player_Y_Position')
    store=bytes((0x85,y))if y<256 else bytes((0x8d,y&255,y>>8))
    # The retained v55 head projection relocates this clamp into
    # BbHeadCapture, then JMPs to the original continuation (not JSR Actor).
    pattern=bytes.fromhex('adc8c329f0')+store
    positions=[i for i in range(len(image)-len(pattern)+1)if image[i:i+len(pattern)]==pattern]
    assert len(positions)==1,'Exact current native ceiling-hit preimage'
    at=positions[0]
    return dict(pc=0xa000+at,offset=3*8192+at,data=image[at:at+16].hex())

OBSERVER=r'''
local function rideState()
 local cpu=emu.getState();local actor=identity==1 and 0x42 or 0x2e;local oy=identity==1 and 8 or 0
 return {Main=updates,frame=frame,PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],x=full_x(),y=r('Player_Y_Position'),native=r('Player_State'),
  native_dy=ram(142),source_x=full_state(0x103+oy),source_y=full_state(0x100+oy),selector=full_state(actor+3),
  direction=full_state(actor+5),support=full_state(actor+9),held=full_state(0x301),saved=r('SavedJoypadBits'),pad=pad,
  support_count=counts.source_bubble_ride_restarts,jumps=counts.source_total_jump_starts}
end
do
 local h=BUB_NATIVE_OBSERVER_CONFIG.hooks.BbOriginal_D36B;local pendingRide=nil
 emu.addMemoryCallback(guard(function()
  if not game or flower.phase~='ride'then return end
  if not mapped(h.pc,emu.memType.nesWorkRam,h.physical)then return end
  local cpu=emu.getState();local actor=cpu['cpu.x']
  if work(2,actor+9)==0 or work(2,actor+1)&128==0 then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact original support restart')end
  flower.support_events=flower.support_events or{}
  assert(#flower.support_events<3,'Bounded actual Flower support restarts')
  local row={entry=rideState()};flower.support_events[#flower.support_events+1]=row
  local sp=cpu['cpu.sp'];local pc=read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
  pendingRide={row=row,pc=pc,sp=(sp+2)&255}
  emu.addMemoryCallback(guard(function()
   local p=pendingRide;if not p then return end
   local s=emu.getState();if s['cpu.pc']~=p.pc or s['cpu.sp']~=p.sp then return end
   p.row.returned=rideState();pendingRide=nil
  end),emu.callbackType.exec,pc)
 end),emu.callbackType.exec,h.pc)
 emu.addMemoryCallback(guard(function()
  if not game or flower.phase~='ride'then return end
  if not mapped(RideHead.pc,emu.memType.nesWorkRam,RideHead.offset)then return end
  for i=1,#RideHead.data,2 do assert(read(RideHead.pc+(i-1)//2)==tonumber(RideHead.data:sub(i,i+1),16),'Actual ceiling-hit code')end
  local s=rideState();local headY=work(2,0xc3c8);s.headY=headY;s.queries={}
  for _,dx in ipairs({1,14})do local solid,tile=full_solid(s.x+dx,headY);s.queries[#s.queries+1]={x=s.x+dx,y=headY,solid=solid,tile=tile}end
  flower.ceiling_hits=flower.ceiling_hits or{};local t=flower.ceiling_hits;t[#t+1]=s
  if#t>8 then table.remove(t,5)end
 end),emu.callbackType.exec,RideHead.pc)
end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.controller(raw,identity,mode)
    once=Witness.Previous.Previous.Previous.once
    at=text.index('\n')+1
    text=text[:at]+'local RideHead='+Witness.Base.Previous.lua(observe_bindings(raw,identity))+'\n'+text[at:]
    text=once(text,'local function full_tick(finish)',OBSERVER+'\nlocal function full_tick(finish)')
    text=once(text,'return{right=best.dx>12 or best.dy>=8,a=true}',r'''if flower.phase=='ride'then
   local selector=full_state((identity==1 and 0x42 or 0x2e)+3)
   local descending=selector==2 or selector==3
   return{right=best.dx>20 or(descending and best.dy>=8),a=true}
  end
  return{right=best.dx>12 or best.dy>=8,a=true}''')
    text=once(text," elseif flower.phase=='ride'then\n  local tx=",r''' elseif flower.phase=='ride-release'then
  full_pad={}
  if sourceUpdates-flower.retry_release>=2 and full_state(0x301)&192==0 then flowerPhase('mount')end
 elseif flower.phase=='ride'then
  if flower.age>8 and q.source_bubble_ride_restarts>flower.base.source_bubble_ride_restarts
   and y>=flower.target.y+16 and full_normal_jump_ready(actor)then
   flower.retries=(flower.retries or 0)+1;assert(flower.retries<=1,'One bounded genuine floor rearm/relaunch')
   flower.landings=flower.landings or{};flower.landings[#flower.landings+1]=rideState()
   flower.retry_release=sourceUpdates;flowerPhase('ride-release');full_pad={};return
  end
  local tx=''')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


def source_check(raw,identity=0):
    ns=dict(Previous.__dict__,controller=controller)
    exec(compile(inspect.getsource(Previous.source_check),str(Path(__file__))+':current-ride-source','exec'),ns)
    return ns['source_check'](raw,identity)

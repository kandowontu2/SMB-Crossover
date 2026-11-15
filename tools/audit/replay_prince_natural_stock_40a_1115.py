"""Strict40a ordinary natural hidden1UP/Star controls, separate from e161."""
from functools import lru_cache
from pathlib import Path
import json
import replay_prince_sword_tier2_fresh_full_1115 as Frozen
import check_prince_sword_tier2_fresh_cold_1115 as Cold
from check_ff_stdout_controller_source_1110 import LuaRuntime

C,N,W,PIN=Frozen.C,Cold.N,Cold.W,Frozen.PIN
FROZEN_SHA='aac0ba31d15a07df0fa9abb6c4a72a63d0c1af818a71cb2d0ac1ada73fd04612'
FROZEN_LUA='e1614ed60e1bb2d3990df26c4f1f16e97fcda6a744ca9950bf346cc2a3ddbc2f'

def lua(value):
    if isinstance(value,dict):return'{'+','.join('['+lua(k)+']='+lua(v)for k,v in sorted(value.items()))+'}'
    if isinstance(value,(tuple,list)):return'{'+','.join(map(lua,value))+'}'
    if isinstance(value,str):return json.dumps(value)
    return str(value).lower()

POLICY=r'''
stock={kind=STOCK.kind,mode=STOCK.mode,resume=0,prince_entries=0,prince_returns=0,samples={},phase='prefix',attempts=0}
local stockUpdatePending,stockPickupPending
local stockReturnSites={}
local function stockActor(i)
 return{slot=i,flag=read(STOCK.ram.Enemy_Flag+i),id=read(STOCK.ram.Enemy_ID+i),state=read(STOCK.ram.Enemy_State+i),kind=read(STOCK.ram.PowerUpType+i),
  x=read(STOCK.ram.Enemy_X_Position+i)+256*read(STOCK.ram.Enemy_PageLoc+i),y=read(STOCK.ram.Enemy_Y_Position+i),high=read(STOCK.ram.Enemy_Y_HighPos+i)}
end
local function stockScore()
 local n=0;for i=0,5 do local v=read(STOCK.ram.Player1ScoreDisplay+i);assert(v<=9,'Actual decimal score');n=n*10+v end;return n
end
local function stockState()
 local s=state();s.sword=source(0x6ee);s.power=read(STOCK.ram.PlayerStatus);s.star=read(STOCK.ram.StarInvincibleTimer)
 s.Prince_returns=stock.prince_returns;s.Main_returns=verifiedMainReturns;return s
end
local function stockPhase(name,buttons)
 stock.phase=name;stock.since=stock.prince_returns;progress='natural-'..STOCK.mode..'-'..name;pad=buttons
end
local function stockHook(h,fn)
 emu.addMemoryCallback(guarded(function()
  local a=emu.convertAddress(h.pc)
  if not a or a.memType~=(h.private and emu.memType.nesWorkRam or emu.memType.nesPrgRom)or a.address~=h.address then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Exact natural-stock owning hook')end
  fn(emu.getState())
 end),emu.callbackType.exec,h.pc)
end
local function stockReturn(cpu,callback)
 local sp=cpu['cpu.sp'];local pc=(read(0x100+((sp+1)&255))+256*read(0x100+((sp+2)&255))+1)&65535
 local a=emu.convertAddress(pc);assert(a,'Actual caller return mapping')
 local expected={pc=pc,sp=(sp+2)&255,memType=a.memType,address=a.address}
 local key=pc..':'..expected.sp..':'..a.memType..':'..a.address
 local site=stockReturnSites[key]
 if not site then
  site={expected=expected};stockReturnSites[key]=site
  emu.addMemoryCallback(guarded(function()
   if not site.pending then return end
   local b=emu.convertAddress(pc);if not b or b.memType~=expected.memType or b.address~=expected.address or emu.getState()['cpu.sp']~=expected.sp then return end
   local q=site.pending;site.pending=nil;q.callback(q.expected,emu.getState())
  end),emu.callbackType.exec,pc)
 end
 assert(not site.pending,'One live return per authenticated caller/SP')
 site.pending={expected=expected,callback=callback}
 return expected
end
stockHook(STOCK.update,function(cpu)
 assert(not stockUpdatePending,'Previous actual Prince update returned')
 stock.prince_entries=stock.prince_entries+1
 local pending;pending=stockReturn(cpu,function(ret)
  if stockUpdatePending~=pending then return end
  stockUpdatePending=nil;stock.prince_returns=stock.prince_returns+1
 end);stockUpdatePending=pending
end)
stockHook(STOCK.head,function(cpu)
 if not stock.active or math.abs(state().x-STOCK.x)>40 then return end
 stock.head_calls=(stock.head_calls or 0)+1
 if #stock.samples<32 then stock.samples[#stock.samples+1]={tag='native-head',A=cpu['cpu.a'],PC=cpu['cpu.pc'],state=stockState()}end
end)
stockHook(STOCK.pickup,function(cpu)
 if not stock.active then return end
 local i=cpu['cpu.x'];local a=stockActor(i);if a.kind~=STOCK.kind then return end
 assert(stock.born and stock.mature and a.flag==1 and a.id==46 and a.state>=128,'Genuine mature authored item before collector')
 assert(not stockPickupPending and not stock.collected,'Single real item collector')
 local p=STOCK.ram.BoundingBox_UL_XPos;local e=p+4*(i+1)
 local pb={read(p),read(p+1),read(p+2),read(p+3)};local eb={read(e),read(e+1),read(e+2),read(e+3)}
 local ox=math.min(pb[3],eb[3])-math.max(pb[1],eb[1]);local oy=math.min(pb[4],eb[4])-math.max(pb[2],eb[2])
 assert(ox>0 and oy>0,'Actual positive native body/item overlap')
 local before={state=stockState(),actor=a,score=stockScore(),player_box=pb,item_box=eb,overlap={ox,oy},PC=cpu['cpu.pc'],SP=cpu['cpu.sp']}
 stock.collector=before
 local pending;pending=stockReturn(cpu,function(ret,returned)
  if stockPickupPending~=pending then return end
  assert((returned['cpu.ps']or returned['cpu.p'])&1~=0,'Actual pickup carry')
  local s=stockState();assert(stock.erase and stock.popup and read(STOCK.ram.Enemy_Flag+i)==0,'Actual item erase/popup')
  assert(read(STOCK.ram.Square2SoundQueue)==32 and read(STOCK.ram.FloateyNum_Control+i)==(STOCK.kind==3 and 11 or 6),'Actual cue32 and item popup')
  assert(s.hp==before.state.hp and s.sword==before.state.sword and s.power==before.state.power and s.lives==2,'Item preserves Prince health/sword/tier before delayed credit')
  if STOCK.kind==2 then assert(s.star==35 and read(STOCK.ram.AreaMusicQueue)==64,'Actual native Star timer/music')end
  stock.collected={state=s,return_PC=ret.pc,return_SP=ret.sp,popup=read(STOCK.ram.FloateyNum_Control+i),cue32=true};stockPickupPending=nil;pad=0
 end);stockPickupPending=pending
end)
stockHook(STOCK.erase,function(cpu)
 if stockPickupPending and cpu['cpu.x']==stock.collector.actor.slot then stock.erase={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=stockState()}end
end)
stockHook(STOCK.popup,function(cpu)
 if stockPickupPending then assert(cpu['cpu.a']==6,'Default popup6 before1UP override');stock.popup={PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=stockState()}end
end)
local function naturalStockTick()
 local s=stockState()
 if not stock.active then
  local start=STOCK.kind==3 and late.fourth_practical_cap and s.x>=980 or STOCK.kind==2 and earnedStage and s.x>=1530
  if not start then return false end
  stock.active=true;stock.start=s;stock.score_before=stockScore();stockPhase(STOCK.kind==3 and'approach'or'left-drop',0)
 end
 assert(s.hp>0 and s.lives==(stock.credit and STOCK.kind==3 and 3 or 2),'Living natural item route')
 assert(stock.prince_returns-stock.start.Prince_returns<1100,'Bounded natural stock controls')
 if stock.last==stock.prince_returns then return true end;stock.last=stock.prince_returns
 local age=stock.prince_returns-stock.since
 if stock.prince_returns%16==0 and #stock.samples<32 then stock.samples[#stock.samples+1]={tag='control',state=s,pad=pad,phase=stock.phase,hidden=tile(STOCK.x,STOCK.y)}end
 local item
 for i=0,5 do local a=stockActor(i)
  if a.flag==1 and a.id==46 and a.kind==STOCK.kind then
   item=a
   stock.born=stock.born or{state=s,actor=a}
   if a.state>=128 then stock.mature=stock.mature or{state=s,actor=a}end
  end
 end
 if stock.collected then
  pad=0
  local credited=STOCK.kind==3 and s.lives==3 or STOCK.kind==2 and stockScore()==stock.collector.score+1000
  if credited and not stock.credit then stock.credit={state=s,score=stockScore(),cue=read(STOCK.ram.Square2SoundQueue)}end
  if stock.credit then
   stock.resume=stock.prince_returns-stock.credit.state.Prince_returns
   assert(s.hp==stock.collected.state.hp and s.sword==stock.collected.state.sword and s.power==stock.collected.state.power,'Post-credit source inventory retained')
   if stock.resume>=25 and not stockUpdatePending and not verifiedPendingMain then stock.finished=true;final=s;finish(true,'Natural Prince '..STOCK.mode..' collector/erase/cue/credit and25 completed Prince updates')end
  end
  return true
 end
 if item then
  if not stock.mature then pad=0;return true end
  local gap=item.x-s.x;pad=gap>5 and 1 or gap< -5 and 2 or 0
  if floor(s)and item.y<s.y-16 and stock.prince_returns-(stock.chase_jump or -100)>48 then
   stock.chase_jump=stock.prince_returns;pad=pad|STOCK.jump
  end
  return true
 end
 if s.sword==2 then
  local i=source(0x61c)&127;local a=i<6 and stockActor(i)or nil
  if s.action==62 then stock.parried=true end
  if not stock.parried then pad=64
  elseif a and a.flag~=0 then local gap=a.x-s.x;pad=math.abs(gap)>36 and(gap>0 and 1 or 2)or 128
  else pad=0 end
  return true
 end
 if stock.phase=='left-drop'then
  pad=2;if floor(s)and s.x<1504 then stockPhase('approach',1)end
 elseif stock.phase=='approach'then
  local target=STOCK.x-8
  if s.x<target-3 then pad=1 elseif s.x>target+3 then pad=2 else stockPhase('release',0)end
 elseif stock.phase=='release'then
  pad=0
  if age>=8 and floor(s)and idle(s)then stock.attempts=stock.attempts+1;assert(stock.attempts<=4,'Finite real hidden/block jump attempts');stock.request=s;stock.minimum_y=s.y;stockPhase('jump',STOCK.jump)end
 elseif stock.phase=='jump'then
  stock.minimum_y=math.min(stock.minimum_y,s.y)
  pad=age<12 and STOCK.jump or 0
  if age>24 and floor(s)and idle(s)then stock.landing=s;stockPhase('approach',0)end
 end
 return true
end
'''

@lru_cache(maxsize=4)
def controller(raw,mode='oneup',jump=8):
    assert mode in('oneup','star')and jump in(8,128)and C.digest(raw)==PIN
    assert C.digest(Path(Frozen.__file__).read_bytes())==FROZEN_SHA
    text=Frozen.controller(raw);assert C.digest(text.encode())==FROZEN_LUA
    bundle=dict(W.Symbols.bundle(),raw=raw);parts=C.Packet.extract(raw)[1]
    ram={name:W.address(bundle,name)for name in('Enemy_Flag','Enemy_ID','Enemy_State','PowerUpType','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Player1ScoreDisplay','BoundingBox_UL_XPos','PlayerStatus','StarInvincibleTimer','AreaMusicQueue','Square2SoundQueue','FloateyNum_Control')}
    def native(name):
        pc=W.address(bundle,name);at=W.location(bundle,name)
        return dict(pc=pc,address=at-16,bytes=list(raw[at:at+8]),private=False)
    def private(pc,bank,data):return dict(pc=pc,address=bank*8192+(pc&8191),bytes=list(data),private=True)
    cfg=dict(mode=mode,kind=3 if mode=='oneup'else 2,x=1024 if mode=='oneup'else 1616,y=128 if mode=='oneup'else 144,jump=jump,ram=ram,
        update=private(0xb36e,3,parts[0][0x136e:0x136e+8]),pickup=private(0xc7b3,2,parts[2][1452:1464]),
        head=native('NativeRarePlayerHeadCollisionCore'),erase=native('EraseEnemyObject'),popup=native('SetupFloateyNumber'))
    def change(old,new):
        nonlocal text
        assert text.count(old)==1,old[:90];text=text.replace(old,new,1)
    change('local function finish(passed,reason)\n','local stock\nlocal function finish(passed,reason)\n')
    change("assert(read(0x75b)==2 and source(0x6ee)==1,'Earned sword persists into actual1-2')","assert(stock and stock.finished,'Qualified natural item endpoint')")
    change('later_route=late,','natural_stock=stock,later_route=late,')
    change('local function tick()\n','local STOCK='+lua(cfg)+'\n'+POLICY+'\nlocal function tick()\n  if naturalStockTick()then return end\n')
    change('  if not earnedStage then return end','  if not earnedStage or(stock and stock.active)then return end')
    LuaRuntime().compile(text)
    assert not any(token in text for token in('emu.write','emu.setState','io.open','dofile','saveState','loadState'))
    return text

def metadata(raw,mode='oneup',jump=8):
    return dict(ROM_SHA256=PIN,Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),mode=mode,jump_mask=jump,
        frozen_e161_prefix=True,required_native_variant=3,first_BBC1_cookies_and4193bytes=True,
        no_gameplay_seeds=True,source_qualified=False,native_ready=False,outputs=0,Mesen=False)

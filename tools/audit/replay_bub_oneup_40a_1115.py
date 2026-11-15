"""Genuine M then hidden1UP using actual authored block and original bubble."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import inspect
import replay_bub_flower_margin_40a_1115 as Previous
import replay_bub_flower_7a80_1115 as Witness

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN
PARENT='88a452e94489dea2749403abc193b7c4a2578b7a2e837183a0cf102af3d85b76'
once=Previous.once

@lru_cache(maxsize=2)
def bindings(raw,identity=0):
    Previous.reference(raw);b=dict(W.Symbols.bundle(),raw=raw)
    fields={n:W.address(b,n)for n in('NumberofLives','Square2SoundQueue','FloateyNum_Control','FloateyNum_Timer')}
    hooks={}
    def hook(name,at,pc):hooks[name]=dict(pc=pc,offset=at-16,data=raw[at:at+8].hex())
    for name in('MarioSourcePowerupCollision','EraseEnemyObject','SetupFloateyNumber'):
        hook(name,W.location(b,name),W.address(b,name))
    at=W.location(b,'MarioSourcePowerupCollision');pc=W.address(b,'MarioSourcePowerupCollision')
    def store(op,address):return bytes((op,address))if address<256 else bytes(({0x95:0x9d,0x85:0x8d}[op],address&255,address>>8))
    pattern=bytes((0xa9,11))+store(0x95,fields['FloateyNum_Control'])+b'\x60'
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0]+len(pattern)-1;hook('LifeReturn',at+delta,pc+delta)
    at=W.location(b,'FloateyNumbersCore');pc=W.address(b,'FloateyNumbersCore');life=fields['NumberofLives']
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    pattern=inc+bytes((0xa9,64))+store(0x85,fields['Square2SoundQueue'])
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    hook('LifeBefore',at+hits[0],pc+hits[0]);delta=hits[0]+len(pattern);hook('LifeAfter',at+delta,pc+delta)
    return dict(ram=fields,hooks=hooks)

STOCK=r'''
stock={phase='M',age=0,last=-1,rows={}}
local lifePending=nil
local function lifeState()local s=itemState();s.original_life=work(2,identity==1 and 0x42 or 0x2e);s.source_lease=work(2,0xc308);return s end
local function lifeActor()
 for i=0,5 do
  if read(L.Enemy_Flag+i)==1 and read(L.Enemy_ID+i)==46 and read(L.PowerUpType+i)==3 then
   return{slot=i,kind=3,state=read(L.Enemy_State+i),x=full_x(i),y=read(L.Enemy_Y_Position+i)}
  end
 end
end
for name,h in pairs(Life.hooks)do
 emu.addMemoryCallback(guard(function()
  if not game or not mapped(h.pc,emu.memType.nesPrgRom,h.offset)then return end
  for i=1,#h.data,2 do assert(read(h.pc+(i-1)//2)==tonumber(h.data:sub(i,i+1),16),'Actual native1UP hook '..name)end
  local cpu=emu.getState();local a=lifeActor()
  if name=='MarioSourcePowerupCollision'and a and a.state>=128 then
   assert(cpu['cpu.x']==a.slot,'Actual physical1UP collector slot');assert(not stock.collector,'One real1UP collector')
   stock.collector={state=lifeState(),actor=a,player_box=itemBox(Stock.ram.BoundingBox_UL_Corner),item_box=itemBox(Stock.ram.EnemyBoundingBoxCoord+4*a.slot)}
  elseif name=='EraseEnemyObject'and stock.collector and cpu['cpu.x']==stock.collector.actor.slot then stock.erase=lifeState()
  elseif name=='SetupFloateyNumber'and stock.collector and cpu['cpu.x']==stock.collector.actor.slot then stock.setup={control=cpu['cpu.a'],state=lifeState()}
  elseif name=='LifeReturn'and stock.collector then
   local slot=stock.collector.actor.slot
   stock.returned={state=lifeState(),control=read(Life.ram.FloateyNum_Control+slot),timer=read(Life.ram.FloateyNum_Timer+slot)}
   assert(stock.returned.control==11,'Actual deferred1UP popup11')
  elseif name=='LifeBefore'and stock.returned and cpu['cpu.x']==stock.collector.actor.slot then
   assert(r('NumberofLives')==2,'Real life balance before deferred INC');lifePending={state=lifeState(),timer=read(Life.ram.FloateyNum_Timer+cpu['cpu.x'])}
  elseif name=='LifeAfter'and lifePending then
   assert(r('NumberofLives')==3 and read(Life.ram.Square2SoundQueue)==64,'Actual INC2to3 and cue64')
   stock.credit={state=lifeState(),before=lifePending};lifePending=nil
  end
 end),emu.callbackType.exec,h.pc)
end
local function lifePhase(p)stock.phase=p;stock.age=0 end
local function full_tick(finish)
 observePickup()
 if stock.phase=='M'then
  return mushroom_tick(function(ok)
   assert(ok,'Exact genuine M prefix');stock.M_moves=actualMoves;stock.M=flower.pickups.M
   currentPickup=nil;lifePhase('M-resume');full_pad={}
  end)
 end
 local q=BUB_OBSERVER.summary();local x,y=full_x(),r('Player_Y_Position');local actor=identity==1 and 0x42 or 0x2e
 assert(r('GameEngineSubroutine')~=11,'Living genuine hidden1UP route')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Authored hidden1UP in actual1-1')
 if q.completed_Main~=stock.last then
  stock.last=q.completed_Main;stock.age=stock.age+1
  if q.completed_Main%8==0 then
   local t=stock.rows;t[#t+1]={state=lifeState(),phase=stock.phase,part=full_part,rides=q.source_bubble_ride_restarts,held=full_state(0x301),item=lifeActor()}
   if#t>24 then table.remove(t,9)end
  end
 end
 assert(stock.age<1700,'Bounded ordinary hidden1UP phase '..stock.phase)
 if stock.phase=='M-resume'then
  full_pad={}
  if actualMoves-stock.M_moves==25 then
   requirePickup(stock.M,25);full_part='approach';full_step=0;full_last=q.completed_Main-1;flower.phase='stock-life';lifePhase('travel')
  else return end
 end
 if stock.credit then
  stock.resume=actualMoves-stock.credit.state.moves;full_pad={}
  assert(stock.resume<=25,'Exactly25 actual Bub entries after real life writer')
  if stock.resume==25 then
   assert(stock.born and stock.mature and stock.collector and stock.erase and stock.setup and stock.returned,'Complete natural1UP lifecycle')
   assert(stock.setup.control==6 and stock.returned.control==11 and stock.credit.before.timer==42,'Native setup6/final11/delayed42')
   assert(stock.ride and r('NumberofLives')==3,'Actual earned bubble support and retained third life')
   assert(lifeState().flags==1 and r('PlayerStatus')==1 and r('GuestPowerupActive')==0,'Preserve earned M upgrades, no1UP freeze')
   assert(itemScore()==stock.collector.state.score,'1UP does not award score')
   finish(true,'Natural hidden1UP actual INC and25 actual postwriter Bub entries');return
  end
  return
 end
 if stock.collector then full_pad={};return end
 local a=lifeActor()
 if a then
  assert(a.x>=1024 and stock.block==96,'Real authored hidden96 block')
  stock.born=stock.born or{state=lifeState(),actor=a}
  if a.state>=128 then stock.mature=stock.mature or{state=lifeState(),actor=a}end
  lifePhase('intercept')
 end
 if stock.phase=='travel'then
  if x>=976 and full_normal_jump_ready(actor)then
   local _,tile=full_solid(1028,128);assert(tile==96,'Actual authored hidden tile96')
   stock.block=tile;lifePhase('runup');full_pad={}
  else return full_tick_base(finish)end
 end
 if stock.phase=='runup'then
  assert(full_solid(956,208),'Actual safe run-up floor past pipe4')
  if not full_normal_jump_ready(actor)then full_pad={};return end
  if x>958 then full_pad={left=true}
  elseif x<954 then full_pad={right=true}
  elseif full_state(0x102+(identity==1 and 8 or 0))&64==0 then full_pad={right=true}
  elseif full_launch_ready(actor)and full_state(0x301)&128==0 then stock.base=q;lifePhase('grow');full_pad={right=true,b=true}
  else full_pad={}end
 elseif stock.phase=='grow'then
  local takeoff;full_pad,takeoff=poweredGrowth(q,stock.base,stock.age)
  if stock.age>=5 then assert(q.launches>stock.base.launches,'Actual hidden1UP free-bubble launch')end
  if takeoff then lifePhase('board')end
  assert(stock.age<180,'Actual grown bubble takeoff window')
 elseif stock.phase=='board'then
  full_pad={right=true,a=true};full_pad=poweredAir(q,stock.base)or full_pad
  if q.source_bubble_ride_restarts>stock.base.source_bubble_ride_restarts then stock.ride=stock.ride or lifeState()end
  assert(x<1090,'Hidden1UP must actually emerge before first pit')
 elseif stock.phase=='intercept'then
  assert(full_solid(1060,208),'Actual real floor at mature1UP interceptor')
  full_pad={right=x<1058,left=x>1062}
 end
end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    assert mode=='mushroom'and identity in(0,1)
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.baseline(raw,identity)
    at=text.index('\n')+1;text=text[:at]+'local Life='+Witness.Base.Previous.lua(bindings(raw,identity))+'\n'+text[at:]
    text=once(text,'local function finish(','local stock=nil\nlocal function finish(')
    text=once(text,'natural_flower=flower','natural_flower=flower,natural_stock=stock')
    text=once(text,"assert(r('NumberofLives')==2 and work(2,0xc300)==identity,'Living exact Bubble identity')",
        "assert(r('NumberofLives')==(stock and stock.credit and 3 or 2)and work(2,0xc300)==identity,'Exact living Bubble identity and authenticated1UP balance')")
    text=once(text,'local function full_tick(finish)','local function unused_flower_tick(finish)')
    text=once(text,'local routeStarted=false',STOCK+'\nlocal routeStarted=false')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text

def source_check(raw,identity=0):
    base=SimpleNamespace(reference=Previous.reference,Previous=Witness.Base.Previous)
    ns=dict(Witness.__dict__,Base=base,PIN=PIN,controller=controller)
    exec(compile(inspect.getsource(Witness.source_check),str(Path(__file__))+':current-life-source','exec'),ns)
    return ns['source_check'](raw,identity)

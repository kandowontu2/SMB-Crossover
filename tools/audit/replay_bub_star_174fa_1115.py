"""Genuine M/F/+25 then ordinary authored Star; frozen palette parents unchanged."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import inspect
import replay_bub_native_palette_current_1115 as Previous

R,ROM,W,N,B,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.B,Previous.PIN
C=Previous.C
once=Previous.Flower.once
PARENT='9ce50ca8ba05b2d6c21f13b41b52258352db966c70b22ed113ee7971d34f694d'

def load_current():
    raw=ROM.read_bytes();actual=sha256(raw).hexdigest()
    if actual==C.PARENT:raw=C.proposal(raw)[0]
    else:assert actual==PIN,'Exact174fa current or exact40a owning parent only'
    C.inverse(raw)
    return raw,actual

@lru_cache(maxsize=1)
def bindings(raw):
    C.inverse(raw);b=dict(W.Symbols.bundle(),raw=raw)
    fields={n:W.address(b,n)for n in('StarInvincibleTimer','AreaMusicQueue','Square2SoundQueue','GuestPowerupActive','NumberofLives','FloateyNum_Timer','FloateyNum_Control','Player1ScoreDisplay')}
    hooks={}
    for name in('MarioSourcePowerupCollision','EraseEnemyObject','SetupFloateyNumber'):
        at=W.location(b,name);pc=W.address(b,name)
        hooks[name]=dict(pc=pc,offset=at-16,data=raw[at:at+8].hex())
    at=W.location(b,'MarioSourcePowerupCollision');pc=W.address(b,'MarioSourcePowerupCollision')
    def sta(a):return bytes((0x85,a))if a<256 else bytes((0x8d,a&255,a>>8))
    pattern=bytes((0xa9,35))+sta(fields['StarInvincibleTimer'])+bytes((0xa9,64))+sta(fields['AreaMusicQueue'])+b'\x60'
    hits=[i for i in range(128-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0]+len(pattern)-1
    hooks['StarReturn']=dict(pc=pc+delta,offset=at+delta-16,data=raw[at+delta:at+delta+8].hex())
    at=W.location(b,'FloateyNumbersCore');pc=W.address(b,'FloateyNumbersCore');life=fields['NumberofLives']
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    pattern=inc+bytes((0xa9,64))+sta(fields['Square2SoundQueue'])
    hits=[i for i in range(128-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0]+len(pattern);assert raw[at+delta]==0xbe
    hooks['ScorePrepare']=dict(pc=pc+delta,offset=at+delta-16,data=raw[at+delta:at+delta+8].hex())
    at=W.location(b,'AddToScore');pc=W.address(b,'AddToScore')
    hooks['AddToScore']=dict(pc=pc,offset=at-16,data=raw[at:at+8].hex())
    return dict(ram=fields,hooks=hooks)

WITNESS=r'''
local starWorker=nil;local starReturnSites={};local completedBubReturns=0;local enteredBubSerial=0
local scoreReturnSites={}
local function starState()
 local s=itemState();s.actual_returns=completedBubReturns;s.star=read(Star.ram.StarInvincibleTimer)
 return s
end
local function starActor()
 for i=0,5 do
  if read(L.Enemy_Flag+i)==1 and read(L.Enemy_ID+i)==46 and read(L.PowerUpType+i)==2 then
   return{slot=i,kind=2,state=read(L.Enemy_State+i),x=full_x(i),y=read(L.Enemy_Y_Position+i)}
  end
 end
end
local function starCaller()
 local s=emu.getState();local sp=s['cpu.sp']
 return sp,read(0x101+sp)+256*read(0x102+sp)+1
end
local moveHook=Stock.hooks.BbNativeUpdate
emu.addMemoryCallback(guard(function()
 if not game or not active()or not mapped(moveHook.pc,emu.memType.nesWorkRam,moveHook.offset)then return end
 assert(not starWorker,'One outstanding actual original movement worker')
 enteredBubSerial=enteredBubSerial+1
 local sp,ret=starCaller();starWorker={sp=sp+2,ret=ret,entry=enteredBubSerial}
 if not starReturnSites[ret]then
  starReturnSites[ret]=true
  emu.addMemoryCallback(guard(function()
   if not starWorker or starWorker.ret~=ret or emu.getState()['cpu.sp']~=starWorker.sp then return end
   local token=starWorker;starWorker=nil;completedBubReturns=completedBubReturns+1
   if star and star.collected and token.entry>star.collected.entry_serial then
    star.post_collector_returns=(star.post_collector_returns or 0)+1
    star.first_post=star.first_post or starState();star.last_post=starState()
   end
   if star and star.credit and token.entry>star.credit.entry_serial then star.post_credit_returns=(star.post_credit_returns or 0)+1 end
  end),emu.callbackType.exec,ret)
 end
end),emu.callbackType.exec,moveHook.pc)
for name,h in pairs(Star.hooks)do
 emu.addMemoryCallback(guard(function()
  if not game or not star or not mapped(h.pc,emu.memType.nesPrgRom,h.offset)then return end
  for i=1,#h.data,2 do assert(read(h.pc+(i-1)//2)==tonumber(h.data:sub(i,i+1),16),'Exact real Star native hook '..name)end
  local slot=emu.getState()['cpu.x'];local a=starActor()
  if name=='MarioSourcePowerupCollision'and a and a.state>=128 then
   assert(slot==a.slot and star.born and star.mature and not star.collector,'Actual mature Star physical collector')
   star.collector={state=starState(),actor=a,player_box=itemBox(Stock.ram.BoundingBox_UL_Corner),item_box=itemBox(Stock.ram.EnemyBoundingBoxCoord+4*slot)}
   assert(read(Star.ram.StarInvincibleTimer)==0,'No Star timer before physical pickup')
  elseif name=='EraseEnemyObject'and star.collector and slot==star.collector.actor.slot then star.erase=starState()
  elseif name=='SetupFloateyNumber'and star.collector and slot==star.collector.actor.slot then
   assert(emu.getState()['cpu.a']==6,'Actual Star1000 setup control6');star.popup={control=6,state=starState()}
  elseif name=='StarReturn'and star.collector and not star.collected then
   assert(star.erase and star.popup and read(L.Enemy_Flag+star.collector.actor.slot)==0,'Real Star erase and popup')
   assert(read(Star.ram.StarInvincibleTimer)==35 and read(Star.ram.AreaMusicQueue)==64 and read(Star.ram.Square2SoundQueue)&32~=0,'Actual Star35/music64/cue32')
   assert(read(Star.ram.GuestPowerupActive)==0,'Star has no hosted M/F freeze')
   star.collected={state=starState(),entry_serial=enteredBubSerial,timer=35,music=64,cue=read(Star.ram.Square2SoundQueue)};star.post_collector_returns=0
   assert(star.collected.state.flags==star.collector.state.flags and star.collected.state.power==star.collector.state.power,'Native Star preserves actual earned original gear')
  elseif name=='ScorePrepare'and star.collected and not star.credit and slot==star.collector.actor.slot then
   local cpu=emu.getState()
   assert(cpu['cpu.a']==43 and cpu['cpu.y']==6 and read(Star.ram.FloateyNum_Timer+slot)==42,'Actual oldtimer43 score branch, postDEC42/control6')
   star.credit_pending={state=starState(),old_timer=43,post_dec_timer=42,slot=slot,writes={}}
  elseif name=='AddToScore'and star.credit_pending then
   local sp,ret=starCaller();star.credit_pending.ret=ret;star.credit_pending.sp=sp+2
   if not scoreReturnSites[ret]then
    scoreReturnSites[ret]=true
    emu.addMemoryCallback(guard(function()
     local p=star and star.credit_pending
     if not p or p.ret~=ret or emu.getState()['cpu.sp']~=p.sp then return end
     assert(#p.writes>0 and itemScore()==star.collector.state.score+1000,'Actual decimal score writes complete Star1000')
     star.credit={state=starState(),entry_serial=enteredBubSerial,writer=p};star.credit_pending=nil;star.post_credit_returns=0
    end),emu.callbackType.exec,ret)
   end
  end
 end),emu.callbackType.exec,h.pc)
end
for digit=0,5 do
 local address=Star.ram.Player1ScoreDisplay+digit
 emu.addMemoryCallback(guard(function(at,value)
  local p=star and star.credit_pending
  if p then assert(#p.writes<12,'Bounded real decimal score writes');p.writes[#p.writes+1]={address=at,old=read(at),new=value,PC=emu.getState()['cpu.pc']}end
 end),emu.callbackType.write,address)
end
'''

ROUTE=r'''
local function full_tick(finish)
 if not star then return flower_tick_preserved(finish)end
 local q=BUB_OBSERVER.summary();local x,y=full_x(),r('Player_Y_Position');local actor=identity==1 and 0x42 or 0x2e
 assert(r('GameEngineSubroutine')~=11 and r('NumberofLives')==2,'Living ordinary earned-M/F Star continuation')
 assert(r('WorldNumber')==0 and r('LevelNumber')==0,'Actual authored1-1 Star')
 if q.completed_Main~=star.last then
  star.last=q.completed_Main;star.age=star.age+1
  if q.completed_Main%8==0 then
   local a=star.rows;a[#a+1]={state=starState(),phase=star.phase,part=full_part,index=full_index,held=full_state(0x301),item=starActor(),rides=q.source_bubble_ride_restarts}
   if#a>24 then table.remove(a,9)end
  end
 end
 assert(star.age<1800,'Bounded ordinary Star phase '..star.phase)
 if star.collected then
  full_pad={};assert((star.post_credit_returns or 0)<=25,'Exactly25 completed workers after actual score writer')
  if star.credit and star.post_credit_returns==25 then
   assert(star.born and star.mature and star.collector and star.erase and star.popup and star.credit,'Complete natural Star lifecycle and actual timer43/1000 writer')
   assert(read(Star.ram.StarInvincibleTimer)>0 and r('GuestPowerupActive')==0,'Real Star remains active without M/F freeze')
   assert(itemScore()==star.collector.state.score+1000,'Exactly1000 actual native score from Star')
   assert(star.post_collector_returns>=25,'Retain postcollector completion count separately')
   finish(true,'Genuine M/F then natural Star1000 and25 completed new original workers after credit');return
  end
  return
 end
 local a=starActor()
 if a then
  if not star.born then assert(a.x==1616,'Authored real Star block1616');star.born={state=starState(),actor=a}end
  if a.state>=128 then star.mature=star.mature or{state=starState(),actor=a}end
  star.phase='intercept'
 end
 if star.phase=='floor-runup'then
  if not star.floor_ready then
   full_pad={right=x<1306}
   if x>=1304 and y==176 and full_normal_jump_ready(actor)then star.floor_ready=starState()end
   return
  end
  assert(full_solid(1268,208),'Actual safe floor below Flower roof, before second pit')
  if y~=176 or not full_normal_jump_ready(actor)then full_pad={};return end
  full_pad={left=x>1266,right=x<1262}
  if x>=1262 and x<=1266 then
   if full_state(0x102+(identity==1 and 8 or 0))&64==0 then full_pad={right=true}
   elseif full_launch_ready(actor)and full_state(0x301)&192==0 then
    star.phase='travel';star.age=0;star.fast_launch=starState();obstacles[6].lead=112
    full_part='grow';full_step=0;full_last=q.completed_Main;full_ride_base=q;full_start_y=y;full_min_y=y
    flower.phase='grow';full_pad={right=true,b=true}
   else full_pad={}end
  end
  return
 end
 if star.phase=='travel'then
  if x>=1570 and full_normal_jump_ready(actor)then
   local solid,tile=full_solid(1620,144);assert(solid,'Actual solid authored Star brick')
   star.block={x=1616,y=144,tile=tile};star.phase='align';star.age=0;full_pad={}
  else
   if q.completed_Main>full_last+1 then full_last=q.completed_Main-1 end
   return full_tick_base(finish)
  end
 end
 if star.phase=='align'then
  full_pad={right=x<1617,left=x>1619}
  if x>=1617 and x<=1619 and full_normal_jump_ready(actor)and full_state(0x301)&128==0 then
   star.phase='bump';star.age=0;star.bump=starState();full_pad={a=true}
  end
 elseif star.phase=='bump'then
  full_pad={a=star.age<25}
  assert(star.age<90,'Actual ordinary head bump must produce authored Star')
 elseif star.phase=='intercept'then
  if a then full_pad={right=x<a.x-3,left=x>a.x+3}else full_pad={}end
  assert(x<2000,'Bounded live Star pursuit before later pipe')
 end
end
'''

@lru_cache(maxsize=2)
def controller(raw,identity=0,mode='mushroom'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.controller(raw,identity,mode,stock='flower')
    at=text.index('\n')+1;text=text[:at]+'local Star='+Previous.Witness.Base.Previous.lua(bindings(raw))+'\n'+text[at:]
    text=once(text,'local function finish(','local star=nil\nlocal function finish(')
    text=once(text,'natural_flower=flower','natural_flower=flower,natural_star=star')
    text=once(text,"   finish(true,'Genuine earned Mushroom then Flower and25 actual movement calls');return",
        "   star={phase='floor-runup',age=0,last=q.completed_Main,rows={},F_ready=itemState()};currentPickup=nil\n   flower.phase='stock-star';full_part='approach';full_step=0;full_last=q.completed_Main;full_pad={};return")
    text=once(text,'local function full_tick(finish)',WITNESS+'\nlocal function flower_tick_preserved(finish)')
    text=once(text,'local routeStarted=false',ROUTE+'\nlocal routeStarted=false')
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text

def source_check(raw,identity=0):
    Witness=Previous.Witness;base=SimpleNamespace(reference=C.inverse,Previous=Witness.Base.Previous)
    ns=dict(Witness.__dict__,Base=base,PIN=PIN,controller=controller)
    exec(compile(inspect.getsource(Witness.source_check),str(Path(__file__))+':actual-star-source','exec'),ns)
    return ns['source_check'](raw,identity)

"""Strict current7a80 WWF genuine M/hidden1UP or M/F/Star, normal inputs."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import compose_gimmick_empty_side_1115 as Current
import replay_wwf_flower_cue_observed_1115 as Parent
import replay_wwf_natural_flower_native_1115 as Base
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN=Current.R,Current.ROM,Current.W,Current.N,Current.CURRENT_CANDIDATE
IDENTITIES=Parent.IDENTITIES
PARENT_SOURCE='440bbaf77683e74e96c6c3bc9d88a337cff60a3f69f8c25c0e2642ea97c59aa6'
KINDS={'oneup':3,'star':2}
once=Parent.Previous.Previous.once


@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and sha256(raw).hexdigest()==PIN,'Expected exact owning7a80'
    assert sha256(Path(Parent.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    return Current.current_inverse(raw)


def normalize(raw):return Parent.normalize(reference(raw))


class Frozen:
    LuaRuntime=Base.Source.Images.WWF.Frozen.LuaRuntime
    normalize=staticmethod(normalize)


@lru_cache(maxsize=12)
def bindings(raw,key='hogan',kind='oneup'):
    assert key in IDENTITIES and kind in KINDS
    q=deepcopy(Parent.bindings(reference(raw),key));q.update(sha=PIN,stock_kind=KINDS[kind],stock_name=kind)
    b=dict(W.Symbols.bundle(),raw=raw)
    for name in('SavedJoypadBits','FloateyNum_Timer','StarInvincibleTimer','AreaMusicQueue','BoundingBox_UL_Corner','EnemyBoundingBoxCoord','Enemy_OffscreenBits'):
        q['ram'][name]=W.address(b,name)
    def hook(name,at,pc):
        bank=(at-16)//8192;q['hooks'][name]=dict(pc=pc,offset=at-16,bytes=list(raw[at:at+8]),bank=bank,
            bank_SHA256=sha256(raw[16+bank*8192:16+(bank+1)*8192]).hexdigest())
    for name in('MarioSourcePowerupCollision','EraseEnemyObject','SetupFloateyNumber'):
        hook(name,W.location(b,name),W.address(b,name))
    name='MarioSourcePowerupCollision';at=W.location(b,name);pc=W.address(b,name)
    def store(op,address):return bytes((op,address))if address<256 else bytes(({0x95:0x9d,0x85:0x8d}[op],address&255,address>>8))
    pattern=bytes((0xa9,11))+store(0x95,W.address(b,'FloateyNum_Control'))+b'\x60'
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0]+len(pattern)-1;hook('StockOneupReturn',at+delta,pc+delta)
    pattern=bytes((0xa9,64))+store(0x85,W.address(b,'AreaMusicQueue'))+b'\x60'
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    delta=hits[0]+len(pattern)-1;hook('StockStarReturn',at+delta,pc+delta)
    name='FloateyNumbersCore';at=W.location(b,name);pc=W.address(b,name);life=W.address(b,'NumberofLives')
    inc=bytes((0xe6,life))if life<256 else bytes((0xee,life&255,life>>8))
    pattern=inc+bytes((0xa9,64))+store(0x85,W.address(b,'Square2SoundQueue'))
    hits=[i for i in range(160-len(pattern))if raw[at+i:at+i+len(pattern)]==pattern];assert len(hits)==1
    hook('StockCreditBefore',at+hits[0],pc+hits[0]);delta=hits[0]+len(pattern);hook('StockCreditAfter',at+delta,pc+delta)
    for label,h in q['hooks'].items():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes']),label
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q


STOCK=r'''
local function box(name,slot)local a={};for i=0,3 do a[#a+1]=r(name,(slot or 0)*4+i)end;return a end
local function stackReturn()
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 return sp,read(256+((sp+1)&255))+256*read(256+((sp+2)&255))+1
end
local function stockActor()
 for i=0,5 do local a=actor(i);if a.flag==1 and a.id==46 and a.kind==C.stock_kind then return a end end
end
local function observeStock(s)
 if not stock.active then return end
 local a=stockActor()
 if a then
  if not stock.born then assert(a.x==(C.stock_kind==3 and 1024 or 1616),'Actual authored stock block');stock.born={state=s,actor=a}end
  if a.state>=128 then stock.mature=stock.mature or{state=s,actor=a}end
  if a.state>=128 and completed%4==0 then
   stock.follow_trace=stock.follow_trace or{};local t=stock.follow_trace
   t[#t+1]={state=s,actor=a,player_box=box('BoundingBox_UL_Corner'),item_box=box('EnemyBoundingBoxCoord',a.slot),offscreen=r('Enemy_OffscreenBits',a.slot),bits=pad}
   if#t>20 then table.remove(t,11)end
  end
 end
end
local function stockDrive(s)
 stock.age=(stock.age or 0)+1;assert(stock.age<1700,'Bounded ordinary WWF stock continuation')
 if stock.collected then
  local credit=C.stock_kind==3 and stock.credit or stock.collected
  if credit then
   stock.resume=moves-credit.moves;assert(stock.resume<=25,'Exactly25 actual post-writer/collector WWF entries')
   stock.final_score=score()
   if C.stock_kind==2 and stock.final_score>=stock.collector.score+1000 then stock.score_awarded=stock.score_awarded or state()end
   if stock.resume==25 then
    assert(stock.born and stock.mature and stock.collector and stock.erase and stock.setup and stock.popup,'Complete physical stock lifecycle')
    if C.stock_kind==3 then assert(s.lives==3 and stock.credit and stock.credit.cue==64,'Real extra life retained through25 WWF calls')
    else assert(r('StarInvincibleTimer')>0 and stock.score_awarded and s.power==stock.collector.state.power,'Real Star and delayed1000 score, preserve actual armor')end
    finish(true,'Natural WWF '..C.stock_name..' and25 actual post-credit WWF movement entries');return
   end
  end
  pad=0;return
 end
 local a=stockActor()
 if a then
  if C.stock_kind==3 and(a.state<128 or a.y<s.y-16)then
   -- Measured WWF walk is3px/4updates while this actor moves1px/update.
   -- Use its real emergence interval to wait on the actual floor below its
   -- off-block descent, rather than start a losing chase after maturity.
   assert(solid(1068,216),'Real floor at the ordinary1UP interception point')
   stock.phase='intercept';stock.intercept=stock.intercept or state()
   pad=s.x<1058 and 1 or(s.x>1062 and 2 or 0);return
  end
  if a.state<128 then pad=0;return end
  stock.phase='follow'
  local dx=a.x-s.x;pad=dx>2 and 1 or(dx< -8 and 2 or 0)
  if C.stock_kind==2 and math.abs(dx)<40 and a.y<s.y-16 and s.native==0 and completed-(stock.jump or-100)>40 then
   stock.jump=completed;pad=pad|128;stock.phase='follow-jump'
  end
  if stock.phase=='follow-jump'and(completed-stock.jump<4 or s.vy>=128)then pad=pad|128 end
  return
 end
 if C.stock_kind==3 then
  if stock.phase=='align'then
   if near(s)and s.native==0 then pad=punch();return end
   if s.x<1016 then pad=1;stock.release=polls
   elseif s.x>1020 then pad=2;stock.release=polls
   else
    pad=0;stock.release=stock.release or polls
    if s.native==0 and polls-stock.release>=2 and r('SavedJoypadBits')&128==0 and r('PreviousA_B_Buttons')&128==0 then
     local idx=(1024//256)%2*208+((128-32)//16)*16+(1024%256)//16
     stock.hidden_tile=r('Block_Buffer_1',idx);assert(stock.hidden_tile==96,'Actual authored hidden1UP metatile96')
     stock.phase='head';stock.jump=completed;stock.request=state();pad=128
    end
   end
  elseif stock.phase=='head'then
   assert(completed-stock.jump<100,'Ordinary hidden block head jump')
   if s.native==1 and s.vy>=128 then stock.admission=stock.admission or state()end
   pad=(completed-stock.jump<4 or s.vy>=128)and 128 or 0
  end
  return
 end
 -- Ordinary continuation from the genuinely earned Flower roof. Preserve
 -- cooldown landing defense and walking-action retirement before each punch.
 if s.x<1598 then
  pad=1
  if stock.travel_jump then
   local age=completed-stock.travel_jump;if age<4 or s.vy>=128 then pad=129 end
   if age>12 and s.native==0 then stock.travel_jump=nil;stock.cooldown=8 end
  elseif(stock.cooldown or 0)>0 then stock.cooldown=stock.cooldown-1
  elseif s.native==0 then
   local pit=s.x>=1346 and s.x<1424
   if pit or not solid(s.x+12,216)or solid(s.x+28,s.y+24)then stock.travel_jump=completed;pad=129 end
  end
  if s.native==0 and near(s)then pad=punch()elseif stock.travel_jump and completed%18<3 then pad=pad|(C.role==3 and 68 or 64)end
 else
  if s.x<1608 then pad=1 elseif s.x>1612 then pad=2 else pad=0 end
  if s.native==0 and s.x>=1608 and s.x<=1612 and r('PreviousA_B_Buttons')&128==0 then
   stock.jump=completed;stock.phase='star-head';pad=128;stock.request=state()
  elseif stock.phase=='star-head'and(completed-stock.jump<4 or s.vy>=128)then pad=pad|128 end
 end
end
hook(C.hooks.HandlePowerUpCollision,function()
 if not menuDone or not stock.active or stock.collected then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];local a=actor(i)
 if a.flag~=1 or a.id~=46 or a.kind~=C.stock_kind then return end
 assert(stock.born and stock.mature and a.state>=128 and not stock.collector,'Actual mature WWF native stock collector')
 stock.collector={state=state(),actor=a,score=score(),player_box=box('BoundingBox_UL_Corner'),item_box=box('EnemyBoundingBoxCoord',i)}
end)
hook(C.hooks.MarioSourcePowerupCollision,function()
 if not stock.collector or stock.collected then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];assert(i==stock.collector.actor.slot,'Actual native stock slot')
 local sp,ret=stackReturn();stockNative={sp=sp,ret=ret,slot=i}
end)
hook(C.hooks.EraseEnemyObject,function()if stockNative then stock.erase=state()end end)
hook(C.hooks.SetupFloateyNumber,function()
 if stockNative then assert(emu.getState()['cpu.a']==6,'Native stock initial popup6');stock.setup=state()end
end)
local function stockReturned(kind)
 if not stockNative or C.stock_kind~=kind then return end
 local sp,ret=stackReturn();assert(sp==stockNative.sp and ret==stockNative.ret,'Actual stock leaf caller PC/SP')
 local i=stockNative.slot;local wanted=kind==3 and 11 or 6
 assert(stock.erase and stock.setup and r('Enemy_Flag',i)==0 and r('FloateyNum_Control',i)==wanted,'Actual stock erase/popup')
 assert(r('GuestPowerupActive')==0 and r('NumberofLives')==2 and r('PlayerStatus')==stock.collector.state.power,'Native stock has no hosted freeze or armor grant')
 stock.popup={control=wanted,timer=r('FloateyNum_Timer',i),state=state()}
 if kind==2 then assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64 and r('Square2SoundQueue')==32,'Actual native Star35/music64/cue32')end
 stock.collected={state=state(),moves=moves,timer=r('StarInvincibleTimer'),music=r('AreaMusicQueue'),cue=r('Square2SoundQueue')};stockNative=nil
end
hook(C.hooks.StockOneupReturn,function()stockReturned(3)end)
hook(C.hooks.StockStarReturn,function()stockReturned(2)end)
hook(C.hooks.StockCreditBefore,function()
 if C.stock_kind~=3 or not stock.collected or stock.credit then return end
 local cpu=emu.getState();local i=cpu['cpu.x'];if i~=stock.collector.actor.slot then return end
 assert(cpu['cpu.y']==11 and r('NumberofLives')==2 and r('FloateyNum_Control',i)==11,'Actual delayed native1UP writer')
 stockCredit={state=state(),moves=moves,slot=i,timer=r('FloateyNum_Timer',i)}
end)
hook(C.hooks.StockCreditAfter,function()
 if not stockCredit then return end
 assert(r('NumberofLives')==3 and r('Square2SoundQueue')==64,'Actual delayed INC2to3 andcue64')
 stock.credit={before=stockCredit,state=state(),moves=moves,cue=64};stockCredit=nil
end)
'''


@lru_cache(maxsize=12)
def controller(raw,key='hogan',kind='oneup'):
    old=reference(raw);text=Parent.controller(old,key)
    prefix='local C='+Text.lua(Parent.bindings(old,key))+'\n';assert text.startswith(prefix)
    body=text[len(prefix):]
    body=once(body,'local pendingMain,pendingPickup,firstJump,travelJump,crossStart',
        'local stock={resume=0}\nlocal stockNative,stockCredit\nlocal pendingMain,pendingPickup,firstJump,travelJump,crossStart')
    body=once(body,"r('LevelNumber')==0 and r('NumberofLives')==2,'Living authored1-1'",
        "r('LevelNumber')==0 and(r('NumberofLives')==2 or(stock.credit and r('NumberofLives')==3)),'Living authored1-1'")
    body=once(body,'WfMovement_calls=moves,items=items,events=events,','WfMovement_calls=moves,natural_stock=stock,stock_kind=C.stock_kind,items=items,events=events,')
    body=once(body,'local function drive()',STOCK+'\nlocal function drive()')
    body=once(body,"assert(completed<4600,'M/F completedMain bound')","observeStock(s);assert(completed<4600,'WWF stock completedMain bound')")
    body=once(body," if s.native==0 and near(s)then combatStart=combatStart or completed else combatStart=nil end\n if phase=='first-M'then",
        " if s.native==0 and near(s)then combatStart=combatStart or completed else combatStart=nil end\n if stock.active then stockDrive(s);return end\n if phase=='first-M'then")
    body=once(body,"if k==1 then finish(true,'Real M and Flower with60-tick transactions and25 resumed moves each')else change('travel')end",
        "if k==1 then stock.active=true;stock.phase='star-travel';change('stock-Star-travel')else change('travel')end")
    body=once(body,"if s.x>=1184 and s.native==0 then assert(s.power==1,'Earned Mushroom armor');change('flower-align')",
        "if C.stock_kind==3 and s.x>=992 and s.native==0 then stock.active=true;stock.phase='align';change('stock-hidden')\n  elseif s.x>=1184 and s.native==0 then assert(s.power==1,'Earned Mushroom armor');change('flower-align')")
    body=once(body,"if a.flag~=1 or a.id~=46 then return end\n local k=a.kind;local it=assert(items[k],'Observed authored birth');assert(k==0 or k==1,'M/F only')",
        "if a.flag~=1 or a.id~=46 or a.kind>=2 then return end\n local k=a.kind;local it=assert(items[k],'Observed authored birth');assert(k==0 or k==1,'M/F only')")
    result='local C='+Text.lua(bindings(raw,key,kind))+'\n'+body;Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='hogan',kind='oneup'):
    text=controller(raw,key,kind)
    return dict(ROM_SHA256=PIN,identity=key,stock=kind,controller_SHA256=sha256(text.encode()).hexdigest(),
        parent16a_factory_SHA256=PARENT_SOURCE,actual7a80_CPU=True,strict_typed_inverse='Gimmick.current_inverse→exact16a;Parent.normalize→exact590',
        scope='Genuine ordinary WWF M/hidden1UP or M/F/Star, native physical collector/popups/producers/25 actual WfMovement afterwriter/collector; source only pending native',
        gameplay_seeds=0,outputs=0,Mesen_run=False)


def family(kind):
    assert kind in KINDS
    return SimpleNamespace(R=R,ROM=ROM,W=W,N=N,PIN=PIN,IDENTITIES=IDENTITIES,Frozen=Frozen,normalize=normalize,
        bindings=lambda raw,key:bindings(raw,key,kind),controller=lambda raw,key:controller(raw,key,kind),metadata=lambda raw,key:metadata(raw,key,kind))

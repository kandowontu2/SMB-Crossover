"""Current WWF genuine M/F then ordinary early Star interception; no seeds."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import replay_wwf_natural_stock_7a80_1115 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,normalize,IDENTITIES=Previous.Frozen,Previous.normalize,Previous.IDENTITIES
PARENT='1b9879d692c3a50de881c605d8f9b0b3e7257761b8b4958affaddde63675a211'
once=Previous.once


def bindings(raw,key='hogan'):return Previous.bindings(raw,key,'star')


STAR_INTERCEPT=r'''
 if a and C.stock_kind==2 then
  assert(solid(1668,216),'Actual floor at ordinary Star interception point')
  local waiting=s.x<1658 and 1 or(s.x>1662 and 2 or 0)
  -- Finish the actual head-jump descent before walking into the next enemy;
  -- apply the retained walking-retirement defense during emergence too.
  if a.state<128 and s.native~=0 then pad=0;return end
  if s.native==0 and near(s)then pad=punch();return end
  if a.state<128 then
   stock.phase='star-intercept';stock.intercept=stock.intercept or state();pad=waiting;return
  end
  if stock.star_jump then
   local age=completed-stock.star_jump;pad=1
   if age<4 or s.vy>=128 then pad=pad|128 end
   if s.native==1 and s.vy>=128 then stock.star_admission=stock.star_admission or state()end
   if age>12 and s.native==0 then stock.star_jump=nil;stock.star_release=polls end
   return
  end
  local released=not stock.star_release or polls-stock.star_release>=2
  if stock.star_falling and a.x>s.x+8 and math.abs(a.x-s.x)<48 and a.y<s.y-8 and s.native==0 and released and r('PreviousA_B_Buttons')&128==0 and not solid(s.x+8,144)then
   stock.star_jump=completed;stock.star_request=state();pad=129;return
  end
  pad=a.x<s.x+24 and waiting or 1;return
 end
 if stock.born and not a and not stock.collected then error('Actual Star lost before physical collector')end
'''


@lru_cache(maxsize=6)
def controller(raw,key='hogan'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.controller(raw,key,'star')
    text=once(text,'local stock={resume=0}','local starPreviousY\nlocal stock={resume=0}')
    text=once(text,"  if a.state>=128 then stock.mature=stock.mature or{state=s,actor=a}end",
        "  if a.state>=128 then stock.mature=stock.mature or{state=s,actor=a};stock.star_falling=starPreviousY and a.y>starPreviousY or false;starPreviousY=a.y end")
    marker=" local a=stockActor()\n if a then\n  if C.stock_kind==3"
    text=once(text,marker,' local a=stockActor()\n'+STAR_INTERCEPT+' if a then\n  if C.stock_kind==3')
    observer=r'''
emu.addMemoryCallback(guard(function(address,value)
 if stockNative and value&32~=0 then
  local cpu=emu.getState();stock.cue_producer={value=value,PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=state()}
 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
emu.addMemoryCallback(guard(function(address,value)
 if stockNative and value==64 then
  local cpu=emu.getState();stock.music_producer={value=value,PC=cpu['cpu.pc'],SP=cpu['cpu.sp'],state=state()}
 end
end),emu.callbackType.write,C.ram.AreaMusicQueue)
'''
    text=once(text,'hook(C.hooks.MarioSourcePowerupCollision,function()',observer+'hook(C.hooks.MarioSourcePowerupCollision,function()')
    text=once(text,"assert(r('StarInvincibleTimer')==35 and r('AreaMusicQueue')==64 and r('Square2SoundQueue')==32,'Actual native Star35/music64/cue32')",
        "assert(r('StarInvincibleTimer')==35 and stock.music_producer and stock.music_producer.value==64 and stock.cue_producer and stock.cue_producer.value&32~=0,'Actual native Star35/music64/cue32 producers')")
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='hogan'):
    q=Previous.metadata(raw,key,'star');q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        parent_factory_SHA256=PARENT,scope='Actual7a80 ordinary WWF M/F then mature native Star interception, physical collector/erase/popup6/actual35+music64+cue32 producers/+1000 and25later WfMovement; source/native pending',
        unchanged_parent_oneup_factory=True,no_game_or_helper_change=True)
    return q


def family():return SimpleNamespace(R=R,ROM=ROM,W=W,N=N,PIN=PIN,IDENTITIES=IDENTITIES,Frozen=Frozen,normalize=normalize,bindings=bindings,controller=controller,metadata=metadata)

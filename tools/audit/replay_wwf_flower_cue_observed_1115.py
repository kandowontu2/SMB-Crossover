"""Observe actual SFX queue producers across the native collector's return."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_wwf_flower_combat_retire_1115 as Previous

R,ROM,W,N,PIN,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN,Previous.IDENTITIES
bindings,normalize=Previous.bindings,Previous.normalize
PARENT='6203ea553d475bccf812e421779a25f7a09b7b73c709650fce55df6df9a181d7'

@lru_cache(maxsize=6)
def controller(raw,key):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.controller(raw,key);once=Previous.Previous.once
    observer="""emu.addMemoryCallback(guard(function(address,value)
 if pendingPickup and value&32~=0 then
  local cpu=emu.getState();local pc=cpu['cpu.pc'];local map=emu.convertAddress(pc)
  pendingPickup.cueProduction={value=value,Main=completed,frame=frame,PC=pc,SP=cpu['cpu.sp'],
   map_type=map and map.memType,map_address=map and map.address}
 end
end),emu.callbackType.write,C.ram.Square2SoundQueue)
"""
    text=once(text,"hook(C.hooks.WfMovement,function()",observer+"hook(C.hooks.WfMovement,function()")
    text=once(text,"assert(r('Square2SoundQueue')&32~=0,'Powerup cue producer')", "assert(p.cueProduction and p.cueProduction.value&32~=0,'Observed actual powerup cue producer')")
    text=once(text,"PC=ret,SP=p.sp,cue=r('Square2SoundQueue')}", "PC=ret,SP=p.sp,cue=r('Square2SoundQueue'),cue_producer=p.cueProduction}")
    Previous.Previous.Previous.Source.Images.WWF.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(text.encode()).hexdigest(),
        parent_factory_SHA256=PARENT,gameplay_seeds=0,outputs=0)

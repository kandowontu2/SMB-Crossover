"""Keep ordinary walking-action retirement before every grounded WWF punch."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_wwf_natural_flower_defense_1115 as Previous

R,ROM,W,N,PIN,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN,Previous.IDENTITIES
bindings,normalize=Previous.bindings,Previous.normalize
PARENT='d5b646d9b30ee7e2af50436a43aa591a2a15a18f3537794f50521a94446c43ab'

@lru_cache(maxsize=6)
def controller(raw,key):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT
    text=Previous.controller(raw,key)
    text=Previous.once(text,"local combatStart", "local combatStart\nlocal previousPower,powerChanges=nil,{}")
    text=Previous.once(text,"local function punch()return completed%18<3 and(C.role==3 and 68 or 64)or 0 end", "local function punch()local age=(completed-(combatStart or completed))%18;return age>=2 and age<5 and(C.role==3 and 68 or 64)or 0 end")
    text=Previous.once(text," if not active()then return end\n if phase=='first-M'then", " if not active()then return end\n if s.native==0 and near(s)then combatStart=combatStart or completed else combatStart=nil end\n if phase=='first-M'then")
    text=Previous.once(text,"identity();local s=state();assert(completed<4600", """identity();local s=state()
 if previousPower~=nil and previousPower~=s.power and#powerChanges<8 then
  local aa={};for i=0,5 do local a=actor(i);if a.flag~=0 then aa[#aa+1]=a end end
  powerChanges[#powerChanges+1]={before=previousPower,after=s.power,state=s,actors=aa,pad=pad}
 end;previousPower=s.power
 assert(completed<4600""")
    text=Previous.once(text,"WfMovement_calls=moves,items=items,events=events,terminal=state(),", "WfMovement_calls=moves,items=items,events=events,power_changes=powerChanges,terminal=state(),")
    Previous.Previous.Source.Images.WWF.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(text.encode()).hexdigest(),
        parent_factory_SHA256=PARENT,gameplay_seeds=0,outputs=0)

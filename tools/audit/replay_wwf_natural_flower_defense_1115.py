"""Typed16a ordinary WWF policy with the retained landing-defense input rule."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import compose_prince_body_transition_590_1115 as Current
import replay_wwf_natural_flower_native_1115 as Previous

R,ROM,W,N,IDENTITIES=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.IDENTITIES
PIN=Current.CANDIDATE
FACTORY='ce286247d8663878373fd144a0053d8a698e9b4f35fd049fd86fb855738bfe37'
TEMPLATE='e941920234332e5a08f5fd458f19597ca03663f94927ec7e2ae9fc09e0bdac21'

def normalize(raw):return Previous.normalize(Current.inverse(raw))

def once(text,old,new):
    assert text.count(old)==1,('Unique control-policy edit',old)
    return text.replace(old,new,1)

@lru_cache(maxsize=6)
def bindings(raw,key):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==FACTORY
    assert sha256(Previous.TEMPLATE.read_bytes()).hexdigest()==TEMPLATE
    q=deepcopy(Previous.bindings(Current.inverse(raw),key));q['sha']=PIN
    for h in q['hooks'].values():
        at=16+h['offset'];assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        if 'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=sha256(raw[at:at+8192]).hexdigest()
    return q

@lru_cache(maxsize=6)
def controller(raw,key):
    parent=Current.inverse(raw);canonical=Previous.Source.Images.WWF.Previous.Frozen.lua
    old=Previous.controller(parent,key);prefix='local C='+canonical(Previous.bindings(parent,key))+'\n'
    assert old.startswith(prefix);body=old[len(prefix):]
    body=once(body,"local phase,pipe,cooldown,retreatSettle='first-M',0,0,0", "local phase,pipe,cooldown,retreatSettle='first-M',0,0,0\nlocal combatStart")
    body=once(body,"  else\n   pad=1\n   if travelJump then", "  else\n   local danger=near(s)\n   if s.native==0 and danger then combatStart=combatStart or completed else combatStart=nil end\n   pad=1\n   if travelJump then")
    old_end="   end\n  end\n elseif phase=='flower-align'then"
    new_end="""   end
   -- Retained native full-route rule: defend even during landing cooldown.
   if s.native==0 and danger then
    local age=(completed-(combatStart or completed))%18
    pad=age>=2 and age<5 and(C.role==3 and 68 or 64)or 0
   elseif travelJump and completed%18<3 then pad=pad|(C.role==3 and 68 or 64)end
  end
 elseif phase=='flower-align'then"""
    body=once(body,old_end,new_end)
    text='local C='+canonical(bindings(raw,key))+'\n'+body
    Previous.Source.Images.WWF.Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key):
    text=controller(raw,key)
    return dict(ROM_SHA256=PIN,identity=key,controller_SHA256=sha256(text.encode()).hexdigest(),
        parent590_factory_SHA256=FACTORY,typed_inverse=True,gameplay_seeds=0,outputs=0)

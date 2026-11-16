"""Retain ordinary grip through the original action7 grab admission gate."""
from functools import lru_cache
import replay_prince_oneup_roof_runway_bc5_1115 as Previous
from replay_prince_natural_stock_40a_1115 import LuaRuntime
import audit_prince_sword_control_map_1115 as Map

C,PIN=Previous.C,Previous.PIN

@lru_cache(maxsize=1)
def controller(raw,mode='oneup',jump=8):
    text=Previous.controller(raw,mode,jump)
    assert C.digest(text.encode())=='b1f9c4870751dfeecd3f040bb74cab0eff7e293ee896b71492580607cfdbdfd4'
    labels=Map.labels(C.R/'build/prince-actor-1101-v1/contact-core.lbl');pc=labels['PpN_7_F8A2'];part=C.Packet.extract(raw)[1][0]
    code=part[pc-0xa000:pc-0xa000+26];assert code[:5]==bytes.fromhex('ad16c6c90a')
    def target(i):return(pc+i+2+(code[i+1]if code[i+1]<128 else code[i+1]-256))&65535
    assert code[5]==0xf0 and target(5)==labels['PpN_7_F8B9']
    for i,value in((7,7),(11,23),(15,18),(19,21)):
        assert code[i:i+3]==bytes((0xc9,value,0xf0))and target(i+2)==labels['PpN_7_F8BC']
    assert code[23:]==bytes((0x4c,labels['PpN_7_F9A1']&255,labels['PpN_7_F9A1']>>8))
    old='  pad=s.lock~=0 and 129 or 1';assert text.count(old)==1
    text=text.replace(old,'  pad=129 -- Keep ordinary grip available when the original action7 gate opens.',1)
    LuaRuntime().compile(text);return text

def metadata(raw,mode='oneup',jump=8):
    q=Previous.metadata(raw,mode,jump);q.update(Lua_SHA256=C.digest(controller(raw,mode,jump).encode()),
        original_F8A2_grab_whitelist_exact=[7,23,18,21],action4_and10_skip_that_query=True,
        ordinary_grip_retained_through_actual_fall=True)
    return q

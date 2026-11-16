"""Separate Star successor: query the roof only after actual grounded landing."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_bowser_star_ground_bc5_1115 as Previous

R,ROM,PIN,W,N,Current=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current
PARENT_SHA='17e124ab4906630eb80fed381abc80c9f84d8603825ba3706b959f5eb6c79172'
@lru_cache(maxsize=2)
def controller(raw,identity=0):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SHA
    text=Previous.controller(raw,identity)
    old=" if BStock.kind==2 and stock.phase=='align'and s.y<160 then"
    new=""" if BStock.kind==2 and stock.phase=='align'and s.native_state~=0 then pad=0;return end
 if BStock.kind==2 and stock.phase=='align'and s.y<160 then"""
    text=Previous.Previous.once(text,old,new)
    Previous.Previous.Old.Base.LuaRuntime().compile(text);return text
def metadata(raw,identity=0):
    q=Previous.metadata(raw,identity);q.update(controller_SHA256=sha256(controller(raw,identity).encode()).hexdigest(),
        landing_factory_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        scope='Actual grounded roof foot row before edge query; same real earned M/F prefix and native stock requirements')
    return q

"""Strict590 Flower replay using native-qualified polled/consumed pipe travel."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_gimmick_pipe_handshake_current_1115 as Pipe
import replay_gimmick_flower_board_prince_current_1115 as Flower

R,ROM,W,N,PIN=Pipe.R,Pipe.ROM,Pipe.W,Pipe.N,Pipe.PIN
Frozen,IDENTITIES,normalize,bindings=Pipe.Frozen,Pipe.IDENTITIES,Pipe.normalize,Pipe.bindings
PIPE_SOURCE='1199acdfd81f540d2398f7f8c13623c539c7d2e362b7dd26b1161d469e70749d'
PIPE_LUA='a3e7f6b318154b046674f061ba6a54b815d6934d1e783e91a88588787fce17b3'
FLOWER_SOURCE='4d275416f5eca9162260747b6314cb48333745bac7aa8e1680b942916488eef2'
FLOWER_LUA='061b6d454717b97643f894b3cc22c79d402c7e27c58008ad0e3901beeeb3325c'


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Pipe.__file__).read_bytes()).hexdigest()==PIPE_SOURCE
    assert sha256(Path(Flower.__file__).read_bytes()).hexdigest()==FLOWER_SOURCE
    text=Pipe.controller(raw,key);assert sha256(text.encode()).hexdigest()==PIPE_LUA
    original=Flower.controller(raw,key);assert sha256(original.encode()).hexdigest()==FLOWER_LUA
    # Keep the qualified travel edge state machine; remove only its narrow end.
    travel=Pipe.TRAVEL;start=travel.index(' if c.x>=976');end=travel.index(' local star=',start)
    travel=travel[:start]+travel[end:]
    text=Pipe.once(text,Pipe.TRAVEL,travel)
    old=next(line for line in text.splitlines()if line.startswith(' local ok=reason=='))
    new=next(line for line in original.splitlines()if line.startswith(' local ok=reason=='))
    text=Pipe.once(text,old,new)
    text=Pipe.once(text,"  if gmTravel.done then finish('four-pipes-and25-grounded-input-consumptions');return end\n",'')
    text=Pipe.once(text,'pipe_input_diagnostic=travelReport(),','travel_input_diagnostic=travelReport(),')
    text=Pipe.once(text,"x>=418 and x<1212 end","x>=418 and x<1328 end")
    text=Pipe.once(text,"return x>=640 and x<=760 end","return(x>=640 and x<=760)or(x>=1180 and x<=1280)end")
    # An old travel request cannot become a later Flower admission witness.
    text=Pipe.once(text,'gmInput=controls(context())\n',
        "gmInput=controls(context())\n  if flower.boarding_policy_start then gmTravel.request=nil end\n")
    text=Pipe.once(text," if not travelRegion()or not gmTravel.request then return end",r'''
 if not travelRegion()then return end
 if not gmTravel.request then
  if flower.boarding_policy_start then
   gmTravel.flower_admissions=(gmTravel.flower_admissions or 0)+1
   gmTravel.record('actual-Flower-phase-jump',gmTravel.snapshot())
  end
  return
 end''')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=Pipe.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        native_qualified_pipe_factory_SHA256=PIPE_SOURCE,native_qualified_pipe_controller_SHA256=PIPE_LUA,
        prior_061b_Flower_factory_SHA256=FLOWER_SOURCE,prior_061b_Flower_controller_SHA256=FLOWER_LUA,
        measured_Flower_boarding_input_policy_unchanged=True,
        scope='Genuine M and native-qualified polled/consumed travel, then actual Flower reflection/support/fresh-jump/physical collector/inventory2/next2/cue1c/erase/1000score/25moves. Source-only until root native replay; no fullstage/audio/visual claim')
    return q

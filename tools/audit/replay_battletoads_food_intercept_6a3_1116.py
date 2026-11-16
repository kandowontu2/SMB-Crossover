"""Separate ground interception; standing-head and chase negative stay frozen."""
from functools import lru_cache
from pathlib import Path
import replay_battletoads_food_align_6a3_1116 as Previous

Current,R,ROM,PIN,W,N=Previous.Current,Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N
CONTROL=R/'tools/playthroughs/battletoads_food_intercept_6a3_1116.lua'

@lru_cache(maxsize=4)
def controller(raw,key='rash',kind='mushroom'):
    text=Previous.controller(raw,key,kind)
    first=text.index(" elseif food.phase=='mushroom-collect'then")
    last=text.index(" if food.phase=='flower-travel'then",first)
    text=text[:first]+CONTROL.read_text()+'\n'+text[last:]
    text=Previous.once(text,"local phase='approach';local clock=0;", "local phase='route';local clock=0;")
    Previous.Previous.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','saveState','loadState','takeScreenshot'))
    return text

def metadata(raw,key='rash',kind='mushroom'):
    q=Previous.metadata(raw,key,kind);q.update(controller_SHA256=Current.digest(controller(raw,key,kind).encode()),
        intercept_factory_SHA256=Current.digest(Path(__file__).read_bytes()),intercept_controls_SHA256=Current.digest(CONTROL.read_bytes()),
        retained_chase_negative='0c9e0d98d798c7f78203147312f1e9d3560a8b3923488260f570cee1c37df367')
    return q

def family(kind='mushroom'):
    from types import SimpleNamespace
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,key,kind),metadata=lambda raw,key:metadata(raw,key,kind))

"""Original airborne Up and one-cell head alignment for the authored Star."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_stock_head_91dc_1116 as Previous
import replay_excitebike_air_lean_91dc_1116 as Lean

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
HEAD_SHA='63fe0e36186e0714609cf4698a3d451c88a25eb1ad545db8cf134cb780887e01'
LEAN_SHA='aa6f42671d55647f2dd421b5825d26e8ab76b3860b0389da7674f71de0aeb0de'

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==HEAD_SHA and digest(Path(Lean.__file__).read_bytes())==LEAN_SHA
    text=Lean.air_lean(Previous.controller(raw,key))
    # Head point is actual playerX+8; the speed832 Star run crosses one full
    # native cell while ascending to row144. Preserve that visible cell by
    # starting the same prelean/A sequence one cell earlier.
    text=Previous.Previous.once(text,'if s.x>=C.target_x-29 and s.native==0','if s.x>=C.target_x-45 and s.native==0')
    Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),star_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_late_Star_negative='d5ea5e3d54f39264d72ff75f922b323a5ccfc0df94526ceb7742fc4be94d4c8f',
        source_control='Actual headX+8 and16pxcell alignment; original36Update airborneUp, no world or physics changes')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))

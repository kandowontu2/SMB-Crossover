"""Ordinary later takeoff for the wider second pit; no game changes."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_metal_native_caps_7c0f_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
KINDS={'star':Previous.KINDS['star']}
BASE_SHA='b801807675bd16beafcbc2e217839615fc77396ced9494e533e285b9df74ccc5'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star' and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    text=Previous.once(text,"if not q and c.x>=g[1]-64 and c.grounded and not lastA then","if not q and c.x>=g[1]-(stock.gap==2 and 32 or 64)and c.grounded and not lastA then")
    text=Previous.once(text,"assert(stepOK-q.since<220,'One ordinary pit crossing');local center=g[2]+24", """q.minimum_y=math.min(q.minimum_y or c.y,c.y);q.maximum_x=math.max(q.maximum_x or c.x,c.x)
   if not q.head_cells then q.head_cells={};for _,x in ipairs({g[1]-32,g[1]-16,g[1],g[2]})do q.head_cells[#q.head_cells+1]={x=x,row144=c.block(x,144),row160=c.block(x,160),floor=c.block(x,208)}end end
   assert(stepOK-q.since<220,'One ordinary pit crossing');local center=g[2]+24""")
    LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        scope='Actual7c0f earned M then Star; second48px pit takeoff32px before edge after prior64px-early flight ended inside pit',
        retained_negative='f88312fc: launch1313, terminal1406/243/engine11 beforefar1424; no Star birth',game_bytes_changed=0)
    return q


def family(kind='star'):
    assert kind=='star';return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))

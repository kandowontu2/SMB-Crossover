"""Ordinary alignment with measured native small head point +8."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_celeste_stock_00bb_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest,KINDS=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest,Previous.KINDS
BASE_SHA='1b77f95a6eb079c667098fc4b3332e9fbe52d233b58b3d50ebc59f0bd46960c2'
TEMPLATE_SHA='9b96123005a74795ac264e95746ca94a1a3e9448f6bfd7cae4c08893d9d2817e'


@lru_cache(maxsize=2)
def controller(raw,key='oneup'):
    assert digest(Path(Previous.__file__).read_bytes())==BASE_SHA and digest(Previous.TEMPLATE.read_bytes())==TEMPLATE_SHA
    text=Previous.controller(raw,key);old='local center=C.target_x-8';assert text.count(old)==1
    text=text.replace(old,'local center=C.target_x-6',1);LuaRuntime().compile(text);return text


def metadata(raw,key='oneup'):
    q=Previous.metadata(raw,key);q.update(factory_SHA256=digest(Path(__file__).read_bytes()),controller_SHA256=digest(controller(raw,key).encode()),
        scope='Actual00bb unchanged Celeste jump/physics; small head +8 aligned inside genuine S/L cell, same strict natural/credit/25 gates',
        retained_negative='b0dc98ae/7bfa580d: minY125/head143 reaches row128 but oldcenter parked1015 and actualhead1023/cell1008 returns0')
    return q


def family(kind='oneup'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))

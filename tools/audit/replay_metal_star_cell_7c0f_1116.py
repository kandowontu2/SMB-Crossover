"""Align the authentic left head point with the real Star cell1616."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_metal_star_gap_7c0f_1116 as Previous
from check_ff_stdout_controller_source_1110 import LuaRuntime

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='877542090bd71b7a564b7f90ab080f84c9b7cee92ece2aea58e7ba66c21e34a3'


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star' and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);old='local center=C.target_x-6';assert text.count(old)==1
    text=text.replace(old,'local center=C.target_x+4',1);LuaRuntime().compile(text);return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),factory_SHA256=digest(Path(__file__).read_bytes()),
        scope='Actual7c0f earned M then authentic Star cell1616; stop1620 so source left-head point reaches the Star instead of adjacent brick1600',
        retained_head_negative='dfff82a7: real AD54 hero1611/source1603/query1607 packet51, authored Star1616 tile87; no Star birth')
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))

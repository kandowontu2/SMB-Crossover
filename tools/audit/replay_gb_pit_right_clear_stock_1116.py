"""Separate native-calibration M/F policy; frozen prior controls stay exact."""
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace
import replay_gb_pit_mushroom_ground_1116 as M
import replay_gb_pit_flower_1116 as Flower

R,ROM,W,N,H,Current=M.R,M.ROM,M.W,M.N,M.H,M.Current
PINS={M:'39fc5b092fbf9da26da702f2c4351defac48aaec6f9c0790217f0d220299bd4c',
      Flower:'611fe3446205a34a2e043cc0084f5e83eb22006b228b44598094e2181247403b'}
OLD_CONTROL_SHA='adbc164c7a7ceab3aaa936aefda4dcf794e9bb5107a952707b8ea7dea88d3102'
CONTROL=R/'tools/playthroughs/gb_pit_mushroom_right_clear_controls_1116.lua'
NATIVE_NEGATIVE='1e6ed2d705a6d471c2c2aa8a53622f76415d28c2c5f482348a7c5436c8188f43'

def base(kind):assert kind in('mushroom','flower');return M if kind=='mushroom'else Flower

def bindings(raw,kind='mushroom'):return base(kind).bindings(raw)

@lru_cache(maxsize=2)
def controller(raw,kind='mushroom'):
    module=base(kind)
    for f,pin in PINS.items():assert H(Path(f.__file__).read_bytes())==pin
    assert H(M.CONTROL.read_bytes())==OLD_CONTROL_SHA
    text=module.controller(raw,kind);old=M.CONTROL.read_text();new=CONTROL.read_text();assert text.count(old)==1
    result=text.replace(old,new,1);assert result.count(new)==1 and result.replace(new,old,1)==text
    M.Previous.LuaRuntime().compile(result)
    assert not any(v in result for v in('emu.write','emu.setState','io.open','dofile','takeScreenshot','loadState','saveState'));return result

def metadata(raw,kind='mushroom'):
    q=base(kind).metadata(raw,kind);q.update(factory_SHA256=H(Path(__file__).read_bytes()),controller_SHA256=H(controller(raw,kind).encode()),
        control_SHA256=H(CONTROL.read_bytes()),frozen_prior_factories={Path(f.__file__).name:pin for f,pin in PINS.items()},
        frozen_prior_control_SHA256=OLD_CONTROL_SHA,input_fragment_only_change=True,all_item_head_growth_credit_and_return_assertions_exact=True,
        retained_native_M_control_negative=NATIVE_NEGATIVE,
        control_delta='Measure actual right row edge and supported clearcolumn, releaseA and remain there untilrealground, then approach authoredM frombelow; recordcamera/support. No engine/art/actor/helper changes.')
    return q

def family(kind='mushroom'):return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,kind),metadata=lambda raw,key:metadata(raw,kind))

"""Brake the measured Star intercept before its original long coast."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_star_park_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='083de6c32551b663d509fe99c551366b4b09b1a1fa1ed0834d0710637ae614f0'

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    old="""  buttons=s.x>C.target_x+64 and 66 or 0
  if buttons==0 then stock.park=stock.park or{state=state(),actor=a}end"""
    new="""  if not stock.brake then
   buttons=s.x>C.target_x+80 and 66 or 0
   if buttons==0 then stock.brake={state=state(),actor=a};stock.park=stock.brake end
  end"""
    assert text.count(old)==1;text=text.replace(old,new,1)
    Previous.Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),brake_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_long_coast_negative='de919b506c452864aee14c22a44a6229edc0e178fe9af4d880120c844ddf0c26',
        measured_brake='Prior left release1679/speed441 coasted to1650; release at native1696 face earlier, then one neutral intercept')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))

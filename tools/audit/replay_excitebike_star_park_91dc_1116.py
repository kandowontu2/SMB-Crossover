"""Preserve actual Star birth; ground-intercept before the real brick wall."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_star_lean_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='2353687ee89a03674657dc9dcf03cf83adcb88ea548b2e93b369b29f502c9eaf'

@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);a=text.index(' if a then\n  if a.state<128 then return end\n');b=text.index(" if stock.phase=='travel'then",a)
    text=text[:a]+""" if a then
  phase='stock-ground-intercept';stock.phase='collect'
  if a.state<128 then return end
  stock.intercept=stock.intercept or{request=state(),actor=a,since=mainReturns}
  assert(mainReturns-stock.intercept.since<750,'One bounded normal ground Star intercept')
  -- The reached parent controller stood1701, beyond the real1696 brick face.
  -- Return into the open1680 ground corridor; let actual native Star motion
  -- and original contact admit it, rather than repeatedly hopping away.
  buttons=s.x>C.target_x+64 and 66 or 0
  if buttons==0 then stock.park=stock.park or{state=state(),actor=a}end
  return
 end
"""+text[b:]
    Previous.Previous.Previous.Previous.LuaRuntime().compile(text);return text

def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),park_factory_SHA256=digest(Path(__file__).read_bytes()),
        retained_chase_negative='8f9c9a1b9037bc370c7b2948130d4e7c183b98b28d514d295dc0ecab00149df2',
        ordinary_intercept='Actual mature Star, original left throttle into open ground1680 then neutral; no synthetic actor/contact')
    return q

def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))

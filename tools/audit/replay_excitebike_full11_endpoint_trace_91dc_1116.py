"""Same-input bounded terminal for the unqualified full-route endpoint observer."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_full11_area2_91dc_1116 as Previous

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='9c8a6a6f286d464f6154f0e02aa855fadc30db503e60fc70d7fef7c0a331abd4'

@lru_cache(maxsize=1)
def controller(raw,key='excitebike'):
    assert digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key)
    marker=' local s=routeState()\n local grounded='
    observer=""" local s=routeState()
 route.debug_scenes=route.debug_scenes or{}
 local sk=table.concat({s.world,s.level,s.area,s.area_type,s.area_offset,s.engine},':')
 if sk~=route.debug_scene_key then
  route.debug_scene_key=sk
  if#route.debug_scenes<32 then route.debug_scenes[#route.debug_scenes+1]=s end
 end
 route.endpoint_gate={state=s,dm=dm,dv=dv,ready=ram2(0x800),flag=not not route.flag,castle=not not route.castle,
  entrance=not not route.entrance,underground_entrance=not not route.underground_entrance,
  active=active(),pendingMain=pendingMain~=nil,pendingMovement=pendingMovement~=nil,pendingMotor=pendingMotor~=nil,
  original_entries=movementEntries,original_returns=movementReturns,motor_entries=motorEntries,motor_returns=motorReturns}
 if mainReturns>=4500 then finish(false,'Same-input endpoint diagnostic at completedMain4500');return end
 local grounded="""
    text=Previous.Previous.once(text,marker,observer)
    Previous.Previous.Base.LuaRuntime().compile(text);return text

def metadata(raw,key='excitebike'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),diagnostic_factory_SHA256=digest(Path(__file__).read_bytes()),
        controls_identical=True,diagnostic_only=True,endpoint_not_relaxed=True)
    return q

def family():return SimpleNamespace(W=W,N=N,controller=controller,metadata=metadata)

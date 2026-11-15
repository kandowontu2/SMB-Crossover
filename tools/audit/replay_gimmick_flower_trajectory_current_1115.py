"""Passive bounded trajectory facade of frozen0a644 actual590 Flower controls."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_gimmick_flower_pollboard_current_1115 as Previous
import replay_smb1_alts_full11_1114 as Text

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize=Previous.Frozen,Previous.IDENTITIES,Previous.normalize
PARENT_SOURCE='3c7ecde80977f5d822ec7ddb88bdf3c89add505dda38f3df5748e8f881772ede'
PARENT_LUA='0a644fcb7ef09267d79e49b36b7fce3837b148ad18f6efa11db30921a4db32da'
once=Previous.Previous.Pipe.once


@lru_cache(maxsize=1)
def bindings(raw,key='mr_gimmick'):
    q=deepcopy(Previous.bindings(raw,key));b=dict(W.Symbols.bundle(),raw=raw)
    for name in('BoundingBox_UL_Corner','Player_X_Speed','Player_Y_Speed'):
        q['ram'][name]=W.address(b,name)
    return q


OBSERVER=r'''
local gmTrajectory={returns={},rides={},borrowed={}}
flower.trajectory_diagnostic=gmTrajectory
local function trajectoryState(kind)
 local q=gmTravel.snapshot();q.observation_kind=kind
 q.hero_x16=r('GmRam00AE')+256*r('GmRam00B8');q.hero_y16=r('GmRam009A')+256*r('GmRam00A4')
 q.star_vx=r('GmRam00CD');q.star_vy=r('GmRam00C3')
 q.star_x16=r('GmRam00AF')+256*r('GmRam00B9');q.star_y16=r('GmRam009B')+256*r('GmRam00A5')
 q.native_vx=r('Player_X_Speed');q.native_vy=r('Player_Y_Speed')
 q.native_box={};for i=0,3 do q.native_box[#q.native_box+1]=r('BoundingBox_UL_Corner',i)end
 return q
end
local function completedTrajectory()
 if not flower.boarding_takeoff then return end
 local vy=r('GmRam00C2')
 if not gmTrajectory.start and r('GmRam036E')==0 and vy>=196 and vy<216 then gmTrajectory.start=updates end
 if gmTrajectory.start and#gmTrajectory.returns<24 then
  gmTrajectory.returns[#gmTrajectory.returns+1]=trajectoryState('completed-Main-restored-after-control-decision')
 end
end
local trajectoryRide
hook('GmRideStar',function()
 if not flower.opposite_launch or#gmTrajectory.rides>=24 then return end
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 trajectoryRide={entry=trajectoryState('actual-GmRideStar-entry'),sp=(sp+2)&255,
  ret=emu.read(256+((sp+1)&255),emu.memType.nesDebug)+256*emu.read(256+((sp+2)&255),emu.memType.nesDebug)+1}
end)
hook('GmRideStarReturn',function()
 if not trajectoryRide then return end
 local q=trajectoryRide;trajectoryRide=nil;local cpu=emu.getState()
 assert(cpu['cpu.sp']==q.sp and cpu['cpu.pc']==q.ret,'Passive actual ride caller PC/SP')
 q.returned=trajectoryState('actual-GmRideStar-return');gmTrajectory.rides[#gmTrajectory.rides+1]=q
end)
hook('BoardStarReflectVX',function()
 if flower.opposite_launch and#gmTrajectory.borrowed<4 then
  gmTrajectory.borrowed[#gmTrajectory.borrowed+1]=trajectoryState('star-side-collision-borrowed-native-fields')
 end
end)
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    original=Previous.controller(raw,key);assert sha256(original.encode()).hexdigest()==PARENT_LUA
    prefix='local C='+Text.lua(Previous.bindings(raw,key))+'\n';assert original.startswith(prefix)
    body=original[len(prefix):]
    body=once(body,"hook('GmMovement',function()",OBSERVER+"hook('GmMovement',function()")
    line="  gmTravel.requested_bits=(gmInput.right and 1 or 0)|(gmInput.left and 2 or 0)|(gmInput.a and 128 or 0)|(gmInput.b and 64 or 0)\n"
    body=once(body,line,line+'  completedTrajectory()\n')
    # Removing only declared passive insertions must recover every original
    # control, callback, behavior assertion and endpoint byte exactly.
    recovered=once(body,OBSERVER,'');recovered=once(recovered,'  completedTrajectory()\n','')
    assert recovered==original[len(prefix):]
    result='local C='+Text.lua(bindings(raw,key))+'\n'+body
    Frozen.LuaRuntime().compile(result)
    assert not any(s in result for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        frozen_control_parent_source_SHA256=PARENT_SOURCE,frozen_control_parent_Lua_SHA256=PARENT_LUA,
        exact_parent_control_and_assertions_after_passive_insertion_removal=True,
        diagnostic_only=True,maximum_completed_return_rows=24,maximum_actual_ride_call_pairs=24,maximum_borrowed_rows=4,
        scope='Passive actual590 Flower route-negative diagnostic: exact0a644 controls and assertions, bounded restored Main/source/star/input/native-box trajectory and actual ride PC/SP pairs. No new gameplay or Flower qualification')
    return q

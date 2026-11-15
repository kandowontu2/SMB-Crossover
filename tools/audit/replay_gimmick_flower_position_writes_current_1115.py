"""Passive actual590 position-write facade; exactff47 controls/assertions."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import replay_gimmick_flower_trajectory_current_1115 as Previous

R,ROM,W,N,PIN=Previous.R,Previous.ROM,Previous.W,Previous.N,Previous.PIN
Frozen,IDENTITIES,normalize,bindings=Previous.Frozen,Previous.IDENTITIES,Previous.normalize,Previous.bindings
PARENT_SOURCE='1188ca4f33967412c1a817aa2d9dabc939cd60275e31a6841fa6822900aa6f12'
PARENT_LUA='ff47b6e21d5275af199b38f61d0975c8b581c3e5d2d5841e804d1958662c893b'

OBSERVER=r'''
local gmPositionWrites={rows={}}
flower.position_write_diagnostic=gmPositionWrites
local function positionWrite(kind,address,value)
 if not gmTrajectory.start or updates>gmTrajectory.start+8 or#gmPositionWrites.rows>=32 then return end
 local old=emu.read(address,emu.memType.nesDebug);if old==value then return end
 local d=math.abs(value-old);d=math.min(d,256-d)
 if kind=='native-X'and d<8 then return end
 local q=gmTravel.snapshot();local cpu=emu.getState();local pc=cpu['cpu.pc'];local sp=cpu['cpu.sp']
 q.write_kind=kind;q.address=address;q.old_value=old;q.new_value=value
 q.cpu_A=cpu['cpu.a'];q.cpu_X=cpu['cpu.x'];q.cpu_Y=cpu['cpu.y'];q.cpu_P=cpu['cpu.ps']or cpu['cpu.p']
 local map=emu.convertAddress(pc);if map then q.mapping={memType=map.memType,address=map.address}end
 q.nearby_PC_start=(pc-6)&65535;q.nearby_bytes={}
 for i=-6,3 do q.nearby_bytes[#q.nearby_bytes+1]=emu.read((pc+i)&65535,emu.memType.nesDebug)end
 q.stack={};for i=1,8 do q.stack[#q.stack+1]=emu.read(256+((sp+i)&255),emu.memType.nesDebug)end
 q.hero_x16=r('GmRam00AE')+256*r('GmRam00B8');q.hero_y16=r('GmRam009A')+256*r('GmRam00A4')
 q.star_x16=r('GmRam00AF')+256*r('GmRam00B9');q.star_y16=r('GmRam009B')+256*r('GmRam00A5')
 q.scratch={};for i=0,7 do q.scratch[#q.scratch+1]=emu.read(i,emu.memType.nesDebug)end
 gmPositionWrites.rows[#gmPositionWrites.rows+1]=q
end
emu.addMemoryCallback(guard(function(address,value)positionWrite('native-X',address,value)end),emu.callbackType.write,C.ram.Player_X_Position)
emu.addMemoryCallback(guard(function(address,value)positionWrite('source-hero-X-high',address,value)end),emu.callbackType.write,C.ram.GmRam00B8)
'''


@lru_cache(maxsize=1)
def controller(raw,key='mr_gimmick'):
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PARENT_SOURCE
    original=Previous.controller(raw,key);assert sha256(original.encode()).hexdigest()==PARENT_LUA
    text=Previous.once(original,"hook('GmMovement',function()",OBSERVER+"hook('GmMovement',function()")
    assert Previous.once(text,OBSERVER,'')==original
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return text


def metadata(raw,key='mr_gimmick'):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        passive_parent_factory_SHA256=PARENT_SOURCE,passive_parent_controller_SHA256=PARENT_LUA,
        exact_parent_after_passive_write_observer_removal=True,maximum_position_write_rows=32,
        native_write_observation_only=True,
        scope='Actual590 native-only passive first-position-write diagnostic, exactff47 controls/assertions; changed source hero X high and large native X writes in admitted jump window, CPU/map/bytes/SP/scratch. No new gameplay qualification')
    return q

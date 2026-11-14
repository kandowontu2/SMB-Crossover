"""Separate all-four CF controller using completed source ground snapshots."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import replay_contra_force_full11_v2_1114 as Previous

PIN,ROM,R,W,N=Previous.PIN,Previous.ROM,Previous.R,Previous.W,Previous.N
Frozen,POLICY,IDENTITIES=Previous.Frozen,Previous.POLICY,Previous.IDENTITIES
normalize,bindings=Previous.normalize,Previous.bindings
PREVIOUS_SOURCE='8330845efee9e4a7eb800e457f3c3c55a28590159d274b6d7d49b699500a08c4'
HOST_SOURCE='50b186659b04247ec14ed4aa1f3ba31464fafd9f813b2df8de04f5fe1da0c046'
LUA_SHA={'burns':'3d3c358cc5f2b8b85f89fe48f88cf93133b4b27f0b892f9a67217d23fd7db3fa',
    'smith':'fc182145cb64cc1ccc26d6b4fe3bed769d22131773e1c3590953548e0c7316e5',
    'iron':'1d90fde89b3752da52cf3d7d8e809382e961453e4c357e6770e4e71a6cf36082',
    'beans':'83b164a83934bded1575b330a15173ab92a0322e294eab4a15038250de03475d'}

SNAPSHOT=r'''
local function cfCompleted()
 if not first or not identity()or not active()then return end
 local function s(at)return emu.read(2*8192+at,emu.memType.nesWorkRam)end
 cfCompletedSource={Main=updates,worker=cfCalls,contact=s(0x4d2),input=s(0x4aa),jump_age=s(0x4b4),native_state=r('Player_State'),x=pos('Player_X_Position','Player_PageLoc'),y=r('Player_Y_Position')}
end
local function cfGrounded()
 local s=cfCompletedSource
 return s and s.Main==updates and s.worker==cfCalls and s.native_state==0 and r('Player_State')==0 and s.contact==1 and s.jump_age==0 and(s.input&64)==0
end
'''


@lru_cache(maxsize=4)
def controller(raw,key):
    assert key in IDENTITIES
    assert sha256(Path(Previous.__file__).read_bytes()).hexdigest()==PREVIOUS_SOURCE
    assert sha256((R/'tools/reference/contra_force_host_runtime_v8.s').read_bytes()).hexdigest()==HOST_SOURCE
    text=Previous.controller(raw,key)
    def once(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new,1)
    once("if stairPhase=='climb'and c.y<=112 then","if stairPhase=='climb'and c.grounded and c.y<=112 then")
    once('local cfDecisionUpdate,cfButtons=nil,{}','local cfDecisionUpdate,cfButtons=nil,{}\nlocal cfCompletedSource')
    once('local function cfOwner()',SNAPSHOT+'\nlocal function cfOwner()')
    once('\n cfOwner()\n','\n cfOwner()\n cfCompleted()\n')
    once('update=updates,heldA=lastA,','update=cfCalls,heldA=lastA,')
    once("grounded=r('Player_State')==0}","grounded=cfGrounded()}")
    once('if cfDecisionUpdate==updates then','if cfDecisionUpdate==cfCalls then')
    once('cfDecisionUpdate,cfButtons=updates,b','cfDecisionUpdate,cfButtons=cfCalls,b')
    once('CF_last_source=cfLastSource,','CF_last_source=cfLastSource,CF_completed_source=cfCompletedSource,')
    Frozen.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    assert sha256(text.encode()).hexdigest()==LUA_SHA[key]
    return text


def metadata(raw,key):
    q=Previous.metadata(raw,key)
    q.update(controller_SHA256=sha256(controller(raw,key).encode()).hexdigest(),
        previous_v2_Lua_SHA256=Previous.LUA_SHA[key],
        grounded='Completed Main: nativeState0 + original C4D2 contact1 + C4B4 age0 + C4AA airbit clear',
        source_movement_clock_for_policy_and_decisions=True,
        previous_gameplay_controls_identical=False,
        actual_ground_required_before_stair_landing_wait=True,
        original_source_host_runtime_v8_SHA256=HOST_SOURCE,
        source_physics_all_cookies_observers_and_success_conditions_unchanged=True)
    return q

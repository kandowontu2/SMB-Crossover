"""Frozen6c6 inputs plus bounded read-only original jump/query observations."""
from hashlib import sha256
import json

import compose_dkjr_direct_platform_1113 as T
from check_ff_stdout_controller_source_1110 import LuaRuntime

P=T.P
BASE_LUA='6c6aac8a3d0fdfe334beebcf62b4514014e45d9e044f43926b3ee38e261c8d73'
POINTS=((0xa0c1,'input','ad49c0'),(0xa210,'transition','ad6bc0'),
    (0xa734,'jump','ad10c2'),(0xaaa1,'gravity','8e0fc0'),
    (0xa39d,'kind2-before',None),(0xa3a0,'kind2-return','c900'),
    (0xa3b7,'accepted-query2','2069ae'),(0xae69,'source-head-service',None),
    (0xa321,'cancel-jump','8d6bc0'),(0xb06b,'terrain-ingress',None))


def controller(raw):
    assert sha256(raw).hexdigest()==T.PIN
    text=T.controller(raw,full=True,departure_enemy_guard=True,approach_enemy_guard=True)
    assert sha256(text.encode()).hexdigest()==BASE_LUA
    body=P.T.payload(raw)
    for pc,name,expected in POINTS:
        if expected is not None:
            value=bytes.fromhex(expected)
            assert body[pc-0xa000:pc-0xa000+len(value)]==value,(hex(pc),name)
    text=P.once(text,'local function finish(ok,why)',
        'local finalStairTrace,finalStairDropped={},0\nlocal function finish(ok,why)')
    text=P.once(text,'controller_only=true,script_RAM_writes=false,output_files=0,terminal=snapshot(),',
        'controller_only=true,script_RAM_writes=false,output_files=0,terminal=snapshot(),\n  final_stair_trace=finalStairTrace,final_stair_trace_dropped=finalStairDropped,')
    text+='''
local function finalStairObserve(name,at)
 if not active()or phase~='final-stairs'or x()<2938 or x()>2948 or not mapped(at,'nesWorkRam',3*8192+at-0xa000)then return end
 local cpu=emu.getState();local q=snapshot()
 q.event=name;q.PC=at;q.A=cpu['cpu.a'];q.X=cpu['cpu.x'];q.Y=cpu['cpu.y'];q.SP=cpu['cpu.sp']
 q.held=ram(2,0x14);q.fresh=ram(2,0x15);q.direction=ram(2,0x54);q.facing=ram(2,0x6d)
 q.prior=ram(2,0x6c);q.jump_age=ram(2,0x7e);q.source_y=ram(2,0x210);q.source_x=ram(2,0x213)
 q.jump_fraction=ram(2,0x7f);q.gravity_low=ram(2,0x82);q.gravity_high=ram(2,0x83)
 q.rect={};for off=0x3e,0x45 do q.rect[#q.rect+1]=ram(2,off)end
 q.query={};for off=0x8db,0x8ef do q.query[#q.query+1]=ram(2,off)end
 q.kind2_list={};for off=0,math.min(ram(2,0x8dd),16)-1 do q.kind2_list[#q.kind2_list+1]=ram(2,0x880+off)end
 q.native_box={read(0x658),read(0x659),read(0x65a),read(0x65b)}
 q.ordinary_bits=bits;q.hold_remaining=hold-updates;q.rearm_remaining=rearm-updates
 if #finalStairTrace>=64 then table.remove(finalStairTrace,17);finalStairDropped=finalStairDropped+1 end
 finalStairTrace[#finalStairTrace+1]=q
end
'''
    for pc,name,expected in POINTS:
        text+=f"emu.addMemoryCallback(guarded('final stair {name}',function()finalStairObserve('{name}',{pc})end),emu.callbackType.exec,{pc})\n"
    LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    _,raw=T.load_inputs();text=controller(raw)
    print('DKJR_FINAL_STAIR_TRACE_CONTROLLER '+json.dumps(dict(candidate_SHA256=T.PIN,
        controls_SHA256=BASE_LUA,trace_Lua_SHA256=sha256(text.encode()).hexdigest(),
        max_trace_rows=64,Lua_compiled=True,controller_choices_unchanged=True,
        state_or_ROM_writes=False,outputs_written=0),separators=(',',':')),flush=True)

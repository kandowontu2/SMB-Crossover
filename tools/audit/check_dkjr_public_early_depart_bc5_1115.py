"""Current binding/cold and pure-controller branch/return-token unit proof."""
from hashlib import sha256
import json
import replay_dkjr_public_early_depart_bc5_1115 as F
import check_dkjr_public_first_pipe_67_1115 as Cold
from check_ff_stdout_controller_source_1110 import LuaRuntime, MOCK

H = lambda value: sha256(value).hexdigest()

EXPOSE = '''function host.beginDepart(x,y,dx,id,dead,indexValue,rearmValue,ground)
 phase='depart';index=indexValue;playing=true;done=false;updates=1000;lastUpdate=-1
 hold=0;rearm=rearmValue;bits=0;events={}
 host.mem[0x75]=x&255;host.mem[0x5c]=x>>8;host.mem[0xbd]=y
 host.mem[0x1e]=ground and 0 or 2;host.mem[2*8192+0x6b]=ground and 1 or 4
 host.mem[2*8192+0x210]=y+15
 for i=0,5 do host.mem[0x10+i]=0 end
 host.mem[0x14]=1;host.mem[0x1b]=id;host.mem[0x23]=dead
 host.mem[0x7a]=(x+dx)&255;host.mem[0x61]=(x+dx)>>8;host.mem[0xc2]=184
end
function host.driveTest()drive()end
function host.departResult()
 local named=0;for _,q in ipairs(events)do if q.event=='third-depart-enemy-hop'then named=named+1 end end
 return bits,hold,rearm,named
end
function host.beginUnderground()
 phase='settle-underground-1-2';undergroundStart=updates;playing=true;done=false
 undergroundGrounded=0;undergroundReturned=0;undergroundPending=nil
end
function host.endpointCounts()return undergroundGrounded,undergroundReturned,undergroundPending~=nil end
'''

SETUP = '''host.env.SMB_STDOUT_ROM_SHA=ROM_PIN;host.env.SMB_TEST_VARIANT='0';host.env.SMB_DKJR_FAST_ROUTE='1'
local oldMap=emu.convertAddress
function emu.convertAddress(pc)
 if pc==0xd65e then return{memType=emu.memType.nesWorkRam,address=2*8192+0x165e}end
 return oldMap(pc)
end
host.mem[0x6002]=40;host.mem[0x771]=1;host.mem[0x773]=3;host.mem[0x0f]=8;host.mem[0x75f]=2
host.mem[2*8192+0x8fe]=2;host.mem[2*8192+0x6b]=1;host.mem[2*8192+0x6c]=1
host.mem[0xa4]=1
'''

BRANCH_TESTS = '''local cases={
 {160,8,6,0,3,0,true,true},{168,30,6,0,3,0,true,true},{176,30,6,0,3,0,true,true},
 {159,30,6,0,3,0,true,false},{177,30,6,0,3,0,true,false},
 {168,31,6,0,3,0,true,false},{168,7,6,0,3,0,true,false},
 {168,30,37,0,3,0,true,false},{168,30,6,32,3,0,true,false},
 {168,30,6,0,2,0,true,false},{168,30,6,0,3,1001,true,false},{168,30,6,0,3,0,false,false}}
for _,q in ipairs(cases)do
 host.beginDepart(783,q[1],q[2],q[3],q[4],q[5],q[6],q[7]);host.driveTest()
 local bits,hold,rearm,count=host.departResult()
 assert((count==1)==q[8]);assert((bits&128~=0)==q[8])
 if q[8]then assert(hold==1008 and rearm==1047 and bits&1==1)end
end
host.branchCases=#cases
'''

GROUND_SETUP = '''host.mem[0x764]=0;host.mem[0x761]=1;host.mem[0x753]=2
host.mem[0x75]=40;host.mem[0x5c]=0;host.mem[0xbd]=176;host.mem[0xa4]=1;host.mem[0x1e]=0
host.mem[2*8192+0x6b]=1;host.mem[2*8192+0x6c]=1;host.mem[2*8192+0x210]=191
host.beginUnderground()
function host.entry()host.stack(0x9afa,222);host.exec(0xd65e,222)end
function host.goodReturn()host.exec(0x9afa,224)end
function host.pair()host.entry();host.goodReturn()end
'''

ENDPOINT_TESTS = '''host.entry()
local g,n,p=host.endpointCounts();assert(g==0 and n==0 and p)
host.exec(0x9afb,224);g,n,p=host.endpointCounts();assert(g==0 and n==0 and p)
host.exec(0x9afa,225);g,n,p=host.endpointCounts();assert(g==0 and n==0 and p)
host.goodReturn();g,n,p=host.endpointCounts();assert(g==1 and n==1 and not p)
host.mem[0x1e]=2;host.pair();g,n,p=host.endpointCounts();assert(g==0 and n==2)
host.mem[0x1e]=0;host.mem[2*8192+0x6b]=4;host.pair();g,n,p=host.endpointCounts();assert(g==0 and n==3)
host.mem[2*8192+0x6b]=1
for i=1,24 do host.pair()end
g,n,p=host.endpointCounts();assert(g==24 and n==27 and not p and host.status==nil)
host.entry();g,n,p=host.endpointCounts();assert(g==24 and n==27 and p)
host.event(emu.eventType.endFrame);assert(host.status==nil)
host.goodReturn();g,n,p=host.endpointCounts();assert(g==25 and n==28 and not p)
host.entry();host.event(emu.eventType.endFrame);assert(host.status==nil)
g,n,p=host.endpointCounts();assert(g==25 and n==28 and p)
host.goodReturn();g,n,p=host.endpointCounts();assert(g==26 and n==29 and not p)
host.event(emu.eventType.endFrame);assert(host.status==0)
'''


def mock(text):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(MOCK)
    lua.globals().ROM_PIN = F.PIN
    lua.execute(SETUP)
    exposed = F.Ground.one(text, 'local function wait(pred)', EXPOSE+'local function wait(pred)')
    lua.execute(exposed)
    return lua


def main():
    raw = F.Early.Old.NIGHTLY.read_bytes()
    print('DKJR_BC5_REVIEW_PHASE strict-input', flush=True)
    reference, info = F.normalize(raw, kind=F.KIND)
    text = F.controller(raw, grounded12=True)
    plain = F.controller(raw, grounded12=False)
    rejected = 0
    for value, kind in ((raw, 'untyped'), (reference, F.KIND),
                        (raw[:-1]+bytes((raw[-1]^1,)), F.KIND)):
        try:
            F.normalize(value, kind=kind)
        except (ValueError, AssertionError):
            rejected += 1
        else:
            raise AssertionError('Strict bc5 facade accepted unknown input')
    assert rejected == 3
    print('DKJR_BC5_REVIEW_PHASE controller-units', flush=True)
    lua = mock(text)
    lua.execute(BRANCH_TESTS)
    branch_cases = lua.globals().host.branchCases
    lua = mock(text)
    lua.execute(GROUND_SETUP)
    lua.execute(ENDPOINT_TESTS)
    direct = mock(text)
    direct.execute(GROUND_SETUP)
    direct.execute('for i=1,25 do host.pair()end;host.event(emu.eventType.endFrame);assert(host.status==0)')
    for field in ('life', 'source5'):
        unit = mock(text)
        unit.execute(GROUND_SETUP)
        if field == 'life':unit.execute('host.mem[0x75f]=1')
        else:unit.execute('host.mem[2*8192+0x6b]=5')
        unit.execute('host.pair();assert(host.status==1)')
    print('DKJR_BC5_REVIEW_PHASE actual-current-cold', flush=True)
    opening, memory = Cold.first_active_cold(raw)
    assert memory.bundle['raw'] == raw and H(memory.bundle['raw']) == F.PIN
    _, payload = F.Early.Old.identity(reference)
    motor = payload[9*1024+0x65e:9*1024+0x6a7]
    assert len(motor) == 73 and motor[-4:] == bytes.fromhex('38601860')
    report = dict(passed=True, input=info, plain_Lua_SHA256=H(plain.encode()),
                  grounded12_Lua_SHA256=H(text.encode()), strict_rejections=rejected,
                  controller_only_branch_cases=branch_cases,
                  completed_return_counter_unit=dict(entries_alone_not_counted=True,
                      wrong_return_PC_SP_rejected=True, airborne_and_source4_reset=True,
                      twenty_four_not_complete=True, twenty_five_complete=True,
                      pending_next_motor_defers_finish=True,
                      actual_mock_returns=29, consecutive_grounded_mock_returns=26,
                      separate_direct25_case_completes_at25=True,
                      life_and_source5_rejected=True),
                  count_scope=dict(entry_PC=0xd65e, RAM_bank=2,
                      source_symbol='DkNativeMain', source_end=0xd6a7, bytes=73,
                      current_motor_SHA256=H(motor), host_Main_completion_claim=False),
                  actual_current_compiled_cold=opening,
                  source67_prefix_receipt='a930f209255e2ba68c3b17d83a07e20b3a63b70e5967cee6c3cbe9d44a9ab0d9',
                  source67_early_enemy_branch_unexercised=True,
                  current_full_route_source_or_native_claim=False,
                  unit_scope='Pure Lua controller mocks, not game-state fixtures or real game returns',
                  game_code_changed=False, output_files=0)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_BC5_EARLY_REVIEW '+encoded, flush=True)
    print('DKJR_BC5_EARLY_REVIEW_SHA256 '+H(encoded.encode()), flush=True)


if __name__ == '__main__':
    main()

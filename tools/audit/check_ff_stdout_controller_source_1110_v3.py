"""API-only qualification of sampled-input jump delivery; no ROM/gameplay."""
from hashlib import sha256
from pathlib import Path
import check_ff_stdout_controller_source_1110 as C
from lupa.lua54 import LuaRuntime

V1 = C.LUA
V2 = C.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v2.lua'
C.LUA = C.R / 'tools/playthroughs/ff_full_stage_stdout_1110_v3.lua'
BASE_RUNTIME = C.runtime

# Only mock tables change. No cartridge/CPU/PPU is executed by these tests.
MOCK_SOURCE_INPUT = r'''
host.mem[0xaacc]=0xa5;host.mem[0xaacd]=0xdc
host.mem[0xab6d]=0xa9;host.mem[0xab6e]=1
function host.main()
 host.event(1)
 host.stack(0x82be);host.exec(0x82d9)
 if host.mem[0x6002]==22 and host.mem[0xf]==8 then
  local pad=host.pad or{};local bits=(pad.a and 128 or 0)|(pad.b and 64 or 0)|
    (pad.right and 1 or 0)|(pad.left and 2 or 0)
  host.mem[0xdc]=bits;host.mem[0x558]=bits&192
  host.exec(0xaacc)
  host.mem[0x5c01]=(bits~(host.mem[0x5c00]or 0))&bits;host.mem[0x5c00]=bits
  if host.mem[0x5c01]&128~=0 and(host.mem[0x1e]or 0)==0 then
   host.exec(0xab6d)
   local x=(host.mem[0x75]or 0)+256*(host.mem[0x5c]or 0)
   host.mem[0x1e]=x==2225 and 0 or 1;host.mem[0x5c09]=1
  end
 end
 host.exec(0x82be,250)
end
'''


def runtime(*args, **kwargs):
    rt = BASE_RUNTIME(*args, **kwargs)
    rt.globals().host.mem[0x7eb8] = 1
    rt.execute(MOCK_SOURCE_INPUT)
    return rt


def jump_fixture():
    rt = LuaRuntime(unpack_returned_tuples=True)
    rt.execute(C.MOCK)
    rt.globals().host.env['SMB_TEST_VARIANT'] = '0'
    rt.globals().host.env['SMB_STDOUT_ROM_SHA'] = C.W.PIN
    # A test-only appended return exposes existing closures. The checked source
    # stays byte-exact and its production callback guards are not replaced.
    expose = '''
return{pad=setPad,sample=jumpSample,
 setup=function()gameplay=true;phase='flower';desiredJumpReason='flower-pipe-608'end,
 advance=function(n)updates=updates+n;completed=completed+n end,
 row=function()return jumpDiagnostics[#jumpDiagnostics]end,
 active=function()return activeJump end}
'''
    functions = rt.execute(C.LUA.read_text() + expose)
    rt.execute(MOCK_SOURCE_INPUT)
    m = rt.globals().host.mem
    m[0x6002], m[0xf], m[0x7eb8], m[0x1e] = 22, 8, 1, 0
    m[0x75], m[0x5c], m[0xbd] = 46, 2, 176
    functions.setup()
    return rt, functions


def jump_tests():
    rt, f = jump_fixture()
    f.pad(129)
    f.pad(1)  # A one-logical-update request followed by catch-up, no poll yet.
    rt.execute('host.event(1)')
    assert rt.globals().host.pad['a'], 'Catch-up must not erase an undelivered request'
    m = rt.globals().host.mem
    m[0xdc], m[0x5c01], m[0x5c00] = 129, 128, 129
    rt.execute('host.exec(0xaacc);host.exec(0xab6d)')
    assert f.row()['accepted'] and f.row()['status'] == 'hold'
    m[0x1e] = 1
    f.pad(1)
    assert f.row()['airborne']
    f.advance(22)
    f.pad(1)
    rt.execute('host.event(1)')
    assert rt.globals().host.pad['a']
    f.advance(1)
    f.pad(1)
    rt.execute('host.event(1)')
    assert not rt.globals().host.pad['a']
    assert f.row()['outcome'] == 'source-accepted-airborne-held23'
    held = f.row()['airborne_Main']
    assert f.row()['returned']['Main'] - held == 23
    old, g = jump_fixture()
    old.globals().host.mem[0xdc] = old.globals().host.mem[0x5c00] = 128
    g.pad(129)
    old.execute('host.event(1)')
    assert not old.globals().host.pad['a'], 'A held in the source must first release'
    old.globals().host.mem[0xdc] = old.globals().host.mem[0x5c00] = 0
    g.pad(1)
    old.execute('host.event(1)')
    assert old.globals().host.pad['a'] and g.row()['fresh_release']
    blocked, b = jump_fixture()
    b.pad(129)
    blocked.globals().host.mem[0x5c01] = 128
    blocked.execute('host.exec(0xab6d)')
    b.advance(4)
    b.pad(1)
    assert b.row()['outcome'] == 'source-accepted-but-no-completed-airborne'
    assert b.active() is None, 'Blocked acceptance must release before retry'
    timeout, t = jump_fixture()
    t.pad(129)
    t.advance(17)
    try:
        t.pad(1)
    except Exception as error:
        assert 'not accepted' in str(error)
    else:
        raise AssertionError('Missing source acceptance must fail within bound')


def main():
    assert sha256(V1.read_bytes()).hexdigest() == '1e11e26049e82ebe7db046dfc3a18a6e3e5927edb34985aabe325609bec68250'
    assert sha256(V2.read_bytes()).hexdigest() == '40f5f3e521d14a3facd80b95a2ba21466e375d5f5f3a140818ee74be2fc55a9e'
    one, two = V2.read_text(), C.LUA.read_text()
    start, end = "  if phase=='mushroom' then", "  elseif phase=='flower' then"
    assert one.split(start)[1].split(end)[0] == two.split(start)[1].split(end)[0]
    source = (C.R / 'src/final_fantasy_core.s').read_text()
    assert 'eor FfPrevious\n and SavedJoypadBits\n sta FfFresh' in source
    assert '; Source ground A cancels attack/preparation/cast; no release-height cut.' in source
    C.runtime = runtime
    C.main()
    jump_tests()
    print('{"jump_delivery_API_mocks":4,"ROM_or_native_gameplay":false,"outputs_written":0,"passed":true}')


if __name__ == '__main__':
    main()

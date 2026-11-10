"""Lua syntax/symbol/API-lifecycle mock only; no ROM/gameplay qualification.

Reuses one existing Lua5.4 binary read-only. Fixtures below change mock tables,
never an emulator or ROM. The production Lua has no memory-write/file APIs.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

R = Path(__file__).resolve().parents[2]
LUA = R / 'tools/playthroughs/ff_full_stage_stdout_1110.lua'
DEPS = R / 'build/smb2-final62-observer-lua-deps-v1'
DLL = DEPS / 'lupa/lua54.cp314-win_amd64.pyd'
DLL_SHA = '0b763f9765d059ebff66d11a2867176b263f7f6fbbb51cbdd876aa05f7f5c9b2'
sys.path[:0] = [str(DEPS), str(R / 'tools'), str(R / 'tools/audit')]
from lupa.lua54 import LuaRuntime
import check_ff_white_mushroom_current_1110 as W

MOCK = r'''
host={mem={},ppu={},callbacks={},events={},prints={},inputs={},status=nil,
 env={},cpu={['cpu.pc']=0,['cpu.sp']=248,['cpu.ps']=49,['cpu.x']=0},wrongMap=false}
function print(v)host.prints[#host.prints+1]=v end
os={getenv=function(k)return host.env[k]end}
emu={memType={nesDebug=1,nesPrgRom=2,nesWorkRam=3,nesPpuDebug=4},
 callbackType={exec=1,write=2},eventType={inputPolled=1,endFrame=2}}
function emu.read(a,t)if t==4 then return host.ppu[a]or 0 end;return host.mem[a]or 0 end
function emu.getState()return host.cpu end
function emu.convertAddress(pc)
 if host.wrongMap then return{address=0,memType=2}end
 if pc>=0xa000 and pc<0xc000 then return{address=3*8192+(pc&8191),memType=3}end
 return{address=(pc>=0xc000 and 127 or 126)*8192+(pc&8191),memType=2}
end
function emu.addMemoryCallback(fn,kind,first,last)
 host.callbacks[#host.callbacks+1]={fn=fn,kind=kind,first=first,last=last or first}
end
function emu.addEventCallback(fn,kind)
 host.events[kind]=host.events[kind]or{};table.insert(host.events[kind],fn)
end
function emu.setInput(pad,port)
 assert(port==0);host.pad=pad;host.inputs[#host.inputs+1]=pad
end
function emu.stop(status)host.status=status end
function emu.takeScreenshot()return '\137PNG\r\n\26\nMOCK' end
function host.event(kind)for _,fn in ipairs(host.events[kind]or{})do fn()end end
function host.exec(pc,sp)
 host.cpu['cpu.pc']=pc;host.cpu['cpu.sp']=sp or 248
 local n=#host.callbacks
 for i=1,n do local q=host.callbacks[i];if q.kind==1 and q.first<=pc and pc<=q.last then q.fn(pc)end end
end
function host.stack(ret,sp)
 sp=sp or 248;ret=ret-1
 host.mem[256+((sp+1)&255)]=ret&255;host.mem[256+((sp+2)&255)]=ret>>8
end
function host.main()
 host.stack(0x82be);host.exec(0x82d9);host.exec(0x82be,250)
end
function host.frame()host.event(1);host.event(2)end
host.mem[0x82d9]=0xa9;host.mem[0x82da]=0xff;host.mem[0x82db]=0x8d
'''


def runtime(variant=0, images=False, expected_stair=False):
    rt = LuaRuntime(unpack_returned_tuples=True)
    rt.execute(MOCK)
    rt.globals().host.env['SMB_TEST_VARIANT'] = str(variant)
    rt.globals().host.env['SMB_STDOUT_ROM_SHA'] = W.PIN
    rt.globals().host.env['SMB_STDOUT_IMAGES'] = '1' if images else '0'
    rt.globals().host.env['SMB_EXPECT_STAIR_STALL'] = '1' if expected_stair else '0'
    rt.execute(LUA.read_text())
    return rt


def result(rt):
    lines = list(rt.globals().host.prints.values())
    receipts = [json.loads(s.removeprefix('SMB_NATIVE_RECEIPT ')) for s in lines
                if s.startswith('SMB_NATIVE_RECEIPT ')]
    assert len(receipts) == 1, lines
    return receipts[0], lines


def startup(rt, variant):
    rt.execute('''
host.mem[0x6004]=1;host.mem[0x75f]=2;host.mem[0x300]=1
host.mem[0x754]=5;host.mem[0x53e]=1
host.menu='title';host.previous={};host.edges={}
function host.advance()
 host.event(1)
 local pad=host.pad or{}
 for _,name in ipairs({'start','select','down','right'})do
  if pad[name]and not host.previous[name]then
   host.edges[#host.edges+1]=name
   if name=='start'and host.menu=='title'then host.menu='roster';host.mem[0x7307]=2
   elseif name=='start'and host.menu=='roster'then
    host.menu='game';host.mem[0x7307]=0;host.mem[0x771]=1;host.mem[0x773]=3
    host.mem[0xf]=8;host.mem[0x75]=40;host.mem[0xbd]=176
   elseif host.menu=='roster'then
    if name=='down'then host.mem[0x7309]=(host.mem[0x7309]or 0)+8
    elseif name=='right'then host.mem[0x7309]=(host.mem[0x7309]or 0)+1
    elseif name=='select'then host.mem[0x5fef]=(host.mem[0x5fef]or 0)+1 end
    if host.mem[0x7309]==21 then host.mem[0x6002]=22 end
   end
  end
 end
 host.previous=pad;host.event(2)
end
''')
    for _ in range(300):
        rt.execute('host.advance()')
        if rt.globals().host.status is not None:
            raise AssertionError(result(rt))
        pad = rt.globals().host.pad
        if rt.globals().host.menu == 'game' and pad and pad['right']:
            break
    else:
        raise AssertionError('Mock natural-menu controller timeout')
    edges = list(rt.globals().host.edges.values())
    assert edges == [
        'start', 'down', 'down', 'right', 'right', 'right', 'right', 'right',
        *(['select'] * variant), 'start', 'right'], edges


def collect(rt, tier, variant):
    m = rt.globals().host.mem
    # Exercise the actual script's callback state machine with API-only tables.
    m[0x15], m[0x1c], m[0x24], m[0x39] = 1, 46, 128, tier - 1
    m[0x7b], m[0x62], m[0xc3] = (70 if tier == 1 else 224), (0 if tier == 1 else 4), 144
    if tier == 2:
        m[0x75], m[0x5c] = 216, 4
    rt.execute('host.main()')
    rt.execute('host.stack(0xe100);host.exec(0xbb60)')
    m[0x5fc5], m[0x5fc6] = tier, tier
    m[0x5fc7] = (1 if tier == 1 else 3) if variant == 1 else 0
    rt.execute('host.exec(0xbc1d)')
    m[0x15], m[0x112], m[0x104] = 0, 6, 32
    m[0xf], m[0x6bfd], m[0x6bfe], m[0x74a] = 9, 1, 0, 255
    rt.execute('host.cpu["cpu.ps"]=49;host.exec(0xe100,250)')
    for age in range(60):
        m[0x6bfe] = age
        rt.execute('host.stack(0xe101);host.exec(0xbc40)')
        m[0x6bfe] = age + 1
        if age == 59:
            m[0xf], m[0x6bfd], m[0x74a] = 8, 0, 0
        rt.execute('host.exec(0xe101,250);host.main()')
    palette = [0x16, 0x30, 0x36] if variant < 2 else [0x28, 0x18, 0x21]
    for at, value in enumerate(palette, 0x3f11):
        rt.globals().host.ppu[at] = value
    x = m[0x75] + 256 * (m[0x5c] or 0) + 16
    m[0x75], m[0x5c] = x & 255, x >> 8
    rt.execute('host.main()')


def success_case(variant, images=False, expected_stair=False):
    rt = runtime(variant, images, expected_stair)
    startup(rt, variant)
    collect(rt, 1, variant)
    collect(rt, 2, variant)
    m = rt.globals().host.mem
    m[0x10], m[0x17], m[0x1f], m[0x76], m[0x5d], m[0xbe] = 1, 6, 0, 0, 5, 184
    m[0x603f], m[0x6045], m[0x1e] = 75, 0, 0
    rt.execute('host.main();host.event(1)')
    assert rt.globals().host.pad['b'], ('Actual script did not commit attack', variant)
    m[0x5c15] = (150, 50, 150, 25)[variant]
    m[0x5c0f], m[0x5c03] = (0, 2) if variant == 2 else (255, 1)
    m[0x5c1c], m[0x5c26] = 1, 2
    rt.execute('host.cpu["cpu.x"]=0;host.stack(0xe102);host.exec(0xb7ae)')
    if variant in (0, 2):
        m[0x10], m[0x1f], m[0x603f] = 0, 32, 0
    else:
        m[0x603f] -= (150, 50, 150, 25)[variant]
    rt.execute('host.cpu["cpu.ps"]=49;host.exec(0xe102,250);host.main()')
    if expected_stair:
        m[0x75], m[0x5c], m[0xbd], m[0xf] = 177, 8, 128, 8
        rt.execute('for i=1,123 do host.main()end;host.event(2)')
        q, _ = result(rt)
        assert q['passed'] and q['expected_original_stair_stall']
        assert not q['full_1_1'] and 'active_1_2' not in q
        assert q['terminal']['x'] == 2225 and q['terminal']['engine'] == 8
        return dict(expected_stair=True, callback_only=True, native_gameplay=False)
    m[0x75], m[0x5c], m[0xbd], m[0xf] = 89, 12, 120, 4
    rt.execute('host.exec(0x8651);host.main()')
    m[0x761], m[0x75], m[0x5c], m[0xbd], m[0xf] = 1, 40, 0, 48, 8
    rt.execute('host.main();host.event(2)')
    q, lines = result(rt)
    assert q['passed'] and rt.globals().host.status == 0, q
    assert q['full_1_1'] and q['active_1_2']['engine'] == 8
    assert q['mushroom']['ticks'] == q['flower']['ticks'] == 60
    assert q['earned_attack']['before']['damage'] == (150, 50, 150, 25)[variant]
    assert len([s for s in lines if s.startswith('SMB_NATIVE_IMAGE ')]) == (2 if images else 0)
    before = len(lines)
    rt.execute('host.event(1);host.event(2);host.main()')
    assert len(rt.globals().host.prints) == before, 'Terminal callbacks must latch'
    return dict(variant=variant, callback_only=True, native_gameplay=False,
                pickup_ticks=[q['mushroom']['ticks'], q['flower']['ticks']], images=2 if images else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    assert args.output.resolve().is_relative_to(R / 'build') and not args.output.exists()
    assert sha256(DLL.read_bytes()).hexdigest() == DLL_SHA
    pins = {
        'check_ff_white_mushroom_current_1110.py': 'c6c3a7dca9cea3bf4577d5038f74a22261be8989edc1ad87ddd8590d0e581de0',
        'check_ff_all_mushrooms_current_1110.py': 'e122dc0dc793eeb7aa002389ea1112302f3cc008b19b77d38d75f695cdcc5f7e',
        'check_ff_flowers_current_1110.py': 'e990661e7b9fe754dede187b39dd0dfda6367f051cdd701b01ddc9b03aad50ec',
        'check_ff_earned_attacks_current_1110.py': 'dd8015682993e4a13190e9a9e200a1ae4b227767172b5ad6036831447110b44e',
        'check_ff_full_stage_current_1110.py': '4081ddb23a5e1c5dd5a59bfa87ae0058b108dc27f0b7fa2c1bb158ed98124439',
    }
    for name, digest in pins.items():
        assert sha256((R / 'tools/audit' / name).read_bytes()).hexdigest() == digest, name
    text = LUA.read_text()
    for forbidden in ('io.open', 'emu.write', 'emu.loadState', 'emu.saveState', 'emu.reset', 'dofile', 'require('):
        assert forbidden not in text, forbidden
    b = W.Symbols.bundle()
    table = text.split('local L = {', 1)[1].split('\n}', 1)[0]
    constants = dict((k, int(v, 0)) for k, v in re.findall(r'(\w+)\s*=\s*(0x[0-9a-f]+|\d+)', table))
    constants.update((k, int(v, 0)) for k, v in re.findall(r'L\.(\w+)\s*=\s*(0x[0-9a-f]+)', text))
    for name, value in constants.items():
        assert W.address(b, name) == value, (name, value, W.address(b, name))
    rows = [success_case(i, i == 0) for i in range(4)]
    stair = success_case(0, expected_stair=True)
    invalid = runtime(4)
    q, _ = result(invalid)
    assert not q['passed'] and invalid.globals().host.status == 1
    failure = runtime(0)
    startup(failure, 0)
    failure.globals().host.mem[0x7ffb] = 1
    failure.execute('host.main();host.frame();host.main()')
    q, lines = result(failure)
    assert not q['passed'] and 'Unexpected cheats' in q['reason'] and failure.globals().host.status == 1
    assert len([s for s in lines if s.startswith('SMB_NATIVE_RECEIPT ')]) == 1
    physical = runtime(0)
    startup(physical, 0)
    physical.execute('for i=1,12001 do host.event(2)end')
    q, _ = result(physical)
    assert not q['passed'] and 'Physical frame bound12000' in q['reason']
    logical = runtime(0)
    logical.execute('for i=1,6001 do host.main()end')
    q, _ = result(logical)
    assert not q['passed'] and 'Logical Main bound6000' in q['reason']
    print(json.dumps(dict(passed=True, outputs_written=0, ROM_written=False,
        Lua_SHA256=sha256(LUA.read_bytes()).hexdigest(), symbols=len(constants),
        Lua54_DLL_SHA256=DLL_SHA, API_only_mocks=rows,
        expected_stair_API_mock=stair,
        negatives=['invalid variant', 'callback assertion latched exactly once',
                   'physical frame bound12000', 'logical Main bound6000'],
        scope='Lua5.4 syntax/current symbol constants and mock API/menu/return lifecycle only; no ROM instructions, Mesen, PPU, game/controller correctness, physical cadence or native full-stage proof.'), sort_keys=True))
    assert not args.output.exists()


if __name__ == '__main__':
    main()

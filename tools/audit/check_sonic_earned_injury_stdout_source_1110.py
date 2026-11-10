"""Mock syntax and actual callback contracts of the Sonic injury controller."""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path
import re

import check_sonic_stdout_controller_source_1110 as Opening

Base = Opening.Base
ROOT = Base.R
LUA = ROOT / 'tools/playthroughs/sonic_earned_injury_stdout_1110.lua'
OLD = '47a7a6aeabe2cc7db593f431591e52331b834485b3d7638e3f10f95cbf43db4b'
NEW = '49295acff1d70349119b599882a2ec0b4e2f58d21f153c90b2228dc9aceee2a7'
OLD_COOKIE = 'a72b01c0f80210577f684adf9ea78ed5'
NEW_COOKIE = 'a72b0194a989064ae62ef75a04986523'


def runtime(pin):
    source = inspect.getsource(Opening.runtime)
    source = source.replace('Base.W.PIN', 'ROM_PIN')
    source = source.replace("bytes.fromhex('a72b0148fc67939017476de86f7ce64f')", 'COOKIE')
    namespace = dict(Opening.__dict__, LUA=LUA, ROM_PIN=pin,
                     COOKIE=bytes.fromhex(OLD_COOKIE if pin == OLD else NEW_COOKIE))
    exec(compile(source, '<Sonic injury Lua API fixture>', 'exec'), namespace)
    rt = namespace['runtime'](images=True)
    rt.execute('''
local previousMap=emu.convertAddress
function emu.convertAddress(pc)
 if pc==0xb299 then return{address=10*8192+(pc&8191),memType=2}end
 return previousMap(pc)
end
function host.write(at,v)
 for _,callback in ipairs(host.callbacks)do
  if callback.kind==2 and callback.first<=at and at<=callback.last then callback.fn(at,v)end
 end
 host.mem[at]=v
end
''')
    return rt


def run(pin):
    rt = runtime(pin)
    Opening.startup(rt)
    host = rt.globals().host
    mem = host.mem
    rt.execute('for i=1,100 do host.gameMain()end')
    assert host.status is None
    mem[5], mem[9], mem[10] = 112, 213, 3
    rt.execute('host.cpu["cpu.a"]=0xc1;host.exec(0x9ef5)')
    mem[0x15], mem[0x1c], mem[0x24], mem[0x39] = 1, 46, 1, 0
    mem[0x7b], mem[0x62], mem[0xc3] = 80, 1, 136
    rt.execute('host.gameMain()')
    mem[0x24] = 128
    rt.execute('host.gameMain()')
    rt.execute('host.cpu["cpu.x"]=5;host.stack(0xe100);host.exec(0x9b28)')
    mem[0x15], mem[0x112], mem[0x6bfd], mem[0x6bfe], mem[0x0f], mem[0x74a] = 0, 6, 1, 0, 9, 255
    rt.execute('host.write(0x104,0x20);host.exec(0xe100,250)')
    for age in range(60):
        mem[0x6bfe] = age
        rt.execute('host.stack(0xe101);host.exec(0xb299)')
        if age == 59:
            mem[0x6bfd], mem[0x6bfe], mem[0x0f], mem[0x74a], mem[0x75b] = 0, 60, 8, 0, 1
            rt.execute('host.exec(0xe101,250)')
        rt.execute('host.gameMain()')
    mem[0x10], mem[0x17], mem[0x1f], mem[0x76], mem[0x5d], mem[0xbe] = 1, 6, 0, 176, 2, 184
    rt.execute('host.cpu["cpu.x"]=0;host.exec(0x9771)')
    if pin == NEW:
        rt.execute('host.exec(0xd31b)')
    rt.execute(f'host.cpu["cpu.a"]={43 if pin == OLD else 0};host.cpu["cpu.ps"]=48;host.exec(0x97a4)')
    mem[0x75b], mem[0x0f], mem[0x74a] = (43 if pin == OLD else 0), 10, 255
    if pin == OLD:
        rt.execute('host.gameMain();host.event(2)')
    else:
        for timer in range(255, 200, -1):
            mem[0x74a] = timer
            rt.execute('host.gameMain()')
        mem[0x74a], mem[0x0f] = 0, 8
        rt.execute('host.gameMain()')
        x = mem[0x75] + 256 * (mem[0x5c] or 0) + 16
        mem[0x75], mem[0x5c] = x & 255, x >> 8
        host.work[0x4000 + 0x92] = 6
        rt.execute('host.gameMain();host.event(2)')
    receipt, lines = Base.result(rt)
    assert receipt['passed'] and host.status == 0, receipt
    assert receipt['transformation_ticks'] == 60 and receipt['collection']['sound_writes20'] == 1
    assert receipt['expected_old_negative'] == (pin == OLD)
    assert receipt['native_status_stores'] == [dict(a=43 if pin == OLD else 0, carry=0)]
    assert receipt['recovery_updates'] == (0 if pin == OLD else 55)
    before = len(lines)
    rt.execute('host.gameMain();host.event(2)')
    assert len(host.prints) == before
    return dict(pin=pin, old=pin == OLD, native_store=receipt['native_status_stores'][0],
                recovery_updates=receipt['recovery_updates'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(ROOT / 'build') and not args.output.exists()
    assert sha256(Base.DLL.read_bytes()).hexdigest() == Base.DLL_SHA
    text = LUA.read_text()
    for forbidden in ('io.open', 'emu.write', 'emu.saveState', 'emu.loadState', 'emu.reset', 'os.execute'):
        assert forbidden not in text
    constants = dict((k, int(v, 0)) for k, v in re.findall(
        r'(\w+)\s*=\s*(0x[0-9a-f]+)', text.split('local L={', 1)[1].split('\n}', 1)[0]))
    bundle = Base.W.Symbols.bundle()
    for name, value in constants.items():
        expected = 0x5ffe if name == 'FmAlts' else Base.W.address(bundle, name)
        assert value == expected, (name, value, expected)
    print(json.dumps(dict(passed=True, native_symbols=len(constants), outputs_written=0,
                          Lua_SHA256=sha256(LUA.read_bytes()).hexdigest(),
                          mock_paths=[run(OLD), run(NEW)], source_API_mock_only=True), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()

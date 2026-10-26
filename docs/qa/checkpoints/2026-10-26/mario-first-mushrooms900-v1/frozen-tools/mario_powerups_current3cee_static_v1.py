"""Load exact generated fixtures and compare old/static CHR return-slot mocks."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

from check_tmnt_render_oa import address, load, location
from parodius_visibility_hud_static_startup_v1 import MOCK

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def symbols(bundle, rom):
    labels = {}
    for s in rom.with_suffix('.lbl').read_text().splitlines():
        m = re.fullmatch(r'al ([0-9A-Fa-f]+) \.([\w]+)', s)
        if m:
            labels[m[2]] = int(m[1], 16)
    banks = {}
    for n, v in bundle['syms'].items():
        try:
            off = location(bundle, n)
            if off >= 16:
                banks[n] = (off - 16) // 8192
        except (KeyError, AssertionError, TypeError, ValueError):
            pass
    for n in ['NonMaskableInterrupt', 'IrqScrollSplit']:
        labels[n + '_RTI'] = address(bundle, n) + int(bundle['syms'][n]['size'], 0) - 1
    return labels, banks


def runtime(LuaRuntime, labels, banks):
    rt = LuaRuntime(unpack_returned_tuples=True)
    rt.execute(MOCK + "\nL={};B={};OUTPUT='synthetic/';emu.memType.nesPrgRom=5")
    for n, v in labels.items():
        rt.globals().L[n] = v
    for n, v in banks.items():
        rt.globals().B[n] = v
    rt.execute("""
texts={};mem={};inputCalls=0
emu.setInput=function()inputCalls=inputCalls+1 end
emu.read=function(a)return mem[a]or 0 end
emu.write=function()error('Fixture game writes forbidden')end
io.open=function(path,mode)
 if mode=='rb'then return nil end
 texts[path]={}
 return{write=function(self,...)for i=1,select('#',...)do texts[path][#texts[path]+1]=tostring(select(i,...))end;return self end,flush=function()end,close=function()end}
end
function dispatch(kind,at,v)
 for _,q in ipairs(callbacks)do if q.kind==kind and at>=q.lo and at<=q.hi then q.fn(at,v)end end
end
""")
    return rt


def chr_equivalence(LuaRuntime, original, successor, labels, banks, character):
    outputs = []
    for static, text in [(False, original), (True, successor)]:
        body = text.rsplit('local observeChr=(function()\n', 1)[1].split('\nend)()\nreturn function(cfg)', 1)[0]
        rt = runtime(LuaRuntime, labels, banks)
        rt.globals().target = character
        rt.execute('local f=(function()\n' + body + "\nend)();local a=f({character=target,out='synthetic/'})")
        if static:
            rt.execute('assert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()')
        count = rt.eval('#callbacks')
        if static:
            rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
        rt.execute("""
mapBank=B.DrawMetasprite
emu.convertAddress=function(a)return{address=mapBank*8192+(a%8192)}end
mem[L.SelectedCharacter]=target;mem[L.OperMode]=1;mem[L.GameEngineSubroutine]=8
for i=0,7 do mem[L.X5ChrMode+i]=128;mem[L.CurrentCHRBank+i]=0 end
state['cpu.y']=0;state['cpu.sp']=250
mem[507]=255;mem[508]=90 -- genuine RTS return5B00, SP252
-- A wrong physical owner cannot open the render span.
mapBank=B.DrawMetasprite+1;dispatch(emu.callbackType.exec,L.DrawMetasprite)
mapBank=B.DrawMetasprite
dispatch(emu.callbackType.exec,L.DrawAllMetasprites)
dispatch(emu.callbackType.exec,L.DrawMetasprite)
dispatch(emu.callbackType.exec,L.MetaspriteRenderLoop)
for i,v in ipairs({80,2,0,80})do mem[511+i]=v;dispatch(emu.callbackType.write,511+i,v)end
-- Wrong stack and unrelated return PC must not finish the pending span.
state['cpu.sp']=251;dispatch(emu.callbackType.exec,23296)
state['cpu.sp']=252;dispatch(emu.callbackType.exec,23297)
dispatch(emu.callbackType.write,16404,2);runevents(emu.eventType.endFrame)
beforeReturn=#texts['synthetic/chr-commit.csv']
dispatch(emu.callbackType.exec,23296)
dispatch(emu.callbackType.write,16404,2);runevents(emu.eventType.endFrame)
afterReturn=#texts['synthetic/chr-commit.csv']
""")
        assert rt.eval('beforeReturn') == 1
        assert rt.eval('afterReturn') == 2
        if static:
            assert rt.eval('#callbacks') == count
        else:
            assert rt.eval('#callbacks') == count + 1
        outputs.append(rt.eval("table.concat(texts['synthetic/chr-commit.csv'])"))
    assert outputs[0] == outputs[1], 'Old/static CHR observation differs'
    return dict(passed=True, old_and_new_observation_byteexact=True,
                wrong_physical_owner_wrong_stack_unrelated_PC_retained=True,
                original_runtime_callback_growth=1, successor_runtime_callback_growth=0,
                synthetic_output_sha256=hashlib.sha256(outputs[0].encode()).hexdigest())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--lua-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(a.lua_root))
    from lupa.lua54 import LuaRuntime
    bundle = load(a.rom)
    labels, banks = symbols(bundle, a.rom)
    cfg = json.loads((a.fixture / 'configuration.json').read_text())
    labels.update(cfg['item']['ram'])
    rt = runtime(LuaRuntime, labels, banks)
    script = (a.fixture / 'run.lua').read_text()
    rt.execute(script)
    count = rt.eval('#callbacks')
    rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
    for frame in range(1, 440):
        rt.execute("state['ppu.frameCount']=" + str(frame) +
                   ";runevents(emu.eventType.inputPolled);runevents(emu.eventType.endFrame)")
    assert rt.eval('#callbacks') == count
    assert rt.eval('inputCalls') == 439
    original = D / 'current3cee-remaining27-routes-v1/native' / a.fixture.name / 'audit.lua'
    comparison = chr_equivalence(LuaRuntime, original.read_text(),
                                 (a.fixture / 'audit.lua').read_text(), labels, banks,
                                 cfg['roster']['character'])
    result = dict(passed=True, native_executed=False, ROM_sha256=sha(a.rom),
                  script_sha256=sha(a.fixture / 'run.lua'), tool_sha256=sha(__file__),
                  actual_generated_fixture_loaded=True, mock_inactive_frames=439,
                  actual_controller_polls=439, startup_memory_callbacks=count,
                  runtime_registration_removal_and_emulated_writes=0,
                  CHR_static_slot_equivalence=comparison,
                  Lua_runtime=rt.eval('_VERSION'),
                  scope='Exact generated fixture/startup and finite old/static CHR-return mocks only. Synthetic API/RAM/bank events, no actual6502/controller/PPU/DMA or gameplay result. Active item assertions remain native-unrun.')
    (a.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

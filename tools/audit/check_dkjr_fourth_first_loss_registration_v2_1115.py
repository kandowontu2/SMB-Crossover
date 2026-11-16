"""Execute callback registration and observer-only mocks; no game execution."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import replay_dkjr_fourth_first_loss_bc5_v2_1115 as F

H = lambda value: sha256(value).hexdigest()

MOCK = r'''
guarded=nil
host={mem={},rom={},callbacks={},events={},prints={},cpu={
 ['cpu.pc']=0,['cpu.sp']=220,['cpu.ps']=49,['cpu.a']=0,['cpu.x']=0,['cpu.y']=0},
 env={SMB_STDOUT_ROM_SHA=ROM_PIN,SMB_TEST_VARIANT='0',SMB_DKJR_FAST_ROUTE='1'}}
os={getenv=function(k)return host.env[k]end}
emu={memType={nesDebug=1,nesPrgRom=2,nesWorkRam=3},
 callbackType={exec=1,write=2},eventType={inputPolled=1,endFrame=2}}
function print(line)host.prints[#host.prints+1]=line end
function emu.read(at,kind)
 if kind==emu.memType.nesPrgRom then return host.rom[at]or 0 end
 return host.mem[at]or 0
end
function emu.getState()return host.cpu end
function emu.convertAddress(pc)
 if pc>=0xa000 and pc<0xc000 then return{memType=3,address=3*8192+(pc&8191)}end
 if pc==0xd65e then return{memType=3,address=2*8192+(pc&8191)}end
 return nil
end
local function label(fn)
 assert(type(fn)=='function','Only functions may be registered')
 for i=1,20 do local name,value=debug.getupvalue(fn,i)
  if name==nil then break end
  if name=='name'then return value end
 end
 error('Callback lacks guarded closure label')
end
function emu.addMemoryCallback(fn,kind,first,last)
 host.callbacks[#host.callbacks+1]={fn=fn,kind=kind,first=first,last=last or first,label=label(fn)}
end
function emu.addEventCallback(fn,kind)
 assert(host.events[kind]==nil,'Duplicate event callback')
 host.events[kind]={fn=fn,label=label(fn)}
end
function emu.setInput(pad,port)assert(port==0);host.pad=pad end
function emu.stop(status)host.status=status end
function host.exec(pc,sp,a)
 host.cpu['cpu.pc']=pc;host.cpu['cpu.sp']=sp or 220;host.cpu['cpu.a']=a or 0
 local n=#host.callbacks
 for i=1,n do local q=host.callbacks[i]
  if q.kind==emu.callbackType.exec and pc>=q.first and pc<=q.last then q.fn(pc)end
 end
end
function host.stack(ret,sp)
 ret=ret-1;host.mem[0x100+((sp+1)&255)]=ret&255
 host.mem[0x100+((sp+2)&255)]=ret>>8
end
'''

EXPOSE = '''
function host.armObserver()
 playing=true;index=4;flSlot=3;flFirst.first_carry={mock_only=true}
 host.mem[0x75]=160;host.mem[0x5c]=3
 host.mem[2*8192+0x8f0]=3;host.mem[2*8192+0x8db]=3
end
function host.observerPair(kind)return flFirst[kind]end
'''


def runtime(raw):
    lua = F.V1.LuaRuntime(unpack_returned_tuples=True)
    lua.globals().ROM_PIN = F.PIN
    lua.execute(MOCK)
    # Only the actual owning cookie is needed by top-level/coroutine readiness.
    for at in range(534485-16, 534500-16+1):
        lua.globals().host.rom[at] = raw[at+16]
    return lua


def labels(lua):
    return Counter(row['label'] for row in lua.globals().host.callbacks.values())


def run(raw, old_text):
    fixed, descriptor = F.from_probe_text(old_text, raw)
    failed = runtime(raw)
    try:
        failed.execute(old_text)
    except Exception as error:
        why = str(error)
        assert "global 'guarded'" in why and 'nil value' in why, why
    else:
        raise AssertionError('Frozen old probe no longer reproduces lexical startup failure')
    assert len(failed.globals().host.callbacks) == 3
    assert len(failed.globals().host.events) == 0
    assert failed.globals().guarded is None

    lua = runtime(raw)
    lua.execute(fixed)
    host = lua.globals().host
    config, _ = F.V1.bindings(raw)
    expected = Counter({'grounded1-2 motor entry': 1,
        'first-loss actual944position': 1, 'first-loss nextD65Eentry': 1,
        'first-loss support entry': 1, 'first-loss wall entry': 1,
        'first-loss plane entry': 1,
        'first-loss source4writer': len(config['state_writers']),
        'first-loss originwriter': len(config['origin_writers']),
        'first-loss nativeXwrite': 1, 'main': 1, 'birth': 1,
        'gap constructor': 1, 'gap constructor return': 1, 'gap top ingress': 1,
        'gap top reject': 3, 'gap top append': 1,
        'original gap landing': 1, 'carry': 1, 'injury': 1})
    assert labels(lua) == expected, (labels(lua), expected)
    assert len(host.events) == 2
    assert host.events[1]['label'] == 'input' and host.events[2]['label'] == 'frame'
    assert lua.globals().guarded is None, 'Production must bind local guarded, not patch its global'
    assert host.status is None and len(host.prints) == 0
    registered = len(host.callbacks)

    # Execute every static closure while the mocked game is inactive, plus both
    # event handlers. This is an API/lexical test; no ROM CPU or gameplay state.
    for row in list(host.callbacks.values()):
        if row['kind'] == 1:
            lua.execute(f'host.exec({row["first"]},220,0)')
        else:
            row['fn'](row['first'], 0)
    host.events[1]['fn']()
    host.events[2]['fn']()
    assert host.status is None and len(host.prints) == 0 and len(host.callbacks) == registered
    assert host.pad is not None

    # The same locally bound guard also wraps actual dynamic return callback
    # registration. Explicit observer-only mock locals do not assert gameplay.
    pair = runtime(raw)
    pair.execute(fixed+EXPOSE)
    pair.execute('host.armObserver()')
    for name in ('support', 'wall', 'plane'):
        pc = {'support': 0xb065, 'wall': 0xb061, 'plane': 0xb5c8}[name]
        for i, value in enumerate(config[name]):
            pair.globals().host.mem[pc+i] = value
        pair.execute(f'host.stack(0x9afa,220);host.exec({pc},220,139)')
        q = pair.globals().host.observerPair(name)
        assert q is not None and q['returned'] is None
        pair.execute('host.exec(0x9afb,222);host.exec(0x9afa,223)')
        assert q['returned'] is None
        pair.execute('host.exec(0x9afa,222,1)')
        assert q['returned']['pc'] == 0x9afa and q['returned']['sp'] == 222
        before = len(pair.globals().host.callbacks)
        pair.execute(f'host.exec({pc},220,139)')
        assert len(pair.globals().host.callbacks) == before
    assert pair.globals().host.status is None and len(pair.globals().host.prints) == 0

    report = dict(passed=True, ROM_SHA256=F.PIN, old_Lua_SHA256=F.V1_LUA_SHA,
        Lua_SHA256=H(fixed.encode()), base_Lua_SHA256=F.V1.BASE,
        old_startup_negative=dict(error="attempt to call a nil value (global 'guarded')",
            static_callbacks_before_abort=3, event_callbacks_before_abort=0,
            native_runs=['21077 no receipt', '65429 no receipt'], gameplay_claim=False),
        executed_top_level_registration=dict(global_guarded_nil=True,
            static_memory_callbacks=registered, labels=dict(sorted(expected.items())),
            input_event=True, endFrame_event=True, all_inactive_closures_and_events_executed=True),
        dynamic_return_mock=dict(kinds=['support', 'wall', 'plane'], wrong_PC_SP_rejected=True,
            matching_returns=3, duplicate_hooks_rejected=True),
        static_binding_preimages=descriptor, exact_v1_and_ed3e_restoration=True,
        maximum_specific_witnesses=8, controls_changed=False, game_writes=False,
        scope='Executed Lua API/lexical mock only; no game CPU/native calibration',
        output_files=0, PNGs=0)
    encoded = json.dumps(report, sort_keys=True, separators=(',', ':'))
    print('DKJR_FOURTH_REGISTRATION_V2 '+encoded, flush=True)
    print('DKJR_FOURTH_REGISTRATION_V2_SHA256 '+H(encoded.encode()), flush=True)
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from-probe', type=Path)
    args = ap.parse_args()
    raw = F.V1.F.Prior.Early.Old.NIGHTLY.read_bytes()
    old_text = (args.from_probe.read_bytes().decode() if args.from_probe
                else F.V1.controller(raw)[0])
    run(raw, old_text)

"""Read-only exact-input replay for the observed low-body Mega Man frames."""
from pathlib import Path
import csv
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/audit'))
from check_tmnt_render_oa import load, address

D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = D / 'root-megaman-lowbody-probe-v1'
ROM = D / 'root-chip-hud-composed-v1/candidate.nes'
ROUTE = D / 'current3cee-eight-routes-v1/native/megaman-easy'
REFERENCE = D / 'current3cee-eight-routes-v1/native/megaman-easy-direct'
CAPTURE = D / 'current3cee-eight-routes-v1/capture.py'
EXPECTED = '3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda: f.read(1048576), b''):
            h.update(data)
    return h.hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    assert sha(ROM) == EXPECTED
    names = ['MmRenderPose', 'MmSliding', 'MmWalkFrame', 'MmStepTimer',
             'GuestHurtTicks', 'GuestInvulTicks', 'GuestHurtVisible', 'InjuryTimer',
             'PlayerFacingDir', 'Player_Rel_XPos', 'Player_Y_Position',
             'Player_Y_HighPos', 'PlayerStatus', 'PlayerOutlinesOff',
             'ObjectMetasprite', 'FrameCounter', 'GuestPowerupActive']
    bundle = load(ROM)
    bindings = {n: address(bundle, n) for n in names}
    lua_names = '{' + ','.join(json.dumps(n) for n in names) + '}'
    lua_addresses = '{' + ','.join(str(bindings[n]) for n in names) + '}'
    observer = r'''
local names=__NAMES__
local addresses=__ADDRESSES__
local out=__OUT__
local stateFile=assert(io.open(out..'visibility.csv','w'))
local ctrl,mask,lastDmaCycle=0,0,-1
local function hex(at,count,kind)
 local t={};for i=0,count-1 do t[#t+1]=string.format('%02x',emu.read(at+i,kind))end
 return table.concat(t)
end
local function ram()
 local t={};for _,at in ipairs(addresses)do t[#t+1]=emu.read(at,emu.memType.nesDebug)end
 return table.concat(t,':')
end
local lastDmaRam=''
emu.addMemoryCallback(function(a,v)ctrl=v end,emu.callbackType.write,0x2000)
emu.addMemoryCallback(function(a,v)mask=v end,emu.callbackType.write,0x2001)
emu.addMemoryCallback(function()
 lastDmaCycle=emu.getState()['cpu.cycleCount'];lastDmaRam=ram()
end,emu.callbackType.write,0x4014)
stateFile:write('ppuFrame,cpuCycle,ctrl,mask,lastDmaCycle,ram,lastDmaRam,chrBanks,hardwareOam,palette\n')
emu.addEventCallback(function()
 local s=emu.getState();local frame=s['ppu.frameCount']
 if frame<500 or frame>3000 then return end
 local banks={};for i=0,11 do banks[#banks+1]=assert(s['mapper.chrBanks'..i])end
 stateFile:write(table.concat({frame,s['cpu.cycleCount'],ctrl,mask,lastDmaCycle,ram(),lastDmaRam,
  table.concat(banks,':'),hex(0,256,emu.memType.nesSpriteRam),hex(0,32,emu.memType.nesPaletteRam)},',')..'\n')
 stateFile:flush()
end,emu.eventType.endFrame)
local oldStop=emu.stop
emu.stop=function(code)stateFile:close();oldStop(code)end
'''.replace('__NAMES__', lua_names).replace('__ADDRESSES__', lua_addresses).replace('__OUT__', json.dumps((OUT / 'native').as_posix() + '/'))
    spec = importlib.util.spec_from_file_location('frozen_visibility_capture', CAPTURE)
    capture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(capture)
    original_observer = capture.OBSERVER
    capture.OBSERVER = observer + original_observer
    (OUT / 'added-read-only-observer.lua').write_text(observer)
    inherited = json.loads((D / 'current3cee-eight-routes-v1/readiness.json').read_text())['bindings']
    inherited.update({str(Path(__file__).resolve()): sha(__file__), str(OUT / 'added-read-only-observer.lua'): sha(OUT / 'added-read-only-observer.lua'), str(REFERENCE / 'proof.json'): sha(REFERENCE / 'proof.json')})
    assert all(Path(p).is_file() and sha(p) == h for p, h in inherited.items())
    readiness = dict(ROM_sha256=EXPECTED, names=names, RAM_bindings=bindings, bindings=inherited,
                     original_capture_observer_sha256=hashlib.sha256(original_observer.encode()).hexdigest(),
                     read_only_extra_callbacks=True, game_writes=False, native_workers=1,
                     scope='Bounded second worker; original fixed inputs, all guards and full original direct capture retained. Additional RAM/hardware reads only.')
    (OUT / 'readiness.json').write_text(json.dumps(readiness, indent=2) + '\n')
    sys.argv = [str(CAPTURE), '--rom', str(ROM), '--route', str(ROUTE), '--output', str(OUT / 'native')]
    capture.main()
    native = OUT / 'native'
    for name in ['inputs.csv', 'trace.csv', 'render.csv', 'oam.csv', 'chr.csv',
                 'scroll-writes.csv', 'audio-events.csv', 'stomp-events.csv',
                 'completed-loop-motion.csv', 'chr-commit.csv']:
        assert (native / name).read_bytes() == (REFERENCE / name).read_bytes(), name
    current = json.loads((native / 'proof.json').read_text())
    reference = json.loads((REFERENCE / 'proof.json').read_text())
    assert current['passed'] and current['raw_stream_sha256'] == reference['raw_stream_sha256']
    assert (native / 'direct-frame-index.csv').read_bytes() == (REFERENCE / 'direct-frame-index.csv').read_bytes()
    with (native / 'visibility.csv').open() as f:
        rows = list(csv.DictReader(f))
    assert [int(r['ppuFrame']) for r in rows] == list(range(500, 3001))
    assert all(Path(p).is_file() and sha(p) == h for p, h in inherited.items())
    proof = dict(passed=True, ROM_sha256=EXPECTED, read_only_instrumentation=True,
                 full_original_direct_stream_and_all_frame_pixels_byte_exact=True,
                 original_named_gameplay_logs_byte_exact=True, logged_frames=len(rows),
                 readiness_sha256=sha(OUT / 'readiness.json'), visibility_sha256=sha(native / 'visibility.csv'),
                 worker_released=True, scope='Attribution data only. Does not itself diagnose or fix body visibility.')
    (OUT / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2), flush=True)


if __name__ == '__main__':
    main()

"""Read completed native updates in an unchanged retained failed route prefix."""
from pathlib import Path
import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import sys
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OBSERVER = r'''
local frame=0
local f=assert(io.open(FAILED_OBS_OUT..'completed.csv','w'))
f:write('frame,cycle,'..table.concat(FAILED_OBS_FIELDS,',')..'\n')
local function r(name)return emu.read(assert(L[name],name),emu.memType.nesDebug)end
local function bank(a)return emu.convertAddress(a).address//8192 end
local pending,callbacks=nil,{}
emu.addMemoryCallback(function()
 if bank(L.GameLoop)~=B.GameLoop then return end
 local state=emu.getState();local sp=state['cpu.sp']
 local target=(emu.read(0x100+(sp+1)%256,emu.memType.nesDebug)+256*emu.read(0x100+(sp+2)%256,emu.memType.nesDebug)+1)%65536
 pending={pc=target,sp=(sp+2)%256}
 if not callbacks[target]then
  callbacks[target]=true
  emu.addMemoryCallback(function()
   local state=emu.getState()
   if not pending or pending.pc~=target or pending.sp~=state['cpu.sp']then return end
   pending=nil
   if frame<FAILED_OBS_BEGIN or frame>FAILED_OBS_END then return end
   local row={frame,state['cpu.cycleCount']}
   for _,name in ipairs(FAILED_OBS_FIELDS)do row[#row+1]=r(name)end
   f:write(table.concat(row,',')..'\n');f:flush()
  end,emu.callbackType.exec,target)
 end
end,emu.callbackType.exec,L.GameLoop)
emu.addEventCallback(function()
 frame=frame+1
 if frame==FAILED_OBS_END then
  local state=emu.getState();assert(state['ppu.frameCount']==frame)
  local buffer=emu.getScreenBuffer();assert(#buffer==256*240)
  local chunks={}
  for i=1,#buffer,8 do chunks[#chunks+1]=string.pack('<I4I4I4I4I4I4I4I4',buffer[i],buffer[i+1],buffer[i+2],buffer[i+3],buffer[i+4],buffer[i+5],buffer[i+6],buffer[i+7])end
  local raw=assert(io.open(FAILED_OBS_OUT..'endpoint.argb','wb'));raw:write(table.concat(chunks));raw:close()
 end
 if frame>=FAILED_OBS_END+1 then f:close();emu.stop(0)end
end,emu.eventType.endFrame)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('rom', 'route', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--start', type=int, required=True)
    p.add_argument('--end', type=int, required=True)
    p.add_argument('--fields', nargs='+', required=True)
    a = p.parse_args()
    assert a.start < a.end
    out, route = a.output.resolve(), a.route.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out / 'frames').mkdir()
    manifest = json.loads((route / 'manifest.json').read_text())
    assert manifest['ROM_sha256'] == sha(a.rom)
    assert manifest['result']['frames'] > a.end + 1 and not manifest['fixed_replay']
    run = (route / 'run.lua').read_text()
    anchor = 'out=' + json.dumps(route.as_posix() + '/')
    assert run.count(anchor) == 1 and run.count('replay=nil') == 1
    run = run.replace(anchor, 'out=' + json.dumps(out.as_posix() + '/'))
    run = run.replace('replay=nil', 'replay=' + json.dumps((route / 'inputs.csv').as_posix()))
    assert run.count('capture=12,') == 1
    run = run.replace('capture=12,', 'capture=0,')
    observer = out / 'observer.lua'
    debug = a.rom.with_suffix('.dbg')
    debug_text = debug.read_text() if debug.exists() else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    field_values = {name: set() for name in a.fields}
    for line in debug_text.splitlines():
        if not line.startswith('sym\t'):
            continue
        symbol = dict(part.split('=', 1) for part in line.split('\t', 1)[1].split(',') if '=' in part)
        name = symbol.get('name', '').strip('"')
        if name in field_values and 'val' in symbol:
            field_values[name].add(int(symbol['val'], 0))
    assert all(len(values) == 1 for values in field_values.values()), field_values
    aliases = ''.join('L[' + json.dumps(name) + ']=' + str(next(iter(values))) + '\n'
                      for name, values in field_values.items())
    observer.write_text(aliases + 'FAILED_OBS_OUT=' + json.dumps(out.as_posix() + '/') + '\nFAILED_OBS_BEGIN=' + str(a.start)
                        + '\nFAILED_OBS_END=' + str(a.end) + '\nFAILED_OBS_FIELDS={'
                        + ','.join(json.dumps(n) for n in a.fields) + '}\n' + OBSERVER)
    at = run.index('dofile(')
    script = out / 'run.lua'
    script.write_text(run[:at] + 'dofile(' + json.dumps(observer.as_posix()) + ')\n' + run[at:])
    native = subprocess.run([sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(out),
                             str(script), str(a.rom.resolve()), '--timeout', '150',
                             '--option=--nes.ramPowerOnState=AllZeros', '--option=--nes.randomizeCpuPpuAlignment=false',
                             '--option=--nes.randomizeMapperPowerOnState=false'], cwd=ROOT, capture_output=True, text=True)
    (out / 'host.log').write_text(native.stdout + native.stderr)
    assert native.returncode == 0, (native.stdout + native.stderr)[-3000:]
    for name in ('inputs.csv', 'trace.csv'):
        before = list(csv.DictReader((route / name).open()))
        after = list(csv.DictReader((out / name).open()))
        assert len(after) > a.start - 2 and after == before[:len(after)], name
    rows = list(csv.DictReader((out / 'completed.csv').open()))
    assert len(rows) >= 10
    values = np.frombuffer((out / 'endpoint.argb').read_bytes(), dtype='<u4').reshape(240, 256)
    rgb = np.stack(((values >> 16) & 255, (values >> 8) & 255, values & 255), axis=2).astype(np.uint8)
    Image.fromarray(rgb).save(out / 'endpoint-direct.png')
    q = dict(observation_complete=True, accepted=False, game_changes=False, ROM_sha256=sha(a.rom),
             original_failed_manifest_sha256=sha(route / 'manifest.json'), exact_input_and_trace_prefix=True,
             completed_updates=len(rows), start_frame=a.start, end_frame=a.end,
             direct_PPU_endpoint=a.end, fields=a.fields, observer_sha256=sha(observer), driver_sha256=sha(Path(__file__)),
             scope='Read-only exact recorded controller prefix. Requested fields are sampled after a complete native GameLoop return, matched by PC and stack depth. Endpoint uses actual PPU-tagged direct pixels. The original failed route and reports remain failed; this is diagnosis, not a new clear, item or graphics certificate.')
    (out / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()

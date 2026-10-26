"""Reproduce a failed frozen route and observe player-position writers only."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import subprocess
import sys
from check_tmnt_render_oa import load, address, location

ROOT = Path(__file__).resolve().parents[2]

OBSERVER = r'''
local C=assert(CHIP_WRITE_OBSERVER)
local f=assert(io.open(ROSTER_CONFIG.out..'position-writes.csv','w'))
f:write('frame,pc,bank,sp,a,x,y,p,address,before,value,'..table.concat(C.names,',')..'\n')
local events=assert(io.open(ROSTER_CONFIG.out..'collision-events.csv','w'))
events:write('event,frame,pc,bank,sp,a,x,y,p,'..table.concat(C.names,',')..'\n')
local function read(a)return emu.read(a,emu.memType.nesDebug)end
local function observe(a,v)
 local s=emu.getState();local frame=s['ppu.frameCount']
 if frame<C.first or frame>C.last then return end
 local pc=s['cpu.pc'];local mapped=emu.convertAddress(pc)
 local row={frame,pc,mapped and mapped.address//8192 or -1,s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']or s['cpu.p']or -1,a,read(a),v}
 for _,n in ipairs(C.names)do row[#row+1]=read(C.ram[n])end
 f:write(table.concat(row,',')..'\n');f:flush()
end
for _,n in ipairs({'Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_Speed'})do
 emu.addMemoryCallback(observe,emu.callbackType.write,C.ram[n])
end
for _,h in ipairs(C.hooks)do
 emu.addMemoryCallback(function()
  local s=emu.getState();local frame=s['ppu.frameCount']
  if frame<C.first or frame>C.last then return end
  local mapped=emu.convertAddress(h.pc)
  if not mapped or mapped.address//8192~=h.bank then return end
  for i,v in ipairs(h.bytes)do assert(read(h.pc+i-1)==v,'Bound observer opcode')end
  local row={h.name,frame,h.pc,h.bank,s['cpu.sp'],s['cpu.a'],s['cpu.x'],s['cpu.y'],s['cpu.ps']or s['cpu.p']or -1}
  for _,n in ipairs(C.names)do row[#row+1]=read(C.ram[n])end
  events:write(table.concat(row,',')..'\n');events:flush()
 end,emu.callbackType.exec,h.pc)
end
local stop=emu.stop;emu.stop=function(code)
 f:close();events:close()
 local ram=assert(io.open(ROSTER_CONFIG.out..'observed-ram.bin','wb'))
 for a=0,2047 do ram:write(string.char(read(a)))end
 for a=0x6000,0x7fff do ram:write(string.char(read(a)))end
 ram:close();stop(code)
end
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lua(value):
    # Python bool subclasses int; emit actual Lua literals before the generic
    # numeric fallback. Bare True/False are undefined Lua globals, so a true
    # configuration flag would otherwise silently become nil.
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if value is None:
        return 'nil'
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, list):
        return '{' + ','.join(map(lua, value)) + '}'
    if isinstance(value, dict):
        return '{' + ','.join('[' + lua(k) + ']=' + lua(v) for k, v in value.items()) + '}'
    return str(value)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for n in ['rom', 'route', 'output']:
        p.add_argument('--' + n, type=Path, required=True)
    p.add_argument('--emulator', required=True)
    args = p.parse_args()
    rom, route, out = args.rom.resolve(), args.route.resolve(), args.output.resolve()
    assert not out.is_relative_to(ROOT), 'Keep generated evidence outside the workspace'
    out.mkdir(parents=True, exist_ok=False)
    (out / 'frames').mkdir()
    m = json.loads((route / 'manifest.json').read_text())
    assert m['ROM_sha256'] == sha(rom) and m['exit'] != 0
    trace = list(csv.DictReader((route / 'trace.csv').open()))
    last = int(trace[-1]['frame'])
    b = load(rom)
    names = ['Player_X_Position', 'Player_PageLoc', 'Player_Y_Position',
             'Player_State', 'Player_X_Speed', 'Player_Y_Speed', 'R0', 'R1',
             'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'MmBlockAttack',
             'SavedJoypadBits', 'CdReady', 'CdOldX', 'CdOldY', 'CdPressed',
             'CdHeld', 'CdHurtTimer', 'CdScratch', 'CdScratch2', 'CdNX', 'CdNY',
             'CdVYLo', 'CdVYHi', 'CdLastExportVY', 'RgCrouch', 'BlockBounceTimer',
             'Local_eb', 'PlayerSize', 'SprDataOffset_Ctrl', 'Block_State',
             'Block_State+1', 'SmTempX', 'SmTempPage']
    names = [n for n in names if n in b['syms']]
    hooks = []
    for n in ['PlayerBGCollision', 'CrossoverHeadProbe', 'BillBGHeadConsumer',
              'BillHeadDispatch', 'TnFastHeadGate', 'TnCv3HeadGate',
              'JnHeadDispatch', 'KbHeadDispatch', 'BlockBufferColli_Head',
              'CheckForCoinMTiles', 'PlayerHeadCollision',
              'NativeRarePlayerHeadCollisionCore', 'NYSpd', 'DoFootCheck',
              'DoPlayerSideCheck', 'CrossoverSourceSideProbe',
              'CheckSideMTiles', 'SamusStopAtWallBanked']:
        if n not in b['syms'] or 'seg' not in b['syms'][n]:
            continue
        pos = location(b, n)
        hooks.append(dict(name=n, pc=address(b, n), bank=(pos-16)//8192,
                          bytes=list(b['raw'][pos:pos+8])))
    cfg = dict(names=names, ram={n: address(b, n) for n in names},
               hooks=hooks, first=max(200, last - 35), last=last + 2)
    observer = out / 'observer.lua'
    observer.write_text('CHIP_WRITE_OBSERVER=' + lua(cfg) + '\n' + OBSERVER)
    text = (route / 'run.lua').read_text()
    old = 'out=' + json.dumps(route.as_posix() + '/')
    assert text.count(old) == 1 and text.count('replay=nil') == 1
    text = text.replace(old, 'out=' + json.dumps(out.as_posix() + '/'))
    text = text.replace('replay=nil', 'replay=' + json.dumps((route / 'inputs.csv').as_posix()))
    at = text.index('dofile(')
    script = out / 'run.lua'
    script.write_text(text[:at] + 'dofile(' + lua(observer.as_posix()) + ')\n' + text[at:])
    with (out / 'host.log').open('w') as log:
        result = subprocess.run([sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'),
                                 '--output', str(out), '--emulator', args.emulator,
                                 str(script), str(rom), '--timeout', '120',
                                 '--option=--doNotSaveSettings',
                                 '--option=--nes.ramPowerOnState=AllZeros',
                                 '--option=--nes.randomizeCpuPpuAlignment=false',
                                 '--option=--nes.randomizeMapperPowerOnState=false'],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    exact = all((out / n).read_bytes() == (route / n).read_bytes()
                for n in ['trace.csv', 'inputs.csv'])
    writes = list(csv.DictReader((out / 'position-writes.csv').open()))
    q = dict(observation_complete=True, repair_passed=False, goal_complete=False,
             ROM_sha256=sha(rom), source_manifest_sha256=sha(route / 'manifest.json'),
             observer_sha256=sha(observer), exit=result.returncode,
             original_failed_inputs_and_trace_exact=exact, observed_writes=len(writes),
             position_writes_sha256=sha(out / 'position-writes.csv'),
             collision_events_sha256=sha(out / 'collision-events.csv'),
             scope='Read-only exact failed-input replay with actual position writer PC/bank/register/RAM evidence. Expected original movement assertion remains active. No ROM, physics, map, inventory or controller mutation and no repair admission.')
    (out / 'proof.json').write_text(json.dumps(q, indent=2))
    print(json.dumps(q))
    print(json.dumps(writes[-8:]))
    assert result.returncode != 0 and exact and writes


if __name__ == '__main__':
    main()

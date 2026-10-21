"""Preserve the original beam oracle; observe physical bank/interrupt context."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import run_mesen

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--tag', required=True)
p.add_argument('--qualified', action='store_true')
a = p.parse_args()
OUT = ROOT/f'build/verification/link-beam-v37-{a.tag}'
OUT.mkdir(exist_ok=False)
original = ROOT/'tests/link-beam-impact.lua'
fixture = original.read_text()
if a.qualified:
    fixture = fixture.replace('if not ready or frame<560 then return end',
                              'if not ready or frame<560 or diagnosticDepth~=0 or diagnosticBank~=4 then return end', 1)
    fixture = fixture.replace('if pending==0 then return end',
                              'if pending==0 or diagnosticDepth~=0 or diagnosticBank~=4 then return end', 1)
(OUT/'fixture.lua').write_text(fixture)
report = {'original_fixture_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
          'qualified_entry_context': a.qualified, 'scope': 'Passive observation and optional actual bank/depth qualification; original fragment/lifetime assertions retained; initialized fixture, not route', 'runs': []}
for version in ('v36', 'v37-provisional-c'):
    for mapper in ('mmc3', 'mmc5'):
        d = OUT/f'{version}-{mapper}'
        d.mkdir()
        rom = ROOT/f'build/checkpoints/roster-audit-{version}/smb-crossover-{mapper}.nes'
        script = d/f'observe-{version}-{mapper}.lua'
        script.write_text(f'''dofile([=[{(ROOT/'tests/menu-bootstrap.lua').as_posix()}]=])
diagnosticBank,diagnosticDepth=nil,0
local frame,selected=0,nil
if ROM_NAME:find('mmc5')then
 emu.addMemoryCallback(function(_,v)diagnosticBank=v%128 end,emu.callbackType.write,0x5115)
else
 emu.addMemoryCallback(function(_,v)selected=v%8 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if selected==7 then diagnosticBank=v%128 end end,emu.callbackType.write,0x8001)
end
for _,pc in ipairs({{L.NonMaskableInterrupt,L.IrqScrollSplit}})do emu.addMemoryCallback(function()diagnosticDepth=diagnosticDepth+1 end,emu.callbackType.exec,pc)end
for _,pc in ipairs({{L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI}})do emu.addMemoryCallback(function()diagnosticDepth=diagnosticDepth-1 end,emu.callbackType.exec,pc)end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
local f=assert(io.open([=[{(d/'callbacks.csv').as_posix()}]=],'w'))
f:write('frame,event,bank,depth,foregroundBank,pc,x,y,RgSlot,RgShotType,RgShotAge,RgShotImpact,RgTemp2,RgTemp3,R4,R5,R6,R7\\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
for _,n in ipairs({{'LinkBeamFragments','MetaspriteRenderLoop'}})do
 emu.addMemoryCallback(function()
  if frame<550 then return end
  local s=emu.getState();local slot=r('RgSlot');local row={{frame,n,diagnosticBank or -1,diagnosticDepth,r('CurrentBank'),s['cpu.pc'],s['cpu.x'],s['cpu.y'],slot,r('RgShotType',slot),r('RgShotAge',slot),r('RgShotImpact',slot),r('RgTemp2'),r('RgTemp3'),r('R4'),r('R5'),r('R6'),r('R7')}}
  f:write(table.concat(row,',')..'\\n');f:flush()
 end,emu.callbackType.exec,L[n])
end
dofile([=[{(OUT/'fixture.lua').as_posix()}]=])
''')
        code = run_mesen.run(script, rom, timeout=70)
        source_log = ROOT/f'build/verification/{rom.stem}-{script.stem}.log'
        shutil.copyfile(source_log, d/'native.log')
        report['runs'].append({'version': version, 'mapper': mapper, 'exit': code,
                              'rom_sha256': hashlib.sha256(rom.read_bytes()).hexdigest()})
        (OUT/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
        print(version, mapper, code, flush=True)

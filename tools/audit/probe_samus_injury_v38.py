"""Keep original Samus injury oracles; observe actual bank/interrupt callbacks."""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import run_mesen

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--tag', required=True)
p.add_argument('--qualified', action='store_true')
p.add_argument('--versions', nargs='+', default=['v38-provisional-e'])
p.add_argument('--mappers', nargs='+', default=['mmc3', 'mmc5'])
a = p.parse_args()
OUT = ROOT/f'build/verification/samus-injury-v38-{a.tag}'
OUT.mkdir(exist_ok=False)
original = ROOT/'tests/samus-injury-202.lua'
fixture = original.read_text()
if a.qualified:
    assert fixture.count("r('CurrentBank')%128~=10") == 5
    fixture = fixture.replace("r('CurrentBank')%128~=10", 'diagnosticBank~=10 or diagnosticDepth~=0')
assert fixture.count('setup();return') == 1
fixture = fixture.replace('setup();return', 'setup();diagnosticSetup(index,c);return', 1)
(OUT/'fixture.lua').write_text(fixture)
report = {'original_fixture_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
          'qualified_entry_context': a.qualified,
          'scope': 'Passive callback context/optional actual-bank-and-depth qualification; original full injury lifecycle/numeric assertions retained; seeded components, not routes', 'runs': []}
for version in a.versions:
    for mapper in a.mappers:
        d = OUT/f'{version}-{mapper}'
        d.mkdir()
        rom = ROOT/f'build/checkpoints/roster-audit-{version}/smb-crossover-{mapper}.nes'
        script = d/f'observe-{version}-{mapper}.lua'
        script.write_text(f'''dofile([=[{(ROOT/'tests/menu-bootstrap.lua').as_posix()}]=])
diagnosticBank,diagnosticDepth=nil,0
local frame,selected,ci,cn,cf,cs=0,nil,0,'none',0,0
function diagnosticSetup(i,c)ci,cn,cf,cs=i,c.name,c.facing,c.side end
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
f:write('frame,case,name,facing,side,event,bank,depth,foregroundBank,pc,opcode,hurtKind,hurtTicks,invulTicks,injuryTimer,playerStatus,x,y\\n')
local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
for _,n in ipairs({{'SamusHurtStart','GuestInjuryStarted','GuestInjuryMovement','SamusHurtIntegrated','GuestInjuryRecovered'}})do
 emu.addMemoryCallback(function()
  if frame<550 then return end
  local s=emu.getState();local row={{frame,ci,cn,cf,cs,n,diagnosticBank or -1,diagnosticDepth,r('CurrentBank'),s['cpu.pc'],emu.read(s['cpu.pc'],emu.memType.nesDebug),r('GuestHurtKind'),r('GuestHurtTicks'),r('GuestInvulTicks'),r('InjuryTimer'),r('PlayerStatus'),r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position')}}
  f:write(table.concat(row,',')..'\\n');f:flush()
 end,emu.callbackType.exec,L[n])
end
dofile([=[{(OUT/'fixture.lua').as_posix()}]=])
''')
        code = run_mesen.run(script, rom, timeout=90)
        source_log = ROOT/f'build/verification/{rom.stem}-{script.stem}.log'
        shutil.copyfile(source_log, d/'native.log')
        report['runs'].append({'version': version, 'mapper': mapper, 'exit': code,
                              'rom_sha256': hashlib.sha256(rom.read_bytes()).hexdigest()})
        (OUT/'manifest.json').write_text(json.dumps(report, indent=2)+'\n')
        print(version, mapper, code, flush=True)

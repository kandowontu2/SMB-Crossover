"""Add read-only physical-bank telemetry around the unchanged sword fixture."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen

OUT = ROOT / 'build/verification/link-sword-timing45-bank-diagnostic-a'
OUT.mkdir(exist_ok=False)
fixture = ROOT / 'tests/link-sword-timing.lua'
original = fixture.read_bytes()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copyfile(fixture, OUT / 'original-fixture.lua')
report = dict(classification='diagnostic; original assertions unchanged', fixture_sha256=sha(fixture), runs=[])
for version, mapper in ((44, 'mmc3'), (45, 'mmc3'), (45, 'mmc5')):
    cp = ROOT / ('build/checkpoints/roster-audit-v44' if version == 44 else 'build/checkpoints/roster-audit-v45-provisional-a')
    rom = cp / f'smb-crossover-{mapper}.nes'
    tag = f'v{version}-{mapper}'
    dest = OUT / tag
    dest.mkdir()
    csv = (dest / 'callbacks.csv').as_posix()
    wrapper = dest / f'link-sword-bank-{tag}.lua'
    wrapper.write_text('''local f=assert(io.open(CSV_PATH,'w'))
f:write('observerFrame,pc,bank,physical,character,age,thrust,code\\n');f:flush()
local frame,selector,mode=0,0,0
local banks={};local mm5mode=nil
local function r(n)return emu.read(assert(L[n]),emu.memType.nesDebug)end
if MAPPER==4 then
 emu.addMemoryCallback(function(_,v)selector=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)
 emu.addMemoryCallback(function(_,v)if selector==7 then banks[1]=v&63 end end,emu.callbackType.write,0x8001)
else
 emu.addMemoryCallback(function(_,v)mm5mode=v&3 end,emu.callbackType.write,0x5100)
 emu.addMemoryCallback(function(_,v)banks[1]=v&127 end,emu.callbackType.write,0x5115)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addMemoryCallback(function()
 if frame<550 or frame>590 then return end
 local s=emu.getState();local code={}
 for i=0,7 do code[#code+1]=string.format('%02x',emu.read(L.MeleeBridge+i,emu.memType.nesDebug))end
 f:write(table.concat({frame,s['cpu.pc'],r('CurrentBank'),banks[1]or-1,r('SelectedCharacter'),r('RgAttackAge'),r('RgThrust'),table.concat(code)},',')..'\\n');f:flush()
end,emu.callbackType.exec,L.MeleeBridge)
dofile(MENU_PATH)
dofile(FIXTURE_PATH)
'''.replace('CSV_PATH', json.dumps(csv)).replace('MAPPER', str(4 if mapper == 'mmc3' else 5))
        .replace('MENU_PATH', json.dumps((ROOT / 'tests/menu-bootstrap.lua').as_posix()))
        .replace('FIXTURE_PATH', json.dumps(fixture.as_posix())))
    code = run_mesen.run(wrapper, rom, timeout=90)
    log = ROOT / f'build/verification/{rom.stem}-{wrapper.stem}.log'
    shutil.copyfile(log, dest / 'native.log')
    report['runs'].append(dict(version=version, mapper=mapper, exit=code, rom_sha256=sha(rom),
        dbg_sha256=sha(rom.with_suffix('.dbg')), lbl_sha256=sha(rom.with_suffix('.lbl')),
        files={p.name:sha(p) for p in dest.iterdir() if p.is_file()}))
    assert fixture.read_bytes() == original
    (OUT / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(tag, 'exit', code, flush=True)

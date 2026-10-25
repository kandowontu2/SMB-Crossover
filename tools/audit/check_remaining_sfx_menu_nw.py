"""Run the established source-effect comparison through the current real menu."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=False)
    source = ROOT / 'tests/remaining-source-sfx.lua'; text = source.read_text()
    anchor = "emu.addEventCallback(function()emu.setInput({right=frame==80 or frame==100 or frame==120,start=frame==200},0)end,emu.eventType.inputPolled)"
    assert text.count(anchor) == 1
    replacement = '''local menuDone=false
emu.addEventCallback(function()
 local buttons={}
 if not menuDone then
  if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
   assert(r('SelectedCharacter')==3,'Source effects fixture enters Bill through actual menus')
   menuDone=true
  elseif frame>=60 and frame%12==0 then
   if r('CrossoverMenuState')~=2 then buttons.start=true
   elseif r('CrossoverMenuIndex')~=3 then buttons.right=true
   elseif r('BillVariant')~=0 then buttons.select=true else buttons.a=true end
  end
 end
 emu.setInput(buttons,0)
end,emu.eventType.inputPolled)
'''
    text = text.replace(anchor, replacement)
    script = args.output / 'fixture.lua'
    script.write_text('TEST_DIR=[=[' + (ROOT / 'tests').as_posix() + '/]=]\n' + text)
    command = [sys.executable, str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(args.output),
               str(script), str(args.rom), '--timeout', '60', '--option=--nes.ramPowerOnState=AllZeros',
               '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false']
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    (args.output / 'runner.log').write_text(result.stdout + result.stderr)
    report = dict(passed=result.returncode == 0, exit=result.returncode,
                  ROM_SHA256=hashlib.sha256(args.rom.read_bytes()).hexdigest(),
                  original_fixture_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  bound_fixture_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                  scope='Established exact source-effect register/duration/voice-restoration comparisons; only outdated controller startup was adapted to the actual menu. Explicit audio requests, not natural collection evidence.')
    (args.output / 'proof.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())

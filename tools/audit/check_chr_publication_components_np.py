"""Rerun existing body/attack/reward fixtures on an explicit CHR-fix candidate.

The Meta Knight/health/attack tests contain seeded component arenas. The old
natural-route fixtures are separately identified; they are not campaign clears.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json

ROOT = Path(__file__).resolve().parents[2]
CASES = {
    'meta': ('tests/meta-knight.lua', 'seeded component arenas'),
    'turtle-health': ('build/verification/tmnt-adoption-mn/turtle-health/turtle-health.lua', 'seeded health arena'),
    'turtle-attacks': ('build/verification/tmnt-adoption-mn/turtle-attacks/turtle-attacks.lua', 'seeded attack arenas'),
    'turtle-natural': ('build/verification/tmnt-adoption-mn/turtle-natural/turtle-natural.lua', 'bounded controller scene'),
    'kirby-food': ('build/verification/kirby-adoption-me/final-fixtures/food-v5.lua', 'bounded controller food emergence scene'),
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--names', nargs='+', choices=CASES, default=list(CASES))
    p.add_argument('--retime-turtle-entry', action='store_true',
                   help='Wait for actual controller menu entry before unchanged turtle arena frames')
    a = p.parse_args()
    out, rom = a.output.resolve(), a.rom.resolve()
    out.mkdir(parents=True, exist_ok=False)
    spec = importlib.util.spec_from_file_location('chr_components_mesen', ROOT/'tools/run_mesen.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    results = {}
    for name in a.names:
        relative, scope = CASES[name]
        original = ROOT / relative
        assert original.is_file(), relative
        folder = out / name
        folder.mkdir()
        script = folder / (name + '.lua')
        text = original.read_text()
        if a.retime_turtle_entry and name in ('turtle-health', 'turtle-attacks'):
            # Old components used a title/menu pulse schedule from an earlier
            # selector. Preserve every arena/action/assertion, but start that
            # fixture clock only after the current menu actually starts TMNT.
            prefix = '''local npStarted,npWall=false,0
local function npMenu()
 local buttons={}
 if npWall>=60 and npWall%12==0 then
  if r('CrossoverMenuState')~=2 then buttons.start=true
  elseif r('CrossoverMenuIndex')~=18 then
   if r('CrossoverMenuIndex')<12 then buttons.down=true else buttons.right=true end
  elseif r('TnVariant')~=0 then buttons.select=true
  else buttons.a=true end
 end
 return buttons
end
'''
            marker = 'emu.addEventCallback(function()'
            at = text.index(marker)
            text = text[:at] + prefix + text[at:]
            text = text.replace(marker, marker+'''\n if not npStarted then emu.setInput(npMenu(),0);return end
''', 1)
            marker = 'f=f+1'
            assert text.count(marker)==1
            text = text.replace(marker, '''if not npStarted then
  npWall=npWall+1
  if r('SelectedCharacter')==19 and r('TnVariant')==0 and r('OperMode')==1 and r('GameEngineSubroutine')==8 then
   npStarted=true;f=549
  else assert(npWall<1800,'Actual turtle controller entry timeout');return end
 end
 f=f+1''')
        script.write_text(text)
        runner.ROOT = folder
        code = runner.run(script, rom, timeout=60, emulator_options=[
            '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
            '--nes.randomizeMapperPowerOnState=false'])
        results[name] = dict(exit=code, scope=scope, fixture=relative,
                             fixture_sha256=sha(original), script_sha256=sha(script),
                             retimed_turtle_entry=a.retime_turtle_entry and name in ('turtle-health','turtle-attacks'))
        (out/'results.json').write_text(json.dumps(dict(rom_sha256=sha(rom),
            passed=all(r['exit']==0 for r in results.values()), results=results), indent=2)+'\n')
    return int(any(r['exit'] for r in results.values()))


if __name__ == '__main__':
    raise SystemExit(main())

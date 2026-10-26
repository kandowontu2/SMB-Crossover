"""Freeze two current-build controller runs; preparation never launches Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
ROM_SHA = '6c69e506b45c8420cf57a62b868f89c0fe86d308c0ee55655b48e8f44af9521a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    rom = D / 'world-firebar-padding-v2/adoption-v1/candidate.nes'
    assert sha(rom) == ROM_SHA
    emulator = D / 'mmc3-flag-fix-v23/script-budget-probe-v2/emulator/Mesen.exe'
    settings = emulator.with_name('settings.json')
    assert sha(emulator) == '8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9'
    assert sha(emulator.with_name('MesenCore.dll')) == '4bd40dfc6512328d56d8ad0563263b52be57bac726d8804f0720e461e558cd41'
    assert sha(settings) == '627cd9c71a2011b4cf5fb03a0712d4d77f7890bc269b174d5757776034aab715'
    assert sha('C:/Mesen2/settings.json') == '8a439e0a5eeddc2d4776e516aacfc224c03048b9c7d23d9926a463460a7e748a'
    sources = [ROOT / 'tools/audit/current_roster_recheck_routes.py',
               D / 'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py',
               D / 'streaming-replay-v1/capture.py']
    options = "'--option=--doNotSaveSettings','--option=--nes.removeSpriteLimit=false',"
    runner = replace_once(sources[1].read_text(),
                          "'--option=--nes.ramPowerOnState=AllZeros',",
                          options + "'--option=--nes.ramPowerOnState=AllZeros',")
    (out / 'runner.py').write_text(runner)
    capture = replace_once(sources[2].read_text(),
                           "'--timeout',str(a.timeout),'--option=--nes.ramPowerOnState=AllZeros',",
                           "'--timeout',str(a.timeout),'--emulator'," + repr(str(emulator)) + ',' + options +
                           "'--option=--nes.ramPowerOnState=AllZeros',")
    (out / 'capture.py').write_text(capture)
    coordinator = replace_once(sources[0].read_text(),
                               'from check_tmnt_render_oa import load, address, location',
                               'sys.path.insert(0,' + repr(str(ROOT / 'tools/audit')) + ')\nfrom check_tmnt_render_oa import load, address, location')
    coordinator = replace_once(coordinator, 'ROOT = Path(__file__).resolve().parents[2]', 'ROOT = Path(' + repr(str(ROOT)) + ')')
    coordinator = replace_once(coordinator, "driver = d / 'mmc3-ship-lives-v25/native-routes-v1/bound-mmc3-runner.py'", "driver = Path(" + repr(str(out / 'runner.py')) + ')')
    coordinator = replace_once(coordinator, "str(d / 'streaming-replay-v1/capture.py')", 'str(Path(' + repr(str(out / 'capture.py')) + '))')
    (out / 'coordinator.py').write_text(coordinator)
    extra = [ROOT / n for n in ['tools/audit/check_tmnt_render_oa.py', 'tools/audit/observe_chip_committed_write.py',
             'tools/audit/run_mesen_isolated.py', 'tools/run_mesen.py', 'tools/playthroughs/roster_harness.lua',
             'tools/playthroughs/roster_audit.lua', 'tools/audit/legacy_chr_observer_of.lua']]
    catalog = json.loads((D / 'cv3-parodius-combined-f35-v1/builds-v1/source-inventory-partitions.json').read_text())
    inputs = sources + extra + [rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'), emulator,
             emulator.with_name('MesenCore.dll'), settings, Path('C:/Mesen2/settings.json'),
             D / 'mmc3-static-call-v37/full-roster-v1/native-guard.lua',
             D / 'native-probes-qa-v2/full-roster-aggregate-v1/proof.json', Path(__file__)]
    inputs += [ROOT / row['path'] for row in catalog['primary_source_tool_asset_paths']]
    aggregate = json.loads((D / 'native-probes-qa-v2/full-roster-aggregate-v1/proof.json').read_text())
    for row in aggregate['runs']:
        if row['identity'] in ['mario', 'luigi']:
            inputs += [Path(row['discovery']), Path(row['discovery']).parent / 'policy.lua']
    inputs += list(out.glob('*.py'))
    bindings = {str(f.resolve()): sha(f) for f in sorted(set(inputs), key=str)}
    command = [sys.executable, '-B', str(out / 'coordinator.py'), '--rom', str(rom), '--archive', str(D),
               '--output', str(out / 'native'), '--cases', 'mario:easy', 'luigi:easy', '--replay', '--frames', '18000']
    proof = dict(passed=True, native_executed=False, ROM_sha256=ROM_SHA, native_workers=1,
                 cases=['mario:easy', 'luigi:easy'], command=command, bindings=bindings,
                 changes='Original controller/CHR/completed-loop guards unchanged. Only isolated paths, no-save-settings and hardware8-sprite CLI made explicit.',
                 scope='Two current Easy full1-1 discoveries and independent direct-PPU replays only. No every-item, Hard, shortcut or full-roster claim.')
    (out / 'readiness.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(passed=True, native_executed=False, bindings=len(bindings), readiness=str(out / 'readiness.json'), readiness_sha256=sha(out / 'readiness.json'))))


if __name__ == '__main__':
    main()

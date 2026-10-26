"""One fresh Easy native pair, replaying frozen historical workload byte-exact.

No within-phase writes, fixture changes, extra cases, native retries or adoption.
"""
from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import sys
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load as load
from tmnt_native_storage_driver import ROOT, CURRENT, sha


CANDIDATE = '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'


def prepare(d, out):
    assert not out.exists() and not out.resolve().is_relative_to(ROOT)
    ready = d / 'parser-ready-v1'
    assert sha(ready / 'receipt.json') == 'db59fddc3479507ea5eb9891a786ad05ff7ef7dd33fb5ed505c18eefbb64d478'
    roms = dict(baseline=d / 'current-baseline-v1/baseline.nes', candidate=ready / 'candidate.nes')
    assert sha(roms['baseline']) == CURRENT and sha(roms['candidate']) == CANDIDATE
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    templates = dict(baseline=d / 'native-pilots-v1/diagnostic-baseline-easy-v2',
                     candidate=d / 'native-pilots-v1/diagnostic-candidate-easy-v3')
    # Equal dependency manifests are necessary for the strict pair comparator.
    # The old generators do not execute here: the frozen final Lua is copied
    # literally, while every actual external runtime dependency is pinned.
    runtime = [Path(__file__), ROOT / 'tools/audit/run_mesen_isolated.py', ROOT / 'tools/run_mesen.py',
               ROOT / 'tools/audit/chr_commit_observer.lua']
    for label in ['baseline', 'candidate']:
        original = json.loads((templates[label] / 'binding.json').read_text())
        runtime.append(Path(original['identical_work_origin']) / 'performance-observer.lua')
    runtime += sorted((d / 'native-pilots-v1/candidate-easy/gold').glob('song-*.bin'))
    assert len(runtime) == 22
    dependencies = {str(path): sha(path) for path in runtime}
    emulator = Path('C:/mesen2/Mesen.exe')
    assert sha(emulator) == '8b92daa209ee5052845e02a663aeb1afd6194eca55d86e6628c51114c61da0a9'
    out.mkdir(parents=True)
    metadata = {}
    for label in ['baseline', 'candidate']:
        template, rom, target = templates[label], roms[label], out / (label + '-easy')
        target.mkdir()
        original = json.loads((template / 'binding.json').read_text())
        assert sha(template / 'run.lua') == original['script_sha256'] and original['behavior'] == 0
        assert original['ROM_sha256'] == (CURRENT if label == 'baseline' else 'a9838664f94d29d87fbf4742e31d4e20d8b3a96862beabd11224afa4742d9003')
        text = (template / 'run.lua').read_text()
        assert not re.search(r'\b(?:True|False)\b', text)
        assert '["behavior"]=0' in text and "State writes only at before-phase setup" in text
        shutil.copyfile(template / 'run.lua', target / 'run.lua')
        shutil.copyfile(template / 'profile-config.json', target / 'profile-config.json')
        origin = Path(original['identical_work_origin'])
        for name in ['config.json', 'performance-fixture.lua', 'performance-observer.lua']:
            shutil.copyfile(origin / name, target / name)
        b = load(rom)
        profile = json.loads((template / 'profile-config.json').read_text())
        for hook in profile['hooks']:
            assert address(b, hook['name']) == hook['pc']
            if 'seg' in b['syms'][hook['name']]: assert (location(b, hook['name']) - 16) // 8192 == hook['bank']
            else: assert hook['name'] in ['TnNativeInit', 'TnNativePlay'] and hook['bank'] == 63
        for name, value in profile['ram'].items(): assert address(b, name) == value
        # The source APUs and profile direct-STA sites still denote literal
        # executable instructions. New parser/math sites do not add DMC stores.
        for site in profile['stores']:
            at = 16 + site['bank'] * 8192 + site['pc'] % 8192
            assert b['raw'][at:at + 3] == bytes([0x8d, site['register'] & 255, 0x40])
        parser = ROOT / 'build/verification/agent47-samus-controller-batch-h-preparation/parser/runtime'
        py = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
        check = 'import pathlib,sys;sys.path.insert(0,sys.argv[1]);from lupa.lua54 import LuaRuntime;LuaRuntime().eval("function(s)local f,e=load(s);assert(f,e);return true end")(pathlib.Path(sys.argv[2]).read_text());print("Lua54 syntax PASS")'
        parsed = subprocess.run([str(py), '-c', check, str(parser), str(target / 'run.lua')], capture_output=True, text=True)
        (target / 'parse.log').write_text(parsed.stdout + parsed.stderr)
        assert parsed.returncode == 0
        binding = dict(prepared=True, ROM_sha256=sha(rom), ROM=str(rom), behavior=0,
                       script_sha256=sha(target / 'run.lua'), dependencies=dependencies, emulator_sha256=sha(emulator),
                       staged_inventory_before_phase_only=True, natural_acquisition_claim=False,
                       frozen_historical_template=str(template), historical_template_binding_sha256=sha(template / 'binding.json'),
                       exact_historical_Lua_workload_and_read_only_observers=True,
                       same_historical_five120update_phases=True, setup_boundary_ledger_and_native_floor_actor_checks=True)
        (target / 'binding.json').write_text(json.dumps(binding, indent=2) + '\n')
        metadata[label] = dict(ROM_sha256=sha(rom), script_sha256=binding['script_sha256'], hooks=len(profile['hooks']))
    result = dict(prepared=True, candidate=CANDIDATE, parent=CURRENT, actual_numeric_mode=0, cases=metadata,
                  no_native_launch_yet=True, one_pair_only=True, new_tool_sha256=sha(Path(__file__)))
    (out / 'preparation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


def run(out, label, timeout):
    folder = out / (label + '-easy')
    binding = json.loads((folder / 'binding.json').read_text())
    rom, script = Path(binding['ROM']), folder / 'run.lua'
    assert not (folder / 'native-result.json').exists() and not (folder / 'host.log').exists()
    assert binding['behavior'] == 0 and sha(rom) == binding['ROM_sha256'] and sha(script) == binding['script_sha256']
    assert sha(ROOT / 'build/smb-crossover-mmc5-expanded.nes') == CURRENT
    assert all(sha(Path(name)) == value for name, value in binding['dependencies'].items())
    emulator = Path('C:/mesen2/Mesen.exe');assert sha(emulator) == binding['emulator_sha256']
    command = "@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"
    active = int(subprocess.check_output(['powershell', '-NoProfile', '-Command', command], text=True).strip())
    assert active < 2, ('Two-worker project maximum', active)
    with (folder / 'host.log').open('w') as log:
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(folder),
                                 '--emulator', str(emulator), str(script), str(rom), '--timeout', str(timeout),
                                 '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros',
                                 '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false'],
                                cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    report = binding | dict(passed=False, exit=result.returncode, runner_sha256=sha(Path(__file__)))
    for name in ['result.json', 'ownership-guards.json', 'chr-commit.json', 'mode-readback.json',
                 'first-hardware-failure.json', 'native-source-hardware.json']:
        if (folder / name).exists(): report[name] = json.loads((folder / name).read_text())
    report['passed'] = result.returncode == 0 and all(report.get(name, {}).get('passed') for name in ['result.json', 'ownership-guards.json', 'chr-commit.json', 'native-source-hardware.json']) and report.get('mode-readback.json', {}).get('actual') == 0
    (folder / 'native-result.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(passed=report['passed'], exit=result.returncode, ROM_sha256=binding['ROM_sha256'], behavior=0,
                          failure=report.get('first-hardware-failure.json'))))
    raise SystemExit(0 if report['passed'] else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--run', choices=['baseline', 'candidate'])
    p.add_argument('--timeout', type=int, default=180)
    a = p.parse_args()
    if a.run: run(a.output, a.run, a.timeout)
    else: prepare(a.experiment, a.output)


if __name__ == '__main__':
    main()

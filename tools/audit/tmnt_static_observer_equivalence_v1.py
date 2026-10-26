"""Freeze/run ONE static-observer equality case; preparation never launches Mesen.

The old dynamic observer is read only and is never rerun.  Equality here must
retain the old parser candidate's timing failure; it is not a ROM repair.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
ROMHASH = '9a791d0e13015ff362ffc9e460aaac8c8a0a5b6f73e990959dee4e074da473fd'
STATICHASH = '3412b98077d9c4f5436ab3df00712004fee572a1a3ceaa2810f355da646b4eca'
CSV = ['audio-components.csv', 'chr-commit.csv', 'dmc-instruction-clocks.csv',
       'gameplay.csv', 'source-apu.csv', 'source-state.csv',
       'tmnt-performance-calls.csv', 'tmnt-performance-frames.csv']
JSONL = ['before-phase-setup.jsonl', 'native-bus.jsonl']
JSON = ['chr-commit.json', 'mode-readback.json', 'native-source-hardware.json',
        'ownership-guards.json', 'result.json']
META = ['binding.json', 'candidate-run.log', 'config.json', 'host.log',
        'native-result.json', 'parse.log', 'performance-fixture.lua',
        'performance-observer.lua', 'profile-config.json', 'run.lua']


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prepare(out):
    assert not out.exists() and not out.resolve().is_relative_to(ROOT)
    storage = D / 'tmnt-native-storage-current50b5-v1'
    old = storage / 'parser-native-pilot-v1/candidate-easy'
    static = D / 'tmnt-static-observer-v1'
    rom = storage / 'parser-ready-v1/candidate.nes'
    assert sha(rom) == ROMHASH and sha(static / 'run.lua') == STATICHASH
    # An unexpected old artifact must be classified rather than silently omitted.
    assert {p.name for p in old.iterdir() if p.is_file()} == set(CSV + JSONL + JSON + META)
    assert json.loads((old / 'mode-readback.json').read_text()) == dict(requested=0, actual=0, selected=19)
    out.mkdir(parents=True)
    # Preserve the frozen Lua's existing import locations. Its workload is exact.
    shutil.copyfile(static / 'run.lua', out / 'run.lua')
    for name in ['config.json', 'performance-fixture.lua', 'profile-config.json']:
        shutil.copyfile(old / name, out / name)
    oldbind = json.loads((old / 'binding.json').read_text())
    imports = [Path(p) for p in oldbind['dependencies']]
    imports += [static / n for n in ['run.lua', 'performance-observer.lua',
                                     'chr-commit-observer.lua', 'tmnt_static_exec_dispatcher_v1.lua']]
    imports += [ROOT / 'tools/audit/run_mesen_isolated.py', ROOT / 'tools/run_mesen.py', Path(__file__)]
    exe = Path('C:/mesen2/Mesen.exe')
    runtime = [exe, *sorted(exe.parent.glob('*.dll')), exe.parent / 'settings.json']
    dependencies = {str(p): sha(p) for p in sorted(set(imports + runtime))}
    romfiles = [rom, *[rom.with_suffix(s) for s in ['.lbl', '.dbg', '.map'] if rom.with_suffix(s).exists()]]
    binding = dict(prepared=True, native_run=False, original=str(old), static=str(static), ROM=str(rom),
                   ROM_sha256=ROMHASH, script_sha256=sha(out / 'run.lua'), numeric_mode=0,
                   original_files={p.name: sha(p) for p in old.iterdir() if p.is_file()},
                   ROM_and_symbols={str(p): sha(p) for p in romfiles}, dependencies=dependencies,
                   compare_byte_exact_CSV=CSV, compare_ordered_parsed_JSONL=JSONL,
                   compare_parsed_JSON=JSON, original_metadata_accounted=META,
                   original_raw_frames=0, original_PPU_screenshots=0,
                   expected_old_negative=dict(updates=600, draws=566, baseline_draws=572),
                   no_original_dynamic_rerun=True, same_input_no_workload_state_changes=True,
                   native_requires_explicit_parent_grant=True)
    (out / 'binding.json').write_text(json.dumps(binding, indent=2) + '\n')
    command = [sys.executable, '-B', str(Path(__file__)), '--output', str(out), '--run-granted']
    (out / 'single-run-command.json').write_text(json.dumps(command, indent=2) + '\n')
    print(json.dumps(dict(prepared=True, native_run=False, binding_sha256=sha(out / 'binding.json'), command=command)))


def compare(out):
    b = json.loads((out / 'binding.json').read_text());old = Path(b['original'])
    for name in CSV:
        assert (old / name).read_bytes() == (out / name).read_bytes(), ('CSV observation changed', name)
    for name in JSONL:
        before = [json.loads(s) for s in (old / name).read_text().splitlines()]
        after = [json.loads(s) for s in (out / name).read_text().splitlines()]
        assert before == after, ('Ordered JSONL observation changed', name)
    for name in JSON:
        assert json.loads((old / name).read_text()) == json.loads((out / name).read_text()), ('JSON observation changed', name)
    assert not list(out.glob('*.png')) and not list(out.glob('*.rgb')), 'Original has no raw frames/screenshots'
    import csv
    rows = list(csv.DictReader((out / 'tmnt-performance-frames.csv').open()))
    # Bind the raw old failure rather than deriving a new performance verdict.
    assert (old / 'tmnt-performance-frames.csv').read_bytes() == (out / 'tmnt-performance-frames.csv').read_bytes()
    proof = dict(passed=True, native_run=True, observer_equivalence_only=True,
                 ROM_sha256=ROMHASH, numeric_mode_readback=0, same_old_cadence_failure_retained=True,
                 old_expected_draws=566, unchanged_600_update_workload=True,
                 CSV_files=len(CSV), ordered_JSONL_files=len(JSONL), JSON_files=len(JSON),
                 raw_frames_in_original_and_successor=0, frame_rows=len(rows),
                 binding_sha256=sha(out / 'binding.json'), checker_sha256=sha(Path(__file__)))
    (out / 'equivalence-proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


def run(out):
    b = json.loads((out / 'binding.json').read_text());rom = Path(b['ROM'])
    assert not (out / 'host.log').exists(), 'ONE run only; failures remain immutable'
    assert all(sha(Path(p)) == h for p, h in (b['dependencies'] | b['ROM_and_symbols']).items())
    assert sha(out / 'run.lua') == b['script_sha256'] == STATICHASH
    old = Path(b['original'])
    assert all(sha(old / p) == h for p, h in b['original_files'].items())
    cmd = "@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*Mesen*' -and $_.CommandLine -like '*--testRunner*' }).Count"
    assert int(subprocess.check_output(['powershell', '-NoProfile', '-Command', cmd], text=True).strip()) < 2
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(out),
               '--emulator', 'C:/mesen2/Mesen.exe', str(out / 'run.lua'), str(rom), '--timeout', '180',
               '--option=--doNotSaveSettings', '--option=--nes.ramPowerOnState=AllZeros',
               '--option=--nes.randomizeCpuPpuAlignment=false', '--option=--nes.randomizeMapperPowerOnState=false']
    with (out / 'host.log').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    (out / 'launch-result.json').write_text(json.dumps(dict(exit=result.returncode, command=command), indent=2) + '\n')
    assert result.returncode == 0, ('Native failure retained; no automatic retry', result.returncode)
    compare(out)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--output', type=Path, required=True)
    p.add_argument('--run-granted', action='store_true');a = p.parse_args()
    run(a.output) if a.run_granted else prepare(a.output)

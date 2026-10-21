"""Run frozen source-derived Ryu gate cases; seeded components, not traversal."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import run_mesen

SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
COUNTS = {'B': 10, 'F': 2, 'G': 6, 'I': 4, 'J': 12}
NEGATIVE_CASES = {'B': [1, 2], 'F': [1, 2], 'G': list(range(1, 7)), 'I': [1, 2]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('checkpoint', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--negative', action='store_true')
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report = dict(scope=__doc__, expected='source-negative' if args.negative else 'all-pass',
                  traversal_proof=False, runs=[], completed=False)
    report_path = out / 'report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    for mapper in ('mmc3', 'mmc5'):
        rom = args.checkpoint.resolve() / f'smb-crossover-{mapper}.nes'
        binding = out / mapper
        subprocess.run([sys.executable, str(ROOT / 'build/verification/prepare_ryu_gates_binding.py'),
                        '--rom', str(rom), '--out', str(binding)], check=True)
        metadata = json.loads((binding / 'binding.json').read_text())
        jump = out / f'{mapper}-jump'
        subprocess.run([sys.executable, str(ROOT / 'build/verification/ryu-wall-jumpslash-v43-preparation/prepare_binding.py'),
                        '--rom', str(rom), '--out', str(jump)], check=True)
        jump_meta = json.loads((jump / 'binding.json').read_text())
        assert jump_meta['component_sha256'] == '6489db543502fae2575f01600442b8f1846f247c67a10ff26125a9b6bcf7f7b2'
        assert metadata['rom_sha256'] == jump_meta['rom_sha256'] == SHA(rom)
        jobs = [(key, Path(f['wrapper']), Path(f['output']), Path(f['core']), f['core_sha256'])
                for key, f in metadata['fixtures'].items()]
        jobs.append(('J', Path(jump_meta['wrapper']), jump / 'future-emulator-output',
                     ROOT / 'build/verification/ryu-wall-jumpslash-v43-preparation/component.lua',
                     jump_meta['component_sha256']))
        for key, wrapper, target, core, digest in jobs:
            assert SHA(core) == digest
            code = run_mesen.run(wrapper, rom, timeout=120)
            original_log = ROOT / f'build/verification/{rom.stem}-{wrapper.stem}.log'
            frozen_log = target / 'native.log'
            shutil.copyfile(original_log, frozen_log)
            result_path = target / 'result.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else None
            row = dict(mapper=mapper, fixture=key, exit=code, rom_sha256=SHA(rom),
                       fixture_sha256=digest, wrapper_sha256=SHA(wrapper),
                       result=result, files={str(p.relative_to(out)): SHA(p)
                                            for p in target.iterdir() if p.is_file()})
            report['runs'].append(row)
            report_path.write_text(json.dumps(report, indent=2) + '\n')
            assert SHA(core) == digest, 'Frozen independent source oracle changed'
            assert result and result['cases'] == result['completed'] == COUNTS[key], (key, code, result)
            if args.negative:
                assert code == 1 and result['mismatches'] > 0, (key, code, result)
                actual_cases = [f['case'] for f in result['failures']]
                if key in NEGATIVE_CASES:
                    assert actual_cases == NEGATIVE_CASES[key], (key, actual_cases)
                else:
                    assert set(actual_cases) == {1, 2, 3, 4}, ('Only wall Jump Slash may fail', actual_cases)
            else:
                assert code == 0 and not result['failures'] and result['mismatches'] == 0, (key, code, result)
            print(mapper, key, 'completed', result['completed'], 'mismatches', result['mismatches'], flush=True)
    report['completed'] = True
    report['total_cases'] = sum(r['result']['completed'] for r in report['runs'])
    report['total_mismatches'] = sum(r['result']['mismatches'] for r in report['runs'])
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print('CONFIRMED NEGATIVE' if args.negative else 'PASS', report['total_cases'], 'source-derived cases', flush=True)


if __name__ == '__main__':
    main()

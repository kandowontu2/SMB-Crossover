"""Root-owned unchanged-oracle checks of the one-byte multirow correction."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
F = ROOT / 'build/checkpoints/roster-audit-v49-provisional-f'
G = ROOT / 'build/checkpoints/roster-audit-v49-provisional-g'
OUT = ROOT / 'build/verification/root49g-bounded-tests-b'


def main():
    OUT.mkdir(exist_ok=False)
    report = dict(status='running-provisional', goal_complete=False, binary_diff={}, runs=[])

    def save():
        (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def run(mapper, label, argv):
        log = OUT / f'{mapper}-{label}.log'
        with log.open('w', encoding='utf-8') as file:
            result = subprocess.run([sys.executable, *argv], cwd=ROOT, stdout=file, stderr=subprocess.STDOUT)
        row = dict(mapper=mapper, fixture=label, exit=result.returncode, log=str(log.relative_to(ROOT)), log_sha256=sha(log), argv=argv)
        report['runs'].append(row)
        save()
        print(json.dumps(row), flush=True)
        return result.returncode

    for mapper in ('mmc3', 'mmc5'):
        old = (F / f'smb-crossover-{mapper}.nes').read_bytes()
        rom = G / f'smb-crossover-{mapper}.nes'
        new = rom.read_bytes()
        differences = [i for i, (a, b) in enumerate(zip(old, new)) if a != b]
        assert len(old) == len(new) and differences == [501754]
        assert old[501753:501755] == bytes((0x90, 0x29))
        assert new[501753:501755] == bytes((0x90, 0x1d))
        assert (F / rom.with_suffix('.lbl').name).read_bytes() == rom.with_suffix('.lbl').read_bytes()
        report['binary_diff'][mapper] = dict(only_operand_rom_offset=501754, branch_rom_offset=501753, old_operand=41, new_operand=29, all_labels_literal_equal=True, sha256=sha(rom))
    save()
    for mapper, data in report['binary_diff'].items():
        digest = data['sha256']
        common = ['--checkpoint-dir', str(G), '--expected-rom-sha256', digest, '--mapper', mapper]
        run(mapper, 'environment-v4', ['build/verification/ryu49-environment-v4-preparation-a/runner.py', *common, '--tag', f'root49g-v4-{mapper}-environment-b', '--run'])
        run(mapper, 'ground-v3', ['build/verification/ryu49f-fixture-bindings-a/runner.py', *common, '--fixture', 'ground', '--tag', f'root49g-v3-{mapper}-ground-b', '--run'])
        runner = 'build/verification/ryu-wall49-component-preparation-b/runner.py'
        bound = OUT / f'wall44-{mapper}'
        assert run(mapper, 'wall44-bind', [runner, 'bind', '--rom', str(G / f'smb-crossover-{mapper}.nes'), '--expected-rom-sha256', digest, '--out', str(bound)]) == 0
        binding = bound / 'binding.json'
        run(mapper, 'wall44', [runner, 'run', '--binding', str(binding), '--expected-binding-sha256', sha(binding)])
    report['status'] = 'PASS' if all(r['exit'] == 0 for r in report['runs']) else 'FAIL-retained'
    save()


if __name__ == '__main__':
    main()

"""Exercise smaller task reservations without changing workspace hard limits."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT/'tools/audit/run_bounded_build_v1.py'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(ROOT/'build') and not out.exists()
    out.mkdir()
    rows = []
    for name, cap, count, resume, expected in (
        ('success', 2, 2, False, True),
        ('overflow', 2, 3, False, False),
        ('resume', 1, 1, True, False),
        ('raise-cap', 1001, 1, False, False),
    ):
        target = out/name
        if resume:
            target.mkdir()
            (target/'keep.txt').write_text('preserve')
        code = ('from pathlib import Path; import sys; p=Path(sys.argv[1]); '
                'p.mkdir(exist_ok=True); '
                '[p.joinpath(str(i)).write_text("bounded") for i in range(int(sys.argv[2]))]')
        command = [sys.executable, '-B', str(RUNNER), '--output', str(target),
                   '--max-files', str(cap), '--timeout', '15']
        if resume:
            command.append('--resume')
        command += ['--', sys.executable, '-B', '-c', code, str(target), str(count)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        assert (result.returncode == 0) == expected, (name, result.stdout, result.stderr)
        if expected:
            assert len(list(target.iterdir())) == count
        elif resume:
            assert [p.name for p in target.iterdir()] == ['keep.txt']
            assert (target/'keep.txt').read_text() == 'preserve'
        else:
            assert not target.exists(), name
        rows.append(dict(case=name, passed=True, exit_code=result.returncode))
    (out/'result.json').write_text(json.dumps(dict(passed=True, cases=rows), indent=2)+'\n')
    print(json.dumps(dict(passed=True, cases=len(rows))))


if __name__ == '__main__':
    main()

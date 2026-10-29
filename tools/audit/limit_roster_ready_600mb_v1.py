"""Apply the stricter 600 MB guard to one immutable, unlaunched ready file."""
from pathlib import Path
import argparse
import json
from current_roster_compact_11_v1 import ROOT, sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ready', type=Path)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    ready = args.ready.resolve()
    assert ready.is_relative_to(ROOT / 'build') and sha(ready) == args.sha256
    record = json.loads(ready.read_text())
    assert not (ready.parent / 'launch.json').exists()
    assert not (ready.parent / 'result.json').exists()
    assert all(sha(path) == expected for path, expected in record['bindings'].items())
    assert 0 < record['config']['capture_bytes'] <= 512 * 1024 * 1024
    assert 600 <= record['config']['limit'] <= 8000
    assert record['screenshot_files_during_native'] == 0
    command = record['command']
    old = str(ROOT / 'tools/audit/run_mesen_isolated.py')
    replacement = ROOT / 'tools/audit/run_mesen_600mb_isolated_v1.py'
    assert command.count(old) == 1
    assert '--option=--nes.removeSpriteLimit=false' in command
    backup = ready.parent / 'prepared-with-2gb-reservation.json'
    assert not backup.exists()
    backup.write_bytes(ready.read_bytes())
    command[command.index(old)] = str(replacement)
    for path in [replacement, Path(__file__).resolve(), backup]:
        record['bindings'][str(path)] = sha(path)
    record['central_run_cap_bytes'] = 600_000_000
    record['storage_guard'] = (
        'Stricter600MB live total run cap around512MiB maximum container; '
        'workspace70GB/archive30GB,64runfiles,25GB free floor and single-process lease enforced.')
    ready.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(dict(ready=str(ready), sha256=sha(ready))))


if __name__ == '__main__':
    main()

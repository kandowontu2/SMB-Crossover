"""Launch one reviewed immutable roster receipt with native hardware settings.

The caller supplies the exact ready digest. Refuse changed dependencies, a
second Mesen process or an existing launch receipt; never restart a lost handle.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys

SETTINGS = Path('C:/Mesen2/settings.json')
SETTINGS_SHA = '66d3c35063c1692c595bab6e07a21854f37b4af970597251a4e320b91d37a9aa'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ready', type=Path)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    ready = args.ready.resolve()
    assert sha(ready) == args.sha256, 'Ready changed'
    record = json.loads(ready.read_text())
    rows = record['bindings']
    bindings = {row['path']: row['sha256'] for row in rows} if isinstance(rows, list) else rows
    for path, expected in bindings.items():
        assert sha(path) == expected, path
    before = sha(SETTINGS)
    assert before == SETTINGS_SHA, 'Hardware settings changed'
    hardware = json.loads(SETTINGS.read_bytes().decode('utf-8-sig'))['Nes']
    assert hardware['RemoveSpriteLimit'] is False and hardware['AdaptiveSpriteLimit'] is False
    assert hardware['PpuExtraScanlinesBeforeNmi'] == hardware['PpuExtraScanlinesAfterNmi'] == 0
    receipt = ready.parent / 'launch.json'
    assert not receipt.exists(), 'Preserve the original launch; inspect its terminal state'
    command = record.get('command')
    if command is None:
        command = json.loads((ready.parent / 'command.json').read_text())
        if isinstance(command, dict):
            command = command['argv']
    assert isinstance(command, list) and command
    if command[0] == 'python':
        command[0] = sys.executable
    if '--emulator' not in command:
        index = next(i for i, item in enumerate(command) if item.endswith('run_mesen_isolated.py'))
        command[index + 1:index + 1] = ['--emulator', 'C:/Mesen2/Mesen.exe']
    if '--option=--nes.removeSpriteLimit=false' not in command:
        command.append('--option=--nes.removeSpriteLimit=false')
    running = subprocess.run(['powershell', '-NoProfile', '-Command',
        "Get-CimInstance Win32_Process -Filter \"Name = 'Mesen.exe'\" | Select-Object -ExpandProperty ProcessId"],
        capture_output=True, text=True, check=True).stdout.strip()
    assert not running, 'Another native Mesen process is active: ' + running
    completed = subprocess.run(command)
    changed = [path for path, expected in bindings.items() if sha(path) != expected]
    after = sha(SETTINGS)
    result = dict(ready_sha256=sha(ready), ROM_sha256=record['ROM_sha256'],
                  exit_code=completed.returncode, settings_before=before,
                  settings_after=after, changed_inputs=changed, actual_argv=command,
                  launcher=dict(path=str(Path(__file__).resolve()), sha256=sha(__file__)))
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    assert before == after and not changed, 'Inputs/settings changed'
    return completed.returncode


if __name__ == '__main__':
    raise SystemExit(main())

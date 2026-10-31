"""One exact, separately granted SMB2 first look; never touch a live Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
O = R / 'build/smb2-final62-firstlooks-v4'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--launch', type=int, choices=range(4), required=True)
    args = ap.parse_args()
    source = R / 'build/functional-roster-coherent62-v4/handoff.json'
    ready = O / 'prepared.json'
    assert sha(source) == 'bb581aad7a4224cd35b83e056fe880cbd49c5cfcf04bfa637b00ea146bc01ab6'
    assert sha(ready) == '48bce99bdba1b18aed1d240ba508ae5050b4a8ecc69a1cb2b60392dd6cf60ef0'
    summary = json.loads(ready.read_text())
    selected = summary['packets'][args.launch]
    assert selected['variant'] == args.launch
    packet = Path(selected['path'])
    assert sha(packet) == selected['sha256']
    packets = [json.loads(p.read_text()) for p in (source, packet)]
    for q in packets:
        for path, digest in q['bindings'].items():
            assert sha(path) == digest, ('Binding drift', path)
    output = packet.parent / 'capture'
    assert not output.exists() or not any(output.iterdir()), 'Do not repeat an executed packet'
    probe = subprocess.run([
        'powershell', '-NoProfile', '-Command',
        'Get-CimInstance Win32_Process -Filter "Name like \'%Mesen%\'" | '
        'Select-Object ProcessId,Name | ConvertTo-Json -Compress',
    ], capture_output=True, text=True, check=True)
    if probe.stdout.strip():
        print(json.dumps(dict(launched=False, reason='Live Mesen; no action taken',
                              processes=probe.stdout.strip())))
        return 3
    grant = dict(reviewed_by='root', source_sha256=sha(source),
                 ready_sha256=sha(packet), tool_sha256=sha(__file__),
                 variant=args.launch, native_class=selected['native_class'],
                 same_process_no_live_Mesen=True, automatic_retries=False,
                 max_PPU_frames=1200, game_PPU_frames=220, host_seconds=60,
                 PNG=4, files=64, bytes=536870912, normal_8_sprites=True,
                 AllZeros=True, no_RAM_writes=True,
                 scope='Cold/menu/lives/parser/walk/jump/land; not a full level or all abilities.')
    (packet.parent / 'root-grant.json').write_text(json.dumps(grant, indent=2) + '\n')
    sys.argv = [str(packet.parent / 'run.py'), '--launch']
    runpy.run_path(str(packet.parent / 'run.py'), run_name='__main__')
    raise AssertionError('Runner must produce a terminal exit code')


if __name__ == '__main__':
    raise SystemExit(main())

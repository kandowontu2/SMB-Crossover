"""Launch exactly the reviewed SMB2 first look, only while Mesen is idle."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
O = R / 'build/smb2-current-native-firstlook-v2'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--launch', action='store_true', required=True)
    ap.parse_args()
    source = R / 'build/functional-roster-smb2-v1/handoff.json'
    ready = O / 'ready.json'
    assert sha(source) == 'daa4910be05ffca20353bc5d6baf84093476369f46b5a71477da130253d2241d'
    assert sha(ready) == 'b82c529192f50987acb2e77b5612a5c3dff4771990acab885036431c1d54ad87'
    packets = [json.loads(p.read_text()) for p in (source, ready)]
    for packet in packets:
        for path, digest in packet['bindings'].items():
            assert sha(path) == digest, ('Binding drift', path)
    capture = O / 'capture'
    # Preparation creates this directory; an empty directory is not a run.
    assert not capture.exists() or not any(capture.iterdir()), 'Do not repeat an executed packet'
    probe = subprocess.run([
        'powershell', '-NoProfile', '-Command',
        'Get-CimInstance Win32_Process -Filter "Name like \'%Mesen%\'" | '
        'Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress',
    ], capture_output=True, text=True, check=True)
    if probe.stdout.strip():
        print(json.dumps(dict(launched=False, reason='Existing Mesen is live; no action taken',
                              processes=probe.stdout.strip())))
        return 3
    grant = dict(
        reviewed_by='root', same_process_live_Mesen_check=True, no_live_Mesen=True,
        guard_tool_sha256=sha(__file__), source_handoff_sha256=sha(source),
        ready_sha256=sha(ready), verified_bindings=sum(len(p['bindings']) for p in packets),
        ROM_sha256=packets[1]['ROM_sha256'], max_frames=1200, game_PPU_frames=220,
        host_seconds=60, max_PNG=4, max_files=64, max_bytes=536870912,
        normal_8_sprites=True, AllZeros=True, no_RAM_writes=True,
        automatic_retries=False,
        scope='SMB2 Mario cold/menu/lives/parser/walk/jump/land and passive timing; no full level claim.',
    )
    (O / 'root-guarded-grant.json').write_text(json.dumps(grant, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('reviewed_smb2_native_firstlook', O / 'run.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    sys.argv = [str(O / 'run.py'), '--launch']
    runner.main()
    raise AssertionError('Runner must produce a terminal exit code')


if __name__ == '__main__':
    raise SystemExit(main())

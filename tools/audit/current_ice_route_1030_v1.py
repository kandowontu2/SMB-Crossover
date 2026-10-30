"""Current Popo/Nana routes with the same native assertions and sparse captures.

The measured Celeste observer required94s for3900frames. The earlier genuine
Ice routes need about5100frames, so this packet permits145s, with the unchanged
6000frame ceiling. Every launch still requires a separately reviewed packet.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
import current_character_route_1030_v4 as D

MARKERS = ['first-active', 'corner-332', 'corner-345', 'corner-360',
           'power-change', 'flagpole', 'endpoint', 'failure']
SCRIPT = R / 'tools/audit/current_ice_sparse_11_1030_v1.lua'


def prepare(args):
    original = R / 'tools/audit/current_character_sparse_11_1030_v1.lua'
    source = original.read_text()
    old = """  want('mushroom',c.status==1)
  want('wall-contact',opt('CmWallGrace')>0 and c.status>0)
  want('flower',c.status==2)
  want('dash',opt('CmDashTimer')>0 or opt('CmState')==6)"""
    new = """  want('corner-332',c.x>=332 and c.x<345)
  want('corner-345',c.x>=345 and c.x<360)
  want('corner-360',c.x>=360 and c.x<380)
  want('power-change',lastPower~=nil and c.status~=lastPower)"""
    assert source.count(old) == 1
    generated = source.replace(old, new)
    # Only review-trigger selection changes. All native assertions, controller
    # policy, frame telemetry, source OAM/CHR and endpoint checks stay intact.
    if SCRIPT.exists():
        assert SCRIPT.read_text() == generated
    else:
        SCRIPT.write_text(generated)
    old_prepare = D.C.prepare
    def ice_prepare(a):
        D.C.SCRIPT = SCRIPT
        D.C.MARKERS = MARKERS
        return old_prepare(a)
    D.C.prepare = ice_prepare
    D.prepare(args)
    p = args.output.resolve() / 'native-packet.json'
    h = json.loads(p.read_text())
    h.update(emulator_timeout_seconds=145, process_timeout_seconds=160,
             prepared_predecessor_sha256=D.sha(p),
             timeout_basis='Measured unchanged sparse observer:3900frames/93.973s; prior authentic Ice route~5100frames. Same6000frame ceiling and512MiB/64files/eightselectedscreens.')
    h['bindings'][str(Path(__file__).resolve())] = D.sha(__file__)
    q = p.with_name('native-ice-packet.json')
    assert not q.exists()
    q.write_text(json.dumps(h, indent=2) + '\n')
    print(json.dumps(dict(packet=str(q), packet_sha256=D.sha(q), native=False)))


def run(args):
    p = args.packet.resolve()
    h = json.loads(p.read_text())
    assert h['prepared'] and not h['native'] and h['maximum_emulated_frames'] <= 6000
    assert D.sha(h['ROM']) == h['ROM_sha256'] and D.sha(h['ready']) == h['ready_sha256']
    assert D.sha(p.with_name('native-packet.json')) == h['prepared_predecessor_sha256']
    for f, expected in h['bindings'].items():
        assert D.sha(f) == expected, f
    assert h['capture_bytes'] == 512*1024*1024 and h['capture_files'] == 64
    assert h['emulator_timeout_seconds'] == 145 and h['process_timeout_seconds'] == 160
    assert h['maximum_selected_PNG_frames'] == 8
    active = subprocess.run(['powershell', '-NoProfile', '-Command',
        'Get-CimInstance Win32_Process -Filter "Name=\'Mesen.exe\'" | Select-Object -ExpandProperty ProcessId'],
        capture_output=True, text=True, check=True).stdout.strip()
    assert not active, 'Existing Mesen is live; do not launch or touch it'
    out = p.parent
    assert not (out/'native-launch.json').exists(), 'No automatic native retry'
    import audit.capture_budget as B
    import run_mesen as M
    assert M.run.__globals__['run_capped'] is B.run_capped
    B.RUN_BYTES = h['capture_bytes']
    B.PAYLOAD_BYTES = B.RUN_BYTES - 1_000_000
    preflight = B.preflight
    B.preflight = lambda output: preflight(output, reserved_bytes=B.RUN_BYTES, reserved_files=64)
    os.environ['SMB_RUN_OUTPUT'] = str(out)
    (out/'native-launch.json').write_text(json.dumps(dict(packet_sha256=D.sha(p),
        exact_ROM_sha256=h['ROM_sha256'], no_existing_Mesen=True, automatic_retries=False,
        capture_bytes=B.RUN_BYTES, process_timeout_seconds=160), indent=2)+'\n')
    code = M.run(Path(h['script']), Path(h['ROM']), h['emulator'],
                 h['emulator_timeout_seconds'], emulator_options=h['settings'])
    print(json.dumps(dict(native_exit_code=code, output=str(out))))
    return code


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='action', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--identity', choices=['popo','nana'], required=True)
    p.add_argument('--mode', choices=['easy','hard'], default='easy')
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--expected-sha256', required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--frames', type=int, default=6000)
    p.add_argument('--policy', type=Path, required=True)
    p = sub.add_parser('run')
    p.add_argument('--packet', type=Path, required=True)
    args = ap.parse_args()
    if args.action == 'prepare':
        assert 1 <= args.frames <= 6000
        prepare(args)
    else:
        return run(args)


if __name__ == '__main__':
    raise SystemExit(main())

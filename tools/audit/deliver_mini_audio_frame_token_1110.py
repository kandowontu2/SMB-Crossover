"""Deliver qualified packed music and validate the installed native audio trace."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from prepare_selected_native_packet_v1 import sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--vectors', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.candidate, args.output
    pin = sha(root/'candidate.nes')
    vectors = json.loads(args.vectors.read_text())
    assert vectors['passed'] and vectors['candidate_SHA256'] == pin
    common = ['--candidate', str(root), '--route', str(root/'route'),
              '--fire', str(root/'native/fire'), '--idle', str(root/'native/idle'),
              '--power', str(root/'native/power'), '--output', str(out),
              '--previous', '14a4e10058c683605344564d118202970da6ccae4482bf1dfca76b9ad743aacc']

    def run(argv):
        result = subprocess.run([sys.executable, '-B', *argv], text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout[-1200:], flush=True)
        assert result.returncode == 0, (argv, result.returncode)

    candidate_audio = json.loads((root/'route/capture/audio-order.json').read_text())
    assert candidate_audio['ROM_sha256'] == pin and candidate_audio['packed_frames'] > 3000
    assert candidate_audio['packed_status_writes'] == candidate_audio['packed_frames']
    run(['tools/audit/deliver_mini_lifts_art_1108.py', 'install', *common])
    run([str(out/'downloads-smoke/run.py')])
    installed_audio = json.loads((out/'downloads-smoke/capture/audio-order.json').read_text())
    assert installed_audio == candidate_audio
    run(['tools/audit/deliver_mini_lifts_art_1108.py', 'finalize', *common])
    receipt_path = out/'verified-delivery.json'
    receipt = json.loads(receipt_path.read_text())
    cadence = receipt['active_11_cadence']
    receipt.update(camera_edge_spawn=True, lag_free=False,
                   exact_composed_vectors_SHA256=sha(args.vectors),
                   previous_comparable_missed_reads=502, native_audio=installed_audio)
    receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    notes = out/'release-notes.txt'
    text = notes.read_text()
    text += ('\nFaster decoding of the shared Rygar/Mini ground music, preserving its ordered voice writes '
             'and required status updates. Character audio transitions and interrupt continuations are qualified. '
             f'The same 1-1 controller recorded {cadence["no_controller_read"]} missed reads '
             f'over {cadence["physical"]} physical frames and {cadence["updates"]} updates; '
             'the prior build recorded 502/3568/3453. Exact Downloads audio trace matches the candidate. '
             'Busy-stage lag remains. Thomas/Goku/Karnov camera changes remain private.\n')
    notes.write_text(text)
    print(json.dumps(dict(delivered=True, ROM_SHA256=pin,
                          IPS_SHA256=receipt['IPS_SHA256'], cadence=cadence)), flush=True)


if __name__ == '__main__':
    main()

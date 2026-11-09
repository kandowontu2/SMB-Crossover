"""Deliver the qualified body/box/girder successor through the Downloads guard."""
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
              '--previous', 'a226894c4f6b97f1b9df248cf1465f1a36037fcc256d8ec703e05d0f077d6746']

    def run(argv):
        result = subprocess.run([sys.executable, '-B', *argv], text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout[-1200:], flush=True)
        assert result.returncode == 0, (argv, result.returncode)

    run(['tools/audit/deliver_mini_lifts_art_1108.py', 'install', *common])
    run([str(out/'downloads-smoke/run.py')])
    run(['tools/audit/deliver_mini_lifts_art_1108.py', 'finalize', *common])
    receipt_path = out/'verified-delivery.json'
    receipt = json.loads(receipt_path.read_text())
    cadence = receipt['active_11_cadence']
    receipt.update(camera_edge_spawn=True, lag_free=False,
                   exact_composed_vectors_SHA256=sha(args.vectors),
                   previous_comparable_missed_reads=636)
    receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    notes = out/'release-notes.txt'
    text = notes.read_text()
    text += ('\nFaster Mini body-box dispatch with unchanged authentication and collision fallback, '
             'plus shared native platform-box and girder-rendering optimizations. '
             f'The same 1-1 controller recorded {cadence["no_controller_read"]} missed reads '
             f'over {cadence["physical"]} active physical frames; the previous build recorded '
             '636 over 3602. Busy-stage lag remains. Mini helpers enter beyond the camera edge. '
             'Thomas/Goku/Karnov camera changes are still private pending their live routes.\n')
    notes.write_text(text)
    print(json.dumps(dict(delivered=True, ROM_SHA256=pin,
                          IPS_SHA256=receipt['IPS_SHA256'], cadence=cadence)), flush=True)


if __name__ == '__main__':
    main()

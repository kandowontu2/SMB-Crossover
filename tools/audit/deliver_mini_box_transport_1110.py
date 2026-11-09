"""Deliver the qualified direct Mini body transport after native regression."""
import argparse
import json
from pathlib import Path

from deliver_helper_camera_render_1110 import bindings, mini_evidence, read, run
from prepare_selected_native_packet_v1 import sha

PREVIOUS = 'f2050c1964b53b4bd3dc2e5f24c2ed688d47ad79a8aef6bb2cfd55e28b3e7e42'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.candidate.resolve(), args.output.resolve()
    pin = sha(root/'candidate.nes')
    proof = read(root/'proof.json')
    assert proof['passed'] and proof['parent_SHA256'] == proof['final_minus_body_SHA256'] == PREVIOUS
    assert proof['candidate_SHA256'] == pin
    bindings(proof['bindings'])
    before = mini_evidence(root/'mini',pin)
    common = ['--candidate',str(root),'--route',str(root/'mini'),
              '--idle',str(root/'native/idle'),'--power',str(root/'native/power'),
              '--fire',str(root/'native/fire'),'--output',str(out),'--previous',PREVIOUS]
    installer = 'tools/audit/deliver_mini_lifts_art_1108.py'
    run([installer,'install',*common])
    run([str(out/'downloads-smoke/run.py')])
    assert mini_evidence(out/'downloads-smoke',pin) == before
    run([installer,'finalize',*common])
    path = out/'verified-delivery.json'
    receipt = read(path)
    assert receipt['Downloads_launch_verified'] and receipt['IPS_roundtrip']
    receipt.update(body_transport_proof_SHA256=sha(root/'proof.json'),
                   native_audio=before['audio'], native_audio_matches_candidate=True,
                   previous_comparable_missed_reads=225,
                   lag_free=before['cadence']['no_controller_read'] == 0,
                   camera_regression_scope='Exact helper routes remain qualified on parent f205. '
                   'This successor changes only bank86 body dispatch and equivalent lifecycle branches; '
                   'foreign owners and composed full-CPU/interrupt continuations are source-qualified. '
                   'Native Mini route and idle/power/fire are repeated on this exact successor.')
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    notes = out/'release-notes.txt'
    text = notes.read_text(encoding='utf-8')
    text += ('\nShorter Mini body-box bank dispatch retains its original frame/owner validation and fallback. '
             f'The replay records {before["cadence"]["no_controller_read"]} missed reads '
             f'over {before["cadence"]["physical"]} physical frames; parent: 225/3488. '
             'Helper camera fixes are retained. Busy-stage zero-lag work remains in progress.\n')
    notes.write_text(text,encoding='utf-8')
    print(json.dumps(dict(delivered=True,ROM_SHA256=pin,IPS_SHA256=receipt['IPS_SHA256'],
                          cadence=before['cadence'])),flush=True)


if __name__ == '__main__':
    main()

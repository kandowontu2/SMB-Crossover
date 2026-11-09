"""Deliver qualified Mini graphics and shared enemy geometry reductions."""
import argparse
import json
from pathlib import Path

from deliver_helper_camera_render_1110 import bindings, mini_evidence, read, run
from prepare_selected_native_packet_v1 import sha

PREVIOUS = '76bd6772112ec63d086865210f4e20f62f59156d182136f23bd627db0df3d811'
KERNEL = Path('build/mini-lift-seen-fast-1110/kernel.bin')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    root, out = args.candidate.resolve(), args.output.resolve()
    pin = sha(root/'candidate.nes')
    proof = read(root/'proof.json')
    assert proof['passed'] and proof['parent_SHA256'] == PREVIOUS and proof['candidate_SHA256'] == pin
    assert len(proof['groups']) == len(proof['component_checks']) == 3
    assert set(proof['groups']) == {'graphics_visibility','enemy_edge','box_core'}
    assert proof['kernel_SHA256'] == sha(KERNEL)
    bindings(proof['bindings'])
    for name in ('mini','native/idle','native/power'):
        ready = read(root/name/'ready.json')
        assert ready['bindings'][str(KERNEL.resolve())] == sha(KERNEL)
        assert ready['ROM_sha256'] == pin
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
    receipt.update(composed_proof_SHA256=sha(root/'proof.json'),kernel_SHA256=sha(KERNEL),
                   native_audio=before['audio'],native_audio_matches_candidate=True,
                   previous_comparable_missed_reads=49,
                   lag_free=before['cadence']['no_controller_read'] == 0)
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    notes = out/'release-notes.txt'
    text = notes.read_text(encoding='utf-8')
    text += ('\nFaster Mini graphics dispatch plus shared enemy offscreen and collision box work, '
             'with original movement and gameplay outputs preserved. '
             f'The replay records {before["cadence"]["no_controller_read"]} missed reads '
             f'over {before["cadence"]["physical"]} physical frames; parent: 49/3458. '
             'Camera-based helpers remain verified. Zero-lag work is still in progress.\n')
    notes.write_text(text,encoding='utf-8')
    print(json.dumps(dict(delivered=True,ROM_SHA256=pin,IPS_SHA256=receipt['IPS_SHA256'],
                          cadence=before['cadence'])),flush=True)


if __name__ == '__main__':
    main()

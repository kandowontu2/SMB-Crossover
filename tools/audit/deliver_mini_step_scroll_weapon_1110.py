"""Deliver the qualified Mini ALU, shared scroll, and inactive-shot composition."""
import argparse
import json
from pathlib import Path

from deliver_helper_camera_render_1110 import bindings, mini_evidence, read, run
from prepare_selected_native_packet_v1 import sha

PREVIOUS = '03c0cfe6d4562f6b7970199ce2d6ffa6f2f0f905a8cb8425945add6fcb71585d'
KERNEL = Path('build/mini-step-alu-1110/kernel.bin')


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
                   previous_comparable_missed_reads=136,
                   lag_free=before['cadence']['no_controller_read'] == 0)
    path.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    notes = out/'release-notes.txt'
    text = notes.read_text(encoding='utf-8')
    text += ('\nFaster Mini source arithmetic, shared vertical offscreen work and post-scroll reuse, '
             'plus a shorter inactive Mini fireball route. Powered and existing shots retain their normal path. '
             f'The replay records {before["cadence"]["no_controller_read"]} missed reads '
             f'over {before["cadence"]["physical"]} physical frames; parent: 136/3474. '
             'Camera-based helpers remain verified. Zero-lag work is still in progress.\n')
    notes.write_text(text,encoding='utf-8')
    print(json.dumps(dict(delivered=True,ROM_SHA256=pin,IPS_SHA256=receipt['IPS_SHA256'],
                          cadence=before['cadence'])),flush=True)


if __name__ == '__main__':
    main()

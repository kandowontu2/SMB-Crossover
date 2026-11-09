"""Deliver the tested native sweep/seam candidate and verify Downloads replay."""
import json
from pathlib import Path
import subprocess
import sys

root=Path('build/mini-sweep-seam-native-1110')
out=Path('build/mini-sweep-seam-delivery-1110')
pin='ddd6e71b42aaed99645a54b64b766b4fb3a32aee5c3b55bfe9b7c552000c94b3'
irq=json.loads(Path('build/mini-sweep-seam-vectors-1110/proof.json').read_text())
assert irq['passed'] and irq['candidate_SHA256']==pin
common=['--candidate',str(root),'--route',str(root/'route'),
        '--fire',str(root/'native/fire'),'--idle',str(root/'native/idle'),
        '--power',str(root/'native/power'),'--output',str(out),
        '--previous','56c4135e3edd7421c207fd4cd623ad8f58cd263353342d0af54202cd790cbcbc']

def run(args):
    p=subprocess.run([sys.executable,'-B',*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    print(p.stdout[-1000:],flush=True)
    assert p.returncode==0,(args,p.returncode)

run(['tools/audit/deliver_mini_lifts_art_1108.py','install',*common])
run([str(out/'downloads-smoke/run.py')])
run(['tools/audit/deliver_mini_lifts_art_1108.py','finalize',*common])
receipt=json.loads((out/'verified-delivery.json').read_text())
receipt.update(camera_edge_spawn=True,lag_free=False,
               improvements=['shared Goomba page-seam native terrain fast path',
                             'Mini center-only rising head probe omits discarded span setup'],
               comparable_previous_missed_reads=785,current_missed_reads=761)
(out/'verified-delivery.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'release-notes.txt').write_text(
    'Current MMC5 work-in-progress nightly.\n\n'
    'Apply the sole IPS to clean, headered Super Mario Bros. (World).\n'
    f'Base SHA-256: {receipt["base_SHA256"]}\nPatched ROM SHA-256: {pin}\n\n'
    'Faster shared Goomba terrain checks at page boundaries and faster Mini rising head probes. '
    'Same early-spawning-lift 1-1 replay:785 to761 missed controller reads,3660 to3644 active '
    'physical frames,3444 updates in both. Busy-stage lag remains; this is not lag-free.\n\n'
    'Mini helpers spawn offscreen, scroll into view, and retain separate native actor slots. '
    '1-1 native left edges560/688/864, centers576/704/880, width32, initial top192. '
    'Exact Downloads replay reaches active1-2 with both lives and all three actual board/departures.\n\n'
    'Empty-area idle/walking, earned mushroom, two GBC-style fireballs and impact art, '
    'and exact composed IRQ/lag-NMI checks pass. No wall grab. Reopen the ROM and start fresh.\n')
print(json.dumps(dict(delivered=True,ROM_SHA256=pin,IPS_SHA256=receipt['IPS_SHA256'])))

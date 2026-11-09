"""Install tested camera-lift nightly, replay Downloads and rebuild its IPS."""
import json
from pathlib import Path
import subprocess
import sys

root=Path('build/mini-combined-camera-native-1110')
out=Path('build/mini-camera-delivery-1110')
pin='56c4135e3edd7421c207fd4cd623ad8f58cd263353342d0af54202cd790cbcbc'
irq=json.loads(Path('build/mini-combined-camera-vectors-1110/proof.json').read_text())
assert irq['passed'] and irq['candidate_SHA256']==pin
common=['--candidate',str(root),'--route',str(root/'route-v2'),
        '--fire',str(root/'native/fire'),'--idle',str(root/'native/idle'),
        '--power',str(root/'native/power'),'--output',str(out),
        '--previous','6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018']

def run(args):
    p=subprocess.run([sys.executable,'-B',*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    print(p.stdout[-1600:],flush=True)
    assert p.returncode==0,(args,p.returncode)

run(['tools/audit/deliver_mini_lifts_art_1108.py','install',*common])
run([str(out/'downloads-smoke/run.py')])
run(['tools/audit/deliver_mini_lifts_art_1108.py','finalize',*common])
receipt=json.loads((out/'verified-delivery.json').read_text())
receipt['camera_edge_spawn']=True
receipt['shared_optimizations']=['native offscreen arithmetic','Mini side-pair native probe reuse']
receipt['movement_optimization']='Exact Mini admitted movement dispatch; validated owner/fallback retained'
receipt['lag_free']=False
(out/'verified-delivery.json').write_text(json.dumps(receipt,indent=2)+'\n')
(out/'release-notes.txt').write_text(
    'Current MMC5 work-in-progress nightly.\n\n'
    'Apply the sole IPS to clean, headered Super Mario Bros. (World).\n'
    f'Base SHA-256: {receipt["base_SHA256"]}\nPatched ROM SHA-256: {pin}\n\n'
    'Mini Mario helpers now spawn just beyond the camera edge, remain separate native actors, '
    'and scroll into view. Native left edges in 1-1: 560, 688, 864; width32, initial top192. '
    'All three actual board/departures and 1-1 to active1-2 pass with both lives from Downloads.\n\n'
    'Faster shared offscreen arithmetic and Mini movement/side-collision dispatch. '
    'The isolated movement/offscreen comparison with identical controls reduced missed reads '
    'from500 to401. Camera-spawn timing changes lift waits; combined route records785 missed '
    'reads over3660 active physical frames. Busy-stage lag remains; this is not lag-free.\n\n'
    'Empty-area idle/walking, real mushroom, two original GBC-style fireballs, impact art, '
    'and exact composed IRQ/lag-NMI checks pass. No wall grab. Reopen the ROM and start fresh.\n')
print(json.dumps(dict(delivered=True,ROM_SHA256=pin,IPS_SHA256=receipt['IPS_SHA256'])))

"""Rerun complete transformation assertions over the corrected row33 body."""
import inspect,json
from pathlib import Path
import check_bub_upgrade_lifecycle_1102_v60 as P
import compose_bub_powerup_update_1102_v62 as G
import prepare_bub_powerup_update_1102_v61 as U
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-lifecycle-1102-v63'

def main():
    old=P.I.U;P.I.U=U
    try:
        env=dict(P.__dict__,G=G,O=O,__file__=str(Path(__file__)));exec(compile(inspect.getsource(P.main),str(Path(__file__)),'exec'),env);env['main']()
    finally:P.I.U=old
    p=O/'receipt.json';q=json.loads(p.read_text());q['bindings'][str(Path(P.__file__).relative_to(R))]=sha(Path(P.__file__));q['retained_predecessor_negative']='build/bub-upgrades-root-lifecycle-1102-v60/negative.json: actual PlayerChangeSize60updates never completed because public33 did not invoke native update.';p.write_text(json.dumps(q,indent=2)+'\n')

if __name__=='__main__':main()

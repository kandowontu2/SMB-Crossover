"""Retain complete native transformation assertions after native tail repair."""
import inspect,json
from pathlib import Path
import check_bub_upgrade_lifecycle_1102_v60 as P
import compose_bub_tail_gateways_1102_v66 as G
import prepare_bub_tail_gateways_1102_v65 as U
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-lifecycle-1102-v67'
def main():
    old=P.I.U;P.I.U=U
    try:
        env=dict(P.__dict__,G=G,O=O,__file__=str(Path(__file__)));exec(compile(inspect.getsource(P.main),str(Path(__file__)),'exec'),env);env['main']()
    finally:P.I.U=old
    p=O/'receipt.json';q=json.loads(p.read_text());q['bindings'][str(Path(P.__file__).relative_to(R))]=sha(Path(P.__file__));p.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()

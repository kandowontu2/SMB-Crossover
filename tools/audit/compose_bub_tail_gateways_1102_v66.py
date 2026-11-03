"""Memory composition of native tail callbacks and the joint rare classifier."""
import json
from pathlib import Path
import compose_bub_powerup_update_1102_v62 as G
import prepare_bub_tail_gateways_1102_v65 as U
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-composition-1102-v66'
def bundles():
    previous=G.U;G.U=U
    try:return G.bundles()
    finally:G.U=previous
def main():
    O.mkdir(exist_ok=True);_,_,_,q=bundles();out=dict(passed=True,ROM_written=False,installed=False,parent_ROM_SHA256=U.PIN,expected_memory_only_ROM_SHA256=q['expected_memory_only_ROM_SHA256'],bindings={str(f.relative_to(R)):sha(f) for f in [Path(__file__),G.O/'proposal.json',U.O/'proposal.json',U.O/'private-image.bin']})
    (O/'proposal.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

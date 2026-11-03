"""Joint rare native gate over the complete pickup+animation private body."""
import json
from pathlib import Path
import compose_bub_collecting_gate_1102_v57 as G
import prepare_bub_powerup_update_1102_v61 as U
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-composition-1102-v62'

def bundles():
    previous=G.U;G.U=U
    try:return G.bundles()
    finally:G.U=previous

def main():
    O.mkdir(exist_ok=True);_,_,_,q=bundles()
    out=dict(passed=True,ROM_written=False,installed=False,parent_ROM_SHA256=U.PIN,expected_memory_only_ROM_SHA256=q['expected_memory_only_ROM_SHA256'],body_proposal=str((U.O/'proposal.json').relative_to(R)),scope='Memory-only exact joint3-span rare gate over corrected row24+33 body; requires successor qualification.',bindings={str(f.relative_to(R)):sha(f) for f in [Path(__file__),G.O/'proposal.json',U.O/'proposal.json',U.O/'private-image.bin']})
    (O/'proposal.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))

if __name__=='__main__':main()

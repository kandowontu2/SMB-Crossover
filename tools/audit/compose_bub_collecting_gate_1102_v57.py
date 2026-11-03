"""Memory-only composition of collecting24 and the qualified joint gate."""
import json
from pathlib import Path
import check_bub_original_upgrades_1102_v49 as Q
import prepare_bub_collecting_upgrades_1102_v56 as U
import prepare_bub_joint_rare_gate_1102_v54 as G
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/bub-upgrades-root-composition-1102-v57'
def bundles():
    previous=Q.U;Q.U=U
    try:old,new,route,body=Q.bundles()
    finally:Q.U=previous
    gate=json.loads((G.O/'proposal.json').read_text());assert gate['passed']and gate['foreign_exact_AXYP_SP_and_target_cases']==130048
    for name,h in gate['bindings'].items():assert sha(R/name)==h,name
    raw=bytearray(new['raw'])
    for row in gate['patches']:
        at=row['file_offset'];before=bytes.fromhex(row['old']);after=bytes.fromhex(row['new']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
    return old,dict(new,raw=bytes(raw)),route,{**body,'expected_memory_only_ROM_SHA256':Q.L.P.sha(raw)}
def main():
    O.mkdir(exist_ok=True);old,new,route,q=bundles();out=dict(passed=True,ROM_written=False,installed=False,parent_ROM_SHA256=U.PIN,expected_memory_only_ROM_SHA256=q['expected_memory_only_ROM_SHA256'],body_proposal=str((U.O/'proposal.json').relative_to(R)),gate_proposal=str((G.O/'proposal.json').relative_to(R)),scope='Reuse exact qualified14B-joint-gate behavior in actual3source-funded spans over new owning-collector body; every preimage matches. No carrier/shared instruction/menu outside declared changes, no cartridge emission or native-ready claim.',bindings={str(p.relative_to(R)):sha(p)for p in[Path(__file__),U.O/'proposal.json',U.O/'private-image.bin',G.O/'proposal.json']})
    (O/'proposal.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

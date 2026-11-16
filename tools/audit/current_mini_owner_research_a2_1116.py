"""Typed currenta2 input→versioned1327 reference; never a combined candidate."""
from pathlib import Path
from functools import lru_cache
import compose_sonic_ceiling_complete_1327_1116 as Sonic
import compose_mini_weapon_owner_1116 as Mini

PIN=Sonic.CANDIDATE
SONIC_SHA='c4456eb759fd35f48022fee64a24b05e37b4968a1ddaf139dceebad154187413'
GRANT=Mini.R/'docs/qa/allocations/mini-weapon-owner-identity-correction-root-1116.json'
GRANT_SHA='cacd271568ed7f9a4d55bde9c895433c0cd709549aa443826f61f19e4fa6b5ec'

@lru_cache(maxsize=1)
def reference(raw):
    assert isinstance(raw,bytes)and Mini.H(raw)==PIN,'Exact a2 current reader only'
    assert Mini.H(Path(Sonic.__file__).read_bytes())==SONIC_SHA and Mini.H(GRANT.read_bytes())==GRANT_SHA
    parent=Sonic.inverse(raw);assert Mini.H(parent)==Mini.PARENT
    return parent

def metadata(raw):
    parent=reference(raw);at=Mini.Plan.Previous.Current.CODE_AT
    assert raw[at:at+7168]==parent[at:at+7168]and raw[16+79*8192:16+80*8192]==parent[16+79*8192:16+80*8192]
    return dict(actual_input_SHA256=PIN,versioned_reference_SHA256=Mini.PARENT,versioned_execution_SHA256=Mini.CANDIDATE,
        Sonic_inverse_SHA256=SONIC_SHA,correction_SHA256=GRANT_SHA,Mini7168_native79_exact=True,
        current_a2_execution_claim=False,combined_latest_candidate=False,outputs=0)

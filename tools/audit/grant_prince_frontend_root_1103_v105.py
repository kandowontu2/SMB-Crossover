"""Approve the exact current Prince frontend for private emulator validation."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/prince-frontend-root-1103-v105'
D=R/'docs/qa/allocations/prince-current-frontend-1103-v105.json'
def main():
    O.mkdir(exist_ok=True);p=R/'build/prince-actor-1101-v1';front=p/'frontend-proposal-v137.json';q=json.loads(front.read_text());manifest=p/'strike-manifest-v130.json';m=json.loads(manifest.read_text())
    assert q['passed']and q['exact_frozen109_nine_spans_rebound']and q['total_changed_bytes']==26 and len(q['patches'])==9
    assert q['unique_named_profiles']==93 and q['actual_named_states']==94 and q['foreign_Start_A_pairs']==186 and q['actual_Select_confirm_cases']==282
    assert q['all256_FmAlts_all32_Start_mask_cases']==8192 and q['resolver_entry_X29_iff_menuindex29']
    assert m['parent_memory_SHA256']=='cf7f157aa39493149b24039c190f09244ce68bc47f0a87f06f01adb47a2c70dd'
    assert q['parent_memory_SHA256']==m['expected_memory_only_SHA256']=='cba497aabf91ccb357a9392a4407f261c8fd33a66032ae9d7b2e1ba790ef490d'
    assert q['expected_memory_only_SHA256']=='b684ff8aaf52aaf41f668e272f9e28704463f8cde50c9254445ec96881a451e1'
    for proof in[q,m]:
        for name,h in proof['bindings'].items():assert sha(R/name)==h,name
    raw=bytearray((R/m['parent_input']).read_bytes())
    for patch in m['patches']:
        at=patch['file_offset'];old=bytes.fromhex(patch['old_hex']);new=bytes.fromhex(patch['new_hex']);assert raw[at:at+len(old)]==old;raw[at:at+len(old)]=new
    import hashlib
    assert hashlib.sha256(raw).hexdigest()==m['expected_memory_only_SHA256']
    patches=[];changed=0
    for patch in q['patches']:
        at=patch['file_offset'];old=bytes.fromhex(patch['old_hex']);new=bytes.fromhex(patch['new_hex']);assert len(old)==len(new)and raw[at:at+len(old)]==old
        patches.append({k:patch[k]for k in['physical_PRG','CPU_half_open','file_offset','old_hex','new_hex']});raw[at:at+len(old)]=new;changed+=sum(a!=b for a,b in zip(old,new))
    assert changed==26 and hashlib.sha256(raw).hexdigest()==q['expected_memory_only_SHA256']
    grant=dict(status='APPROVED_EXACT_PRIVATE_NATIVE_CANDIDATE_ONLY',granted=True,owner='Prince of Persia raw38, Excitebike Select alternate',reviewed_parent_ROM_SHA256=m['parent_memory_SHA256'],reviewed_component_memory_SHA256=m['expected_memory_only_SHA256'],expected_candidate_SHA256=q['expected_memory_only_SHA256'],approved_exact_patches=patches,total_changed_frontend_bytes=26,new_allocated_bytes=0,new_RAM_bytes=0,private_candidate_menu_admission_authorized=True,nightly_installation_authorized=False,review='Root inspected the actual21B X29 resolver, unchanged FmPending/name atlas authority,25to26 ready cutoff and source-funded74B family-mask function. Both terminalEA bytes fund only the relocated group tail/fallback zero; no address/span growth. Existing Prince diamond becomes blank. Actual93profiles/94states,186foreignconfirms/282Selectconfirm/8192masks preserve all other identities. Root independently composes every existing component and frontend preimage in memory to the exact b684 hash.',conditions=['Use precisely these nine frontend spans and the source-bound130 component manifest. Preserve all current cf7 Bub/head/initial-tier/menu-family and other owner payloads outside the explicit patches.','Require current135 lifecycle-ISR and136 actual nested-IRQ passes plus current fullcold/foreign/earned-strike/death-respawn receipts before emitting this candidate.','Run native cold menu/lives, idle/walk/jump/strike/contact/death and hardware assertions under the single root Mesen queue. No active state injection.','No claim of 1-1, helper crossings, original audio or all upgrades until actual respective tests pass. Root must review native results before nightly replacement.'],bindings={f.relative_to(R).as_posix():sha(f)for f in[Path(__file__),front,manifest,p/'frontend-source-CPU-v113.json',R/'docs/qa/allocations/prince-post-return-lifetime-1102-v70.json',R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json']})
    D.write_text(json.dumps(grant,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(grant,indent=2)+'\n');print(json.dumps({k:v for k,v in grant.items()if k not in['bindings','review','approved_exact_patches']}))
if __name__=='__main__':main()

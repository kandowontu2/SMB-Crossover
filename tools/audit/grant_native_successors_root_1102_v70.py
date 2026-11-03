"""Root-reviewed private native ingress/lifetime grants; no cartridge emission."""
import hashlib,json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/native-successor-root-grants-1102-v70'

def bound(path):
    q=json.loads(path.read_text());assert q['passed']
    for f,h in q['bindings'].items():assert sha(R/f)==h,f
    return q

def main():
    O.mkdir(exist_ok=True);base=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes');raw=base.read_bytes();assert sha(base)=='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'
    source=(R/'build/karnov-host-resource-base-1101-v1/new_roster_dispatch.s').read_text()
    assert ' jmp GmMatureGate\n .res 15,$ea\nOwn:' in source and ' jmp GmPickupGate\n .res 15,$ea\nIce:' in source
    gate_path=R/'build/bub-upgrades-root-gate-1102-v54/proposal.json';g=bound(gate_path)
    assert g['all_native_classifier_cases']==131072 and g['foreign_exact_AXYP_SP_and_target_cases']==130048
    assert [r['CPU_half_open'] for r in g['patches']]==[[0xa2be,0xa2c2],[0xa7ca,0xa7d5],[0xa81f,0xa824]]
    for p in g['patches']:
        at=p['file_offset'];old=bytes.fromhex(p['old']);assert raw[at:at+len(old)]==old
    gate=dict(status='APPROVED_PRIVATE_SOURCE_COMPOSITION_AND_NATIVE_TEST_ONLY',owners=['Prince of Persia raw38','Bub/Bob raw39'],reviewed_base_SHA256=sha(base),proposal=gate_path.relative_to(R).as_posix(),proposal_SHA256=sha(gate_path),approved_exact_patches=g['patches'],supersedes_for_joint_composition='docs/qa/allocations/prince-native-rare-gate-1102-v64.json',review='Root read actual NrPickupCollision/NrPickup unconditional source tails and current classifier instructions. All proposal bindings/preimages match;131072 actual ingress cases preserve complete internal target+AXYP/SP for130048 foreign cases and deliberately admit only38/39. Each rejected value repeats original CMP37 to retain internalNZ/C. Both source tails retain original Own/Ice entries; no new RAM/carriers/menu entries.',conditions=['Use exactly4+11+5 bytes; retain all other tail bytes/downstream PCs and current Sunny/menu bytes.','This supersedes the older38-only14byte veneer for a joint image; never apply both overlapping variants.','Owner lifecycle/header/readback/IRQ/native gameplay must pass on the exact composed image before installation.','No permission for a new character unlock, broad shared manager rewrite or installation is implied.'],installation_authorized=False,menu_admission_authorized=False)
    gate_dest=R/'docs/qa/allocations/joint-native-rare-gate-1102-v70.json'
    if gate_dest.exists():assert json.loads(gate_dest.read_text())==gate
    else:gate_dest.write_text(json.dumps(gate,indent=2)+'\n')
    pp=R/'build/prince-actor-1101-v1';path=pp/'post-return-lifetime-proposal-v91.json';p=bound(path)
    assert p['interrupt_proof']['real_IRQ']==1846 and p['interrupt_proof']['actual_FF_lag_NMI']==1846 and p['interrupt_proof']['nested_lag_IRQ_cases']==6690
    assert p['physical_resources']==dict(existing_pages=44,new_pages=0,capacity=45056,payload_bytes=44472,spare_bytes=584)
    assert p['requested_existing_exclusive_RAM2_half_open']==dict(synchronous_gateway_packet=[0xc200,0xc20d],live_audio_extension=[0xc766,0xc780],cold_prefix_PC_extension=[0xc678,0xc67a],metadata_extension=[0xdfce,0xdfcf])
    assert not p['original_reader_closure']['direct_766_800'] and not p['original_reader_closure']['packet_direct_and_all256_index_aliases']
    for row in p['exact_shared_hook_patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);assert raw[at:at+len(old)]==old
    receipt=json.loads((pp/'post-return-checkpoint-v95.json').read_text());assert receipt['passed'];archive=pp/'post-return-source-v95.zip';assert sha(archive)==receipt['checkpoint_SHA256']
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==122
        for name in z.namelist():
            live=pp/name.removeprefix('generated/') if name.startswith('generated/') else R/name
            assert live.is_file() and z.read(name)==live.read_bytes(),name
    dest=R/'docs/qa/checkpoints/2026-11-02/prince-post-return-v95';assert not dest.exists();dest.mkdir()
    for f,name in [(archive,'inputs.zip'),(pp/'post-return-checkpoint-v95.json','receipt.json')]:
        (dest/name).write_bytes(f.read_bytes());assert sha(dest/name)==sha(f)
    grant=dict(status='APPROVED_CONDITIONAL_PRIVATE_SOURCE_COMPOSITION_ONLY',owner='Prince of Persia raw38',proposal=path.relative_to(R).as_posix(),proposal_SHA256=sha(path),checkpoint=dest.relative_to(R).as_posix(),reviewed_current_hook_preimages_SHA256=sha(base),approved_exclusive_RAM2_lifetimes=p['requested_existing_exclusive_RAM2_half_open'],approved_exact_PRG124_hook_patches=p['exact_shared_hook_patches'],new_carrier_pages=0,review='Root read exact source-dead execution/prefix/palette extension, finite original indexed/immutable-script reader bounds and synchronous13byte packet lifetime; verified every proposal binding and all122 frozen members. Native post-return hook occupies source15EA tails after unconditional GmRise/GmPrivate gates, preserves displacedSTA and every foreignAXYP/SP case. Deepest actual IRQ, genuine FF lag and nestedIRQ receipts pass on their declared historical source-injected fixture, with precise native07DA async allowance. They do not establish a current-image shared cold/respawn.',conditions=['Apply only these four exclusive lifetimes and exact25+3 hook bytes; prior44carrier ownership/headers/DFD0clock remain unchanged.','C200..C20D packet is foreground synchronous only: no original/native Draw or gateway reentry until savedR0..7 and all5SMC bytes restore. Genuine Draw overwrites consumed sprite packet before renderer.','C65F..C67A prefix runs only forcedblank/SEI/disabledNMI/invalidheaders before constructor; copy+verify154B C766..C800. Preserve all genuinely live original state; publish headers last.','Use0179 transport operand only within existing five-byte SMC save/restore lifetime and consume tag before any nested rewrite.','Rebase current9cf or an explicitly tested successor, joint rare gate, final Bub cookie/body and Ex37 cold carry fix. Historical16a9/v65 fixture is not a current-image claim.','Full actual shared cold/auth/foreign retirement/death/respawn/IRQ/native mechanics and1-1 remain required; original audio mapping remains unfinished.','No ROM emission, menu admission or installation authorized by this private grant.'],ROM_emission_authorized=False,menu_admission_authorized=False,installation_authorized=False)
    pd=R/'docs/qa/allocations/prince-post-return-lifetime-1102-v70.json';assert not pd.exists();pd.write_text(json.dumps(grant,indent=2)+'\n')
    out=dict(passed=True,ROM_written=False,grants={str(f.relative_to(R)):sha(f) for f in [gate_dest,pd]},frozen_Prince_members=122,checkpoint=dest.relative_to(R).as_posix());(O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()

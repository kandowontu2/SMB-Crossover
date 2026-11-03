"""Reserve only source-reviewed Mini carriers and the exclusive overlay."""
from pathlib import Path
import hashlib
import json
import build_storage_guard_v1 as G

R=Path(__file__).resolve().parents[2]
O=R/'build/mini-mario-resource-root-1103-v24'
A=R/'docs/qa/allocations/mini-mario-private-resources-1103-v24.json'
sha=lambda b:hashlib.sha256(b).hexdigest()


def main():
    G.preflight(private_root=O,reserved_bytes=20000,reserved_files=1,fresh=True)
    O.mkdir(exist_ok=False)
    p=R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json'
    q=json.loads(p.read_text());assert q['passed'] and not q['resource_granted'] and not q['ROM_written']
    for name,h in q['bindings'].items():assert sha((R/name).read_bytes())==h,name
    raw=(R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes').read_bytes()
    assert sha(raw)==q['current_ROM_SHA256']=='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
    pages=set(range(962,969));assert q['proposed_code']==list(range(962,967))
    assert q['proposed_immutable']==967 and q['proposed_art']==968
    assert not any(pages&set(values) for values in q['exact_finite_domains'].values())
    assert q['inherited_native_writer_instructions_exact']==802
    assert len(q['source_relocated_helper_writers'])==10 and len(q['retired_Arthur_writers'])==4
    assert len(q['inherited_private_writer_chunks_exact'])==15 and q['current_DK_replacement_pages_exact']==11
    assert q['current_shared_cold_worker_exact']
    for row in q['preimages']:
        assert row['page'] in pages and row['bytes']==1024
        assert row['file_offset']==1048592+row['page']*1024
        assert sha(raw[row['file_offset']:row['file_offset']+1024])==row['SHA256']
    grant=dict(granted=True,status='CONDITIONAL_PRIVATE_CARRIERS_AND_OVERLAY_ONLY',
        owner='Mini Mario original source port',raw_identity_reserved=41,
        reviewed_parent_SHA256=q['current_ROM_SHA256'],code_pages=list(range(962,967)),
        immutable_page=967,art_page=968,physical_preimages=q['preimages'],
        conditional_RAM=dict(code_bank3_half_open=[0xa000,0xbfe0],
            original_motion_world_and_query_bank2_half_open=[0xc200,0xc2ea],
            host_bank2_half_open=[0xc300,0xc340],metadata_bank2_half_open=[0xd000,0xd400],
            headers=[0xbfe0,0xdfe0],shared_clock_retained=[0xdfd0,0xdfd3]),
        review='Root inspected the finite962..968 source hole, current native/descriptor/CHR tables and inherited writer closure. No blank-byte assumption: all existing Prince44/Bub9/DK11 domains, historical FF893..900, Benjamin901..914, SMB3Plus969..1018 and Karnov1019..1023 remain occupied. Exact802 inherited writer instructions,10 source-relocated WWF writes,4 explicitly retired Arthur883 writes and15 private writer chunks are bound to actual80d3.',
        conditions=[
            'Exclusive bank2/3 owner. Retire foreign owners and invalidate both headers before copying; never overwrite live other-owner state. Publish both complete payload-derived16B headers after copy/readback under the established forcedblank/disabledNMI/IRQ protocol.',
            'At most5120 code bytes across962..966. Metadata967 must keep D25E cold copier separate from animation indices D000..D160, framesD160..D239 and native attributesD300..D400. Art968 retains the exact original1024-byte Mini atlas.',
            'No shared PRG/selector/manager/bootstrap, public raw41/menu or nightly approval is inferred. Final source-fit/full-header/private-to-native ABI/current foreign/lifecycle/IRQ proofs and actual native checks remain required.',
            'Native first1-1 build retains original ground/jump/fall/crouch/skid source motion. Wall cling/jump, if included, is an explicit user-authorized host traversal adaptation; verify real crossings. Do not invent platform visuals or claim source actors/swim/climb already ported.',
            'Root alone emits candidate, runs Mesen, installs Downloads without backups, verifies actual Downloads context and updates the sole Current IPS.'
        ],shared_bytes_granted=0,ROM_emission_authorized=False,menu_admission_authorized=False,
        installation_authorized=False,bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in[
            Path(__file__),R/'build/mini-mario-owner-1103-v15/carrier-audit-v16.json',
            R/'docs/qa/allocations/combined-owner-auth-1103-v116.json']})
    assert not A.exists();A.write_text(json.dumps(grant,indent=2)+'\n')
    (O/'receipt.json').write_text(json.dumps(grant,indent=2)+'\n')
    print(json.dumps(dict(granted=True,code=grant['code_pages'],metadata=967,art=968,ROM_written=False)))


if __name__=='__main__':main()

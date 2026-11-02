"""Record reviewed Prince carriers and rebind the disjoint Bub grant to cf.

This writes allocation metadata only, never ROM bytes or menu admission.
"""
import hashlib
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/prince-resources-1102-v1'
P = R / 'build/prince-actor-1101-v1'
E = R / 'build/excitebike-pose-1101-v3'
BASE = R / 'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes'
CURRENT = E / 'current4.nes'
OLD = 'd8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
POOL = sorted({*range(341, 356, 2), 357, 359, 361, 365, 369, 373, 377,
               *range(381, 394, 2), 544, 545, *range(605, 628, 2),
               690, 691, 692, 693, 695, 795})


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def bound(name):
    path = P / name
    q = read(path)
    assert q['passed'], name
    for p, digest in q.get('bindings', {}).items():
        assert sha(R / p) == digest, (name, p)
    return q


def main():
    O.mkdir(exist_ok=True)
    assert sha(BASE) == OLD and sha(CURRENT) == PIN
    old, current = BASE.read_bytes(), CURRENT.read_bytes()
    composition = read(E / 'current4-composition.json')
    assert composition['passed'] and composition['base_ROM_SHA256'] == OLD
    assert composition['ROM_SHA256'] == PIN and composition['all_foreign_ROM_exact']
    delta = [dict(offset=i, old=a, new=b) for i, (a, b) in enumerate(zip(old, current)) if a != b]
    assert len(old) == len(current) and delta == composition['delta'] and len(delta) == 175
    cookie_start = 16 + 65 * 8192 + 0x1016
    code_start = 1048592 + 728 * 1024
    assert all(cookie_start <= d['offset'] < cookie_start + 16 or
               code_start <= d['offset'] < code_start + 6144 for d in delta)
    # The heat patch only extends the original source timer/lane/throttle
    # phases. Its publication services, resident entries, art and metadata
    # remain identical; finite art domains therefore remain unchanged.
    for name in ['heat-assembly.json', 'heat-CPU.json', 'heat-ISR-CPU.json']:
        q = read(E / name)
        assert q['passed'] and q['memory_candidate_SHA256'] == PIN
        for p, digest in q['bindings'].items():
            assert sha(R / p) == digest, (name, p)

    proposal = bound('pool-proposal.json')
    layout = bound('pooled-layout.json')
    publication = bound('publication-CPU-controls.json')
    for name in ['writer-preservation.json', 'new-owner-pages.json', 'smb3-pages.json',
                 'replacement-pages.json']:
        bound(name)
    assert proposal['ROM_sha256'] == OLD and proposal['complete_publication_retest']
    assert proposal['proposed_physical_CHR_pages'] == POOL and len(POOL) == 42
    assert publication['current_ROM_sha256'] == OLD
    assert publication['proposed_pages'] == POOL and publication['no_proposed_page_published']
    assert layout['source_payload_bytes'] == 42579 and layout['pool_bytes'] == 43008
    assert layout['max_body_read_end'] == 31072
    assert layout['source_facing_packets'] == 408 and layout['actual_body_pair_reads_checked'] == 2578
    assert sha(P / 'pooled-source.bin') == layout['payload_sha256']

    bub_path = R / 'docs/qa/allocations/bubble-bobble-1102-v1.json'
    bub = read(bub_path)
    bub_pages = [p['page'] for p in bub['physical_CHR_pages']]
    assert bub['granted'] and bub['base_ROM_SHA256'] == OLD and not set(bub_pages) & set(POOL)
    preimages = {row['page']: row['preimage_sha256'] for row in proposal['preimages']}
    pages = []
    for page in POOL + bub_pages:
        offset = 1048592 + page * 1024
        assert current[offset:offset + 1024] == old[offset:offset + 1024]
        digest = hashlib.sha256(current[offset:offset + 1024]).hexdigest()
        if page in POOL:
            assert digest == preimages[page], page
            pages.append(dict(page=page, file_offset=offset, bytes=1024, preimage_SHA256=digest))

    grant = dict(granted=True, owner='Prince of Persia original actor component', date='2026-11-02',
                 base_ROM_SHA256=PIN, existing_consumer_proof_ROM_SHA256=OLD,
                 physical_CHR_pages=pages, logical_to_physical_page_order=POOL,
                 packed_layout=layout['packed_regions'], physical_spare_bytes=429,
                 conditional_RAM=dict(code_bank=3, code_body_half_open=[0xa000, 0xbfe0],
                                      state_bank=2, original_state_half_open=[0xc000, 0xc800],
                                      pose_metadata_half_open=[0xc800, 0xdd32],
                                      headers=[[0xbfe0, 0xbff0], [0xdfe0, 0xdff0]],
                                      shared_clock_mailbox_DFD0_DFD2_retained=True,
                                      unconditional_RAM=False),
                 conditions=[
                     'Exclusive overlay with all current bank2/3 owners, including Excitebike and Bub/Bob.',
                     'Authenticate full headers; retire foreign owners before writes and publish headers only after complete copy and verification.',
                     'Cold CHR reads require the existing forced-blank/publication protocol and restoration of source mapper state.',
                     'Translate every logical art page through the granted physical map; at most three independent body sprite windows.',
                     'Only the 31072-byte body region is sprite art. The last body page also contains code, outside every proved legal body-pair read.',
                     'Only 429 physical bytes remain before compression or another reviewed allocation. Runtime address-space spare is not ROM storage.',
                     'The 20 fixture environment callbacks must be replaced by actual host services before native execution.',
                     'Resident PRG/bootstrap, shared dispatch, identity admission and menu confirmation require separate measured integration.'
                 ],
                 resident_PRG_granted=False, shared_router_granted=False,
                 raw_identity_reserved=38, menu_admission_granted=False,
                 host_ROM_changed=False, native_playable=False,
                 evidence={name: sha(P / name) for name in [
                     'pool-proposal.json', 'pooled-layout.json', 'writer-preservation.json',
                     'new-owner-pages.json', 'smb3-pages.json', 'replacement-pages.json',
                     'publication-CPU-controls.json']},
                 current_rebase=dict(changed_bytes=175, only_existing_Ex_code_and_cookie=True,
                                     all_resident_and_foreign_publisher_bytes_retained=True,
                                     composition_SHA256=sha(E / 'current4-composition.json')))
    rebase = dict(granted=True, owner=bub['owner'], original_grant=str(bub_path.relative_to(R)),
                  original_grant_SHA256=sha(bub_path), base_ROM_SHA256=PIN,
                  previous_base_ROM_SHA256=OLD, all_existing_grant_conditions_retained=True,
                  physical_pages_unchanged=bub_pages, disjoint_Prince_pages=POOL,
                  new_PRG_RAM_or_identity_grant=False, host_ROM_changed=False,
                  source_publication_and_cold_loader_bytes_unchanged=True,
                  composition_SHA256=sha(E / 'current4-composition.json'))
    for name, data in [('prince-1102-v1.json', grant), ('bubble-bobble-rebase-1102-v2.json', rebase)]:
        dest = R / 'docs/qa/allocations' / name
        assert not dest.exists(), dest
        dest.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/prince-resource-pool-v1'
    cp.mkdir(parents=True, exist_ok=True)
    for name in list(grant['evidence']) + ['upper2-finite-domains.json']:
        (cp / name).write_bytes((P / name).read_bytes())
    (O / 'grant.json').write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(granted=True, Prince_pages=42, physical_spare_bytes=429,
                          Bub_rebased=True, resident_granted=False, host_ROM_changed=False)))


if __name__ == '__main__':
    main()

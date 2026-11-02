"""Record the reviewed Bub/Bob carrier and exclusive RAM ownership grant."""
import hashlib
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/bubble-bobble-resources-1102-v1'
SOURCE = R / 'build/bubble-bobble-source-1101-v1'
BASE = R / 'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes'
PIN = 'd8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05'
OLD = '37959000690d3f9fe596823fc0910e86b9fc977448779360d523751764248b0c'
CODE = [301, 305, 337, 362, 363, 440, 819, 666]
ART = [441]


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    O.mkdir(exist_ok=True)
    proof = SOURCE / 'current3-closure-supplement.json'
    assert sha(proof) == '858ccee4febd10a651fbb58b96f9f77bf29eb7cb1695f1a11fcd4ece23faaadc'
    q = read(proof)
    assert q['passed'] and q['existing_candidate_consumer_closure']
    assert q['remaining_existing_finite_publishers'] == 0
    assert q['proposed_code_pages'] == CODE and q['proposed_art_pages'] == ART
    for path, digest in q['bindings'].items():
        assert sha(R / path) == digest, path
    base, previous = BASE.read_bytes(), (R / 'build/excitebike-pose-1101-v3/current3.nes').read_bytes()
    assert sha(BASE) == PIN and hashlib.sha256(previous).hexdigest() == OLD
    delta = [i for i, (a, b) in enumerate(zip(previous, base)) if a != b]
    assert len(base) == len(previous) and delta == [580983, 580984]
    assert base[580983:580985] == bytes.fromhex('92bd')
    pages = []
    for page in CODE + ART:
        offset = 1048592 + page * 1024
        data = base[offset:offset + 1024]
        assert data == bytes(1024)
        assert hashlib.sha256(data).hexdigest() == q['preimage_SHA256'][str(page)]
        pages.append(dict(page=page, bytes=1024, file_offset=offset,
                          purpose='code carrier' if page in CODE else 'sprite art',
                          preimage_SHA256=q['preimage_SHA256'][str(page)]))
    grant = dict(granted=True, owner='Bub/Bob original Bubble Bobble component',
                 date='2026-11-02', base_ROM_SHA256=PIN,
                 existing_consumer_proof_ROM_SHA256=OLD,
                 retained_parent_publisher_bytes=True, parent_delta=delta,
                 physical_CHR_pages=pages, code_page_load_order=CODE,
                 conditional_RAM=dict(code_bank=3, code_body_half_open=[0xa000, 0xbfe0],
                                      state_bank=2, state_half_open=[0xc000, 0xc400],
                                      headers=[[0xbfe0, 0xbff0], [0xdfe0, 0xdff0]],
                                      unconditional_RAM=False,
                                      shared_clock_mailbox_DFD0_DFD2_retained=True),
                 conditions=q['conditional_RAM']['conditions'] + [
                     'Mutually exclusive with every current bank2/3 overlay; no concurrent contents or header ownership.',
                     'New resident loader/authentication/routing requires a separate source-funded grant before any shared ROM edit.',
                     'Do not publish code carrier pages as normal body/background art; cold transfers require the existing forced-blank protocol.',
                     'Header publication follows complete copy and verification; retire every foreign owner before any copy/zero/header writes.',
                     'Compiled service plus update/camera glue must fit the granted body before integration; no full service-fit claim from the partial private component.'
                 ],
                 resident_PRG_granted=False, shared_router_granted=False,
                 raw_identity_granted=False, menu_admission_granted=False,
                 native_playable=False, host_bytes_written=False,
                 evidence=dict(supplement=sha(proof),
                               finite_domains=sha(SOURCE / 'current3-domain-rebind.json'),
                               publication=sha(SOURCE / 'publication-CPU-controls.json')),
                 proof_counts=q['proof_counts'],
                 exclusions=['846 belongs to Parodius pool3 special art.',
                             '667 is the WWF zero carrier.',
                             'No Prince physical page may overlap these nine pages.'])
    destination = R / 'docs/qa/allocations/bubble-bobble-1102-v1.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    assert not destination.exists()
    destination.write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    (O / 'grant.json').write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/bubble-bobble-resources-v1'
    cp.mkdir(parents=True, exist_ok=True)
    for name in ['current3-closure-supplement.json', 'current3-domain-rebind.json', 'publication-CPU-controls.json']:
        (cp / name).write_bytes((SOURCE / name).read_bytes())
    print(json.dumps(dict(granted=True, code_pages=CODE, art_pages=ART,
                          conditional_RAM_only=True, resident_granted=False,
                          playable=False, host_ROM_changed=False)))


if __name__ == '__main__':
    main()

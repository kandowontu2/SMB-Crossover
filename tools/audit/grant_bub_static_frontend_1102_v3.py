"""Grant only the source-proven static menu spans; gameplay stays gated."""
import hashlib
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/bub-static-grant-1102-v3'
P = R / 'build/bub-menu-integration-1102-v1'
ROM = R / 'build/metal-reservation-1102-v42/candidate.nes'
PIN = '1cd8e192ee4bee33dfe0d9c737bec097e1cf2339e0b9f77353fd5194f2530f55'
CF = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def bound(q):
    for p, digest in q.get('bindings', {}).items():
        assert sha(R / p) == digest, p


def main():
    O.mkdir(exist_ok=True)
    assert sha(ROM) == PIN
    freeze = read(P / 'frontend-source-freeze.json')
    art, controls, closure = [read(P / n) for n in ['art-proposal.json', 'controls-proposal.json', 'art-CPU-closure.json']]
    for q in [freeze, art, controls, closure]:
        assert q['passed'] and not q['ROM_written'] and not q['menu_admitted']
        bound(q)
    assert freeze['source_base_SHA256'] == art['base_ROM_SHA256'] == controls['base_ROM_SHA256'] == closure['base_ROM_SHA256'] == CF
    assert sha(R / freeze['checkpoint']) == freeze['checkpoint_SHA256']
    cons, cuts = closure['consumers'], closure['interrupts']
    assert cons['passed'] and cons['actual_existing_profiles'] == 91
    assert not set(cons['name_rows']) & {0, 1, 9, 14}
    assert not set(cons['portrait_rows']) & {9, 14}
    assert cons['inherited_finite_table_rebinds'] == 44 and cons['source_family_page_domains'] == 59
    assert cons['nonmenu_upper2_domains_exclude700']
    for p, digest in cons['inherited_bindings'].items():
        assert sha(R / p) == digest, p
    assert len(cons['existing_screen_builds']) == 4
    assert cuts['passed'] and cuts['actual_new_copy_instruction_state_cuts'] == 2535
    assert cuts['actual_ISR_counts'] == {'NMI_accepted': 2535, 'IRQ_accepted': 5, 'IRQ_masked': 2530}
    assert closure['ingress_interrupts']['actual_changed_instruction_identity_states'] == 1293
    assert art['decoder_full_input_P_cases'] == 256 and art['stream_and_decoder_bytes'] == 501
    assert art['new_stream_bytes'] == 410 and art['decoder_bytes'] == 91
    assert controls['old_profiles'] == 91 and controls['foreign_actual_input_cases'] == 1274
    assert controls['granted_frontend_used_bytes'] == 63 and controls['allocated_bytes'] == 66
    raw = ROM.read_bytes()
    patches = art['requested_patches'] + controls['required_operand_patches']
    spans = []
    for p in patches:
        at, old, new = p['offset'], bytes.fromhex(p['old']), bytes.fromhex(p['new'])
        assert len(old) == len(new) and raw[at:at + len(old)] == old, p['role']
        assert not any(max(at, lo) < min(at + len(old), hi) for lo, hi in spans)
        spans.append((at, at + len(old)))
    # One combined source lease: the old initializer and stream are a single
    # same-bank transaction. The exact source-valid reader domains establish
    # unused art/data; blank bytes alone do not establish ownership.
    grant = dict(granted=True, owner='Bub/Bob static character-select frontend', date='2026-11-02',
        base_ROM_SHA256=PIN, source_proof_base_SHA256=CF,
        rebase='docs/qa/allocations/roster-rebase-1102-v3.json',
        exact_static_patches=patches, allocated_new_PRG_bytes=0, allocated_new_RAM_bytes=0,
        source_funding=dict(unused_FmNames_bytes=64, unused_preview_tile_color_bytes=14,
            unused_static_CHR700_prefix_bytes=96, unused_menu_BG_tile_bytes=64,
            existing_FmPending_entry_bytes=3, existing_PPU_initializer_decoder_bytes=49,
            existing_SelectNameTable_span_bytes=677, stream_bytes=410, transaction_decoder_bytes=91,
            stream_span_spare_bytes=176, existing_Select_confirm_operand_bytes=6),
        evidence=dict(source_profiles=91, full_foreign_input_cases=1274, incoming_P_cases=256,
            copy_ISR_states=2535, menu_ingress_ISR_states=1293, finite_table_rebinds=44, family_page_domains=59),
        prior_grants=['docs/qa/allocations/bub-menu-1102-v1.json', 'docs/qa/allocations/bub-menu-flags-1102-v2.json'],
        conditions=[
            'Apply exact owned preimages over1cd8; retain current Metal, Ex and Arthur payloads and cookies.',
            'Names0/1 and9/14, preview rows9/14 and static CHR700 prefix0..96 are no longer old-data APIs. All live old rows and other art stay exact.',
            'Keep all1024 menu PPU bytes exact except four declared new icon cells and protect PPU initialization/copy with the proven PHP/SEI/PLP boundary.',
            'Do not execute the private cold overlay in OperMode0. Static UI uses only existing native ROM readers.',
            'Preserve both old selectors and simultaneous Select/confirm behavior. The new slot displays normal BUB/BOB names.',
            'Confirmation remains blocked at the exact owned gate until actual backend/native acceptance. Rendering alone is not character playability.',
            'Root must inspect actual native menu pixels, transitions and BT/CF restoration before delivery.'
        ], menu_admitted=False, native_playable=False, host_ROM_changed=False,
        bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), ROM,
            P / 'frontend-source-freeze.json', P / 'art-proposal.json', P / 'controls-proposal.json', P / 'art-CPU-closure.json']})
    dest = R / 'docs/qa/allocations/bub-menu-static-1102-v3.json'
    assert not dest.exists()
    dest.write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/bub-static-frontend-v3'
    cp.mkdir(parents=True, exist_ok=True)
    for src, name in [(R / freeze['checkpoint'], 'inputs.zip'), (P / 'frontend-source-freeze.json', 'manifest.json'),
                      (P / 'art-proposal.json', 'art-proposal.json'), (P / 'controls-proposal.json', 'controls-proposal.json'),
                      (P / 'art-CPU-closure.json', 'CPU-closure.json')]:
        assert not (cp / name).exists()
        (cp / name).write_bytes(src.read_bytes())
    (cp / 'commit-files.txt').write_text('\n'.join(freeze['source_files_to_stage']) + '\n', encoding='utf-8')
    (O / 'grant.json').write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(granted=True, exact_patches=len(patches), new_PRG_or_RAM_bytes=0,
                          source_funded_spare_bytes=176, gameplay_confirmed=False)))


if __name__ == '__main__':
    main()

"""Extend the exclusive Bub overlay with an authenticated art/helper row."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/bubble-helper-grant-1102-v2'
P = R / 'build/bubble-bobble-source-1101-v1'


def main():
    O.mkdir(exist_ok=True)
    proof = P / 'helper-row-proposal.json'
    assert sha(proof) == '15c11612909a3b81e5b953704a3f0bb02b29404ab4b2154e0adfacc737c5ec5c'
    q = json.loads(proof.read_text(encoding='utf-8'))
    assert q['passed'] and q['actual_compiled_tile_input_cases'] == 256
    assert q['source_native_art_cases'] == 140 and len(q['accepted_pairs']) == 25
    assert max(p['physical_art_half_open'][1] for p in q['accepted_pairs']) == 800
    assert q['source_state_write_operands'] == 504 and q['maximum_literal_state_write'] < 0xc400
    for path, digest in q['bindings'].items():
        assert sha(R / path) == digest, path
    grant = dict(granted=True, owner='Bub/Bob original component helper row', date='2026-11-02',
                 base_ROM_SHA256=q['base_ROM_SHA256'],
                 inherited_grant='docs/qa/allocations/bubble-bobble-1102-v1.json',
                 current_rebase='docs/qa/allocations/bubble-bobble-rebase-1102-v2.json',
                 physical_CHR=dict(page=441, original_body_art_half_open=[0, 800],
                                   helper_code_data_half_open=[800, 1024], helper_bytes=224),
                 conditional_RAM=dict(bank=2, copied_art_prefix_half_open=[0xd000, 0xd320],
                                      immutable_helper_half_open=[0xd320, 0xd400],
                                      full_copy_half_open=[0xd000, 0xd400], unconditional_RAM=False),
                 descriptor=q['proposed_descriptor'],
                 conditions=[
                     'Preserve the original 800 art bytes. Only the final 224 bytes may hold new helper code/data.',
                     'All tile readers must keep the proved 25-pair domain; never expose helper bytes as sprites.',
                     'Copy and verify all nine code/art rows before publishing either complete owner header. Existing cookie hashes the entire art441 page.',
                     'Treat D000..D400 as immutable while this owner is live; no additional mutable state is granted.',
                     'Retire foreign owners and trapped actors before any overwrite; remain exclusive with all other bank2/3 owners.',
                     'Keep shared DFD0..DFD2 clock and both BFE0/DFE0 headers unchanged in meaning.',
                     'Real native callback ABI, interrupt cuts, CHR publication and frontend must pass before menu admission.'
                 ], native_playable=False, menu_admitted=False, host_ROM_changed=False,
                 evidence_SHA256=sha(proof))
    dest = R / 'docs/qa/allocations/bubble-helper-row-1102-v2.json'
    assert not dest.exists()
    dest.write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/bubble-helper-row-v2'
    cp.mkdir(parents=True, exist_ok=True)
    (cp / proof.name).write_bytes(proof.read_bytes())
    (O / 'grant.json').write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(granted=True, helper_bytes=224, new_physical_pages=0,
                          exclusive_bank2_row='D000..D400', native_playable=False)))


if __name__ == '__main__':
    main()

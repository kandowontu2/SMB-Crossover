"""Record the source-proven same-footprint palette-marker/Start rewrite."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

O = R / 'build/bub-menu-flags-grant-1102-v2'
P = R / 'build/bub-menu-integration-1102-v1'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def main():
    O.mkdir(exist_ok=True)
    q = json.loads((P / 'flag-proposal.json').read_text(encoding='utf-8'))
    assert q['passed'] and q['proposal_only'] and not q['ROM_written']
    assert q['base_ROM_SHA256'] == sha(ROM) == PIN
    assert (q['mask_pairs'], q['all_input_flag_pairs'], q['whole_preview_restore_Start_cases']) == (33792, 8448, 924)
    for path, digest in q['bindings'].items():
        assert sha(R / path) == digest, path
    raw = ROM.read_bytes()
    for patch in q['patches']:
        at, old, new = patch['offset'], bytes.fromhex(patch['old']), bytes.fromhex(patch['new'])
        assert len(old) == len(new) and raw[at:at + len(old)] == old
    assert [len(bytes.fromhex(p['new'])) for p in q['patches']] == [1, 1, 1, 74]
    grant = dict(granted=True, owner='Bub/Bob frontend', date='2026-11-02', base_ROM_SHA256=PIN,
                 patches=q['patches'], new_PRG_bytes=0, new_RAM_bytes=0,
                 selector=dict(address=0x5fe8, bit=7, alias='FmGroups',
                               condition='Apply all three source-proven shared P1 palette-marker operands together with the same-footprint Start masks.'),
                 actual_transition_cases=924, full_byte_mask_cases=33792, input_flag_cases=8448,
                 conditions=[
                     'Old slots0..31 retain their effective alternate masks, original retirement order and AXYP/SP/maps behavior.',
                     'Slot32 alone retains bit7; BT/CF use the existing bit6 P1 lease marker and restore the same palette.',
                     'This does not grant private cold execution in menu OperMode0 or gameplay confirmation before backend acceptance.',
                     'Repeat actual native BT/CF selection/Start and Bub/Bob menu rendering before installation.'
                 ], menu_admitted=False, native_playable=False, host_ROM_changed=False,
                 bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), ROM, P / 'flag-proposal.json']})
    dest = R / 'docs/qa/allocations/bub-menu-flags-1102-v2.json'
    assert not dest.exists()
    dest.write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/bub-menu-flags-v2'
    cp.mkdir(parents=True, exist_ok=True)
    for name in ['flag-proposal.json', 'start-flags.s']:
        (cp / name).write_bytes((P / name).read_bytes())
    (O / 'grant.json').write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(granted=True, operand_bytes=3, same_span_Start_bytes=74, native=False)))


if __name__ == '__main__':
    main()

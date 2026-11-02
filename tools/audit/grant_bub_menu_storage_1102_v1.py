"""Lease the retired expanded-menu cursor body for the new Bub/Bob entry."""
import hashlib
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

O = R / 'build/bub-menu-resources-1102-v1'
N = R / 'build/bub-menu-navigation-1102-v1'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def main():
    O.mkdir(exist_ok=True)
    q = json.loads((N / 'proposal.json').read_text(encoding='utf-8'))
    assert q['passed'] and q['ROM_sha256'] == PIN and sha(ROM) == PIN
    for p, digest in q['bindings'].items():
        assert sha(R / p) == digest, p
    assert q['cursor_full_thunk_cases'] == 396 and q['actual_navigation_cases'] == 792
    b = scoped_load(ROM)
    at = location(b, 'QueueCursor')
    assert address(b, 'QueueCursor') == 0xad27 and (at - 16) // 8192 == 66
    assert b['raw'][at:at + 18] == bytes.fromhex('8d6a01a9a58d6c01a9ac8d6d01a9fc4c5a01')
    assert location(b, 'QueueTitleCursor') == at + 84
    assert b['raw'][at + 60:at + 72] == bytes.fromhex('62676c71767b22272c31363b')
    assert b['raw'][at + 72:at + 84] == bytes.fromhex('212121212121222222222222')
    assert hashlib.sha256(b['raw'][at + 18:at + 84]).hexdigest() == q['front_end_dead_span_proposal']['preimage_SHA256']
    source = (R / 'src/character_select.s').read_text(encoding='utf-8')
    proc = source.split('.proc QueueCursor\n', 1)[1].split('.endproc', 1)[0]
    assert proc.startswith('.if ::ENABLE_MMC5_EXPANDED\n  farcall NrQueueCursor,jmp\n.endif\n')
    references = []
    for p in (R / 'src').rglob('*'):
        if p.suffix not in ['.s', '.inc']:
            continue
        text = p.read_text(encoding='utf-8', errors='replace')
        if 'CursorLow' in text or 'CursorHigh' in text:
            references.append(str(p.relative_to(R)))
    assert references == [str(Path('src/character_select.s'))], references
    grant = dict(granted=True, owner='Bub/Bob character-select integration', date='2026-11-02',
                 base_ROM_SHA256=PIN,
                 front_end_PRG=dict(bank=66, CPU_half_open=[0xad39, 0xad7b], bytes=66,
                     file_offset=at + 18, preimage_SHA256=q['front_end_dead_span_proposal']['preimage_SHA256'],
                     source_funding='Unconditional expanded QueueCursor tail thunk makes the following 42B fallback and both 12B local tables unreachable.'),
                 navigation=dict(bank=124, CPU_half_open=[0xa000, 0xa0e0], bytes=224,
                     replacement_scope='Six 33-entry tables plus computed cursor high byte; update the seven exact actual reader operands.',
                     proposal_SHA256=sha(N / 'proposal.json'), used_bytes=214, spare_bytes=10),
                 selector_reservation=dict(address=0x5fe8, alias='FmGroups', bit=7,
                     additional_RAM_bytes=0,
                     condition='Prove actual WWF/ContraForce/menu readers and preserve bit7 across other family toggles before enabling. CF AND31→AND159 is proposed, not already installed.'),
                 conditions=[
                     'Preserve QueueCursor public 18B tail thunk and QueueTitleCursor at AD7B.',
                     'Retired CursorLow/High labels are no longer data APIs and must never receive a new reader.',
                     'Do not move existing navigation-tail code at A0E0 or enlarge the 224B allocation.',
                     'Old native family names, palettes, selection retention and simultaneous Select+confirm must retain behavior.',
                     'One new position at leftX32, topY160; center preview remains separate. Rendering must pass before delivery.',
                     'Actual raw39 backend, owner-specific enemy admission and native controls must work before allowing gameplay confirmation.'
                 ], raw39_reserved=True, menu_admitted=False, native_playable=False,
                 host_ROM_changed=False,
                 bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), ROM,
                     R / 'src/character_select.s', R / 'src/new_roster_dispatch.s', N / 'proposal.json']})
    p = R / 'docs/qa/allocations/bub-menu-1102-v1.json'
    assert not p.exists()
    p.write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/bub-menu-navigation-v1'
    cp.mkdir(parents=True, exist_ok=True)
    for name in ['proposal.json', 'navigation.s']:
        (cp / name).write_bytes((N / name).read_bytes())
    (O / 'grant.json').write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(granted=True, front_end_bytes=66, navigation_bytes=224,
                          new_RAM_bytes=0, menu_admitted=False, ROM_changed=False)))


if __name__ == '__main__':
    main()

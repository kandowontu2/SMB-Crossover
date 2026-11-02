"""Grant exact source-funded backend spans and one private native-test gate."""
import hashlib
import json
from pathlib import Path
import zipfile
from prepare_selected_native_packet_v1 import R, sha
from build_storage_guard_v1 import preflight

O = R / 'build/bubble-shared-grant-1102-v5'
P = R / 'build/bubble-bobble-source-1101-v1'
PIN = '1966a4883a888a5e62f90c4d3e96d25ecf028ddd7d714214727793418d633243'
MANIFEST = '2b7cb50eec12c4c60ce563a188daab2a8e2c42e28f2519c94f797377f406201c'
FREEZE = '6227411b4a9297b71b05d52c2bcd57fe7c335fecefce1ec718019975c6996279'


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    O.mkdir(exist_ok=True)
    preflight(private_root=O, reserved_bytes=1000000, reserved_files=12, fresh=True)
    manifest = P / 'native-proxy-shared-proposal-1966.json'
    freeze = P / 'native-proxy-qualified-1102-v5.json'
    assert sha(manifest) == MANIFEST and sha(freeze) == FREEZE
    q, f = read(manifest), read(freeze)
    assert q['passed'] and f['passed'] and not q['ROM_written'] and not q['admitted']
    assert q['base_ROM_SHA256'] == PIN and sha(R / q['base_ROM']) == PIN
    archive = R / f['archive']
    assert sha(archive) == f['archive_SHA256'] and archive.stat().st_size == 109996
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == set(f['files'])
        for name, info in f['files'].items():
            data = z.read(name)
            assert len(data) == info['bytes'] and hashlib.sha256(data).hexdigest() == info['SHA256'], name
            assert (R / name).read_bytes() == data, name
    for name, h in q['funding_closure']['source_bindings'].items():
        assert sha(R / name) == h, name
    receipts = {}
    for name, h in q['receipts'].items():
        assert sha(R / name) == h, name
        receipt = read(R / name)
        assert receipt['passed'] and not receipt['ROM_written'] and not receipt['admitted']
        for source, digest in receipt['bindings'].items():
            assert sha(R / source) == digest, source
        receipts[Path(name).name] = receipt
    typed = receipts['native-proxy-typed-contact-CPU.json']['checks']
    assert typed['actual_all_37_Ex_row_full_state_ABI_differentials'] == 148
    assert typed['typed37_invalid_foreign_raw_no_private_execution_cases'] == 508
    assert typed['HuBody11_profile_does_not_contact_ObjectOffset_enemy'] == 12
    assert typed['actual_fixed_bridge_dedicated37_original_9px_contacts'] == 882
    assert typed['actual_typed_contact_auth_IRQ_lagNMI']['cuts'] == {'IRQ': 234, 'lagNMI': 234}
    ports = receipts['native-proxy-ports-CPU.json']['checks']
    assert ports['all_255_foreign_native_bbox_ABI_ZP_application_SMC_maps_cases'] == 1530
    assert ports['all_255_foreign_native_shot_full_state_ABI_cases'] == 510
    assert ports['authenticated_Sh_original_pose_bbox_full_state_ABI_cases']['cases'] == 828
    cold = receipts['native-proxy-cold-CPU.json']['checks']
    assert cold['both_owners_both_headers_all16bytes_reject'] == 64
    assert cold['actual_source_trap_to_Ex_cold_restores_flag_AI_before_overwrite']
    assert q['bodygate_ordinary_contact_row'] == 37 and q['HuBody11_profile_reject']
    assert q['existing_PRG79_router_changed_bytes'] == 0
    assert q['existing37_Ex_veneers_realExMenuDone_unchanged']
    assert q['no_new_mutable_RAM'] and q['no_AI_birth_hook'] and q['no_menu_or_confirmation_write']
    assert q['private_code']['spare'] == 15 and q['private_code']['helper_tail_spare'] == 4
    assert not q['funding_closure']['surviving_interior_B029_B031_readers_entries']
    source = (R / q['base_ROM']).read_bytes()
    combined = bytearray(source)
    spans = []
    assert len(q['patches']) == 25 and len(q['shared_patches']) == 16
    for p in q['patches']:
        at, before, after = p['offset'], bytes.fromhex(p['old']), bytes.fromhex(p['new'])
        assert len(before) == len(after) and source[at:at + len(before)] == before, p['role']
        assert not any(max(at, a) < min(at + len(before), b) for a, b in spans)
        spans.append((at, at + len(before)))
        combined[at:at + len(before)] = after
    assert hashlib.sha256(combined).hexdigest() == q['in_memory_backend_only_over1966_SHA256']
    assert sum(a != b for a, b in zip(source, combined)) == 9782
    assert combined[792580:792583] == bytes.fromhex('3aaf88')
    carrier_grant = read(R / 'docs/qa/allocations/bubble-bobble-1102-v1.json')
    assert [p['physical_CHR'] for p in q['owned_carriers']] == [301, 305, 337, 362, 363, 440, 819, 666, 441]
    assert {p['file_offset'] for p in q['owned_carriers']} == {p['file_offset'] for p in carrier_grant['physical_CHR_pages']}
    frontend = R / 'build/bub-menu-candidate-1102-v2/candidate.nes'
    assert sha(frontend) == '90a7108003343ad9f5f9719f860f44f09d1e1932194d5eac1c89bc473e932dd8'
    gate = 16 + 66 * 8192 + 0xd64
    assert frontend.read_bytes()[gate] == 0x38
    cp = R / 'docs/qa/checkpoints/2026-11-02/bubble-native-proxy-v5'
    assert not cp.exists()
    cp.mkdir(parents=True)
    for p, name in [(archive, 'inputs.zip'), (freeze, 'manifest.json'), (manifest, 'proposal.json')]:
        (cp / name).write_bytes(p.read_bytes())
    (cp / 'commit-files.txt').write_text('\n'.join(f['source_files']) + '\n', encoding='utf-8', newline='\n')
    grant = dict(granted=True, date='2026-11-02', owner='Authenticated Ex/Bub/Bob source-funded shared backend',
        base_ROM_SHA256=PIN, approved_proposal_SHA256=MANIFEST,
        approved_proposal=str((cp / 'proposal.json').relative_to(R)).replace('\\', '/'),
        source_checkpoint=str(cp.relative_to(R)).replace('\\', '/'),
        shared_exact_spans=q['shared_patches'], existing_carriers=q['owned_carriers'],
        new_unconditional_RAM_bytes=0, new_physical_carriers=0, additional_AI_or_birth_hooks=False,
        ordinary_contact_row=37, HuBody11_unchanged_profile=True,
        private_native_candidate_allowed=True, production_menu_admitted=False, native_playable=False,
        private_confirmation_patch=dict(offset=gate, old='38', new='18',
            source_lease='Existing new-slot confirmation inside PRG66 AD39..AD7B frontend grant',
            apply_after='Exact granted1249-byte static frontend delta over1966',
            reason='Private controller-only qualification needs the real cold confirmation/scene path.'),
        conditions=[
            'Apply only the exact25 approved backend patches over1966 and exact granted frontend delta; retain WWF death3B and every other current byte.',
            'The AD64 SEC-to-CLC amendment permits a private test candidate only. Do not install or claim Bub/Bob playable before native qualification.',
            'Preserve realB0FB ExMenuDone; virtual typed37 selects privateA06F and native contact uses residentB029. HuBody11 remains profile-only.',
            'Both complete owner headers must authenticate, with real trapped actors retired before invalidation or overwrite. Preserve current Ex payload/cookie.',
            'Shared full-page loader support does not grant Prince compressed payload support or any new RAM.',
            'Root runs genuine cold-menu Bub/Bob controls, graphics, source bubble trap/pop/release, terrain and death/scene checks, plus affected Ex/Sh/BT/CF regressions.',
            'Measure actual idle/walk cadence. Full1-1, earned powerups and final helper requirements remain incomplete until separately verified.'
        ], bindings={str(p.relative_to(R)).replace('\\', '/'): sha(p) for p in
                    [Path(__file__), manifest, freeze, archive, R / q['base_ROM'], frontend]})
    dest = R / 'docs/qa/allocations/bubble-shared-native-1102-v5.json'
    assert not dest.exists()
    dest.write_text(json.dumps(grant, indent=2) + '\n', encoding='utf-8')
    (O / 'receipt.json').write_text(json.dumps(dict(passed=True, granted=True,
        approved_proposal_SHA256=MANIFEST, private_native_only=True, installed=False,
        production_menu_admitted=False, source_archive_bytes=109996), indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(granted=True, shared_spans=16, existing_carriers=9,
                          private_native_only=True, installed=False)))


if __name__ == '__main__':
    main()

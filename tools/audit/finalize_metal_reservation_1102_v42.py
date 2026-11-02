"""Freeze bounded source/evidence and record the verified installed successor."""
import hashlib
import json
import zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from nightly_patch_guard_v1 import check
from build_storage_guard_v1 import inventory, preflight

O = R / 'build/metal-reservation-1102-v42'
BASE = R / 'build/excitebike-pose-1101-v3/current4.nes'
ROM = O / 'candidate.nes'
DEST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    digest = sha(ROM)
    assert sha(DEST) == digest and check(DEST)['passed']
    q = read(O / 'delivery.json')
    result, binding = [read(O / 'downloads/capture' / n) for n in ['result.json', 'binding.json']]
    assert result['passed'] and binding['exit_code'] == 0 and binding['ROM_sha256'] == digest
    for p, h in read(O / 'downloads/ready.json')['bindings'].items():
        assert sha(p) == h, p
    q['downloads_launch_verified'] = True
    q['downloads_verification'] = result
    q['after'] = check(DEST)
    (O / 'delivery.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    cp = R / 'docs/qa/checkpoints/2026-11-02/metal-reservation-v42'
    cp.mkdir(parents=True, exist_ok=True)
    archive = cp / 'inputs.zip'
    assert not archive.exists()
    members = {name: (O / name).read_bytes() for name in ['component.s', 'component.cfg',
               'component.lbl', 'body-compact.bin', 'native-cookie.bin', 'native-actor.bin',
               'native-render.bin', 'native-extra.bin', 'native-auth.bin', 'native-finish.bin']}
    members['shot-meta.bin'] = (R / 'build/metal-storm-render-host-1101-v7/shot-meta.bin').read_bytes()
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in members.items():
            info = zipfile.ZipInfo(name, date_time=(2026, 11, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    manifest = dict(archive_bytes=archive.stat().st_size, archive_SHA256=sha(archive),
                    no_ROM_or_capture_archive=True,
                    members=[dict(path=n, bytes=len(v), SHA256=hashlib.sha256(v).hexdigest())
                             for n, v in members.items()],
                    scope='Exact expanded source plus only its two art inputs and current compact native leaves. '
                          'Absolute build output path in linker config must be rebound before reconstruction; '
                          'no complete donor, host ROM, debug graph, historical tree or media archive.')
    (cp / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    evidence = {}
    for folder in ['native', 'route', 'downloads']:
        evidence[folder] = dict(result=read(O / folder / 'capture/result.json'),
                                binding=read(O / folder / 'capture/binding.json'),
                                ready_SHA256=sha(O / folder / 'ready.json'))
    receipt = dict(passed=True, installed=True, ROM_SHA256=digest, parent_ROM_SHA256=sha(BASE),
                   source=manifest, assembly=read(O / 'assembly.json'), CPU=read(O / 'CPU.json'),
                   native=evidence, delivery=q, ordering=read(O / 'native/capture/ordering.json'),
                   DMA_samples=read(O / 'native/capture/graphics.json'), helpers_added=False,
                   remaining='Metal Storm palette, HUD name, original audio, gravity escape/upgrade/modes and '
                             'shortcut checks remain open. This is not all-character or zero-lag qualification.')
    (cp / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    before, after = BASE.read_bytes(), ROM.read_bytes()
    changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
    assert len(before) == len(after)
    code_pages = {247, 248, 249, 250, 827, 828, 829, 830, 831, 500, 494}
    resident = [(16 + bank * 8192 + off, n) for bank, off, n in [(25, 0x1f9e, 97), (99, 0x176e, 135)]]
    assert all(any(lo <= i < lo + n for lo, n in resident) or
               (i >= 16 + 1048576 and (i - 16 - 1048576) // 1024 in code_pages) for i in changed)
    grants = ['bubble-bobble-1102-v1.json', 'prince-1102-v1.json', 'common-cold-1102-v1.json',
              'bub-menu-1102-v1.json', 'bub-menu-flags-1102-v2.json', 'bubble-helper-row-1102-v2.json']
    # Physical carrier sets are explicit source-derived grants, not a search
    # for repeated filler. The successor leaves each proposed identity intact.
    pools = {'Bub_Bob': [301, 305, 337, 362, 363, 440, 819, 666, 441],
             'Prince': [341,343,345,347,349,351,353,355,357,359,361,365,369,373,377,381,
                        383,385,387,389,391,393,544,545,605,607,609,611,613,615,617,619,
                        621,623,625,627,690,691,692,693,695,795]}
    for pages in pools.values():
        for page in pages:
            at = 16 + 1048576 + page * 1024
            assert before[at:at + 1024] == after[at:at + 1024]
    for bank in [29, 65, 66, 76, 123, 124]:
        at = 16 + bank * 8192
        assert before[at:at + 8192] == after[at:at + 8192]
    rebase = dict(granted=True, date='2026-11-02', previous_ROM_SHA256=sha(BASE),
                  successor_ROM_SHA256=digest, changed_ROM_bytes=len(changed),
                  changed_scope='Only existing Metal private code/reference relocation and complete cookie bindings.',
                  unchanged_carrier_pools=pools, unchanged_full_PRG_banks=[29,65,66,76,123,124],
                  original_grants={n: sha(R / 'docs/qa/allocations' / n) for n in grants},
                  condition='Carry the tested Metal successor into composition; retain all original grant conditions. '
                            'No shared routing, new RAM, new physical pages or native/menu admission is implied.',
                  menu_admitted=False, native_Bub_or_Prince=False,
                  bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), BASE, ROM, cp / 'receipt.json']})
    dest = R / 'docs/qa/allocations/roster-rebase-1102-v3.json'
    assert not dest.exists()
    dest.write_text(json.dumps(rebase, indent=2) + '\n', encoding='utf-8')
    note = '''# Metal Storm native sprite reservation — November 2

The installed MMC5 nightly now uses SHA256 `DIGEST`. The actual Downloads
launch passes the same cold-menu, idle/walk and OAM checks as the candidate.
The file was replaced directly, with no backup or sidecar patch.

The renderer was reserving player sprites through a null pose pointer. Its
first byte happened to be175, so the allocation advanced by a non-multiple of
four and eventually rotated tile/attribute/position bytes into the wrong OAM
fields. The visible body appeared displaced and scrambled. The private graphics
worker also supplied a pointer into a cache bank that did not remain mapped.

Movement and drawing now establish a zero-length reservation using the stable
native ObjectMetasprite byte. The original actor, sprite packets, shot logic
and physics stay intact. Six renderer bytes are added inside the existing
3072-byte allocation; genuine references are relocated and both full cookies
updated. No additional resident storage, RAM or helper platform is used.

Verification includes16 real public movement equivalence cases, every one of
32 single-byte full-header corruptions, and174 actual IRQ plus174 busy-NMI
interruption/return cases. A real cold native run observes74 aligned draw,
reservation and emission calls. The full non-shortcut route reaches active1-2
in5587physicalframes with a genuine native enemy defeat and lives2→2.

Performance in the empty opening remains120 Main updates per180 physical
idle frames and27/40 walking frames. This repair does not claim reduced lag.
The visible sprite is now coherent at its native position. The MARIO HUD name
and incorrect player palette remain open, along with original audio, upgrades,
gravity-related escape cases and shortcut/mode testing.

Compact source and evidence: `docs/qa/checkpoints/2026-11-02/metal-reservation-v42/`.
'''.replace('DIGEST', digest)
    (R / 'docs/qa/metal-reservation-1102-v42.md').write_text(note, encoding='utf-8')
    handoff = R / 'docs/qa/continuation-current.json'
    current = read(handoff)
    current['installed_nightly'] = q
    current['goal_status'] = 'ACTIVE_INCOMPLETE'
    current['previous_goal_turn_classification'] = 'progress'
    current['roster_integration_followup']['installed_ROM_sha256'] = digest
    current['roster_integration_followup']['helpers_model'] = 'gpt-6.1-sol'
    current['roster_integration_followup']['helpers_reasoning'] = 'xhigh'
    current['roster_integration_followup']['next'] = ('Continue native Bub/Bob/Prince and absent identities; '
        'all-character1-1, every-powerup and severe idle/walk lag remain unfinished. Preserve Metal1cd8 and current Ex/Arthur fixes.')
    current['Metal_reservation_followup'] = dict(installed=True, ROM_SHA256=digest,
        source_checkpoint=str(cp.relative_to(R)), note='docs/qa/metal-reservation-1102-v42.md',
        full11=True, full11_frames=5587, initial_lives=2, final_lives=2, helpers_added=False,
        actual_Downloads_launch_verified=True, original_audio_or_all_powerups=False,
        remaining='Palette/HUD/audio and complete abilities/modes/shortcut remain open; idle cadence unchanged.')
    current['current_owning_candidate'] = str(ROM)
    current['current_owning_build_recipe'] = 'tools/audit/prepare_metal_reservation_1102_v42.py'
    current['source_override_required'] = ('Latest installed1cd8 is a verified successor tocf1412. '
        'Use the exact private recipe/frozen inputs and current parent; never replace it with an older canonical kernel. '
        'Bub/Prince rebase: docs/qa/allocations/roster-rebase-1102-v3.json.')
    current['Bub_Bob_resource_followup']['frontend_flags_grant'] = 'docs/qa/allocations/bub-menu-flags-1102-v2.json'
    current['Bub_Bob_resource_followup']['latest_rebase'] = str(dest.relative_to(R))
    current['Prince_resource_followup']['latest_rebase'] = str(dest.relative_to(R))
    handoff.write_text(json.dumps(current, indent=2) + '\n', encoding='utf-8')
    p = R / 'docs/qa/helper-platform-inventory-1101.md'
    text = p.read_text(encoding='utf-8')
    old = 'Current nightly SHA256: `' + sha(BASE) + '`.'
    assert text.count(old) == 1
    text = text.replace(old, 'Current nightly SHA256: `' + digest + '`.')
    text = text.replace('See `docs/qa/metal-storm-route-1101.md`. Its powerup/mode checks remain unfinished.',
        'The November2 successor repeats the full route in5587frames, lives2→2, with repaired sprite reservation. '
        'See `docs/qa/metal-reservation-1102-v42.md`. Powerup/mode checks remain unfinished.')
    p.write_text(text, encoding='utf-8')
    readme = R / 'README.md'
    text = readme.read_text(encoding='utf-8')
    marker = '**All six WWF wrestlers**'
    assert text.count(marker) == 1
    paragraph = ('**Metal Storm** now has repaired sprite allocation: his body stays coherent at its native position '
        'instead of scrambling during OAM rotation. The latest candidate clears non-shortcut1-1 into active1-2 '
        'without life loss or helpers, and the actual Downloads launch passes. His palette/HUD name and original '
        'audio remain unfinished; empty-area update cadence is unchanged. See the '
        '[November2 verification](docs/qa/metal-reservation-1102-v42.md).\n\n')
    readme.write_text(text.replace(marker, paragraph + marker), encoding='utf-8')
    storage = preflight(fresh=True)
    storage['workspace_bytes'], storage['workspace_files'] = inventory(R, 70_000_000_000, 10_000_000)
    storage['task_bytes'], storage['task_files'] = inventory(O, 256_000_000, 1000)
    (O / 'storage.json').write_text(json.dumps(storage, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(installed_SHA256=digest, source_archive_bytes=archive.stat().st_size,
                         exact_changed_bytes=len(changed), goal_complete=False, storage=storage)))


if __name__ == '__main__':
    main()

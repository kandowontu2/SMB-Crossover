"""Record actual Downloads validation and the disjoint three-byte successor."""
import json
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from nightly_patch_guard_v1 import check
from build_storage_guard_v1 import preflight, inventory

O = R / 'build/wwf-death-1102-v2'
ROM = O / 'candidate.nes'
BASE = R / 'build/metal-reservation-1102-v42/candidate.nes'
DEST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    digest = sha(ROM)
    assert sha(DEST) == digest and check(DEST)['passed']
    result, binding = [read(O / 'downloads/capture' / n) for n in ['result.json', 'binding.json']]
    assert result['passed'] and binding['exit_code'] == 0 and binding['ROM_sha256'] == digest
    for p, h in read(O / 'downloads/ready.json')['bindings'].items():
        assert sha(p) == h, p
    delivery = read(O / 'delivery.json')
    delivery.update(downloads_launch_verified=True, downloads_verification=result, after=check(DEST))
    (O / 'delivery.json').write_text(json.dumps(delivery, indent=2) + '\n', encoding='utf-8')
    rows = []
    for name in [*[f'contact-{i}' for i in range(6)], 'pit']:
        p = O / 'native-v3' / name
        q, b = read(p / 'capture/result.json'), read(p / 'capture/binding.json')
        assert q['passed'] and b['exit_code'] == 0 and b['ROM_sha256'] == digest
        rows.append(dict(case=name, result=q, binding=b, ready_SHA256=sha(p / 'ready.json')))
    before, after = BASE.read_bytes(), ROM.read_bytes()
    diff = [i for i, (x, y) in enumerate(zip(before, after)) if x != y]
    assert len(before) == len(after) and diff == [792580, 792581, 792582]
    cp = R / 'docs/qa/checkpoints/2026-11-02/wwf-death-v2'
    cp.mkdir(parents=True, exist_ok=True)
    receipt = dict(passed=True, installed=True, ROM_SHA256=digest, parent_ROM_SHA256=sha(BASE),
        assembly=read(O / 'assembly.json'), CPU=read(O / 'CPU.json'), native=rows, delivery=delivery,
        original_negative=read(R / 'build/hogan-full11-1102-v2/native/capture/result.json'),
        observer_negative='First contact observer missed the final age168 store when engine11→6 before endFrame; '
                          'native-v3 observes that actual bus write and retains all duration/respawn assertions.',
        helpers_added=False, full11_cleared=False,
        remaining='WWF full1-1 traversal/gaps, all earned powerups, original endurance/advanced moves and performance remain unfinished.')
    (cp / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    (cp / 'death-row.s').write_bytes((O / 'death-row.s').read_bytes())
    # New private/menu proposals remain based on1cd8, with every relevant byte
    # unchanged except this single existing WWF service-table entry.
    rebase = dict(granted=True, date='2026-11-02', previous_ROM_SHA256=sha(BASE), successor_ROM_SHA256=digest,
        only_patch=dict(file_offset=792580, physical_PRG=96, CPU=0xb7f4,
                        old=before[792580:792583].hex(), new=after[792580:792583].hex()),
        unchanged_all_other_ROM_bytes=True, additional_RAM_or_storage=False,
        conditions=['Carry the tested WWF death row into any subsequent1cd8-based composition.',
                    'Every Bub/Bob/Prince/menu/common storage grant retains its existing conditions.',
                    'This does not admit new characters or qualify shared backend/scene changes.'],
        menu_admitted=False, native_Bub_or_Prince=False,
        bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), BASE, ROM, cp / 'receipt.json']})
    grant = R / 'docs/qa/allocations/roster-rebase-1102-v4.json'
    assert not grant.exists()
    grant.write_text(json.dumps(rebase, indent=2) + '\n', encoding='utf-8')
    note = f'''# WWF native death completion — November 2

Current installed MMC5 SHA256: `{digest}`. Actual Downloads launch is verified;
the ROM was replaced directly with no backup or sidecar patch.

Hogan's natural1-1 attempt cleared all four pipes and defeated three enemies,
then fell into the first pit. Engine11 never completed because WWF's typed
death-tick row8 pointed to WfNoop. The stall is reproduced through the actual
public service: ten calls leave death age0 and engine11 unchanged.

The repair changes only three existing table bytes in PRG96 at B7F4, shared
by all six wrestlers. Row8 now selects the existing native guest death worker.
It uses the already initialized150-tick pit or168-tick contact sequence, then
enters native life loss. No new timer, RAM, physics or art is added.

CPU verification covers both complete death sequences and real PlayerLoseLife
for all six variants,420 unchanged other WWF service resolutions,84 foreign
resolver full-state comparisons and two invalid WWF selectors. Real Mesen
controller runs verify ordinary enemy-contact death→one life lost→active1-1
respawn for every wrestler, retaining identity. Hogan's original first-pit
route also recovers into active1-1. Actual Downloads repeats his contact case.

Full1-1 is still unqualified. The first controller jumps too early for the first
gap, so that failure does not establish a helper-platform requirement. Other
gaps, all earned powerups, authentic endurance/advanced moves and lag remain
open. This fixes life-loss progression, not original WWF death artwork.

Compact evidence: `docs/qa/checkpoints/2026-11-02/wwf-death-v2/receipt.json`.
'''
    (R / 'docs/qa/wwf-death-1102-v2.md').write_text(note, encoding='utf-8', newline='\n')
    p = R / 'docs/qa/continuation-current.json'
    q = read(p)
    q['installed_nightly'] = delivery
    q['goal_status'] = 'ACTIVE_INCOMPLETE'
    q['previous_goal_turn_classification'] = 'progress'
    q['roster_integration_followup']['installed_ROM_sha256'] = digest
    q['WWF_death_followup'] = dict(installed=True, ROM_SHA256=digest,
        note='docs/qa/wwf-death-1102-v2.md', checkpoint=str(cp.relative_to(R)),
        native_contact_death_respawn_variants=6, native_Hogan_pit_respawn=True,
        actual_Downloads_verified=True, full11=False, helpers_added=False,
        next='Late-edge gap attempt and complete routes/powerups; do not infer helpers from early-jump policy.')
    q['current_owning_candidate'] = str(ROM)
    q['current_owning_build_recipe'] = 'tools/audit/prepare_wwf_death_1102_v2.py'
    q['source_override_required'] = ('Latest installed1966 is a3-byte WWF death-row successor to1cd8. '
        'Keep both the latest Metal repair and WWF row when composing new characters. '
        'Formal rebase: docs/qa/allocations/roster-rebase-1102-v4.json. Canonical37-character source builder is not this full WIP.')
    for key in ['Bub_Bob_resource_followup', 'Prince_resource_followup']:
        q[key]['latest_rebase'] = str(grant.relative_to(R))
    q['Bub_Bob_resource_followup']['frontend_static_grant'] = 'docs/qa/allocations/bub-menu-static-1102-v3.json'
    q['Bub_Bob_resource_followup']['frontend_native_negatives'] = [
        'native-menu: Mesen importer rejected dangling synthetic DBGsegment900000 before gameplay.',
        'native-menu2: simultaneous Select+A name expectation disagreed with preserved native Select-before-confirm order. '
        'Helper is proving ordered input and preparing a distinct observer; not native menu acceptance.']
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    p = R / 'docs/qa/helper-platform-inventory-1101.md'
    text = p.read_text(encoding='utf-8')
    old = 'Current nightly SHA256: `' + sha(BASE) + '`.'
    assert text.count(old) == 1
    text = text.replace(old, 'Current nightly SHA256: `' + digest + '`.')
    marker = '## Later-stage shared placements'
    assert text.count(marker) == 1
    text = text.replace(marker, 'Hogan now crosses all four1-1 pipes in a natural controller attempt without\n'
        'helpers, then fails the first gap under an early-jump policy. A subsequent\n'
        'native death repair is verified for all six WWF identities. No WWF helper\n'
        'placement or impossible-crossing claim follows from that unfinished route.\n\n' + marker)
    p.write_text(text, encoding='utf-8', newline='\n')
    p = R / 'README.md'
    text = p.read_text(encoding='utf-8')
    old = 'The latest delivered nightly is `1cd8e192` (November 2)'
    assert text.count(old) == 1
    text = text.replace(old, 'The latest delivered nightly is `1966a488` (November 2)')
    marker = '**Thomas** is now playable:'
    assert text.count(marker) == 1
    text = text.replace(marker, '**WWF death recovery:** all six wrestlers now complete the native life-loss '
        'sequence and respawn after enemy contact. Hogan also recovers from a natural pit death; the actual '
        'Downloads launch is verified. A missing death-tick binding had left them stuck. Full WWF routes '
        'and powerups remain unfinished. See the [November2 checks](docs/qa/wwf-death-1102-v2.md).\n\n' + marker)
    p.write_text(text, encoding='utf-8', newline='\n')
    storage = preflight(fresh=True)
    storage['task_bytes'], storage['task_files'] = inventory(O, 256_000_000, 1000)
    (O / 'storage.json').write_text(json.dumps(storage, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(installed_SHA256=digest, native_cases=7, Downloads_verified=True,
                         exact_changed_bytes=3, helpers_added=False, goal_complete=False, storage=storage)))


if __name__ == '__main__':
    main()

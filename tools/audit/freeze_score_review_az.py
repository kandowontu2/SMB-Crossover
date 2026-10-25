"""Preserve the installed score fix and the already completed footage review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil, sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/playthroughs'))
from roster_run import workspace_bytes

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

aq = read(R / 'build/verification/score-anchor-aq/summary.json')
at = read(R / 'build/verification/score-abi-at/summary.json')
assert at['passed']
unchanged = [z for z in aq['results'] if z['test'] != 'score-popup-location']
assert len(unchanged) == 20 and all(z['passed'] for z in unchanged)
evidence = []
native = {}
for mapper in ('mmc3', 'mmc5'):
    p = R / 'build/verification' / f'score-popup-fixture-au-{mapper}.log'
    text = p.read_text(encoding='utf-8')
    assert 'PASS six native weapon defeats' in text and 'Mesen exit: 0' in text and 'FAIL' not in text
    evidence.append(dict(path=p.relative_to(R).as_posix(), sha256=sha(p)))
    native[mapper] = {}
    for version in ('old', 'new'):
        p = R / 'build/verification' / f'score-anchor-native-an-{version}-{mapper}/summary.json'
        z = read(p)
        assert z['ordinary_controller'] and not z['emulated_memory_writes']
        assert z['score-summary']['calls'] == 16 and z['score-summary']['bad_returns'] == 0
        assert z['score-summary']['wrong_anchors'] == (7 if version == 'old' else 0)
        native[mapper][version] = dict(path=p.relative_to(R).as_posix(), sha256=sha(p), summary=z['score-summary'])
negative = R / 'build/verification/score-popup-fixture-au-old-negative.log'
assert 'FAIL Defeat score must follow its target' in negative.read_text(encoding='utf-8')
roms = {m: sha(R / 'build' / f'smb-crossover-{m}.nes') for m in ('mmc3', 'mmc5')}
for z in aq['layout']:
    assert roms[z['mapper']] == z['ROM_sha256']
    assert z['literal_baseline'] and z['all_old_label_addresses_unchanged'] and z['no_new_RAM']

O = R / 'build/checkpoints/score-popup-location-az'
assert not O.exists()
O.mkdir()
names = [f'build/smb-crossover-{m}.{e}' for m in ('mmc3', 'mmc5') for e in ('nes', 'lbl', 'dbg', 'map')]
names += ['smb1base.cfg', 'src/collision.s', 'src/entrypoint.s', 'src/score_popup.s',
          'src/game.s', 'src/guest_body_contact.s', 'src/terrain_catchup.s',
          'tests/score-popup-location.lua', 'tests/terrain-coin-publication.lua', 'tools/verify.py']
for name in names:
    p = O / name
    p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(R / name, p)
manifest = dict(status='INSTALLED_SCORE_ANCHOR_REPAIR_WITH_TERRAIN_AF_NOT_FINAL_RELEASE',
    parent_checkpoint='build/checkpoints/terrain-publication-af/manifest.json',
    parent_checkpoint_sha256=sha(R / 'build/checkpoints/terrain-publication-af/manifest.json'),
    ROMs=roms, hashes={n: sha(O / n) for n in names},
    source_hashes={p.relative_to(R).as_posix(): sha(p) for p in (R / 'src').rglob('*') if p.is_file()},
    layout=aq['layout'], unchanged_native_checks=unchanged, corrected_native_score_fixtures=evidence,
    ordinary_controller_before_after=native,
    compiled_selector_cases=sum(z['cases'] for z in at['results']),
    compiled_selector_report_sha256=sha(R / 'build/verification/score-abi-at/summary.json'),
    native_old_ROM_negative_sha256=sha(negative),
    original_AQ_matrix_passed=False,
    test_harness_correction='Removed nesDebug writes to $8000: they patch emulated ROM rather than selecting a mapper register. On-disk ROMs were unchanged. Actual native returns are read-only; foreign selectors are covered separately by compiled CPU execution.',
    new_RAM_bytes=0,
    tail_partition='A bank $24: Water B600-B6FF, Ryu B700-BFBF, score BFC0-BFFF. Ryu F ends B9D4. No private component is installed by this repair.',
    interrupt_injection_claim=False, full_suite_rerun=False, goal_complete=False)
(O / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

report = R / 'docs/qa/score-popup-repair-2026-10-22.md'
assert not report.exists()
report.write_text('''# Score popup position repair

The defeat popup used a shared relative X left by an earlier actor or the target before it moved. It now uses the defeated slot's own world X minus the camera position. Y, timer and popup selection retain the native behavior. This repair builds on the installed green-terrain publication repair.

The 19-byte resident entry retains its old address and calls a small cold body through the existing selector-preserving native-call mechanism. The new body occupies the unused A-mapped bank $24 tail at BFC0. The header, CHR, all old code/RAM labels and baseline ROM builds are unchanged; no new RAM is allocated. Only the entry and previously unused tail change (58 ROM bytes MMC3, 50 MMC5). The reserved 64-byte score tail leaves B600-B6FF for the private Water candidate and B700-BFBF for Ryu; the frozen Ryu F body ends at B9D4.

## Verification

- An ordinary 6,000-frame Bill controller run on each mapper produces 16 score calls. The old ROM misplaces seven; the repaired ROM misplaces zero. Both return all observed caller registers, flags, stack depth and mapper state correctly. These are bounded, zero-death runs into 1-2, not full clears.
- The permanent native fixture passes on both mappers: six authored target slots, camera/page boundaries, actual prone shots, and the actual number renderer. The old ROM fails specifically on the stale anchor. This is a diagnostic arena, not a controller-only route claim.
- Twenty unchanged scoped native checks passed in the original AQ matrix. Its initial MMC3 score fixture failed because an attempted debug-register write actually patched the emulated code. That harness error was removed; the corrected AU score fixtures pass on both mappers. The original failed matrix and diagnostic evidence are retained. On-disk ROM files were unchanged.
- A separate compiled CPU test passes 9,072 cases, including all eight foreign MMC3 selectors, flags, slots, camera boundaries, stack and bank restoration. The rejected standard-call prototype fails the selector check. This is not an interrupt-injection or cycle-cost claim; no interrupt occurred inside the observed ordinary score calls.

Checkpoint: `build/checkpoints/score-popup-location-az/manifest.json`. Evidence: `score-anchor-aq/summary.json`, `score-popup-fixture-au-*.log`, `score-anchor-native-an-*/summary.json`, and `score-abi-at/summary.json` under `build/verification`.

The old fourteen delivery videos retain their original identities. They were not re-recorded by this repair. Bullet Bill duplication, missing firebars, underground block colors, late HUD splits, remaining private component composition and final all-character captures remain open.
''', encoding='utf-8')
for name in ('footage-review-2026-10-22.md', 'terrain-publication-repair-2026-10-22.md'):
    p = R / 'docs/qa' / name
    with p.open('a', encoding='utf-8') as f:
        f.write('\nLater follow-up: [score popup repair](score-popup-repair-2026-10-22.md) records the installed successor. Earlier findings and test counts above retain their original build identities.\n')

used = workspace_bytes(R)
assert used < 100000000000
handoff = dict(status='ALL14_FOOTAGE_REVIEWED_GREEN_LOCATED_SCORE_ANCHOR_REPAIRED_FULL_GOAL_ACTIVE',
    utc=datetime.now(timezone.utc).isoformat(),
    previous_progress_sha256=sha(R / 'build/verification/root-current49-progress-ak.json'),
    checkpoint=(O / 'manifest.json').relative_to(R).as_posix(), checkpoint_sha256=sha(O / 'manifest.json'),
    ROMs=roms, report=report.relative_to(R).as_posix(), report_sha256=sha(report),
    review='docs/qa/footage-review-2026-10-22.md',
    green_location='Bill.mp4, 1-3, 4:01-4:05; ground blocks and cloud. Review clip retained.',
    hard_trials={
        'hard-upgrade-ay-0': dict(terminal=True, item=3, kind='Flare', native_AV=False, deaths=0),
        'hard-upgrade-ay-1': dict(terminal=True, item=3, kind='Flare', native_AV=False, deaths=0),
        'hard-upgrade-ay-2': dict(terminal=True, item=2, kind='Laser', native_AV=False, deaths=0)},
    root_native_handles=[], goal_complete=False, goal_status='active',
    full_all_character_final_movies_not_regenerated=True,
    workspace_bytes=used, workspace_cap=100000000000, all_lossless_and_negatives_retained=True,
    remaining=[
        'Fresh ordinary visit/recording of repaired Bill 1-3 location; current full route correction still dies at later 1-2 x2303.',
        'Actual actor/OAM diagnosis of duplicated Bullet Bills and missing firebars; underground block palette and late HUD splits remain open.',
        'Natural Hard Bill upgrade A/V clips and Easy/Hard landing comparison; AY discovery gives actual Flare and Laser. Rapid, Rapid2 chain, Machine and Spread still need natural acquisition and recordings.',
        'Retain Claude, terrain and score changes during additive private HUD/Land/Arm/Rush/audio/Ryu/visible-Water composition. HUD consumer-busy bug remains unimplemented.',
        'Original all-character/all-ability/all-upgrade/mode/SFX/performance scope and final through-2-2 recordings remain required.'])
(R / 'build/verification/root-current49-progress-az.json').write_text(json.dumps(handoff, indent=2) + '\n', encoding='utf-8')
print(json.dumps(dict(checkpoint=str(O), ROMs=roms, workspace_bytes=used, goal_complete=False), indent=2))

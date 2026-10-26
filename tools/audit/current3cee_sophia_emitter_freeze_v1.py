"""Freeze the one source-only Sophia experiment and its positive-cost limits."""
from pathlib import Path
from collections import defaultdict
import argparse, hashlib, inspect, json, shutil, sys
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from py65.devices import mpu6502

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda: f.read(1048576), b''):
            h.update(data)
    return h.hexdigest()


def get(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def put(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    a = parser.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    build = get(a.prepared / 'proof.json')
    cpu = get(a.prepared / 'cpu-v1/proof.json')
    assert build['passed'] and cpu['passed'] and not cpu['native_run']
    assert sha(a.prepared / 'candidate.nes') == build['candidate_ROM_sha256'] == cpu['candidate_ROM_sha256']
    old, new = [scoped_load(a.prepared / (name + '.nes')) for name in ['baseline', 'candidate']]
    physical = 0
    for name, sym in old['syms'].items():
        if 'seg' in sym and 'ooffs' in old['segs'][sym['seg']]:
            assert location(old, name) == location(new, name), ('Old physical location moved', name)
            physical += 1
    groups = defaultdict(list)
    rows = get(a.prepared / 'cpu-v1/emitter-cases.json')
    for r in rows:
        x, y, xh, yh = r['origin']
        category = ('hot' if r['hot'] else 'foreign' if r['char'] != 11 else
                    'unsupported-record' if r['pointer'] not in [0xc00a, 0xc017] else
                    'nonzero-attribute' if r['attr'] else 'wrong-high-page' if xh != 0 or yh != 1 else
                    'X-edge' if not 12 <= x < 252 else 'Y-edge' if y < 3 else 'full-capacity')
        groups[category].append(r['delta'])
    cost = {k: dict(cases=len(v), minimum_CPU_delta=min(v), maximum_CPU_delta=max(v)) for k, v in groups.items()}
    callers = get(a.prepared / 'cpu-v1/caller-cases.json')
    caller_cost = []
    for key in sorted(set((r['char'], r['shot'], r['mode'], r['active_slots'], r['cursor']) for r in callers)):
        selected = [r for r in callers if (r['char'], r['shot'], r['mode'], r['active_slots'], r['cursor']) == key]
        caller_cost.append(dict(character=key[0], shot=key[1], source_weapon_mode=key[2], active_slots=key[3],
                                initial_cursor=key[4], min_delta=min(r['delta'] for r in selected), max_delta=max(r['delta'] for r in selected)))
    put(a.output / 'costs.json', dict(per_emitter=cost, full_caller_groups=caller_cost,
                                    interpretation='Positive fallback costs are material and retained. CPU-only costs do not establish recovered native update/draw cadence.'))
    # A finite applicability control from the already captured original crowded
    # epoch, not a new native run or an invented full game-state replay.
    probe = D / 'current3cee-vehicle-visibility-v1/sophia/native'
    publications = [json.loads(line) for line in (probe / 'visibility-publications.jsonl').open()]
    pub = next(p for p in publications if p['id'] == 959)
    b = pub['body']
    oam = bytes.fromhex(pub['oam'])
    assert b['logical_start'] == 36 and b['rotation'] == 200
    parts = [oam[(i * 4 + b['rotation']) & 255:((i * 4 + b['rotation']) & 255) + 4] for i in range(9)]
    record = bytes.fromhex(get(a.prepared / 'records.json')[1]['bytes'])
    original_parts = [record[i:i + 4] for i in range(1, 13, 4)][::-1]
    shots = []
    for i in range(3):
        group = parts[i * 3:i * 3 + 3]
        origin_x = (group[0][3] - (original_parts[0][3] if original_parts[0][3] < 128 else original_parts[0][3] - 256)) & 255
        origin_y = (group[0][0] + 3) & 255
        assert 12 <= origin_x < 252 and origin_y >= 3
        for actual, (tile, attr, dy, dx) in zip(group, original_parts):
            dx = dx if dx < 128 else dx - 256
            assert actual == bytes([(origin_y - 3) & 255, tile, attr, origin_x + dx])
        shots.append(dict(logical_part_start=i * 3, origin_relative_X=origin_x, origin_Y_low=origin_y,
                          original_OAM_tuples=[p.hex() for p in group], source_record_pointer=0xc017,
                          eligible_geometric_bounds=True))
    put(a.output / 'saved-native-applicability.json', dict(
        source_ROM_sha256=build['baseline_ROM_sha256'], candidate_not_run=True,
        original_actual_PPU_frames=[3064, 3065, 3066], original_publication=959, original_DMA=1434,
        native_body_wrap_still_present=True, original_prefix_parts=9, matched_immutable_wave_records=3,
        shots=shots, scope='Only the original nine pre-body OAM records are projected onto the two compiled horizontal-wave records. This proves an applicable original crowded record geometry, not a reconstructed complete CPU state or candidate native timing.'))
    # Current bank36 is split between a C-window art region and A-window owners.
    bank36 = []
    for s in old['segs'].values():
        if 'ooffs' in s and (int(s['ooffs'], 0) - 16) // 8192 == 36:
            bank36.append(dict(segment=s['name'].strip('"'), CPU_start=int(s['start'], 0), size=int(s['size'], 0),
                               physical_offset=int(s['ooffs'], 0) - (16 + 36 * 8192)))
    assert set(old['raw'][16 + 4 * 8192 + 0x1f33:16 + 4 * 8192 + 0x1f8b]) == {255}
    assert set(old['raw'][16 + 36 * 8192 + 0x1523:16 + 36 * 8192 + 0x1600]) == {255}
    put(a.output / 'placement-and-owners.json', dict(
        all_old_values_exact=build['all_old_symbol_values_exact'], old_ROM_symbol_locations_exact=physical,
        current_bank36_segments=bank36, gate=dict(bank=4, start=0xbf33, end=0xbf8a, bytes=87),
        emitter=dict(bank=36, start=0xd523, end=0xd5ec, bytes=201),
        untouched_bank36_A_window_begin=0xb600, untouched_bank36_physical_offset=0x1600,
        guard_profile=dict(character=11, C_window_owner=36, immutable_pointers=[0xc00a, 0xc017],
                           R3=0, X_high=0, Y_high=1, X_low_inclusive=[12, 251], Y_low_inclusive=[3, 255], cursor_maximum=243),
        production_mapping_owner='ExpandedWeaponPointer calls ExpandedGraphicsBank before pointer selection; real ExpandedDrawShots then writes R3=0 and reaches the sole patched JSR. The component guard also rejects nonzero R3. Actual compiled IRQ/NMI controls preserve the mapped bank/shadows.',
        state_writes='Only original ordered OAM writes and CurrentOAMOffset. No shot, movement, inventory, lifetime, collision, upgrade, scratch or new RAM write is added.'))
    report = f'''Sophia exact-OAM emitter experiment - source-only, held, 2026-10-26

One finite private experiment is frozen. No native emulator was launched; no native grant is held. Production, Downloads/default, settings, Git and all prior receipts are untouched. Current parent ROM: {build['baseline_ROM_sha256']}. Private candidate: {build['candidate_ROM_sha256']}. Exact source/overlay/builds are under {a.prepared.as_posix()}.

The current body-exclusion evidence identifies the allocation owner: ExpandedDrawShots emits native Sophia cannons/missiles before DrawAllMetasprites reserves the player body. MetaspriteRenderLoop expands every source part and the whole used OAM ring is rotated. Actual nonwrapped Octopus2150 demonstrates that wrap is not the sole cause. Sophia3064..3066 carries three original horizontal-wave records, nine pre-body parts, and a partially admitted body. Those nine actual saved OAM tuples match the immutable horizontal record and pass this experiment's geometric bounds; saved-native-applicability.json binds the finite projection. It does not reconstruct complete native CPU state.

Remedies ranked before choosing this experiment:
1. A specialized emitter for the common three-part horizontal wave reduces generic interpretation work while preserving exact OAM. It has a small, source-verifiable scope and leaves all physics/projectile semantics intact. This experiment chooses only that CPU-work reduction.
2. Regrid projectile art to reduce transparent scanline occupancy. Width requires three eight-pixel columns in the horizontal wave, and moving transparent margins requires CHR/record changes plus all orientation/edge/pixel/fairness proof. This is not implemented or claimed as solved.
3. Change body/weapon priority or rotate/clamp differently. This changes physical admission fairness and repeats risks from the rejected e11 body ordering. The held 2dcac8cc guarded 32-pose selector costs +308..309 cycles on selected paths and does not cover Sophia. It is not reused here. Neither prior packet is relabeled or modified.

The only original runtime hook changes the three-byte JSR target inside ExpandedDrawShots after its real LDA0/STA R3 prefix. A new 87-byte gate occupies verified current3cee FF bytes in bank4 BF33..BF89, ending at BF8A before Darkwing's BF8B owner. A 201-byte emitter occupies bank36 D523..D5EB, ending at D5EC. Current bank36 art ends D522; the declared art region ends D5FF. Physical offset1600 onward is separately mapped A-window Water/Ryu/score code beginning B600 and remains byte-exact. Candidate changes290 ROM bytes total. The complete header/CHR, all72,800 old symbol values and {physical:,} old ROM symbol locations are exact. No c5 bank66 or heldChip bank78 region is touched.

Only original XgSOPHIAWeapon4Left/Right at C00A/C017 (frames4..7 aliases) use the fast path. It requires character11, the genuine mapped Sophia C-window, R3=0, X high0, Y high1, X low12..251, Y low3..255 and logical cursor<=243. It emits the same three tuples in the same reverse source order with identical wrap at physical OAM255, cursor, registers and flags. Literal constants are generated from those exact compiled original records. Missiles, other angles, impacts, other weapon modes/records, edges, invalid capacity, nonzero attributes and foreign identities all enter the untouched generic renderer. No new RAM, extra stack depth or projectile-state write is introduced.

Fresh copied-source baseline build exactly reproduces current3cee. Overlay is exactly smb1base-mmc5-expanded.cfg, src/entrypoint.s, src/expanded_weapons.s and new src/sophia_wave_emitter.s. Both standard flag-off builds remain exact: MMC3 d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb; MMC5 f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833.

Assembled CPU controls PASS: 9,378 selected-emitter cases cover all106 original table entries/39 unique records, both source facings, interior and clipping edges, capacity boundaries, rotated OAM, inactive rotation, nonzero attribute fallbacks, all256 incoming flag values on both hot records and five foreign families' actual original records. Full returned A/X/Y/P/SP, all nonstack application RAM, actual banks and ordered nonstack/OAM writes are exact, without return-flag or scratch exclusions. Another324 complete ExpandedDrawShots calls cover zero/one/three/ten active slots, all three Sophia cannon modes, both missile types, initial cursor0/160/244, rotation and producer order, plus original Pit/Rygar/Luigi/Bass/Ryu callers. Their complete public return and all application/write state are exact, so caller liveness is not inferred from a partial emitter stop. These are constructed source-valid CPU states, not natural item-acquisition evidence.

At754 actual instruction-boundary interruptions (377 compiled lag NMIs and377 compiled IRQs), foreground A/X/Y/P/SP, five farcall SMC operand bytes, actual A/C banks and shadows restore exactly. Resumed OAM/cursor/renderer inputs match the uninterrupted result. These synthetic cleared interrupt contexts do not establish real scanline31, maximum DMC, worst audio budget or native hardware timing.

Costs are intentionally not hidden. Hot horizontal waves save126..131 CPU cycles per shot. Unsupported records add19..30; foreign emitted shots add12; nonzero attributes add32..35; wrong high pages add37..47; X-edge fallbacks add51..58; Y-edge fallbacks add62..65; full-capacity fallback adds70..73 per attempted shot. The324 full callers range from -1310 to +700 cycles; zero active slots add0. All exact per-path cases remain in costs.json and the CPU receipt. The full-capacity penalty and foreign costs keep this proposal HELD for review. No second optimized variant or native trial is implied.

The experiment deliberately preserves per-publication OAM demand and first-eight fairness. It cannot make a starved body visible within the same committed image. Faster or slower source drawing may change which images are published before a deadline; unchanged tuples do not certify fairness or update/draw cadence across video frames. No recovered FPS/cadence, visibility improvement, starvation/flicker fix, full-roster completion or every-item fidelity claim follows. Movement, projectile states/lifetimes/collisions/upgrades and all art are unchanged. Tiny HUD, original areaFALSE/natural Buffer2 overlap and the earlier body-visibility negatives remain open.

Stable source-only commands, into fresh external directories:
python -B tools/audit/current3cee_sophia_emitter_candidate_v1.py --parent "{(D / 'root-chip-hud-composed-v1').as_posix()}" --output <fresh-external-candidate-directory>
python -B tools/audit/current3cee_sophia_emitter_cpu_v1.py --prepared "{a.prepared.as_posix()}" --output <fresh-external-CPU-directory>
No native command or launch authorization is provided.
'''
    (a.output / 'report.txt').write_text(report, encoding='utf-8')
    dependencies = {str(a.prepared / rel): h for rel, h in get(a.prepared / 'source-manifest.json').items()}
    # Correct the inventory root: source-manifest paths are relative to source/.
    dependencies = {str(a.prepared / 'source' / rel): h for rel, h in get(a.prepared / 'source-manifest.json').items()}
    parent = D / 'root-chip-hud-composed-v1'
    dependencies.update({str(parent / 'source' / rel): h for rel, h in get(parent / 'source-manifest.json').items()})
    for folder in [a.prepared, a.prepared / 'cpu-v1', a.prepared / 'overlay', a.output]:
        for file in folder.rglob('*') if folder.name == 'overlay' else folder.iterdir():
            if file.is_file():
                dependencies[str(file)] = sha(file)
    for file in [Path(__file__), ROOT / 'tools/audit/current3cee_sophia_emitter_candidate_v1.py',
                 ROOT / 'tools/audit/current3cee_sophia_emitter_cpu_v1.py', ROOT / 'tools/audit/check_tmnt_render_oa.py',
                 ROOT / 'tools/audit/link_pit_rygar_sophia_audit_cpu.py', ROOT / 'tools/audit/verify_native_relocation.py',
                 ROOT / 'docs/qa/parodius-guarded-body-source-2026-10-25.txt', ROOT / 'docs/qa/parodius-combined-cold-native-2026-10-25.txt',
                 D / 'current3cee-vehicle-visibility-final-v1/proof.json', probe / 'visibility-publications.jsonl',
                 probe / 'visibility-frames.jsonl', Path(inspect.getfile(mpu6502)), Path(sys.executable),
                 ROOT / 'tools/Windows/cc65/bin/cl65.exe']:
        dependencies[str(file)] = sha(file)
    assert all(sha(path) == digest for path, digest in dependencies.items())
    put(a.output / 'bindings.json', dependencies)
    put(a.output / 'proof.json', dict(
        passed=True, source_only=True, native_run=False, native_workers_held=0,
        adopted=False, held_for_review=True, baseline_ROM_sha256=build['baseline_ROM_sha256'],
        candidate_ROM_sha256=build['candidate_ROM_sha256'], source_layout_proof_sha256=sha(a.prepared / 'proof.json'),
        CPU_proof_sha256=sha(a.prepared / 'cpu-v1/proof.json'), different_ROM_bytes=290,
        old_symbol_values_exact=72800, old_ROM_symbol_locations_exact=physical,
        selected_emitter_cases=9378, full_caller_cases=324, actual_interrupt_cases=754,
        hot_cycle_delta=[-131, -126], full_caller_delta=[-1310, 700], foreign_per_shot_delta=12,
        full_capacity_per_attempt_delta=[70, 73], per_publication_OAM_and_fairness_unchanged=True,
        cadence_and_visibility_improvement_proved=False, starvation_fixed=False,
        report_sha256=sha(a.output / 'report.txt'), bindings=len(dependencies), bindings_sha256=sha(a.output / 'bindings.json'),
        limits='One source experiment only. Positive fallback/foreign costs held for review; no native grant, recovered cadence, body-priority change or production mutation.'))
    print(json.dumps(dict(passed=True, held_for_review=True, bindings=len(dependencies),
                          proof_sha256=sha(a.output / 'proof.json'), manifest_sha256=sha(a.output / 'bindings.json'),
                          report_sha256=sha(a.output / 'report.txt')), indent=2))


if __name__ == '__main__':
    main()

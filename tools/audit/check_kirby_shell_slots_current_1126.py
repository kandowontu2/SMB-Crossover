"""Current Kirby shell pool regression; disclosed linked CPU fixtures only.

Copies are earned by inhale/Down.  Direct CopyAttack/ Shots calls then isolate
all three source-allocated slots; these calls deliberately bypass the input
cooldown and do not claim a natural three-shot route or native Mesen coverage.
Only scene/NPC fixture data are staged; no copy, mouth, health, shot or outcome
is written.  Off-page NPC states are explicit rejection fixtures, not claimed
native lifecycle states.  Results stay in one in-memory receipt.
"""

from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import check_kirby_inhale_safety_1113 as Existing
import check_contra_force_combined_palette_1122 as Fixed
import compose_kirby_spiny_sound_1123 as Needles
import current_sonic_parent_rom_1122 as Sonic


N, Main, Bind, A = Existing.N, Existing.Main, Existing.Bind, Existing.A
ROM = Bind.NIGHTLY
PIN = '83b387931d2cf22981b6267fe062d246ba684d1bcb62e066d932dc9ae82aee40'
FIELDS = ('KbShotType', 'KbShotKind', 'KbShotAge', 'KbShotDir', 'KbShotX',
          'KbShotPage', 'KbShotY', 'KbShotVXHi', 'KbShotVXLo', 'KbShotFX',
          'KbShotVYHi', 'KbShotVYLo', 'KbShotFY')


def H(data):
    return sha256(data).hexdigest()


def bundle(raw):
    assert isinstance(raw, bytes) and len(raw) == 2097168 and H(raw) == PIN
    start = 16 + 74 * 8192
    assert raw[Needles.OFFSET:Needles.OFFSET + len(Needles.AFTER)] == Needles.AFTER
    restored = bytearray(raw)
    restored[Needles.OFFSET:Needles.OFFSET + len(Needles.AFTER)] = Needles.BEFORE
    shared = []
    # PRG74 also contains the shared native body gate changed by Sonic's1122
    # motion delivery.  These are the typed original preimages retained by its
    # strict59->32 inverse, rather than an invented historical Kirby image.
    for at, before, role in Sonic.PREIMAGES:
        if start <= at < start + 8192:
            shared.append(dict(offset=at - start, bytes=len(before), role=role,
                               current_SHA256=H(raw[at:at + len(before)]),
                               prior_SHA256=H(before)))
            restored[at:at + len(before)] = before
    assert len(shared) == 2
    assert H(restored[start:start + 8192]) == Existing.KIRBY_BANK_SHA
    main_at, prior_main = Fixed.BASE_PREIMAGES[0]
    layout = Fixed.Layout
    assert main_at == layout.offset(126, layout.MAIN)
    assert H(prior_main[:125]) == layout.OLD_FIXED_SHA
    current_main = raw[main_at:main_at + len(prior_main)]
    restored[main_at:main_at + len(prior_main)] = prior_main
    restored = bytes(restored)
    # Retained complete-bank, capture inverse/forward, red-catch inverse/forward,
    # Main125 and native body/input metadata checks apply to these preimages.
    b = Existing.bundle(restored)
    syms = dict(b['syms'])
    assert A.address(b, 'PauseRoutine') == layout.PAUSE
    syms['PauseRoutine'] = dict(syms['PauseRoutine'], val=hex(layout.NEW_PAUSE))
    pause_at = layout.offset(126, layout.NEW_PAUSE)
    prior_pause = prior_main[layout.PAUSE - layout.MAIN:layout.GRAPHICS - layout.MAIN - 1]
    assert raw[pause_at:pause_at + len(prior_pause)] == prior_pause
    return dict(b, raw=raw, syms=syms), dict(ROM_SHA256=PIN, Kirby_PRG74_SHA256=H(raw[start:start + 8192]),
        prior_PRG74_SHA256=Existing.KIRBY_BANK_SHA,
        needle_cue_change=dict(PC=Needles.PC, bytes=len(Needles.AFTER),
                               before=Needles.BEFORE.hex(), after=Needles.AFTER.hex()),
        shared_Sonic_native_body_spans=shared,
        all_other_PRG74_bytes_equal_prior_delivered_bank=True,
        actual_current_Main_SHA256=H(current_main),
        current_PauseRoutine=layout.NEW_PAUSE,
        retained_inhale_shell_capture_and_catch_source_authenticates=True)


def shots(m):
    result = []
    for slot in range(3):
        row = {name: N.get(m, name, slot) for name in FIELDS}
        row['slot'] = slot
        row['x'] = row['KbShotX'] + 256 * row['KbShotPage']
        row['vx'] = (row['KbShotVXHi'] + 128) % 256 - 128
        result.append(row)
    return result


def earn_pool(seed, family, face):
    name = 'GreenKoopa' if family == 2 else 'RedKoopa'
    m, earned = Existing.acquired(seed, name, face, swallow=True)
    assert N.get(m, 'KbCopy') == family and N.get(m, 'KbHealth') == 6
    launches = []
    for slot in range(3):
        before = shots(m)
        Bind.call(m, 'KbWeapons::CopyAttack')
        after = shots(m)
        assert after[slot]['KbShotType'] == 3 and after[slot]['KbShotKind'] == family
        assert after[slot]['KbShotAge'] == 0 and after[slot]['KbShotVXLo'] == 0
        assert after[slot]['vx'] == (3 if face == 1 else -3)
        assert all(before[i] == after[i] for i in range(slot)), ('Spawn overwrote live slot', family, face, slot)
        launches.append(dict(slot=slot, x=after[slot]['x'], age=after[slot]['KbShotAge']))
        if slot < 2:
            for _ in range(14):
                previous = shots(m)
                _, events = Bind.call(m, 'KbWeapons::Shots')
                assert not events['native_defeat']
                now = shots(m)
                for i in range(slot + 1):
                    assert now[i]['KbShotType'] == 3 and now[i]['x'] - previous[i]['x'] == now[i]['vx']
    full = shots(m)
    assert all(row['KbShotType'] == 3 for row in full)
    assert [row['KbShotAge'] for row in full] == [28, 14, 0]
    Bind.call(m, 'KbWeapons::CopyAttack')
    assert shots(m) == full, 'A fourth source allocation preserves the full projectile pool'
    return m, dict(earned=earned, source_allocations=launches, full_pool=full,
                   fourth_allocation_preserves_shots=True)


def target(m, ex, page):
    slot = Bind.SLOT
    Main.actor(m, A.address(m.bundle, 'Goomba'), ex, y=184, slot=slot)
    N.put(m, ObjectOffset=slot)
    Bind.call(m, 'CheckpointEnemyID', x=slot)
    Bind.put_slot(m, slot, Enemy_X_Position=ex & 255, Enemy_PageLoc=ex >> 8,
                  Enemy_Y_Position=184, Enemy_Y_HighPos=page, EnemyOffscrBitsMasked=0)
    assert N.get(m, 'Enemy_BoundBoxCtrl', slot) == 9


def regression(seed):
    rows, totals = [], Counter()
    for family, face in product((2, 3), (1, 2)):
        pool, earned = earn_pool(seed, family, face)
        for shot_slot, page in product(range(3), (0, 1, 2)):
            m = N.fork(pool)
            before = shots(m)
            chosen = before[shot_slot]
            next_x = chosen['x'] + chosen['vx']
            target(m, next_x + (4 if face == 1 else -4), page)
            _, events = Bind.call(m, 'KbWeapons::Shots')
            after = shots(m)
            hit = page == 1
            assert events['native_defeat'] == int(hit), (family, face, shot_slot, page, events,
                before, after, Bind.enemy(m))
            assert bool(N.get(m, 'Enemy_State', Bind.SLOT) & 32) == hit
            for i, row in enumerate(after):
                assert row['x'] - before[i]['x'] == before[i]['vx'], ('Three-pixel slot motion', family, face, i)
                assert row['KbShotVXLo'] == 0 and row['KbShotFX'] == 0
                assert row['KbShotKind'] == family
                assert row['KbShotType'] == (0 if hit and i == shot_slot else 3), ('Shot ownership', family, face, shot_slot, page, i)
                assert row['KbShotAge'] == before[i]['KbShotAge'] + 1
            assert N.get(m, 'KbHealth') == 6 and N.get(m, 'NumberofLives') == 2
            assert N.get(m, 'KbCopy') == family and N.get(m, 'KbMouth') == 0
            totals['cases'] += 1
            totals['visible_defeats' if hit else 'offpage_rejects'] += 1
            totals['checked_shot_updates'] += 3
            rows.append(dict(copy=family, facing=face, selected_shot_slot=shot_slot,
                             enemy_page=page, native_defeats=events['native_defeat'],
                             consumed=[i for i, row in enumerate(after) if row['KbShotType'] == 0],
                             positions_before=[row['x'] for row in before], positions_after=[row['x'] for row in after]))
        totals['earned_copies'] += 1
        totals['full_pool_rejects'] += int(earned['fourth_allocation_preserves_shots'])
    return dict(counts=dict(totals), cases=rows)


def main():
    raw = ROM.read_bytes()
    b, authentication = bundle(raw)
    seed, setup = Existing.Old.Wide.spawn_seed(b)
    result = regression(seed)
    assert ROM.read_bytes() == raw
    receipt = dict(passed=True, authentication=authentication, menu_parser_updates=setup,
                   settle_updates=40, **result, source_CPU=True, native_Mesen=False,
                   fixtures='Flat scene and explicit Goomba coordinates/Y-pages, including synthetic off-page rejection controls; copies earned by inhale/Down. Direct source attack/shot entry bypasses input cooldown to isolate every live slot.',
                   copy_mouth_health_projectile_and_outcome_seeds=0,
                   ROM_changes=0, outputs=0, source_SHA256=H(Path(__file__).read_bytes()))
    receipt['receipt_SHA256'] = H(json.dumps(receipt, sort_keys=True, separators=(',', ':')).encode())
    print('KIRBY_SHELL_SLOTS ' + json.dumps(receipt, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()

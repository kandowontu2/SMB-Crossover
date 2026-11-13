"""Compose a same-span red-shell catch and qualify installed native CPU paths."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

import check_kirby_red_return_1111 as Control
import check_kirby_red_sweep_1111 as Sweep
import check_sonic_native_effects_vectors_1110 as Clone
from check_steve_shatterhand_upgrade_transport_1111 import H


A, N = Control.Authority, Control.N
SOURCE = A.R/'tools/reference/kirby_red_catch_1112.s'
BANK, START, END, MOVE, KILL = 74, 0xa5d1, 0xa61b, 0xa61b, 0xa694
PREIMAGE = bytes.fromhex(
    'bd675cc903f0034cfba5bd5e5cc920b0034cfba5bd435cc575bd465ce55c'
    'a903b0034cf8a5a9fd9d4f5cbd675cc908f0034c1ba6bd5e5c2908d003'
    '4c16a6a901f0034c18a6a9ff9d555c')


def offset(pc):
    return 16+BANK*8192+(pc & 8191)


def authority(raw):
    assert A.sha(A.AUTHORITY) == A.AUTHORITY_ROM
    assert A.sha(A.AUTHORITY.with_suffix('.dbg')) == A.AUTHORITY_DBG
    bundle = A.scoped_load(A.AUTHORITY)
    assert A.address(bundle, 'KbWeapons::NotArc') == START
    assert A.address(bundle, 'KbWeapons::Move') == MOVE
    assert A.address(bundle, 'KbWeapons::Kill') == KILL
    assert A.location(bundle, 'KbWeapons::NotArc') == offset(START)
    assert raw[offset(MOVE):offset(MOVE)+7] == bytes.fromhex('18bd585c7d4c5c')
    assert raw[offset(KILL):offset(KILL)+5] == bytes.fromhex('a9009d405c')
    bundle['raw'] = raw
    return bundle


def proposal(raw):
    """Composable exact-preimage patch; preserve every byte outside 74 owned bytes."""
    bundle = authority(raw)
    assert len(PREIMAGE) == END-START == 74
    assert raw[offset(START):offset(END)] == PREIMAGE
    # Every displaced label is private to this envelope. External motion and
    # retirement entries retain their exact addresses and instructions.
    owned = raw[offset(0xa000):offset(0xa000)+8192]
    for target, expected in ((0xa5fb, (0xa5d8, 0xa5e2)),
                             (0xa5f8, (0xa5f3,)), (0xa616, (0xa60c,)),
                             (0xa618, (0xa613,))):
        needle = b'\x4c'+target.to_bytes(2, 'little')
        assert tuple(0xa000+i for i in range(len(owned)-2)
                     if owned[i:i+3] == needle) == expected
        assert b'\x20'+target.to_bytes(2, 'little') not in owned
    fields = {name: A.address(bundle, name) for name in
              ('KbShotKind', 'KbShotAge', 'KbShotX', 'KbShotPage',
               'KbShotVXHi', 'KbShotVYHi', 'Player_X_Position', 'Player_PageLoc')}
    fields.update(KirbyShotMove=MOVE, KirbyShotKill=KILL)
    definitions = ''.join(f'{name}=${value:04x}\n' for name, value in fields.items())
    linked = H.assemble(definitions+SOURCE.read_text(encoding='ascii'),
                        {'KIRBY_RETURN': (START, END-START)})
    code = linked['images']['KIRBY_RETURN']
    assert len(code) <= END-START
    payload = code.ljust(END-START, b'\xea')
    result = raw[:offset(START)]+payload+raw[offset(END):]
    return result, dict(file_offset=offset(START), preimage=PREIMAGE, replacement=payload,
                        worker_bytes=len(code), allocation_bytes=END-START,
                        source_SHA256=sha256(SOURCE.read_bytes()).hexdigest(), linked=linked)


def prepare(raw):
    bundle = authority(raw)
    seed = N.fresh(bundle)
    N.put(seed, SelectedCharacter=13, KbVariant=0, OperMode=1, OperMode_Task=3,
          GameEngineSubroutine=8, AreaType=1, KbHealth=6, NumberofLives=2,
          Player_Y_HighPos=1, Player_Y_Position=160, ScreenLeft_PageLoc=2,
          ScreenLeft_X_Pos=0, NmiDisable=255, ObjectOffset=0)
    seed[0x300:0x4a0] = bytes(0x1a0)
    return seed


def view(seed, image):
    model = N.fork(seed)
    model.bundle = dict(model.bundle, raw=image)
    return model


def set_player(model, world):
    N.put(model, Player_X_Position=world & 255, Player_PageLoc=world >> 8)


def move_slot(model, slot):
    if not slot:
        return
    for name in ('KbShotType', 'KbShotX', 'KbShotPage', 'KbShotY', 'KbShotVXLo',
                 'KbShotVXHi', 'KbShotVYLo', 'KbShotVYHi', 'KbShotFX', 'KbShotFY',
                 'KbShotAge', 'KbShotDir', 'KbShotHits', 'KbShotKind'):
        at = A.address(model.bundle, name)
        model[at+slot], model[at] = model[at], 0


def snapshot(model, cpu, events):
    return (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp, bytes(model[0:0x800]),
            bytes(model[0x5c00:0x5d00]), tuple(bytes(bank) for bank in model.ram),
            tuple(model.rawtags), tuple(model.ppu_log), events,
            tuple((at, value) for at, value in model.writes if 0x5113 <= at <= 0x5117))


def other_power_pairs(seed, trial):
    counts, cycles = Counter(), []
    for kind, age, slot, vx in product((k for k in range(14) if k != 3),
                                      (0, 6, 7, 14, 15, 22, 23, 30, 31, 32, 63, 88, 89),
                                      range(3), (3, -3)):
        pair = []
        for source in (seed, trial):
            model = N.fork(source)
            set_player(model, 600)
            Control.place_shot(model, 624, vx, age=age)
            N.put(model, KbShotKind=kind, KbShotVYLo=128, KbShotFY=96)
            move_slot(model, slot)
            cpu, events = Control.call(model, 'KbWeapons::Shots')
            pair.append((snapshot(model, cpu, events), cpu.processorCycles))
        assert pair[0][0] == pair[1][0], (kind, age, slot, vx,
            [i for i, (left, right) in enumerate(zip(pair[0][0], pair[1][0])) if left != right])
        counts[str(kind)] += 1
        cycles.append(pair[1][1]-pair[0][1])
    return dict(pairs=sum(counts.values()), kinds=dict(counts),
                cycle_delta=[min(cycles), max(cycles)], complete_register_RAM_parity=True)


def red_contact_pairs(seed, trial):
    counts, cycles = Counter(), []
    for vx, sx, ey, box, age in product((3, -3), (621, 626, 648, 651),
                                       (150, 151, 168, 178), (3, 9), (5, 30, 31, 67, 88)):
        pair = []
        for source in (seed, trial):
            model = N.fork(source)
            set_player(model, 800 if vx > 0 else 400)
            Control.place_enemy(model, 626, ey)
            Control.put_slot(model, Control.SLOT, Enemy_BoundBoxCtrl=box,
                             Enemy_ID=6 if box == 9 else 3)
            Control.place_shot(model, sx-vx, vx, age=age)
            cpu, events = Control.call(model, 'KbWeapons::Shots')
            pair.append((snapshot(model, cpu, events), cpu.processorCycles))
        assert pair[0][0] == pair[1][0], (vx, sx, ey, box, age,
            [i for i, (left, right) in enumerate(zip(pair[0][0], pair[1][0])) if left != right])
        counts['hit' if pair[0][0][10]['native_defeat'] else 'miss'] += 1
        cycles.append(pair[1][1]-pair[0][1])
    assert counts['hit'] and counts['miss']
    return dict(pairs=dict(counts), cycle_delta=[min(cycles), max(cycles)],
                complete_register_RAM_parity=True)


def lifecycle(seed, trial):
    counts = Counter()
    # Native puff and star motion bypass/enter the envelope differently.
    # Red TTL remains authoritative when the shell cannot reach Kirby.
    for shot_type, kind, age, slot in product((1, 2, 3), (0, 3, 8),
                                             (7, 8, 11, 13, 15, 22, 23, 88, 89), range(3)):
        pair = []
        for source in (seed, trial):
            model = N.fork(source)
            set_player(model, 800)
            Control.place_shot(model, 624, 3, age=age)
            N.put(model, KbShotType=shot_type, KbShotKind=kind)
            move_slot(model, slot)
            cpu, events = Control.call(model, 'KbWeapons::Shots')
            pair.append(snapshot(model, cpu, events))
        assert pair[0] == pair[1], (shot_type, kind, age, slot)
        counts['puff_star_TTL_pairs'] += 1

    for caught_slot in range(3):
        model = N.fork(trial)
        set_player(model, 600)
        N.put(model, ObjectOffset=17, KbCopy=3, KbHealth=6, NumberofLives=2)
        for slot in range(3):
            Control.put_slot(model, slot, KbShotType=3, KbShotKind=8,
                             KbShotX=624 & 255, KbShotPage=624 >> 8,
                             KbShotY=180, KbShotVXHi=3, KbShotAge=7)
        Control.put_slot(model, caught_slot, KbShotKind=3, KbShotX=601 & 255,
                         KbShotPage=601 >> 8, KbShotAge=31)
        _, events = Control.call(model, 'KbWeapons::Shots')
        assert not events and N.get(model, 'ObjectOffset') == 17
        assert (N.get(model, 'KbCopy'), N.get(model, 'KbHealth'), N.get(model, 'NumberofLives')) == (3, 6, 2)
        for slot in range(3):
            if slot == caught_slot:
                assert (N.get(model, 'KbShotType', slot), N.get(model, 'KbShotAge', slot),
                        Control.world(model, 'KbShotX', 'KbShotPage', slot)) == (0, 32, 601)
            else:
                assert (N.get(model, 'KbShotType', slot), N.get(model, 'KbShotAge', slot),
                        Control.world(model, 'KbShotX', 'KbShotPage', slot),
                        N.get(model, 'KbShotY', slot)) == (3, 8, 627, 181)
        counts['mixed_slot_catch_cleanup'] += 1
    return dict(counts)


def catches(seed):
    cases = Counter()
    for slot, player, delta, age in product(range(3), (0, 2, 253, 255, 256, 600, 65533, 65535),
                                           (-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5), (30, 31, 32, 67, 88)):
        world = player+delta
        if not 0 <= world <= 65535:
            continue
        model = N.fork(seed)
        set_player(model, player)
        Control.place_shot(model, world, 3 if delta >= 0 else -3, age=age)
        move_slot(model, slot)
        # Keep the screen admission on the same page as the shot; a catch
        # must occur before the unchanged native camera admission.
        N.put(model, ScreenLeft_PageLoc=world >> 8, ScreenLeft_X_Pos=0)
        _, events = Control.call(model, 'KbWeapons::Shots')
        want = age+1 >= 32 and abs(delta) <= 3
        actual = N.get(model, 'KbShotType', slot)
        if want:
            assert actual == 0 and N.get(model, 'KbShotX', slot) == (world & 255)
            assert N.get(model, 'KbShotPage', slot) == world >> 8
            cases['caught'] += 1
        else:
            velocity = (3 if delta >= 0 else -3) if age+1 < 32 else (-3 if delta >= 0 else 3)
            expected = (world+velocity) & 65535
            assert Control.world(model, 'KbShotX', 'KbShotPage', slot) == expected
            cases['moving'] += 1
        assert N.get(model, 'KbShotAge', slot) == age+1
        assert not events
    assert cases['caught'] and cases['moving']
    return dict(cases)


def traces(seed, *, fixed):
    rows = []
    for player, facing in product((255, 256, 490, 600), (1, 2)):
        model = N.fork(seed)
        N.put(model, ScreenLeft_PageLoc=max(0, (player-100) >> 8), ScreenLeft_X_Pos=(player-100) & 255)
        Control.launch(model, player, facing)
        positions = []
        catch_age = None
        for age in range(1, 91):
            _, events = Control.call(model, 'KbWeapons::Shots')
            current = Control.shot(model)
            assert not events
            if not current['type']:
                catch_age = age
                break
            positions.append(current['x'])
            assert abs(current['vx']) == 3 and current['fraction'] == 0
        if fixed:
            assert catch_age is not None and 32 < catch_age < 90, (player, facing, positions)
            # One repeated position straddles the intentional outbound turn.
            # The inbound leg itself must never reverse or bounce.
            inbound = positions[31:]
            expected_step = -3 if facing == 1 else 3
            assert len(positions) < 70 and all(b-a == expected_step
                                             for a, b in zip(inbound, inbound[1:]))
        else:
            assert catch_age == 90
            assert len(set(positions[-12:])) <= 2
        rows.append(dict(player=player, facing=facing, retirement_age=catch_age,
                         last_positions=positions[-4:]))
    return rows


def vectors(seed, info):
    irq = Clone.ISR
    irq.DEEPEST = None
    irq.PATHS.clear()
    reached, stats = set(), Counter()

    def live(model, cpu):
        return (irq.regs(cpu), bytes(model[3:11]), bytes(model[0x15a:0x17b]),
                bytes(model[0x101+cpu.sp:0x200]), bytes(model[0x200:0x800]),
                bytes(model[0x5c00:0x5d00]), tuple(bytes(bank) for bank in model.ram),
                tuple(model.rawtags))

    def observe(model, cpu):
        if model.rawtags[1] != 202 or not START <= cpu.pc < END or cpu.pc in reached:
            return
        reached.add(cpu.pc)
        baseline, plain = Clone.clone(model, cpu)
        irq.finish(baseline, plain, Sweep.STOP)
        for kind in ('NMI', 'IRQ'):
            branch, cut = Clone.clone(model, cpu)
            before = live(branch, cut)
            assert irq.isr(branch, cut, kind, Sweep.STOP) == 'returned'
            assert live(branch, cut) == before, (kind, hex(cpu.pc), 'return')
            irq.finish(branch, cut, Sweep.STOP)
            assert live(branch, cut) == live(baseline, plain), (kind, hex(cpu.pc), 'continuation')
            stats[kind] += 1

    with patch.object(irq, 'regs', side_effect=lambda c: (c.pc,c.a,c.x,c.y,c.p & 0xef,c.sp)), \
            patch.object(irq, 'clone', side_effect=Clone.clone):
        for kind, age, player, world in ((3, 5, 600, 620), (3, 31, 600, 620),
                                        (3, 31, 600, 595), (3, 31, 600, 599),
                                        (3, 31, 600, 602), (3, 31, 256, 512),
                                        (3, 31, 600, 256), (8, 6, 600, 624),
                                        (8, 7, 600, 624), (2, 5, 600, 624)):
            model = N.fork(seed)
            set_player(model, player)
            Control.place_shot(model, world, 3, age=age)
            N.put(model, KbShotKind=kind, DisableScreenFlag=0, Mirror_PPUMASK=30, NmiDisable=255)
            Control.call(model, 'KbWeapons::Shots', observe=observe)
        assert irq.DEEPEST is not None
        model, cpu, entry, stop = irq.DEEPEST
        branch, cut = Clone.clone(model, cpu)
        baseline, plain = Clone.clone(model, cpu)
        before = live(branch, cut)
        assert irq.isr(branch, cut, 'IRQ') == 'returned' and live(branch, cut) == before
        for target in ((entry[0], entry[-1]), stop):
            irq.finish(baseline, plain, target)
            irq.finish(branch, cut, target)
            assert live(branch, cut) == live(baseline, plain)
    symbols = info['linked']['symbols']
    assert all(symbols[name] in reached for name in
               ('KirbyReturnMotion', 'KirbyShellLeft', 'KirbyShellRightFar',
                'KirbyShellLeftFar', 'KirbyShellSpeed', 'KirbyShellCatch', 'KirbyWaveMotion'))
    assert stats['NMI'] == stats['IRQ'] >= 30
    return dict(cuts=dict(stats), reached_instruction_starts=len(reached), nested_IRQ=1,
                deepest_parent_SP=cpu.sp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Control.NIGHTLY)
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    candidate, info = proposal(raw)
    before = prepare(raw)
    after = view(before, candidate)
    print(json.dumps(dict(passed=True, parent_SHA256=sha256(raw).hexdigest(),
                          candidate_SHA256=sha256(candidate).hexdigest(),
                          worker_bytes=info['worker_bytes'], allocation_bytes=info['allocation_bytes'],
                          original_turns=Control.turns(before), fixed_turns=Control.turns(after),
                          original_oscillation=traces(before, fixed=False),
                          fixed_return=traces(after, fixed=True), boundary_catches=catches(after),
                          other_powers=other_power_pairs(before, after),
                          red_enemy_contacts=red_contact_pairs(before, after),
                          green_native_contacts=Sweep.green_full_pairs(before, after),
                          native_corner_contacts=Control.corners(after, (2, 9, 14, 21), swept=True),
                          lifecycle=lifecycle(before, after),
                          interrupts=vectors(after, info),
                          source_SHA256=info['source_SHA256'], output_files=0)), flush=True)


if __name__ == '__main__':
    main()

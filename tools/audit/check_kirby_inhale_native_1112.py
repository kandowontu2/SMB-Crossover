"""Audit installed inhale/body/injury ordering with bounded native CPU fixtures."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from unittest.mock import patch

import check_kirby_owner_main_1101_v2 as Main
import check_kirby_red_return_1111 as Bind
import check_kirby_inhale_vertical_wide_1111 as Wide
import check_sonic_native_effects_vectors_1110 as Vectors
from check_steve_shatterhand_upgrade_transport_1111 import H


A, N = Bind.Authority, Bind.N
ENEMIES = ('GreenKoopa', 'BuzzyBeetle', 'RedKoopa', 'HammerBro', 'Goomba',
           'Bloober', 'BulletBill_FrenzyVar', 'GreyCheepCheep', 'RedCheepCheep',
           'Podoboo', 'PiranhaPlant', 'GreenParatroopaJump', 'RedParatroopa',
           'GreenParatroopaFly', 'Lakitu', 'Spiny', 'FlyingCheepCheep',
           'BulletBill_CannonVar')
EXPECTED = dict(zip(ENEMIES, (2, 4, 3, 5, 1, 6, 14, 7, 8, 13, 12, 9, 9, 9, 10, 11, 8, 14)))
BODY = bytes.fromhex(
    'ad165cd0034c31aa38602000a0d0034cf4aaade95ff0034c9aaaad0b5cc901f0034c9aaaa5dc2940d0034cf4aa'
    '20f6aab0034cf4aab57638e5758d1e5cb55de55c8d1f5cad3e05c901d0034c86aa38a900ed1e5c8d1e5ca900'
    'ed1f5c8d1f5cad1f5cf0034cf4aaad1e5cc93990034cf4aa3860ad0b5cc905d0034ce3aac904f0034cf4aaad01'
    '5cc904f0034cc0aab517c90cd0034cf4aa3860c901d0034ce3aac909d0034ce3aac90bd0034ce3aac90cd0034c'
    'e3aac90ef0034cf4aa8a48a50d48860d20f59a68850d68aa38601860')
SOURCE = A.R/'tools/reference/kirby_inhale_capture_frame_1112.s'
CLOCK = (0xa092, bytes.fromhex('ad0c5cd0034cb1a0ce0c5cf0034cb1a0ad0b5cc901d0034cb1a0a9008d0b5c'))
TAIL = (0xa31a, bytes.fromhex('a9008d0b5ca9018d04014c83a3'))


def proposal(raw):
    """Compose the capture-frame fix against the installed Kirby preimages."""
    b = bundle(raw)
    assert A.address(b, 'KbWeapons::Input') == 0xa0b1
    assert A.address(b, 'KbWeapons::PullReturn') == 0xa383
    assert A.address(b, 'KbWeapons::Capture') == 0xa2ff
    assert A.address(b, 'KbWeapons::PullNext') == 0xa327
    code = raw[Wide.offset(0xa000):Wide.offset(0xa000)+8192]
    assert code[0x314:0x31a] == bytes.fromhex('ae1b5c202f8d')
    for target, expected in ((0xa0a2, ()), (0xa0ac, ()), (0xa31f, ())):
        refs = tuple(0xa000+i for i in range(len(code)-2) if code[i] in (0x4c, 0x20)
                     and code[i+1:i+3] == target.to_bytes(2, 'little'))
        assert refs == expected
    spans = dict(ACTION_CLOCK=CLOCK, CAPTURE_TAIL=TAIL)
    bindings = {name: A.address(b, name) for name in
                ('KbAction', 'KbActionAge', 'KbMouth', 'Square2SoundQueue')}
    bindings.update(KirbyWeaponInput=0xa0b1, KirbyPullReturn=0xa383)
    definitions = ''.join(f'{name}=${value:04x}\n' for name, value in bindings.items())
    p = H.assemble(definitions+SOURCE.read_text(encoding='ascii'),
                   {name: (start, len(old)) for name, (start, old) in spans.items()})
    image, edits = bytearray(raw), []
    for name, (start, old) in spans.items():
        at = Wide.offset(start)
        assert raw[at:at+len(old)] == old
        body = p['images'][name]
        assert len(body) <= len(old)
        body = body.ljust(len(old), b'\xea')
        image[at:at+len(old)] = body
        edits.append((at, old, body))
    return bytes(image), dict(edits=edits, used=p['used'], source_SHA256=sha256(SOURCE.read_bytes()).hexdigest())


def bundle(raw):
    assert A.sha(A.AUTHORITY) == A.AUTHORITY_ROM
    assert A.sha(A.AUTHORITY.with_suffix('.dbg')) == A.AUTHORITY_DBG
    result = A.scoped_load(A.AUTHORITY)
    for name in ('KbFamilyForEnemy', 'KbInputs', 'KbMovement', 'KbInjuryStart',
                 'GuestBodyContactBridge', 'KbBodyDispatch'):
        start = A.location(result, name)
        size = int(result['syms'][name]['size'], 0)
        assert size > 0 and raw[start:start+size] == result['raw'][start:start+size], name
    # The current GameLoop has the qualified post-1108 input factoring. Its
    # public address and caller remain fixed; authenticate the current body.
    start = A.location(result, 'GameLoop')
    assert sha256(raw[start:start+125]).hexdigest() == '7691d0dc57393348bcd6ade38bc74c9e4d35388a729a2fe8b2c3824d488f5b44'
    start = A.location(result, 'KbBodyContact')
    assert len(BODY) == int(result['syms']['KbBodyContact']['size'], 0)
    assert raw[start:start+len(BODY)] == BODY
    result['raw'] = raw
    return result


def eligible(model, slot):
    flag = N.get(model, 'Enemy_Flag', slot)
    state = N.get(model, 'Enemy_State', slot)
    kind = N.get(model, 'Enemy_ID', slot)
    family = next((EXPECTED[name] for name in ENEMIES if A.address(model.bundle, name) == kind), 0)
    family = family if flag and not flag & 128 and not state & 32 and (kind != 6 or state < 2) else 0
    dx = Bind.world(model, 'Enemy_X_Position', 'Enemy_PageLoc', slot)-Bind.world(model, 'Player_X_Position', 'Player_PageLoc')
    if N.get(model, 'PlayerFacingDir') != 1:
        dx = -dx
    dy = 256*N.get(model, 'Enemy_Y_HighPos', slot)+N.get(model, 'Enemy_Y_Position', slot)-(
         256*N.get(model, 'Player_Y_HighPos')+N.get(model, 'Player_Y_Position'))
    return dict(family=family, dx=dx, dy=dy, in_range=bool(family and 0 <= dx <= 56 and -4 <= dy <= 20
                and N.get(model, 'Enemy_Y_HighPos', slot) == 1))


def families(seed):
    counts = Counter()
    for kind, flag, state, slot in product(range(256), (0, 1, 128), (0, 1, 2, 32, 128), (0, 3, 5)):
        model = N.fork(seed)
        Bind.put_slot(model, slot, Enemy_ID=kind, Enemy_Flag=flag, Enemy_State=state)
        want = eligible(model, slot)['family']
        cpu, _ = Bind.call(model, 'KbFamilyForEnemy', x=slot)
        assert cpu.a == want and bool(cpu.p & 2) == (want == 0), (kind, flag, state, slot, cpu.a, want)
        counts['accepted' if want else 'rejected'] += 1
    return dict(counts)


class Observe:
    def __init__(self, b):
        names = ('KbInputs', 'KbWeapons', 'KbWeapons::Suction', 'KbWeapons::Capture',
                 'KbBodyContact', 'KbInjuryStart', 'EnemyStomped', 'EraseEnemyObject', 'InjurePlayer')
        self.points = {(A.address(b, name), ((A.location(b, name)-16)//8192)|128): name
                       for name in names}
        self.events = []
        self.pending = None
        self.errors = []

    def __call__(self, model, cpu, instruction):
        if self.pending and (cpu.pc, cpu.sp) == self.pending['return']:
            event = self.pending
            event['protected'] = bool(cpu.p & 1)
            if event['eligible']['in_range'] and event['action'] == 1 and event['buttons'] & 64:
                if not event['protected']:
                    self.errors.append(event)
            self.pending = None
        if cpu.pc < 0x8000:
            return
        name = self.points.get((cpu.pc, model.rawtags[(cpu.pc-0x8000)//8192]))
        if not name:
            return
        slot = cpu.x if name in ('KbBodyContact', 'KbWeapons::Capture', 'EraseEnemyObject') \
            else N.get(model, 'ObjectOffset')
        event = dict(name=name, instruction=instruction, slot=slot, action=N.get(model, 'KbAction'),
                     age=N.get(model, 'KbActionAge'), fresh=N.get(model, 'KbFresh'),
                     buttons=N.get(model, 'SavedJoypadBits'), health=N.get(model, 'KbHealth'),
                     player_x=Bind.world(model, 'Player_X_Position', 'Player_PageLoc'),
                     player_y=256*N.get(model, 'Player_Y_HighPos')+N.get(model, 'Player_Y_Position'))
        if 0 <= slot < 6:
            event['eligible'] = eligible(model, slot)
        self.events.append(event)
        if name == 'KbBodyContact':
            assert self.pending is None
            ret = model[0x100+cpu.sp+1]+256*model[0x100+cpu.sp+2]+1
            event['return'] = ret, cpu.sp+2
            self.pending = event
        elif name in ('InjurePlayer', 'KbInjuryStart') and event.get('eligible', {}).get('in_range') \
                and event['action'] == 1 and event['buttons'] & 64 and not N.get(model, 'KbVariant') \
                and not N.get(model, 'MmUnderwater'):
            self.errors.append(dict(reason='eligible-inhale-reached-injury', **event))


def one_main(seed, name, face, gap, mode, buttons, *, water=False, held=0, initialize=True, dy=8,
             second=None, observe=None, return_model=False):
    model = N.fork(seed)
    Main.scene(model, face)
    N.put(model, CrossoverBehaviorVersion=mode, AreaType=0 if water else 1,
          SwimmingFlag=int(water))
    Main.actor(model, A.address(model.bundle, name), 112+gap*(1 if face == 1 else -1))
    if initialize:
        Bind.call(model, 'CheckpointEnemyID')
        # The fixture sets a legal visible body position after native init;
        # no ability, health, collision outcome, or executable bytes are seeded.
        Bind.put_slot(model, 0, Enemy_Y_Position=176+dy, Enemy_Y_HighPos=1, EnemyOffscrBitsMasked=0)
        if name == 'BulletBill_CannonVar':
            Bind.put_slot(model, 0, Enemy_State=1, Enemy_BoundBoxCtrl=9)
    if second:
        target, distance, vertical = second
        Main.actor(model, A.address(model.bundle, target), 112+distance*(1 if face == 1 else -1),
                   y=176+vertical, slot=3)
    events, counts = [], Counter()
    for _ in range(held+1):
        Main.keys(model, buttons)
        observer = Observe(model.bundle)
        def watch(m, cpu, step):
            observer(m, cpu, step)
            if observe:
                observe(m, cpu)
        Main.call(model, 'GameLoop', watch)
        assert not model.blocked, model.blocked
        assert not observer.errors, observer.errors
        events.extend(observer.events)
        counts.update(event['name'] for event in observer.events)
        if N.get(model, 'KbMouth') or N.get(model, 'KbHealth') != 6:
            break
        N.consume(model)
    row = dict(name=name, face=face, gap=gap, mode=mode, buttons=buttons, water=water,
                health=N.get(model, 'KbHealth'), hurt=N.get(model, 'KbHurt'),
                mouth=N.get(model, 'KbMouth'), copy=N.get(model, 'KbMouthCopy'),
                action=N.get(model, 'KbAction'), age=N.get(model, 'KbActionAge'),
                flag=N.get(model, 'Enemy_Flag'), counts=dict(counts), events=events)
    return (row, model) if return_model else row


def matrix(seed, *, water=False, held=0, vertical=False):
    counts, rows = Counter(), []
    gaps, dys = ((6,), (-5, -4, 8, 20, 21)) if vertical else ((6, 12, 14, 28, 56, 57, -6), (8,))
    for name, face, gap, mode, buttons, dy in product(ENEMIES, (1, 2), gaps, (0, 1), (0, 64), dys):
        row = one_main(seed, name, face, gap, mode, buttons, water=water, held=held, dy=dy)
        counts['cases'] += 1
        counts['injury' if row['health'] < 6 else 'uninjured'] += 1
        counts['body_calls'] += row['counts'].get('KbBodyContact', 0)
        counts['capture'] += row['counts'].get('KbWeapons::Capture', 0)
        if row['health'] < 6:
            counts[f"{'front' if gap >= 0 else 'rear'}_{'B' if buttons else 'released'}_injury"] += 1
        if row['health'] < 6 and buttons == 64 and gap >= 0:
            counts['front_B_injury'] += 1
            if len(rows) < 8:
                rows.append({**row, 'events': [event for event in row['events'] if event['name'] in
                             ('KbWeapons::Capture', 'KbBodyContact', 'KbInjuryStart')]})
    return dict(counts=dict(counts), front_B_injuries=rows)


def matrix_parity(before, after, *, water=False, vertical=False, held=0, face_filter=None):
    counts = Counter()
    gaps = (6,) if vertical else (6, 12, 14, 28, 56, 57, -6)
    heights = (-5, -4, 8, 20, 21) if vertical else (8,)
    fields = ('health', 'hurt', 'mouth', 'copy', 'flag', 'counts')
    faces = (face_filter,) if face_filter else (1, 2)
    for enemy, face, gap, mode, buttons, dy in product(ENEMIES, faces, gaps, (0, 1), (0, 64), heights):
        key = enemy, face, gap, mode, buttons
        old, fixed = (one_main(seed, *key, water=water, held=held, dy=dy) for seed in (before, after))
        if held and not water and not vertical and key == ('Lakitu', 1, 14, mode, 64):
            assert (old['health'], old['mouth'], fixed['health'], fixed['mouth']) == (5, 0, 6, 19)
            counts['corrected'] += 1
        else:
            assert tuple(old[k] for k in fields) == tuple(fixed[k] for k in fields), (key, dy, old, fixed)
            if not old['mouth']:
                assert (old['action'], old['age']) == (fixed['action'], fixed['age']), (key, dy, old, fixed)
            counts['matched'] += 1
        if old['counts'].get('KbWeapons::Capture'):
            counts['captures'] += 1
    return dict(counts)


def remap(seed, image):
    model = N.fork(seed)
    model.bundle = dict(seed.bundle, raw=image)
    for window, tag in enumerate(model.rawtags):
        if tag & 128:
            model.raw_page(window, tag)
    return model


def same_capture_frame(before, after):
    evidence = []
    for mode in (0, 1):
        old = one_main(before, 'Lakitu', 1, 14, mode, 64, held=8)
        fixed, model = one_main(after, 'Lakitu', 1, 14, mode, 64, held=8, return_model=True)
        for row in (old, fixed):
            assert row['counts']['KbWeapons::Capture'] == row['counts']['EraseEnemyObject'] == 1, row
            assert row['flag'] == 1 and row['copy'] == 11, row
            capture = next(event for event in row['events'] if event['name'] == 'KbWeapons::Capture')
            assert capture['slot'] == 1 and capture['eligible']['family'] == 11
        assert (old['health'], old['hurt'], old['mouth']) == (5, 120, 0), old
        assert (fixed['health'], fixed['hurt'], fixed['mouth'], fixed['action'], fixed['age']) == (6, 0, 19, 1, 1), fixed
        assert not fixed['counts'].get('KbInjuryStart')
        collision = [event for event in fixed['events'] if event['name'] == 'KbBodyContact'][-1]
        assert collision['slot'] == 0 and collision['protected'] and collision['eligible']['family'] == 10
        N.consume(model)
        Main.keys(model, 64)
        followup = Observe(model.bundle)
        Main.call(model, 'GameLoop', followup)
        assert not followup.errors and not model.blocked
        assert N.get(model, 'KbHealth') == 5 and N.get(model, 'KbMouth') == 0
        assert any(event['name'] == 'KbBodyContact' and event['action'] == 0 and not event['protected']
                   for event in followup.events)
        evidence.append(dict(mode=mode, capture='Spiny', remaining_contact='Lakitu',
                             old_health=5, fixed_capture_health=6, next_held_update_health=5,
                             capture_slot=capture['slot'], body_slot=collision['slot']))
    return evidence


def capture_controls(before, after):
    counts = Counter()
    controls = (('Goomba', 6, 8, False), ('Goomba', -6, 8, True), ('GreenKoopa', 6, 21, True),
                ('BowserFlame', 6, 8, True))
    for mode, face, (enemy, gap, dy, injured) in product((0, 1), (1, 2), controls):
        args = enemy, face, gap, mode, 64
        old, fixed = (one_main(seed, *args, second=('Goomba', 8, 8), dy=dy,
                               initialize=enemy != 'BowserFlame') for seed in (before, after))
        assert old['counts']['KbWeapons::Capture'] == fixed['counts']['KbWeapons::Capture'] == 1
        if injured:
            assert (old['health'], fixed['health'], old['mouth'], fixed['mouth']) == (5, 5, 0, 0), (old, fixed)
            counts[f'damage_{enemy}_{gap}_{dy}'] += 1
        else:
            assert (old['health'], fixed['health'], old['mouth'], fixed['mouth']) == (5, 6, 0, 7), (old, fixed)
            counts['two_edible_targets'] += 1
    return dict(counts)


def action_lifecycle(before, after):
    counts = Counter()
    for face, mode, sequence in product((1, 2), (0, 1), ((4,), (64, 4), (0, 4), (0, 64), (0, 0, 0))):
        states = []
        for seed in (before, after):
            capture, model = one_main(seed, 'Goomba', face, 6, mode, 64, return_model=True)
            assert capture['mouth'] == 7 and capture['copy'] == 1 and capture['health'] == 6
            for buttons in sequence:
                N.consume(model)
                Main.keys(model, buttons)
                observer = Observe(model.bundle)
                Main.call(model, 'GameLoop', observer)
                assert not observer.errors and not model.blocked
            names = ('KbMouth', 'KbMouthCopy', 'KbCopy', 'KbAction', 'KbActionAge', 'KbHealth', 'KbHurt',
                     'KbShotType', 'KbShotKind', 'KbShotAge', 'KbShotX', 'KbShotPage', 'KbShotY')
            states.append(tuple(N.get(model, n) for n in names))
        old, fixed = states
        assert old[:4] == fixed[:4] and old[5:] == fixed[5:], (sequence, old, fixed)
        if sequence[-1] == 4:
            assert fixed[:5] == (0, 1, 1, 3, 24)
            counts['swallow'] += 1
        elif sequence[-1] == 64:
            assert fixed[:5] == (0, 1, 0, 2, 24) and fixed[7] == 1
            counts['spit'] += 1
        else:
            assert fixed[:5] == (7, 1, 0, 0, 0)
            counts['mouth_hold'] += 1
    return dict(counts)


def vectors(seed):
    irq = Vectors.ISR
    irq.DEEPEST = None
    irq.PATHS.clear()
    # Main.call stops immediately after the actual caller's PLA.
    idle = A.address(seed.bundle, 'IdleLoop')
    loop = A.address(seed.bundle, 'GameLoop')
    caller = bytes(seed[idle:idle+16]).index(b'\x20'+loop.to_bytes(2, 'little'))
    stop = idle+caller+4, 253
    cuts, reached = Counter(), set()

    def live(model, cpu):
        return (irq.regs(cpu), bytes(model[0x101+cpu.sp:0x200]), Main.fg(model))

    def watch(model, cpu):
        if model.rawtags[1] != 202 or cpu.pc in reached or not any(
                start <= cpu.pc < start+len(old) for start, old in (CLOCK, TAIL)):
            return
        reached.add(cpu.pc)
        plain_model, plain_cpu = Vectors.clone(model, cpu)
        irq.finish(plain_model, plain_cpu, stop)
        for kind in ('NMI', 'IRQ'):
            branch, cut = Vectors.clone(model, cpu)
            old = live(branch, cut)
            assert irq.isr(branch, cut, kind, stop) == 'returned'
            assert live(branch, cut) == old, (kind, hex(cpu.pc), 'ISR return')
            irq.finish(branch, cut, stop)
            assert live(branch, cut) == live(plain_model, plain_cpu), (kind, hex(cpu.pc), 'continuation')
            cuts[kind] += 1

    with patch.object(irq, 'regs', side_effect=lambda c: (c.pc, c.a, c.x, c.y, c.p & 0xef, c.sp)), \
            patch.object(irq, 'clone', side_effect=Vectors.clone):
        _, held = one_main(seed, 'Goomba', 1, 6, 1, 64, observe=watch, return_model=True)
        N.consume(held)
        Main.keys(held, 4)
        Main.call(held, 'GameLoop', lambda m, c, _: watch(m, c))
        one_main(seed, 'Goomba', 1, 76, 1, 64, held=8, observe=watch)
        assert irq.DEEPEST is not None
        m, c, entry, target = irq.DEEPEST
        branch, cut = Vectors.clone(m, c)
        plain_model, plain_cpu = Vectors.clone(m, c)
        old = live(branch, cut)
        assert irq.isr(branch, cut, 'IRQ') == 'returned' and live(branch, cut) == old
        for at in ((entry[0], entry[-1]), target):
            irq.finish(branch, cut, at)
            irq.finish(plain_model, plain_cpu, at)
            assert live(branch, cut) == live(plain_model, plain_cpu)
    assert cuts['NMI'] == cuts['IRQ'] >= 19, [hex(pc) for pc in sorted(reached)]
    return dict(cuts=dict(cuts), nested_IRQ=1, deepest_parent_SP=c.sp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Bind.NIGHTLY)
    parser.add_argument('--part', choices=('families', 'land', 'water', 'vertical', 'capture'), default='land')
    parser.add_argument('--held', type=int, default=0)
    parser.add_argument('--candidate', action='store_true')
    parser.add_argument('--compare', action='store_true')
    parser.add_argument('--face', type=int, choices=(1, 2), help='Limit a paired matrix to one facing.')
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    b = bundle(raw)
    if args.part == 'families':
        evidence = families(N.fresh(b))
        origin = None
    else:
        seed, origin = Wide.spawn_seed(b)
        origin = dict(menu_slot=12, parser_updates=origin, settle_updates=40)
        print(json.dumps(dict(event='cold', **origin)), flush=True)
        if args.part == 'capture':
            image, info = proposal(raw)
            trial = remap(seed, image)
            evidence = dict(candidate_SHA256=sha256(image).hexdigest(), used=info['used'],
                            source_SHA256=info['source_SHA256'], same_update=same_capture_frame(seed, trial),
                            controls=capture_controls(seed, trial), lifecycle=action_lifecycle(seed, trial),
                            interrupts=vectors(trial))
        elif args.compare:
            image, _ = proposal(raw)
            evidence = matrix_parity(seed, remap(seed, image), water=args.part == 'water',
                                     vertical=args.part == 'vertical', held=args.held, face_filter=args.face)
        else:
            if args.candidate:
                raw, _ = proposal(raw)
                seed = remap(seed, raw)
            evidence = matrix(seed, water=args.part == 'water', held=args.held, vertical=args.part == 'vertical')
    print(json.dumps(dict(passed=True, ROM_SHA256=sha256(raw).hexdigest(), part=args.part,
                          held_extra_updates=args.held, origin=origin, evidence=evidence,
                          output_files=0, native_emulator=False)), flush=True)


if __name__ == '__main__':
    main()

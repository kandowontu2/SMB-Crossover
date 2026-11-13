"""Qualify the exact private Prince moving-support delta without output files."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU

import check_prince_exposed_brick_idle_1111 as Idle


Brick = Idle.Brick
R = Brick.Packet.R
PARENT = '464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0'
CANDIDATE = '6d0346164b7099f8e75cdbe22a9e9f1fd5f4f673116fd1dcb48a3cee620734c2'
PATCH = 0xd736
OLD = bytes.fromhex('ad16c6d017')
NEW = bytes([0xea]) * 5
ADDED = (0x51, 0x57, 0xc0)


def layout(parent, candidate):
    assert sha256(parent).hexdigest() == PARENT
    assert sha256(candidate).hexdigest() == CANDIDATE
    _, old, _ = Brick.Packet.extract(parent)
    _, new, _ = Brick.Packet.extract(candidate)
    assert old[0] == new[0] and old[2] == new[2]
    offset = PATCH - 0xc800
    assert old[1][offset:offset + 5] == OLD
    assert new[1][offset:offset + 5] == NEW
    assert [(i, a, b) for i, (a, b) in enumerate(zip(old[1], new[1])) if a != b] == [
        (offset + i, a, b) for i, (a, b) in enumerate(zip(OLD, NEW))]

    def change(runtime, metadata, state):
        assert metadata[offset:offset + 5] == OLD
        metadata[offset:offset + 5] = NEW
        return runtime, metadata, state

    rebuilt, recipe = Brick.Packet.rebuild(parent, change)
    assert rebuilt == candidate
    memory = [0] * 65536
    memory[0xa000:0xa000 + len(old[0])] = old[0]
    memory[0xc800:0xc800 + len(old[1])] = old[1]
    decoder = Disassembler(MPU(memory=memory))
    instructions = []
    pc = 0xd720
    while pc < 0xd756:
        size, text = decoder.instruction_at(pc)
        instructions.append([f'{pc:04x}', text])
        pc += size
    logical = []
    pc = 0xbd82
    while pc < 0xbda2:
        size, text = decoder.instruction_at(pc)
        logical.append([f'{pc:04x}', text])
        pc += size
    return dict(parent=PARENT, candidate=CANDIDATE, patch_hex=f'{PATCH:04x}',
                old=OLD.hex(), replacement=NEW.hex(), decoded_delta_bytes=5,
                exact_rebuild=True, recipe=recipe, old_support_tail=instructions,
                logical_fallback=logical)


def fixture(seed, tile=0x51, **kwargs):
    options = dict(x=307, left=320, face=255, action=1, mode=255, pose=6)
    options.update(kwargs)
    return Idle.fixture(seed, tile, **options)


def differences(a, b):
    return set(Idle.differences(a, b))


def pair(parent, candidate, tile=0x51, *, entry=Idle.SUPPORT[0], mutate=None,
         args=Idle.ARGS, **kwargs):
    a, b = (fixture(seed, tile, **kwargs) for seed in (parent, candidate))
    if mutate is not None:
        for model in (a, b):
            mutate(model)
    old, new = Idle.call(a, entry, args), Idle.call(b, entry, args)
    assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
    assert bytes(a[3:11]) == bytes(b[3:11])
    return a, b, old, new


def same_state(a, b, *, scratch=()):
    ignored = {(bank, i) for bank in (2, 3) for i in range(0x1fe0, 0x1ff0)}
    ignored.update((2, i) for i in range(PATCH - 0xc000, PATCH - 0xc000 + 5))
    ignored.update(scratch)
    for bank, (old, new) in enumerate(zip(a.ram, b.ram)):
        left, right = bytearray(old), bytearray(new)
        for owner, at in ignored:
            if owner == bank:
                left[at] = right[at] = 0
        assert left == right, (bank, sorted(differences(a, b)))


def materials(parent, candidate):
    totals = Counter()
    changed = []
    for action, mode, pose in ((0, 0, 15), (1, 1, 6), (1, 255, 6),
                               (42, 1, 123), (42, 255, 123)):
        for tile in range(256):
            a, b, old, new = pair(parent, candidate, tile, action=action, mode=mode, pose=pose)
            expect = action != 0 and tile in ADDED
            if expect:
                assert (old[0], new[0]) == (0, 1), (action, mode, tile, old, new)
                assert old[1:3] == new[1:3] and old[4] == new[4]
                assert old[3] ^ new[3] == 2
                assert Brick.snapshot(b)['surface'] == 144
                assert differences(a, b) <= Idle.POINT_SCRATCH | {(2, 0x7f)}
                totals['new_moving_support'] += 1
                changed.append([action, mode, tile])
            else:
                assert old == new and differences(a, b) <= Idle.POINT_SCRATCH, (
                    action, mode, tile, old, new, sorted(differences(a, b)))
                totals['unchanged'] += 1
    return dict(totals=totals, changed_materials=changed)


def action_modes(parent, candidate):
    totals = Counter()
    scenarios = set()
    for face, x in ((255, 307), (0, 333)):
        for action in range(256):
            for mode in (1, 255):
                scenarios.add((face, x, action, mode, 123 if action == 42 else 6))
        for action in (0, 1, 42):
            for mode in range(256):
                scenarios.add((face, x, action, mode, 15 if action == 0 else 123 if action == 42 else 6))
    for face, x, action, mode, pose in sorted(scenarios):
        a, b, old, new = pair(parent, candidate, face=face, x=x, action=action, mode=mode, pose=pose)
        expected = action == 0 and mode == 0 and pose == 15 or action in (1, 42) and mode in (1, 255)
        assert new[0] == int(expected), (face, action, mode, pose, old, new)
        if old != new:
            assert action in (1, 42) and mode in (1, 255) and (old[0], new[0]) == (0, 1)
            same_state(a, b, scratch=Idle.POINT_SCRATCH | {(2, 0x7f)})
            totals['new_moving_support'] += 1
        else:
            same_state(a, b, scratch=Idle.POINT_SCRATCH)
            totals['unchanged'] += 1
    for pose in range(256):
        a, b, old, new = pair(parent, candidate, action=0, mode=0, pose=pose)
        assert old == new and new[0] == int(pose == 15), (pose, old, new)
        same_state(a, b, scratch=Idle.POINT_SCRATCH)
        totals['idle_pose_controls'] += 1
    return dict(totals)


def geometry(parent, candidate):
    totals = Counter()
    negatives = [dict(state=state) for state in (1, 2, 3)]
    negatives += [dict(native_y=y) for y in (0, 111, 113, 175, 176, 255)]
    negatives += [dict(previous_sole=y) for y in (0, 144, 146, 255)]
    negatives += [dict(cover=tile) for tile in (0x51, 0x54, 0x57, 0x58, 0xc0)]
    mutations = [
        ('previous sole high', lambda m: m.ram[2].__setitem__(0x87, 1)),
        ('native Y page zero', lambda m: Brick.N.put(m, Player_Y_HighPos=0)),
        ('native Y page two', lambda m: Brick.N.put(m, Player_Y_HighPos=2)),
    ]
    for face, x in ((255, 307), (0, 333)):
        for tile in ADDED:
            for case in negatives:
                a, b, old, new = pair(parent, candidate, tile, face=face, x=x, **case)
                assert old == new and new[0] == 0, (face, tile, case, old, new)
                same_state(a, b, scratch=Idle.POINT_SCRATCH)
                totals['rejected_geometry'] += 1
            # The actual BDE2 provider refreshes the current sole before this
            # predicate. Mutating its stale input is a canonicalization control,
            # not a reached mismatched-sole rejection fixture.
            for at, value in ((0x84, 144), (0x85, 1)):
                a, b, old, new = pair(parent, candidate, tile, face=face, x=x,
                    mutate=lambda m, at=at, value=value: m.ram[2].__setitem__(at, value))
                assert (old[0], new[0]) == (0, 1)
                assert bytes(a.ram[2][0x84:0x86]) == bytes(b.ram[2][0x84:0x86]) == bytes((145, 0))
                same_state(a, b, scratch=Idle.POINT_SCRATCH | {(2, 0x7f)})
                totals['current_sole_canonicalization'] += 1
            for name, change in mutations:
                a, b, old, new = pair(parent, candidate, tile, face=face, x=x, mutate=change)
                assert old == new and new[0] == 0, (face, tile, name, old, new)
                same_state(a, b, scratch=Idle.POINT_SCRATCH)
                totals['rejected_geometry'] += 1
            # The native facing-foot query must remain within this exact cell.
            for position in range(280, 361):
                a, b, old, new = pair(parent, candidate, tile, face=face, x=position)
                # ADC #1 consumes the set carry from the equal sole compare.
                foot = position + (13 if face else 2)
                expected = 320 <= foot < 336
                if old[0]:
                    # Original WorldTileY nonempty results bypass the fallback.
                    assert new == old, (face, tile, position, foot, old, new)
                    same_state(a, b)
                    totals['original_nonempty_passthrough'] += 1
                else:
                    assert new[0] == int(expected), (face, tile, position, foot, old, new)
                    same_state(a, b, scratch=Idle.POINT_SCRATCH | ({(2, 0x7f)} if expected else set()))
                totals['facing_foot_positions'] += 1
    return dict(totals)


def decisions(parent, candidate):
    totals = Counter()
    examples = []
    for face, x in ((255, 307), (0, 333)):
        for action, pose in ((1, 6), (42, 123)):
            for mode in (1, 255):
                for tile in ADDED:
                    for carry in (0, 1):
                        args = (*Idle.ARGS[:3], Idle.ARGS[3] | carry)
                        a, b, _, _ = pair(parent, candidate, tile, face=face, x=x,
                                         action=action, mode=mode, pose=pose,
                                         entry=0xa6f6, args=args)
                        before, after = Brick.snapshot(a), Brick.snapshot(b)
                        assert before['action'] == 7, (face, action, mode, tile, before)
                        assert (after['x'], after['y'], after['action'], after['surface']) == (
                            x + 8, 65, action, 144), (face, action, mode, tile, after)
                        if face == 255 and action == 1 and mode == 255 and carry == 0:
                            examples.append(dict(tile=tile, before=before, after=after))
                        totals['moving_material_full_decisions'] += 1
            for tile in (0, 0x14, 0x54, 0x5f, 0xc2):
                a, b, old, new = pair(parent, candidate, tile, face=face, x=x,
                                     action=action, pose=pose, entry=0xa6f6)
                assert old == new
                same_state(a, b, scratch=Idle.POINT_SCRATCH)
                totals['unchanged_non_support_full_decisions'] += 1
    return dict(totals=totals, recorded_geometry=examples)


def interrupt_cases(candidate):
    watch = [(2, *Idle.SUPPORT), (3, 0xa6fc, 0xa71b),
             (3, 0xbd82, 0xbda2), (3, 0xb310, 0xb353)]
    return [Brick.Async.stress(name, fixture(candidate, tile, **options), Idle.call, watch)
            for name, tile, options in (
                ('moving brick51', 0x51, {}),
                ('moving brick57 mirrored', 0x57, dict(face=0, x=333)),
                ('careful questionC0', 0xc0, dict(action=42, mode=1, pose=123)),
                ('covered brick rejection', 0x51, dict(cover=0x54)),
                ('jump action rejection', 0x51, dict(action=3, mode=0, pose=16)),
            )]


def diagnostic(seed):
    model = fixture(seed)
    model.ram[2][0x84] = 144
    native = Brick.N.NesMPU
    rows = []
    class Trace(native):
        def step(self):
            if (0xd6d1 <= self.pc < 0xd756 or 0xbd82 <= self.pc < 0xbda2):
                rows.append([f'{self.pc:04x}', self.a, self.p, self.memory[0xbd],
                             self.memory.ram[2][0x84], self.memory.ram[2][0x86]])
            return native.step(self)
    Brick.N.NesMPU = Trace
    try:
        registers = Idle.call(model)
    finally:
        Brick.N.NesMPU = native
    return dict(registers=registers, trace=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Brick.Route.Combined.Stage.NIGHTLY)
    parser.add_argument('--candidate', type=Path,
                        default=R / 'build/prince-first-pickup-1112/candidate.nes')
    parser.add_argument('--layout-only', action='store_true')
    parser.add_argument('--diagnose', action='store_true')
    args = parser.parse_args()
    raw, changed = args.rom.read_bytes(), args.candidate.read_bytes()
    result = dict(layout=layout(raw, changed), output_files=0)
    print('PRINCE_MOVING_LAYOUT ' + json.dumps(result, separators=(',', ':')), flush=True)
    if args.layout_only:
        return
    parent, cold_parent = Brick.cold(raw)
    candidate, cold_candidate = Brick.cold(changed)
    assert not differences(parent, candidate)
    if args.diagnose:
        print('PRINCE_MOVING_DIAGNOSTIC ' + json.dumps(dict(parent=diagnostic(parent),
              candidate=diagnostic(candidate)), separators=(',', ':')), flush=True)
        return
    result.update(cold_PPU_reads=[cold_parent['PPU_reads'], cold_candidate['PPU_reads']],
                  materials=materials(parent, candidate),
                  action_modes=action_modes(parent, candidate),
                  geometry=geometry(parent, candidate),
                  decisions=decisions(parent, candidate))
    print('PRINCE_MOVING_SUPPORT ' + json.dumps(result, separators=(',', ':')), flush=True)
    result.update(passed=True, interrupts=interrupt_cases(candidate),
                  script_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope='Cold-backed isolated CPU support and D297 response fixtures; '
                        'actual IRQ and FF lag-NMI cuts. No natural pickup, native '
                        'controller route, nested IRQ-in-NMI or full-stage qualification.')
    print('PRINCE_MOVING_QUALIFIED ' + json.dumps(result, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()

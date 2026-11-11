"""Exercise Prince's exact cold question-block climb and idle predicate."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU

import compose_prince_question_ledge_1111 as Source


Idle, Brick = Source.Idle, Source.Idle.Brick
N = Brick.N
NIGHTLY = Brick.Route.Combined.Stage.NIGHTLY
CANDIDATE = '99eeae726f5cb7b5af35c4e59421ea110cd3365336e76e65114b49c75c11018e'


def word(model, address):
    return model[address] | model[address + 1] << 8


def native_x(model):
    return N.get(model, 'Player_X_Position') | N.get(model, 'Player_PageLoc') << 8


def scene(seed, x=1744, tile=0xc0, geometry=None):
    model = Brick.fixture(seed, tile=0, x=x, native_y=176, previous_sole=209,
                          face=255, action=0, mode=0)
    cells = {(1744, 144): tile, (1792, 144): 0xc0}
    cells.update(geometry or {})
    ring = {(column % 512, y): material for (column, y), material in cells.items()}
    Brick.terrain(model, lambda col, y: ring.get((col, y), 0x54 if y == 208 else 0))
    for address, value in ((0xc40a, 8), (0xc617, 15), (0xc611, 129), (0xc084, 209),
                           (0xc08b, 129), (0xc6cf, 4)):
        model[address] = value
    N.put(model, Player_Rel_XPos=x - 1584, Player_Rel_YPos=176,
          ScreenLeft_X_Pos=48, ScreenLeft_PageLoc=6, ScreenRight_X_Pos=47,
          ScreenRight_PageLoc=7, AreaType=1, NumberofLives=2)
    return model


def state(model):
    return [native_x(model), N.get(model, 'Player_Y_Position'), N.get(model, 'Player_State'),
            model[0xc616], model[0xc617], model[0xc618], word(model, 0xc084),
            model[0xc6cf], N.get(model, 'NumberofLives')]


def replay(seed):
    model = scene(seed)
    watch = {(3, 0xb0da): 'F801', (2, 0xd854): 'align_publish',
             (2, Source.source_workers()[1]['PublishSupport']): 'idle_publish'}
    visits = []
    rows = {}
    native = N.NesMPU

    class Trace(native):
        def step(self):
            if self.pc >= 0x8000:
                tag = model.rawtags[(self.pc - 0x8000) // 8192]
                label = watch.get((tag, self.pc))
                if label:
                    visits.append([tick, label, self.a, word(model, 0xb369),
                                   word(model, 0xb36b), *state(model)])
            return super().step()

    with patch.object(N, 'NesMPU', Trace):
        for tick in range(195):
            pad = 8 if tick < 51 else 0 if tick < 192 else 128
            N.put(model, FrameCounter=tick, SavedJoypad1Bits=pad, SavedJoypadBits=pad)
            N.invoke(model, 'PlayerCtrlRoutine', a=83, x=0, y=0, p=0x21)
            if tick in (48, 50, 64, 76, 108, 110, 111, 190, 194):
                rows[tick] = state(model)
    return rows, visits


def positive(parent, candidate):
    old, old_visits = replay(parent)
    new, new_visits = replay(candidate)
    assert old[48] == new[48] == [1752, 173, 2, 8, 78, 2, 205, 5, 2], (old, new)
    assert old[50][:6] == [1744, 173, 2, 10, 78, 255], old
    assert old[110][:6] == [1771, 113, 2, 0, 15, 0], old
    assert new[50][:6] == [1728, 173, 2, 10, 78, 255], new
    assert new[110] == new[111] == new[190] == [1731, 112, 0, 0, 15, 0, 145, 5, 2], new
    assert new[194][:6] == [1731, 112, 0, 3, 15, 255], new
    assert [row[0] for row in new_visits if row[1] == 'idle_publish'] == list(range(111, 192, 4))
    assert not [row for row in old_visits if row[1] in ('align_publish', 'idle_publish')]
    assert [row[3] for row in new_visits if row[1] == 'align_publish'] == [1744]
    return dict(parent=old, candidate=new, actual_idle_publications=21)


def differences(parent, candidate):
    spans = {3: (Source.GEOMETRY, Source.ENTRY, Source.COORDINATE),
             2: (Source.FALLBACK,)}
    bases = {3: 0xa000, 2: 0xc000}
    return [(bank, at) for bank, at in Idle.differences(parent, candidate)
            if bank not in spans or not any(start <= at + bases[bank] < end for start, end in spans[bank])]


def source_closure(raw, seed):
    _, (runtime, metadata, state_stream), _ = Source.Packet.extract(raw)
    ranges = (Source.ENTRY, Source.GEOMETRY, Source.COORDINATE)
    guarded = ((0xa87d, Source.ENTRY[1]), (0xa90b, Source.GEOMETRY[1]),
               (0xb0eb, Source.COORDINATE[1]))
    assert runtime[0x87a:0x884] == bytes.fromhex('20e2bd8dbfc4c90dd026')
    assert runtime[0x908:0x917] == bytes.fromhex('20e2bdc90cf008c907f004c904d062')
    assert runtime[0x10e8:0x10ef] == bytes.fromhex('20e5bdc904d030')

    direct = []
    for origin, chunk in ((0xa000, runtime), (0xc800, metadata), (0xc0b0, state_stream)):
        for at in range(len(chunk) - 2):
            if chunk[at] not in (0x20, 0x4c):
                continue
            operand = int.from_bytes(chunk[at + 1:at + 3], 'little')
            if any(start <= operand < end for start, end in guarded):
                direct.append((origin + at, operand))
    assert direct == [(0xa92c, 0xa931)], direct

    # Each relative range extends more than a branch displacement beyond the
    # two repurposed intervals it covers. The installed code has no data gaps.
    memory = [0] * 65536
    memory[0xa000:0xa000 + len(runtime)] = runtime
    decoder = Disassembler(MPU(memory=memory))
    external = []
    for pc, stop in ((0xa7f2, 0xa9fb), (0xb06c, 0xb1a2)):
        while pc < stop:
            size, operation = decoder.instruction_at(pc)
            assert operation != '???', hex(pc)
            if memory[pc] & 0x1f == 0x10:
                operand = int(operation.rsplit('$', 1)[1], 16)
                assert not any(start <= operand < end and not start <= pc < end for start, end in guarded), (
                    hex(pc), hex(operand))
                for start, end in ranges:
                    if start <= operand < end and not start <= pc < end:
                        external.append((pc, operand))
            pc += size
    assert external == [(0xa90d, 0xa917), (0xa911, 0xa917)], external
    vector_words = [int.from_bytes(runtime[i:i + 2], 'little') for i in range(0x1ba1, 0x1bc1, 2)]
    assert all(not any(start <= target < end for start, end in guarded) for target in vector_words)
    return dict(provider_returns=Idle.material_domain(seed),
                donor_branches_only_for_impossible_materials=external,
                internal_absolute_transfer=direct, original_animation_vector_entries=len(vector_words))


def hang(seed, *, edge=1744, hand=181, face=255, tile=0xc0, action=8, mode=2,
         pose=78, cells=None, actor_x=None):
    x = edge + 8 if actor_x is None else actor_x - 8
    model = Brick.fixture(seed, 0, x=x, native_y=173, previous_sole=hand + 24,
                          face=face, action=action, mode=mode, state=2)
    tiles = {(edge % 512, 144): tile}
    tiles.update({(world_x % 512, y): material for (world_x, y), material in (cells or {}).items()})
    Brick.terrain(model, lambda col, y: tiles.get((col, y), 0x54 if y == 208 else 0))
    for at, value in ((0xc40a, 8), (0xc617, pose), (0xc611, 128), (0xc08b, 128),
                      (0xc07a, 9), (0xc4b1, 19), (0xc4e7, 9), (0xc081, 1)):
        model[at] = value
    for at, value in ((0xc078, edge - 4), (0xc084, hand + 24),
                      (0xc07d, edge - 16), (0xc07f, 208)):
        model[at] = value & 255
        model[at + 1] = value >> 8
    return model


def call_edge(model, *, y=24, entry=0xd7b3):
    return Idle.call(model, entry, (255, 0, y, 0x60))


def geometry(parent, candidate):
    results = []
    native = N.NesMPU
    for edge in (1744, 1776):
        old, new = (hang(seed, edge=edge) for seed in (parent, candidate))
        probes = []

        class Trace(native):
            def step(self):
                if self.pc == 0xb310 and self.memory.rawtags[1] == 3:
                    probes.append([word(self.memory, 0xb369), word(self.memory, 0xb36b)])
                return super().step()

        before = call_edge(old)
        with patch.object(N, 'NesMPU', Trace):
            after = call_edge(new)
        assert before == after, (edge, before, after)
        assert (word(old, 0xc60f) - 8, word(new, 0xc60f) - 8) == (edge, edge - 16)
        assert probes == [[edge + 16, 181], [edge + 15, 181], [edge + 15, 144],
                          [edge + 16, 144], [edge - 1, 144], [edge, 143], [edge, 160]], probes
        assert set(differences(old, new)) <= Idle.POINT_SCRATCH | {(2, 0x60f), (2, 0x610)}
        results.append(dict(edge=edge, climb_x=edge - 16, probes=probes))

    controls = {
        'empty': dict(tile=0), 'ordinary brick': dict(tile=0x51), 'question power-up': dict(tile=0xc1),
        'coin': dict(tile=0xc2), 'hidden': dict(tile=0x5f), 'shaft': dict(tile=0x14),
        'covered by pipe cap': dict(cells={(1744, 128): 0x12}),
        'solid left': dict(cells={(1728, 144): 0x54}),
        'solid right': dict(cells={(1760, 144): 0xc0}),
        'solid below': dict(cells={(1744, 160): 0x54}),
        'occupied hand': dict(cells={(1744, 176): 0x54}),
        'page seam occupied right': dict(edge=1776, cells={(1792, 144): 0xc0}),
        'old typed wall': dict(cells={(1760, 176): 0x54}),
        'old typed pipe': dict(cells={(1760, 176): 0x14, (1760, 160): 0x12}),
        'mirrored isolated block': dict(face=0),
        'mirrored original ledge': dict(face=0, cells={(1744, 176): 0x54}),
        'wrong action': dict(action=9), 'wrong mode': dict(mode=6), 'wrong pose': dict(pose=77),
        'wrong half-cell': dict(actor_x=1744), 'offscreen hand': dict(hand=240),
    }
    for name, options in controls.items():
        for entry in (0xd7b3, 0xb0bb):
            a, b = (hang(seed, **options) for seed in (parent, candidate))
            y = 58 if options.get('face') == 0 else 24
            before, after = (call_edge(model, y=y, entry=entry) for model in (a, b))
            assert before == after and set(differences(a, b)) <= Idle.POINT_SCRATCH, (
                name, hex(entry), before, after, differences(a, b))
            if options.get('face') == 0:
                assert not differences(a, b), (name, hex(entry))
    return dict(actual_exposed_points=results, unchanged_calls=len(controls) * 2,
                mirrored_calls=4, tested_controls=list(controls))


def materials(parent, candidate):
    cases = Counter()
    for action, mode, pose in ((0, 0, 15), (1, 1, 6), (1, 255, 6),
                               (42, 1, 123), (42, 255, 123)):
        for tile in range(256):
            a, b = (Idle.fixture(seed, tile, action=action, mode=mode, pose=pose)
                    for seed in (parent, candidate))
            before, after = Idle.call(a), Idle.call(b)
            if (action, tile) == (0, 0xc0):
                assert before[0] == 0 and after[0] == 1 and before[3] ^ after[3] == 2
                assert before[1:3] == after[1:3] and before[4] == after[4]
                assert set(differences(a, b)) <= Idle.POINT_SCRATCH | {(2, 0x7f)}
                cases['new_idle_metatile'] += 1
            else:
                assert before == after and not differences(a, b), (action, mode, tile)
                cases['unchanged_material_pairs'] += 1
    return dict(cases)


def grounded_decision(parent, candidate):
    def fixture(seed, **changes):
        return Idle.fixture(seed, x=1731, left=1744, **dict(dict(tile=0xc0), **changes))

    old, new = (fixture(seed) for seed in (parent, candidate))
    for model in (old, new):
        Idle.call(model, 0xa6f6)
    assert (word(old, 0xc60f) - 8, old[0xc616]) == (1724, 7)
    assert (word(new, 0xc60f) - 8, new[0xc616], word(new, 0xc07f)) == (1731, 0, 144)
    negatives = (dict(tile=0), dict(cover=0x12), dict(state=2),
                 dict(previous_sole=144), dict(native_y=111), dict(pose=14))
    for case in negatives:
        a, b = (fixture(seed, **case) for seed in (parent, candidate))
        before, after = (Idle.call(model, 0xa6f6) for model in (a, b))
        assert before == after and set(differences(a, b)) <= Idle.POINT_SCRATCH, (case, before, after)
        assert b[0xc616] == 7, (case, state(b))
    return dict(real_empty_fall_relocation=1724, unchanged_fall_controls=len(negatives))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=NIGHTLY)
    parser.add_argument('--layout-only', action='store_true')
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    parent = args.rom.read_bytes()
    if sha256(parent).hexdigest() != Source.PIN:
        parent = Source.recover_parent(parent)
    image, layout = Source.proposal(parent)
    assert Source.recover_parent(image) == parent
    digest = sha256(image).hexdigest()
    assert digest == CANDIDATE
    print('PRINCE_QUESTION_LAYOUT ' + json.dumps(dict(parent=Source.PIN, candidate=digest, **layout)), flush=True)
    if args.layout_only:
        return
    old, old_cold = Brick.cold(parent)
    new, new_cold = Brick.cold(image)
    print('PRINCE_QUESTION_SMOKE ' + json.dumps(dict(cold_reads=[old_cold['PPU_reads'], new_cold['PPU_reads']],
                                                     **positive(old, new))), flush=True)
    if args.smoke:
        return
    proof = dict(closure=source_closure(parent, old), geometry=geometry(old, new),
                 materials=materials(old, new), grounded_decision=grounded_decision(old, new))
    print('PRINCE_QUESTION_CPU ' + json.dumps(proof), flush=True)
    windows = [(2, 0xd7b3, 0xd87d), (3, *Source.ENTRY), (3, *Source.COORDINATE),
               (3, *Source.GEOMETRY), (3, 0xb310, 0xb353)]
    irq = [Brick.Async.stress('exposed question ledge', hang(new), call_edge, windows),
           Brick.Async.stress('real covered neighbor', hang(new, cells={(1744, 128): 0x12}),
                              call_edge, windows),
           Brick.Async.stress('grounded idle question', Idle.fixture(new, 0xc0),
                              Idle.call, [(2, *Idle.SUPPORT), (3, 0xb310, 0xb353)])]
    print('PRINCE_QUESTION_IRQ ' + json.dumps(irq), flush=True)


if __name__ == '__main__':
    main()

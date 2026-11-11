"""Qualify the exact cold Prince standing support decision and original fall."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU

import check_prince_brick_support_1111 as Brick
from check_prince_wall_sweep_1110_v6 import assemble
from compose_prince_brick_1111 import support_workers


PIN = '409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280'
CANDIDATE = 'ac2624467d4c3abc8988088ab22a4d2a0f52059e2e2d23373940fc9d17006066'
SOURCE = Brick.Packet.R / 'tools/reference/prince_exposed_brick_idle_1111.s'
SUPPORT = (0xd6d1, 0xd756)
DISPATCH = (0xa6f9, 0xa71b)
OLD_DISPATCH = bytes.fromhex(
    'c911f007c910d0094c56aaceb1c44c56aac902d00620f9b24c97dac90bd0034ce7a7'
)
ARGS = (6, 0, 9, 0x60)
BRICKS = (0x51, 0x57, 0x58)
PIPES = tuple(range(0x10, 0x14))
POINT_SCRATCH = {(3, i) for i in (0x133b, 0x1369, 0x136a, 0x136b, 0x136c, 0x136d)}


def source_workers():
    text = SOURCE.read_text(encoding='utf-8')
    dispatch_text, support_text = text.split('.segment "SUPPORT"', 1)
    dispatch, labels = assemble(dispatch_text, DISPATCH[0])
    support, _ = assemble(support_text, SUPPORT[0], {'SupportAction': labels['SupportAction']})
    assert len(dispatch) == DISPATCH[1] - DISPATCH[0] - 1
    assert len(support) == SUPPORT[1] - SUPPORT[0] - 2, len(support)
    return (OLD_DISPATCH, support_workers()[1]), (dispatch + b'\xea', support + b'\xea\xea')


def replace_workers(image, old, new):
    def mutate(runtime, metadata, state):
        for block, origin, start, before, after in (
            (runtime, 0xa000, DISPATCH[0], old[0], new[0]),
            (metadata, 0xc800, SUPPORT[0], old[1], new[1]),
        ):
            extent = slice(start - origin, start - origin + len(before))
            assert len(before) == len(after) and block[extent] == before
            block[extent] = after
        return runtime, metadata, state

    return Brick.Packet.rebuild(image, mutate)


def proposal(image):
    assert sha256(image).hexdigest() == PIN
    return replace_workers(image, *source_workers())


def source_closure(raw):
    _, (runtime, metadata, state), _ = Brick.Packet.extract(raw)
    # Translated donor branch targets in the replaced interval are internal.
    # Scan all direct transfer encodings in the three decoded streams and all
    # relative instruction boundaries in branch range from the pinned caller.
    target = range(*DISPATCH)
    direct = []
    words = []
    for origin, data in ((0xa000, runtime), (0xc800, metadata), (0xc0b0, state)):
        for i in range(len(data) - 1):
            operand = data[i] | data[i + 1] << 8
            if operand in target:
                words.append((origin + i, operand))
                if i and data[i - 1] in (0x20, 0x4c):
                    direct.append((origin + i - 1, operand))
    assert not direct, direct

    memory = [0] * 65536
    memory[0xa000:0xa000 + len(runtime)] = runtime
    decoder = Disassembler(MPU(memory=memory))
    branches = []
    pc = 0xa641
    while pc < 0xa79c:
        length, operation = decoder.instruction_at(pc)
        if memory[pc] & 0x1f == 0x10:
            operand = int(operation.rsplit('$', 1)[1], 16)
            if operand in target:
                branches.append((pc, operand))
        pc += length
    assert branches == [(0xa6fb, 0xa704), (0xa6ff, 0xa70a), (0xa70c, 0xa714)], branches
    assert runtime[0x6f6:0x71d] == bytes.fromhex('20d1d6') + OLD_DISPATCH + bytes.fromhex('c914')

    # The only literal target words are within the authentic donor animation
    # stream and Prince's packed pose metadata. Neither is a code vector.
    assert words == [(0xb49f, 0xa701), (0xce64, 0xa702)], words
    donor = Brick.Original.donor()
    bank5 = 16 + 5 * 16384
    assert runtime[0x1400:0x1ae5] == donor[bank5 + 0x16ae:bank5 + 0x1d93]
    assert metadata[0x662:0x668] == bytes.fromhex('040002a70d0e')
    return dict(direct_entries=direct, internal_branch_entries=branches,
                incidental_animation_and_pose_words=words)


def fixture(seed, tile=0x51, *, x=1587, left=1600, face=255,
            action=0, mode=0, pose=15, **kwargs):
    model = Brick.fixture(seed, tile=0, x=x, face=face, action=action, mode=mode, **kwargs)
    cover = kwargs.get('cover', 0)
    Brick.terrain(model, lambda col, y: (tile if y == 144 else cover)
                  if col == left % 512 and y in (128, 144) else 0x54 if y >= 208 else 0)
    actor = model.ram[2]
    # The physical 3204 query is native X1587, actor X1595, and X1567
    # after donor D279. Right-running still uses its original 32px offset.
    offset = (-32 if action == 1 else -28) if face else 22
    actor[0x78:0x7a] = (x + 8 + offset).to_bytes(2, 'little')
    actor[0x617] = pose
    actor[0xa6] = 132
    actor[0x9b:0x9d] = (144).to_bytes(2, 'little')
    return model


def call(model, entry=SUPPORT[0], args=ARGS):
    registers = Brick.I.invoke(model, 3, entry, args)['regs']
    registers[3] &= 0xef
    return registers


def differences(old, new):
    return [(bank, at) for bank, at in Brick.observed_difference(old, new)
            if not (bank == 3 and DISPATCH[0] - 0xa000 <= at < DISPATCH[1] - 0xa000)]


def support_matrix(parent, candidate):
    totals = Counter()
    for action, mode, pose in ((0, 0, 15), (1, 1, 6), (1, 255, 6),
                               (42, 1, 123), (42, 255, 123)):
        for tile in range(256):
            a, b = (fixture(seed, tile, action=action, mode=mode, pose=pose)
                    for seed in (parent, candidate))
            before, after = call(a), call(b)
            changed = action == 0 and tile in BRICKS + PIPES
            if changed:
                assert before[0] == 0 and after[0] == 1
                assert before[1:3] == after[1:3] and before[4] == after[4]
                assert before[3] ^ after[3] == 2
                assert Brick.snapshot(b)['surface'] == 144
                assert set(differences(a, b)) <= POINT_SCRATCH | {(2, 0x7f)}
                totals['added_idle_materials'] += 1
            else:
                allowed = POINT_SCRATCH if action == 0 else set()
                assert before == after and set(differences(a, b)) <= allowed, (
                    action, tile, before, after, differences(a, b))
                totals['unchanged_material_cases'] += 1
            assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
    return dict(totals)


def material_domain(seed):
    returns = set()
    for sweep in (0, 1):
        for wall in (0, 1):
            for floor in (0, 1):
                model = Brick.Q.Sonic.slim_fork(seed)
                model.raw_page(1, 3)
                model.raw_page(2, 2)
                model.ram[2][0x8c:0x8f] = bytes((wall, floor, sweep))
                cpu = Brick.N.NesMPU(memory=model, pc=0xbf59)
                cpu.sp = 0xfd
                cpu.stPushWord(0x5ffe)
                cpu.stPush(cpu.p)  # WorldTileY's existing PHP.
                for _ in range(32):
                    if cpu.pc == 0x5fff:
                        break
                    cpu.step()
                else:
                    raise AssertionError(('Native material decision did not return', cpu.pc))
                a = cpu.a
                expected = 1 if floor and (sweep or not wall) else 0x14 if wall else 0
                assert a == expected, (sweep, wall, floor, a)
                returns.add(a)
    assert returns == {0, 1, 0x14}
    return sorted(returns)


def original_empty_fall(reference, args):
    cpu = Brick.Original.machine()
    bus = cpu.memory
    bus.switch(5)
    state = bytearray(reference.ram[2][:0x800])
    world_origin = 1248
    state[0x60f:0x611] = (1595 - world_origin).to_bytes(2, 'little')
    state[0x6cd:0x6cf] = (0x300).to_bytes(2, 'little')
    state[0x300:0x31e] = bytes(30)
    list.__setitem__(bus, slice(0, 0x800), state)
    cpu.a, cpu.x, cpu.y, cpu.p = args
    cpu.pc, cpu.sp = 0xd297, 0xfd
    cpu.stPushWord(0x5afe)
    visits = []
    Brick.Original.until(cpu, 0x5aff, sp=0xfd, limit=3000,
                         trace=lambda c: visits.append(c.pc))
    assert 0xd35c in visits and 0xd36d in visits
    return int.from_bytes(bus[0x60f:0x611], 'little') + world_origin, bus[0x611], bus[0x616]


def nonzero_decisions(parent, candidate):
    checked = []
    for y, material in ((144, 1), (112, 0x14)):
        for entry in (SUPPORT[0], 0xa6f6):
            a, b = (fixture(seed) for seed in (parent, candidate))
            for model in (a, b):
                Brick.terrain(model, lambda _col, row: 0x54 if row == y else 0)
            before, after = call(a, entry), call(b, entry)
            assert before == after and not differences(a, b), (y, entry, before, after, differences(a, b))
            if entry == SUPPORT[0]:
                assert after[0] == material
            checked.append((entry, material))
    return checked


def decisions(parent, candidate):
    outcomes = {}
    for carry in (0, 1):
        args = (*ARGS[:3], ARGS[3] | carry)
        old, new = (fixture(seed) for seed in (parent, candidate))
        for model in (old, new):
            call(model, 0xa6f6, args)
        before, after = (Brick.snapshot(model) for model in (old, new))
        oracle = original_empty_fall(fixture(parent, 0), args)
        assert (before['x'], before['y'], before['action']) == oracle == (1572, 65, 7)
        assert (after['x'], after['y'], after['action'], after['surface']) == (1595, 65, 0, 144)
        outcomes[str(carry)] = dict(before=before, after=after, donor_empty_fall=oracle)

    positives = (dict(tile=0x57, x=1603, left=1616),
                 dict(tile=0x57, x=1629, left=1616, face=0))
    for case in positives:
        assert call(fixture(parent, **case))[0] == 0, case
        assert call(fixture(candidate, **case))[0] == 1, case

    negatives = (dict(tile=0), dict(tile=0xc2), dict(tile=0x5f), dict(tile=0xc0),
                 dict(tile=0x14), dict(tile=0x54), dict(x=1586), dict(cover=0x54),
                 dict(state=2), dict(native_y=111), dict(previous_sole=144),
                 dict(mode=2), dict(pose=14), dict(pose=16), dict(action=3),
                 dict(tile=0x57, x=1630, left=1616, face=0))
    for case in negatives:
        a, b = (fixture(seed, **case) for seed in (parent, candidate))
        before, after = call(a, 0xa6f6), call(b, 0xa6f6)
        # The new idle predicate may perform a facing-foot read in cases the
        # old action gate skipped. Only the native query scratch can differ.
        assert before == after and set(differences(a, b)) <= POINT_SCRATCH, (
            case, before, after, differences(a, b))
        if case == dict(tile=0):
            assert Brick.snapshot(b)['action'] == 7
    return dict(physical_3204=outcomes, mirrored_and_next_tile_controls=len(positives),
                unchanged_full_decisions=len(negatives))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Brick.Route.Combined.Stage.NIGHTLY)
    parser.add_argument('--layout-only', action='store_true')
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    if sha256(raw).hexdigest() == CANDIDATE:
        raw, _ = replace_workers(raw, *source_workers()[::-1])
    changed, layout = proposal(raw)
    assert sha256(changed).hexdigest() == CANDIDATE
    assert replace_workers(changed, *source_workers()[::-1])[0] == raw
    result = dict(parent=PIN, candidate=CANDIDATE, layout=layout,
                  source_closure=source_closure(raw), output_files=0)
    print('PRINCE_IDLE_LAYOUT ' + json.dumps(result, separators=(',', ':')), flush=True)
    if args.layout_only:
        return
    parent, cold_parent = Brick.cold(raw)
    candidate, cold_candidate = Brick.cold(changed)
    assert not differences(parent, candidate), differences(parent, candidate)
    result.update(cold_PPU_reads=[cold_parent['PPU_reads'], cold_candidate['PPU_reads']],
                  material_domain=material_domain(parent),
                  materials=support_matrix(parent, candidate),
                  decisions=decisions(parent, candidate),
                  nonzero_decisions=nonzero_decisions(parent, candidate))
    print('PRINCE_IDLE_DECISIONS ' + json.dumps(result, separators=(',', ':')), flush=True)
    windows = [(2, *SUPPORT), (3, *DISPATCH), (3, 0xb310, 0xb353)]
    cuts = [Brick.Async.stress(name, fixture(candidate, tile, **options), call, windows)
            for name, tile, options in (('idle brick', 0x51, {}),
                                        ('idle empty', 0, {}),
                                        ('running pipe', 0x12, dict(action=1, mode=1)))]
    print('PRINCE_IDLE_IRQ ' + json.dumps(cuts, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()

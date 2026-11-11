"""Compare the exact cold Prince brick predicate, donor fall and interrupt cuts."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import check_prince_flagpole_route_1110 as Route
import check_prince_climb_funded_irq_1109_v2 as Async
import prince_cold_packet_1111 as Packet
import prince_original_cpu_1101_v1 as Original
from check_prince_player_pipeline_1102_v67 import terrain


PIN = '4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc'
CANDIDATE = '17122790d711b905c681dced1fd9b3a0e69e1364cb039d514ba635c31a1e4fed'
C, N, Q, I = Route.C, Route.N, Route.Combined.Q, Route.Combined.I
SUPPORT = 0xd6d1
ACTION_TEST = 0xa6f6  # Original D297: material lookup and original response.
POINT_READ = 0xb310
BRICK = 0x58
BRICK_LEFT = 1504
BRICK_TOP = 144
ARGS = (83, 71, 109, 0x61)


def cold(raw):
    model = Q.Sonic.O.blank(C.Start.W.bundle(raw))
    result = Q.Sonic.C.cold(model, 38, None)
    cookie = raw[Packet.COOKIE:Packet.COOKIE + 16]
    assert Q.Sonic.O.headers(model) == (cookie, cookie)
    _, chunks, _ = Packet.extract(raw)
    assert bytes(model.ram[2][0x800:0x800 + len(chunks[1])]) == chunks[1]
    assert bytes(model.ram[3][ACTION_TEST - 0xa000:ACTION_TEST - 0xa000 + 3]) == bytes.fromhex('20d1d6')
    return model, result


def fixture(seed, tile=BRICK, *, x=1491, native_y=112, previous_sole=145,
            face=255, action=1, mode=1, state=0, cover=0):
    model = Q.Sonic.slim_fork(seed)
    model.raw_page(1, 3)
    model.raw_page(2, 2)
    N.put(model, CurrentBank=3, CurrentBankC=2, SelectedCharacter=38,
          GameEngineSubroutine=8, OperMode=1, GamePauseStatus=0, NmiDisable=255,
          DisableScreenFlag=0, Mirror_PPUMASK=30, Player_State=state,
          Player_X_Position=x & 255, Player_PageLoc=x >> 8,
          Player_Y_Position=native_y, Player_Y_HighPos=1, Player_Y_Speed=0)

    def native_tile(col, y):
        if col == BRICK_LEFT % 512:
            if y == BRICK_TOP:
                return tile
            if y == BRICK_TOP - 16:
                return cover
        return 0x54 if y >= 208 else 0

    terrain(model, native_tile)
    ram = model.ram[2]
    for at, value in ((0x60f, x + 8), (0x78, x + 8 - (32 if face else 22)),
                      (0x84, 145), (0x86, previous_sole), (0x89, 77)):
        ram[at:at + 2] = value.to_bytes(2, 'little')
    for at, value in ((0x611, 65), (0x88, 3), (0x8b, 65), (0x615, face),
                      (0x616, action), (0x617, 6), (0x618, mode), (0x7a, 9),
                      (0x4b1, 9), (0x4fe, 0), (0x6ee, 0), (0x6d1, 5)):
        ram[at] = value
    Q.Sonic.O.clear_logs(model)
    return model


def call(model, entry=SUPPORT):
    registers = I.invoke(model, 3, entry, ARGS)['regs']
    registers[3] &= 0xef  # B is a software stack bit, independent of real RTI.
    return registers


def snapshot(model):
    ram = model.ram[2]
    return dict(x=int.from_bytes(ram[0x60f:0x611], 'little'), y=ram[0x611],
                action=ram[0x616], frame=ram[0x617], mode=ram[0x618],
                cell=int.from_bytes(ram[0x7d:0x7f], 'little'), surface=ram[0x7f],
                material=ram[0x9f], current_sole=ram[0x84], previous_sole=ram[0x86])


def observed_difference(a, b):
    # The old predicate is 133 bytes and the repair is in-place. Authenticated
    # cold headers and the worker itself are the only static RAM differences.
    return [(bank, i) for bank, (old, new) in enumerate(zip(a.ram, b.ram))
            for i, (left, right) in enumerate(zip(old, new)) if left != right
            and not ((bank in (2, 3) and 0x1fe0 <= i < 0x1ff0)
                     or (bank == 2 and SUPPORT - 0xc000 <= i < SUPPORT - 0xc000 + 133))]


def material_matrix(parent, candidate):
    counts = Counter()
    for tile in range(256):
        a, b = [fixture(seed, tile) for seed in (parent, candidate)]
        old, new = call(a), call(b)
        assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
        assert bytes(a[3:11]) == bytes(b[3:11])
        if tile == BRICK:
            assert (old[0], new[0], old[3] ^ new[3]) == (0, 1, 2), (old, new, snapshot(a), snapshot(b))
            assert old[1:3] == new[1:3] and old[4] == new[4]
            assert (snapshot(a)['surface'], snapshot(b)['surface']) == (145, 144)
            assert all(bank == 3 and 0x133a <= at <= 0x136d or bank == 2 and at == 0x7f
                       for bank, at in observed_difference(a, b)), observed_difference(a, b)
            counts['brick_support'] += 1
        else:
            assert old == new and not observed_difference(a, b), (tile, old, new, observed_difference(a, b))
            if 0x10 <= tile <= 0x13:
                assert old[0] == 1, (tile, old, snapshot(a))
                counts['legacy_pipe_caps'] += 1
            counts['identical_material_pairs'] += 1
    negatives = [dict(x=1490), dict(cover=0x54), dict(state=2), dict(native_y=111),
                 dict(previous_sole=144), dict(mode=2), dict(action=3), dict(face=0)]
    for case in negatives:
        a, b = [fixture(seed, **case) for seed in (parent, candidate)]
        old, new = call(a), call(b)
        # The covered brick performs the new overhead read before rejecting.
        scratch = [(3, 0x136b), (3, 0x136d)] if 'cover' in case else []
        assert old == new and observed_difference(a, b) == scratch, (case, old, new, observed_difference(a, b))
        counts['unchanged_support_controls'] += 1
    return dict(counts)


def original_fall(reference):
    cpu = Original.machine()
    bus = cpu.memory
    bus.switch(5)
    state = bytearray(reference.ram[2][:0x800])
    # Same donor query column and local alignment. The source probe is 32
    # pixels behind the actor, while host native terrain uses 16-pixel tiles.
    world_origin = 1152
    state[0x60f:0x611] = (1499 - world_origin).to_bytes(2, 'little')
    state[0x6cd:0x6cf] = (0x300).to_bytes(2, 'little')
    state[0x300:0x31e] = bytes(30)
    list.__setitem__(bus, slice(0, 0x800), state)
    cpu.a, cpu.x, cpu.y, cpu.p = ARGS
    cpu.pc, cpu.sp = 0xd297, 0xfd
    cpu.stPushWord(0x5afe)
    path = []

    def observe(c):
        if c.pc in (0xd297, 0xd29a, 0xd35c, 0xd35f, 0xd36d):
            path.append([c.pc, c.a, c.x, c.y, bus[0x4b1],
                         int.from_bytes(bus[0x60f:0x611], 'little') + world_origin])

    Original.until(cpu, 0x5aff, sp=0xfd, limit=3000, trace=observe)
    end_x = int.from_bytes(bus[0x60f:0x611], 'little') + world_origin
    assert [row[0] for row in path] == [0xd297, 0xd29a, 0xd35c, 0xd35f, 0xd36d], path
    assert path[1][1] == 0 and path[2][1:3] == [0x24, 0x3e]
    assert (end_x, bus[0x611], bus[0x616]) == (1476, 65, 7), (path, end_x, bus[0x616])
    return dict(path=path, final=[end_x, bus[0x611], bus[0x616]])


def full_decision(parent, candidate):
    unsupported = fixture(parent, 0)
    donor = original_fall(unsupported)
    old_fall, new_fall = [fixture(seed, 0) for seed in (parent, candidate)]
    assert call(old_fall, ACTION_TEST) == call(new_fall, ACTION_TEST)
    assert not observed_difference(old_fall, new_fall)
    fall = snapshot(new_fall)
    assert [fall[k] for k in ('x', 'y', 'action')] == donor['final']
    old, new = [fixture(seed) for seed in (parent, candidate)]
    for m in (old, new):
        call(m, ACTION_TEST)
    before, after = map(snapshot, (old, new))
    assert (before['x'], before['action']) == (1476, 7), before
    assert (after['x'], after['y'], after['action'], after['surface']) == (1499, 65, 1, 144), after
    return dict(original_SHA256=Original.SHA, donor_fall=donor, brick_before=before,
                brick_after=after, unsupported=fall)


def source_pair(raw):
    from compose_prince_brick_1111 import START, END, proposal, support_workers

    if sha256(raw).hexdigest() == CANDIDATE:
        old, new, _ = support_workers()
        left, right = START - 0xc800, END - 0xc800

        def restore(runtime, metadata, state):
            assert metadata[left:right] == new
            metadata[left:right] = old
            return runtime, metadata, state

        raw, _ = Packet.rebuild(raw, restore)

    assert sha256(raw).hexdigest() == PIN
    changed, _ = proposal(raw)
    assert sha256(changed).hexdigest() == CANDIDATE
    return raw, changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Route.Combined.Stage.NIGHTLY)
    raw, changed = source_pair(parser.parse_args().rom.read_bytes())
    before, parent_cold = cold(raw)
    after, candidate_cold = cold(changed)
    assert (parent_cold['PPU_reads'], candidate_cold['PPU_reads']) == (31248, 31252)
    assert not observed_difference(before, after), observed_difference(before, after)[:30]
    matrix = material_matrix(before, after)
    decision = full_decision(before, after)
    cuts = [Async.stress(name, fixture(after, tile), call,
                         [(2, SUPPORT, SUPPORT + 133), (3, POINT_READ, 0xb353)])
            for name, tile in (('exposed brick', BRICK), ('legacy cap', 0x12), ('unsupported', 0))]
    print(json.dumps(dict(parent=PIN, candidate=CANDIDATE,
        cold_PPU_reads=[parent_cold['PPU_reads'], candidate_cold['PPU_reads']],
        material=matrix, decision=decision, interrupt_cuts=cuts, output_files=0),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()

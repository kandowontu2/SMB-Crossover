"""Compare the exact f33 native side predicate and its real interrupt cuts."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_getsu_fuma_owner_1110 as A
import check_getsu_loaded_hot_1110 as ISR
import check_native_contact_tank_precheck_1110 as Tank
import check_native_sparse_world_draw_1110 as W
from check_mini_funded_actor_1108_v3 import live_stack, registers, slim_fork


R, N, SHA = W.R, W.N, A.SHA
PIN = 'f33c7b19d27309ab4e4771125a74360f978dba08bd807d25bc6307026e568734'
BASE = R / 'build/shared-sparse-draw-native-1110/candidate.nes'
SOURCE = R / 'tools/reference/shared_side_tank_precheck_1110.s'
OLD_SOURCE = R / 'tools/reference/mini_native_side_single_map_1109_v1.s'
LO, HI = 0xbea2, 0xbf00
OFFSET = 16 + 33 * 8192 + (LO & 8191)
OLD = bytes.fromhex('08a9b08d6c01a9bf8d6d01a99c205a019010a9558d6c01a9b78d6d0128a9024c5a01'
                    'ad6a01284ce2be68288d6a01a9588d6c01a9bc8d6d01a9d94c5a01eaeaea'
                    '0848ad0260c904f0e0c90bb0dc68284c8b95') + b'\xff' * 12
SIDE, CHECK, STOP = 0x90e4, (156, 0xbfb0), 0x5b00
TRANSPORT = {0x145, 0x5115, *Tank.SMC}


def link(raw, output):
    assert SHA(raw) == PIN
    assert '.res 94-(*-ForeignSide), $ff' in OLD_SOURCE.read_text()
    assert len(OLD) == HI - LO and raw[OFFSET:OFFSET + len(OLD)] == OLD
    at = Tank.at(28, 0xbfb0)
    assert raw[at:at + 5] == bytes.fromhex('ad0260d030')
    assert raw[at + 0x35:at + 0x37] == bytes.fromhex('1860')
    assert raw[Tank.at(126, SIDE):Tank.at(126, SIDE) + 25] == bytes.fromhex(
        '8d6a01ad02604929f04fa9a28d6c01a9be8d6d01a9a14c5a01')
    new, labels = A.assemble(output, SOURCE.read_text(), (('B', LO, HI - LO, ('SIDE',)),))
    assert labels == {'ForeignSide': LO, 'LegacySide': 0xbee2, 'Rejected': 0xbef4}
    assert len(new) == len(OLD)
    row = dict(physical_PRG=33, CPU_half_open=[LO, HI], file_offset=OFFSET,
               old_hex=OLD.hex(), new_hex=new.hex())
    return raw[:OFFSET] + new + raw[OFFSET + len(new):], row


def cpu_at(m, pc, a=0x95, x=3, y=17, p=0x21):
    c = N.NesMPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 236
    c.stPushWord(STOP - 1)
    return c


def done(c):
    return (c.pc, c.sp) == (STOP, 236)


def writes(m, skipped):
    return ([(at, v) for at, v in m.writes if at not in TRANSPORT and not 0x100 <= at < 0x200],
            tuple(m.ram_writes))


def mapper(m, skipped):
    seq = [value for at, value in m.writes if at == 0x5115]
    if skipped:
        i = 0
        while i + 1 < len(seq):
            if seq[i:i + 2] == [156, 161]:
                del seq[i:i + 2]
                skipped -= 1
            else:
                i += 1
    assert skipped == 0
    return seq


def compare(old, new, skipped):
    m, z = old.memory, new.memory
    assert registers(old, 0xef) == registers(new, 0xef)
    assert live_stack(old) == live_stack(new) and W.memory(m) == W.memory(z)
    assert writes(m, skipped) == writes(z, 0) and mapper(m, skipped) == mapper(z, 0)


def new_leaf(seed, raw, variant, engine, y, x, foot, tile, p, poison=None):
    m = slim_fork(seed)
    N.put(m, SelectedCharacter=raw, MarioVariant=variant, GameEngineSubroutine=engine,
          OperMode=1, OperMode_Task=3, NmiDisable=255, DisableScreenFlag=0,
          Player_X_Position=x, Player_PageLoc=1, Player_Y_Position=foot, Player_Y_HighPos=1)
    if poison is not None:
        m.ram[2][0x1fe0 + poison] ^= 1
    N.invoke(m, 'BlockBufferColli_Side', y=y)
    m[m[9] + 256 * m[10] + m[5]] = tile
    A.clear_logs(m)
    return cpu_at(m, SIDE, y=y, p=p)


def leaves(images):
    normal = [N.fresh(b) for b in images]
    loaded = [Tank.cold(b, 0) for b in images]
    counts = Counter()
    cases = [(raw, raw & 7, (4, 8)[raw & 1], (17, 20)[raw & 1], (1, 253)[raw >> 1 & 1],
              (63, 191)[raw >> 2 & 1], tile, p, None)
             for raw, tile, p in product(range(1, 256), (0, 0x54, 0xc3), (0x21, 0x60, 0xa5))]
    cases += [(0, variant, engine, y, 253, 191, tile, p, None)
              for variant, engine, y, tile, p in product(range(9), (4, 8), (17, 20), (0, 0x54), (0x21, 0x60))]
    cases += [(0, 7, 8, 17, 253, 191, 0x54, 0x21, bad) for bad in range(16)]
    for case in cases:
        raw, variant = case[:2]
        pair = [new_leaf(m, *case) for m in (loaded if raw == 0 and variant == 7 else normal)]
        visits = []
        for c in pair:
            hits = Counter()
            W.run(c, done, lambda q: hits.update([ISR.point(q)]) if ISR.point(q) == CHECK else None)
            visits.append(hits[CHECK])
        assert visits == ([0, 0] if raw == 41 else [1, int(raw == 0)]), (case, visits)
        try:
            compare(*pair, visits[0] - visits[1])
        except AssertionError as error:
            raise AssertionError((case, [registers(c) for c in pair],
                                  [bytes(c.memory[0x15a:0x17b]).hex() for c in pair])) from error
        label = 'Tank' if raw == 0 and variant == 7 else 'raw0' if raw == 0 else 'Mini' if raw == 41 else 'other'
        counts[label, pair[0].processorCycles - pair[1].processorCycles] += 1
    return [[label, cycles, count] for (label, cycles), count in sorted(counts.items())]


def openings(images):
    results = []
    for raw, rogue in ((0, False), (2, False), (2, True), (3, False)):
        seeds = [W.cold(b, raw, rogue) for b in images]
        for phase, key, frames in (('idle', 0, 32), ('walk', 1, 136)):
            histogram, admission = Counter(), Counter()
            for _ in range(frames):
                cpus, hits = [], []
                for m in seeds:
                    A.clear_logs(m)
                    W.Match.controls(m, key)
                    c = cpu_at(m, W.P.address(m.bundle, 'GameLoop'), a=0, x=0, y=0)
                    visits = Counter()
                    W.run(c, done, lambda q: visits.update([ISR.point(q)]) if ISR.point(q) == CHECK else None)
                    hits.append(visits[CHECK])
                    cpus.append(c)
                skipped = hits[0] - hits[1]
                compare(*cpus, skipped)
                histogram[cpus[0].processorCycles - cpus[1].processorCycles] += 1
                admission[skipped] += 1
                for m in seeds:
                    N.consume(m)
                assert W.memory(seeds[0]) == W.memory(seeds[1])
            results.append(dict(raw=raw, rogue=rogue, phase=phase, updates=frames,
                                cycles_saved=dict(histogram), Tank_calls_skipped=dict(admission)))
    return results


def vectors(images):
    stats, minimum = Counter(), 255
    for image, raw, rogue in product(images, (0, 2, 3), (False, True)):
        if rogue and raw != 2:
            continue
        m = W.cold(image, raw, rogue)
        A.clear_logs(m)
        W.Match.controls(m, 0)
        c = cpu_at(m, W.P.address(image, 'GameLoop'), a=0, x=0, y=0)
        seen, deepest = set(), []

        def watch(q):
            nonlocal minimum
            tag, pc = ISR.point(q)
            if not (tag == 161 and LO <= pc < HI or tag == 156 and 0xbfb0 <= pc < 0xbfe7):
                return
            cut = tag, pc, q.sp
            if cut in seen:
                return
            seen.add(cut)

            def nested(z):
                if not z.p & 4 and (not deepest or z.sp < deepest[0].sp):
                    deepest[:] = [ISR.clone(z)]

            for kind in ('FF', 'IRQ'):
                if kind == 'IRQ' and q.p & 4:
                    continue
                interrupted = ISR.clone(q)
                smc = bytes(interrupted.memory[0x15a:0x17b])
                minimum = min(minimum, ISR.vector(interrupted, kind, nested if kind == 'FF' else None))
                assert bytes(interrupted.memory[0x15a:0x17b]) == smc
                stats[kind] += 1

        W.run(c, done, watch)
        assert seen and deepest
        minimum = min(minimum, ISR.vector(deepest[0], 'IRQ'))
        stats['nested_IRQ'] += 1
    return dict(cuts=dict(stats), minimum_SP=minimum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    output = parser.parse_args().output.resolve()
    assert output.is_relative_to(R / 'build')
    output.mkdir(exist_ok=True)
    before = BASE.read_bytes()
    after, patch = link(before, output)
    images = [W.bundle(r) for r in (before, after)]
    controls = leaves(images)
    print(json.dumps(dict(leaves=controls)), flush=True)
    measured = openings(images)
    print(json.dumps(dict(openings=measured)), flush=True)
    irq = vectors(images)
    bindings = (Path(__file__), SOURCE, OLD_SOURCE, Path(ISR.__file__), Path(W.__file__), Path(Tank.__file__))
    receipt = dict(passed=True, ROM_written=False, parent_SHA256=PIN, expected_memory_only_SHA256=SHA(after),
                   patches=[patch], leaves=controls, openings=measured, vectors=irq,
                   bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in bindings})
    (output / 'proof.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(SHA256=SHA(after), vectors=irq)))


if __name__ == '__main__':
    main()

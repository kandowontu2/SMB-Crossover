"""Qualify the exact Mini movement prefix and redundant native box comparison."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_native_enemy_ordinary_dispatch_1110 as Q
import check_native_enemy_ordinary_dispatch_irq_1110 as IRQ
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at, lag_pcs


P, N, D, R = Q.P, Q.N, Q.D, Q.R
BASE = R / 'build/mini-helper-powered-injury-native-1110/candidate.nes'
PIN = 'f003b378b0e5bd862403eae71f267d8c33a3b06e9270548ae20b1d9f6b2f9979'
SOURCE = R / 'tools/reference/mini_movement_prefix_1110.s'
KERNEL = R / 'build/mini-native-injury-status-fix-1110/kernel.bin'
KERNEL_PIN = 'cdea2e5496abb30c04cd7357834fe25a9b2df31a380b4b9a211b0c868f57dab6'
PROFILE = R / 'build/mini-six-player-profile-1110/capture/instruction-sample.json'
ENTRY, END, STOP = 0xa614, 0xa645, 0x5b00
COLLISION, SPRITE, BRANCH, REPEAT, COMPARED = 0x9512, 0x9514, 0x9520, 0x954c, 0x954f
OLD = bytes.fromhex('4c17a60848ad0260c90ad01dade55f2944c940d01468288d6a01a9008d6c01'
                    'a9b48d6d01a9d54c5a0168284c3da7eaeaea')
POINTS = {0: (221, 0xa0b0), 14: (209, 0xa0b2), 19: (215, 0xa352),
          41: (212, 0xb420), 'chip': (213, 0xb400)}


def patch(bank, pc, old, new):
    assert len(old) == len(new)
    return dict(physical_PRG=bank, CPU_half_open=[pc, pc + len(old)],
                file_offset=D.offset(bank, pc), old_hex=old.hex(), new_hex=new.hex())


def link(raw, output):
    assert P.sha(raw) == PIN
    x5 = (R / 'src/x5_bounce.s').read_text()
    assert x5.count('jsr X5OwnMovement') == 1 and 'jmp CdCameraMovementAdmission' in x5
    D.check_span(raw, 86, 0xa514, bytes.fromhex('48a5758dfd7f682014a64c2da5'))
    D.check_span(raw, 86, 0xa73d, bytes.fromhex('8d6a0108ad0260'))
    D.check_span(raw, 86, 0xa3d9, bytes.fromhex('a9208d6c01a9b48d6d01a9d44c5a01'))
    D.check_span(raw, 84, 0xb420, bytes.fromhex('4c4db4'))
    bank86 = raw[D.offset(86, 0xa000):D.offset(86, 0xa000) + 8192]
    entries = [(0xa000 + i, pc) for i, op in enumerate(bank86[:-2]) if op in (0x20, 0x4c, 0x6c)
               and ENTRY <= (pc := bank86[i + 1] + 256 * bank86[i + 2]) < END]
    assert entries == [(0xa51b, ENTRY), (ENTRY, ENTRY + 3)], entries
    for pc in range(ENTRY, END):
        assert bytes.fromhex(f'a9{pc & 255:02x}8d6c01a9{pc >> 8:02x}8d6d01a9d6') not in raw[:1048592]
    cc = R / 'tools/Windows/cc65/bin'
    with tempfile.TemporaryDirectory(prefix='prefix-', dir=output) as folder:
        t = Path(folder)
        cfg, obj, binary = (t / f'prefix.{ext}' for ext in ('cfg', 'o', 'bin'))
        cfg.write_text('MEMORY { C:start=$A614,size=49,file=%O; } SEGMENTS { MOVEMENT:load=C,type=ro; }\n')
        subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
        new = binary.read_bytes()
    assert len(new) == len(OLD) == END - ENTRY and new[-2:] == b'\xea\xea'
    D.check_span(raw, 126, 0x951d, bytes.fromhex('dd5806b02a'))
    D.check_span(raw, 126, REPEAT, bytes.fromhex('dd5806f01a'))
    source = (R / 'src/collision.s').read_text()
    assert source.count('FirstBoxGreater') == 2 and 'FirstBoxGreater:\n  cmp BoundingBox_UL_Corner,x' in source
    # Keep the old CMP intact. Only the original carry branch bypasses it.
    rows = [patch(86, ENTRY, OLD, new), patch(126, BRANCH + 1, b'\x2a', b'\x2d')]
    return install(raw, rows), rows


def snapshot(c):
    return (Q.state(c), live_stack(c), IRQ.hardware(c))


def movement_start(seed, raw, alts, flags, *, full=False):
    m = slim_fork(seed)
    m.raw_page(1, 214)
    N.put(m, CurrentBank=214, SelectedCharacter=raw, NmiDisable=255)
    m[0x5fe5] = alts
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    c = cpu_at(m, ENTRY, 232, flags, x=0 if full else raw, y=91)
    c.a = raw ^ alts ^ 0x61
    return c


def finish(c):
    return (c.pc, c.sp) == (STOP, 232)


def classify(raw, alts):
    if raw == 10:
        return 'chip' if alts & 0x44 == 0x40 else 'chip_legacy'
    return {14: 'thomas', 19: 'scrooge', 41: 'mini'}.get(raw, 'legacy')


def cold_seeds(before, after):
    edge = Q.Edge
    previous = edge.KERNEL, edge.KERNEL_PIN
    edge.KERNEL, edge.KERNEL_PIN = KERNEL, KERNEL_PIN
    try:
        return Q.cold([P.bundle(q) for q in (before, after)])
    finally:
        edge.KERNEL, edge.KERNEL_PIN = previous


def finite(seeds):
    counts = Counter()
    live = [slim_fork(seed) for seed in seeds[41]]
    for m in live:
        if m.ram[2][0x300] != 2:
            N.invoke(m, 'GameCoreRoutine', x=0, y=0)
        assert m.ram[2][0x300] == 2
    for raw, alts, flags in product(range(256), (0, 4, 64, 68, 255), (0x21, 0xe4)):
        role = classify(raw, alts)
        target = POINTS['chip'] if role == 'chip' else POINTS.get(raw, POINTS[0])
        cpus = [movement_start(m, raw, alts, flags) for m in seeds[41]]
        for c in cpus:
            run(c, lambda z: D.bank_pc(z) == target)
        a, b = cpus
        assert snapshot(a) == snapshot(b), (raw, alts, flags, registers(a), registers(b))
        saving = a.processorCycles - b.processorCycles
        assert saving == {'mini': 37, 'chip': 6}.get(role, 13), (role, saving)
        counts[role, saving] += 1

    for engine, invalid, flags in product((4, 5, 7, 8, 9, 10, 11),
            ('ready', 'ram2_marker', 'ram2_owner', 'ram3_marker', 'ram3_owner', None), (0x21, 0x65)):
        cpus, paths = [], []
        for seed in live:
            c = movement_start(seed, 41, 0, flags, full=True)
            m = c.memory
            N.put(m, GameEngineSubroutine=engine, Player_State=0)
            if invalid == 'ready':
                m.ram[2][0x300] = 1
            elif invalid:
                bank, offset = int(invalid[3]), 0x1fe0 + invalid.endswith('owner')
                m.ram[bank][offset] ^= 1
            hits = []
            run(c, finish, lambda z: hits.append(D.bank_pc(z)) if D.bank_pc(z) in
                ((212, 0xb420), (212, 0xb44d), (3, 0xa000), (193, 0xb08c)) else None)
            cpus.append(c)
            paths.append(hits)
        a, b = cpus
        assert paths[0] == paths[1] and (212, 0xb44d) in paths[0]
        assert ((193, 0xb08c) in paths[0]) == (engine != 8 or invalid is not None), (engine, invalid, paths)
        assert snapshot(a) == snapshot(b), (engine, invalid, flags)
        assert a.processorCycles - b.processorCycles == 37
        counts['actual_mini_row', 37] += 1
    return [[*key, n] for key, n in sorted(counts.items())]


def collision_cases(before, after):
    cpus = []
    for image in (before, after):
        m = bytearray(65536)
        at = D.offset(126, 0x8000)
        m[0x8000:0xa000] = image[at:at + 8192]
        cpus.append(N.NesMPU(memory=m))
    counts = Counter()
    values = (0, 1, 7, 32, 128, 239, 254, 255)
    for i, (a0, a1, b0, b1) in enumerate(product(values, repeat=4)):
        x, y = (0 if i & 1 else 4 * (1 + i % 6)), 4 * (7 + i % 6)
        entry = COLLISION if i & 1 else SPRITE
        box_a = (a0, values[(i + a0) % 8], a1, values[(i + b1) % 8])
        box_b = (b0, values[(i + b0) % 8], b1, values[(i + a1) % 8])
        results = []
        for c in cpus:
            m = c.memory
            m[0x658 + x:0x65c + x] = bytes(box_a)
            m[0x658 + y:0x65c + y] = bytes(box_b)
            c.pc, c.a, c.x, c.y, c.p, c.sp = entry, 65, x, y, (0x21, 0xe4)[i & 1], 232
            c.processorCycles = 0
            c.stPushWord(STOP - 1)
            run(c, finish)
            results.append((registers(c), bytes(m[0x101 + c.sp:0x200]), bytes(m[:256]), c.processorCycles))
        a, b = results
        assert a[:-1] == b[:-1], (i, box_a, box_b)
        counts[a[-1] - b[-1]] += 1
    assert set(counts) == {0, 4, 8}
    return dict(sorted(counts.items()))


def whole(before, after):
    edge = Q.Edge
    previous = edge.KERNEL, edge.KERNEL_PIN
    edge.KERNEL, edge.KERNEL_PIN = KERNEL, KERNEL_PIN
    try:
        return Q.whole(before, after)
    finally:
        edge.KERNEL, edge.KERNEL_PIN = previous


def vectors(before, after):
    images = [P.bundle(q) for q in (before, after)]
    seeds = cold_seeds(before, after)
    lag, normal = lag_pcs(seeds[41][1])
    counts, deepest, sites = Counter(), {}, set()
    minimum = [255, 255]
    scene = Q.read_scene(PROFILE)

    def replay(c, kind, side, record=False):
        q = fork(c, images[side])
        m = q.memory
        if kind == 'normal':
            N.put(m, NmiDisable=0)
        m.writes.clear()
        m.ram_writes.clear()
        m.ppu_log.clear()
        geometry = bytes(m[0x658:0x690])

        def inspect(z):
            minimum[1] = min(minimum[1], z.sp)
            key = kind, N.get(z.memory, 'SelectedCharacter'), tuple(z.memory.rawtags)
            if record and kind != 'IRQ' and not z.p & 4 and (key not in deepest or z.sp < deepest[key].sp):
                deepest[key] = fork(z)
                deepest[key].memory.vector_floor = None

        cost = IRQ.interrupt(q, kind, lag, normal, inspect)
        assert bytes(m[0x658:0x690]) == geometry and not any(0x658 <= at < 0x690 for at, _ in m.writes)
        return q, cost

    def paired_cut(c, side, seen):
        tag, pc = D.bank_pc(c)
        family = 'movement' if tag == 214 and ENTRY <= pc < END else 'collision'
        if family == 'collision' and not (tag == 254 and COLLISION <= pc <= 0x9574):
            return
        key = tag, pc, c.sp, c.p & 5
        if key in seen:
            return
        seen.add(key)
        sites.add((side, tag, pc))
        minimum[0] = min(minimum[0], c.sp)
        for kind in ('FF', 'IRQ', 'normal'):
            if kind == 'IRQ' and c.p & 4 or kind == 'normal' and pc not in (ENTRY, BRANCH, REPEAT, COMPARED):
                continue
            a, ac = replay(c, kind, side, record=True)
            b, bc = replay(c, kind, 1 - side)
            assert snapshot(a) == snapshot(b) and ac == bc, (family, key, kind)
            counts[family, kind] += 1

    for side, owner in product((0, 1), seeds):
        c = Q.Edge.prepare(seeds[owner][side], scene, False)
        N.put(c.memory, NmiDisable=255)
        seen = set()
        run(c, Q.at_end, lambda z: paired_cut(z, side, seen))
        assert seen
    for side, raw, alts, flags in product((0, 1), (10, 14, 19, 41, 255), (0, 64), (0x21, 0x65)):
        c = movement_start(seeds[41][side], raw, alts, flags)
        seen = set()
        role = classify(raw, alts)
        target = POINTS['chip'] if role == 'chip' else POINTS.get(raw, POINTS[0])
        run(c, lambda z: D.bank_pc(z) == target, lambda z: paired_cut(z, side, seen))

    for c in deepest.values():
        a, ac = replay(c, 'IRQ', 0)
        b, bc = replay(c, 'IRQ', 1)
        assert snapshot(a) == snapshot(b) and ac == bc
        counts['nested', 'IRQ'] += 1

    # Inject the same interrupt at each real common entry and resume both
    # binaries. This checks the skipped CMP with actual interrupted state.
    for owner, entry, kind in product(seeds, ((214, ENTRY), (254, BRANCH)), ('FF', 'IRQ', 'normal')):
        pair = [Q.Edge.prepare(seed, scene, False) for seed in seeds[owner]]
        for c in pair:
            N.put(c.memory, NmiDisable=255)
            run(c, lambda z: Q.at_end(z) or D.bank_pc(z) == entry)
        assert Q.at_end(pair[0]) == Q.at_end(pair[1])
        if Q.at_end(pair[0]):
            continue
        a, b = [replay(c, kind, side)[0] for side, c in enumerate(pair)]
        assert IRQ.hardware(a) == IRQ.hardware(b), (owner, entry, kind)
        Q.through_frame(a, b)
        counts['resumed', kind] += 1
    assert all(counts[key] for key in (('movement', 'FF'), ('collision', 'FF'), ('movement', 'IRQ'),
                                      ('collision', 'IRQ'), ('nested', 'IRQ'), ('resumed', 'FF')))
    assert minimum[1] > 0x7a
    return dict(cuts=[[family, kind, n] for (family, kind), n in sorted(counts.items())],
                sites=sorted(sites), minimum_SP=minimum, actual_lag_PC=lag, actual_normal_NMI_PC=normal)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--vectors-only', action='store_true')
    args = ap.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R / 'build')
    out.mkdir(exist_ok=True)
    before = BASE.read_bytes()
    assert P.sha(before) == PIN
    proof = out / 'proof.json'
    if args.vectors_only:
        old = json.loads(proof.read_text())
        assert old['passed'] and old['parent_SHA256'] == PIN and not (out / 'irq.json').exists()
        for path, digest in old['bindings'].items():
            assert P.sha(Path(path).read_bytes()) == digest, path
        after = install(before, old['patches'])
        assert P.sha(after) == old['expected_memory_only_SHA256']
        result = vectors(before, after)
        target, refs = out / 'irq.json', (Path(__file__), proof, R / 'src/reset.s')
    else:
        assert not proof.exists()
        after, rows = link(before, out)
        result = dict(patches=rows, movement=finite(cold_seeds(before, after)),
                      collision=collision_cases(before, after))
        print('Exact movement and collision leaf differentials passed.', flush=True)
        result['whole_GameLoop'] = whole(before, after)
        target, refs = proof, (Path(__file__), SOURCE, PROFILE, KERNEL, R / 'src/x5_bounce.s', R / 'src/collision.s')
    result.update(passed=True, parent_SHA256=PIN, expected_memory_only_SHA256=P.sha(after), ROM_written=False,
                  bindings={str(p.resolve()): P.sha(p.read_bytes()) for p in refs})
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(target, result['expected_memory_only_SHA256'], flush=True)


if __name__ == '__main__':
    main()

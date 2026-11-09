"""Compare the shared top-score updater and its native interrupt behavior."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import random
import subprocess
import tempfile

import check_mini_movement_prefix_1110 as engine
from check_mini_funded_actor_1108_v3 import install, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


R, P, N, D = engine.R, engine.P, engine.N, engine.D
SOURCE = R / 'tools/reference/native_top_score_1110.s'
BANK, START, END, STOP = 3, 0xb83f, 0xb8c4, 0x5b00
TOP, SCORES = 0x07a9, 0x07af
OLD = bytes.fromhex(
    '2062b8a20ba00538bdaf07f9a907ca8810f6900ee8c8bdaf0799a907e8c8c00690f460'
    'adaf07cda9079034d033adb007cdaa07902ad029adb107cdab079020d01f'
    'adb207cdac079016d015adb307cdad07900cd00badb407cdae079002d00160'
    'adaf078da907adb0078daa07adb1078dab07adb2078dac07adb3078dad07adb4078dae0760')


def compile_update(before, output):
    assert P.sha(before) == engine.PIN
    D.check_span(before, BANK, START, OLD)
    bundle = P.bundle(before)
    assert P.address(bundle, 'UpdateTopScore') == START
    assert P.address(bundle, 'PlayerScoreDisplay') == SCORES and P.address(bundle, 'TopScoreDisplay') == TOP
    code = before[D.offset(BANK, 0xa000):D.offset(BANK, 0xa000) + 8192]
    # Preserve the sole farcall entry. Absolute internal references can only
    # point from within the replaced procedure.
    assert not [(i, target) for i, opcode in enumerate(code[:-2])
                if opcode in (0x20, 0x4c) and not START <= i + 0xa000 < END
                and START < (target := code[i+1] + 256 * code[i+2]) < END]
    with tempfile.TemporaryDirectory(dir=output, prefix='top-') as folder:
        cfg, obj, binary = (Path(folder) / f'top.{ext}' for ext in ('cfg', 'o', 'bin'))
        cfg.write_text('MEMORY { C:start=$B83F,size=$85,file=%O; } SEGMENTS { TOP_SCORE:load=C,type=ro; }\n')
        cc = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
        new = binary.read_bytes()
    patch = engine.patch(BANK, START, OLD, new)
    return install(before, [patch]), patch


class ScoreBus(list):
    def __setitem__(self, address, value):
        if isinstance(address, int) and TOP <= address < SCORES:
            self.writes.append((address, value))
        super().__setitem__(address, value)


def finite(before, after):
    pair = []
    offset = D.offset(BANK, START)
    for rom in (before, after):
        bus = ScoreBus([0] * 65536)
        bus[START:END] = rom[offset:offset + END - START]
        pair.append(N.NesMPU(memory=bus))
    gen = random.Random(0x07af)
    values = (0, 1, 9, 10, 127, 128, 254, 255)
    cases = [(bytes([a] * 6), bytes([b] * 6), bytes([c] * 6)) for a, b, c in product(values, repeat=3)]
    for limit in (10, 256):
        for _ in range(4096):
            top, p1, p2 = (bytes(gen.randrange(limit) for _ in range(6)) for _ in range(3))
            cases.extend(((top, p1, p2), (top, top, p2), (top, p1, top)))
    saves = Counter()
    for i, (top, p1, p2) in enumerate(cases):
        rows = []
        for cpu in pair:
            bus = cpu.memory
            bus[TOP:SCORES+12] = top+p1+p2
            bus.writes = []
            cpu.pc, cpu.sp, cpu.a, cpu.x, cpu.y = START, 230, 0x5a, 193, 255
            cpu.p = (0x21, 0x2d, 0x65, 0xe8)[i & 3]
            cpu.processorCycles = 0
            cpu.stPushWord(STOP-1)
            run(cpu, lambda c: c.pc == STOP)
            rows.append((registers(cpu), bytes(bus[TOP:SCORES+12]), bus.writes, cpu.processorCycles))
        old, new = rows
        assert old[:-1] == new[:-1], (i, (top, p1, p2), old, new)
        saves[old[-1]-new[-1]] += 1
    return dict(sorted(saves.items()))


def vectors(before, after):
    seeds = engine.cold_seeds(before, after)
    lag, normal = engine.lag_pcs(seeds[41][1])
    scene = engine.Q.read_scene(engine.PROFILE)
    counts = Counter()
    for owner, pair in seeds.items():
        for side, seed in enumerate(pair):
            for winning in (False, True):
                c = engine.Q.Edge.prepare(seed, scene, False)
                N.put(c.memory, NmiDisable=255)
                c.memory[TOP:SCORES+12] = bytes([5]*6 + [9 if winning else 0]*12)
                run(c, lambda q: D.bank_pc(q) == (131, START))
                sp = c.sp

                def done(z):
                    return D.bank_pc(z) == (254, 0x8322) and z.sp == sp + 5

                original = fork(c)
                run(original, done)
                sites = set()

                def check(cut):
                    tag, pc = D.bank_pc(cut)
                    if tag != 131 or not START <= pc < END or pc in sites:
                        return
                    sites.add(pc)
                    for kind in ('FF', 'IRQ'):
                        if kind == 'IRQ' and cut.p & 4:
                            continue
                        probe = fork(cut)
                        engine.IRQ.interrupt(probe, kind, lag, normal)
                        run(probe, done)
                        assert registers(probe, 0xef) == registers(original, 0xef)
                        assert bytes(probe.memory[TOP:SCORES+12]) == bytes(original.memory[TOP:SCORES+12])
                        counts[side, kind] += 1

                run(c, done, check)
    assert len(counts) == 4
    return [[side, kind, count] for (side, kind), count in sorted(counts.items())]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    args.output.mkdir(exist_ok=True)
    assert not (args.output / 'proof.json').exists()
    before = engine.BASE.read_bytes()
    after, patch = compile_update(before, args.output)
    direct = finite(before, after)
    print('Exact score comparisons', sum(direct.values()), 'saving range', (min(direct), max(direct)), flush=True)
    frames = engine.whole(before, after)
    cuts = vectors(before, after)
    print('Interrupt cuts', cuts, flush=True)
    proof = dict(passed=True, parent_SHA256=P.sha(before), expected_memory_only_SHA256=P.sha(after),
                 patches=[patch], score_cases=direct, whole_GameLoop=frames, vectors=cuts,
                 bindings={str(p.resolve()): P.sha(p.read_bytes()) for p in (Path(__file__), SOURCE)})
    (args.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

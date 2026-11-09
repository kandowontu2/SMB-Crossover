"""Verify the shared RNG step against the delivered MMC5 engine."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess
import tempfile

import check_mini_movement_prefix_1110 as engine
from check_mini_funded_actor_1108_v3 import install, registers, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork


R, P, N, D = engine.R, engine.P, engine.N, engine.D
SOURCE = R / 'tools/reference/native_rng_step_1110.s'
START, END, RNG = 0x82f3, 0x8310, 0x07a0
OLD = bytes.fromhex('a200a007ada00729028503ada1072902450318f001387ea007e888d0f9')


def finish(c):
    return c.pc == END


def rng_state(c):
    return registers(c), c.memory[3], bytes(c.memory[RNG:RNG + 7])


def compile_step(raw, output):
    assert P.sha(raw) == engine.PIN
    D.check_span(raw, 126, START, OLD)
    assert P.address(P.bundle(raw), 'PseudoRandomBitReg') == RNG
    cc = R / 'tools/Windows/cc65/bin'
    with tempfile.TemporaryDirectory(dir=output, prefix='rng-') as folder:
        cfg, obj, binary = (Path(folder) / f'rng.{ext}' for ext in ('cfg', 'o', 'bin'))
        cfg.write_text('MEMORY { C:start=$82F3,size=$1D,file=%O; } SEGMENTS { RNG_STEP:load=C,type=ro; }\n')
        subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
        new = binary.read_bytes()
    patch = engine.patch(126, START, OLD, new)
    return install(raw, [patch]), patch


def finite(before, after):
    cpus = [N.NesMPU(memory=[0] * 65536) for _ in range(2)]
    offset = D.offset(126, START)
    for cpu, rom in zip(cpus, (before, after), strict=True):
        cpu.memory[START:END] = rom[offset:offset + END - START]
    saved = Counter()
    for first, second in product(range(256), repeat=2):
        seed = bytes((first, second, first ^ second, first, second ^ 255, second, first ^ 255))
        for c in cpus:
            c.memory[RNG:RNG + 7] = seed
            c.memory[3] = 0x5a
            c.pc, c.sp, c.a, c.x, c.y = START, 237, 73, 57, 213
            c.p = (0x21, 0x65, 0xed, 0x28)[(first ^ second) & 3]
            c.processorCycles = 0
            run(c, finish)
        a, b = cpus
        assert rng_state(a) == rng_state(b), (first, second, rng_state(a), rng_state(b))
        saved[a.processorCycles - b.processorCycles] += 1
    assert min(saved) > 0
    return dict(sorted(saved.items()))


def vectors(before, after):
    seeds = engine.cold_seeds(before, after)
    lag, normal = engine.lag_pcs(seeds[41][1])
    scene = engine.Q.read_scene(engine.PROFILE)
    counts = Counter()
    for owner, pair in seeds.items():
        for side, seed in enumerate(pair):
            c = engine.Q.Edge.prepare(seed, scene, False)
            N.put(c.memory, NmiDisable=255)
            run(c, lambda q: D.bank_pc(q) == (254, START))
            original = fork(c)
            run(original, finish)

            def check(cut):
                for kind in ('FF', 'IRQ'):
                    if kind == 'IRQ' and cut.p & 4:
                        continue
                    probe = fork(cut)
                    engine.IRQ.interrupt(probe, kind, lag, normal)
                    run(probe, finish)
                    assert rng_state(probe) == rng_state(original), (owner, side, kind, cut.pc)
                    counts[side, kind] += 1

            run(c, finish, check)
    assert len(counts) == 4
    return [[side, kind, count] for (side, kind), count in sorted(counts.items())]


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    args.output.mkdir()
    before = engine.BASE.read_bytes()
    after, patch = compile_step(before, args.output)
    direct = finite(before, after)
    print('Exact RNG step differential', direct, flush=True)
    frames = engine.whole(before, after)
    assert all(set(row['cycles_saved']) <= set(direct) for row in frames)
    cuts = vectors(before, after)
    print('Interrupt cuts', cuts, flush=True)
    result = dict(passed=True, parent_SHA256=P.sha(before), expected_memory_only_SHA256=P.sha(after),
                  patches=[patch], feedback_cases=direct, whole_GameLoop=frames, vectors=cuts,
                  bindings={str(p.resolve()): engine.P.sha(p.read_bytes())
                            for p in (Path(__file__), SOURCE, Path(engine.__file__))})
    (args.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()

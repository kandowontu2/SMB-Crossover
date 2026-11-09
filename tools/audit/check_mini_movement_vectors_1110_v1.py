"""Qualify actual IRQ and lag-NMI cuts for the Mini movement admission."""

from collections import Counter
import json
from pathlib import Path

import check_mini_movement_admission_1110_v1 as M
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork


def audit(images):
    seeds = [M.N.fresh(images[1]), M.P.fixture(images[1], 0, False, False)]
    ranges = [(M.PAD, M.PAD + 15), (M.ENTRY, M.END)]
    counts, minimum = Counter(), [255, 255]
    deepest = {}

    def clone(c, old=False):
        m = slim_fork(c.memory)
        if old:
            m.bundle = images[0]
            for i, tag in enumerate(m.rawtags[:]):
                m.raw_page(i, tag)
        z = M.N.NesMPU(memory=m, pc=c.pc)
        z.a, z.x, z.y, z.p, z.sp = registers(c)
        return z

    def interrupt(c, kind, collect=False):
        ret = c.pc, c.sp
        nmi = kind == 'FF'
        before = M.state(c)
        samples = []
        if nmi:
            assert M.N.get(c.memory, 'NmiDisable') == 255
        else:
            assert not c.p & 4

        def inspect(q):
            minimum[1] = min(minimum[1], q.sp)
            if collect and not q.p & 4:
                key = *M.point(q), q.a, q.p & 1
                if key not in deepest or q.sp < deepest[key].sp:
                    deepest[key] = clone(q)

        for old in (False, True):
            z = clone(c, old)
            z.memory.writes.clear()
            getattr(z, 'nmi' if nmi else 'irq')()
            run(z, lambda q: (q.pc, q.sp) == ret, None if old else inspect)
            samples.append((M.state(z), z.memory.writes))
        assert samples[0] == samples[1], (kind, M.point(c), ret)
        after = samples[0][0]
        assert before[:2] == after[:2], (kind, M.point(c), 'registers or live stack')
        assert before[2][3:6] == after[2][3:6], (kind, M.point(c), 'SMC, maps or private RAM')
        counts[kind] += 1

    def exercise(seed, raw, engine, p, bad_header=False):
        c = M.local(seed, dict(SelectedCharacter=raw, GameEngineSubroutine=engine,
                              NmiDisable=255), 0xa5 if raw != 41 else 0, 0, 91, p)
        if bad_header:
            c.memory.ram[3][0x1fe1] ^= 1
        seen = set()

        def observe(q):
            tag, pc = M.point(q)
            watched = tag == M.TAG and any(lo <= pc < hi for lo, hi in ranges)
            watched |= raw == 41 and (tag, pc) in (M.MINI_VENEER, M.MINI_CHECK)
            watched |= pc == 0x15a and (raw == 41 or not seen.intersection({(tag, pc)}))
            if not watched or (tag, pc) in seen:
                return
            seen.add((tag, pc))
            minimum[0] = min(minimum[0], q.sp)
            interrupt(q, 'FF', collect=True)
            if not q.p & 4:
                interrupt(q, 'IRQ')

        if raw == 41:
            run(c, M.end, observe)
        else:
            run(c, lambda q: M.point(q) == M.foreign_target(raw), observe)

    for raw in (0, 14, 19, 40, 255):
        for p in (0x20, 0x65):
            exercise(seeds[0], raw, 8, p)
    for engine, bad in ((8, False), (8, True), (9, False)):
        for p in (0x20, 0x65):
            exercise(seeds[1], 41, engine, p, bad)
    for c in deepest.values():
        interrupt(c, 'nested_IRQ')
    assert all(counts[k] for k in ['FF', 'IRQ', 'nested_IRQ']) and minimum[1] > 0x7a
    return dict(cuts=dict(counts), minimum_foreground_SP=minimum[0], minimum_ISR_SP=minimum[1])


def main():
    cpu_receipt = M.OUT / 'movement-CPU.json'
    data = json.loads(cpu_receipt.read_text())
    raw = M.BASE.read_bytes()
    assert M.P.sha(raw) == M.PIN == data['base_ROM_SHA256']
    after = install(raw, data['patches'])
    assert M.P.sha(after) == data['expected_memory_ROM_SHA256']
    proof = audit([M.P.bundle(raw), M.P.bundle(after)])
    proof.update(passed=True, base_ROM_SHA256=M.PIN, expected_memory_ROM_SHA256=M.P.sha(after),
                 scope='Actual IRQ and FF lag NMI at every reached changed instruction in the original foreign lanes and Mini warm and rejected-header/fallback lanes; nested IRQ at deepest reached lag-handler state for each PC/A/C.',
                 bindings={p.relative_to(M.R).as_posix():M.P.sha(p.read_bytes())
                           for p in (cpu_receipt, Path(__file__))})
    (M.OUT / 'movement-vectors.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(proof, flush=True)


if __name__ == '__main__':
    main()

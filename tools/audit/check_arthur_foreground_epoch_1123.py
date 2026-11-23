"""Compare Arthur's frame-scoped cache check with the original linked code."""

from collections import Counter
from itertools import product
import json

import check_arthur_side_shortcut_1123 as SideCheck
import compose_arthur_foreground_epoch_1123 as Epoch
from check_mini_funded_actor_1108_v3 import slim_fork


B, N, TRACE = SideCheck.B, SideCheck.N, SideCheck.Roster.Profile
STAMP = 0x1FDF


def compare(old, new, label):
    tagged = new.ram[2][STAMP]
    assert old.ram[2][STAMP] == 0
    new.ram[2][STAMP] = 0
    try:
        SideCheck.Parent.Compare.compare(old, new, label)
    finally:
        new.ram[2][STAMP] = tagged


class Visits:
    def __init__(self, symbols):
        self.symbols = symbols
        self.count = Counter()

    def run(self, cpu, stop):
        self.validated = None
        m = cpu.memory

        def visit(c):
            if TRACE.point(m, c.pc) == (198, self.symbols['FullCheck']):
                self.count['full'] += 1
            if TRACE.point(m, c.pc) == (198, self.symbols['Accepted']) and c.y == 0:
                assert bytes(m.ram[2][0x1FE0:0x1FF0]) == Epoch.HEADER
                self.validated = m[0x0E]
            if TRACE.point(m, c.pc) == (198, self.symbols['Cached']):
                assert c.y != 29 and self.validated and m[0x0E] == self.validated == m.ram[2][STAMP]
                assert bytes(m.ram[2][0x1FE0:0x1FF0]) == Epoch.HEADER
                self.count['fast'] += 1

        SideCheck.CPU.run(cpu, lambda c: (c.pc, c.sp) == stop, visit)


def predicate_controls(models):
    count = 0
    for bad, row, status, context in product(range(-1, 16), (0, 9, 14, 29),
                                              (0x30, 0x71, 0xB0), ('ordinary', 'wrap', 'outside')):
        pair = []
        for index, seed in enumerate(models):
            m = slim_fork(seed)
            N.put(m, CurrentBankC=198, NmiDisable=255)
            m[0x5116] = 198
            m[0x0E] = 0 if context == 'wrap' else 52
            m[0x1F9], m[0x1FA] = (0x52, 0x83) if context != 'outside' else (0xF2, 0x82)
            if index:
                # Seed a prior update's stamp, or a stale value outside Main.
                m.ram[2][STAMP] = 52 if context == 'outside' else 51
            if bad >= 0:
                m.ram[2][0x1FE0 + bad] ^= 0x80
            proof = N.invoke(m, 'ArGenCheckForeground', a=85, x=19, y=row, p=status)
            pair.append((m, tuple(proof[reg] for reg in ('A', 'X', 'Y', 'P'))))
        (old, old_result), (new, new_result) = pair
        assert old_result == new_result, (bad, row, status, context, old_result, new_result)
        assert bool(new_result[-1] & 1) == (bad < 0)
        compare(old, new, (bad, row, status, context))
        count += 1
    return count


def main():
    parent = SideCheck.Arthur.ROM.read_bytes()
    candidate = Epoch.compose(parent)
    direct = Epoch.Side.compose(parent)
    images = parent, direct, candidate
    models = [SideCheck.arthur_opening(image) for image in images]
    linked = Epoch.Side.Prior.Layout.M.assemble(Epoch.SOURCE.read_text(),
                                                {'AUTH': (Epoch.ADDRESS, Epoch.SIZE)})
    symbols = linked['symbols']
    compare(models[0], models[2], 'cold')
    controls = predicate_controls((models[1], models[2]))
    for phase, pad, count in (
        ('standing', 0, 24), ('walking', 1, 24), ('walk left', 2, 12),
        ('jump', 129, 1), ('land', 1, 40), ('stationary', 0, 24),
    ):
        visits = Visits(symbols)
        cycles = [0, 0, 0]
        for _ in range(count):
            for i, m in enumerate(models):
                assert not any(B.flags(m))
                total, _ = B.main_step(m, pad, visits if i == 2 else None)
                cycles[i] += total
            compare(models[0], models[2], phase)
            SideCheck.Parent.Compare.compare(models[0], models[1], phase)
        assert visits.count['fast'] > 0
        print(json.dumps(dict(phase=phase, updates=count, cycles=cycles, calls=dict(visits.count),
                              saved_per_update=(cycles[0] - cycles[2]) / count)), flush=True)
    print(json.dumps(dict(image=Epoch.Side.sha256(candidate).hexdigest(), live_header_cases=controls,
                          files=0, physical_timing_test=False)), flush=True)


if __name__ == '__main__':
    main()

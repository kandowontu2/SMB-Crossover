"""Compare Karnov's shorter warm checks with the original linked game."""

from collections import Counter
from itertools import product
import json
import argparse
from unittest.mock import patch

import check_dkjr_sonic_dispatch_1123 as CPU
import check_prince_epoch_current_1123 as Compare
import compose_karnov_foreground_cookie_1123 as Cookie
import compose_karnov_side_route_1123 as Side
import profile_roster_empty_draw_1123 as Roster


B, N, W = Roster.B, Roster.N, Roster.W
STAMP = 0x1FDF


def compare(old, new, label):
    assert old.ram[2][STAMP] == 0
    marker = new.ram[2][STAMP]
    new.ram[2][STAMP] = 0
    try:
        Compare.compare(old, new, label)
    finally:
        new.ram[2][STAMP] = marker


class Trace:
    def __init__(self, symbols, snapshots=None, cuts=None, interrupt_base=None):
        self.symbols = symbols
        self.snapshots, self.cuts = snapshots, cuts
        self.interrupt_base = interrupt_base
        self.counts = Counter()

    def run(self, cpu, stop):
        m = cpu.memory
        m.combined_terminal = stop
        trusted = None
        mode = None
        service = None
        interrupt_key = None

        def visit(c):
            nonlocal trusted, mode, service, interrupt_key
            bank, pc = Roster.Profile.point(m, c.pc)
            if bank != 157:
                return
            if pc == 0xBB3A:
                interrupt_key = m[0x16C], c.y
                if self.interrupt_base is not None and interrupt_key[0] in (0, 0x2A, 0x57):
                    if interrupt_key not in self.interrupt_base:
                        self.interrupt_base[interrupt_key] = CPU.clone(c)
            if self.interrupt_base is not None:
                return
            if pc == self.symbols['ReadBanks']:
                mode, service = c.a, m[0x16C]
                assert mode in (3, 15)
                self.counts['full' if mode == 15 else 'short'] += 1
                if mode == 3:
                    assert trusted and trusted == m[0x0E] == m.ram[2][STAMP]
                    assert (m[0x01F9], m[0x01FA]) == (0x52, 0x83)
                    assert service not in (0, 0x57)
                elif service == 0:
                    self.counts['movement_full'] += 1
                elif service == 0x57:
                    self.counts['pause_full'] += 1
            if pc == self.symbols['SelectService'] and mode is not None:
                assert all(bytes(m.ram[ram][0x1FE0:0x1FF0]) == Cookie.HEADER for ram in (2, 3))
                if mode == 15 and (m[0x01F9], m[0x01FA]) == (0x52, 0x83):
                    trusted = m[0x0E]
                mode = None
            if self.snapshots is not None and pc == 0xB48E:
                row = m[0x16C]
                if row in (0, 0x2A, 0x57) and row not in self.snapshots:
                    self.snapshots[row] = CPU.clone(c)
            if self.cuts is not None and interrupt_key and interrupt_key[0] in (0, 0x2A, 0x57) and any(
                start <= pc < start + size for start, size in Cookie.LAYOUT.values()
            ):
                key = pc, interrupt_key
                if key not in self.cuts:
                    self.cuts[key] = CPU.clone(c)

        CPU.run(cpu, lambda c: (c.pc, c.sp) == stop, visit)


def start(image, name):
    with patch.dict(Roster.ROSTER, {'KARNOV': (7, 1), 'RYGAR': (7, 0), 'LITTLE MAC': (14, 0)}):
        return Roster.start(image, W.Symbols.bundle(), name)


def cold_snapshot(snapshot, raw, original):
    cpu = CPU.clone(snapshot)
    m = cpu.memory
    m.bundle = dict(m.bundle, raw=raw)
    m.raw_page(1, 157)
    if original:
        m.ram[2][STAMP] = 0
        cpu.pc = 0xBF59
    return cpu


def finish_dispatch(cpu):
    # KrDispatch saved P/A/X/Y, the C bank and five SMC operands
    # before arriving at the admission gate.
    sp = cpu.sp + 10
    m = cpu.memory
    end = (1 + m[0x101 + sp] + 256 * m[0x102 + sp]) & 65535, sp + 2
    CPU.run(cpu, lambda c: (c.pc, c.sp) == end)


def header_controls(images, snapshots):
    counts = Counter()
    for row, bank, byte in product((0, 0x2A, 0x57), (2, 3), range(16)):
        old, new = (cold_snapshot(snapshots[row], raw, i == 0) for i, raw in enumerate(images))
        for c in (old, new):
            c.memory.ram[bank][0x1FE0 + byte] ^= 0x80
        if row == 0x2A and byte >= 4:
            # A new frame or a stale cache always forces the full path.
            new.memory.ram[2][STAMP] = new.memory[0x0E] ^ 0xFF
        for c in (old, new):
            finish_dispatch(c)
            assert not c.p & 1, (row, bank, byte)
        assert CPU.registers(old) == CPU.registers(new)
        assert CPU.live_stack(old) == CPU.live_stack(new)
        compare(old.memory, new.memory, (row, bank, byte))
        counts['rejected header'] += 1
    return dict(counts)


def matched_interrupts(base, cuts, compare_results=compare):
    counts = Counter()
    for (_, key), cut in cuts.items():
        for kind in ('irq', 'nmi'):
            old, new = CPU.clone(base[key]), CPU.clone(cut)
            for c in (old, new):
                c.p &= ~4
                before = CPU.registers(c), CPU.live_stack(c), c.pc, bytes(c.memory[0x15A:0x17B])
                getattr(c, kind)()
                assert c.pc != before[2]
                CPU.run(c, lambda z: (z.pc, z.sp) == (before[2], before[0][-1]))
                assert (CPU.registers(c), CPU.live_stack(c), c.pc, bytes(c.memory[0x15A:0x17B])) == before
                CPU.run(c, lambda z: (z.pc, z.sp) == c.memory.combined_terminal)
            assert CPU.registers(old) == CPU.registers(new)
            assert CPU.live_stack(old) == CPU.live_stack(new)
            compare_results(old.memory, new.memory, (kind, key, hex(cut.pc)))
            counts[kind] += 1
    assert counts
    return dict(counts)


def main():
    from profile_dkjr_empty_current_1123 import Old

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--side-route', action='store_true')
    args = parser.parse_args()
    parent = Old.ROM.read_bytes()
    if Cookie.sha256(parent).hexdigest() == Side.CANDIDATE:
        parent = Side.inverse(parent)
    candidate = (Side if args.side_route else Cookie).compose(parent)
    models = [start(image, 'KARNOV') for image in (parent, candidate)]
    symbols = Cookie.assemble()['symbols']
    snapshots, cuts, interrupt_base = {}, {}, {}
    compare(*models, 'opening')
    for name, pad, updates in (('standing', 0, 24), ('right', 1, 24), ('left', 2, 12),
                               ('jump', 129, 1), ('land', 1, 44), ('rest', 0, 12)):
        totals = [0, 0]
        counts = Counter()
        for index in range(updates):
            sample = name == 'standing' and index == 0
            trace = Trace(symbols, snapshots, cuts if sample else None)
            control = Trace(symbols, interrupt_base=interrupt_base) if sample else None
            for i, m in enumerate(models):
                assert not any(B.flags(m))
                main, _ = B.main_step(m, pad, trace if i else control)
                totals[i] += main
            compare(*models, (name, index))
            assert trace.counts['pause_full'] == trace.counts['movement_full'] == 1
            counts.update(trace.counts)
        print(json.dumps(dict(phase=name, updates=updates, CPU_cycles=totals, admission=dict(counts),
                              saved_per_update=(totals[0] - totals[1]) / updates)), flush=True)
    foreign_controls = {}
    names = ('RYGAR', 'DONKEY KONG', 'LITTLE MAC') if args.side_route else ('RYGAR',)
    for name in names:
        foreign = [start(image, name) for image in (parent, candidate)]
        controls = (0,) * 8 + (1,) * 16 + (129,) + (0,) * 16
        for pad in controls:
            for m in foreign:
                B.main_step(m, pad)
            Compare.compare(*foreign, name)
        foreign_controls[name] = len(controls)
    proof = header_controls((parent, candidate), snapshots)
    print(json.dumps(dict(candidate=Cookie.sha256(candidate).hexdigest(),
                          header_cases=proof, interrupts=matched_interrupts(interrupt_base, cuts),
                          foreign_updates=foreign_controls, files=0)), flush=True)


if __name__ == '__main__':
    main()

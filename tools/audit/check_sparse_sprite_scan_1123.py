"""Compare complete normal game updates and both exits of the sparse draw pass."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json

import check_dkjr_sonic_dispatch_1123 as CPU
import check_prince_epoch_current_1123 as Epoch
import compose_sparse_sprite_scan_1123 as Sparse
import profile_roster_empty_draw_1123 as Profiles


B, N, W = Profiles.B, Profiles.N, Profiles.W
DEAD_TRANSPORT = (0x162, 0x16A, 0x16C, 0x16D, 0x179)


def at(cpu, bank, pc):
    return cpu.pc == pc and Profiles.Profile.point(cpu.memory, pc)[0] == bank


class Capture:
    def __init__(self, *, hooks=None, cuts=None, resident=True):
        self.hooks, self.cuts = hooks, cuts
        self.resident = resident
        self.scan = Sparse.resident()['symbols']['ScanEmpty'] if resident else Sparse.SCAN
        self.worker_bank = 132 if resident else 128 + Sparse.WORK_BANK
        self.calls = Counter()

    def run(self, cpu, stop):
        cpu.memory.combined_terminal = stop

        def visit(c):
            if at(c, 132, Sparse.HOOK) and self.hooks is not None:
                self.hooks.append(CPU.clone(c))
            if at(c, self.worker_bank, self.scan):
                self.calls['scan'] += 1
            if at(c, 132, 0xA038):
                self.calls['alternate_shuffle'] += 1
            if at(c, 132, Sparse.DONE):
                self.calls['continue'] += 1
            if at(c, 132, 0xA261):
                self.calls['world'] += 1
            tag, pc = Profiles.Profile.point(c.memory, c.pc)
            if self.resident:
                in_worker = tag == 132 and (Sparse.OAM_CLEAR <= pc < Sparse.OAM_CLEAR + len(Sparse.OAM_BEFORE)
                                          or Sparse.LEGACY_CLEAR <= pc < Sparse.LEGACY_CLEAR + len(Sparse.LEGACY_BEFORE))
            else:
                in_worker = tag == self.worker_bank and (Sparse.SCAN <= pc < Sparse.SCAN + Sparse.SCAN_SIZE
                             or Sparse.ADVANCE <= pc < Sparse.ADVANCE + Sparse.ADVANCE_SIZE)
            if self.cuts is not None and (in_worker or (tag == 132 and Sparse.HOOK <= pc < Sparse.POSITIVE)):
                key = tag, pc, c.sp, c.p & 5
                if key not in self.cuts:
                    self.cuts[key] = CPU.clone(c)

        CPU.run(cpu, lambda c: (c.pc, c.sp) == stop, visit)


def branch_cases(seed, candidate, resident):
    ctrl = seed.memory
    meta = W.address(ctrl.bundle, 'ObjectMetasprite')
    id_base = W.address(ctrl.bundle, 'Enemy_ID')
    cases = [('empty', 0)] + [('sprite', idx) for idx in range(1, 25)]
    cases += [('stale_id', idx) for idx in range(6)]
    timing = Counter()
    for parity, before, (category, index) in product(range(2), range(24), cases):
        final = []
        for raw in (ctrl.bundle['raw'], candidate):
            cpu = CPU.clone(seed)
            m = cpu.memory
            m.bundle = dict(m.bundle, raw=raw)
            m.raw_page(1, 132)
            m[0x06E0], m[0x0E] = before, 40 + parity
            if category == 'sprite':
                m[meta + index] = 0xFC
            elif category == 'stale_id':
                m[id_base + index] = 0x1B
            trace = Capture(resident=resident)
            trace.run(cpu, (Sparse.DONE, seed.sp))
            final.append((cpu, trace))
        (old, old_trace), (new, new_trace) = final
        assert CPU.registers(old) == CPU.registers(new), (category, index, parity, before,
                                                          CPU.registers(old), CPU.registers(new))
        assert CPU.live_stack(old) == CPU.live_stack(new)
        # The different bank call owns only the five trampoline operands.
        for pos in DEAD_TRANSPORT:
            new.memory[pos] = old.memory[pos]
        Epoch.compare(old.memory, new.memory, (category, index, parity, before))
        assert old_trace.calls == Counter(world=1)
        assert new_trace.calls == Counter(world=int(category != 'empty'), scan=1)
        timing[category, old.processorCycles - new.processorCycles] += 1
    return {kind: dict(sorted((delta, n) for (category, delta), n in timing.items() if category == kind))
            for kind in ('empty', 'sprite', 'stale_id')}


def compared(parent, candidate, bundle, name, cuts, resident):
    models = [Profiles.start(image, bundle, name) for image in (parent, candidate)]
    Epoch.compare(*models, name)
    hooks = []
    report = {}
    for phase, pad, count in (('idle', 0, 8), ('walk', 1, 16), ('jump', 0x81, 12), ('land', 0, 16)):
        totals = [0, 0]
        visits = [Counter(), Counter()]
        for _ in range(count):
            for index, model in enumerate(models):
                trace = Capture(hooks=hooks if not hooks and index == 0 else None,
                                cuts=cuts if phase == 'idle' and index == 1 else None, resident=resident)
                cycles, _ = B.main_step(model, pad, trace)
                totals[index] += cycles
                visits[index].update(trace.calls)
            Epoch.compare(*models, (name, phase))
        report[phase] = dict(updates=count, saved_per_update=(totals[0] - totals[1])/count,
                             visits=list(map(dict, visits)))
    return report, hooks[0] if hooks else None


def clear_cases(seed, candidate):
    original = seed.memory.bundle['raw']
    counts = Counter()
    cases = [(offset, 'suffix') for offset in range(0, 256, 4)]
    cases += [(x, 'full') for x in range(256)]
    for offset, mode in cases:
        endpoints = []
        for raw in (original, candidate):
            cpu = CPU.clone(seed)
            m = cpu.memory
            m.bundle = dict(m.bundle, raw=raw)
            m.raw_page(1, 132)
            m[0x200:0x300] = bytes(range(256))
            m.writes.clear()
            if mode == 'suffix':
                cpu.pc = Sparse.LEGACY_CLEAR
                cpu.stPush(offset)
                stop = 0x85B8, seed.sp
            else:
                cpu.pc = Sparse.OAM_CLEAR
                cpu.a = 0xF8
                cpu.x = offset
                cpu.stPushWord(0x5AFF)
                stop = 0x5B00, seed.sp
            CPU.run(cpu, lambda c: (c.pc, c.sp) == stop)
            endpoints.append((CPU.registers(cpu, 0xEF), CPU.live_stack(cpu),
                              tuple((a, v) for a, v in m.writes if 0x200 <= a < 0x300),
                              m[0x0B], m[0x0C]))
        assert endpoints[0] == endpoints[1], (mode, offset, endpoints[0][:2], endpoints[1][:2])
        assert endpoints[0][2] == tuple((0x200+i, 0xF8) for i in range(0 if mode == 'full' else offset & 0xFC, 256, 4))
        counts[mode] += 1
    return dict(counts)


def live_world_cases(seed, candidate):
    """Exercise real sprite writes with a live world actor in either draw loop."""
    original = seed.memory.bundle['raw']
    cases = Counter()
    for entry, frame, slot, ident in product((Sparse.HOOK, Sparse.ALT_HOOK),
                                             (40, 41), (0, 5), (0x1B, 0x2B)):
        results = []
        for raw in (original, candidate):
            cpu = CPU.clone(seed)
            m = cpu.memory
            m.bundle = dict(m.bundle, raw=raw)
            m.raw_page(1, 132)
            cpu.pc = entry
            N.put(m, CurrentOAMOffset=20, SpriteShuffleOffset=12, FrameCounter=frame,
                  GuestOamRotationActive=1, AreaPointer=0x62, WorldNumber=1)
            for name, value in (('Enemy_ID', ident), ('Enemy_Flag', 1), ('Enemy_State', 0),
                                ('Enemy_X_Position', 110), ('Enemy_PageLoc', 0),
                                ('Enemy_Y_Position', 112), ('Enemy_Y_HighPos', 1)):
                m[W.address(m.bundle, name) + slot] = value
            if ident == 0x1B:
                N.invoke(m, 'InitEnemyObject', x=slot)
                N.invoke(m, 'ProcFirebar', x=slot)
            m.raw_page(1, 132)
            N.put(m, CurrentBank=132)
            m.writes.clear()
            Capture().run(cpu, (Sparse.DONE, seed.sp))
            writes = tuple((a, v) for a, v in m.writes if 0x200 <= a < 0x300)
            results.append((cpu, writes))
        (left, old), (right, new) = results
        assert old == new and CPU.registers(left) == CPU.registers(right)
        assert CPU.live_stack(left) == CPU.live_stack(right)
        Epoch.compare(left.memory, right.memory, (entry, frame, slot, ident))
        kind = 'firebar' if ident == 0x1B else 'small_lift'
        cases[kind + ('_with_OAM_writes' if old else '_culled')] += 1
    assert cases['firebar_with_OAM_writes'] and cases['small_lift_with_OAM_writes']
    return dict(cases)


def main():
    from run_sonic_current_empty_cadence_1122 import ROM

    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('characters', nargs='+', choices=tuple(Profiles.ROSTER))
    args.add_argument('--matrix', action='store_true')
    args.add_argument('--interrupts', action='store_true')
    args.add_argument('--benchmark', action='store_true')
    cli = args.parse_args()
    raw = ROM.read_bytes()
    candidate = Sparse.compose_benchmark(raw) if cli.benchmark else Sparse.compose(raw)
    cuts = {} if cli.interrupts else None
    host = W.Symbols.bundle()
    first = None
    for name in cli.characters:
        phases, observed = compared(raw, candidate, host, name, cuts, not cli.benchmark)
        first = first or observed
        print('SPARSE MAIN ' + json.dumps(dict(character=name, phases=phases),
                                          separators=(',', ':')), flush=True)
    report = dict(parent=Sparse.Parent.CORRECTED, candidate=sha256(candidate).hexdigest(), outputs=0)
    if cli.matrix:
        assert first is not None, 'Choose a character which uses the shared renderer'
        report['matrix'] = branch_cases(first, candidate, not cli.benchmark)
        if not cli.benchmark:
            report['OAM_clear'] = clear_cases(first, candidate)
            report['live_world_draw'] = live_world_cases(first, candidate)
    if cuts:
        report['interrupts'] = CPU.interrupts(cuts)
    print('SPARSE PROOF ' + json.dumps(report, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()

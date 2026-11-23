"""Compare Arthur's direct terrain call through actual linked gameplay."""

from collections import Counter
from itertools import product
import json
from unittest.mock import patch

import check_dkjr_sonic_dispatch_1123 as CPU
import check_donkey_side_shortcut_1123 as Parent
import compose_arthur_side_shortcut_1123 as Side
import profile_roster_empty_draw_1123 as Roster
import run_arthur_mushroom_1123 as Arthur


B, N = Roster.B, Roster.N


class Trace:
    def __init__(self, cuts=None, snapshot=None, interrupt_base=None):
        self.calls = Counter()
        self.cuts, self.snapshot = cuts, snapshot
        self.interrupt_base = interrupt_base
        self.services = []

    def run(self, cpu, stop):
        cpu.memory.combined_terminal = stop
        pending = None
        side_return = None

        def visit(c):
            nonlocal pending, side_return
            m = c.memory
            tag, pc = Roster.Profile.point(m, c.pc)
            if side_return == (pc, c.sp):
                side_return = None
            if pending and (pc, c.sp) == pending:
                self.services.append(('return', CPU.registers(c)[:4], m[6], m[7]))
                pending = None
            if (tag, pc) == (161, 0xBEA2):
                if self.snapshot is not None and not self.snapshot:
                    self.snapshot.append(CPU.clone(c))
                self.calls['collision_entry'] += 1
            if (tag, pc) == (217, 0xBC58):
                assert m[0x16C] == 0x58 and m[0x16D] == 0xBC
                side_return = (m[0x101 + c.sp] + 256 * m[0x102 + c.sp] + 1) & 65535, c.sp + 2
                self.calls['shared_side_gate'] += 1
                if self.interrupt_base is not None and c.y not in self.interrupt_base:
                    self.interrupt_base[c.y] = CPU.clone(c)
            if (tag, pc) == (252, 0xAAD9):
                self.calls['generic_side'] += 1
            if (tag, pc) == (154, 0xBD3D):
                self.calls['arthur_side'] += 1
                self.services.append(('entry', CPU.registers(c)[:4]))
                ret = (m[0x101 + c.sp] + 256 * m[0x102 + c.sp] + 1) & 65535
                pending = ret, c.sp + 2
            if (tag, pc) == (193, 0xBFD8):
                self.calls['donkey_side'] += 1
            if self.cuts is not None and side_return and tag == 217 and any(
                start <= pc < start + size for start, size in Side.LAYOUT.values()
            ):
                key = pc, c.y, c.p & 5
                if key not in self.cuts:
                    self.cuts[key] = CPU.clone(c)

        CPU.run(cpu, lambda c: (c.pc, c.sp) == stop, visit)


def arthur_opening(raw):
    with patch.object(Arthur, 'controller', lambda image: b''):
        model = Arthur.cold(raw)
    for _ in range(4):
        B.main_step(model, 0)
    assert B.position(model) == 40 and N.get(model, 'ArHostReady') == 0xA7
    return model


def arthur_compare(parent, candidate):
    models = [arthur_opening(rom) for rom in (parent, candidate)]
    cuts, interrupt_base, snapshot = {}, {}, []
    Parent.Compare.compare(*models, 'Arthur start')
    phases = (
        ('standing', 0, 24), ('walking', 1, 24), ('left', 2, 12),
        ('jump', 129, 1), ('landing', 1, 40), ('standing again', 0, 16),
    )
    for phase, pad, updates in phases:
        cycles, calls = [0, 0], [Counter(), Counter()]
        for update in range(updates):
            sample = phase == 'standing' and update == 0
            old = Trace(snapshot=snapshot, interrupt_base=interrupt_base if sample else None)
            new = Trace(cuts=cuts if sample else None)
            for i, trace in enumerate((old, new)):
                assert not any(B.flags(models[i]))
                main, _ = B.main_step(models[i], pad, trace)
                cycles[i] += main
                calls[i].update(trace.calls)
            Parent.Compare.compare(*models, phase)
            assert old.services == new.services, (phase, old.services, new.services)
        assert calls[0]['arthur_side'] == calls[1]['arthur_side']
        assert calls[0]['generic_side'] == calls[0]['arthur_side'] and not calls[1]['generic_side']
        print(json.dumps(dict(character='Arthur', phase=phase, updates=updates, calls=list(map(dict, calls)),
                              cycles=cycles, savings=(cycles[0] - cycles[1]) / updates)), flush=True)
    assert cuts and snapshot
    return matched_interrupts(interrupt_base, cuts), snapshot[0]


def matched_interrupts(base, cuts):
    counts = Counter()
    for cut in cuts.values():
        for kind in ('irq', 'nmi'):
            old, new = CPU.clone(base[cut.y]), CPU.clone(cut)
            for c in (old, new):
                N.put(c.memory, NmiDisable=255)
                c.p &= ~4
                pc = c.pc
                before = CPU.registers(c), CPU.live_stack(c), tuple(c.memory.rawtags)
                getattr(c, kind)()
                assert c.pc != pc
                CPU.run(c, lambda z: (z.pc, z.sp) == (pc, before[0][-1]))
                assert before == (CPU.registers(c), CPU.live_stack(c), tuple(c.memory.rawtags))
                Trace().run(c, c.memory.combined_terminal)
            assert CPU.registers(old) == CPU.registers(new)
            assert CPU.live_stack(old) == CPU.live_stack(new)
            Parent.Compare.compare(old.memory, new.memory, ('Arthur interrupt', kind, hex(cut.pc), cut.y))
            counts[kind] += 1
    return dict(counts)


def terrain_controls(seed, images):
    cases = 0
    for engine, probe, x, y, tile in product((4, 5, 8, 9, 11), range(3, 7),
                                              (7, 254, 279), (32, 176, 232), (0, 0x54, 0x25)):
        pair = []
        for raw in images:
            c = CPU.clone(seed)
            m = c.memory
            m.bundle = dict(m.bundle, raw=raw)
            N.put(m, GameEngineSubroutine=engine, Player_X_Position=x & 255,
                  Player_PageLoc=x >> 8, Player_Y_Position=y)
            c.y = probe
            start = Roster.W.address(m.bundle, 'Block_Buffer_1')
            for addr in range(start, start + 416):
                m[addr] = tile
            ret = (m[0x101 + c.sp] + 256 * m[0x102 + c.sp] + 1) & 65535
            Trace().run(c, (ret, c.sp + 2))
            pair.append(c)
        old, new = pair
        case = engine, probe, x, y, tile
        assert CPU.registers(old) == CPU.registers(new), (case, CPU.registers(old), CPU.registers(new))
        assert CPU.live_stack(old) == CPU.live_stack(new), case
        Parent.Compare.compare(old.memory, new.memory, case)
        cases += 1
    return cases


def foreign_compare(parent, candidate):
    names = ('DONKEY KONG', 'DONKEY KONG JR', 'LITTLE MAC', 'SAMUS ARAN', 'BASS')
    # Menu slots are the native cursor coordinates flattened by UI.seed.
    with patch.dict(Roster.ROSTER, {'DONKEY KONG JR': (27, 1), 'LITTLE MAC': (14, 0)}):
        models_bundle = Roster.W.Symbols.bundle()
        for name in names:
            models = [Roster.start(rom, models_bundle, name) for rom in (parent, candidate)]
            totals = [0, 0]
            for pad, updates in ((0, 12), (1, 12), (129, 1), (0, 16)):
                for _ in range(updates):
                    for i, model in enumerate(models):
                        main, _ = B.main_step(model, pad, Trace())
                        totals[i] += main
                    Parent.Compare.compare(*models, name)
            print(json.dumps(dict(character=name, cycles=totals, matching_updates=41)), flush=True)


def main():
    parent = Arthur.ROM.read_bytes()
    candidate = Side.compose(parent)
    proof, seed = arthur_compare(parent, candidate)
    cases = terrain_controls(seed, (parent, candidate))
    foreign_compare(parent, candidate)
    print(json.dumps(dict(candidate=Side.sha256(candidate).hexdigest(), interrupts=proof,
                          terrain_cases=cases, files=0)), flush=True)


if __name__ == '__main__':
    main()

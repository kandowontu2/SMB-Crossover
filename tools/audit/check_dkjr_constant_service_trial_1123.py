"""Test the DK Jr. constant returns with the real linked caller and bank exit.

The trial code is supplied to instruction fetches only. It occupies no
cartridge bytes, never shadows game data, and cannot produce a ROM.
"""

import argparse
from collections import Counter
import json
from unittest.mock import patch

import check_dkjr_rect_read_current_1123 as RectCheck
import compose_dkjr_scene_hot_1123 as Scene
import profile_dkjr_empty_current_1123 as Profile
from check_mini_funded_actor_1108_v3 import live_stack, slim_fork


P, W = Profile, Profile.W
SOURCE = Scene.Head.R / 'tools/reference/dkjr_constant_service_trial_1123.s'
HOOK, TRIAL, EARLY = 0xB087, 0xBBB5, 0xBDB0
SERVICES = {0xB0A7: None, 0xB0B0: 2, 0xB0B3: 1, 0xB0F2: None}
OP_SIZE = {'imp': 1, 'imm': 2, 'rel': 2, 'abs': 3, 'abx': 3}


class FetchBus(W.ControllerBus):
    instruction = ()

    def __getitem__(self, address):
        if isinstance(address, int) and self.instruction:
            pc, code = self.instruction
            if pc <= address < pc + len(code):
                return code[address - pc]
        return super().__getitem__(address)


def reg(cpu):
    return cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp


class Observe:
    def __init__(self, code=b'', early_return=None):
        self.code = code
        self.early_return = early_return
        self.early_active = False
        self.results = []
        self.shortcuts = Counter()
        self.callers = Counter()

    def fetch(self, cpu):
        bus = cpu.memory
        if not self.code:
            return
        bus.instruction = ()
        bank, pc = P.point(bus, cpu.pc)
        if self.early_return and bank == 193 and pc in SERVICES:
            target = 0xA7E4 if pc in (0xB0B0, 0xB0B3) else 0xAF9D
            assert bytes(bus[pc:pc + 3]) == bytes((0x4C, target & 255, target >> 8))
            self.early_active = True
            bus.instruction = pc, bytes((0x4C, EARLY & 255, EARLY >> 8))
        elif self.early_active and bank == 193 and EARLY <= pc < EARLY + len(self.code):
            offset = pc - EARLY
            kind = cpu.disassemble[self.code[offset]][1]
            bus.instruction = pc, self.code[offset:offset + OP_SIZE[kind]]
        elif not self.early_return and (bank, pc) == (213, HOOK):
            assert bytes(bus[pc:pc + 3]) == b'\x20\xf0\xb8'
            bus.instruction = pc, bytes((0x20, TRIAL & 255, TRIAL >> 8))
        elif bank == 213 and TRIAL <= pc < TRIAL + len(self.code):
            offset = pc - TRIAL
            kind = cpu.disassemble[self.code[offset]][1]
            bus.instruction = pc, self.code[offset:offset + OP_SIZE[kind]]

    def run(self, cpu, stop):
        bus = cpu.memory
        active = None
        sp_after = None
        prior_pc = None
        for _ in range(180000):
            if (cpu.pc, cpu.sp) == stop:
                assert active is None
                return
            bank, pc = P.point(bus, cpu.pc)
            if bank == 193 and pc in SERVICES:
                assert active is None
                assert bus[0x16C] + 256 * bus[0x16D] == pc
                active = pc, reg(cpu)
                sp_after = cpu.sp
            if active and (bank, pc) == (193, 0xAB4B) and prior_pc == 0x017A:
                assert cpu.x == sp_after - 10
                self.shortcuts[active[0]] += 1
            is_early = self.early_return is not None and pc == self.early_return
            if active and bank == 193 and cpu.sp == sp_after and (is_early or pc == 0xAB71):
                target, args = active
                if is_early:
                    self.shortcuts[target] += 1
                result = reg(cpu)
                assert result[0:2] == args[0:2]
                assert result[2] == (args[2] if SERVICES[target] is None else SERVICES[target])
                nz = (args[0] & 0x80) | (2 if args[0] == 0 else 0)
                assert result[3] == ((args[3] & 0x7D) | nz | 1)
                self.results.append((target, args, result))
                active = None
            if (bank, pc) == (213, HOOK):
                self.callers[bytes(bus[0x104 + cpu.sp:0x107 + cpu.sp]).hex()] += 1
            self.fetch(cpu)
            try:
                assert bus[pc], ('Unexpected BRK', bank, hex(pc))
                cpu.step()
            finally:
                bus.instruction = ()
            if is_early or (bank, pc) in ((193, 0xAF9D), (193, 0xA7E4)):
                self.early_active = False
            prior_pc = pc
        raise AssertionError(('Linked Main did not return', stop, hex(cpu.pc)))


def compare(a, b):
    assert a.rawtags == b.rawtags and a.chr_latches == b.chr_latches
    assert a.ram == b.ram and a.vram == b.vram
    for lo, hi in ((0, 0x100), (0x15A, 0x17B), (0x200, 0x800), (0x5C00, 0x8000)):
        assert bytes(a[lo:hi]) == bytes(b[lo:hi]), (hex(lo), hex(hi))
    # The shortcut deliberately omits switches into and back out of DK Jr.'s
    # code/data banks. All other hardware writes and final mappings must match.
    writes = lambda m: [(at, value) for at, value in m.writes
                        if 0x2000 <= at < 0x6000 and at not in (0x5115, 0x5116)]
    assert writes(a) == writes(b)


def run_public(cpu, trace, stop, observe=None):
    bus = cpu.memory
    hit = False
    for _ in range(12000):
        if (cpu.pc, cpu.sp) == stop:
            return hit
        bank, pc = P.point(bus, cpu.pc)
        hit |= (bank, pc) == (193, trace.early_return)
        if observe:
            observe(cpu, trace)
        trace.fetch(cpu)
        try:
            assert bus[pc], ('Unexpected public service BRK', bank, hex(pc))
            cpu.step()
        finally:
            bus.instruction = ()
        if (bank, pc) in ((193, 0xAF9D), (193, 0xA7E4)):
            trace.early_active = False
    raise AssertionError(('Public service did not return', stop, hex(cpu.pc)))


def controls(trial, code, early_return):
    """Test public entry controls without changing the normal opening sample."""
    total = Counter()
    for name, owner, bank in (
        ('expired-stamp', 40, None), ('corrupt-data-header', 40, 2),
        ('corrupt-code-header', 40, 3), ('quick-man', 42, None),
    ):
        for target in SERVICES:
            pair = []
            for body in (b'', code):
                model = slim_fork(trial)
                model[0x6002] = owner
                model[0x16A], model[0x16C], model[0x16D] = 0x84, target & 255, target >> 8
                if bank is not None:
                    model.ram[bank][0x1FE0] ^= 0xFF
                if name == 'expired-stamp':
                    model.ram[2][0x8FF] = model[0x0E] ^ 0xFF
                cpu = P.N.NesMPU(memory=model, pc=0x015A)
                cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0xC1, 0x71, 0x38, 0x71, 0xE0
                cpu.stPushWord(0x5AFF)
                W.clear_logs(model)
                trace = Observe(body, early_return if body else None)
                assert not run_public(cpu, trace, (0x5B00, 0xE0))
                pair.append(cpu)
            assert reg(pair[0]) == reg(pair[1]), (name, target)
            compare(pair[0].memory, pair[1].memory)
            total[name] += 1
    return dict(total)


def invoke_code(trial, code, early_return, target):
    model = slim_fork(trial)
    assert model[0x6002] == 40 and model[0x0E]
    model[0x16A], model[0x16C], model[0x16D] = 0x84, target & 255, target >> 8
    P.N.put(model, NmiDisable=0xFF)
    cpu = P.N.NesMPU(memory=model, pc=0x015A)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0xC1, 0x71, 0x38, 0x71, 0xE0
    cpu.stPushWord(0x5AFF)
    return cpu, Observe(code, early_return)


def interrupt_controls(trial, code, early_return):
    completed = Counter()
    for target in SERVICES:
        cpu, trace = invoke_code(trial, code, early_return, target)
        stop = (0x5B00, 0xE0)
        cuts = {}

        def collect(c, observer):
            bank, pc = P.point(c.memory, c.pc)
            if (bank == 193 and EARLY <= pc < EARLY + len(code)) or (bank == 213 and pc == 0xA8DC):
                cuts[bank, pc] = RectCheck.Q.clone(c), observer.early_active

        assert run_public(cpu, trace, stop, collect) and cuts
        for cut, active in cuts.values():
            for kind in ('irq', 'nmi'):
                z = RectCheck.Q.clone(cut)
                z.p &= ~4
                before = reg(z), live_stack(z), tuple(z.memory.rawtags), bytes(z.memory[0x15A:0x17B])
                point = z.pc, z.sp
                getattr(z, kind)()
                assert (z.pc, z.sp) != point
                RectCheck.finish(z, point)
                after = reg(z), live_stack(z), tuple(z.memory.rawtags), bytes(z.memory[0x15A:0x17B])
                assert before == after, (target, kind, hex(z.pc))
                observer = Observe(code, early_return)
                observer.early_active = active
                assert run_public(z, observer, stop)
                assert reg(z) == reg(cpu)
                completed[kind] += 1
    return dict(completed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--early', action='store_true')
    args = parser.parse_args()
    rom = P.Old.ROM.read_bytes()
    assert Scene.sha256(rom).hexdigest() == Scene.PIN
    source = Scene.Head.assemble(SOURCE.read_text(), {'TRIAL': (TRIAL, 110), 'EARLY_TRIAL': (EARLY, 110)})
    assert source['symbols']['ConstantService'] == TRIAL
    assert source['symbols']['FastEntry'] == EARLY
    code = source['images']['EARLY_TRIAL' if args.early else 'TRIAL']
    early_return = source['symbols']['FastReturn'] if args.early else None
    baseline = P.Old.boot(rom)
    with patch.object(W, 'ControllerBus', FetchBus):
        trial = P.Old.boot(rom)
    compare(baseline, trial)
    linked = []
    for name, pad, count in (
        ('standing', 0, 16), ('walking', 1, 24), ('left', 2, 10),
        ('jump', 129, 1), ('landing', 1, 54),
    ):
        traces = Observe(), Observe(code, early_return)
        totals = [0, 0]
        wraps = 0
        for _ in range(count):
            for i, (model, trace) in enumerate(zip((baseline, trial), traces, strict=True)):
                assert not any(P.Opening.flags(model))
                totals[i] += P.Opening.main_step(model, pad, trace)[0]
            compare(baseline, trial)
            wraps += trial[0x0E] == 0
        control, fast = traces
        assert control.results == fast.results
        if not args.early:
            assert control.callers == fast.callers
        per_service = Counter(target for target, _, _ in control.results)
        expected = per_service.copy()
        expected.subtract({service: wraps for service in SERVICES})
        assert not control.shortcuts and fast.shortcuts == expected, (name, fast.shortcuts, expected)
        row = dict(phase=name, updates=count, cycle_totals=totals,
                   saved_per_update=(totals[0] - totals[1]) / count,
                   shortcut_calls=sum(fast.shortcuts.values()),
                   frame_counter_wraps=wraps,
                   other_authenticated_callers=dict(fast.callers))
        linked.append(row)
        print(json.dumps(row, separators=(',', ':')), flush=True)
    print(json.dumps(dict(trial_code_bytes=len(code), measured_updates=sum(v['updates'] for v in linked),
                          linked_services=sum(v['shortcut_calls'] for v in linked),
                          rejected_shortcut_controls=controls(trial, code, early_return) if args.early else {},
                          interrupt_returns=interrupt_controls(trial, code, early_return) if args.early else {},
                          cartridge_bytes_written=0, physical_cadence_qualified=False)), flush=True)


if __name__ == '__main__':
    main()

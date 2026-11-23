"""Check paired native state and instruction counts for the Prince epoch change."""

import argparse
from collections import Counter
import json

import check_dkjr_sonic_dispatch_1123 as Existing
import compose_prince_epoch_current_1123 as Epoch
import probe_prince_hidden_life_current_1123 as Prince


B, N, W = Existing.B, Existing.N, Existing.W
OWNER_CASES = ('Prince', 'DK', 'Mini', 'Sonic', 'Super')


def selector_domain(parent, candidate):
    from py65.devices.mpu6502 import MPU

    entry = Epoch.SELECTOR[0] + 3
    machines = [MPU(memory=bytearray(65536)) for _ in range(2)]
    for cpu, image in zip(machines, (parent, candidate), strict=True):
        offset = Epoch.Shared.S.off(65, Epoch.SELECTOR[0])
        end = Epoch.SELECTOR[0] + Epoch.SELECTOR[1]
        cpu.memory[Epoch.SELECTOR[0]:end] = image[offset:offset + Epoch.SELECTOR[1]]
    stops = {0xA738, 0xA779, 0xA790, 0xA791, 0xA794, 0xB031}
    counts = Counter()
    for owner in range(256):
        for high in (0xAA, 0xAF, 0xB0, 0xB1):
            for low in range(256):
                routes = []
                for cpu in machines:
                    cpu.pc, cpu.sp, cpu.p = entry, 210, 0x31
                    cpu.memory[0x6002] = owner
                    cpu.memory[0x16C], cpu.memory[0x16D] = low, high
                    for _ in range(40):
                        if cpu.pc in stops:
                            break
                        assert cpu.memory[cpu.pc]
                        cpu.step()
                    else:
                        raise AssertionError(('Selector entry bound', owner, high, low))
                    routes.append(cpu.pc)
                offset = (low - 0x8C) & 255
                eligible = high == 0xB0 and 0 < offset < 114
                prince = owner == 38 and eligible
                early = owner in (38, 40, 41, 43) and eligible
                assert (routes[1] == 0xA738) == early, (owner, high, low)
                if prince:
                    assert routes[0] == 0xA779
                else:
                    assert routes[0] == routes[1], (owner, high, low, routes)
                if early:
                    cpu = machines[1]
                    assert cpu.memory[0x16C] == 0xB0 and cpu.memory[0x16D] == high
                    assert cpu.sp == 209 and cpu.memory[0x100 + cpu.sp + 1] == offset
                else:
                    assert machines[1].memory[0x16C] == low
                if high == 0xB0 and low == 0x8C and 37 <= owner <= 43:
                    assert routes == [0xA779, 0xA779]
                    counts['row_zero_full'] += 1
                counts['cases'] += 1
                counts['new_Prince_quick'] += prince
                counts['canonical_quick'] += early
    return dict(counts)


def enter(image, owner):
    if owner != 'Prince':
        return Existing.enter(image, owner)
    _, _, cookie, _ = Epoch.Reach.C.extract(image)
    def authenticate(raw):
        assert raw == image

    use = Prince.clone(Prince.cold, dict(authenticate=authenticate, COOKIE=cookie.hex()))
    return use(image)


def compare(left, right, owner):
    # This established linked-frame boundary has no active caller stack.
    # Stack slots left behind by a shorter transport are not live state.
    native = (*range(0x17B), *range(0x1FE, 0x800), *range(0x5C00, 0x8000))
    mismatches = [hex(i) for i in native if left[i] != right[i]]
    assert not mismatches, (owner, mismatches[:15])
    for name in ('rawtags', 'chr_latches', 'vram', 'ppuctrl'):
        assert getattr(left, name) == getattr(right, name), (owner, name)
    assert all(a == b for a, b in zip(left.ram, right.ram, strict=True)), owner


class Visits:
    def __init__(self, cuts=None):
        self.counts = Counter()
        self.context = []
        self.cuts = cuts

    def run(self, cpu, stop):
        m = cpu.memory
        m.combined_terminal = stop
        guarded = m.bundle['raw'][Epoch.Shared.S.off(85, Epoch.READ_EPOCH)] == 0x4C
        for _ in range(500000):
            if (cpu.pc, cpu.sp) == stop:
                return
            pc = cpu.pc
            tag = m.rawtags[(pc - 0x8000) // 8192] if pc >= 0x8000 else -1
            if (tag, pc) == (193, 0xAF27):
                self.counts['full'] += 1
            if (tag, pc) == (213, 0xA8DC):
                self.counts['quick'] += 1
                if guarded:
                    target = m[0x16C] + 256 * m[0x16D]
                    assert target in (0xB0B0, 0xB0BC, 0xA8DC), hex(target)
            if guarded and (tag, pc) == (213, Epoch.PRINCE_READER):
                self.counts['prince_reader'] += 1
                self.context.append((m[0x5FFF], m[0x1F9], m[0x1FA], m[15],
                                     m[0x777], m[0x74A], m.ram[2][0xAA],
                                     m.ram[2][0xA9], m[0xE]))
            if guarded and (tag, pc) == (213, 0xB075) and cpu.x == 38:
                self.counts['prince_valid'] += 1
            if self.cuts is not None:
                watched = ((tag == 193 and 0xA743 <= pc < 0xA77E) or
                           (tag == 213 and (0xA8DC <= pc < 0xA900 or
                            Epoch.READ_EPOCH <= pc < Epoch.NEXT_PUBLIC_ROW)) or
                           (tag == 161 and (0xBED1 <= pc < 0xBED8 or 0xBFE1 <= pc < 0xC000)) or
                           (tag == 254 and 0x80C2 <= pc < 0x80C9))
                if watched:
                    key = tag, pc, cpu.sp, cpu.p & 5
                    if key not in self.cuts:
                        self.cuts[key] = Existing.clone(cpu)
            assert m[pc], ('Unexpected BRK', tag, hex(pc))
            cpu.step()
        raise AssertionError(('Bounded linked frame', hex(cpu.pc), cpu.sp))


def paired(parent, candidate, owner, count):
    a, b = [enter(rom, owner) for rom in (parent, candidate)]
    if owner != 'Prince':
        for frame in range(300):
            ready = [tuple(N.get(m, k) for k in ('OperMode', 'OperMode_Task', 'GameEngineSubroutine'))
                     == (1, 3, 8) for m in (a, b)]
            assert ready[0] == ready[1]
            if ready[0]:
                break
            for m in (a, b):
                B.main_step(m, 0, Visits())
            compare(a, b, owner)
        else:
            raise AssertionError(('Cold entry bound', owner, frame))
    compare(a, b, owner)
    phases = {}
    for phase, pad, size in (('settle', 0, 4), ('idle', 0, count), ('walk', 1, count),
                             ('jump', 0x81, 1), ('air', 1, count), ('release', 0, count)):
        cycles = [0, 0]
        invocations = [Counter(), Counter()]
        contexts = Counter()
        for _ in range(size):
            observers = [Visits(), Visits()]
            for i, m in enumerate((a, b)):
                cycles[i] += B.main_step(m, pad, observers[i])[0]
                invocations[i].update(observers[i].counts)
            compare(a, b, owner)
            contexts.update(row[:7] for row in observers[1].context)
        phases[phase] = dict(updates=size, cycles=cycles, saved_per_update=(cycles[0]-cycles[1])/size,
                             dispatch=list(map(dict, invocations)),
                             prince_contexts=[(row, n) for row, n in contexts.items()])
    return phases


def gate_cases(image):
    from probe_prince_wram1_funding_1123 import call

    base = enter(image, 'Prince')
    # A directed call uses the same state that the linked Main test observes
    # at the fast entry. Change just one field per rejection case.
    base.raw_page(1, 213)
    base.raw_page(2, 201)
    base[0x7DA1] = 201
    base[0x5FFF] = 1
    base[0x1F9], base[0x1FA] = 0x52, 0x83
    base[0xE], base.ram[2][0xA9], base.ram[2][0xAA] = 40, 40, 1
    N.put(base, GameEngineSubroutine=8, GamePauseStatus=0, TimerControl=0)
    checks = [
        ('ordinary', (), True),
        ('no_foreground', ((None, 0x5FFF, 0),), False),
        ('wrong_stack_low', ((None, 0x1F9, 0x53),), False),
        ('wrong_stack_high', ((None, 0x1FA, 0x84),), False),
        ('engine_transition', ((None, 0xF, 7),), False),
        ('paused', ((None, 0x777, 1),), False),
        ('timer_hold', ((None, 0x74A, 1),), False),
        ('no_update', ((2, 0xAA, 0),), False),
        ('old_update', ((2, 0xA9, 39),), False),
        ('wrap', ((None, 0xE, 0), (2, 0xA9, 0)), False),
        ('state_cookie_prefix', ((2, 0x1FE0, 0),), False),
        ('state_cookie_owner', ((2, 0x1FE1, 41),), False),
        ('code_cookie_prefix', ((3, 0x1FE0, 0),), False),
        ('code_cookie_owner', ((3, 0x1FE1, 41),), False),
    ]
    for name, edits, expected in checks:
        m = N.fork(base)
        for bank, address, value in edits:
            if bank is None:
                m[address] = value
            else:
                m.ram[bank][address] = value
        banks = tuple(m.rawtags)
        headers = [bytes(m.ram[i][0x1FE0:0x1FF0]) for i in (2, 3)]
        result = call(m, Epoch.CANONICAL_ROW, y=91)
        assert bool(result['regs'][3] & 1) == expected, (name, result)
        assert tuple(m.rawtags) == banks and m[0x7DA1] == 201 and result['regs'][2] == 91, name
        assert [bytes(m.ram[i][0x1FE0:0x1FF0]) for i in (2, 3)] == headers, name
    return [name for name, _, _ in checks]


def irq_cases(image):
    m = enter(image, 'Prince')
    for _ in range(4):
        B.main_step(m, 0, Visits())
    cuts = {}
    B.main_step(m, 0, Visits(cuts))
    assert any(tag == 213 and pc == Epoch.PRINCE_READER for tag, pc, _, _ in cuts)
    assert any(tag == 193 and pc == 0xA779 for tag, pc, _, _ in cuts)
    result = Existing.interrupts(cuts)
    assert result['returns'].get('IRQ') and result['returns'].get('busyNMI')
    return result


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('owners', nargs='+', choices=OWNER_CASES + ('selector', 'gate', 'irq'))
    a.add_argument('--count', type=int, default=6)
    a.add_argument('--side', action='store_true')
    args = a.parse_args()
    assert 4 <= args.count <= 24
    from run_prince_oneup_lift_native_1123 import Timing
    parent = Timing.ROM.read_bytes()
    if args.side:
        import compose_prince_side_current_1123 as Side
        candidate, _ = Side.compose(parent)
    else:
        candidate, _ = Epoch.compose(parent)
    for owner in args.owners:
        if owner == 'selector':
            print('PRINCE EPOCH SELECTOR ' + json.dumps(selector_domain(parent, candidate),
                  separators=(',', ':')), flush=True)
            continue
        if owner == 'gate':
            print('PRINCE EPOCH GATE ' + json.dumps(gate_cases(candidate),
                  separators=(',', ':')), flush=True)
            continue
        if owner == 'irq':
            print('PRINCE EPOCH IRQ ' + json.dumps(irq_cases(candidate),
                  separators=(',', ':')), flush=True)
            continue
        phases = paired(parent, candidate, owner, args.count)
        print('PRINCE EPOCH PAIR ' + json.dumps(dict(owner=owner, candidate=Epoch.H(candidate),
              phases=phases, outputs=0), separators=(',', ':')), flush=True)
        if owner == 'Prince':
            assert phases['idle']['dispatch'][1].get('prince_valid', 0) > 0
            assert phases['idle']['saved_per_update'] > 3000


if __name__ == '__main__':
    main()

"""Compare the Bub and Bob cache change through the linked MMC5 game loop."""

from collections import Counter
from hashlib import sha256
from itertools import product
import json
from unittest.mock import patch

import check_dkjr_sonic_dispatch_1123 as CPU
import check_prince_epoch_current_1123 as Shared
import compose_bub_epoch_1123 as Epoch
import profile_roster_empty_draw_1123 as Roster


B, N, W = Roster.B, Roster.N, Roster.W
SLOTS = {'BUB': (25, 1), 'BOB': (25, 2)}


class Trace:
    def __init__(self, candidate, snapshots=None, cuts=None):
        self.candidate = candidate
        self.snapshots, self.cuts = snapshots, cuts
        self.count = Counter()
        self.movement_epoch = None
        self.stamped = None

    def run(self, cpu, stop):
        m = cpu.memory
        m.combined_terminal = stop
        service = None

        def visit(c):
            nonlocal service
            point = Roster.Profile.point(m, c.pc)
            if point in ((193, 0xA76B), (193, 0xA779)):
                service = m[0x16C]
                if self.snapshots is not None and service not in self.snapshots:
                    self.snapshots[service] = CPU.clone(c)
            if self.cuts is not None and service is not None:
                tag, pc = point
                touched = ((tag == 193 and 0xA76B <= pc < 0xA779) or
                           (tag == 3 and Epoch.STAMP_CODE <= pc < Epoch.STAMP_CODE + 12) or
                           (tag == 213 and (0xA8DC <= pc < 0xA8FE or 0xB08F <= pc < 0xB0FE)))
                if touched and (point, service) not in self.cuts:
                    self.cuts[point, service] = CPU.clone(c)
            if point == (193, 0xAF44) and m[0x16C] == 0x8C and m[0x16D] == 0xB0:
                self.movement_epoch = m[0x0E]
                self.count['full_movement'] += 1
            if point == (193, 0xAF27):
                self.count['full'] += 1
            if point == (3, Epoch.STAMP_CODE):
                assert self.candidate and self.movement_epoch == m[0x0E]
                self.stamped = self.movement_epoch
                self.count['stamp'] += 1
            if point == (213, 0xB07D) and c.x == 39:
                assert self.stamped and self.stamped == m[0x0E] == m.ram[2][Epoch.STAMP - 0xC000]
                self.count['fast'] += 1

        CPU.run(cpu, lambda c: (c.pc, c.sp) == stop, visit)


def compare(parent, candidate, label, edits, header):
    native = (*range(0x17B), *range(0x1FE, 0x800), *range(0x5C00, 0x8000))
    differences = [hex(i) for i in native if parent[i] != candidate[i]]
    assert not differences, (label, differences[:15])
    for name in ('rawtags', 'chr_latches', 'vram', 'ppuctrl'):
        assert getattr(parent, name) == getattr(candidate, name), (label, name)
    expected = {
        2: [(0x1FE0, Epoch.HEADER, header)],
        3: [(at, old, new) for at, (_, old, new) in zip((0, Epoch.STAMP_CODE - 0xA000), edits[-2:], strict=True)]
        + [(0x1FE0, Epoch.HEADER, header)],
    }
    for index, (old, new) in enumerate(zip(parent.ram, candidate.ram, strict=True)):
        normalized = bytearray(new)
        for address, before, after in expected.get(index, ()):
            span = slice(address, address + len(before))
            assert old[span] == before and new[span] == after, (label, index, hex(address))
            normalized[span] = before
        if index == 2:
            address = Epoch.STAMP - 0xC000
            assert old[address] == 0
            normalized[address] = 0
        if old != normalized:
            differences = [hex(i) for i, pair in enumerate(zip(old, normalized, strict=True)) if pair[0] != pair[1]]
            raise AssertionError((label, index, differences[:15]))


def play(images):
    edits = Epoch.static_edits(images[0])
    header = Epoch.Bub.cookie(images[1])
    phases = (('idle', 0, 24), ('walk', 1, 24), ('back', 2, 12), ('jump', 0x81, 12),
              ('attack', 0x41, 30), ('settle', 0, 15))
    for name in SLOTS:
        with patch.dict(Roster.ROSTER, SLOTS):
            machines = [Roster.start(image, W.Symbols.bundle(), name) for image in images]
        compare(*machines, ('start', name), edits, header)
        report = {}
        for phase, pad, length in phases:
            totals = [0, 0]
            calls = [Counter(), Counter()]
            for _ in range(length):
                for i, m in enumerate(machines):
                    trace = Trace(bool(i))
                    totals[i] += B.main_step(m, pad, trace)[0]
                    calls[i].update(trace.count)
                compare(*machines, (name, phase), edits, header)
            assert calls[0]['full_movement'] == calls[1]['full_movement'] == calls[1]['stamp']
            report[phase] = dict(updates=length, saved_per_update=(totals[0] - totals[1]) / length,
                                 checks=list(map(dict, calls)))
        print(name, json.dumps(report, separators=(',', ':')), flush=True)


def foreign(images):
    for name in Shared.OWNER_CASES:
        models = [Shared.enter(rom, name) for rom in images]
        for pad in [0] * 80 + [1] * 12 + [0x81] + [1] * 6:
            for model in models:
                B.main_step(model, pad, Shared.Visits())
            Shared.compare(*models, name)
        print(name, '99 paired updates matched', flush=True)


def gates(images):
    from probe_prince_wram1_funding_1123 import call

    marker = Epoch.STAMP - 0xC000
    with patch.dict(Roster.ROSTER, SLOTS):
        old, new = [Roster.start(image, W.Symbols.bundle(), 'BUB') for image in images]
    new.raw_page(1, 213)
    new[0x5FFF] = 1
    new[0x1F9], new[0x1FA] = 0x52, 0x83
    new[0x0E], new.ram[2][marker] = 42, 42
    N.put(new, GameEngineSubroutine=8, GamePauseStatus=0, TimerControl=0)
    cases = {
        'matching': (),
        'not_foreground': ((None, 0x5FFF, 0),),
        'different_return_low': ((None, 0x1F9, 0),),
        'different_return_high': ((None, 0x1FA, 0),),
        'transition': ((None, 0x0F, 7),),
        'paused': ((None, 0x0777, 1),),
        'timer_held': ((None, 0x074A, 1),),
        'stale': ((2, marker, 41),),
        'wrapped': ((None, 0x0E, 0), (2, marker, 0)),
        'state_prefix': ((2, 0x1FE0, 0),),
        'state_owner': ((2, 0x1FE1, 38),),
        'code_prefix': ((3, 0x1FE0, 0),),
        'code_owner': ((3, 0x1FE1, 38),),
    }
    for name, changes in cases.items():
        m = N.fork(new)
        for bank, address, value in changes:
            if bank is None:
                m[address] = value
            else:
                m.ram[bank][address] = value
        mapped = tuple(m.rawtags)
        result = call(m, 0xB0B0)
        assert bool(result['regs'][3] & 1) == (name == 'matching'), name
        assert tuple(m.rawtags) == mapped, name

    for bank, byte in product((2, 3), range(16)):
        for base in (old, new):
            m = N.fork(base)
            m.raw_page(1, 193)
            m.ram[bank][0x1FE0 + byte] ^= 0x80
            assert not call(m, 0xAEE2)['regs'][3] & 1, (bank, byte)
    print(f'{len(cases)} foreground gate cases and 64 full-header rejection checks passed', flush=True)


def interrupts(images):
    from check_karnov_foreground_cookie_1123 import matched_interrupts

    edits, header = Epoch.static_edits(images[0]), Epoch.Bub.cookie(images[1])
    with patch.dict(Roster.ROSTER, SLOTS):
        old, new = [Roster.start(image, W.Symbols.bundle(), 'BOB') for image in images]
    snapshots, cuts = {}, {}
    B.main_step(old, 0, Trace(False, snapshots=snapshots))
    B.main_step(new, 0, Trace(True, cuts=cuts))
    compare(old, new, 'interrupt baseline', edits, header)
    results = matched_interrupts(snapshots, cuts, lambda a, b, label: compare(a, b, label, edits, header))
    print('Interrupt returns ' + json.dumps(results, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    parent = Epoch.Bub.ROM.read_bytes()
    candidate = Epoch.compose(parent)
    assert Epoch.inverse(candidate) == parent
    print('Candidate', sha256(candidate).hexdigest(), flush=True)
    play((parent, candidate))
    gates((parent, candidate))
    interrupts((parent, candidate))
    foreign((parent, candidate))

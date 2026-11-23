"""Compare the guarded side route with Karnov's installed callbacks."""

from collections import Counter
from itertools import product
import json

import check_karnov_foreground_cookie_1123 as Shared
import compose_karnov_native_side_1123 as Trial
from profile_dkjr_empty_current_1123 import Old


CPU, B = Shared.CPU, Shared.B
ROOT = (254, 0x90E4)


def point(c):
    return Shared.Roster.Profile.point(c.memory, c.pc)


def return_to(c):
    m = c.memory
    low = m[0x100 + ((c.sp + 1) & 255)]
    high = m[0x100 + ((c.sp + 2) & 255)]
    return ((1 + low + 256 * high) & 65535, (c.sp + 2) & 255)


class Visits:
    def __init__(self, symbols, entries=None, cuts=None, phase=None):
        self.symbols = symbols
        self.entries, self.cuts = entries, cuts
        self.phase = phase
        self.count = Counter()

    def run(self, c, stop):
        active = None

        def visit(cpu):
            nonlocal active
            bank, pc = point(cpu)
            if (bank, pc) == ROOT:
                active = self.phase, cpu.y
                if self.entries is not None and active not in self.entries:
                    entry = CPU.clone(cpu)
                    entry.memory.combined_terminal = stop
                    self.entries[active] = entry
            if bank == 128 + Trial.BANK:
                if pc == self.symbols['InBounds']:
                    self.count['native'] += 1
                if pc == self.symbols['Reject']:
                    self.count['fallback'] += 1
                if self.cuts is not None and active is not None and (pc, active) not in self.cuts:
                    cut = CPU.clone(cpu)
                    cut.memory.combined_terminal = stop
                    self.cuts[pc, active] = cut

        CPU.run(c, lambda cpu: (cpu.pc, cpu.sp) == stop, visit)


def returned_pair(old, new, label):
    assert CPU.registers(old) == CPU.registers(new), (label, CPU.registers(old), CPU.registers(new))
    assert CPU.live_stack(old) == CPU.live_stack(new), label
    Shared.Compare.compare(old.memory, new.memory, label)


def side_case(entries, symbols, y, *, x=254, page=1, height=176, crouch=0, fault=None):
    run = Visits(symbols)
    old, new = (CPU.clone(entry[y if y in entry else 33]) for entry in entries)
    for c in (old, new):
        m = c.memory
        c.y = y
        Shared.N.put(m, Player_X_Position=x, Player_PageLoc=page,
                     Player_Y_Position=height, CrouchingFlag=crouch)
        if fault:
            fault(m)
    for c, trace in ((old, CPU), (new, run)):
        end = return_to(c)
        if trace is CPU:
            CPU.run(c, lambda cpu: (cpu.pc, cpu.sp) == end)
        else:
            trace.run(c, end)
    returned_pair(old, new, (y, x, page, height, crouch))
    return run.count


def probes(entries, symbols):
    tally = Counter()
    for y, x, page, height, crouch in product(
        (33, 34, 35, 36), (0, 241, 255), (0, 1), (0, 8, 20, 32, 128, 176, 224, 240, 255), (0, 1)
    ):
        tally.update(side_case(entries, symbols, y, x=x, page=page, height=height, crouch=crouch))
    faults = {
        'zero stamp': lambda m: m.ram[2].__setitem__(Shared.STAMP, 0),
        'expired stamp': lambda m: m.ram[2].__setitem__(Shared.STAMP, m[0x0E] ^ 255),
        'timer wrap': lambda m: m.__setitem__(0x0E, 0),
        'outside Main': lambda m: m.__setitem__(0x1F9, 0),
    }
    for label, fault in faults.items():
        assert side_case(entries, symbols, 33, fault=fault) == {'fallback': 1}, label
    for bank, byte in product((2, 3), range(16)):
        def corrupt(m):
            m.ram[2][Shared.STAMP] = 0
            m.ram[bank][0x1FE0 + byte] ^= 0x80

        assert side_case(entries, symbols, 33, fault=corrupt) == {'fallback': 1}
    for bank, byte in product((2, 3), range(4)):
        def corrupt_prefix(m):
            m.ram[bank][0x1FE0 + byte] ^= 0x80

        assert side_case(entries, symbols, 33, fault=corrupt_prefix) == {'fallback': 1}
    for y in (0, 30, 32, 37, 47, 255):
        assert side_case(entries, symbols, y) == {'fallback': 1}
    assert tally['native'] and tally['fallback']
    return dict(tally, directed_fallback=50)


def recorded_audio_reads(model, parent, candidate):
    """Observe overlap with the retained source campaigns and exact host map."""
    path = Trial.SOURCE.parents[2] / 'docs/qa/rogue-dawn-audio-campaigns-2026-10-28.json'
    receipt = json.loads(path.read_text(encoding='utf-8-sig'))
    assert receipt['passed']
    rows = {q['bank']: q['ranges'] for q in receipt['observed_ROM']}
    lower = (52, 48, 53, 54, 50, 51)
    overlaps = []
    observed_pages = []
    for stem, count in (('RdaLower', 192), ('RdaUpperRaw', 32)):
        banks, highs = (Shared.W.location(model.bundle, stem + suffix) for suffix in ('BankTable', 'HighTable'))
        for i in range(count):
            if parent[banks + i] != 0x80 | Trial.BANK:
                continue
            high = parent[highs + i]
            at = Trial.Side.at(Trial.BANK, high * 256)
            changed = [j for j in range(256) if parent[at + j] != candidate[at + j]]
            if not changed:
                continue
            orig = lower[i // 32] if stem == 'RdaLower' else 49
            page = i % 32
            observed_pages.append(dict(source_bank=orig, source_page=page, program_page=hex(high), cells=len(changed)))
            overlaps.extend([orig, page * 256 + j] for j in changed if any(
                span['start'] <= page * 256 + j < span['end_exclusive'] for span in rows[orig]
            ))
    assert observed_pages
    return dict(campaigns=len(receipt['campaigns']), updates=receipt['total_updates'],
                mapped_pages=observed_pages, overlap=overlaps)


def main():
    parent = Old.ROM.read_bytes()
    candidate = Trial.compose(parent)
    symbols = Trial.program()['symbols']
    old, new = (Shared.start(image, 'KARNOV') for image in (parent, candidate))
    entries, alternatives, cuts = {}, {}, {}
    totals, visits, differences = Counter(), Counter(), Counter()
    for phase, pads in (
        ('idle', (0,) * 24), ('right', (1,) * 24), ('crouch_fire', (68, 4) * 12),
        ('jump_land', (129,) + (1,) * 47), ('left', (2,) * 12),
    ):
        for i, pad in enumerate(pads):
            record = phase in ('idle', 'crouch_fire', 'jump_land') and i == 0
            control = Visits(symbols, entries if record else None, phase=phase)
            route = Visits(symbols, alternatives if record else None, cuts if record else None, phase=phase)
            left = B.main_step(old, pad, control)
            right = B.main_step(new, pad, route)
            assert left[1] == right[1]
            Shared.Compare.compare(old, new, (phase, i))
            visits.update(route.count)
            totals[phase] += 1
            differences[phase] += left[0] - right[0]
    assert totals and visits['native']
    idle = ({y: c for (phase, y), c in samples.items() if phase == 'idle'}
            for samples in (entries, alternatives))
    report = dict(candidate=Trial.sha256(candidate).hexdigest(), phases=dict(totals),
                  savings_per_update={k: differences[k] / v for k, v in totals.items()},
                  visits=dict(visits), probes=probes(tuple(idle), symbols),
                  recorded_audio_reads=recorded_audio_reads(old, parent, candidate),
                  interrupts=Shared.matched_interrupts(entries, cuts, Shared.Compare.compare), outputs=0)
    print(json.dumps(report, separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()

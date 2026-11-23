"""Exact6201 DK Jr. empty opening CPU profile; stdout, zero retained outputs.

Reuses the established compiled native menu and actual serial controller plus
normal-NMI scheduler.  Instruction cycles are not physical video cadence.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

import profile_dkjr_shared_dispatch_1123 as Old

W, N, Opening = Old.W, Old.N, Old.Opening
PIN = '6201e3b6680659fc1b1fab4e09125f9dc05e3b9e2b9a9beebcb656ef1bc2f36f'


def point(m, pc):
    return (m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1, pc)


class Trace:
    def __init__(self, m):
        self.m = m
        self.cycles, self.instructions = Counter(), Counter()
        self.calls, self.counts = Counter(), Counter()
        self.entries = Counter()
        self.labels = defaultdict(dict)
        self.epoch_rows = []
        for name, symbol in m.bundle['syms'].items():
            if 'seg' not in symbol or '::' in name:
                continue
            try:
                at, offset = W.address(m.bundle, name), W.location(m.bundle, name)
            except (KeyError, ValueError):
                continue
            if at >= 0x8000 and offset >= 16:
                self.labels[(offset-16)//8192 | 128].setdefault(at, name)

    def name(self, q):
        tag, pc = q
        available = [a for a in self.labels[tag] if a <= pc]
        if tag in (2, 3):
            return f'RAM{tag}:{pc:04X}'
        if not available:
            return f'{tag}:{pc:04X}'
        at = max(available)
        return f'{tag}:{pc:04X} {self.labels[tag][at]}+{pc-at:X}'

    def run(self, c, stop):
        pending = []
        m = self.m
        common = W.address(m.bundle, 'FarCallCommon')
        prior = None
        for _ in range(300000):
            state = c.pc, c.sp
            for i in range(len(pending)-1, -1, -1):
                goal, key, start = pending[i]
                if state == goal:
                    self.calls[key] += c.processorCycles-start
                    self.counts[key] += 1
                    del pending[i]
            if state == stop:
                assert not pending, pending
                return
            here = point(m, c.pc)
            if c.pc == common:
                destination = m[0x16c] + 256*m[0x16d]
                target = (c.a, destination) if 0xa000 <= destination < 0xe000 else point(m, destination)
                ret = m[0x100+((c.sp+1)&255)] + 256*m[0x100+((c.sp+2)&255)] + 1
                pending.append((((ret&65535), (c.sp+2)&255), (prior, target), c.processorCycles))
            if here in ((193, 0xaf27), (213, 0xa8dc), (161, 0xbfb5)):
                self.entries[f'{here[0]}:{here[1]:04X}'] += 1
            before = c.processorCycles
            assert m[c.pc], ('Actual CPU BRK', here)
            c.step()
            self.cycles[here] += c.processorCycles-before
            self.instructions[here] += 1
            prior = here
        raise AssertionError(('Actual CPU Main bound', point(m, c.pc)))

    def summary(self, rows):
        n = len(rows)
        banks, regions = Counter(), Counter()
        for (tag, pc), cycles in self.cycles.items():
            banks[tag] += cycles
            regions[tag, pc&0xffc0] += cycles
        assert sum(row['main_cycles'] for row in rows) == sum(self.cycles.values())
        return dict(updates=n, first=rows[0], last=rows[-1],
            mean_main_cycles=sum(self.cycles.values())/n,
            mean_logical_NMI_cycles=sum(row['NMI_cycles'] for row in rows)/n,
            auth_entries_per_Main={k:v/n for k,v in self.entries.items()},
            mapped_banks=[dict(tag=k, cycles_per_Main=v/n) for k,v in banks.most_common()],
            hot_regions=[dict(at=self.name(k), cycles_per_Main=v/n) for k,v in regions.most_common(30)],
            hot_instructions=[dict(at=self.name(k), cycles_per_Main=v/n,
                executions_per_Main=self.instructions[k]/n) for k,v in self.cycles.most_common(30)],
            hot_FarCallCommon=[dict(caller=self.name(k[0]), target=self.name(k[1]),
                inclusive_cycles_per_Main=v/n, calls_per_Main=self.counts[k]/n)
                for k,v in self.calls.most_common(22)])


def profile(raw, count=16, emit=True):
    assert sha256(raw).hexdigest() == PIN
    m = Old.boot(raw)
    result = {}
    for phase, pad in (('standing', 0), ('walking', 1)):
        trace, rows = Trace(m), []
        for i in range(count):
            x0 = Opening.position(m)
            assert not any(Opening.flags(m))
            main, nmi = Opening.main_step(m, pad, trace)
            assert not any(Opening.flags(m)) and N.get(m, 'NumberofLives') == 2
            assert (N.get(m, 'SelectedCharacter'), N.get(m, 'GameEngineSubroutine')) == (40, 8)
            rows.append(dict(update=i, x_before=x0, x_after=Opening.position(m),
                y=N.get(m, 'Player_Y_Position'), original_state=m.ram[2][0x6b],
                main_cycles=main, NMI_cycles=nmi))
        result[phase] = trace.summary(rows)
        if emit:
            print('DK CURRENT PROFILE '+json.dumps(dict(phase=phase, **result[phase]), separators=(',', ':')), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--count', type=int, default=16)
    ap.add_argument('--compact', action='store_true')
    args = ap.parse_args()
    assert 4 <= args.count <= 32
    raw = Old.ROM.read_bytes()
    result = dict(passed=True, ROM_SHA256=PIN, source_SHA256=sha256(Path(__file__).read_bytes()).hexdigest(),
        source_CPU_only=True, Mesen_run=False, normal_logical_NMI=True,
        DMA_stalls_modelled=False, physical_cadence_qualified=False,
        retained_outputs=0, phases=profile(raw, args.count, not args.compact))
    if args.compact:
        for row in result['phases'].values():
            row['hot_instructions'] = row['hot_instructions'][:8]
            row['hot_regions'] = row['hot_regions'][:14]
            row['hot_FarCallCommon'] = row['hot_FarCallCommon'][:15]
    canonical = json.dumps(result, sort_keys=True, separators=(',', ':'))
    print('DK CURRENT RECEIPT '+json.dumps(dict(result=result, receipt_SHA256=sha256(canonical.encode()).hexdigest()),
        separators=(',', ':')), flush=True)


if __name__ == '__main__':
    main()

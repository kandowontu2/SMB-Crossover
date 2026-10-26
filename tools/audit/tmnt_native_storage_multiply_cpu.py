"""Actual linked multiply ABI/domain and complete original-song CPU comparison."""
from pathlib import Path
import argparse
import gzip
import json
from collections import Counter
from check_tmnt_render_oa import load, address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT, OB, ORIGINAL, sha
from tmnt_native_storage_cpu import Probe
from tmnt_native_storage_multiply import MathMemory
import tmnt_native_storage_linked_cpu as previous


class Linked(previous.Linked):
    def __init__(self, rom, swap):
        previous.Memory = MathMemory
        super().__init__(rom, swap)
        self.allowed.update([0x5205, 0x5206])
        self.math_calls = 0
        self.helper = address(self.b, 'TnFastProduct') if 'TnFastProduct' in self.b['syms'] else None
        self.helper_end = self.helper + int(self.b['syms']['TnFastProduct']['size'], 0) if self.helper else None

    def call(self, row, song):
        c, m = self.c, self.m
        c.sp = 253;m[510], m[511] = 255, 1
        if row['call'] == -1: c.a, c.x, c.y, c.pc = song - 1, 0, 0, address(self.b, 'TnNativeInit')
        else: c.pc = address(self.b, 'TnNativePlay')
        m.writes = [];m.math_events = []
        start, source, pending, minimum = c.processorCycles, [], [], 255
        for _ in range(50000):
            if c.pc == 512: break
            minimum = min(minimum, c.sp)
            if pending and c.pc == pending[-1][0]:
                ret, before = pending.pop()
                assert (c.a, c.x, c.y, c.p & 207, c.sp) == before, ('Source writer ABI', song, row['call'], hex(ret))
                self.writers += 1
            if c.pc in self.sites and m.banks[(c.pc - 0x8000) // 8192] == 63:
                site = self.sites[c.pc]
                index = c.x if site['mode'] == 'abx' else c.y if site['mode'] == 'aby' else 0
                source.append([site['address'] + index, c.a])
                pending.append((c.pc + 3, (c.a, c.x, c.y, c.p & 207, c.sp)))
            m.executing_PC = c.pc
            c.step()
        else: raise AssertionError(('Linked source timeout', song, row['call'], hex(c.pc)))
        assert not pending and c.sp == 255 and source == row['writes'], ('Original source order', song, row['call'])
        assert all(at in self.allowed for at, value in m.writes if at < 0x8000 and not 0x4000 <= at <= 0x4017)
        assert all(m[i] == self.saved_zp[i] for i in range(256) if not self.zp <= i < self.zp + 14)
        assert not [(at, value) for at, value in m.writes if 0x2000 <= at < 0x4000 or 0x5000 <= at < 0x6000 and at not in [0x5205, 0x5206]]
        assert len(m.math_events) % 4 == 0
        for index in range(0, len(m.math_events), 4):
            group = m.math_events[index:index + 4]
            assert [(q[0], q[1]) for q in group] == [('W', 0x5205), ('W', 0x5206), ('R', 0x5205), ('R', 0x5206)]
            assert all(self.helper <= q[3] < self.helper_end for q in group), group
            assert 2 <= group[0][2] <= 15
            product = group[0][2] * group[1][2]
            assert [group[2][2], group[3][2]] == [product & 255, product >> 8]
            self.math_calls += 1
        assert m.banks == [126, 63, 99 if self.swap else 124, 127]
        self.depth = min(self.depth or 255, minimum)
        self.HW.extend((at, value) for at, value in m.writes if 0x4000 <= at <= 0x4017)
        return c.processorCycles - start


def domain(a):
    bundles = [load(a.baseline), load(a.candidate)]
    machines = []
    for b in bundles:
        m = MathMemory(b);m.page(1, 63);m.page(2, 99)
        machines.append((b, NesMPU(memory=m), m))
    flags = [value for value in range(256) if value & 0x30 == 0x20]
    costs = {n: set() for n in range(16)}
    count, helper = 0, address(bundles[1], 'TnFastProduct')
    for n in range(16):
        for coefficient in range(256):
            for x in range(6):
                for p in flags:
                    outputs, cycles = [], []
                    for b, c, m in machines:
                        zp, ram = address(b, 'TnAudioZp'), address(b, 'TnAudioRam')
                        c.pc, c.a, c.x, c.y, c.p, c.sp = 0xacbd, n, x, 7, p, 253
                        m[510], m[511] = 255, 1
                        m[ram + 4 + x] = coefficient
                        m[zp + 2], m[zp + 4], m[zp + 5] = 37, 83, 149
                        m.operands = [37, 149];m.math_events = [];m.writes = []
                        start = c.processorCycles
                        for _ in range(300):
                            if c.pc == 512: break
                            m.executing_PC = c.pc;c.step()
                        else: raise AssertionError(('Multiply timeout', n, coefficient, x, p))
                        assert set(at for at, value in m.writes) <= {zp + 2, zp + 4, zp + 5, 0x5205, 0x5206}
                        outputs.append((c.a, c.x, c.y, c.p & 207, c.sp, m[zp + 2], m[zp + 4], m[zp + 5]))
                        cycles.append(c.processorCycles - start)
                    assert outputs[0] == outputs[1], ('Multiply full ABI/RAM', n, coefficient, x, p, outputs)
                    new = machines[1][2]
                    assert len(new.math_events) == (4 if n >= 2 else 0)
                    assert not machines[0][2].math_events
                    if n >= 2:
                        assert [(q[0], q[1]) for q in new.math_events] == [('W', 0x5205), ('W', 0x5206), ('R', 0x5205), ('R', 0x5206)]
                        assert new.operands == [n, coefficient]
                        assert all(helper <= q[3] < helper + 75 for q in new.math_events)
                    else: assert new.operands == [37, 149]
                    costs[n].add(cycles[1] - cycles[0]);count += 1
        print('DOMAIN', n, sorted(costs[n]), count, flush=True)
    assert max(max(value) for value in costs.values()) <= 0
    proof = dict(passed=True, source_only=True, native_run=False, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 cases=count, multiplier_nibble_inputs=list(range(16)), coefficient_inputs=[0, 255], all_meaningful_P=flags,
                 actual_X_inputs=list(range(6)), upper_A_bits_discarded_by_identical_AND15=True,
                 exact_full_AXYP_SP_E2_E4_E5_and_owned_writes=True, exact_MMC5_order_product_and_owner=True,
                 no_zero_one_hardware_access=True, CPU_cycle_deltas_by_n={str(k): sorted(v) for k, v in costs.items()},
                 no_input_domain_cycle_regression=True, checker_sha256=sha(Path(__file__)))
    return proof


def songs(a):
    coverage = json.loads((OB / 'probe-v2/coverage.json').read_text())
    results, calls, stores, writers, hardware_calls = [], 0, 0, 0, 0
    for song, metadata in coverage['songs'].items():
        capture = OB / f'probe-v2/song-{int(song):02d}.json.gz'
        assert sha(capture) == metadata['capture_sha256']
        gold = json.loads(gzip.decompress(capture.read_bytes()))
        original, parent, child = Probe(a.raw_original, True), Linked(a.baseline, True), Linked(a.candidate, True)
        costs = [[], [], []]
        for row in gold:
            for i, runner in enumerate([original, parent, child]): costs[i].append(runner.call(row, int(song)))
            assert original.registers() == parent.registers() == child.registers(), ('Literal public source ABI', song, row['call'])
            positions = list(range(0xe0, 0xee)) + list(range(0x7000, 0x70ae))
            expected = bytes((original.m[at] - (27 if original.origin.get(at) in original.changed_high else 0)) & 255 for at in positions)
            assert parent.state() == child.state() == expected, ('Exact full source state/provenance', song, row['call'])
            assert costs[2][-1] <= costs[1][-1], ('New source update regression', song, row['call'], costs[1][-1], costs[2][-1])
            calls += 1;stores += len(row['writes'])
        row = dict(song=int(song), calls=len(gold), requests=sum(len(row['writes']) for row in gold),
                   original_cycles=sum(costs[0]), parent_cycles=sum(costs[1]), candidate_cycles=sum(costs[2]),
                   parent_peak=max(costs[1][1:]), candidate_peak=max(costs[2][1:]),
                   parent_mean_play=sum(costs[1][1:]) / 12000, candidate_mean_play=sum(costs[2][1:]) / 12000,
                   minimum_stack_pointer=min(parent.depth, child.depth), hardware_multiply_calls=child.math_calls)
        results.append(row);writers += parent.writers + child.writers;hardware_calls += child.math_calls
        print('SONG', row, flush=True)
        (a.output / 'progress.json').write_text(json.dumps(results, indent=2) + '\n')
    return dict(passed=True, source_only=True, native_run=False, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                original_NSF_sha256=ORIGINAL, original_calls=calls, original_ordered_APU_requests=stores,
                checked_writer_returns=writers, hardware_multiply_calls=hardware_calls,
                all_source_AXYP_SP_188byte_state_foreground_SMC_ZP_banks_exact=True,
                only_exact_helper_owned_product_register_accesses=True, every_call_CPU_no_worse=True,
                songs=results, checker_sha256=sha(Path(__file__)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--test', choices=['domain', 'songs'], required=True)
    p.add_argument('--raw-original', type=Path)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    proof = domain(a) if a.test == 'domain' else songs(a)
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: v for k, v in proof.items() if k in ['passed', 'cases', 'original_calls', 'original_ordered_APU_requests', 'checked_writer_returns', 'candidate_ROM_sha256']}))


if __name__ == '__main__':
    main()

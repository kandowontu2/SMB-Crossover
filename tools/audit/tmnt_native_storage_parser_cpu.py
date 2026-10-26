"""Exact compiled parser domains plus unchanged all-song source goldens."""
from pathlib import Path
import argparse
import itertools
import json
from collections import Counter
from check_tmnt_render_oa import load, address
from verify_native_relocation import NesMPU
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_multiply_cpu import songs


FLAGS = [value for value in range(256) if value & 0x30 == 0x20]


def domains(a):
    machines = []
    for path in [a.baseline, a.candidate]:
        b = load(path);m = MathMemory(b);m.page(1, 63);m.page(2, 99)
        c = NesMPU(memory=m)
        machines.append((b, c, m, address(b, 'TnAudioZp'), address(b, 'TnAudioRam')))

    def one(entry, stops, accumulator, x, y, flags, setup, allowed):
        outcomes, costs = [], []
        for b, c, m, zp, ram in machines:
            setup(m, zp, ram)
            c.pc, c.a, c.x, c.y, c.p, c.sp = entry, accumulator, x, y, flags, 253
            m.math_events = [];m.writes = [];start = c.processorCycles
            for _ in range(1600):
                if c.pc in stops: break
                m.executing_PC = c.pc;c.step()
            else: raise AssertionError(('Parser component timeout', hex(entry), accumulator, x, y, flags))
            assert not m.math_events
            assert set(at for at, value in m.writes) <= {zp + delta for delta in allowed}
            outcomes.append((c.pc, c.a, c.x, c.y, c.p & 207, c.sp, tuple(m[zp:zp + 14]), list(m.writes), list(m.banks)))
            costs.append(c.processorCycles - start)
        assert outcomes[0] == outcomes[1], ('Parser component ABI/state', hex(entry), accumulator, x, y, flags, outcomes)
        assert costs[1] <= costs[0], ('Parser component cost', hex(entry), accumulator, x, y, flags, costs)
        return costs[1] - costs[0]

    rows = []
    # Complete triangle coefficient0..255/note0..15/all64 incomingP. Its
    # original zero and single-term paths preserve incoming overflow.
    costs, count = Counter(), 0
    for coefficient, note, flags in itertools.product(range(256), range(16), FLAGS):
        def setup(m, zp, ram):
            m[zp], m[zp + 1] = 0, 96;m[0x6007] = note
            m[ram + 0x54] = coefficient
            m[zp + 2], m[zp + 3] = 37, 149
        delta = one(0xaab7, {0xaadd}, 83, 2, 7, flags, setup, {2})
        costs[delta] += 1;count += 1
    rows.append(dict(component='triangle AAB7..AADD', cases=count, all256coefficients_all16notes_all64P=True,
                     exact_original_last_ADC_flags_and_first_overflow_X=True, cycle_deltas=dict(costs)))
    print(rows[-1], flush=True)
    # SEC plus the first SBC kill every incoming C/N/Z/V. All operand pairs
    # cross all D/I combinations; representative operands cross all64P too.
    costs, count = Counter(), 0
    pairs = itertools.chain(itertools.product(range(256), range(1, 256), [0x20, 0x24, 0x28, 0x2c]),
                            itertools.product([0, 1, 15, 127, 128, 254, 255], [1, 2, 15, 127, 128, 255], FLAGS),
                            itertools.product([0], [0], FLAGS))
    for accumulator, divisor, flags in pairs:
        def setup(m, zp, ram): m[zp + 2] = divisor
        delta = one(0xa6a0, {0xa6a7, 0xa6e3}, accumulator, 3, 7, flags, setup, set())
        costs[delta] += 1;count += 1
    rows.append(dict(component='remainder A6A0 back edge', cases=count, every_terminating_byte_operand_pair=True,
                     initial_SEC_then_SBC_dead_incoming_CNZV=True, all_DI_combinations_and_full64P_controls=True,
                     original_positive_A_zero_divisor_nontermination_not_claimed_as_terminating=True, cycle_deltas=dict(costs)))
    print(rows[-1], flush=True)
    # Every high-nibble input reaches the same exact original handler vector.
    # The subsequent AND15 discards stream high bits independently.
    costs, count = Counter(), 0
    raw = a.baseline.read_bytes();off = 16 + 63 * 8192
    vectors = raw[off + 0xfc4:off + 0xfcc]
    stops = {vectors[i] + 256 * vectors[i + 1] for i in range(0, 8, 2)}
    for accumulator, note, channel, flags in itertools.product(range(256), [0, 1, 15, 128, 255], [0, 2, 5], FLAGS):
        def setup(m, zp, ram):
            m[zp], m[zp + 1] = 0, 96;m[0x60ff] = note
            m[ram + 0x92] = channel
            m[zp + 2], m[zp + 3] = 37, 149
        delta = one(0xa937, stops, accumulator, 4, 255, flags, setup, {2, 3})
        costs[delta] += 1;count += 1
    assert set(costs) == {-4}
    rows.append(dict(component='command dispatch A937..original vector', cases=count,
                     all256incomingA_all64P=True, exact_E2_E3_handler_target_streamA_XY_and_flags=True,
                     cycle_deltas=dict(costs)))
    print(rows[-1], flush=True)
    return dict(passed=True, source_only=True, native_run=False, baseline_ROM_sha256=sha(a.baseline),
                candidate_ROM_sha256=sha(a.candidate), cases=sum(row['cases'] for row in rows), rows=rows,
                no_new_RAM_or_hardware_accesses=True, each_terminating_case_no_worse=True,
                checker_sha256=sha(Path(__file__)))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']: p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--test', choices=['domains', 'songs'], required=True)
    p.add_argument('--raw-original', type=Path)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    proof = domains(a) if a.test == 'domains' else songs(a)
    if a.test == 'songs':
        proof['unchanged_complete_original_checker_sha256'] = proof.pop('checker_sha256')
        proof['checker_sha256'] = sha(Path(__file__))
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({key: proof[key] for key in ['passed', 'cases', 'original_calls', 'original_ordered_APU_requests'] if key in proof}))


if __name__ == '__main__':
    main()

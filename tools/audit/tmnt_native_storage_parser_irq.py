"""Real compiled IRQ at parser loops/vector-dispatch instruction boundaries."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load, address
from verify_native_relocation import NesMPU
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_irq_cpu import ordinary, registers
from tmnt_native_storage_driver import ROOT, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    b = load(a.candidate)
    raw = a.candidate.read_bytes();off = 16 + 63 * 8192
    data = raw[off + 0xfc4:off + 0xfcc]
    vectors = {data[i] + 256 * data[i + 1] for i in range(0, 8, 2)}
    cases = []
    for coefficient, note, flags in itertools.product([0, 1, 0x20, 0x7f, 0x80, 0xff], [0, 8, 15], [0x20, 0x60]):
        cases.append(('triangle', coefficient, note, flags))
    for accumulator, divisor, flags in itertools.product([0, 128, 255], [1, 15, 128], [0x20, 0x60]):
        cases.append(('remainder', accumulator, divisor, flags))
    for value, note, flags in itertools.product([0, 0x10, 0x20, 0x30], [0, 255], [0x20, 0x60]):
        cases.append(('dispatch', value, note, flags))

    def setup(case):
        name, first, second, flags = case
        m = MathMemory(b);m.page(1, 63);m.page(2, 99)
        zp, ram = address(b, 'TnAudioZp'), address(b, 'TnAudioRam')
        for key, value in dict(SelectedCharacter=19, OperMode=1, CurrentBank=191, CurrentBankC=227).items(): m[address(b, key)] = value
        m[0x5204] = 128
        m[zp], m[zp + 1] = 0, 96;m[0x60ff] = second
        m[zp + 2], m[zp + 3] = 37, 149
        m[ram + 0x92] = 5
        c = NesMPU(memory=m)
        c.a, c.x, c.y, c.p, c.sp = first, 2, 255, flags, 253
        if name == 'triangle': c.pc = 0xaab7;m[ram + 0x54] = first;stops = {0xaadd}
        elif name == 'remainder': c.pc = 0xa6a0;m[zp + 2] = second;stops = {0xa6a7, 0xa6e3}
        else: c.pc = 0xa937;stops = vectors
        m.writes = [];m.math_events = []
        return c, m, stops

    def outcome(c, m): return registers(c), ordinary(m), list(m.banks), list(m.operands), list(m.math_events)

    count, maximum, rows = 0, 0, []
    for case in cases:
        c, m, stops = setup(case);trace = []
        for index in range(1600):
            if c.pc in stops: break
            trace.append(index);m.executing_PC = c.pc;c.step()
        else: raise AssertionError(('Uninterrupted parser timeout', case))
        expected = outcome(c, m)
        for at in trace:
            d, q, stops = setup(case);injected = False
            for index in range(1600):
                if d.pc in stops: break
                if index == at:
                    before = outcome(d, q)
                    assert not d.p & 4
                    start = len(q.writes);d.irq();assert d.pc == 0x8000;minimum = d.sp
                    for _ in range(300):
                        if d.pc == before[0][0] and d.sp == before[0][-1]: break
                        minimum = min(minimum, d.sp);q.executing_PC = d.pc;d.step()
                    else: raise AssertionError(('Actual IRQ failed return', case, at))
                    assert outcome(d, q) == before
                    stores = [(address_, value) for address_, value in q.writes[start:] if 0x2000 <= address_ < 0x6000]
                    assert stores and all(address_ in [0x2005, 0x2006, 0x5128, 0x5130] for address_, value in stores)
                    maximum = max(maximum, 255 - minimum);injected = True
                q.executing_PC = d.pc;d.step()
            else: raise AssertionError(('Interrupted parser timeout', case, at))
            assert injected and outcome(d, q) == expected
            count += 1
        rows.append(dict(component=case[0], input1=case[1], input2=case[2], flags=case[3], actual_IRQ_instruction_boundaries=len(trace)))
    proof = dict(passed=True, source_only=True, native_run=False, candidate_ROM_sha256=sha(a.candidate),
                 real_compiled_IRQ_injections=count, actual_vector=0x8000, maximum_total_stack_depth=maximum,
                 intermediate_AXYP_SP_PC_RAM_SMC_banks_math_exact=True,
                 final_source_component_state_exact=True, no_nested_NMI_domain_claim=True,
                 cases=rows, checker_sha256=sha(Path(__file__)),
                 limits='Actual compiled vector/IRQ/RTI, instruction-boundary injection only. No native timing, DMC DMA, PPU/OAM or nested-NMI result.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({key: proof[key] for key in ['passed', 'real_compiled_IRQ_injections', 'maximum_total_stack_depth']}))


if __name__ == '__main__':
    main()

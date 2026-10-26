"""Actual compiled IRQ at every multiply-helper/tail instruction boundary."""
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
    helper = address(b, 'TnFastProduct')
    count, maximum, rows = 0, 0, []
    for n, coefficient, x, flags in itertools.product([0, 1, 2, 10, 15], [0, 7, 255], [0, 3], [0x20, 0x60]):
        def setup():
            m = MathMemory(b);m.page(1, 63);m.page(2, 99)
            for key, value in dict(SelectedCharacter=19, OperMode=1, CurrentBank=191, CurrentBankC=227).items(): m[address(b, key)] = value
            m[address(b, 'TnAudioRam') + 4 + x] = coefficient
            m[0x5204] = 128;m[510], m[511] = 255, 1
            c = NesMPU(memory=m);c.pc, c.a, c.x, c.y, c.p, c.sp = 0xacbd, n, x, 7, flags, 253
            m.writes = [];m.math_events = []
            return c, m
        c, m = setup();trace = []
        for index in range(300):
            if c.pc == 512: break
            trace.append(index);m.executing_PC = c.pc;c.step()
        else: raise AssertionError('Uninterrupted multiply timeout')
        expected = registers(c), ordinary(m), list(m.banks), list(m.operands), list(m.math_events)
        for at in trace:
            d, q = setup();injected = False
            for index in range(300):
                if d.pc == 512: break
                if index == at:
                    before = registers(d), ordinary(q), list(q.banks), list(q.operands), list(q.math_events)
                    d.irq();assert d.pc == 0x8000;minimum = d.sp
                    for _ in range(300):
                        if d.pc == before[0][0] and d.sp == before[0][-1]: break
                        minimum = min(minimum, d.sp);q.executing_PC = d.pc;d.step()
                    else: raise AssertionError('Actual IRQ failed to return')
                    assert (registers(d), ordinary(q), list(q.banks), list(q.operands), list(q.math_events)) == before
                    maximum = max(maximum, 255 - minimum);injected = True
                q.executing_PC = d.pc;d.step()
            else: raise AssertionError('Interrupted multiply timeout')
            assert injected and (registers(d), ordinary(q), list(q.banks), list(q.operands), list(q.math_events)) == expected
            count += 1
        rows.append(dict(n=n, coefficient=coefficient, x=x, flags=flags, actual_IRQ_instruction_boundaries=len(trace)))
    proof = dict(passed=True, candidate_ROM_sha256=sha(a.candidate), real_compiled_IRQ_injections=count,
                 actual_vector=0x8000, maximum_total_stack_depth=maximum,
                 intermediate_operands_registers_RAM_banks_exact=True, final_source_state_math_stream_exact=True,
                 IRQ_has_no_math_register_access=True, no_nested_NMI_domain_claim=True,
                 cases=rows, source_only=True, native_run=False, checker_sha256=sha(Path(__file__)))
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: proof[k] for k in ['passed', 'real_compiled_IRQ_injections', 'maximum_total_stack_depth']}))


if __name__ == '__main__':
    main()

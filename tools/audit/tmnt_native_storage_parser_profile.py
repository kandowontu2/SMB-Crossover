"""Bind parser edits to actual407/505 states and original control-flow roots."""
from pathlib import Path
from collections import Counter
import argparse
import csv
import gzip
import json
from py65.disassembler import Disassembler
from tmnt_native_storage_driver import ROOT, OB, sha, source_data
from tmnt_native_storage_multiply_cpu import Linked


def closure():
    _, memory, cpu, disasm, seen, words = source_data()
    ranges = [(0x8937, 0x8951), (0x8ad4, 0x8ad7)]
    rows = []
    for lo, hi in ranges:
        incoming = []
        for pc in seen:
            if lo <= pc < hi: continue
            width, _ = disasm.instruction_at(pc)
            op, mode = cpu.disassemble[memory[pc]]
            targets = []
            if mode == 'rel':
                offset = memory[pc + 1]
                targets = [pc + width, pc + width + (offset - 256 if offset >= 128 else offset)]
            elif op in ['JMP', 'JSR']:
                if mode == 'abs': targets.append(memory[pc + 1] + 256 * memory[pc + 2])
                if op == 'JSR': targets.append(pc + width)
            elif op not in ['RTS', 'RTI', 'BRK']: targets = [pc + width]
            for target in targets:
                if lo <= target < hi: incoming.append(dict(source_PC=pc, target=target))
        pointer_roots = [word for word in words if lo <= memory[word] + 256 * memory[word + 1] < hi]
        assert all(row['target'] == lo for row in incoming) and not pointer_roots
        rows.append(dict(original_span=[lo, hi], incoming=incoming, original_pointer_roots=pointer_roots))
    return dict(complete_original_instructions=len(seen), complete_original_pointer_words=len(words),
                rewritten_instruction_interiors_no_external_entry=rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['experiment', 'baseline', 'candidate', 'output']: p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    actual = a.experiment / 'native-pilots-v1/diagnostic-candidate-easy-v3/source-state.csv'
    with actual.open() as stream: states = {int(row['sourceTick']): bytes.fromhex(row['ZP14_RAM174_hex']) for row in csv.DictReader(stream)}
    gold = json.loads(gzip.decompress((OB / 'probe-v2/song-02.json.gz').read_bytes()))
    parent, child = Linked(a.baseline, True), Linked(a.candidate, True)
    rows = []
    for tick in range(506):
        if tick not in [407, 505]:
            parent.call(gold[tick], 2);child.call(gold[tick], 2);continue
        assert parent.state() == child.state() == states[tick - 1]
        costs, profiles = [], []
        for runner, label in [(parent, 'parent'), (child, 'candidate')]:
            c, m = runner.c, runner.m
            disasm = Disassembler(c)
            stack, trace, own, instructions, counts = [], [], Counter(), Counter(), Counter()
            real_step = c.step
            def step():
                pc, before = c.pc, c.processorCycles
                _, text = disasm.instruction_at(pc)
                operation, mode = c.disassemble[m[pc]]
                owner = stack[-1] if stack else 0xa644
                target = m[pc + 1] + 256 * m[pc + 2] if operation == 'JSR' else None
                before_regs = [c.a, c.x, c.y, c.p & 207, c.sp]
                real_step()
                elapsed = c.processorCycles - before
                own[owner] += elapsed;instructions[pc, text] += elapsed;counts[pc] += 1
                trace.append(dict(PC=pc, instruction=text, cycles=elapsed, owner=owner, registers_before=before_regs))
                if operation == 'JSR': stack.append(target)
                elif operation == 'RTS' and stack: stack.pop()
            c.step = step
            cycles = runner.call(gold[tick], 2)
            c.step = real_step
            assert not stack
            costs.append(cycles)
            profiles.append(dict(label=label, full_source_CPUcycles=cycles,
                                 parser_A671_exclusive_CPUcycles=own[0xa671],
                                 actual_ADC_AAD0_count=counts[0xaad0], actual_SBC_A6A1_count=counts[0xa6a1],
                                 top_instructions=[dict(PC=pc, instruction=text, cycles=value, count=counts[pc]) for (pc, text), value in instructions.most_common(30)]))
            (a.output / f'{label}-{tick}.json.gz').write_bytes(gzip.compress(json.dumps(trace).encode()))
        assert parent.state() == child.state() == states[tick] and parent.registers() == child.registers()
        assert profiles[0]['actual_ADC_AAD0_count'] == profiles[1]['actual_ADC_AAD0_count']
        assert profiles[0]['actual_SBC_A6A1_count'] == profiles[1]['actual_SBC_A6A1_count']
        assert costs[1] <= costs[0]
        rows.append(dict(sourceTick=tick, parent_cycles=costs[0], candidate_cycles=costs[1], saved_CPUcycles=costs[0] - costs[1],
                         actual_native188byte_before_after_exact=True, original_ordered_APU=len(gold[tick]['writes']), profiles=profiles))
        print(rows[-1], flush=True)
    proof = dict(passed=True, source_only=True, native_run=False, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 actual_a983_native_state_stream_sha256=sha(actual), original_closure=closure(), rows=rows,
                 surrounding_506_calls_state_APU_ABI_exact=True, checker_sha256=sha(Path(__file__)),
                 limits='Actual native states bind CPU control flow. Isolated CPU fixture DMC state is disclosed; it does not simulate native DMA/PPU/NMI clocks or prove recovery of the eight lost draws.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(passed=True, saved=[row['saved_CPUcycles'] for row in rows])))


if __name__ == '__main__':
    main()

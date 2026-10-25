"""Profile exact original-driver hot calls bound to observed native source states.

Source-only attribution; no game edits, native launch or optimization acceptance.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import gzip
import json
from py65.disassembler import Disassembler
from tmnt_native_storage_driver import ROOT, OB, sha
from tmnt_native_storage_cpu import Probe


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--experiment', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    native = a.experiment / 'native-pilots-v1/diagnostic-candidate-easy-v3'
    with (native / 'source-state.csv').open() as stream: states = {int(row['sourceTick']): row for row in csv.DictReader(stream)}
    with (native / 'audio-components.csv').open() as stream: components = list(csv.DictReader(stream))
    with (native / 'source-apu.csv').open() as stream: source_requests = list(csv.DictReader(stream))
    gold = json.loads(gzip.decompress((OB / 'probe-v2/song-02.json.gz').read_bytes()))
    original = Probe(a.experiment / 'standalone-original-v1', True)
    raw = Probe(a.experiment / 'standalone-swap-v2', True)
    apu_sites = set(row['pc'] + 8192 if row['pc'] < 0xc000 else row['pc'] - 8192 for row in raw.info['APU_stores'])
    result = []
    for index in range(506):
        if index not in [407, 505]:
            original.call(gold[index], 2);raw.call(gold[index], 2);continue
        assert raw.state() == bytes.fromhex(states[index - 1]['ZP14_RAM174_hex'])
        disasm = Disassembler(raw.c)
        costs, counts = Counter(), Counter()
        owners, own_cost, owner_calls = [], Counter(), Counter()
        trace, multiply_inputs = [], []
        real_step = raw.c.step
        def step():
            c, m = raw.c, raw.m
            pc, before = c.pc, c.processorCycles
            width, text = disasm.instruction_at(pc)
            opcode, mode = c.disassemble[m[pc]]
            if pc == 0xacbd:
                multiply_inputs.append(dict(A=c.a, coefficient=m[0x7004 + c.x], X=c.x, P=c.p))
            owner = owners[-1] if owners else 0xa644
            if opcode == 'JSR':
                target = m[pc + 1] + 256 * m[pc + 2]
                owner_calls[target] += 1
            real_step()
            elapsed = c.processorCycles - before
            costs[pc, text] += elapsed;counts[pc, text] += 1;own_cost[owner] += elapsed
            trace.append(dict(pc=pc, text=text, cycles=elapsed, owner=owner))
            if opcode == 'JSR': owners.append(target)
            elif opcode == 'RTS' and owners: owners.pop()
        raw.c.step = step
        raw_cycles = raw.call(gold[index], 2)
        raw.c.step = real_step
        original_cycles = original.call(gold[index], 2)
        assert not owners and raw.state() == bytes.fromhex(states[index]['ZP14_RAM174_hex'])
        request = next(row for row in source_requests if int(row['sourceTick']) == index)
        clock = int(request['cpu'])
        call = next(row for row in components if row['name'] == 'TnNativePlay' and int(row['startCPU']) <= clock <= int(row['endCPU']))
        writers = [row for row in components if row['name'].startswith('TnSourceSTA') and int(row['startCPU']) >= int(call['startCPU']) and int(row['endCPU']) <= int(call['endCPU'])]
        replacement_sites = sum(1 for row in trace if row['pc'] in apu_sites)
        assert replacement_sites == len(writers) == len(gold[index]['writes'])
        replacement_overhead = sum(6 - row['cycles'] for row in trace if row['pc'] in apu_sites)
        predicted = raw_cycles + sum(int(row['CPUcycles']) for row in writers) + replacement_overhead
        residual = int(call['CPUcycles']) - predicted
        # Every driver opcode/call/branch is recorded; driver RAM and original
        # APU order match the observed actual native source call.
        row = dict(sourceTick=index, original_source_cycles=original_cycles,
                   duration_and_storage_raw_cycles=raw_cycles, actual_native_core_cycles=int(call['CPUcycles']),
                   actual_native_writer_cycles=sum(int(row['CPUcycles']) for row in writers),
                   replaced_STA_count=replacement_sites, JSR_minus_actual_original_STA_cycles=replacement_overhead,
                   measured_native_minus_reconstructed_residual=residual,
                   hot_instructions=[dict(pc=pc, instruction=text, cycles=value, count=counts[pc, text]) for (pc, text), value in costs.most_common(25)],
                   own_cycles_by_direct_call_target={hex(key): value for key, value in own_cost.most_common()},
                   direct_call_counts={hex(key): value for key, value in owner_calls.most_common()},
                   original_ACBD_multiply_inputs=multiply_inputs,
                   writer_details=writers)
        result.append(row)
        (a.output / f'trace-{index}.json').write_text(json.dumps(trace, indent=2) + '\n')
        print(json.dumps(row), flush=True)
    proof = dict(passed=True, source_only=True, native_run=False, production_changes=False,
                 actual_native_candidate_sha256='a9838664f94d29d87fbf4742e31d4e20d8b3a96862beabd11224afa4742d9003',
                 actual_native_state_stream_sha256=sha(native / 'source-state.csv'),
                 actual_native_cost_stream_sha256=sha(native / 'audio-components.csv'),
                 source_before_and_after188_byte_states_literal_native_exact=True,
                 complete_original_ordered_APU_exact=True, rows=result, tool_sha256=sha(Path(__file__)),
                 limits='Exact CPU driver trace bound to actual native source input/output states; measured residual remains explicit rather than asserted to be fully DMA. No optimized implementation or native cadence acceptance.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')


if __name__ == '__main__':
    main()

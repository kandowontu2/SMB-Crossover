"""Original Parodius final pointer-plus-Y closure through proven state repeats.

Source-only: no replacement music, game source mutation, Mesen, DMA timing,
track title guess or native integration claim. Original cartridge wrappers
bind reset C542, grouped request C58D and play80A2 with banks12/13/14/15.
"""
from pathlib import Path
from collections import Counter
import argparse, gzip, hashlib, json
from py65.disassembler import Disassembler
from mike_parodius_rom_probe import RomBus, SOURCE, EXPECTED
from verify_native_relocation import NesMPU

ROOT = Path(__file__).resolve().parents[2]
ZP = [0x45] + list(range(0xe0, 0xf0))
RAM = list(range(0x500, 0x600))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--calls', type=int, default=18000)
    p.add_argument('--songs', default=','.join(f'{s:x}' for s in range(0x46, 0x9b, 4)))
    p.add_argument('--gold', type=Path, required=True)
    a = p.parse_args()
    songs = [int(s, 16) for s in a.songs.split(',')]
    assert set(songs) <= set(range(0x46, 0x9b, 4))
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    raw = SOURCE.read_bytes()
    assert sha(SOURCE) == EXPECTED
    golden = json.loads((a.gold / 'coverage.json').read_text())
    assert golden['passed'] and golden['source_sha256'] == EXPECTED
    assert golden['provenance_version'] == 2
    reference_calls = reference_writes = 0
    seen, data, pairs, unknown, accesses, stores_at = set(), set(), set(), set(), {}, {}
    immediate_origins, pointer_accesses, final_pointer_accesses = set(), set(), set()
    pc_count, pc_cycles, summaries = Counter(), Counter(), {}
    source_insns, sample_configs = {}, set()
    for song in songs:
        m = RomBus(raw)
        c = NesMPU(memory=m)
        dis = Disassembler(c)
        origins, regs, stack_origins = {}, {'a': None, 'x': None, 'y': None}, {}

        def read(at):
            return m.peek(at)

        def romorigin(at):
            return m.physical(at) if at >= 0x8000 else origins.get(at)

        def effective(pc, mode):
            v = read(pc + 1)
            word = v + 256 * read(pc + 2)
            if mode == 'zpg': return v
            if mode == 'zpx': return (v + c.x) & 255
            if mode == 'zpy': return (v + c.y) & 255
            if mode == 'abs': return word
            if mode == 'abx': return (word + c.x) & 65535
            if mode == 'aby': return (word + c.y) & 65535
            if mode in ['inx', 'iny', 'ind']:
                ptr = (v + c.x) & 255 if mode == 'inx' else v if mode == 'iny' else word
                hi = (ptr + 1) & 255 if mode != 'ind' else (ptr & 65280) | ((ptr + 1) & 255)
                target = read(ptr) + 256 * read(hi)
                if target >= 0x8000:
                    lo_origin, hi_origin = origins.get(ptr), origins.get(hi)
                    row = (pc, ptr, target, lo_origin, hi_origin)
                    if lo_origin is None or hi_origin is None:
                        unknown.add(row)
                    else:
                        base = m.image[lo_origin] + 256 * m.image[hi_origin]
                        if base < 0x8000:
                            unknown.add(row)
                        else:
                            pairs.add((lo_origin, hi_origin, base, m.physical(base)))
                            pointer_accesses.add((pc, ptr, base, target, (target - base) & 65535))
                            actual = (target + (c.y if mode == 'iny' else 0)) & 65535
                            final_pointer_accesses.add((pc, ptr, base, actual, (actual - base) & 65535))
                return (target + (c.y if mode == 'iny' else 0)) & 65535
            return None

        costs, writes, minsp, peak = [], 0, 255, None
        repeats, prior_states = [], {}
        peak_trace, current_trace = [], []
        capture = out / f'song-{song:02x}.jsonl.gz'
        with gzip.open(capture, 'wt', encoding='utf-8', newline='\n') as stream, gzip.open(a.gold / capture.name, 'rt') as reference:
            for step in range(a.calls + 2):
                c.pc = 0xc542 if step == 0 else 0xc58d if step == 1 else 0x80a2
                c.a, c.x, c.y, c.sp, c.p = song if step == 1 else 0, 0, 0, 253, 36
                list.__setitem__(m, 510, 255)
                list.__setitem__(m, 511, 126)
                m.events = []
                start = c.processorCycles
                current_trace = []
                if step < 2:
                    regs.update(a=None, x=None, y=None)
                for _ in range(200000):
                    if c.pc == 0x7f00:
                        break
                    pc = c.pc
                    assert pc >= 0x8000, (song, step, hex(pc))
                    physical = m.physical(pc)
                    seen.add((pc, physical))
                    op, mode = c.disassemble[read(pc)]
                    at = effective(pc, mode)
                    if at is not None:
                        accesses.setdefault(pc, set()).add(at)
                    if pc not in source_insns:
                        n, text = dis.instruction_at(pc)
                        source_insns[pc] = dict(physical=physical, size=n, instruction=text)
                    if op in ['LDA', 'LDX', 'LDY']:
                        regs[op[-1].lower()] = m.physical(pc + 1) if mode == 'imm' else romorigin(at)
                        if mode == 'imm': immediate_origins.add(m.physical(pc + 1))
                        if at is not None and at >= 0x8000:
                            data.add(m.physical(at))
                    elif op in ['STA', 'STX', 'STY']:
                        origins[at] = regs[op[-1].lower()]
                        stores_at.setdefault(pc, set()).add(at)
                    elif op in ['TAX', 'TAY']:
                        regs[op[-1].lower()] = regs['a']
                    elif op in ['TXA', 'TYA']:
                        regs['a'] = regs[op[1].lower()]
                    elif op == 'PHA': stack_origins[c.sp] = regs['a']
                    elif op == 'PLA': regs['a'] = stack_origins.get((c.sp + 1) & 255)
                    elif op in ['ADC', 'SBC']:
                        # ROM pointer bytes remain anchored to their source byte
                        # when adding runtime indices/carries. Immediate constants
                        # are scalar terms when combined with a ROM-loaded base.
                        right = m.physical(pc + 1) if mode == 'imm' else romorigin(at)
                        terms = {v for v in [regs['a'], right] if v is not None and v not in immediate_origins}
                        regs['a'] = next(iter(terms)) if len(terms) == 1 else None
                    elif op in ['AND', 'ORA', 'EOR'] or op in ['ASL', 'LSR', 'ROL', 'ROR'] and mode == 'acc':
                        regs['a'] = None
                    elif op in ['INX', 'DEX', 'TSX']: regs['x'] = None
                    elif op in ['INY', 'DEY']: regs['y'] = None
                    # INC/DEC preserve the affine ROM-byte anchor. Their actual
                    # changing byte values are retained literally in every golden.
                    if op in ['ASL', 'LSR', 'ROL', 'ROR'] and at is not None:
                        origins[at] = None
                    if op in ['LDA', 'LDX', 'LDY', 'ADC', 'SBC', 'CMP', 'CPX', 'CPY', 'BIT', 'AND', 'ORA', 'EOR'] and at is not None and at >= 0x8000:
                        data.add(m.physical(at))
                    before = c.processorCycles
                    current_trace.append((pc, c.a, c.x, c.y, c.p, c.sp, c.processorCycles - start))
                    minsp = min(minsp, c.sp)
                    c.step()
                    pc_count[pc] += 1
                    pc_cycles[pc] += c.processorCycles - before
                else:
                    raise AssertionError(('Source timeout', song, step, hex(c.pc)))
                assert c.sp == 255 and not m.bad_writes and not m.mapper and not m.io_reads
                elapsed = c.processorCycles - start
                if step >= 2:
                    costs.append(elapsed)
                    if peak is None or elapsed > peak['cycles']:
                        peak = dict(step=step, cycles=elapsed)
                        peak_trace = current_trace
                for at, value in m.events:
                    if at == 0x4015 and value & 16:
                        sample_configs.add(tuple(m.apu[16:20]))
                writes += len(m.events)
                state = bytes(read(x) for x in ZP + RAM)
                h = hashlib.sha256(state).hexdigest()
                if step >= 2:
                    if h in prior_states and len(repeats) < 16:
                        repeats.append([prior_states[h], step, step - prior_states[h]])
                    else:
                        prior_states[h] = step
                stream.write(json.dumps(dict(step=step, cycles=elapsed, writes=m.events,
                                             state=list(state), origins=[origins.get(x) for x in ZP + RAM],
                                             full_source_RAM_sha256=hashlib.sha256(bytes(list.__getitem__(m, slice(0, 2048))) +
                                                 bytes(list.__getitem__(m, slice(0x6000, 0x8000)))).hexdigest()),
                                        separators=(',', ':')) + '\n')
                original = json.loads(next(reference))
                assert original['step'] == step and original['cycles'] == elapsed
                assert original['writes'] == [list(v) for v in m.events]
                assert original['state'] == list(state)
                assert original['full_source_RAM_sha256'] == hashlib.sha256(bytes(list.__getitem__(m, slice(0, 2048))) + bytes(list.__getitem__(m, slice(0x6000, 0x8000)))).hexdigest()
                reference_calls += 1
                reference_writes += len(m.events)
                if repeats: break
        assert repeats and repeats[0] == golden['original_exact_state_repeats'][str(song)][0]
        (out / f'song-{song:02x}-peak.json').write_text(json.dumps(peak | dict(trace=peak_trace), separators=(',', ':')) + '\n')
        summaries[str(song)] = dict(source_calls=step + 1, play_calls=step - 1,
                                    ordered_APU_stores=writes, mean_play_cycles=sum(costs) / len(costs),
                                    peak=peak, minimum_SP=minsp, exact_state_repeats=repeats,
                                    source_RAM_reads=sorted(m.ram_reads), source_RAM_writes=sorted(m.ram_writes),
                                    DMC_sample_physical_bytes=sorted(m.sample_ranges), capture_sha256=sha(capture))
        print(hex(song), {k: summaries[str(song)][k] for k in ['ordered_APU_stores', 'mean_play_cycles', 'peak', 'minimum_SP']}, flush=True)
    probe = dict(passed=True, source_only=True, native_emulator_launched=False,
                 source=str(SOURCE), source_sha256=EXPECTED, songs=songs, calls_per_song=a.calls,
                 source_reset=0xc542, source_request=0xc58d, source_play=0x80a2,
                 source_mapped_banks=[12, 13, 14, 15], ZP=ZP, RAM=RAM,
                 seen_instructions=sorted(map(list, seen)), ROM_data_reads=sorted(data),
                 source_instructions=source_insns,
                 pointer_components=sorted(map(list, pairs)), unknown_pointer_origins=sorted(map(list, unknown)),
                 pointer_accesses=sorted(map(list, pointer_accesses)),
                 final_pointer_plus_Y_accesses=sorted(map(list, final_pointer_accesses)), provenance_version=3,
                 exact_reference_prefix_calls=reference_calls, exact_reference_prefix_APU_stores=reference_writes,
                 reference_coverage_sha256=sha(a.gold / 'coverage.json'),
                 first_exact_state_repeat_terminated_every_track=True,
                 golden_probe_v2_sha256='28dbae5d036c74bcc36a6ab6d146b2a8b619f1ca35f83883cdc3fc4c6838e9fb',
                 accesses={k: sorted(v) for k, v in accesses.items()}, stores={k: sorted(v) for k, v in stores_at.items()},
                 profile={pc: dict(count=pc_count[pc], cycles=pc_cycles[pc]) for pc in pc_count},
                 DMC_register_configs=sorted(map(list, sample_configs)), tracks=summaries,
                 tool_sha256=sha(Path(__file__)), inherited_probe_sha256=sha(ROOT / 'tools/audit/mike_parodius_rom_probe.py'),
                 limits='Every original source call through each first exact persistent-state repeat is compared with the full goldens. External pause is zero and there are no external source SFX. Final indirect pointer plus Y is recorded; byte-span feasibility is not a linked relocation, native DMA/IRQ/cadence or waveform claim.')
    (out / 'coverage.json').write_text(json.dumps(probe, indent=2) + '\n')
    m = RomBus(raw)
    c = NesMPU(memory=m)
    d = Disassembler(c)
    lines = []
    for lo, hi in [(0xc542, 0xc650), (0x80a2, 0x81d0)]:
        lines.append(f'\nSPAN {lo:04x}..{hi:04x}')
        while lo < hi:
            size, text = d.instruction_at(lo)
            lines.append(f'{lo:04X} {text}')
            lo += size
    (out / 'source-entries.txt').write_text('\n'.join(lines) + '\n')
    print('COMPLETE', len(seen), len(data), len(pairs), len(unknown), flush=True)


if __name__ == '__main__':
    main()

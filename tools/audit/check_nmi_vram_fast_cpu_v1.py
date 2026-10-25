"""Execute both linked NMI transfer paths; no native timing acceptance claim."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_tmnt_render_oa import Memory, address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Bus(Memory):
    def __init__(self, bundle):
        super().__init__(bundle)
        self.page(2, 116)
        for at in range(0x800):
            list.__setitem__(self, at, (at * 73 + 19) & 255)
        for at in range(0x5c00, 0x8000):
            list.__setitem__(self, at, (at * 31 + 7) & 255)
        self.reads = []
        self.palette = None
        self.writes = []

    def __getitem__(self, at):
        if at == 0x2007 and self.palette is not None:
            assert len(self.reads) < len(self.palette)
            value = self.palette[len(self.reads)]
            self.reads.append((at, value))
            return value
        return super().__getitem__(at)

    def put(self, at, value):
        list.__setitem__(self, at, value)


def run(bundle, memory, start, stop, a, x, y, flags, irq_after=None):
    memory.writes = []
    memory.reads = []
    cpu = NesMPU(memory=memory, pc=start)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, flags, 0xfd
    injected = False
    for steps in range(30000):
        if cpu.pc == stop:
            break
        # Actual compiled IRQ, between complete 6502 instructions. Its extra
        # PPU/bank writes must also agree between the two transfer versions.
        if irq_after is not None and not injected:
            count = sum(at == 0x2007 for at, _ in memory.writes)
            if count >= irq_after:
                memory.put(0x5204, 0x80)
                cpu.p &= ~cpu.INTERRUPT
                cpu.irq()
                injected = True
        cpu.step()
    else:
        raise AssertionError(('CPU timeout', hex(cpu.pc), memory.banks))
    assert irq_after is None or injected
    state = (cpu.a, cpu.x, cpu.y, cpu.p & 0xcf, cpu.sp)
    writes = [(at, value) for at, value in memory.writes if not 0x100 <= at < 0x200]
    ram = bytes(list.__getitem__(memory, slice(0, 0x100)))
    ram += bytes(list.__getitem__(memory, slice(0x200, 0x800)))
    ram += bytes(list.__getitem__(memory, slice(0x5c00, 0x8000)))
    return dict(state=state, writes=writes, reads=memory.reads[:], ram=ram,
                banks=memory.banks[:], cycles=cpu.processorCycles, steps=steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    old, new = scoped_load(args.baseline), scoped_load(args.candidate)
    assert sha(args.baseline) == '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    assert sha(args.candidate) == 'cf0f53f012a7830c38d4a2212ceed8bc875040b5698345a83d0b7c98213eeed5'
    for name, symbol in old['syms'].items():
        assert name in new['syms'], name
        assert symbol['val'] == new['syms'][name]['val'], name
    allowed = set(range(1032315, 1032318)) | set(range(950337, 950340))
    allowed |= set(range(952745, 952745 + 298))
    differing = [i for i, (a, b) in enumerate(zip(old['raw'], new['raw'])) if a != b]
    assert len(old['raw']) == len(new['raw']) and len(differing) == 304
    assert set(differing) <= allowed
    assert old['raw'][952745:952745 + 298] == bytes([255]) * 298
    memories = [Bus(old), Bus(new)]
    flags_values = [0x30 | (v << 2 & 4) | (v << 2 & 8) | (v << 4 & 0x40)
                    for v in range(8)]
    assert len(set(flags_values)) == 8
    rows = []

    def compare(kind, spec, start_name, stop_offset, prepare, regs, irq_after=None):
        values = []
        for bundle, memory in zip((old, new), memories):
            prepare(bundle, memory)
            start = address(bundle, start_name)
            values.append(run(bundle, memory, start, start + stop_offset,
                              *regs, irq_after=irq_after))
        before, after = values
        for key in ('state', 'writes', 'reads', 'ram', 'banks'):
            assert before[key] == after[key], (kind, spec, key,
                before[key] if key != 'ram' else 'RAM mismatch',
                after[key] if key != 'ram' else 'RAM mismatch')
        rows.append(dict(kind=kind, spec=spec, before=before['cycles'], after=after['cycles']))

    shapes = [(0, 0x0300), (1, 0x0301), (7, 0x037f), (127, 0x03f0),
              (248, 0x03ff), (255, 0x0600), (252, 0x06f8), (128, 0x067f)]
    cases = set()
    for x, carry, shape in itertools.product(range(256), range(2), range(8)):
        y, pointer = shapes[shape]
        cases.add((x, carry, y, pointer, flags_values[(x + shape) % 8]))
    for x, carry, y, pointer, flags in itertools.product(
            [0, 1, 2, 7, 8, 9, 15, 16, 17, 63, 64, 127, 128, 255], range(2),
            [0, 7, 127, 248, 252, 255], [0x0300, 0x0301, 0x037f, 0x03f0, 0x03ff, 0x06ff], flags_values):
        cases.add((x, carry, y, pointer, flags))
    for x, carry, y, pointer, flags in sorted(cases):
        def prepare(bundle, memory):
            memory.palette = None
            memory.put(address(bundle, 'NmiR0'), pointer & 255)
            memory.put(address(bundle, 'NmiR1'), pointer >> 8)
        compare('transfer', [x, carry, y, pointer, flags], 'OutputToVRAM', 11,
                prepare, (0xa5, x, y, (flags & ~1) | carry))
    print(json.dumps(dict(stage='transfer', cases=len(rows))), flush=True)

    for seed, y, flags in itertools.product(range(256), [0, 255], flags_values):
        palette = [(seed + i * 97) & 255 for i in range(32)]
        def prepare(bundle, memory):
            memory.palette = palette
            base = address(bundle, 'PnBombPaletteShadow')
            for i in range(32):
                memory.put(base + i, (i * 41 + 7) & 255)
        compare('palette', [seed, y, flags], 'PnPaletteScreenUpdate::Copy', 11,
                prepare, (0, 0, y, flags))
    print(json.dumps(dict(stage='palette', cases=sum(r['kind'] == 'palette' for r in rows))), flush=True)

    # The public routine includes length flags, source pointer progression,
    # multiple commands, the terminator and final scroll/latch writes.
    packets = []
    for length, repeat, vertical in itertools.product(range(1, 64), range(2), range(2)):
        count = length
        payload = [(i * 43 + 91) & 255 for i in range(1 if repeat else count)]
        packets.append([0x23, 0xf0, length | (repeat << 6) | (vertical << 7)] + payload + [0])
    packets += [[0x20, 0x22, 28] + list(range(28)) + [0x23, 0xc0, 8] + list(range(8))
                + [0x3f, 0x0c, 4, 15, 0, 16, 32, 0x20, 0x7a, 3, 1, 2, 3, 0],
                [0x21, 0x10, 0x7f, 0xa5, 0x22, 0x10, 0x81, 0x37, 0]]
    for packet_id, pointer, flags in itertools.product(range(len(packets)), [0x0300, 0x03f8], flags_values):
        packet = packets[packet_id]
        def prepare(bundle, memory):
            memory.palette = None
            for i, value in enumerate(packet):
                memory.put(pointer + i, value)
            memory.put(address(bundle, 'NmiR0'), pointer & 255)
            memory.put(address(bundle, 'NmiR1'), pointer >> 8)
            memory.put(address(bundle, 'Mirror_PPUCTRL'), (packet_id * 11) & 255)
            memory.put(0x2002, 0x80)
            memory.put(0x1fe, 0xff)
            memory.put(0x1ff, 0x01)
        # RTS uses the preloaded return at01FE/01FF ->0200.
        start = address(old, 'UpdateScreen')
        compare('packet', [packet_id, pointer, flags], 'UpdateScreen', 0x0200 - start,
                prepare, (0x55, 0x37, 0xa5, flags))
    print(json.dumps(dict(stage='packets', cases=sum(r['kind'] == 'packet' for r in rows))), flush=True)

    for length, carry, boundary in itertools.product([1, 7, 8, 9, 32, 63, 255, 0], range(2), [0, 1]):
        count = length or 256
        for after in sorted({0, min(8, count - 1), count - 1}):
            pointer, y = (0x03ff, 255) if boundary else (0x0300, 0)
            def prepare(bundle, memory):
                memory.palette = None
                memory.put(address(bundle, 'NmiR0'), pointer & 255)
                memory.put(address(bundle, 'NmiR1'), pointer >> 8)
                memory.put(address(bundle, 'IrqNewScroll'), 0xa5)
                memory.put(address(bundle, 'IrqPPUCTRL'), 1)
            compare('irq-transfer', [length, carry, boundary, after], 'OutputToVRAM', 11,
                    prepare, (0x55, length, y, 0x70 | carry), irq_after=after)

    result = dict(passed=True, baseline_ROM_sha256=sha(args.baseline),
        candidate_ROM_sha256=sha(args.candidate), tool_sha256=sha(__file__),
        all_existing_scoped_symbol_addresses_exact=True, differing_bytes=len(differing),
        new_tail_was_FF=True, cases=len(rows), groups={},
        equality='A/X/Y/NV-DIZC/SP, all nonstack application RAM, final mapper banks, ordered nonstack writes including every2007 byte, ordered palette reads.',
        IRQ_scope='Compiled IrqScrollSplit injected between complete instructions at bounded write boundaries; no PPU cycle or native scheduling model.',
        limits='Only exact linked transfer/palette helpers and complete UpdateScreen packets. Native DMA/IRQ scanline/CHR/roster/palette-burst budget still required; short literal transfers may cost extra cycles.')
    for kind in sorted({r['kind'] for r in rows}):
        selected = [r for r in rows if r['kind'] == kind]
        delta = [r['after'] - r['before'] for r in selected]
        result['groups'][kind] = dict(cases=len(selected), cycle_delta_min=min(delta),
                                     cycle_delta_max=max(delta))
    raw = args.output / 'cases.json'
    raw.write_text(json.dumps(rows, separators=(',', ':')) + '\n')
    result['cases_sha256'] = sha(raw)
    (args.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()

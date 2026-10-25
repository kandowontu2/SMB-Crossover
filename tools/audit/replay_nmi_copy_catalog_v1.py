"""Replay the frozen independent20,284-case NMI helper catalog on a new ROM.

Only transfer/palette/UpdateScreen/IRQ component equivalence is asserted.
HUD publication, full NMI budgets, source integration and native timing need
separate qualification. No whole-ROM adoption verdict is produced here.
"""
from pathlib import Path
import argparse
import itertools
import json

from check_nmi_vram_fast_cpu_v1 import Bus, address, run, scoped_load, sha

BASE = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
CATALOG = '88f303ff2e1a3cf249294866186cf84eb7c637a53e69431658bd66fd229717ad'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--catalog', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert sha(args.baseline) == BASE
    assert sha(args.candidate) == args.expected_sha256
    assert sha(args.catalog) == CATALOG
    args.output.mkdir(parents=True, exist_ok=False)
    old, new = scoped_load(args.baseline), scoped_load(args.candidate)
    for name in ['OutputToVRAM', 'UpdateScreen', 'NmiR0', 'NmiR1',
                 'PnPaletteScreenUpdate::Copy', 'PnBombPaletteShadow']:
        assert address(old, name) == address(new, name), name
    memories = [Bus(old), Bus(new)]
    packets = []
    for length, repeat, vertical in itertools.product(range(1, 64), range(2), range(2)):
        data = [(i * 43 + 91) & 255 for i in range(1 if repeat else length)]
        packets.append([0x23, 0xf0, length | (repeat << 6) | (vertical << 7)] + data + [0])
    packets += [[0x20, 0x22, 28] + list(range(28)) + [0x23, 0xc0, 8] + list(range(8))
                + [0x3f, 0x0c, 4, 15, 0, 16, 32, 0x20, 0x7a, 3, 1, 2, 3, 0],
                [0x21, 0x10, 0x7f, 0xa5, 0x22, 0x10, 0x81, 0x37, 0]]
    catalog = json.loads(args.catalog.read_text())
    assert len(catalog) == 20284
    stats = {}
    for case_id, row in enumerate(catalog):
        kind, spec = row['kind'], row['spec']
        values = []
        for bundle, memory in zip((old, new), memories):
            memory.palette = None
            irq_after = None
            if kind in ['transfer', 'irq-transfer']:
                name, stop = 'OutputToVRAM', address(bundle, 'OutputToVRAM') + 11
                if kind == 'transfer':
                    x, carry, y, pointer, flags = spec
                    regs = (0xa5, x, y, (flags & ~1) | carry)
                else:
                    x, carry, boundary, irq_after = spec
                    pointer, y = (0x03ff, 255) if boundary else (0x0300, 0)
                    regs = (0x55, x, y, 0x70 | carry)
                    memory.put(address(bundle, 'IrqNewScroll'), 0xa5)
                    memory.put(address(bundle, 'IrqPPUCTRL'), 1)
                memory.put(address(bundle, 'NmiR0'), pointer & 255)
                memory.put(address(bundle, 'NmiR1'), pointer >> 8)
            elif kind == 'palette':
                seed, y, flags = spec
                name = 'PnPaletteScreenUpdate::Copy'
                stop = address(bundle, name) + 11
                memory.palette = [(seed + i * 97) & 255 for i in range(32)]
                for i in range(32):
                    memory.put(address(bundle, 'PnBombPaletteShadow') + i, (i * 41 + 7) & 255)
                regs = (0, 0, y, flags)
            elif kind == 'packet':
                packet_id, pointer, flags = spec
                name, stop = 'UpdateScreen', 0x0200
                for i, value in enumerate(packets[packet_id]):
                    memory.put(pointer + i, value)
                memory.put(address(bundle, 'NmiR0'), pointer & 255)
                memory.put(address(bundle, 'NmiR1'), pointer >> 8)
                memory.put(address(bundle, 'Mirror_PPUCTRL'), (packet_id * 11) & 255)
                memory.put(0x2002, 0x80)
                memory.put(0x1fe, 0xff)
                memory.put(0x1ff, 0x01)
                regs = (0x55, 0x37, 0xa5, flags)
            else:
                raise AssertionError(('Unknown frozen case kind', kind))
            values.append(run(bundle, memory, address(bundle, name), stop, *regs, irq_after=irq_after))
        before, after = values
        assert before['cycles'] == row['before'], ('Frozen baseline reconstruction', case_id, spec)
        for key in ['state', 'writes', 'reads', 'ram', 'banks']:
            if before[key] != after[key]:
                failure = dict(passed=False, case=case_id, kind=kind, spec=spec, field=key,
                    baseline_ROM_sha256=BASE, candidate_ROM_sha256=sha(args.candidate))
                if key == 'ram':
                    failure['first_differences'] = [(i, a, b) for i, (a, b) in
                        enumerate(zip(before[key], after[key])) if a != b][:20]
                else:
                    failure['before'], failure['after'] = before[key], after[key]
                (args.output / 'failure.json').write_text(json.dumps(failure, indent=2) + '\n')
                raise AssertionError((case_id, kind, spec, key))
        delta = after['cycles'] - before['cycles']
        group = stats.setdefault(kind, dict(cases=0, cycle_delta_min=delta, cycle_delta_max=delta))
        group['cases'] += 1
        group['cycle_delta_min'] = min(group['cycle_delta_min'], delta)
        group['cycle_delta_max'] = max(group['cycle_delta_max'], delta)
    assert {k: v['cases'] for k, v in stats.items()} == dict(transfer=12048, palette=4096, packet=4064, **{'irq-transfer': 76})
    proof = dict(passed=True, component_only=True, native_run=False, adoption_qualified=False,
        baseline_ROM_sha256=BASE, candidate_ROM_sha256=sha(args.candidate),
        tool_sha256=sha(__file__), catalog_path=args.catalog.resolve().as_posix(),
        catalog_sha256=CATALOG, cases=len(catalog), groups=stats,
        dependencies={Path(p).name: sha(Path(p)) for p in [
            Path(__file__).with_name('check_nmi_vram_fast_cpu_v1.py'),
            Path(__file__).with_name('check_tmnt_render_oa.py'),
            Path(__file__).with_name('link_pit_rygar_sophia_audit_cpu.py'),
            Path(__file__).with_name('verify_native_relocation.py')]},
        equality='AXYP/SP, all final nonstack application RAM, every ordered nonstack write/palette read and final mapper banks. Every reconstructed baseline cycle count matches the immutable first catalog.',
        limits=__doc__)
    (args.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2), flush=True)


if __name__ == '__main__':
    main()

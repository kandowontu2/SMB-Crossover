"""Check full native continuation after the private chunk counter trial.

The old partial-stop catalog is immutable. Here its transfer shapes continue
through real SEC/TYA/ADC and UpdateScreen RTS, using a synthetic terminator.
No register/flag/RAM exclusion is added to the full returned-state comparison.
"""
from pathlib import Path
import argparse
import itertools
import json

from check_nmi_vram_fast_cpu_v1 import Bus, address, run, scoped_load, sha
from check_tmnt_audio_fallback_oc import qualified

CATALOG = '88f303ff2e1a3cf249294866186cf84eb7c637a53e69431658bd66fd229717ad'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--catalog', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expected-baseline-sha256', required=True)
    p.add_argument('--expected-candidate-sha256', required=True)
    a = p.parse_args()
    PARENT, NEW = a.expected_baseline_sha256, a.expected_candidate_sha256
    assert len(PARENT) == len(NEW) == 64
    assert sha(a.baseline) == PARENT and sha(a.candidate) == NEW
    assert sha(a.catalog) == CATALOG
    a.output.mkdir(parents=True, exist_ok=False)
    bundles = [scoped_load(a.baseline), scoped_load(a.candidate)]
    assert len(bundles[0]['raw']) == len(bundles[1]['raw'])
    assert address(bundles[0], 'FastNmiPaletteCapture') == address(bundles[1], 'FastNmiPaletteCapture')
    lo = 16 + 116*8192 + address(bundles[0], 'FastNmiVramCopy') - 0xc000
    hi = 16 + 116*8192 + address(bundles[0], 'FastNmiPaletteCapture') - 0xc000
    changed = [i for i, (x, y) in enumerate(zip(bundles[0]['raw'], bundles[1]['raw'])) if x != y]
    assert changed and all(lo <= i < hi for i in changed)
    qold, qnew = qualified(a.baseline), qualified(a.candidate)
    moved = {str(k): [v, qnew.get(k)] for k, v in qold.items() if qnew.get(k) != v}
    assert moved and all(k[0] == 'FastNmiVramCopy' for k, v in qold.items() if qnew.get(k) != v)
    for b in bundles:
        m = Bus(b)
        r0, r1 = address(b, 'NmiR0'), address(b, 'NmiR1')
        assert r0 < 256 and r1 < 256
        continuation = bytes([0x38, 0x98, 0x65, r0, 0x85, r0, 0xa9, 0,
                              0x65, r1, 0x85, r1])
        at = address(b, 'OutputToVRAM') + 11
        assert bytes(m[at+i] for i in range(len(continuation))) == continuation
    packets = []
    for length, repeat, vertical in itertools.product(range(1, 64), range(2), range(2)):
        data = [(i*43+91) & 255 for i in range(1 if repeat else length)]
        packets.append([0x23, 0xf0, length | repeat << 6 | vertical << 7] + data + [0])
    packets += [[0x20, 0x22, 28] + list(range(28)) + [0x23, 0xc0, 8] + list(range(8))
                + [0x3f, 0x0c, 4, 15, 0, 16, 32, 0x20, 0x7a, 3, 1, 2, 3, 0],
                [0x21, 0x10, 0x7f, 0xa5, 0x22, 0x10, 0x81, 0x37, 0]]
    memories = [Bus(b) for b in bundles]
    catalog = json.loads(a.catalog.read_text())
    assert len(catalog) == 20284
    rows, groups = [], {}
    for case, entry in enumerate(catalog):
        kind, spec = entry['kind'], entry['spec']
        values = []
        for b, m in zip(bundles, memories):
            m.palette = None
            irq_after, terminator = None, None
            if kind in ('transfer', 'irq-transfer'):
                if kind == 'transfer':
                    x, carry, y, pointer, flags = spec
                    regs = (0xa5, x, y, flags & ~1 | carry)
                else:
                    x, carry, boundary, irq_after = spec
                    pointer, y = (0x03ff, 255) if boundary else (0x0300, 0)
                    regs = (0x55, x, y, 0x70 | carry)
                    m.put(address(b, 'IrqNewScroll'), 0xa5)
                    m.put(address(b, 'IrqPPUCTRL'), 1)
                m.put(address(b, 'NmiR0'), pointer & 255)
                m.put(address(b, 'NmiR1'), pointer >> 8)
                count = x or 256
                end_y = y if carry else (y + count) & 255
                terminator = (pointer + end_y + 1) & 65535
                m.put(terminator, 0)
                m.put(0x2002, 0x80)
                m.put(0x1fe, 0xff)
                m.put(0x1ff, 0x01)
                name, stop = 'OutputToVRAM', 0x0200
            elif kind == 'palette':
                seed, y, flags = spec
                m.palette = [(seed + i*97) & 255 for i in range(32)]
                for i in range(32):
                    m.put(address(b, 'PnBombPaletteShadow') + i, (i*41+7) & 255)
                name, regs = 'PnPaletteScreenUpdate::Copy', (0, 0, y, flags)
                stop = address(b, name) + 11
            elif kind == 'packet':
                packet, pointer, flags = spec
                for i, value in enumerate(packets[packet]):
                    m.put(pointer + i, value)
                m.put(address(b, 'NmiR0'), pointer & 255)
                m.put(address(b, 'NmiR1'), pointer >> 8)
                m.put(address(b, 'Mirror_PPUCTRL'), packet*11 & 255)
                m.put(0x2002, 0x80)
                m.put(0x1fe, 0xff)
                m.put(0x1ff, 0x01)
                name, stop, regs = 'UpdateScreen', 0x0200, (0x55, 0x37, 0xa5, flags)
            else:
                raise AssertionError(kind)
            result = run(b, m, address(b, name), stop, *regs, irq_after=irq_after)
            if terminator is not None:
                assert m[address(b, 'NmiR0')] + 256*m[address(b, 'NmiR1')] == terminator
            values.append(result)
        before, after = values
        for field in ('state', 'writes', 'reads', 'ram', 'banks'):
            if before[field] != after[field]:
                (a.output / 'failure.json').write_text(json.dumps(dict(
                    passed=False, case=case, kind=kind, spec=spec, field=field)) + '\n')
                raise AssertionError((case, kind, spec, field))
        delta = after['cycles'] - before['cycles']
        assert delta <= 0, (kind, spec, delta)
        g = groups.setdefault(kind, dict(cases=0, cycle_delta_min=delta, cycle_delta_max=delta))
        g['cases'] += 1
        g['cycle_delta_min'] = min(g['cycle_delta_min'], delta)
        g['cycle_delta_max'] = max(g['cycle_delta_max'], delta)
        rows.append(dict(kind=kind, spec=spec, before=before['cycles'], after=after['cycles']))
    raw = a.output / 'cases.json'
    raw.write_text(json.dumps(rows, separators=(',', ':')) + '\n')
    result = dict(passed=True, native_run=False, adoption_qualified=False,
                  parent_ROM_sha256=PARENT, candidate_ROM_sha256=NEW,
                  cases=len(rows), groups=groups, raw_cases_sha256=sha(raw),
                  changed_ROM_bytes=len(changed), allowed_ROM_window=[lo, hi],
                  original_shape_catalog_sha256=CATALOG, tool_sha256=sha(Path(__file__)),
                  genuine_private_label_moves=moved,
                  equality='Full returned AXYP/SP, all final nonstack application RAM, '
                           'ordered nonstack writes and palette reads, mapper banks.',
                  liveness='Both linked continuations are exactly SEC/TYA/ADC R0/STA R0/'
                           'LDA#0/ADC R1/STA R1. A is replaced before read; V is replaced '
                           'before any branch or read. No internal A/V mask is applied to returned state.',
                  limits=__doc__ + ' CPU-only component trial; source/HUD/native acceptance remains separate.')
    (a.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()

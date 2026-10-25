"""Generate audited source helpers mapped onto preserved native NES landmarks.

No emulation or level-stream mutation. All derived coordinates and source
bindings are saved beside the generated include for review.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re

R = Path(__file__).resolve().parents[2]
AUDIT = R / 'build/verification/level-layout-audit-agent'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def native_column(area, col):
    original, source = area['offset'], 0
    for op in area['column_operations']:
        a, b = op['original_columns']
        c, d = op['crossover_columns']
        if col < c:
            return original + col - source
        if c <= col < d:
            assert b - a == d - c, ('Helper anchor lies in an unmapped insertion', area['area'], col, op)
            return a + col - c
        original, source = b, d
    return original + col - source


def properties(value):
    parts = value.split('&&')
    values = {}
    for prop in parts[1:]:
        key, _, val = prop.partition('=')
        if key and key not in values:
            values[key] = val
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    inventory = json.loads((AUDIT / 'xml-inventory.json').read_text())
    align = {a['area']: a for a in json.loads((AUDIT / 'static-column-alignments.json').read_text())}
    early = {(h['area'], h['x_tile'], h['y_tile']): h for h in inventory['helpers'] if h['version'] == 'early' and h['layer'] == 'PICKUPS'}
    records = []
    for h in inventory['helpers']:
        if h['version'] != '2.02' or h['layer'] != 'PICKUPS' or h['area'] not in align:
            continue
        a = align[h['area']]
        p = properties(h['value'])
        assert p['type'] in ('waveHorizontal', 'waveVertical')
        col = native_column(a, h['x_tile'])
        x = col * 16 + 8 + (8 if 'shiftRight' in p else 0)
        match = re.fullmatch(r'(Water|Ground|Underground|Castle)(\d+)', a['original_area'])
        assert match
        kind, number = match.groups()
        pointer = ('Water', 'Ground', 'Underground', 'Castle').index(kind) * 32 + int(number) - 1
        w, level = map(int, h['area'][:3].split('-'))
        old = early.get((h['area'], h['x_tile'], h['y_tile']))
        oldp = properties(old['value']) if old else {}
        # The hosted PICKUPS.charVert filtering omission admits its original
        # six identities; later custom identities are not invented originals.
        gate_early = 0 if old is None else 1 if 'charHorz' in oldp else 4
        gate_hard = 1 if 'charHorz' in p else 2 if 'charVert' in p else 4
        records.append(dict(area=h['area'], source_tile=[h['x_tile'], h['y_tile']],
            source_value=h['value'], native_column=col, native_area=a['original_area'],
            world_level=(w - 1) * 4 + level - 1, pointer=pointer, center_x=x,
            top_y=h['y_tile'] * 16, width_tiles=int(p['width']),
            axis=int(p['type'] == 'waveVertical'), easy_gate=gate_early, hard_gate=gate_hard))
    assert len(records) == 34 and sum(r['easy_gate'] != 0 for r in records) == 31
    fields = [('Key', 'world_level'), ('Area', 'pointer'), ('XLo', 'center_x'),
              ('XHi', 'center_x'), ('Y', 'top_y'), ('Width', 'width_tiles'),
              ('Axis', 'axis'), ('EasyGate', 'easy_gate'), ('HardGate', 'hard_gate')]
    lines = ['; Generated from the complete pre-change level audit. Native geometry is retained.',
             'HELPER_RECORDS = 34', 'HpCharacterMasks:',
             '  .byte 0,3,1,3,3,1,1,1,0,0,1,2,3']
    for label, key in fields:
        values = [(r[key] >> 8 if label == 'XHi' else r[key]) & 255 for r in records]
        lines += [f'HpData{label}:', '  .byte ' + ','.join(str(v) for v in values)]
    # Four mirrored quadrants give 1024 phase bins with only 256 bytes per
    # amplitude. Each entry is explicitly rounded to the nearest NES pixel.
    for label, amplitude in [('Horizontal', 30), ('Vertical', 75)]:
        values = [math.floor(amplitude * math.sin(i * math.pi / 512) + .5) for i in range(256)]
        lines += [f'HpSine{label}:']
        for begin in range(0, 256, 16):
            lines += ['  .byte ' + ','.join(map(str, values[begin:begin + 16]))]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text('\n'.join(lines) + '\n')
    binding = dict(coordinate_policy='Retain current native geometry and translate each helper by the explicit source/native column alignment. Do not import expanded maze/padding columns.',
        records=records, inputs={n: sha(AUDIT / n) for n in ('xml-inventory.json', 'static-column-alignments.json')},
        output_sha256=sha(args.output), phase_units='24-bit turns; horizontal step66754, vertical44503; sample current phase before advancing; offscreen phase holds',
        motion_limit='1024-bin mirrored integer-pixel sine; NES quantization is explicit, not a claim of exact Flash floating-point trajectories.', game_changed=False)
    args.output.with_suffix('.json').write_text(json.dumps(binding, indent=2) + '\n')
    print(json.dumps(dict(records=len(records), bytes=args.output.stat().st_size, binding=str(args.output.with_suffix('.json')))))


if __name__ == '__main__':
    main()

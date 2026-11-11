"""Trace Shatterhand's native movement from an ordinary controller-only opening."""

import argparse
from hashlib import sha256
import json

import trace_steve_shatterhand_donor_1111 as D


PADS = {
    'walk_right': [0] * 4 + [128] * 12 + [0] * 8,
    'walk_left': [0] * 4 + [64] * 12 + [0] * 8,
    'reverse': [128] * 12 + [64] * 12 + [0] * 4,
    'jump_tap': [1] + [0] * 49,
    'jump_hold': [1] * 50,
    'jump_right': [129] * 12 + [1] * 8 + [65] * 8 + [0] * 22,
    'crouch': [32] * 6 + [160] * 6 + [161] * 6 + [1] * 8 + [0] * 32,
    'crouch_from_walk': [128] * 10 + [160] * 6 + [128] * 12 + [0] * 4,
    'down_a_from_idle': [33] * 6 + [0] * 3 + [1] * 12 + [0] * 45,
    'jump_repress': [1] * 4 + [0] * 3 + [1] * 30 + [0] * 22,
    'both_directions': [192] * 6 + [128] * 6 + [192] * 6 + [0] * 8,
}
SOURCE = D.ROOT / 'tools/reference/steve_shatterhand_motion_1111.s'
FIELDS = {name: 0x5c90 + i for i, name in enumerate((
    'Pad', 'Pressed', 'State', 'VX', 'VY', 'DX', 'DY', 'JumpHold', 'Facing', 'Recovery', 'Drag'))}
ORIGIN = 0x8000
FLOOR = 0x1900


def link(origin=ORIGIN):
    import sys
    sys.path.insert(0, str(D.ROOT / 'tools/reference'))
    from sonic_sms_compact_cold_worker_1110 import assemble

    aliases = ''.join(f'SteveMove{name} = ${at:04x}\n' for name, at in FIELDS.items())
    return assemble(aliases + SOURCE.read_text(), {'MOTION': (origin, 512)})


def signed(value):
    return value - 256 if value >= 128 else value


def position(bus, at):
    return bus[at] | bus[at + 1] << 8


def trace(seed, program, pads, *, debug=False):
    cpu = D.fork(seed)
    bus = cpu.memory
    image = program['images']['MOTION']
    worker = D.NesMPU(memory=[0] * 65536)
    worker.memory[ORIGIN:ORIGIN+len(image)] = image
    entry, finish = (program['symbols'][name] for name in ('SteveMotionProject', 'SteveMotionFinish'))
    initial = x, y = position(bus, 0x80), position(bus, 0x82)
    assert y == FLOOR and (bus[0x5a2], bus[0x35], bus[0x5ad], bus[0x5ae]) == (0, 0, 0, 0)
    worker.memory[FIELDS['Facing']] = bus[0x5b2] & 128
    rows = []
    for update, pad in enumerate(pads, 1):
        ingress = []

        def observe(original):
            if bus.code_key(original.pc) == (12, 0x94e7):
                ingress.append((bus[0x06], bus[0x04]))

        D.frame(cpu, pad, observe)
        assert len(ingress) == 1, (update, ingress)
        worker.memory[FIELDS['Pad']], worker.memory[FIELDS['Pressed']] = ingress[0]
        D.run(worker, entry, 0)
        x += signed(worker.memory[FIELDS['DX']])
        dy = signed(worker.memory[FIELDS['DY']])
        landed = dy > 0 and y + dy >= FLOOR
        y = min(FLOOR, y + dy)
        worker.p = (worker.p & ~worker.CARRY) | int(landed)
        D.run(worker, finish, 0)
        expected = (position(bus, 0x80), position(bus, 0x82), bus[0x5a2], signed(bus[0x35]),
                    signed(bus[0x5ad]), bus[0x5b2] & 128)
        fields = tuple(worker.memory[FIELDS[name]] for name in ('State', 'VX', 'VY', 'Facing'))
        actual = x, y, fields[0], signed(fields[1]), signed(fields[2]), fields[3]
        if debug:
            print(update, pad, ingress, expected, actual, bus[0x5a4], bus[0x5b5], flush=True)
        assert actual == expected, (update, pad, ingress, actual, expected)
        rows.append(actual)
    return initial, rows


def summary(initial, rows):
    x, y = initial
    apex = max(y - row[1] for row in rows)
    return {
        'updates': len(rows),
        'net_X_Q4': rows[-1][0] - x,
        'peak_abs_VX_Q4': max(abs(row[3]) for row in rows),
        'apex_Q4': apex,
        'apex_update': next(i for i, row in enumerate(rows, 1) if y - row[1] == apex) if apex else None,
        'state_changes': [(i, row[2]) for i, row in enumerate(rows, 1)
                          if row[2] != (rows[i - 2][2] if i > 1 else 0)],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', choices=PADS)
    args = parser.parse_args()
    program = link()
    seed = D.boot(D.DONOR.read_bytes())
    print('Donor and opening verified', D.PIN, D.hardware_anchors(seed), flush=True)
    summaries = {}
    for name in (args.debug,) if args.debug else PADS:
        initial, rows = trace(seed, program, PADS[name], debug=bool(args.debug))
        summaries[name] = summary(initial, rows)
        print(name, json.dumps(summaries[name]), flush=True)
    code = program['images']['MOTION']
    print(json.dumps({'passed': True, 'donor_sha256': D.PIN, 'installed_sha256': sha256(D.HOST.read_bytes()).hexdigest(),
                      'source_sha256': sha256(SOURCE.read_bytes()).hexdigest(), 'worker_bytes': len(code),
                      'worker_sha256': sha256(code).hexdigest(), 'paired_updates': sum(s['updates'] for s in summaries.values()),
                      'output_files': 0}, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()

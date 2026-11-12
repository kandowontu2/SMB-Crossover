"""Trace lift geometry and metasprites on the pinned Shatterhand cartridge."""

from collections import Counter
import json

import trace_steve_shatterhand_donor_1111 as D


POSES = {0x006c: 64, 0x00ac: 72, 0x00b0: 75, 0x00b4: 74, 0x00b6: 75, 0x00b8: 75,
         0x015e: 87, 0x0160: 87, 0x0162: 87, 0x0164: 87}
ATTACHED = bytes.fromhex('00ff80fe80fe30fe')
DECISIONS = {0x9d10, 0x98dc, 0x9945, 0x99b5, 0x9a08}


def word(bus, low, high=None):
    return bus[low] + 256*bus[low+1 if high is None else high]


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value


def code(raw, bank, at, count):
    start = 16 + bank*8192 + (at & 8191)
    return raw[start:start+count]


def parts(raw, pose, base_attr=0):
    def record(at, count):
        return code(raw, 10 if at < 0xa000 else 11, at, count)

    table = int.from_bytes(record(0x8004, 2), 'little')
    assert table == 0x86df
    page, flags, lo, hi = record(table+4*pose, 4)
    pointer = lo + 256*hi
    geometry = int.from_bytes(record(pointer, 2), 'little')
    count, = record(geometry, 1)
    offsets = record(geometry+1, 2*count)
    tiles = record(pointer+2, 2*count)
    assert 1 <= count <= 7
    result = []
    for dy, dx, tile, attr in zip(offsets[::2], offsets[1::2], tiles[::2], tiles[1::2], strict=True):
        dx = signed(dx, 8)
        result.append((signed(dy, 8), -dx-8 if flags & 64 else dx, tile, attr ^ flags ^ base_attr))
    return page, result


def vector(raw, angle, radius):
    offset = angle & 15
    row = code(raw, 12, 0x9078+radius, 16)
    primary = row[offset]
    other = row[(16-offset) & 15] if offset else row[0]
    if not offset:
        other = 0
    dx, dy = (other, primary) if angle & 16 else (primary, other)
    return (-dx if (angle & 0x30) in (0x10, 0x20) else dx)*4, (-dy if angle & 0x20 else dy)*4


def route(raw, seed, *, left):
    cpu = D.fork(seed)
    bus = cpu.memory
    bus[0x5c4] = 0x25 if left else 0x15
    for i in range(150):
        D.frame(cpu, 64 if left and i == 135 else 0)
    assert bus[0x60c] == (3 if left else 1)
    geometry = 0
    rise_frames = 0
    transitions = []
    radius_counts = Counter()
    pose_counts = Counter()
    sites = []
    player = (0x80, 0x82)
    bot = ((0xac, 0xbc), (0xcc, 0xdc))

    def center(who):
        return tuple(word(bus, a, b) for a, b in bot) if who == 'bot' else tuple(word(bus, a) for a in player)

    for frame in range(100):
        last_state = bus[0x5a2]
        last_player = center('player')
        pad = 32 if frame < 3 else 33 if frame < 56 else 1 if rise_frames < 15 else 3 if left else 0
        entry = None
        render = None
        ordered = []

        def watch(at, value):
            if render is not None and 0x200 <= at < 0x300:
                render[3][at] = value

        def observe(c):
            nonlocal entry, geometry, render
            pc = c.pc
            if render is not None and c.sp == render[0]+2:
                _, pose, relative, writes, base_attr = render
                page, shape = parts(raw, pose+left, base_attr)
                assert page == POSES[pose]
                assert bus[0x43 if pose >= 0x100 else 0x42] == page
                x, y = relative
                expected = {(y+dy, tile, attr, x+dx) for dy, dx, tile, attr in shape}
                actual = {tuple(writes[i+j] for j in range(4)) for i in writes
                          if i & 3 == 0 and all(i+j in writes for j in range(4))}
                assert actual == expected, (left, frame, hex(pose), expected, actual)
                pose_counts[f'{pose:04x}'] += 1
                render = None
            if pc in DECISIONS:
                ordered.append(pc)
            elif pc == 0xa62a and c.x == 12:
                entry = bus[0x61c], center('player'), bus[0x5a2]
                ordered.append(pc)
            elif pc == 0xa6da and c.x == 12 and entry is not None:
                angle, (px, py), state = entry
                radius = bus[0x5af]
                assert not bus[0x5cb] & 128
                diff = (angle-0x30) & 63
                step = 0 if not diff else 1 if diff >= 32 else -1
                new_angle = (angle+step) & 255
                assert bus[0x61c] == new_angle
                pose = word(bus, 0x5a6)
                if (state == 6 or radius < 0x50) and 0xac <= pose < 0x100:
                    at = (pose-0xac)//2
                    dx, dy = 0, signed(int.from_bytes(ATTACHED[at:at+2], 'little'), 16)
                    if bus[0x6cc] == 255:
                        dy -= 8*(bus[0x0c] & 3)
                else:
                    dx, dy = vector(raw, new_angle, radius)
                assert center('bot') == (px+dx, py+dy), (left, frame, state, new_angle, radius, pose)
                assert center('player') == (px, py) and bus[0x68c] == bus[0x5b2]
                radius_counts[f'{radius:02x}'] += 1
                geometry += 1
                ordered.append(pc)
            if pc == 0xc003 and bus[0x5a2] in (4, 5, 6, 7):
                for who, pose in (('player', word(bus, 0x5a6)), ('bot', word(bus, 0x66c, 0x67c))):
                    rx, ry = ((value-word(bus, at)) & 65535 for value, at in zip(center(who), (0x30, 0x32), strict=True))
                    if pose in POSES and c.a+256*c.y == pose+left and (word(bus, 0x90), word(bus, 0x92)) == (rx, ry):
                        render = c.sp, pose, (rx>>4, ry>>4), {}, bus[0x9e]
                        break

        bus.watch = watch
        D.frame(cpu, pad, observe)
        assert render is None
        state = bus[0x5a2]
        if state in (4, 5, 6, 7):
            assert len(ordered) == 3 and ordered[1:] == [0xa62a, 0xa6da], ordered
        if state != last_state:
            transitions.append((frame, state, bus[0x61c], bus[0x5af], center('player'), center('bot')))
        if state == last_state == 7:
            assert center('player') == (last_player[0], last_player[1]-16)
            assert center('bot') == (last_player[0], last_player[1]-16-28*16)
        if state == 7:
            rise_frames += 1
        if frame in (3, 56, 77, 78, 92):
            sites.append((frame, [f'{pc:04x}' for pc in ordered]))
        if rise_frames == 15 and state == 1:
            if left:
                assert bus[0x65c] & 128 and word(bus, 0x5a6) == 0xb4
                assert center('bot') == (last_player[0]-96, last_player[1]-28*16)
            break
    assert [row[:2] for row in transitions] == [(0, 3), (3, 4), (27 if left else 29, 5), (56, 6), (77, 7), (92, 1)]
    assert rise_frames == 15 and geometry == 89
    assert set(pose_counts) == {f'{p:04x}' for p in POSES if p != 0xb4}
    return dict(checked_geometry_updates=geometry, transitions_q4=transitions, rising_updates=rise_frames-1,
                radius_counts=radius_counts, sprite_comparisons=pose_counts, selected_update_order=sites)


def main():
    raw = D.DONOR.read_bytes()
    assert code(raw, 13, 0xa6bf, len(ATTACHED)) == ATTACHED
    assert code(raw, 12, 0x90f8, 16).hex() == '908f8d8a857f7870675c5145392c1e10'
    sprite_parts = {}
    for pose, page in POSES.items():
        right_page, right = parts(raw, pose)
        left_page, left = parts(raw, pose+1)
        assert right_page == left_page == page
        assert left == [(dy, -dx-8, tile, attr ^ 64) for dy, dx, tile, attr in right]
        sprite_parts[f'{pose:04x}'] = dict(CHR_page=page, right_dy_dx_tile_attr=right)
    seed = D.boot(raw)
    report = dict(donor_SHA256=D.PIN, parts=sprite_parts, attached_table=ATTACHED.hex(),
                  AAA_right=route(raw, seed, left=False), AAB_left=route(raw, seed, left=True))
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()

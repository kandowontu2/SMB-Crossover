"""Compare detached Laserbot burst and segment decisions to Shatterhand USA."""

from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_companion_orbit_1111 as Orbit


SOURCE = Orbit.Donor.ROOT / 'tools/reference/steve_shatterhand_laserbot_1111.s'
ORIGIN, STOP, ORIGINAL_DRAW = 0xca00, 0x5000, 0xc01b
SCALARS = dict(SteveBotX=(0xac, 0xbc), SteveBotY=(0xcc, 0xdc), SteveBotFacing=(0x68c,),
               SteveBotPlayerState=(0x5a2,), SteveBotRoomPolarity=(0x5cb,), SteveBotPad=(0x06,),
               SteveBotClock=(0x0c,), SteveBotShotSound=(0xf1,), SteveBotPose=(0x66c, 0x67c),
               SteveLaserCooldown=(0x69d,), SteveLaserCharge=(0x64d,), SteveLaserGroup=(0x63d,),
               SteveLaserDeltaX=(0x62c, 0x63c), SteveLaserDeltaY=(0x64c, 0x69c),
               SteveLaserCameraX=(0x30, 0x31), SteveLaserCameraY=(0x32, 0x33))
ARRAYS = {f'SteveLaserShot{name}': tuple(range(at, at+11)) for name, at in
          zip(('Type', 'XLo', 'XHi', 'YLo', 'YHi', 'Packed', 'Flags', 'Power'),
              range(0x700, 0x780, 0x10), strict=True)}
ORIGINAL = SCALARS | ARRAYS
SCRATCH = dict(SteveLaserBirthKind=1, SteveLaserRelX=2, SteveLaserRelY=2,
               SteveLaserDrawTile1=1, SteveLaserDrawTile2=1, SteveLaserDrawAttr1=1, SteveLaserDrawAttr2=1)


def link(raw):
    assert sha256(raw).hexdigest() == Orbit.Donor.PIN
    fields, address = {}, 0x6000
    sizes = {name: len(addrs) for name, addrs in ORIGINAL.items()} | SCRATCH
    for name, width in sizes.items():
        fields[name] = address
        address += width
    definitions = ''.join(f'{name}=${value:04x}\n' for name, value in fields.items())
    return Orbit.H.assemble(definitions + SOURCE.read_text(), {'LASERBOT': (ORIGIN, 0x400)}), fields


def call(cpu, pc, x, *, stop_at_draw=False):
    cpu.pc, cpu.x, cpu.y, cpu.p, cpu.sp = pc, x, 0, 0x21, 0xec
    cpu.stPushWord(STOP - 1)
    for _ in range(1024):
        if cpu.pc == STOP:
            assert cpu.sp == 0xec
            return False
        if stop_at_draw and cpu.pc == ORIGINAL_DRAW:
            assert cpu.sp == 0xea
            return True
        assert cpu.memory[cpu.pc], (hex(pc), hex(cpu.pc))
        cpu.step()
    raise AssertionError((hex(pc), hex(cpu.pc)))


class Pair:
    def __init__(self, raw, program, fields):
        self.donor, self.host = MPU(), MPU()
        self.donor.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
        code = program['images']['LASERBOT']
        self.host.memory[ORIGIN:ORIGIN+len(code)] = code
        self.fields, self.symbols = fields, program['symbols']
        assert bytes(self.donor.memory[0xa5a5:0xa5a7]) == b'\x8f\xa9'
        assert bytes(self.donor.memory[0xa9d8:0xa9e3]) == bytes.fromhex('ad9d06f006ce9d064c32aa')
        assert bytes(self.donor.memory[0xb438:0xb445]) == bytes.fromhex('2038b3de6007d005fe6007d010')

    def set(self, name, value, slot=None):
        addresses = ORIGINAL[name]
        if slot is None:
            items = value.to_bytes(len(addresses), 'little') if isinstance(value, int) else value
            start = self.fields[name]
        else:
            addresses = (addresses[slot],)
            items = (value,)
            start = self.fields[name] + slot
        self.host.memory[start:start+len(items)] = items
        for address, byte in zip(addresses, items, strict=True):
            self.donor.memory[address] = byte

    def get(self, name, width=1):
        start = self.fields[name]
        return int.from_bytes(self.host.memory[start:start+width], 'little')

    def compare(self, names, context):
        for name in names:
            start = self.fields[name]
            old = bytes(self.donor.memory[at] for at in ORIGINAL[name])
            new = bytes(self.host.memory[start:start+len(old)])
            assert old == new, (context, name, old.hex(), new.hex())


def weapons(q):
    comparisons = births = packed_left = 0
    for facing, polarity, posture, phase, occupancy in product((0, 128), (0, 128), (0, 3),
                                                               (0, 1, 253), range(3)):
        for name in ORIGINAL:
            q.set(name, 0)
        q.set('SteveBotFacing', facing)
        q.set('SteveBotRoomPolarity', polarity)
        q.set('SteveBotPlayerState', posture)
        if occupancy == 1:
            q.set('SteveLaserGroup', 0xfe)
            q.set('SteveLaserShotType', 0x88, 7)
        if occupancy == 2:
            q.set('SteveLaserShotType', bytes([0x83])*11)
        for tick in range(112):
            clock = (phase+tick)&255
            pad = 64 if 4 <= tick < 90 else 0
            q.set('SteveBotClock', clock)
            q.set('SteveBotPad', pad)
            q.set('SteveBotX', (0xffe2+17*tick)&65535)
            q.set('SteveBotY', (0x0012-19*tick)&65535)
            q.set('SteveBotShotSound', 0)
            if tick % 11 == 0 and occupancy != 2:
                q.set('SteveLaserShotType', 0, tick//11)
            before = q.donor.memory[0x700:0x70b]
            call(q.donor, 0xa9d8, 12)
            call(q.host, q.symbols['SteveLaserBotWeapon'], 0)
            q.compare(ORIGINAL, (facing, polarity, posture, phase, occupancy, tick))
            for i, (previous, actual) in enumerate(zip(before, q.donor.memory[0x700:0x70b], strict=True)):
                if not previous and actual:
                    births += 1
                    packed_left += bool(facing and actual & 0x80 and q.donor.memory[0x750+i] & 0x80)
            comparisons += 1
    assert births and packed_left
    return dict(weapon_updates=comparisons, births=births, mirrored_live_births=packed_left)


def poses(q):
    for address in (0x6bc, 0x6cc, 0x6dc):
        q.donor.memory[address] = 0
    q.set('SteveBotPose', 0)
    postures = [0]*130 + [3]*130 + [0, 3]*8
    for posture in postures:
        q.set('SteveBotPlayerState', posture)
        q.donor.a = 8 if posture == 3 else 7
        call(q.donor, 0x8dee, 12)
        call(q.host, q.symbols['SteveLaserBotPose'], 0)
        q.compare(('SteveBotPose',), posture)
    return dict(pose_updates=len(postures))


def segments(q):
    checked = rendered = 0
    origins = ((0x0008, 0x000e, 0, 0), (0x0ff9, 0x0ff7, 0, 0),
               (0x5510, 0x9018, 0x5015, 0x9019), (0xffe0, 0x0005, 0xff01, 0),
               (0x3001, 0x7009, 0x3002, 0x6007), (0x0120, 0xffff, 0, 0xfffe))
    slot_fields = tuple(ARRAYS)
    for kind, velocity, delay, (x, y, cx, cy) in product((0x83, 0x88, 3, 8), range(256), (1, 2), origins):
        slot = (velocity+delay)%8
        q.set('SteveLaserDeltaX', 0x0013 if velocity & 1 else 0xffe5)
        q.set('SteveLaserDeltaY', 0x0011 if velocity & 2 else 0xffe7)
        q.set('SteveLaserCameraX', cx)
        q.set('SteveLaserCameraY', cy)
        for name, value in zip(slot_fields, (kind, x&255, x>>8, y&255, y>>8, velocity, delay, 0x7f), strict=True):
            q.set(name, value, slot)
        draw = call(q.donor, 0xb199, slot, stop_at_draw=True)
        call(q.host, q.symbols['SteveLaserSegmentTick'], slot)
        q.compare(slot_fields, (kind, velocity, delay, x, y, cx, cy))
        old = q.donor.memory
        px = old[0x710+slot] + 256*old[0x720+slot]
        py = old[0x730+slot] + 256*old[0x740+slot]
        rel_x, rel_y = (px-cx)&65535, (py-cy)&65535
        visible = draw and rel_x < 0x1000 and rel_y < 0x1000
        assert bool(q.host.p & q.host.CARRY) == visible
        if visible:
            assert q.get('SteveLaserRelX', 2) == rel_x == old[0x90]+256*old[0x91]
            assert q.get('SteveLaserRelY', 2) == rel_y == old[0x92]+256*old[0x93]
            expected = old[0x9e], old[0x9f], q.donor.a, q.donor.y
            actual = tuple(q.get(f'SteveLaserDraw{name}') for name in ('Tile1', 'Tile2', 'Attr1', 'Attr2'))
            assert actual == expected, (kind, velocity, delay, actual, expected)
            rendered += 1
        checked += 1
    return dict(projectile_updates=checked, drawable_pairs=rendered)


def main():
    raw = Orbit.Donor.DONOR.read_bytes()
    program, fields = link(raw)
    pair = Pair(raw, program, fields)
    result = poses(pair) | weapons(pair) | segments(pair)
    code = program['images']['LASERBOT']
    print(json.dumps(dict(passed=True, donor=Orbit.Donor.PIN, bytes=len(code),
                          worker_SHA256=sha256(code).hexdigest(), output_files=0, **result)), flush=True)


if __name__ == '__main__':
    main()

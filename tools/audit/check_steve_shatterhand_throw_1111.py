"""Compare the detached throw core to original Shatterhand CPU updates."""

from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_companion_orbit_1111 as Orbit
import check_steve_shatterhand_lift_1111 as Lift


D = Orbit.Donor
SOURCE = D.ROOT / 'tools/reference/steve_shatterhand_throw_1111.s'
ORIGIN, STOP = 0xd000, 0x5000
ORIGINAL = {
    'SteveBotActor': (0x60c,), 'SteveBotAngle': (0x61c,), 'SteveBotAge': (0x6ec,),
    'SteveBotFacing': (0x68c,), 'SteveBotClock': (0x0c,), 'SteveBotX': (0xac, 0xbc),
    'SteveBotY': (0xcc, 0xdc), 'SteveBotPlayerX': (0x80, 0x81), 'SteveBotPlayerY': (0x82, 0x83),
    'SteveBotPose': (0x66c, 0x67c), 'SteveLiftBotAnim': (0x6bc,), 'SteveLiftBotDelay': (0x6cc,),
    'SteveLiftBotStep': (0x6dc,), 'SteveThrowSelector': (0x65c,), 'SteveThrowTimer': (0x62c,),
    'SteveThrowSpeed': (0x63c,), 'SteveThrowAux': (0x64c,), 'SteveThrowAim': (0x69c,),
    'SteveThrowAnimAux': (0x6ac,), 'SteveThrowSound': (0xf1,),
    'SteveThrowCameraX': (0x30, 0x31), 'SteveThrowCameraY': (0x32, 0x33),
}


def link(raw):
    assert sha256(raw).hexdigest() == D.PIN
    fields = {name: 0x6000+address-Orbit.STATE for name, address in Orbit.FIELDS.items()}
    fields.update({f'SteveLift{name}': 0x6100+i for i, name in enumerate(Lift.NAMES)})
    fields['SteveBotPose'] = fields['SteveLiftBotPose']
    throw_fields = [name for name in ORIGINAL if name not in fields] + ['SteveThrowQuadrant']
    at = 0x6150
    for name in throw_fields:
        fields[name] = at
        at += len(ORIGINAL.get(name, (0,)))

    def table(name, data):
        return f'\n{name}: .byte ' + ','.join(map(str, data)) + '\n'

    donor_angles = Orbit.rom_data(raw, 12, 0x8eea)[:256]
    for x, y in product(range(16), repeat=2):
        if max(x, y) >= 8:
            assert donor_angles[16*y+x] + donor_angles[16*x+y] == 16
    angles = bytes((donor_angles[16*y+x] & 15) | ((donor_angles[16*(y+1)+x] & 15) << 4)
                   for x in range(8, 16) for y in range(0, 16, 2))
    bob = Orbit.rom_data(raw, 13, 0xae6b)[:16]
    polar = Orbit.rom_data(raw, 12, 0x9078)[:0x90]
    definitions = 'STEVE_LIFT_LIVE=1\n' + ''.join(f'{name}=${value:04x}\n' for name, value in fields.items())
    source = (definitions + Orbit.SOURCE.read_text() + table('CompanionBob', bob) + table('CompanionPolar', polar)
              + Lift.SOURCE.read_text() + Lift.animation_tables(raw) + SOURCE.read_text()
              + table('SteveThrowAngles', angles))
    result = Orbit.H.assemble(source, {'COMPANION': (0xc500, 0x300), 'LIFT': (0xc900, 0x400),
                                       'THROW': (ORIGIN, 0x500)})
    return result, fields


def call(cpu, entry, x=0):
    cpu.pc, cpu.x, cpu.sp, cpu.p = entry, x, 0xf0, 0x21
    cpu.stPushWord(STOP-1)
    for _ in range(1500):
        if (cpu.pc, cpu.sp) == (STOP, 0xf0):
            return
        assert cpu.memory[cpu.pc], (hex(entry), hex(cpu.pc))
        cpu.step()
    raise AssertionError((hex(entry), hex(cpu.pc)))


class Pair:
    def __init__(self, raw, program, fields):
        self.original, self.host = MPU(), MPU()
        self.original.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
        # The fixture already maps PRG12/13. Natural comparisons run the
        # original fixed-bank mapper wrapper as well.
        self.original.memory[0xc051:0xc056] = bytes.fromhex('84904c548e')
        for segment, origin in (('COMPANION', 0xc500), ('LIFT', 0xc900), ('THROW', ORIGIN)):
            code = program['images'][segment]
            self.host.memory[origin:origin+len(code)] = code
        self.symbols = program['symbols']
        self.fields = fields

    def data(self, memory, name):
        result = bytes(memory[address] for address in ORIGINAL[name])
        if name == 'SteveLiftBotAnim' and result[0] in Lift.SEQUENCES:
            return bytes((Lift.SEQUENCES.index(result[0]),))
        return result

    def load(self, memory):
        for name in ORIGINAL:
            data, start = self.data(memory, name), self.fields[name]
            self.host.memory[start:start+len(data)] = data

    def compare(self, memory, context):
        for name in ORIGINAL:
            data, start = self.data(memory, name), self.fields[name]
            actual = bytes(self.host.memory[start:start+len(data)])
            assert actual == data, (context, name, actual.hex(), data.hex())

    def write(self, memory, name, value):
        addresses = ORIGINAL[name]
        for address, byte in zip(addresses, value.to_bytes(len(addresses), 'little'), strict=True):
            memory[address] = byte


def directions(pair):
    native = pair.original.memory
    deltas = (0, 1, 7, 15, 16, 127, 255, 256, 511, 1023, 4095, 8191)
    deltas += tuple(-value for value in deltas if value)
    count = 0
    for dx, dy in product(deltas, repeat=2):
        px, py = 0x5119, 0x3f55
        bx, by = px+dx, py+dy
        native[0x90:0x98] = px.to_bytes(2, 'little')+py.to_bytes(2, 'little')+bx.to_bytes(2, 'little')+by.to_bytes(2, 'little')
        for name, value in (('PlayerX', px), ('PlayerY', py), ('X', bx), ('Y', by)):
            pair.write(native, 'SteveBot'+name, value)
        pair.load(native)
        call(pair.original, 0x8e5c)
        call(pair.host, pair.symbols['SteveThrowDirection'])
        assert pair.original.a == pair.host.a, (dx, dy, pair.original.a, pair.host.a)
        count += 1
    return count


def contacts(pair):
    native = pair.original.memory
    count = 0
    for facing, kind in product((0, 128), (1, 3)):
        for name in ORIGINAL:
            pair.write(native, name, 0)
        for name, value in (('SteveBotX', 6400), ('SteveBotY', 5600), ('SteveBotPlayerX', 7000),
                            ('SteveBotPlayerY', 6000), ('SteveThrowCameraX', 6000),
                            ('SteveBotActor', 0xc0|kind), ('SteveBotFacing', facing),
                            ('SteveThrowSelector', 128 if kind == 1 else 130),
                            ('SteveThrowTimer', 6), ('SteveThrowSpeed', 160 if facing else 96)):
            pair.write(native, name, value)
        pair.load(native)
        for i in range(2):
            call(pair.original, 0xa740, x=12)
            call(pair.host, pair.symbols['SteveThrowUpdate'])
            pair.compare(native, (facing, kind, i))
            count += 1
    return count


def begins(pair):
    native = pair.original.memory
    fields = ('SteveThrowSelector', 'SteveThrowTimer', 'SteveThrowSpeed', 'SteveThrowSound')
    entries = {5: 0x9965, 6: 0x99e6, 7: 0x9a2c}
    count = 0
    for state, facing, selector in product(entries, (0, 128), (0, 2)):
        for name in ORIGINAL:
            pair.write(native, name, 0)
        pair.write(native, 'SteveThrowSelector', selector)
        pair.write(native, 'SteveBotFacing', facing)
        native[0x5a2], native[0x5b2] = state, facing
        native[0x5a5], native[0x5a4], native[0x5b4] = state+12, 1, 1
        pair.load(native)
        before = {name: pair.host.memory[pair.fields[name]:pair.fields[name]+len(addresses)]
                  for name, addresses in ORIGINAL.items() if name not in fields}
        call(pair.original, entries[state], x=12)
        pair.host.a = state
        call(pair.host, pair.symbols['SteveThrowBegin'])
        assert tuple(pair.host.memory[pair.fields[name]] for name in fields) == tuple(
            native[ORIGINAL[name][0]] for name in fields), (state, facing, selector)
        for name, old in before.items():
            assert pair.host.memory[pair.fields[name]:pair.fields[name]+len(old)] == old, name
        count += 1
    return count


def natural(pair, seed, *, left):
    cpu = D.fork(seed)
    bus = cpu.memory
    bus[0x5c4] = 0x25 if left else 0x15
    for i in range(150):
        D.frame(cpu, 64 if left and i == 135 else 0)
    for i in range(91):
        D.frame(cpu, 32 if i < 3 else 33 if i < 56 else 1)
    assert bus[0x5a2] == 7
    witnessed = []
    for frame in range(310):
        entered = []

        def visit(c):
            if c.x != 12 or bus.code_key(c.pc)[0] != 13:
                return
            if c.pc == 0xa740:
                assert not entered
                entered.append(bus[0x62c])
                pair.load(bus)
                call(pair.host, pair.symbols['SteveThrowUpdate'])
            if c.pc == 0xa523 and entered:
                pair.compare(bus, (left, frame, entered[-1]))
                witnessed.append((frame, entered.pop(), bus[0x62c]))

        D.frame(cpu, 2 if frame == 0 else 0, visit)
        assert not entered
        if not bus[0x65c] & 128:
            break
    result = (len(witnessed), next(f for f, _, new in witnessed if new == 128),
              next(f for f, old, _ in witnessed if old == 255), witnessed[-1][0])
    assert result == ((296, 18, 273, 295) if left else (301, 22, 277, 300)), result
    return result


def main():
    raw = D.DONOR.read_bytes()
    program, fields = link(raw)
    pair = Pair(raw, program, fields)
    compared = directions(pair)
    contact = contacts(pair)
    launches = begins(pair)
    seed = D.boot(raw)
    right = natural(pair, seed, left=False)
    left = natural(pair, seed, left=True)
    worker = program['images']['THROW']
    print(json.dumps(dict(donor=D.PIN, direction_comparisons=compared, contact_updates=contact, launches=launches,
                          AAA_right=right, AAB_left=left, bytes=len(worker), SHA256=sha256(worker).hexdigest(),
                          outputs=0)), flush=True)


if __name__ == '__main__':
    main()

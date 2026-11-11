"""Compare the projected companion orbit against the pinned Shatterhand ROM."""

from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import trace_steve_shatterhand_donor_1111 as Donor
from check_steve_shatterhand_upgrade_transport_1111 import H


SOURCE = Donor.ROOT / 'tools/reference/steve_shatterhand_companion_orbit_1111.s'
ORIGIN = 0xc500
CAPACITY = 0x3c0
STATE = 0xc900
STOP = 0x5000
ORIGINAL = {
    'SteveBotActor': (0x060c,), 'SteveBotAngle': (0x061c,), 'SteveBotAge': (0x06ec,),
    'SteveBotFacing': (0x068c,), 'SteveBotPlayerFacing': (0x05b2,),
    'SteveBotRoomPolarity': (0x05cb,), 'SteveBotClock': (0x0c,), 'SteveBotPad': (0x06,),
    'SteveBotPlayerX': (0x80, 0x81), 'SteveBotPlayerY': (0x82, 0x83),
    'SteveBotX': (0xac, 0xbc), 'SteveBotY': (0xcc, 0xdc),
    'SteveBotVectorX': (0x90, 0x91), 'SteveBotVectorY': (0x92, 0x93),
}
FIELDS = {}
next_field = STATE
for name, original in ORIGINAL.items():
    FIELDS[name] = next_field
    next_field += len(original)
FIELDS['SteveBotRadius'] = next_field


def rom_data(raw, bank, cpu):
    return raw[16+bank*8192+(cpu&0x1fff):16+(bank+1)*8192]


def link(raw, *, fields=FIELDS, origin=ORIGIN, tail='', shot_polar=False):
    assert sha256(raw).hexdigest() == Donor.PIN and FIELDS.keys() <= fields.keys()
    bob = rom_data(raw, 13, 0xae6b)[:16]
    polar = rom_data(raw, 12, 0x90e8)[:32]
    assert len(bob) == 16 and len(polar) == 32
    assert rom_data(raw, 13, 0xadfb)[:6] == bytes((27, 37, 27, 37, 27, 37))
    if shot_polar:
        polar += rom_data(raw, 12, 0x9158)[:16]
    definitions = ''.join(f'{name}=${address:04x}\n' for name, address in fields.items())
    tables = '\n'.join(f'\n{name}:\n    .byte ' + ','.join(map(str, data))
                       for name, data in (('CompanionBob', bob), ('CompanionPolar', polar)))
    return H.assemble(definitions + SOURCE.read_text(encoding='utf-8') + '\n' + tail + tables + '\n',
                      {'COMPANION': (origin, CAPACITY)})


def call(cpu, pc, *, x=12, y=0, p=0x21, before_draw=None):
    cpu.pc, cpu.x, cpu.y, cpu.sp, cpu.p = pc, x, y, 0xec, p
    cpu.stPushWord(STOP - 1)
    start = cpu.processorCycles
    for _ in range(260):
        if cpu.pc == STOP:
            assert cpu.sp == 0xec
            return cpu.processorCycles - start
        if cpu.pc == before_draw:
            assert cpu.sp == 0xea
            return cpu.processorCycles - start
        cpu.step()
    raise AssertionError((hex(pc), hex(cpu.pc)))


def compare(raw, program):
    donor, linked = MPU(), MPU()
    donor.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
    assert bytes(donor.memory[0xad51:0xad54]) == bytes.fromhex('2031ae')
    assert bytes(donor.memory[0x900e:0x9014]) == bytes.fromhex('869448290f18')
    code = program['images']['COMPANION']
    linked.memory[ORIGIN:ORIGIN+len(code)] = code
    run = program['symbols']['SteveCompanionOrbit']
    ranges = [[], []]
    count = 0

    def set_fields(values):
        for name, addresses in ORIGINAL.items():
            data = values.get(name, 0).to_bytes(len(addresses), 'little')
            linked.memory[FIELDS[name]:FIELDS[name]+len(data)] = data
            for address, value in zip(addresses, data, strict=True):
                donor.memory[address] = value

    for angle, time, pad, face, polarity, actor, age in product(
        (*range(64), 127, 128, 255), (0, 1, 30, 31, 32, 33, 254, 255), (0, 1, 2, 3),
        (0, 128), (0, 128), (1, 0x81, 0xc1), (0, 5, 6, 255),
    ):
        # Both sides of byte/page wrap, with nonzero player fractions.
        x = (0x0007, 0x10f9, 0xfff5)[(angle+time) % 3]
        y = (0x0004, 0x1913, 0xfffa)[(angle+age) % 3]
        set_fields(dict(SteveBotActor=actor, SteveBotAngle=angle, SteveBotAge=age,
                        SteveBotPlayerFacing=face, SteveBotRoomPolarity=polarity,
                        SteveBotClock=time, SteveBotPad=pad, SteveBotPlayerX=x, SteveBotPlayerY=y))
        first = call(donor, 0xad51)
        second = call(linked, run, x=7, y=4, p=0x20)
        if not ranges[0]:
            ranges = [[first, first], [second, second]]
        else:
            for values, value in zip(ranges, (first, second), strict=True):
                values[0] = min(values[0], value)
                values[1] = max(values[1], value)
        count += 1
        for name, addresses in ORIGINAL.items():
            actual = bytes(linked.memory[FIELDS[name]:FIELDS[name]+len(addresses)])
            expected = bytes(donor.memory[address] for address in addresses)
            assert actual == expected, (name, angle, time, pad, face, polarity, actor, age, x, y, actual, expected)
    return dict(cases=count, donor_cycles=ranges[0], worker_cycles=ranges[1])


def main():
    raw = Donor.DONOR.read_bytes()
    program = link(raw)
    code = program['images']['COMPANION']
    result = compare(raw, program)
    print(json.dumps(dict(passed=True, donor=Donor.PIN, worker_bytes=len(code),
                          worker_SHA256=sha256(code).hexdigest(), **result, output_files=0)), flush=True)


if __name__ == '__main__':
    main()

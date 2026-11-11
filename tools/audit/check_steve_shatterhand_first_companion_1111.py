"""Compare the first Shatterhand companion's real attack and shot projection."""

from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_companion_orbit_1111 as Orbit


SOURCE = Orbit.Donor.ROOT / 'tools/reference/steve_shatterhand_first_companion_1111.s'
ORIGINAL = {
    'SteveBotPressed': (0x04,), 'SteveBotPlayerState': (0x05a2,),
    'SteveBotAnim': (0x06ac,), 'SteveBotAnimStep': (0x06dc,), 'SteveBotAnimDelay': (0x06cc,),
    'SteveBotPose': (0x066c, 0x067c), 'SteveBotShotType': (0x0700,), 'SteveBotShotTimer': (0x0750,),
    'SteveBotShotFlags': (0x0760,), 'SteveBotShotPower': (0x0770,), 'SteveBotShotSound': (0xf1,),
    'SteveBotShotAngle': (0x069c,), 'SteveBotShotSpin': (0x064c,),
    'SteveBotShotX': (0x0710, 0x0720), 'SteveBotShotY': (0x0730, 0x0740),
}
FIELDS = dict(Orbit.FIELDS)
next_field = max(FIELDS.values()) + 1
for name, original in ORIGINAL.items():
    FIELDS[name] = next_field
    next_field += len(original)
assert next_field <= Orbit.STATE + 0x40


def link(raw, *, fields=FIELDS, tail=''):
    return Orbit.link(raw, fields=fields, tail=SOURCE.read_text(encoding='utf-8')+'\n'+tail, shot_polar=True)


def compare(raw, program):
    fields = Orbit.ORIGINAL | ORIGINAL
    donor, host = MPU(), MPU()
    donor.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
    code = program['images']['COMPANION']
    host.memory[Orbit.ORIGIN:Orbit.ORIGIN+len(code)] = code
    symbols = program['symbols']
    assert bytes(donor.memory[0xa957:0xa961]) == bytes.fromhex('bda006f005a0014cc08d')
    assert bytes(donor.memory[0xb6ed:0xb6f7]) == bytes.fromhex('a50c2907d004a93485f1')
    assert bytes(donor.memory[0xbe27:0xbe60]) == bytes.fromhex('03bc0203c00203be02')*6 + b'\xff\xbe\x02'

    def set_field(name, value):
        data = value.to_bytes(len(fields[name]), 'little')
        at = FIELDS[name]
        host.memory[at:at+len(data)] = data
        for address, item in zip(fields[name], data, strict=True):
            donor.memory[address] = item

    cases = updates = shots = samples = 0
    for face, polarity, posture, start in product((0, 128), (0, 128), (0, 3), (0, 7, 63, 253)):
        for name in fields:
            set_field(name, 0)
        set_field('SteveBotFacing', face)
        set_field('SteveBotPlayerFacing', face)
        set_field('SteveBotRoomPolarity', polarity)
        set_field('SteveBotPlayerState', posture)
        set_field('SteveBotActor', 1)
        fired = []
        cases += 1
        for tick in range(126):
            set_field('SteveBotClock', (start+tick)&255)
            set_field('SteveBotX', (0xff61+tick*19)&65535)
            set_field('SteveBotY', (0x00b3-tick*17)&65535)
            if tick == 29:
                # The original reflects X on a turn during a live spin.
                set_field('SteveBotPlayerFacing', face ^ 128)
            if donor.memory[0x0700]:
                Orbit.call(donor, 0xb6ed, x=0, before_draw=0xb75f)
                Orbit.call(host, symbols['SteveFirstBotShotUpdate'], x=0)
                samples += 1
            before = donor.memory[0x0700]
            set_field('SteveBotPressed', 64 if tick in (1, 2, 7, 19, 50, 53, 55, 56, 70, 116) else 0)
            Orbit.call(donor, 0xa957)
            Orbit.call(host, symbols['SteveFirstBotWeapon'])
            if donor.memory[0x0700] and not before:
                fired.append(tick)
            for name, addresses in ORIGINAL.items():
                at = FIELDS[name]
                actual = bytes(host.memory[at:at+len(addresses)])
                expected = bytes(donor.memory[address] for address in addresses)
                assert actual == expected, (name, face, polarity, posture, start, tick, actual, expected)
            updates += 1
        assert fired == [1, 56, 116], fired
        shots += len(fired)
    for pose, delay in product((0xbc, 0xbe, 0xc0), (1, 2, 3)):
        for name, value in (('SteveBotShotType', 0x15), ('SteveBotShotTimer', 0),
                            ('SteveBotShotPower', 0), ('SteveBotAnim', 1), ('SteveBotAnimStep', 6),
                            ('SteveBotAnimDelay', delay), ('SteveBotPose', 0x200 | pose)):
            set_field(name, value)
        Orbit.call(donor, 0xb222, x=0)
        Orbit.call(host, symbols['SteveFirstBotShotUpdate'], x=0)
        for name in ('SteveBotShotType', 'SteveBotAnim', 'SteveBotAnimStep', 'SteveBotAnimDelay'):
            assert donor.memory[ORIGINAL[name][0]] == host.memory[FIELDS[name]] == 0, name
    return dict(input_cases=cases, weapon_updates=updates, projectile_updates=samples, births=shots,
                spent_shot_resets=9)


def main():
    raw = Orbit.Donor.DONOR.read_bytes()
    program = link(raw)
    code = program['images']['COMPANION']
    report = compare(raw, program)
    print(json.dumps(dict(passed=True, worker_bytes=len(code), worker_SHA256=sha256(code).hexdigest(),
                          **report, output_files=0)), flush=True)


if __name__ == '__main__':
    main()

"""Compare the detached live-facing throw player worker to Shatterhand USA."""

from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_throw_1111 as Throw
import trace_steve_shatterhand_motion_1111 as Motion


D, Lift, H = Throw.D, Throw.Lift, Throw.Orbit.H
SOURCE = D.ROOT / 'tools/reference/steve_shatterhand_throw_player_1111.s'
LAYOUT = {'THROW_PLAYER_BEGIN': (0xc4a0, 96), 'THROW_PLAYER_TICK': (0xc980, 128),
          'LIFT': (0xd462, 0x31e), 'THROW': (0xd800, 0x30), 'MOTION': (0xdec0, 0x120)}
ENTRIES = {5: 0x9965, 6: 0x99e6, 7: 0x9a2c}
AIR_VY = 0xe0


def animation_tables(raw):
    """Append the original player action rows while preserving existing indices."""
    offsets, records = Lift.animation_tables(raw).strip().splitlines()

    def data(pc, count):
        return Throw.Orbit.rom_data(raw, 12 if pc < 0xa000 else 13, pc)[:count]

    def word(pc):
        return int.from_bytes(data(pc, 2), 'little')

    player = word(0x801c)
    source = tuple(word(player + action*2) for action in (0x14, 0x15))
    assert source == (0xbd3d, 0xbd46)
    rows = b''.join(data(pc, 9) for pc in source)
    assert rows == bytes.fromhex('06b4000ab200ffb20006ac000aae00ffae00')
    end = len(records.partition('.byte ')[2].split(','))
    return f'\n{offsets}, {end}, {end+9}\n{records}, ' + ','.join(map(str, rows)) + '\n'


def motion_source():
    """Keep the original $9C6D bidirectional cap after a recoil exceeds ±22."""
    source = Motion.SOURCE.read_text()
    for old, new in (('    bmi StoreX\n    cmp #22', '    bmi ThrowClampLeft\nThrowClampRight:\n    cmp #22'),
                     ('    bpl StoreX\n    cmp #$ea', '    bpl ThrowClampRight\nThrowClampLeft:\n    cmp #$ea')):
        assert source.count(old) == 1
        source = source.replace(old, new)
    return source


def link(raw):
    assert sha256(raw).hexdigest() == D.PIN
    fields = {f'SteveMove{name}': at for name, at in Motion.FIELDS.items()}
    fields.update({f'SteveLift{name}': at for name, at in Lift.FIELDS.items()})
    fields.update(SteveThrowPlayerAction=0xc977, SteveThrowSelector=0xc969, SteveThrowTimer=0xc96a,
                  SteveThrowSpeed=0xc96b, SteveThrowSound=0xc96f,
                  SteveBotFacing=Throw.Orbit.FIELDS['SteveBotFacing'])
    definitions = ''.join(f'{name} = ${at:04x}\n' for name, at in fields.items())
    throw_launch, marker, _ = Throw.SOURCE.read_text().partition('\nSteveThrowUpdate:')
    assert marker
    source = ('SteveThrowAirVY = $%02x\n' % AIR_VY + definitions + Lift.SOURCE.read_text() +
              animation_tables(raw) + '\n' + throw_launch + '\n' + motion_source() +
              '\n' + SOURCE.read_text())
    return H.assemble(source, LAYOUT), fields


def invoke(cpu, entry, a=0, *, carry=True):
    cpu.pc, cpu.a, cpu.x, cpu.sp, cpu.p = entry, a, 12, 0xf0, 0x20 | carry
    cpu.stPushWord(Throw.STOP-1)
    for _ in range(1500):
        if (cpu.pc, cpu.sp) == (Throw.STOP, 0xf0):
            return bool(cpu.p & cpu.CARRY)
        assert cpu.memory[cpu.pc], (hex(entry), hex(cpu.pc))
        cpu.step()
    raise AssertionError((hex(entry), hex(cpu.pc)))


def fixture(raw, linked, fields, state, facing, selector, pad):
    donor, host = MPU(), MPU()
    d, m = donor.memory, host.memory
    d[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
    # Resolve geometry at the environment seams, leaving the donor's actual
    # projection, steering, action dispatch, and animation code executable.
    d[0xa1a1:0xa1a4] = bytes.fromhex('a98060')  # Ground remains supported.
    for entry in (0xa17f, 0xa1e3, 0xa23f):
        d[entry:entry+3] = bytes.fromhex('a90060')  # Free air on both edges.
    for entry in (0xa343, 0xa362, 0xa3cd, 0xa3f2):
        d[entry] = 0x60  # Unobstructed horizontal projection.
    for segment, (origin, _) in LAYOUT.items():
        code = linked['images'][segment]
        m[origin:origin+len(code)] = code

    for at, value in ((0x05a2, state), (0x05b2, facing), (0x068c, facing), (0x065c, selector),
                      (0x05e8, AIR_VY), (0x05e9, 4), (0x05ea, 6), (0x05ac, 0xff),
                      (0x05b6, 0xf9), (0x05b7, 0xff), (6, pad), (4, 0x40)):
        d[at] = value
    for name, value in dict(SteveLiftState=state, SteveMoveState=state, SteveMoveFacing=facing,
                            SteveThrowSelector=selector, SteveMoveJumpHold=0xff, SteveMoveDX=0xf9,
                            SteveMoveDY=0xf0, SteveMovePad=pad, SteveMovePressed=0x40,
                            SteveBotFacing=facing^0x80, SteveLiftPlayerAnim=state-4,
                            SteveLiftPlayerDelay=5, SteveLiftPlayerStep=2).items():
        m[fields[name]] = value
    return donor, host


def compare(donor, host, fields, context, *, launch=False):
    d, m = donor.memory, host.memory
    mapping = {'SteveMoveState': 0x05a2, 'SteveMoveVX': 0x35,
               'SteveMoveVY': 0x05ad, 'SteveMoveDX': 0x05b6, 'SteveMoveDY': 0x05b8,
               'SteveLiftPlayerDelay': 0x05a4, 'SteveLiftPlayerStep': 0x05b4,
               'SteveLiftPlayerPose': 0x05a6, 'SteveLiftPlayerPoseHigh': 0x05a7,
               'SteveThrowTimer': 0x062c, 'SteveThrowSpeed': 0x063c,
               'SteveThrowSelector': 0x065c, 'SteveThrowSound': 0x00f1}
    if launch:
        mapping['SteveMoveJumpHold'] = 0x05ac
    elif d[0x05a2] == 1:
        assert m[fields['SteveMoveJumpHold']] >= 6 and d[0x05ac] >= 6, context
    for name, at in mapping.items():
        assert m[fields[name]] == d[at], (context, name, hex(m[fields[name]]), hex(d[at]))
    assert m[fields['SteveMoveFacing']] & 0x80 == d[0x05b2] & 0x80, context
    action = {0x14: 7, 0x15: 8, 0: 0x80}[d[0x05a5]]
    assert m[fields['SteveThrowPlayerAction']] == action, (context, action)


def launch(raw, linked, fields, state, facing, selector, pad):
    donor, host = fixture(raw, linked, fields, state, facing, selector, pad)
    symbols = linked['symbols']
    invoke(donor, ENTRIES[state])
    invoke(host, symbols['SteveThrowPlayerBegin'], a=state)
    context = (state, facing, selector, pad)
    compare(donor, host, fields, context, launch=True)
    assert host.memory[fields['SteveLiftState']] == 0
    assert host.memory[fields['SteveBotFacing']] == facing
    invoke(donor, 0x9ab2)
    invoke(host, symbols['SteveMotionFinish'], carry=False)
    compare(donor, host, fields, (*context, 'finish'), launch=True)
    return donor, host


def recovery(raw, linked, fields, state, facing, pad):
    donor, host = launch(raw, linked, fields, state, facing, 0, pad)
    symbols = linked['symbols']
    d, m = donor.memory, host.memory
    native_tick = 0x9c8a if state == 5 else 0xa012
    context = (state, facing, pad)
    pose = m[fields['SteveLiftPlayerPose']]
    poses = []
    for update in range(1, 17):
        d[0x05b6:0x05ba] = bytes(4)
        d[4], d[6] = 0, pad
        m[fields['SteveMovePressed']], m[fields['SteveMovePad']] = 0, pad
        invoke(donor, native_tick)
        assert invoke(host, symbols['SteveThrowPlayerStep']), (*context, update)
        compare(donor, host, fields, (*context, update))
        invoke(donor, 0x9ab2)
        invoke(host, symbols['SteveMotionFinish'], carry=False)
        compare(donor, host, fields, (*context, update, 'finish'))
        current = m[fields['SteveLiftPlayerPose']]
        if current != pose or not d[0x05a5]:
            poses.append((update, current))
            pose = current
    end = 0xae if state == 5 else 0xb2
    assert poses == [(6, end), (16, end)], (context, poses)
    assert m[fields['SteveThrowPlayerAction']] == 0x80
    assert not invoke(host, symbols['SteveThrowPlayerStep'])
    assert m[fields['SteveThrowPlayerAction']] == 0
    if state == 5 and not pad & 4:
        invoke(host, symbols['SteveMotionProject'])
        assert m[fields['SteveMoveState']] == 0
    return len(range(1, 17))


def cancel(raw, linked, fields):
    donor, host = launch(raw, linked, fields, 7, 0, 0, 0)
    invoke(donor, 0xa319)
    host.memory[fields['SteveMoveState']] = donor.memory[0x05a2]
    assert not invoke(host, linked['symbols']['SteveThrowPlayerStep'])
    for name, at in (('SteveThrowPlayerAction', 0x05a5), ('SteveLiftPlayerDelay', 0x05a4),
                     ('SteveLiftPlayerStep', 0x05b4)):
        assert host.memory[fields[name]] == donor.memory[at] == 0
    _, host = launch(raw, linked, fields, 5, 0x80, 0, 4)
    projected = ('SteveMoveState', 'SteveMoveVX', 'SteveMoveVY', 'SteveMoveDX', 'SteveMoveDY')
    before = tuple(host.memory[fields[name]] for name in projected)
    assert not invoke(host, linked['symbols']['SteveThrowPlayerCancel'])
    assert all(host.memory[fields[name]] == 0 for name in
               ('SteveThrowPlayerAction', 'SteveLiftPlayerDelay', 'SteveLiftPlayerStep'))
    assert tuple(host.memory[fields[name]] for name in projected) == before


def main():
    raw = D.DONOR.read_bytes()
    linked, fields = link(raw)
    launch_cases = tuple(product(ENTRIES, (0, 0x80), (0, 2), (0, 1, 2, 3, 0x84)))
    for case in launch_cases:
        launch(raw, linked, fields, *case)
    updates = sum(recovery(raw, linked, fields, *case) for case in product(ENTRIES, (0, 0x80), (0, 4, 0x80)))
    cancel(raw, linked, fields)
    images = {name: code for name, code in linked['images'].items() if name.startswith('THROW_PLAYER_')}
    print(json.dumps(dict(donor=D.PIN, launch_cases=len(launch_cases), recovery_updates=updates,
                          landing_and_scene_cancellation=True,
                          worker_bytes={key: len(code) for key, code in images.items()},
                          added_lift_table_bytes=20, worker_SHA256=sha256(b''.join(images.values())).hexdigest(),
                          outputs=0)), flush=True)


if __name__ == '__main__':
    main()

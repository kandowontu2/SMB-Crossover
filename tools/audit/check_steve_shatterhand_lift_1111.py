"""Compare the detached lift decisions and animation clocks to Shatterhand."""

from hashlib import sha256
from itertools import product
import json

from py65.devices.mpu6502 import MPU

import check_steve_shatterhand_companion_orbit_1111 as Orbit


SOURCE = Orbit.Donor.ROOT / 'tools/reference/steve_shatterhand_lift_1111.s'
ORIGIN, STATE = 0xce00, 0xc950
PLAYER = (0x05b5, 0x05a4, 0x05b4, 0x05a6, 0x05a7)
BOT = (0x06bc, 0x06cc, 0x06dc, 0x066c, 0x067c)
SEQUENCES = (3, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16)
NAMES = ('PlayerAnim', 'PlayerDelay', 'PlayerStep', 'PlayerPose', 'PlayerPoseHigh',
         'BotAnim', 'BotDelay', 'BotStep', 'BotPose', 'BotPoseHigh',
         'State', 'Angle', 'Radius', 'Wait', 'Polarity', 'Bot', 'Supported',
         'CanRise', 'Pad', 'Pressed', 'Clock', 'Sound', 'Delta', 'Throw', 'Temp')
FIELDS = {name: STATE+i for i, name in enumerate(NAMES)}
ENTRIES = {4: 0x98dc, 5: 0x9945, 6: 0x99b5, 7: 0x9a08}


def animation_tables(raw):
    def bank12_13(at, size):
        return Orbit.rom_data(raw, 12 if at < 0xa000 else 13, at)[:size]

    def word(at):
        return int.from_bytes(bank12_13(at, 2), 'little')

    records = bytearray()
    offsets = []
    for index, action in enumerate(SEQUENCES):
        at = word(word(0x801e if index >= 4 else 0x801c) + 2*action)
        offsets.append(len(records))
        for _ in range(8):
            row = bank12_13(at, 3)
            records.extend(row)
            if row[0] in (0, 255):
                break
            at += 3
        else:
            raise AssertionError((action, hex(at)))
    assert offsets == [0, 6, 12, 21, 30, 36, 48]
    return ('\nLiftSequenceOffsets: .byte ' + ','.join(map(str, offsets)) +
            '\nLiftSequences: .byte ' + ','.join(map(str, records)) + '\n')


def link(raw, fields=FIELDS):
    assert sha256(raw).hexdigest() == Orbit.Donor.PIN
    aliases = ''.join(f'SteveLift{name} = ${at:04x}\n' for name, at in fields.items())
    return Orbit.H.assemble(aliases + SOURCE.read_text() + animation_tables(raw),
                            {'LIFT': (ORIGIN, 768)})


def fixture(raw, program, polarity):
    donor, host = MPU(), MPU()
    donor.memory[0x8000:0xc000] = raw[16+12*8192:16+14*8192]
    code = program['images']['LIFT']
    host.memory[ORIGIN:ORIGIN+len(code)] = code
    donor.memory[0xa12f] = donor.memory[0xa260] = 0x60
    donor.memory[0xa1a1:0xa1a4] = [0xa9, 0x80, 0x60]
    donor.memory[0x05cb], host.memory[FIELDS['Polarity']] = polarity, polarity
    donor.memory[0x060c], host.memory[FIELDS['Bot']] = 1, 1
    donor.memory[0x33] = 0x10
    donor.memory[PLAYER[0]] = 0xff
    host.memory[FIELDS['PlayerAnim']] = 0xff
    Orbit.call(donor, 0x9d10)
    Orbit.call(host, program['symbols']['SteveLiftBegin'])
    assert (donor.memory[0x05a2], donor.memory[0x05af], donor.memory[0x05ab]) == (4, 128, 16)
    assert (host.memory[FIELDS['State']], host.memory[FIELDS['Radius']], host.memory[FIELDS['Wait']]) == (4, 128, 16)
    return donor, host


def trial(raw, program, *, polarity, delay, release_down, exit_action):
    original, linked = fixture(raw, program, polarity)
    target = 0x10 if polarity else 0x30
    seen = [4]
    rows = []
    done_at = None
    for frame in range(180):
        actual, native = linked.memory, original.memory
        state = actual[FIELDS['State']]
        angle = target + max(0, delay-frame)
        pad, pressed, bot, support, can_rise = 0x84 if frame < release_down else 0x80, 0, 1, 1, 1
        if exit_action == 'early_release' and frame == 8:
            pad = 0
        if exit_action == 'lost_support' and frame == 12:
            support = 0
        if exit_action == 'throw_latched' and state == 5:
            pressed = 0x40
        if exit_action == 'throw_rising' and state == 7:
            pressed = 0x40
        if state == 7:
            done_at = frame if done_at is None else done_at
            can_rise = int((frame-done_at) % 4 != 3)
            if frame-done_at == 13:
                pad = 0
            if exit_action == 'lost_robot' and frame-done_at == 2:
                bot = 0xff
        clock = (frame+delay) & 255
        for name, number in (('Angle', angle), ('Pad', pad), ('Pressed', pressed), ('Bot', bot),
                             ('Supported', support), ('CanRise', can_rise), ('Clock', clock)):
            actual[FIELDS[name]] = number
        native[0x06], native[0x04], native[0x0c] = pad, pressed, clock
        native[0x061c], native[0x060c] = angle, bot
        native[0xa1a2] = 0x80 if support else 0
        native[0xdc] = 8 if can_rise == bool(polarity) else 32
        native[0x05b8] = 0
        Orbit.call(original, ENTRIES[state])
        Orbit.call(linked, program['symbols']['SteveLiftDecision'])
        new_state = actual[FIELDS['State']]
        throw = actual[FIELDS['Throw']]
        for name, at in (('State', 0x05a2), ('Radius', 0x05af), ('Wait', 0x05ab),
                         ('Sound', 0xf1), ('Delta', 0x05b8)):
            assert native[at] == actual[FIELDS[name]], (name, frame, state, native[at], actual[FIELDS[name]])
        assert bool(native[0x065c] & 128) == bool(throw)
        if not throw:
            for first, addresses in (('PlayerAnim', PLAYER), ('BotAnim', BOT)):
                start = FIELDS[first]
                selector = actual[start]
                expected = SEQUENCES[selector] if selector in range(len(SEQUENCES)) else selector
                assert native[addresses[0]] == expected, (first, frame, state, native[addresses[0]], expected)
                assert tuple(native[at] for at in addresses[1:]) == tuple(actual[start+1:start+5]), (
                    first, frame, state, [native[at] for at in addresses], actual[start:start+5])
        rows.append((new_state, actual[FIELDS['Delta']], throw))
        if new_state != state:
            seen.append(new_state)
        if new_state < 4:
            break
    else:
        raise AssertionError((polarity, delay, release_down, exit_action, seen))
    return rows, seen


def main():
    raw = Orbit.Donor.DONOR.read_bytes()
    program = link(raw)
    cases, updates, climbs = 0, 0, 0
    for polarity, delay, release, action in product(
            (0, 128), (0, 5, 16), (9, 66), ('normal', 'early_release', 'lost_support',
                                            'lost_robot', 'throw_latched', 'throw_rising')):
        rows, seen = trial(raw, program, polarity=polarity, delay=delay,
                           release_down=release, exit_action=action)
        if action == 'normal':
            assert seen == [4, 5, 6, 7, 1]
            assert {delta for _, delta, _ in rows} == {0, 16 if polarity else 240}
            climbs += 1
        cases += 1
        updates += len(rows)
    code = program['images']['LIFT']
    print(json.dumps(dict(passed=True, cases=cases, updates=updates, complete_lifts=climbs,
                          worker_bytes=len(code), worker_SHA256=sha256(code).hexdigest(), output_files=0)),
          flush=True)


if __name__ == '__main__':
    main()

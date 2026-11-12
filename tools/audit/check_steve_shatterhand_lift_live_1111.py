"""Mount the donor lift decision and orbit in the native Steve movement path."""

import argparse
import json

import check_steve_shatterhand_companion_live_1111 as Live
import check_steve_shatterhand_laser_live_1111 as Laser
import check_steve_shatterhand_lift_1111 as Donor


ORIGIN = 0xd462
QUALIFIED = '235de3ed2487cd3f93c695e1eb2ceec55c172cede3cb6d98c5309afbc7cfbe38'
BRIDGE = Live.H.ROOT / 'tools/reference/steve_shatterhand_lift_live_1111.s'
MOVE_SYMBOLS = ('SteveMoveState', 'SteveMovePad', 'SteveMoveJumpHold', 'SteveMotionProject',
                'SteveMoveVX', 'SteveMoveVY', 'SteveMoveDX', 'SteveMoveDY')


def bindings(shared, bundle):
    fields = {f'SteveLift{name}': address for name, address in Donor.FIELDS.items()}
    aliases = {'Angle': 'Angle', 'Bot': 'Actor', 'Polarity': 'RoomPolarity', 'Clock': 'Clock', 'Pad': 'Pad'}
    fields.update({f'SteveLift{name}': shared['SteveBot'+alias] for name, alias in aliases.items()})
    move = Live.Move.link()['symbols']
    fields.update({name: move[name] for name in MOVE_SYMBOLS})
    fields.update({name: Live.W.address(bundle, name) for name in
                   ('Block_Buffer_1', 'Block_Buffer_2', 'MTileAttribute', 'JnHurt')})
    assert fields['Block_Buffer_1'] >> 8 == fields['Block_Buffer_2'] >> 8
    return fields


def source(raw):
    return Donor.SOURCE.read_text() + Donor.animation_tables(raw) + BRIDGE.read_text()


def movement_edits(raw, symbols):
    move = Live.Move.link()
    page = Live.Move.Carrier.PAGE
    origin = Live.Move.Carrier.ORIGIN
    offset = Live.C.CHR + 1024*page
    bridge = move['images']['BRIDGE']
    assert raw[offset:offset+len(bridge)] == bridge
    hook, = [insn['pc'] for insn in move['instructions']
             if insn['segment'] == 'BRIDGE' and insn['op'] == 'JSR'
             and insn['operand'] == move['symbols']['SteveMotionProject']]
    forget = move['symbols']['SteveForgetMotion']
    return ((offset+hook-origin, b'\x20'+move['symbols']['SteveMotionProject'].to_bytes(2, 'little'),
             b'\x20'+symbols['SteveLiftMovement'].to_bytes(2, 'little')),
            (offset+forget-origin, b'\xa9\0\x8d\x8d\x5c',
             b'\x4c'+symbols['SteveLiftForget'].to_bytes(2, 'little')+b'\xea\xea'))


def exercise(candidate, info, *, laser=False):
    if laser:
        m, _, reward = Live.earn_laser(candidate, info)
    else:
        m, reward = Live.natural(candidate, info)
    state = info['lift_fields']['SteveLiftState']
    delay = info['lift_fields']['SteveLiftBotDelay']
    x, start_y = Live.Ingress.Live.player(m)
    assert (x, start_y) == (1740, 48)
    transitions = []
    updates = 0

    def frame(pad):
        nonlocal updates
        m.controller_pad = pad
        Live.C.Game.frame(m)
        updates += 1
        assert Live.Ingress.Live.mode(m) == Live.Ingress.S.PLAY and Live.N.get(m, 'NumberofLives') == 2
        assert Live.Ingress.Live.player(m)[0] == x
        current = Live.resident(m, state)
        if not transitions or transitions[-1][1] != current:
            transitions.append((updates, current))
        return current, Live.Ingress.Live.player(m)[1]

    for _ in range(3):
        frame(4)
    assert m[Live.Move.Motion.FIELDS['State']] == 3
    assert frame(128) == (4, start_y)
    assert frame(0) == (0, start_y)
    for _ in range(3):
        frame(4)
    assert frame(132) == (4, start_y)
    for _ in range(80):
        current, y = frame(132)
        assert current in (4, 5) and y == start_y
        if current == 5 and Live.resident(m, delay) == 0xff:
            break
    else:
        raise AssertionError(('Robot failed to latch', transitions))

    rises = []
    ceiling = None
    for _ in range(85):
        previous = Live.Ingress.Live.player(m)[1]
        current, y = frame(128)
        assert current in (6, 7)
        if current == 6:
            assert y == start_y
        elif y != previous:
            assert y == previous-1
            rises.append(y)
            if y == 45:
                ceiling = ceiling_contact(m, info, x)
    assert rises == list(range(start_y-1, 26, -1)), (rises, transitions)
    assert frame(0) == (0, 27)
    for _ in range(40):
        current, y = frame(0)
        assert current == 0
        if y == start_y and Live.N.get(m, 'Player_State') == 0:
            break
    else:
        raise AssertionError(('Lift release failed to land', y, transitions))
    return dict(robot='Laserbot' if laser else 'Alpha', earned=reward, transitions=transitions,
                rise_updates=len(rises), ceiling=ceiling, landing_y=y, lives=2)


def ceiling_contact(lifting, info, x):
    m = Live.C.Vector.clone(lifting)
    buf = 'Block_Buffer_2' if (x+8) & 256 else 'Block_Buffer_1'
    cell = Live.W.address(m.bundle, buf) + (((x+8) & 255) >> 4)
    solid = 0x52
    state = info['lift_fields']['SteveLiftState']
    assert m[cell] == 0 and m[Live.W.address(m.bundle, 'MTileAttribute')+solid] & 3 == 1
    m[cell] = solid
    positions = []
    for _ in range(5):
        m.controller_pad = 128
        probes = []

        def observe(q, cpu):
            if q.rawtags[2] == 2 and cpu.pc == info['companion_symbols']['LiftReadCell']:
                address = q[6]+256*q[7]+cpu.y
                probes.append((hex(address), q[address]))

        Live.C.Game.frame(m, observe)
        assert m[cell] == solid and Live.resident(m, state) == 7, (
            hex(cell), m[cell], Live.resident(m, state), Live.Ingress.Live.player(m), probes)
        positions.append(Live.Ingress.Live.player(m)[1])
    assert positions == [44]*5, positions
    return dict(stopped_y=positions[-1], preserved_cell=solid, held_updates=len(positions))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--laser', action='store_true')
    args = parser.parse_args()
    raw = Live.DONOR.HOST.read_bytes()
    candidate, info = Laser.proposal(raw, lift=True)
    result = exercise(candidate, info, laser=args.laser)
    print(json.dumps(dict(passed=True, candidate=Live.C.digest(candidate), laser_bytes=len(info['laser_payload']),
                          lift_bytes=len(info['lift_payload']), companion_host_bytes=info['live_bytes'],
                          output_files=0, **result)), flush=True)


if __name__ == '__main__':
    main()

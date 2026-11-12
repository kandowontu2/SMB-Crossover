"""Link physical throw input/recovery into the loaded Steve code, in memory only."""

import argparse
import json

import check_steve_shatterhand_pose_live_1111 as Pose
import check_steve_shatterhand_throw_carrier_1111 as Carrier
import check_steve_shatterhand_throw_player_1111 as Player

Live, C, H = Carrier.Live, Carrier.C, Carrier.H
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_throw_controls_1111.s'


def address(pc):
    if 0xd400 <= pc < 0xd780:
        return C.CHR + 338*1024 + pc-0xd400
    if 0xdc00 <= pc < 0xdfe0:
        return C.CHR + 167*1024 + pc-0xdc00
    raise AssertionError(hex(pc))


def proposal(raw):
    base, info = Pose.proposal(raw)
    assert base == raw
    donor = Live.DONOR.DONOR.read_bytes()
    core, throw_fields = Carrier.live_link(donor, info, data_origin=0xcd88)
    shared = info['companion_symbols']
    move = Live.Move.link()
    fields = shared | info['companion_fields'] | info['lift_fields'] | throw_fields
    fields.update({name: value for name, value in move['symbols'].items() if name.startswith('SteveMove')})
    fields.update(SteveThrowBegin=core['symbols']['SteveThrowBegin'], SteveThrowPlayerAction=0xc977,
                  SteveThrowAirVY=Player.AIR_VY, SteveMotionProject=move['symbols']['SteveMotionProject'])
    table = shared['LiftSequenceOffsets']
    assert shared['LiftSequences'] == table+7 and shared['SteveLiftForget'] == table+64
    layout = {'THROW_PLAYER_BEGIN': (table, 64), 'THROW_PLAYER_TICK': (0xc980, 74),
              'THROW_TABLE': (0xc4a0, 96), 'THROW_ENTRY': (0xde92, 46),
              'THROW_CONTROL': (0xc9ca, 54)}
    definitions = Live.bindings({name: value for name, value in fields.items()
                                if name not in ('LiftSequenceOffsets', 'LiftSequences')})
    source = (definitions + Player.SOURCE.read_text() + '\n' + SOURCE.read_text() +
              '\n.segment "THROW_TABLE"\n' + Player.animation_tables(donor))
    linked = H.assemble(source, layout)
    symbols, images = linked['symbols'], linked['images']
    bridge = (images['THROW_PLAYER_TICK'] + images['THROW_CONTROL'].ljust(54, b'\xea') +
              images['THROW_TABLE'].ljust(96, b'\xea'))
    assert len(bridge) == 224
    edits, resident_edits = [], []

    def edit(pc, old, new):
        at = address(pc)
        assert len(old) == len(new) and raw[at:at+len(old)] == old, (hex(pc), raw[at:at+len(old)].hex(), old.hex())
        edits.append((at, old, new))
        resident_edits.append((pc, old, new))

    old_table = bytes(int(part.strip()) for line in Player.Lift.animation_tables(donor).strip().splitlines()
                      for part in line.partition('.byte ')[2].split(','))
    edit(table, old_table, images['THROW_PLAYER_BEGIN'].ljust(64, b'\xea'))
    edit(0xde92, b'\xea'*46, images['THROW_ENTRY'].ljust(46, b'\xea'))
    # These four absolute indexed operands are inside the original decoder.
    start, end = shared['PlayLiftPlayer'], table
    decoder = raw[address(start):address(end)]
    for old_addr, new_addr, opcode in ((table, 0xc4a0, 0x79),
                                     (table+7, 0xc4a9, 0xb9),
                                     (table+8, 0xc4aa, 0xb9),
                                     (table+9, 0xc4ab, 0xb9)):
        needle = bytes((opcode,)) + old_addr.to_bytes(2, 'little')
        assert decoder.count(needle) == 1
        edit(start+decoder.index(needle)+1, needle[1:], new_addr.to_bytes(2, 'little'))
    edit(shared['SteveLiftMovement'], b'\xad'+fields['SteveUpgradeState'].to_bytes(2, 'little'),
         b'\x4c'+symbols['SteveThrowMovementGate'].to_bytes(2, 'little'))
    edit(shared['DecideLift'], b'\x20'+shared['SteveLiftDecision'].to_bytes(2, 'little')+
         b'\xad'+fields['SteveLiftState'].to_bytes(2, 'little'),
         b'\x4c'+symbols['SteveThrowDecisionGate'].to_bytes(2, 'little')+b'\xea'*3)
    edit(shared['SteveLiftForget'], bytes.fromhex('a9008d'),
         b'\x4c'+symbols['SteveThrowForget'].to_bytes(2, 'little'))
    edit(shared['LiftThrowPressed']+1, fields['SteveLiftPressed'].to_bytes(2, 'little'),
         fields['JnPressed'].to_bytes(2, 'little'))
    for pc, old, new in ((0xdfa1, 0x38, 0x10), (0xdfb1, 0x28, 0xf0)):
        edit(pc, bytes((old,)), bytes((new,)))
    candidate, result = Carrier.mount(raw, info, core['images']['THROW'], core['images']['THROW_DATA'],
                                      pose=True, bridge=bridge, extra_edits=edits)
    return candidate, result | dict(throw_control_link=linked, throw_control_fields=fields,
                                    throw_control_parent=info, throw_core_link=core,
                                    throw_control_edits=resident_edits)


def launch_case(seed, info, entry, facing):
    m = C.Vector.clone(seed)
    fields = info['throw_control_fields']
    state = fields['SteveLiftState']

    def frame(pad):
        m.controller_pad = pad
        C.Game.frame(m)
        assert Live.N.get(m, 'NumberofLives') == 2
        return Live.resident(m, state)

    frame(2 if facing else 1)
    for _ in range(3):
        frame(4)
    for _ in range(90):
        if frame(132) == 5 and Live.resident(m, fields['SteveLiftBotDelay']) == 255:
            break
    else:
        raise AssertionError('No latch')
    if entry >= 6:
        assert frame(128) == 6
    if entry == 7:
        for _ in range(60):
            if frame(128) == 7:
                break
        else:
            raise AssertionError('No rising lift')
    assert Live.resident(m, state) == entry
    frame(196 if entry == 5 else 192)
    values = {name: Live.resident(m, fields[name]) for name in
              ('SteveThrowPlayerAction', 'SteveThrowTimer', 'SteveThrowSpeed', 'SteveMoveState',
               'SteveMoveVX', 'SteveMoveDX', 'SteveLiftPlayerPose', 'SteveLiftState')}
    ground = entry == 5
    action, motion = (8, 3) if ground else (7, 1)
    first_pose, last_pose = (0xac, 0xae) if ground else (0xb4, 0xb2)
    vx = (0x1c if facing else 0xe4) if ground else (0x1f if facing else 0xe1)
    assert values == dict(SteveThrowPlayerAction=action, SteveThrowTimer=3 if ground else 6,
                          SteveThrowSpeed=0xa0 if facing else 0x60, SteveMoveState=motion,
                          SteveMoveVX=vx, SteveMoveDX=0, SteveLiftPlayerPose=first_pose,
                          SteveLiftState=0), (entry, facing, values)
    assert m[fields['JnPressed']] & 64 == 0
    phases = []
    for update in range(17):
        frame(0)
        phases.append([Live.resident(m, fields[name]) for name in
                       ('SteveThrowPlayerAction', 'SteveMoveState', 'SteveLiftPlayerPose')])
    assert all(row[1] == motion for row in phases[:16]), (entry, facing, phases)
    assert phases[5] == [action, motion, last_pose] and phases[15] == [0x80, motion, last_pose], phases
    assert phases[16][:2] == [0, 0 if ground else 1], phases
    return dict(entry=entry, facing=facing, launch=values, recovery=phases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cold-only', action='store_true')
    args = parser.parse_args()
    raw = Live.DONOR.HOST.read_bytes()
    candidate, info = proposal(raw)
    if args.cold_only:
        proof = Carrier.cold_controls(raw, info['throw_control_parent'], candidate, info,
                                      info['pose_worker'], info['throw_core_link'], info['throw_control_fields'],
                                      live_bindings=True, resident_edits=info['throw_control_edits'])
        print(json.dumps(dict(candidate=C.digest(candidate), cold=proof, output_files=0, delivered=False)), flush=True)
        return
    seed, _ = Live.natural(candidate, info)
    cases = [launch_case(seed, info, entry, facing) for entry in (5, 6, 7) for facing in (0, 0x80)]
    print(json.dumps(dict(candidate=C.digest(candidate), cases=cases,
                          linked_bytes={key: len(value) for key, value in info['throw_control_link']['images'].items()},
                          output_files=0, delivered=False)), flush=True)


if __name__ == '__main__':
    main()

"""Link physical throw input/recovery into the loaded Steve code, in memory only."""

import argparse
import json

import check_steve_shatterhand_pose_live_1111 as Pose
import check_steve_shatterhand_throw_carrier_1111 as Carrier
import check_steve_shatterhand_throw_player_1111 as Player

Live, C, H = Carrier.Live, Carrier.C, Carrier.H
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_throw_controls_1111.s'


def address(pc):
    if 0xc500 <= pc < 0xc900:
        return C.CHR + 379*1024 + pc-0xc500
    if 0xca00 <= pc < 0xcd00:
        return C.CHR + 375*1024 + pc-0xca00
    if 0xd000 <= pc < 0xd400:
        return C.CHR + 336*1024 + pc-0xd000
    if 0xd400 <= pc < 0xd780:
        return C.CHR + 338*1024 + pc-0xd400
    if 0xdc00 <= pc < 0xdfe0:
        return C.CHR + 167*1024 + pc-0xdc00
    raise AssertionError(hex(pc))


def proposal(raw, *, graphics=False, flight_storage=False, flight_active=False, combat_storage=False):
    if combat_storage:
        graphics = flight_storage = flight_active = True
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
    flight_link = None
    if flight_active:
        import check_steve_throw_flight_leaf_1111 as Flight

        assert graphics and flight_storage
        link_info = info | dict(throw_control_fields=fields, throw_core_link=core)
        if combat_storage:
            import link_steve_throw_combat_1112 as Combat

            flight_link, _, _ = Combat.link(link_info)
        else:
            flight_link, _ = Flight.link(link_info)
        fields['SteveThrowReset'] = flight_link['symbols']['SteveThrowReset']
    table = shared['LiftSequenceOffsets']
    assert shared['LiftSequences'] == table+7 and shared['SteveLiftForget'] == table+64
    layout = {'THROW_PLAYER_BEGIN': (table, 64), 'THROW_PLAYER_TICK': (0xc980, 74),
              'THROW_TABLE': (0xc4a0, 96), 'THROW_ENTRY': (0xde92, 46),
              'THROW_CONTROL': (0xc9ca, 54)}
    definitions = Live.bindings({name: value for name, value in fields.items()
                                if name not in ('LiftSequenceOffsets', 'LiftSequences')})
    source = (('STEVE_THROW_FLIGHT=1\n' if flight_active else '') + definitions + Player.SOURCE.read_text() + '\n' + SOURCE.read_text() +
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
    if flight_active:
        def jsr(name):
            return b'\x20'+flight_link['symbols'][name].to_bytes(2, 'little')

        facing = Live.W.address(Live.W.Symbols.bundle(), 'PlayerFacingDir')
        prefix = bytes((0xa5, facing)) if facing < 256 else b'\xad'+facing.to_bytes(2, 'little')
        old = prefix+b'\xc9\x02'
        edit(shared['TickUnpaused'], old, jsr('SteveThrowTickPrelude')+b'\xea'*(len(old)-3))
        old = b'\xad'+fields['SteveLiftState'].to_bytes(2, 'little')
        edit(shared['SteveLiftOrbit'], old, b'\x4c'+flight_link['symbols']['SteveThrowOrbit'].to_bytes(2, 'little'))
        for start, end in ((shared['SteveCompanionTick'], shared['FirstBotActive']),
                           (shared['SteveLaserTick'], shared['LaserCueDone'])):
            region = bytes(raw[address(pc)] for pc in range(start, end))
            needle = old+b'\xc9\x04\xb0'
            assert region.count(needle) == 1, (hex(start), region.count(needle))
            edit(start+region.index(needle), needle[:5], jsr('SteveThrowEmissionGate')+b'\xea\xea')
        edit(0xd777, b'\xea'*9, flight_link['images']['THROW_EMISSION'])
        needle = b'\x20'+shared['SteveTokenTick'].to_bytes(2, 'little')
        start, end = shared['SteveCompanionTick'], shared['FirstBotActive']
        region = bytes(raw[address(pc)] for pc in range(start, end))
        assert region.count(needle) == 1
        edit(start+region.index(needle), needle, jsr('SteveThrowGrant'))
    data, tail, pose_info = core['images']['THROW_DATA'], b'', {}
    extension, funding_edit = None, None
    if flight_storage:
        import check_steve_shatterhand_roll_blank_1111 as Roll
        import check_steve_shatterhand_throw_raw3_1111 as Space
        import check_steve_throw_flight_leaf_1111 as Flight

        assert graphics
        funding_edit, _ = Roll.funding(raw)
        assert len(Space.preimage(raw)) == 1024
        flight = flight_link
        if flight is None:
            flight, _ = Flight.link(info | dict(throw_control_fields=fields, throw_core_link=core))
        payload = flight['images']['THROW_FLIGHT']
        if combat_storage:
            payload = b''.join(flight['images'][name] for name, _ in Combat.PARTS)
        extension = dict(page=304, origin=0xab00, payload=payload)
        pose_info.update(throw_combat_storage=combat_storage, throw_extension_used=len(payload))
        pose_info.update(throw_flight_link=flight, throw_flight_active=flight_active)
    if graphics:
        import check_steve_shatterhand_throw_pose_1111 as Render
        from deliver_steve_lift_art_1111 import recover_parent

        worker, renderer = Render.link(info, chr_origin=0xda72 if flight_storage else 0xda71)
        if combat_storage:
            draw_at = renderer['symbols']['SteveLiftDraw']-0xce00
            assert worker[draw_at:draw_at+3] == bytes.fromhex('2c78c9')
            worker = (worker[:draw_at]+b'\x4c'+flight_link['symbols']['SteveDeathDrawMux'].to_bytes(2, 'little')+
                      worker[draw_at+3:])
        art = Render.Art.plan(recover_parent(raw), donor, pose_worker=worker)
        data += Render.records(art)
        tail = renderer['images']['THROW_POSE_CHR']
        assert len(core['images']['THROW'])+(37 if flight_storage else 36)+0xd800 == renderer['symbols']['SteveThrowPoseChr']
        renderedits = Render.rom_edits(raw, info, worker, renderer)
        edits.extend(renderedits)
        draw = shared['SteveCompanionDraw']
        host = Live.Transport
        host_at = C.CHR+1024*host.EXT_PAGE+draw-host.EXT_ORIGIN
        destinations = (0xce00, 0xc8a5, draw+renderedits[2][0]-host_at)
        resident_edits.extend((pc, old, new) for pc, (_, old, new) in zip(destinations, renderedits, strict=True))
        pose_info.update(pose_worker=worker, pose_link=renderer, throw_graphics=True)
    if combat_storage:
        import steve_robot_death_art_funding_1112 as DeathArt

        edits.extend(DeathArt.edits(raw, donor))
    candidate, result = Carrier.mount(raw, info, core['images']['THROW'], data,
                                      pose=True, bridge=bridge, extra_edits=edits, bridge_tail=tail,
                                      extension=extension, funding_edit=funding_edit)
    return candidate, result | dict(throw_control_link=linked, throw_control_fields=fields,
                                    throw_control_parent=info, throw_core_link=core,
                                    throw_control_edits=resident_edits) | pose_info


def launch_case(seed, info, entry, facing):
    m = C.Vector.clone(seed)
    fields = info['throw_control_fields']
    state = fields['SteveLiftState']
    graphics = info.get('throw_graphics', False)
    flight_active = info.get('throw_flight_active', False)
    frame_at = 0xc978
    flight_seen = dict(body_draws=0, hidden_updates=0, reattach_updates=0)
    weapon_entries = {info['companion_symbols'][name] for name in ('SteveFirstBotWeapon', 'SteveLaserBotWeapon')}
    pending, dma_count, poses = None, 0, set()
    if graphics:
        from check_jay_silius_stock_draw_dispatch_1111 import DmaBus

        m.__class__ = DmaBus
    renderer = Live.W.address(m.bundle, 'MetaspriteRenderLoop')

    def frame(pad):
        nonlocal pending, dma_count
        m.controller_pad = pad
        current = None
        if graphics:
            m.dma = None

        def observe(memory, cpu):
            nonlocal current
            if memory.rawtags[2] != 2:
                return
            if flight_active and Live.resident(memory, frame_at):
                assert cpu.pc not in weapon_entries, ('weapon emitted while thrown', hex(cpu.pc))
                if cpu.pc == info['companion_symbols']['DrawCompanionMeta']:
                    assert Live.resident(memory, fields['SteveBotPose']) != 0, 'hidden robot body drawn'
                    flight_seen['body_draws'] += 1
            if not graphics or cpu.pc != renderer:
                return
            if (memory[3], memory[4]) != (0xc0, 0xc8) or not Live.resident(memory, fields['SteveThrowPlayerAction']):
                return
            pose = Live.resident(memory, fields['SteveLiftPlayerPose'])
            poses.add(pose)
            page = 307 if pose in (0xae, 0xb2) else 339
            assert tuple(Live.N.get(memory, name) for name in ('SmChrBank', 'PlayerChrBank')) == (page & 255,)*2
            record = bytes(memory.ram[2][0x8c0:0x8dd])
            x, y = memory[7]+256*memory[8], memory[9]+256*memory[10]
            cells = set()
            for at in range(1, record[0]+1, 4):
                tile, attr, dy, dx = record[at:at+4]
                sx, sy = x+(dx-256 if dx & 128 else dx), y+(dy-256 if dy & 128 else dy)
                if 0 <= sx < 256 and 256 <= sy < 496:
                    cells.add((sy & 255, tile, (attr | memory[6]) & 0xf3, sx))
            assert cells, ('invisible recovery', entry, facing, pose)
            current = cells, page

        C.Game.frame(m, observe)
        if graphics:
            if pending is not None:
                cells, page = pending
                assert m.dma is not None
                actual = {tuple(m.dma[at:at+4]) for at in range(0, 256, 4)}
                assert cells <= actual, ('missing recovery DMA cells', entry, facing, cells-actual)
                assert m.chr_latches[0] == page, ('recovery DMA CHR', entry, facing, page, m.chr_latches[0])
                dma_count += 1
            if Live.resident(m, fields['SteveThrowPlayerAction']):
                assert current is not None, ('recovery bypassed native renderer', entry, facing)
            pending = current
        assert Live.N.get(m, 'NumberofLives') == 2
        if flight_active and Live.resident(m, frame_at):
            if Live.resident(m, fields['SteveBotPose']) == 0:
                flight_seen['hidden_updates'] += 1
            if not Live.resident(m, fields['SteveThrowSelector']) & 128:
                assert Live.resident(m, fields['SteveBotPose']) == 0
                flight_seen['reattach_updates'] += 1
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
    if graphics:
        frame(0)
        assert m.chr_latches[0] == 220, ('ordinary CHR not restored', m.chr_latches[0])
        assert poses == {first_pose, last_pose}, poses
    if flight_active:
        for update in range(600):
            if not Live.resident(m, fields['SteveThrowSelector']) & 128:
                break
            frame(0)
        else:
            raise AssertionError(('throw never returned', entry, facing))
        assert flight_seen['body_draws'] > 0 and flight_seen['hidden_updates'] > 0
        assert flight_seen['reattach_updates'] == 1, flight_seen
        frame(0)
        assert Live.resident(m, frame_at) == 0
    return dict(entry=entry, facing=facing, launch=values, recovery=phases,
                graphics=dict(dma_updates=dma_count, poses=sorted(poses)) if graphics else None,
                flight=flight_seen if flight_active else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cold-only', action='store_true')
    parser.add_argument('--graphics', action='store_true')
    parser.add_argument('--flight-storage', action='store_true')
    parser.add_argument('--flight', action='store_true')
    parser.add_argument('--combat-storage', action='store_true',
                        help='Load combat leaves with live flight; contact dispatch remains unwired.')
    args = parser.parse_args()
    raw = Live.DONOR.HOST.read_bytes()
    candidate, info = proposal(raw, graphics=args.graphics or args.flight_storage or args.flight,
                               flight_storage=args.flight_storage or args.flight, flight_active=args.flight,
                               combat_storage=args.combat_storage)
    if args.cold_only:
        proof = Carrier.cold_controls(raw, info['throw_control_parent'], candidate, info,
                                      info['pose_worker'], info['throw_core_link'], info['throw_control_fields'],
                                      live_bindings=True, resident_edits=info['throw_control_edits'])
        print(json.dumps(dict(candidate=C.digest(candidate), cold=proof,
                              extension_used=info.get('throw_extension_used', 0),
                              combat_storage=info.get('throw_combat_storage', False),
                              output_files=0, delivered=False)), flush=True)
        return
    seed, _ = Live.natural(candidate, info)
    cases = [launch_case(seed, info, entry, facing) for entry in (5, 6, 7) for facing in (0, 0x80)]
    print(json.dumps(dict(candidate=C.digest(candidate), cases=cases,
                          linked_bytes={key: len(value) for key, value in info['throw_control_link']['images'].items()},
                          output_files=0, delivered=False)), flush=True)


if __name__ == '__main__':
    main()

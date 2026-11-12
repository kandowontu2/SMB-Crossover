"""Build the first earned Shatterhand companion and verify the live game route."""

import argparse
import json

import check_steve_shatterhand_companion_transport_1111 as Transport
import check_steve_shatterhand_first_companion_1111 as First
import check_steve_shatterhand_move_live_1111 as Move


Draw, Ingress, C, H, N, W = (Transport.Draw, Transport.Ingress, Transport.C,
                             Transport.H, Transport.N, Transport.W)
SOURCE = H.ROOT / 'tools/reference/steve_shatterhand_companion_live_1111.s'
DONOR = First.Orbit.Donor
CHR_PAGE, CHR_OFFSET = 711, 0x2e0
NATIVE = ('GamePauseStatus', 'GameEngineSubroutine', 'FrameCounter', 'SavedJoypadBits',
          'JnPressed', 'PlayerFacingDir', 'Player_X_Position', 'Player_PageLoc',
          'Player_Y_Position', 'Player_Y_HighPos', 'Player_State', 'ScreenLeft_X_Pos',
          'ScreenLeft_PageLoc', 'Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_Y_HighPos',
          'JnEnemyHurt', 'JnEnemyHP', 'BoundingBox_UL_Corner', 'Square1SoundQueue')


def proposal(raw, *, roll_storage=False, laser=False, lift=False):
    """Build the first companion, or stage the host edits for the late Laserbot loader."""
    bundle = W.Symbols.bundle()
    lifecycle = Ingress.Transport
    private = {name: lifecycle.STATE+i for i, name in enumerate(lifecycle.Upgrade.ALIASES)}
    fields = First.FIELDS | dict(SteveBotActor=private['SteveRobotActor'],
                                 SteveBotAngle=private['SteveRobotAngle'],
                                 SteveBotAge=private['SteveRobotLife'],
                                 SteveBotPlayerFacing=private['SteveUpgradeFacing'])
    fields.update({name: W.address(bundle, name) for name in NATIVE})
    fields.update(SteveBotClock=fields['FrameCounter'], SteveBotPad=fields['SavedJoypadBits'],
                  SteveBotPressed=fields['JnPressed'])
    donor = DONOR.DONOR.read_bytes()
    assert not lift or laser
    core = First.link(donor, fields=fields, lift_polar=lift)
    upgrade = H.assemble(bindings(private) + lifecycle.Upgrade.SOURCE.read_text(),
                         {'UPGRADE': (lifecycle.ORIGIN, lifecycle.STATE-lifecycle.ORIGIN)})
    punch = Ingress.S.link(bundle, movement_entry=0xdc00)['symbols']
    host_symbols = fields | Move.HOST | core['symbols'] | private
    host_symbols.update(SteveTokenTick=upgrade['symbols']['SteveTokenTick'],
                        SteveDrawInvoke=punch['SteveDrawInvoke'],
                        SteveBotDrawPhase=Transport.EXT_STATE,
                        NativeRender=W.address(bundle, 'MetaspriteRenderLoop'),
                        NativeDefeat=W.address(bundle, 'JnDefeat'))
    layout = {'COMPANION_HOST': (Transport.EXT_ORIGIN, Transport.EXT_CAPACITY)}
    if laser:
        import check_steve_shatterhand_laser_live_1111 as Laser

        laser_fields = Laser.fields(host_symbols)
        host_symbols.update(laser_fields)
        layout.update(LASERBOT=(Laser.ORIGIN, Laser.STATE-Laser.ORIGIN))
        options = 'STEVE_LASER_LIVE=1\n'
        source = '\n'.join(path.read_text() for path in (SOURCE, Laser.Core.SOURCE, Laser.BRIDGE))
        if lift:
            import check_steve_shatterhand_lift_live_1111 as Lift

            lift_fields = Lift.bindings(host_symbols, bundle)
            host_symbols.update(lift_fields)
            options += 'STEVE_LIFT_LIVE=1\n'
            source += '\n' + Lift.source(donor)
            layout['LASERBOT'] = Laser.ORIGIN, Lift.ORIGIN-Laser.ORIGIN
            layout['LIFT'] = Lift.ORIGIN, Laser.STATE-Lift.ORIGIN
        host = H.assemble(options + bindings(host_symbols) + source, layout)
        assert len(host['images']['COMPANION_HOST']) <= 0x300
    else:
        host = H.assemble(bindings(host_symbols) + SOURCE.read_text(), layout)
    tick, draw = (host['symbols'][name] for name in ('SteveCompanionTick', 'SteveCompanionDraw'))
    token_image, info = Draw.proposal(raw, companion_tick=tick, companion_draw=draw,
                                     roll_storage=roll_storage)
    donor_chr = DONOR.ShatterhandBus(donor).chr
    art = b''.join(donor_chr[88*1024+start:88*1024+start+32]
                   for start in (0x20, 0x40, 0, 0x60, 0x140, 0x160))
    assert len(art) == 192 and all(any(art[i:i+32]) for i in range(0, 192, 32))
    art_edit = (C.CHR+1024*CHR_PAGE+CHR_OFFSET, bytes(len(art)), art)
    extra_edits = (art_edit,)
    if laser:
        extra_edits += Laser.Art.edits(raw, donor)
    if lift:
        extra_edits += Lift.movement_edits(raw, host['symbols'])
    candidate, info = Transport.mount(token_image, info, core['images']['COMPANION'],
                                     extension=host['images']['COMPANION_HOST'],
                                     extra_edits=extra_edits, funding_source=raw if roll_storage else None)
    info = info | dict(companion_fields=fields | private | {'SteveBotDrawPhase': Transport.EXT_STATE},
                       companion_symbols=host['symbols'] | core['symbols'],
                       live_bytes=len(host['images']['COMPANION_HOST']))
    if laser:
        info.update(laser_payload=host['images']['LASERBOT'], laser_fields=laser_fields)
    if lift:
        info.update(lift_fields=lift_fields, lift_payload=host['images']['LIFT'])
    return candidate, info


def on_nightly(raw, *, laser=False, lift=False):
    if C.digest(raw) == Ingress.PIN:
        return proposal(raw, laser=laser, lift=lift)
    from deliver_sonic_vol2_forms_1111 import recover_parent

    parent = recover_parent(raw)
    steve, info = proposal(parent, roll_storage=True, laser=laser, lift=lift)
    image = bytearray(raw)
    changes = 0
    for offset, (old, new) in enumerate(zip(parent, steve, strict=True)):
        if old != new:
            assert raw[offset] == old, hex(offset)
            image[offset] = new
            changes += 1
    return bytes(image), info | dict(rebased_changes=changes)


def bindings(symbols):
    return ''.join('%s=$%04x\n' % (name, address) for name, address in symbols.items())


def resident(m, at):
    return m.ram[2][at-0xc000] if at >= 0xc000 else m[at]


def native_position(m, fields, x, y):
    def q4(field):
        at = fields[field]
        return resident(m, at) + 256*resident(m, at+1)
    camera = (N.get(m, 'ScreenLeft_PageLoc') << 8) + N.get(m, 'ScreenLeft_X_Pos')
    x = ((q4(x)//16-camera+2048) % 4096)-2048
    raw_y = q4(y)
    y = (raw_y-(65536 if raw_y & 32768 else 0))//16
    return x, y


def sprites(m, tiles):
    oam = bytes(m[0x200:0x300])
    return {tuple(oam[i:i+4]) for i in range(0, 256, 4)
            if oam[i] < 240 and oam[i+1] in tiles}


def natural(candidate, info):
    m, route = Ingress.third_block(candidate, info)
    frame = route['frame']
    fields = info['companion_fields']
    def value(name):
        return resident(m, fields['SteveBot'+name])

    count = fields['SteveTokenCountdown']
    assert value('Actor') == 0 and resident(m, count) > 0x30, (value('Actor'), resident(m, count))
    birth_wait = resident(m, count)-0x30
    for _ in range(birth_wait-1):
        frame(0)
        assert value('Actor') == 0
    frame(0)
    assert value('Actor') == 1 and resident(m, count) == 0x30
    assert resident(m, fields['SteveTokenPattern']) == 0
    x, y = native_position(m, fields, 'SteveBotX', 'SteveBotY')
    assert 8 <= x < 248 and 8 <= y < 240
    expected = {(y-8, 0x71, 1, x-8), (y-8, 0x6f, 1, x)}
    assert expected <= sprites(m, (0x71, 0x6f)), (expected, sprites(m, (0x71, 0x6f)))
    assert m.chr_latches[5] == CHR_PAGE, m.chr_latches
    frame(64)
    assert value('ShotType') == 0x95 and value('ShotTimer') == 51 and not sprites(m, (0x77, 0x79))
    poses = set()
    visible_shot = set()
    draw_phase = value('DrawPhase')
    for expected_timer in range(50, 0, -1):
        frame(64)
        assert value('ShotTimer') == expected_timer and value('ShotType') == 0x95
        x, y = native_position(m, fields, 'SteveBotShotX', 'SteveBotShotY')
        if 8 <= x < 248 and 8 <= y < 240:
            observed = sprites(m, (0x77, 0x79))
            assert (draw_phase ^ value('DrawPhase')) & 1
            tile, palette = (0x77, 1) if value('DrawPhase') & 1 else (0x79, 2)
            expected = {(y-8, tile, palette, x-8), (y-8, tile, palette | 64, x)}
            assert expected <= observed, (expected_timer, expected, observed)
            visible_shot.add(tile)
        draw_phase = value('DrawPhase')
        poses.add(value('Pose'))
    frame(64)
    assert value('ShotTimer') == 0 and value('ShotType') == 0 and not sprites(m, (0x77, 0x79))
    assert visible_shot == {0x77, 0x79} and poses == {0xbc, 0xc0, 0xbe}
    assert N.get(m, 'NumberofLives') == 2
    return m, dict(route=route['third'], birth_wait=birth_wait, draw_poses=sorted(poses),
                   shot_tiles=sorted(visible_shot), uninterrupted_shot_updates=51)


def native_contact(base, info, *, laser=False):
    fields = info['companion_fields']
    entry = info['companion_symbols']['SteveLaserContact' if laser else 'SteveCompanionHit']
    values = (('left outside', 95, 108, 2, 0, False),
              ('right outside', 112, 108, 2, 0, False),
              ('top outside', 100, 99, 2, 0, False),
              ('bottom outside', 100, 117, 2, 0, False),
              ('left and top inclusive', 96, 100, 2, 0, True),
              ('right inside and bottom inclusive', 111, 116, 2, 0, True),
              ('native hurt cooldown', 100, 108, 2, 1, False),
              ('native defeat', 100, 108, 1, 0, True))
    if laser:
        values += (('beam exhausted', 100, 108, 2, 0, True),)
    for name, x, y, hp, cooldown, hit in values:
        m = C.Vector.clone(base)
        m.raw_page(2, 2)
        N.put(m, CurrentBankC=2, ScreenLeft_PageLoc=5, ScreenLeft_X_Pos=252)
        for i in range(6):
            m[fields['Enemy_Flag']+i] = int(i == 0)
        for field, value in (('Enemy_ID', 6), ('Enemy_State', 0), ('Enemy_Y_HighPos', 1),
                             ('JnEnemyHP', hp), ('JnEnemyHurt', cooldown)):
            m[fields[field]] = value
        for i, byte in enumerate((96, 100, 112, 116)):
            m[fields['BoundingBox_UL_Corner']+4+i] = byte
        if laser:
            beam = info['laser_fields']
            for field, number in (('RelX', x*16+7), ('RelY', y*16+9)):
                at = beam['SteveLaser'+field]
                m[at], m[at+1] = number & 255, number >> 8
            power = hp if name == 'beam exhausted' else 0x7f
            shot_type, shot_power, packed = (beam['SteveLaserShot'+part] for part in ('Type', 'Power', 'Packed'))
            m[shot_type], m[shot_power], m[packed] = 0x88, power, 0x74
            Transport.Transport.Upgrade.call(N.NesMPU(memory=m), entry)
            remaining = power - hp*int(hit)
            assert resident(m, shot_power) == remaining, name
            assert resident(m, shot_type) == (0x88 if remaining else 8), name
            assert resident(m, packed) == (0x74 if remaining else 0), name
        else:
            for field, number in (('ShotX', (5*256+252+x)*16+7), ('ShotY', y*16+9)):
                at = fields['SteveBot'+field]
                m[at], m[at+1] = number & 255, number >> 8
            m[fields['SteveBotShotType']] = 0x95
            m[fields['SteveBotShotPower']] = 1
            m[fields['SteveBotShotTimer']] = 30
            Transport.Transport.Upgrade.call(N.NesMPU(memory=m), entry)
            assert resident(m, fields['SteveBotShotType']) == (0x15 if hit else 0x95), name
            assert resident(m, fields['SteveBotShotTimer']) == (0 if hit else 30), name
        if hit and hp == 1:
            assert m[fields['Enemy_State']] & 0x20, name
        else:
            assert m[fields['JnEnemyHP']] == hp-int(hit), name
    return len(values)


def earn_laser(candidate, info):
    model, route = Ingress.third_block(candidate, info, third_beta=True)
    fields = info['companion_fields']
    count = fields['SteveTokenCountdown']
    actor = fields['SteveBotActor']
    wait = resident(model, count)-0x30
    assert wait == 54
    for _ in range(wait):
        assert resident(model, actor) == 0
        route['frame'](0)
    assert resident(model, actor) == 3 and resident(model, count) == 0x30
    assert resident(model, fields['SteveTokenPattern']) == 0
    return model, route, dict(actor=3, birth_wait=wait, route=route['third'])


def laser_grant(candidate, info):
    _, _, result = earn_laser(candidate, info)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--laser-grant', action='store_true')
    args = parser.parse_args()
    raw = DONOR.HOST.read_bytes()
    candidate, info = on_nightly(raw)
    if args.laser_grant:
        print(json.dumps(dict(passed=True, candidate=C.digest(candidate),
                              **laser_grant(candidate, info), output_files=0)), flush=True)
        return
    model, result = natural(candidate, info)
    contacts = native_contact(model, info)
    report = dict(passed=True, candidate=C.digest(candidate),
                          core_bytes=len(info['companion']), host_bytes=info['live_bytes'],
                          native_contact_checks=contacts, **result, output_files=0)
    if 'rebased_changes' in info:
        report['rebased_changes'] = info['rebased_changes']
        report['roll_parity'] = Transport.roll_parity(raw, candidate, extended=True, roll_storage=True)
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()

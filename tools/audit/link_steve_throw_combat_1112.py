"""Link the verified combat leaves to actual fields without modifying a ROM."""
import json
from py65.devices.mpu6502 import MPU
import check_steve_throw_controls_live_1111 as Controls
import check_steve_shatterhand_robot_death_1112 as Death
import check_steve_shatterhand_throw_pose_1111 as Render
import steve_robot_death_art_funding_1112 as DeathArt

Live, H = Controls.Live, Controls.H
PARTS = (
    ('THROW_FLIGHT', 'steve_shatterhand_throw_flight_live_1111.s'),
    ('ROBOT_DEATH', 'steve_shatterhand_robot_death_1112.s'),
    ('ENEMY_RECT', 'steve_throw_enemy_rect_1112.s'),
    ('OVERLAP', 'steve_throw_overlap_1112.s'),
    ('THROW_TARGET', 'steve_throw_target_1112.s'),
    ('THROW_DAMAGE', 'steve_throw_damage_1112.s'),
    ('DEATH_SHOTS', 'steve_robot_clear_shots_1112.s'),
    ('THROW_POINT', 'steve_throw_point_1112.s'),
    ('THROW_CONTACT', 'steve_throw_contact_1112.s'),
    ('THROW_SCAN', 'steve_throw_scan_1112.s'),
    ('DEATH_DRAW', 'steve_robot_death_draw_1112.s'),
    ('DEATH_RECORDS', None),
)


def link(info):
    fields = info['throw_control_fields'] | info['throw_core_link']['symbols'] | info['laser_fields']
    _, renderer = Render.link(info.get('throw_control_parent', info), chr_origin=0xda72)
    fields.update(renderer['symbols'])
    fields['SteveDeathOrdinaryDraw'] = renderer['symbols']['SteveLiftDraw']+3
    for name in ('Enemy_BoundBoxCtrl', 'Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position',
                 'Enemy_Y_HighPos', 'BoundBoxCtrlData', 'PlayerFacingDir', 'ObjectOffset'):
        fields[name] = Live.W.address(Live.W.Symbols.bundle(), name)
    fields.update(SteveThrowFrame=0xc978, SteveDeathDraw=0xc979,
                  SteveDeathPolarity=fields['SteveBotRoomPolarity'], SteveBotHP=fields['SteveRobotArrival'],
                  ThrowPoint=3, ThrowLow=7, ThrowHigh=11, ThrowDelta=0x90, ThrowExtent=0x92)
    source = Live.bindings(fields)+'\n'.join(Death.source(fields) if segment == 'ROBOT_DEATH'
                                           else DeathArt.records_source(Live.DONOR.DONOR.read_bytes()) if segment == 'DEATH_RECORDS'
                                           else (H.ROOT/'tools/reference'/name).read_text()
                                           for segment, name in PARTS)
    # First pass obtains exact instruction lengths; second packs all leaves
    # into the authenticated 1KiB row, without changing zero-page selection.
    layout = {name: (0xa000+index*0x200, 512) for index, (name, _) in enumerate(PARTS)}
    layout['THROW_EMISSION'] = (0xd777, 9)
    first = H.assemble(source, layout)
    cursor = 0xab00
    packed = {}
    for name, _ in PARTS:
        size = len(first['images'][name])
        packed[name] = cursor, size
        cursor += size
    assert cursor <= 0xaf00, hex(cursor)
    record_start, record_size = packed['DEATH_RECORDS']
    assert record_start >> 8 == (record_start+record_size-1) >> 8
    packed['THROW_EMISSION'] = (0xd777, 9)
    result = H.assemble(source, packed)
    return result, fields, cursor


def main():
    _, info = Controls.proposal(Live.DONOR.HOST.read_bytes(), graphics=True)
    linked, fields, end = link(info)
    cpu = MPU()
    for segment, code in linked['images'].items():
        start = linked['symbols']['SteveDeathClearShots'] if segment == 'DEATH_SHOTS' else None
        if start is not None:
            cpu.memory[start:start+len(code)] = code
    arrays = [fields['SteveBotShotType'], fields['SteveBotShotTimer'], fields['SteveBotShotPower']]
    arrays += list(range(fields['SteveLaserShotType'], fields['SteveLaserShotType']+11))
    for address in arrays:
        cpu.memory[address] = 0x95
    cpu.memory[0x92:0x94] = (0xf0, 0xff)
    cpu.pc, cpu.sp = linked['symbols']['SteveDeathClearShots'], 0xf0
    cpu.stPushWord(0x4fff)
    for _ in range(100):
        if cpu.pc == 0x5000:
            break
        cpu.step()
    assert cpu.pc == 0x5000 and cpu.sp == 0xf0
    assert all(cpu.memory[address] == 0 for address in arrays)
    assert cpu.memory[0x92:0x94] == [0xf0, 0xff]
    print(json.dumps(dict(row_used=end-0xab00, row_remaining=0xaf00-end,
                          segment_bytes={name:len(code) for name,code in linked['images'].items()},
                          clear_shots_preserves_death_delta=True, output_files=0, mounted=False)))


if __name__ == '__main__':
    main()

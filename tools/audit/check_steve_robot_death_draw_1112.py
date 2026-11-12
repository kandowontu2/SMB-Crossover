"""Exercise original explosion records through the existing pose builder."""
import json
from itertools import product
import check_steve_throw_controls_live_1111 as Controls
import check_steve_shatterhand_throw_pose_1111 as Render
import check_steve_shatterhand_robot_death_1112 as Death


def main():
    raw = Controls.Live.DONOR.HOST.read_bytes()
    _, info = Controls.proposal(raw, combat_storage=True)
    parent = info['throw_control_parent']
    renderer = info['pose_link']
    fields = info['throw_control_fields'] | renderer['symbols'] | dict(
        SteveThrowFrame=0xc978, SteveDeathDraw=0xc979,
        SteveDeathPolarity=info['throw_control_fields']['SteveBotRoomPolarity'],
        SteveDeathOrdinaryDraw=renderer['symbols']['SteveLiftDraw']+3)
    donor = Controls.Live.DONOR.DONOR.read_bytes()
    graphics = Death.graphics(donor, raw)
    records = []
    mapping = {0x51:0x5f, 0x53:0x61, 0x55:0x77, 0x57:0x79}
    for pose in (0x1dc, 0x1de, 0x1e0, 0x1e2):
        parts = graphics['records_with_hurt_palette'][f'{pose:04x}']
        record = bytes([len(parts)*4]+[value for dy, dx, tile, attr in parts
                                     for value in (mapping[tile], attr, dy & 255, dx & 255)])
        records.append(record)
    data = '.segment "DEATH_RECORDS"\nDeathRecords:\n'
    for index, record in enumerate(records):
        data += f'DeathRecord{index}:\n.byte '+','.join(str(b) for b in record)+'\n'
    data += 'DeathRecordLow:\n.byte <DeathRecord0,<DeathRecord1,<DeathRecord2,<DeathRecord3\n'
    source = (Controls.H.ROOT/'tools/reference/steve_robot_death_draw_1112.s').read_text()
    linked = Controls.H.assemble(Controls.Live.bindings(fields)+source+'\n'+data,
                                 {'DEATH_DRAW': (0xb000, 256), 'DEATH_RECORDS': (0xb100, 64)})
    count = hidden = 0
    for index, facing, polarity, draw in product(range(4), (0, 128), (0, 128), (0, 1)):
        cpu = Render.fixture(parent, info['pose_worker'], renderer)
        m = cpu.memory
        for segment, address in (('DEATH_DRAW', 0xb000), ('DEATH_RECORDS', 0xb100)):
            code = linked['images'][segment]
            m[address:address+len(code)] = code
        for name, value in dict(SteveThrowFrame=0xc0, SteveDeathDraw=draw,
                                SteveBotPose=0xdc+index*2, SteveBotFacing=facing,
                                SteveDeathPolarity=polarity, SteveLaserActive=0).items():
            m[fields[name]] = value
        output = fields['PoseBuffer']+32
        m[output:output+32] = [0xa5]*32
        Render.run(cpu, linked['symbols']['SteveDeathDrawMux'])
        assert cpu.sp == 0xf0 and cpu.p & 1
        if draw:
            expected = bytearray(records[index])
            for offset in range(2, len(expected), 4):
                expected[offset] ^= polarity
            assert bytes(m[output:output+len(expected)]) == expected, (index, facing, polarity)
            count += 1
        else:
            assert m[output:output+32] == [0xa5]*32
            hidden += 1
    retained = 0
    for facing, polarity in product((0, 128), (0, 128)):
        cpu = Render.fixture(parent, info['pose_worker'], renderer)
        m = cpu.memory
        m[0xb000:0xb000+len(linked['images']['DEATH_DRAW'])] = linked['images']['DEATH_DRAW']
        for name, value in dict(SteveThrowFrame=0x80, SteveDeathDraw=1, SteveBotPose=0x5e,
                                SteveBotFacing=facing, SteveDeathPolarity=polarity,
                                SteveLaserActive=0).items():
            m[fields[name]] = value
        output = fields['PoseBuffer']+32
        Render.run(cpu, renderer['symbols']['SteveLiftDraw'])
        size = m[output]+1
        assert size > 1
        expected = bytearray(m[output:output+size])
        for offset in range(2, size, 4):
            expected[offset] ^= 3 | polarity
        m[fields['SteveThrowFrame']] = 0xc0
        Render.run(cpu, linked['symbols']['SteveDeathDrawMux'])
        assert bytes(m[output:output+size]) == expected, (facing, polarity)
        assert cpu.sp == 0xf0 and cpu.p & 1
        retained += 1
    print(json.dumps(dict(explosion_draws=count, hidden_draws=hidden, retained_bodies=retained,
                          bytes={name:len(code) for name,code in linked['images'].items()},
                          mounted=False, output_files=0)))


if __name__ == '__main__':
    main()

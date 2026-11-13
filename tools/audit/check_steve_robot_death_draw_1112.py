"""Exercise original explosion records through the existing pose builder."""
import json
import argparse
from itertools import product
import check_steve_throw_controls_live_1111 as Controls
import check_steve_shatterhand_throw_pose_1111 as Render
import check_steve_shatterhand_robot_death_1112 as Death


def mounted(candidate, info, records, interrupts=False):
    Live, C = Controls.Live, Controls.C
    seed, _ = Live.natural(candidate, info)
    fields = info['throw_control_fields'] | info['laser_fields'] | dict(SteveThrowFrame=0xc978, SteveDeathDraw=0xc979)
    count = hidden = cuts = 0
    for index, facing, polarity, draw in product(range(4), (0, 128), (0, 128), (0, 1)):
        m = C.Vector.clone(seed)
        m.raw_page(1, 3)
        m.raw_page(2, 2)
        Live.N.put(m, CurrentBank=3, CurrentBankC=2, GameEngineSubroutine=8,
                   GuestOamRotationActive=0, CurrentOAMOffset=0)
        cpu = Live.N.NesMPU(memory=m)
        call = Controls.Carrier.Late.Transport.Transport.Upgrade.call
        call(cpu, info['throw_flight_link']['symbols']['SteveDeathClearShots'])
        for name, value in dict(SteveThrowFrame=0xc0, SteveDeathDraw=draw, SteveBotPose=0xdc+index*2,
                                SteveBotFacing=facing, SteveBotRoomPolarity=polarity, SteveLaserActive=0).items():
            m[fields[name]] = value
        m[fields['SteveBotPose']+1] = 1
        camera = Live.N.get(m, 'ScreenLeft_X_Pos')+256*Live.N.get(m, 'ScreenLeft_PageLoc')
        for name, value in (('SteveBotX', ((camera+100)*16) & 65535), ('SteveBotY', 1600)):
            m[fields[name]], m[fields[name]+1] = value & 255, value >> 8
        if interrupts and draw:
            original_step = cpu.step
            def checked_step():
                nonlocal cuts
                if cpu.pc == info['pose_link']['symbols']['BuildPose']:
                    for kind in ('NMI', 'IRQ'):
                        q, branch = C.Vector.clone(m, cpu)
                        branch.step = type(branch).step.__get__(branch, type(branch))
                        before = bytes(q[3:7])
                        assert C.Vector.isr(q, branch, kind) == 'returned'
                        assert bytes(q[3:7]) == before, (kind, hex(cpu.pc), before.hex(), bytes(q[3:7]).hex())
                        cuts += 1
                return original_step()
            cpu.step = checked_step
        call(cpu, info['companion_symbols']['SteveCompanionDraw'])
        record = records[index]
        if draw:
            expected = []
            for at in range(1, len(record), 4):
                tile, attr, dy, dx = record[at:at+4]
                expected.append(((100+(dy if dy < 128 else dy-256)) & 255, tile,
                                 attr ^ polarity, (100+(dx if dx < 128 else dx-256)) & 255))
            expected.reverse()  # Native metasprite renderer walks cells backward.
            actual = [tuple(m[0x200+at:0x204+at]) for at in range(0, len(expected)*4, 4)]
            assert actual == expected, (index, facing, polarity, actual, expected)
            assert Live.N.get(m, 'CurrentOAMOffset') == len(expected)*4
            assert m.chr_latches[5] == 711
            count += 1
        else:
            assert Live.N.get(m, 'CurrentOAMOffset') == 0
            hidden += 1
    print(json.dumps(dict(candidate=C.digest(candidate), native_OAM_draws=count, hidden_draws=hidden,
                          interrupt_cuts=cuts, mounted=True, output_files=0, delivered=False)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mounted', action='store_true')
    parser.add_argument('--interrupts', action='store_true')
    args = parser.parse_args()
    raw = Controls.Live.DONOR.HOST.read_bytes()
    candidate, info = Controls.proposal(raw, combat_storage=True)
    parent = info['throw_control_parent']
    renderer = info['pose_link']
    # The isolated fixture calls its separately linked mux; keep the old
    # worker entry here rather than the mounted candidate's AB00-row jump.
    fixture_worker, _ = Render.link(parent, chr_origin=0xda72)
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
    if args.mounted:
        mounted(candidate, info, records, args.interrupts)
        return
    data = '.segment "DEATH_RECORDS"\nDeathRecords:\n'
    for index, record in enumerate(records):
        data += f'DeathRecord{index}:\n.byte '+','.join(str(b) for b in record)+'\n'
    data += 'DeathRecordLow:\n.byte <DeathRecord0,<DeathRecord1,<DeathRecord2,<DeathRecord3\n'
    source = (Controls.H.ROOT/'tools/reference/steve_robot_death_draw_1112.s').read_text()
    linked = Controls.H.assemble(Controls.Live.bindings(fields)+source+'\n'+data,
                                 {'DEATH_DRAW': (0xb000, 256), 'DEATH_RECORDS': (0xb100, 64)})
    count = hidden = 0
    for index, facing, polarity, draw in product(range(4), (0, 128), (0, 128), (0, 1)):
        cpu = Render.fixture(parent, fixture_worker, renderer)
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
        cpu = Render.fixture(parent, fixture_worker, renderer)
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

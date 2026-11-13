"""Run real companion updates through contact, death, native draw and retirement."""
import json
from itertools import product
import check_steve_throw_controls_live_1111 as Controls

Live, C = Controls.Live, Controls.C


def main():
    candidate, info = Controls.proposal(Live.DONOR.HOST.read_bytes(), combat_active=True)
    seed, _ = Live.natural(candidate, info)
    fields = info['throw_control_fields'] | info['laser_fields'] | dict(SteveDeathDraw=0xc979, SteveThrowFrame=0xc978)
    fields['SteveBotHP'] = fields['SteveRobotArrival']
    bundle = Live.W.Symbols.bundle()
    for name in ('Enemy_X_Position', 'Enemy_PageLoc', 'Enemy_Y_Position', 'Enemy_BoundBoxCtrl'):
        fields[name] = Live.W.address(bundle, name)
    results = []
    for actor, hp, polarity in product((1, 3), (1, 16), (0, 128)):
        m = C.Vector.clone(seed)
        m.raw_page(1, 3)
        m.raw_page(2, 2)
        Live.N.put(m, CurrentBank=3, CurrentBankC=2, GameEngineSubroutine=8,
                   GamePauseStatus=0, GuestOamRotationActive=0, ObjectOffset=0)
        cpu = Live.N.NesMPU(memory=m)
        call = Controls.Carrier.Late.Transport.Transport.Upgrade.call
        call(cpu, info['throw_flight_link']['symbols']['SteveDeathClearShots'])
        values = dict(SteveBotActor=actor, SteveLaserActive=int(actor == 3), SteveBotHP=hp,
                      SteveBotAge=60, SteveUpgradeState=0, SteveArmorTimer=0, SteveTokenCountdown=0,
                      SteveTokenPattern=0, SteveThrowSelector=128, SteveThrowTimer=3,
                      SteveThrowSpeed=0x60, SteveBotRoomPolarity=polarity, SteveBotPressed=0,
                      SteveLiftState=0, SteveThrowPlayerAction=0, SteveThrowSound=0, SteveBotClock=0)
        for name, value in values.items():
            m[fields[name]] = value
        camera = Live.N.get(m, 'ScreenLeft_X_Pos')+256*Live.N.get(m, 'ScreenLeft_PageLoc')
        for name, value in (('SteveBotX', ((camera+100)*16) & 65535), ('SteveBotY', 1600), ('SteveBotPose', 0x15e)):
            m[fields[name]], m[fields[name]+1] = value & 255, value >> 8
        for index in range(6):
            m[fields['Enemy_Flag']+index] = 0
        enemy_x = camera+92
        for name, value in dict(Enemy_Flag=1, Enemy_ID=6, Enemy_State=0, Enemy_Y_HighPos=1,
                                Enemy_X_Position=enemy_x & 255, Enemy_PageLoc=enemy_x >> 8,
                                Enemy_Y_Position=88, Enemy_BoundBoxCtrl=3, JnEnemyHP=6, JnEnemyHurt=0).items():
            m[fields[name]+2] = value
        drawn = 0
        for tick in range(46 if hp == 1 else 2):
            m[fields['SteveBotClock']] = tick
            call(cpu, info['companion_symbols']['SteveCompanionTick'])
            assert m[fields['JnEnemyHP']+2] == 4, (actor, hp, polarity, tick, 'enemy damage')
            Live.N.put(m, CurrentOAMOffset=0)
            call(cpu, info['companion_symbols']['SteveCompanionDraw'])
            visible = Live.N.get(m, 'CurrentOAMOffset') > 0
            drawn += visible
            if hp != 1:
                assert m[fields['SteveBotActor']] == actor
                assert m[fields['SteveBotHP']] == 15 and m[fields['SteveBotAge']] == tick+1
                continue
            assert m[fields['SteveBotAge']] == 0
            assert m[fields['SteveThrowFrame']] == 0xc0
            if not m[fields['SteveBotActor']]:
                assert tick == 44 and not visible, (actor, polarity, tick, visible)
                break
            assert m[fields['SteveBotActor']] == 255
            assert m[fields['SteveLaserActive']] == int(actor == 3)
        if hp == 1:
            assert tick == 44 and drawn == 28, (actor, polarity, tick, drawn)
            call(cpu, info['companion_symbols']['SteveCompanionTick'])
            assert m[fields['SteveThrowFrame']] == 0 and m[fields['SteveLaserActive']] == 0
        results.append(dict(actor=actor, initial_hp=hp, polarity=polarity, updates=tick+1, body_draws=drawn))
    print(json.dumps(dict(candidate=C.digest(candidate), cases=results, row_bytes=info['throw_extension_used'],
                          output_files=0, delivered=False)))


if __name__ == '__main__':
    main()

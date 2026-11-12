"""Execute mounted contact damage, including the real native defeat call."""
import json
import argparse
from itertools import product
import check_steve_throw_controls_live_1111 as Controls

Live, C = Controls.Live, Controls.C


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scan', action='store_true')
    args = parser.parse_args()
    candidate, info = Controls.proposal(Live.DONOR.HOST.read_bytes(), combat_storage=True)
    # Native defeat uses runtime services beyond the cold-loader fixture.
    # Reach an earned robot through the real level route before calling it.
    seed, _ = Live.natural(candidate, info)
    seed.raw_page(1, 3)
    seed.raw_page(2, 2)
    Live.N.put(seed, CurrentBank=3, CurrentBankC=2)
    fields = info['throw_control_fields'] | dict(SteveBotHP=info['throw_control_fields']['SteveRobotArrival'])
    bundle = Live.W.Symbols.bundle()
    for name in ('Enemy_Y_Position', 'Enemy_PageLoc', 'Enemy_X_Position', 'Enemy_BoundBoxCtrl', 'ObjectOffset'):
        fields[name] = Live.W.address(bundle, name)
    symbols = info['throw_flight_link']['symbols']
    count = 0
    for actor, robot_hp, enemy_hp, cooldown in product((1, 3), (1, 16), (1, 2, 6), (0, 7)):
        m = C.Vector.clone(seed)
        cpu = Live.N.NesMPU(memory=m)
        for name, value in dict(SteveBotActor=actor, SteveBotHP=robot_hp, SteveBotAge=60,
                                SteveThrowTimer=3, SteveThrowSound=0, SteveBotAngle=16,
                                SteveUpgradeState=0, SteveArmorTimer=0,
                                SteveThrowSelector=128).items():
            m[fields[name]] = value
        for name, value in (('SteveBotX', 364*16), ('SteveBotY', 188*16), ('SteveBotPose', 0x15e)):
            m[fields[name]], m[fields[name]+1] = value & 255, value >> 8
        Live.N.put(m, ScreenLeft_PageLoc=1, ScreenLeft_X_Pos=0)
        slot = 2
        for index in range(6):
            m[fields['Enemy_Flag']+index] = 0
        for name, value in dict(Enemy_Flag=1, Enemy_ID=6, Enemy_State=0,
                                Enemy_Y_HighPos=1, Enemy_Y_Position=176,
                                Enemy_PageLoc=1, Enemy_X_Position=100,
                                Enemy_BoundBoxCtrl=3, JnEnemyHP=enemy_hp, JnEnemyHurt=cooldown).items():
            m[fields[name]+slot] = value
        Live.N.put(m, ObjectOffset=4 if args.scan else slot)
        scratch = bytes(m[0:15]), m[0x90]
        entry = 'SteveThrowScan' if args.scan else 'SteveThrowContactDamage'
        Controls.Carrier.Late.Transport.Transport.Upgrade.call(cpu, symbols[entry], a=1, x=slot)
        if args.scan:
            assert (bytes(m[0:15]), m[0x90]) == scratch
            assert m[fields['ObjectOffset']] == 4
        expected_actor = 255 if robot_hp == 1 else actor | 192
        assert m[fields['SteveBotActor']] == expected_actor
        assert m[fields['SteveBotHP']] == (robot_hp if robot_hp == 1 else robot_hp-1)
        assert m[fields['SteveBotAge']] == int(args.scan and robot_hp != 1)
        assert m[fields['SteveThrowTimer']] == (32 if robot_hp == 1 else 3)
        assert m[fields['JnEnemyHurt']+slot] == (cooldown or 12)
        killed = cooldown == 0 and enemy_hp <= 2
        if not killed:
            assert m[fields['JnEnemyHP']+slot] == (enemy_hp if cooldown else enemy_hp-2)
        else:
            assert m[fields['Enemy_State']+slot] & 0x20, ('native defeat missing', actor, robot_hp, enemy_hp)
        assert m.rawtags[1:3] == [3, 2], m.rawtags
        count += 1
    guards = 0
    if args.scan:
        for overrides in ({'SteveBotAge': 11}, {'SteveArmorTimer': 1},
                          {'SteveUpgradeState': 13}, {'SteveThrowSelector': 0},
                          {'SteveThrowTimer': 128}, {'SteveThrowTimer': 254},
                          {'SteveBotPoseHigh': 0}, {'SteveBotActor': 0},
                          {'SteveBotActor': 255}, {'SteveBotAge': 255, 'SteveThrowSelector': 0}):
            q = C.Vector.clone(m)
            fields['SteveBotPoseHigh'] = fields['SteveBotPose']+1
            values = dict(SteveBotActor=1, SteveBotHP=16, SteveBotAge=60,
                          SteveArmorTimer=0, SteveUpgradeState=0, SteveThrowSelector=128,
                          SteveThrowTimer=3, SteveBotPoseHigh=1) | overrides
            for name, value in values.items():
                q[fields[name]] = value
            scratch = bytes(q[0:15]), q[0x90], q[fields['ObjectOffset']]
            Controls.Carrier.Late.Transport.Transport.Upgrade.call(
                Live.N.NesMPU(memory=q), symbols['SteveThrowScan'])
            assert q[fields['SteveBotHP']] == 16, overrides
            assert q[fields['SteveBotActor']] == values['SteveBotActor'], overrides
            age = values['SteveBotAge']
            if values['SteveBotActor'] in (1, 3):
                age = min(255, age+1)
            assert q[fields['SteveBotAge']] == age, overrides
            assert (bytes(q[0:15]), q[0x90], q[fields['ObjectOffset']]) == scratch
            guards += 1
    print(json.dumps(dict(candidate=C.digest(candidate), loaded_contacts=count, rejected_contacts=guards,
                          native_defeat_executed=True, scan=args.scan, output_files=0, delivered=False)))


if __name__ == '__main__':
    main()

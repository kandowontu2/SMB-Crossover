"""Execute mounted contact damage, including the real native defeat call."""
import json
from itertools import product
import check_steve_throw_controls_live_1111 as Controls

Live, C = Controls.Live, Controls.C


def main():
    candidate, info = Controls.proposal(Live.DONOR.HOST.read_bytes(), combat_storage=True)
    # Native defeat uses runtime services beyond the cold-loader fixture.
    # Reach an earned robot through the real level route before calling it.
    seed, _ = Live.natural(candidate, info)
    seed.raw_page(1, 3)
    seed.raw_page(2, 2)
    Live.N.put(seed, CurrentBank=3, CurrentBankC=2)
    fields = info['throw_control_fields'] | dict(SteveBotHP=info['throw_control_fields']['SteveRobotArrival'])
    bundle = Live.W.Symbols.bundle()
    for name in ('Enemy_Y_Position', 'Enemy_PageLoc', 'Enemy_X_Position'):
        fields[name] = Live.W.address(bundle, name)
    symbols = info['throw_flight_link']['symbols']
    count = 0
    for actor, robot_hp, enemy_hp, cooldown in product((1, 3), (1, 16), (1, 2, 6), (0, 7)):
        m = C.Vector.clone(seed)
        cpu = Live.N.NesMPU(memory=m)
        for name, value in dict(SteveBotActor=actor, SteveBotHP=robot_hp, SteveBotAge=60,
                                SteveThrowTimer=3, SteveThrowSound=0, SteveBotAngle=16,
                                SteveUpgradeState=0).items():
            m[fields[name]] = value
        slot = 2
        for name, value in dict(Enemy_Flag=1, Enemy_ID=6, Enemy_State=0,
                                Enemy_Y_HighPos=1, Enemy_Y_Position=176,
                                Enemy_PageLoc=1, Enemy_X_Position=100,
                                JnEnemyHP=enemy_hp, JnEnemyHurt=cooldown).items():
            m[fields[name]+slot] = value
        Live.N.put(m, ObjectOffset=slot)
        Controls.Carrier.Late.Transport.Transport.Upgrade.call(cpu, symbols['SteveThrowContactDamage'], a=1, x=slot)
        expected_actor = 255 if robot_hp == 1 else actor | 192
        assert m[fields['SteveBotActor']] == expected_actor
        assert m[fields['SteveBotHP']] == (robot_hp if robot_hp == 1 else robot_hp-1)
        assert m[fields['SteveBotAge']] == 0
        assert m[fields['SteveThrowTimer']] == (32 if robot_hp == 1 else 3)
        assert m[fields['JnEnemyHurt']+slot] == (cooldown or 12)
        killed = cooldown == 0 and enemy_hp <= 2
        if not killed:
            assert m[fields['JnEnemyHP']+slot] == (enemy_hp if cooldown else enemy_hp-2)
        else:
            assert m[fields['Enemy_State']+slot] & 0x20, ('native defeat missing', actor, robot_hp, enemy_hp)
        assert m.rawtags[1:3] == [3, 2], m.rawtags
        count += 1
    print(json.dumps(dict(candidate=C.digest(candidate), loaded_contacts=count,
                          native_defeat_executed=True, output_files=0, delivered=False)))


if __name__ == '__main__':
    main()

"""Directed CPU traces of Sonic's delivered native pickup and injury ABI."""
import argparse
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path

import audit_current_roster_powerups_1110 as Pickup
import check_ff_head_lifetime_irq_1110 as CPU
import check_sonic_native_controller_1110 as Controller
import check_sonic_native_scene_1110 as Scene
import stage_sonic_original_scene_1110 as Stage

PIN = 'd2542ff3c9f78ac26eb7e19d64a7708711bc766515f634b05952bab1be9103f0'
T, N, W = Scene.T, Scene.T.N, CPU.W


def injury(seed):
    traces = []
    points = {0x9771: ('ForceInjury', 254), 0xb660: ('HuInjuryStatus', 207),
              0xd112: ('SonicStatus6', 2), 0xb650: ('HuInjury', 207),
              0xd10f: ('SonicInjury5', 2), 0x97a2: ('NativeCarryBranch', 254),
              0x97a4: ('NativeStatusStore', 254), 0x97d6: ('KillPlayer', 254)}
    for tier in (0, 1, 2):
        for timer in (0, 8):
            mem = CPU.clone(seed)
            mem.raw_page(0, 254)
            N.put(mem, PlayerStatus=tier, InjuryTimer=timer, ObjectOffset=4)
            cpu = N.NesMPU(memory=mem, pc=W.address(mem.bundle, 'InjurePlayer'))
            cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 43, 4, 7, 0x31, 224
            cpu.stPushWord(0x5aff)
            path = []

            def observe(mem, cpu):
                point = points.get(cpu.pc)
                if point and mem.rawtags[(cpu.pc - 0x8000) // 8192] == point[1]:
                    path.append(dict(name=point[0], PC=cpu.pc, A=cpu.a,
                                     X=cpu.x, Y=cpu.y, C=cpu.p & 1))

            CPU.finish(mem, cpu, (0x5b00, 224), observe)
            status = N.get(mem, 'PlayerStatus')
            engine = N.get(mem, 'GameEngineSubroutine')
            if timer:
                assert not path and (engine, status) == (8, tier)
            elif not tier:
                assert path[-1]['name'] == 'KillPlayer' and (engine, status) == (11, 0)
            else:
                assert (engine, status) == (10, 43)
                assert path[-1]['name'] == 'NativeStatusStore'
                assert (path[-1]['A'], path[-1]['C']) == (43, 0)
            traces.append(dict(tier=tier, entry_InjuryTimer=timer, resulting_status=status,
                               resulting_engine=engine, path=path))
    return traces


def native_pickups(seed):
    results = []
    for kind in range(4):
        for state in (0, 5, 6, 128):
            mem = CPU.clone(seed)
            mem[W.address(mem.bundle, 'Enemy_State') + 4] = state
            mem[W.address(mem.bundle, 'PowerUpType') + 4] = kind
            cpu = CPU.call(mem, 'NrPickupCollision', a=0, x=4, y=23, p=0x30)
            assert cpu.p & 1 and (cpu.x, cpu.y) == (4, 23)
        receipt = Pickup.collect(seed, kind)
        collected, resumed = receipt['collected'], receipt['resumed']
        assert not receipt['issues'] and not collected['actor_flag']
        assert receipt['calls']['MarioSourcePowerupCollision'] == 1
        assert 'HuPickup' not in receipt['calls']
        assert receipt['progression_calls'] == (60 if kind < 2 else 0)
        assert collected['floaty'] == (11 if kind == 3 else 6)
        assert collected['StarInvincibleTimer'] == (35 if kind == 2 else 0)
        assert resumed['GameEngineSubroutine'] == 8 and not resumed['GuestPowerupActive']
        results.append(dict(kind=kind, progression=receipt['progression_calls'],
                            stage_return=resumed['GameEngineSubroutine'],
                            star=collected['StarInvincibleTimer'], floaty=collected['floaty'],
                            observed_path=receipt['calls']))
    return dict(direct_maturity_pairs=16, directed_mature_pickups=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert args.output.resolve().is_relative_to(Stage.R / 'build') and not args.output.exists()
    image, program, p, _ = Stage.reconstruct()
    assert sha256(image).hexdigest() == PIN
    mem = T.install(Scene.C.Current.W.bundle(image), p, program)
    T.S.scene(mem, 40, 176)
    N.put(mem, OperMode=1, OperMode_Task=3, DisableScreenFlag=0, Mirror_PPUMASK=30,
          NmiDisable=255, NumberofLives=2, CrossoverBehaviorVersion=1)
    table = p['service']['symbols']['SonicServices']
    T.invoke(mem, table, watch=False)
    veneers = {5: '4c73bd', 6: '4c75bd', 11: '4ce5d0',
               23: '4c71bd', 24: '4c73bd', 33: '4c51bf'}
    for row, expected in veneers.items():
        start = table + 3 * row
        assert bytes(mem[start:start + 3]).hex() == expected
    with redirect_stdout(io.StringIO()):
        opening, gameplay = Controller.run(image, p, goal_x=80)
    assert opening['passed'] and opening['terminal']['lives'] == 2
    result = dict(passed=True, delivered_ROM_SHA256=PIN, output_files=0,
                  current_veneer_bytes=veneers, injury=injury(mem), pickups=native_pickups(gameplay),
                  fixture='Authenticated injury arena and actual menu-to-X80 for pickups. Explicit actor/health fixtures invoke real native code; natural pickups and physical damage are separate.')
    print(json.dumps(result, sort_keys=True), flush=True)
    assert not args.output.exists()


if __name__ == '__main__':
    main()

"""Read-only first Pit negative and finite compiled GameLoop reconstruction.

Never launches an emulator, edits a fixture, or changes a game asset. The CPU
arena reconstructs disclosed scene state; it is not a saved native RAM image.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

EXPECTED = '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
READY = '2f87e9de3a4b404ae4f11febebf50d4b44d74c49dafdd5fbf5c1d502009d9fa0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(b, mode, tier, ex, kind='bow'):
    q = Arena(b, 6)
    q.put(CrossoverBehaviorVersion=mode, PlayerStatus=tier,
          Player_X_Position=112, Player_PageLoc=0, Player_Y_Position=176,
          Player_Y_HighPos=1, Player_State=0, PlayerFacingDir=1,
          Player_MovingDir=1, Player_CollisionBits=255, MmOldX=112,
          ScreenLeft_PageLoc=0, ScreenLeft_X_Pos=0, ScreenRight_PageLoc=0,
          ScreenRight_X_Pos=255, GameEngineSubroutine=8, TimerControl=0,
          AreaType=1, OperMode_Task=3, ScrollLock=1, AreaParserTaskNum=0)
    # Complete ordinary timer/room context, not the CPU helper's zeroed clock.
    # Native screenshot shows 399. No native state snapshot is claimed here.
    q.array('GameTimerDisplay', [3, 9, 9])
    for page in (0, 1):
        for row in (11, 12):
            for col in range(16):
                q.set('Block_Buffer_1', 0x54, page*208 + row*16 + col)
    ey = 168 if kind == 'hammer' else 184
    if kind == 'hammer':
        q.set('Block_Buffer_1', 0x54, 168)
    for n, v in dict(Enemy_Flag=1, Enemy_ID=6, Enemy_State=0,
                     Enemy_X_Position=ex, Enemy_PageLoc=0,
                     Enemy_Y_Position=ey, Enemy_Y_HighPos=1,
                     Enemy_X_Speed=0, Enemy_Y_Speed=0, Enemy_Y_MoveForce=0,
                     Enemy_MovingDir=1, Enemy_BoundBoxCtrl=9,
                     EnemyOffscrBitsMasked=0, Enemy_CollisionBits=0,
                     MmEnemyHealthLo=0, MmEnemyHealthHi=0,
                     MmEnemyFlash=0, RgEnemyStun=0).items():
        q.set(n, v, 0)
    names = ['GameLoop', 'HpProcessFireballsBridge', 'ProcFireball_Bubble',
             'RlWeaponsDispatch', 'LmWeaponsGate', 'JnWeaponsDispatch',
             'M3WeaponsDispatch', 'VvWeaponsDispatch', 'TnWeaponsDispatch',
             'CdWeaponsDispatch', 'KbWeaponsDispatch', 'ExpandedWeapons',
             'ExpandedWeapons::MoveKill', 'MegaManWeapons::DamageEnemy',
             'EnemiesAndLoopsCore']
    owners = {(address(b, n), (location(b, n)-16)//8192): n for n in names}
    path, calls, contact, killed, hp, shots = [], {}, [], [], [], []
    original = NesMPU.step
    update = 0

    def step(c):
        bank = q.m.banks[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
        name = owners.get((c.pc, bank))
        if name:
            calls[name] = calls.get(name, 0) + 1
            if name not in path:
                path.append(name)
            if name == 'MegaManWeapons::DamageEnemy':
                assert c.x == 0
                contact.append(dict(update=update, bank=bank, PC=c.pc,
                                    bullet_type=q.get('MmBulletType'),
                                    x=q.get('MmBulletX'), y=q.get('MmBulletY'),
                                    enemy_x=q.get('Enemy_X_Position'),
                                    enemy_y=q.get('Enemy_Y_Position')))
            if name == 'ExpandedWeapons::MoveKill':
                killed.append(dict(update=update, shot_age=q.get('RgShotAge', c.x),
                                   x=q.get('RgShotX', c.x), y=q.get('RgShotY', c.x)))
        original(c)

    NesMPU.step = step
    try:
        for update in range(1, 111):
            buttons = (64 if 6 <= update < 9 else 0) if kind == 'bow' else (32 if 6 <= update < 10 else 0)
            q.put(SavedJoypadBits=buttons)
            _, writes = q.invoke('GameLoop')
            assert q.get('GameEngineSubroutine') == 8
            assert q.get('PlayerStatus') == tier
            assert q.get('Player_X_Position') == 112 and q.get('Player_Y_Position') == 176
            assert q.get('Player_State') == 0 and q.get('InjuryTimer') == 0
            assert q.get('GuestHurtTicks') == 0 and q.get('MmDeathFlag') == 0
            for slot in range(10):
                if q.get('RgShotType', slot):
                    shots.append(dict(update=update, slot=slot, age=q.get('RgShotAge', slot),
                                      x=q.get('RgShotX', slot), y=q.get('RgShotY', slot)))
            for w in writes:
                if w['address'] in (address(b, 'MmEnemyHealthLo'), address(b, 'MmEnemyHealthHi')):
                    hp.append(dict(update=update, **w))
    finally:
        NesMPU.step = original
    assert all(n in path for n in names if n not in ['ExpandedWeapons::MoveKill', 'MegaManWeapons::DamageEnemy'])
    assert calls['GameLoop'] == calls['ExpandedWeapons'] == 110
    assert not any(q.get('RgShotType', s) for s in range(10))
    assert q.get('RgAttack') == q.get('RgShootPose') == 0
    return dict(mode=mode, tier=tier, kind=kind, target=[ex, ey],
                complete_GameLoop_calls=110, path=path, calls=calls,
                shots=shots, contacts=contact, MoveKill=killed, health_writes=hp,
                final_enemy=dict(flag=q.get('Enemy_Flag'), state=q.get('Enemy_State'),
                                 x=q.get('Enemy_X_Position'), y=q.get('Enemy_Y_Position'),
                                 health=q.get('MmEnemyHealthLo')+256*q.get('MmEnemyHealthHi')),
                cleanup=True, no_damage_or_player_movement=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'build/current-6be-pit-easy-items-v1/first-negative.json')
    a = p.parse_args()
    assert not a.output.exists(), 'Additive only; never overwrite a receipt'
    folder = ROOT/'build/current-6be-pit-easy-items-v1'
    ready = folder/'prepared-not-run.json'
    assert sha(ready) == READY
    for item in json.loads(ready.read_text())['bindings']:
        path = Path(item['path'])
        assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
    rom = ROOT/'build/samus_fixed_hud_current4a.nes'
    assert sha(rom) == EXPECTED
    b = scoped_load(rom)
    rows = list(csv.DictReader((folder/'native/pit-components.csv').open()))
    assert rows[0]['event'] == 'disclosed-scene-setup'
    events = {n: [r for r in rows if r['event'] == n] for n in
              ['actual-bow-spawn', 'actual-source-contact', 'actual-target-health-write', 'case-complete']}
    assert len(events['actual-bow-spawn']) == 1
    assert not any(events[n] for n in events if n != 'actual-bow-spawn')
    assert rows[-1]['wall'] == '425' and rows[-1]['update'] == '139' and rows[-1]['age'] == '109'
    assert [r['wall'] for r in rows if r['event'] == 'update' and int(r['shots']) > 0] == [str(i) for i in range(322, 334)]
    log = (folder/'native/samus_fixed_hud_current4a-run.log').read_text()
    assert 'FAIL One real bow shot/contact/native damage' in log
    launch = json.loads((folder/'launch.json').read_text())
    assert launch['exit_code'] == 1 and launch['settings_before'] == launch['settings_after']
    assert not launch['changed_inputs']
    assert not (ROOT/'build/current-6be-pit-hard-items-v1/native').exists()
    cfg = json.loads((folder/'config.json').read_text())
    owner = cfg['hooks']['DamageEnemy']
    assert owner['pc'] == address(b, 'MegaManWeapons::DamageEnemy')
    assert owner['banks'] == [(location(b, 'MegaManWeapons::DamageEnemy')-16)//8192]
    radius_x = b['raw'][location(b, 'MegaManWeapons::RadiusX')+25]
    radius_y = b['raw'][location(b, 'MegaManWeapons::RadiusY')+25]
    assert (radius_x, radius_y) == (4, 3)
    controls = []
    for mode in (0, 1):
        old = reconstruct(b, mode, 0, 176)
        assert not old['contacts'] and not old['health_writes']
        assert [s['x'] for s in old['shots']] == [124,128,132,136,140,145,149,153,157,161,165,170]
        assert old['MoveKill'] == [dict(update=18, shot_age=13, x=170, y=194)]
        assert old['final_enemy'] == dict(flag=1, state=0, x=176, y=184, health=0)
        controls.append(old)
        near = reconstruct(b, mode, 0, 160)
        assert len(near['contacts']) == 1 and near['contacts'][0]['bullet_type'] == 26
        assert near['contacts'][0]['update'] == 14 and near['contacts'][0]['x'] == 157
        assert len(near['health_writes']) == 4 and near['final_enemy']['health'] == 75
        controls.append(near)
        for tier in (1, 2):
            powered = reconstruct(b, mode, tier, 176)
            assert len(powered['contacts']) == 1 and powered['contacts'][0]['bullet_type'] == 26+tier
            assert len(powered['health_writes']) == 4
            controls.append(powered)
            hammer = reconstruct(b, mode, tier, 136, 'hammer')
            assert len(hammer['contacts']) >= 1 and all(c['bullet_type'] == 38 for c in hammer['contacts'])
            assert hammer['health_writes']
            controls.append(hammer)
    paths = [Path(__file__), ready, folder/'launch.json']
    paths += sorted(p for p in (folder/'native').iterdir() if p.is_file())
    paths += [ROOT/'tools/audit/current_pit_powerups_v1.lua', ROOT/'tools/audit/current_pit_powerups_prepare_v1.py',
              rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl')]
    paths += [ROOT/'src'/n for n in ['game.s', 'object.s', 'expanded_weapons.s', 'megaman_weapons.s', 'roster_weapons.s']]
    paths += [ROOT/'tools/audit'/n for n in ['link_pit_rygar_sophia_audit_cpu.py', 'check_tmnt_render_oa.py', 'verify_native_relocation.py']]
    proof = dict(passed=False, native_passed=False, diagnosis_source_controls_passed=True,
                 ROM_sha256=EXPECTED, original_ready_sha256=READY, native_launches=1,
                 first_failure='One real bow shot/contact/native damage',
                 native_facts=dict(completed_cases=0, recorded_spawn=events['actual-bow-spawn'][0],
                                   recorded_contact_count=0, recorded_health_write_count=0,
                                   last_CSV=rows[-1], shot_present_wall=[322,333],
                                   shot_absent_from_wall=334, Hard='UNRUN', settings_unchanged=True),
                 source_cause=dict(classification='Invalid target distance in the component fixture',
                                   cold_centers=[124,128,132,136,140,145,149,153,157,161,165,170],
                                   radius_x=radius_x, radius_y=radius_y, max_right=174, target_left=176,
                                   expiry_age=13, expiry_before_movement_or_collision=True,
                                   expected_safe_target_x=160,
                                   future_oracle_correction='Bow proxy is 26+PlayerStatus, not constant26; cold failure is not caused by this later-tier observer error.'),
                 source_CPU_controls=controls,
                 limits='Reconstructed complete GameLoop CPU arenas; not exact saved native RAM, PPU timing, Lua execution or new native proof. Actual CSV lacks target/shot coordinate provenance. Existing failure/inputs/assertions remain immutable. No game defect or successful acquisition/use unit claimed.',
                 agent_visual_review=dict(passed_scope=True, images=['native/cold-bow.png'],
                                          scope='One actual whole-frame sample; separated Pit/arrow/Goomba and ordinary floor visible, no terrain displacement evident in this sample. Not all-frame/pixel fidelity.'),
                 bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p)) for p in paths])
    a.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(output=str(a.output),sha256=sha(a.output),native_passed=False,
                          source_controls=len(controls),complete_GameLoops=sum(z['complete_GameLoop_calls'] for z in controls),
                          bindings=len(paths))))


if __name__ == '__main__':
    main()

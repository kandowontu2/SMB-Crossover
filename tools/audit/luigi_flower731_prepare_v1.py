"""Prepare one LuigiEasy physical flower component; source/CPU/mocks only."""
from pathlib import Path
import argparse
import difflib
import itertools
import json
import re
import shutil
import subprocess
import sys

from check_tmnt_render_oa import address, load, location
from observe_chip_committed_write import lua
from robots_weapon_cpu_v1 import Arena
from mario_powerups_current3cee_static_v2 import runtime, symbols
from mario_flower900_prepare_v4 import controller_controls
from mario_flower731_prepare_v1 import ROOT, D, SOURCE, SHA, get, put, sha, source_controls

PARENT = D / 'mario-flower731-east-v1'


def feasibility(bundle, rom, observer, output):
    sys.path.insert(0, str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    text = observer.read_text()
    aim = 'local function aim(c,target)\n' + text.split('local function aim(c,target)\n', 1)[1].split('\nend\n', 1)[0] + '\nend\n'
    rt = LuaRuntime(unpack_returned_tuples=True)
    arc = 'local b=aim(c,1248);b.a=arcAge<32;b.b=true;return b'
    assert text.count(arc) == 1
    rt.execute(aim + 'function control(c,arcAge)' + arc + ' end')
    table = location(bundle, 'BoundBoxCtrlData')
    big = list(bundle['raw'][table:table + 4])
    reward = list(bundle['raw'][table + 36:table + 40])
    assert big == [2, 8, 14, 32] and reward == [3, 14, 13, 20]
    trajectories = []
    for start in range(1288, 1293):
        for fraction, subspeed in itertools.product([0, 85, 170, 255], [0, 255]):
            q = Arena(bundle, char=8)
            q.put(CrossoverBehaviorVersion=0, MarioVariant=1, Player_X_Position=start % 256,
                  Player_PageLoc=start // 256, Player_Y_Position=176, Player_Y_HighPos=1,
                  PlayerStatus=1, PlayerSize=0, Player_State=0, Player_X_Speed=0,
                  Player_X_MoveForce=subspeed, Player_XSpeedAbsolute=0, Player_Y_Speed=0,
                  Player_Y_MoveForce=0, Player_YMoveForceFractional=0, SprObject_X_MoveForce=fraction,
                  PlayerFacingDir=2, Player_MovingDir=2, Player_CollisionBits=255,
                  AreaType=1, SwimmingFlag=0, GameEngineSubroutine=8, VerticalForceDown=112,
                  ScrollLock=1, OperMode_Task=3)
            for _ in range(2):
                q.put(SavedJoypadBits=0, A_B_Buttons=0, Left_Right_Buttons=0, Up_Down_Buttons=0)
                q.invoke('PlayerMovementSubs')
            assert q.get('Player_X_Speed') == 0 and q.get('Player_X_MoveForce') == subspeed
            path = []
            for age in range(1, 49):
                x = q.get('Player_X_Position') + 256 * q.get('Player_PageLoc')
                context = rt.table_from(dict(x=x, vx=q.get('Player_X_Speed')))
                buttons = dict(a=True, left=True, b=True) if age == 1 else dict(rt.globals().control(context, age - 1).items())
                mask = sum(v for k, v in [('a', 128), ('b', 64), ('left', 2), ('right', 1)] if buttons.get(k))
                q.put(SavedJoypadBits=mask, A_B_Buttons=mask & 192, Left_Right_Buttons=mask & 3, Up_Down_Buttons=0)
                q.invoke('PlayerMovementSubs')
                q.put(PreviousA_B_Buttons=mask & 192, Player_MovingDir=2 if q.get('Player_X_Speed') >= 128 else 1)
                if q.get('RunningTimer'):
                    q.set('RunningTimer', q.get('RunningTimer') - 1)
                q.set('FrameCounter', (q.get('FrameCounter') + 1) & 255)
                x = q.get('Player_X_Position') + 256 * q.get('Player_PageLoc')
                y = q.get('Player_Y_Position')
                overlap = x + big[0] < 1248 + reward[2] and x + big[2] > 1248 + reward[0] and y + big[1] < 119 + reward[3] and y + big[3] > 119 + reward[1]
                path.append(dict(age=age, x=x, y=y, buttons=mask, vy=q.get('Player_Y_Speed'),
                                 flower_bbox_overlap=overlap, horizontal_gap_from_static_Goomba1236=x + 2 - (1236 + 13)))
            overlap = next(z for z in path if z['flower_bbox_overlap'])
            landing = next(z for a, z in zip(path, path[1:]) if a['y'] <= 112 < z['y'] and z['vy'] < 128)
            assert 1232 <= landing['x'] + 3 < 1280
            assert overlap['age'] <= 43 and overlap['horizontal_gap_from_static_Goomba1236'] >= 8
            assert min(z['y'] for z in path) > 95
            trajectories.append(dict(start=start, displacement_fraction=fraction, retained_native_subspeed=subspeed,
                quiet_coast_does_not_clear_native_subspeed=True, first_flower_overlap=overlap,
                predicted_lower_row_descent=landing, minimum_y=min(z['y'] for z in path), trajectory=path))
    transforms = []
    for power in [0, 1]:
        q = Arena(bundle, char=8)
        q.put(CrossoverBehaviorVersion=0, MarioVariant=1, PlayerStatus=power,
              Player_X_Position=34, Player_PageLoc=5, Player_Y_Position=112,
              GuestPowerupActive=0, GuestPowerupAge=0)
        q.invoke('GuestBeginPowerup', x=5)
        assert q.get('GuestPowerupTarget') == power + 1 and q.get('GuestPowerupActive') == 1
        for age in range(60):
            assert q.get('GuestPowerupAge') == age
            q.invoke('GuestPowerupUpdate')
            assert q.get('Player_X_Position') == 34 and q.get('Player_Y_Position') == 112
        assert q.get('GuestPowerupActive') == 0 and q.get('PlayerStatus') == power + 1
        transforms.append(dict(initial_power=power, target=power + 1, actual_owner='GuestPowerupUpdate', source_updates=60))
    poses = []
    palettes = []
    for power in range(3):
        for name in ['STAND', 'JUMP', 'CROUCH']:
            pose = address(bundle, 'XG_POSE_' + name)
            q = Arena(bundle, char=8)
            q.put(PlayerStatus=power, GuestPowerupActive=0, RgPose=pose, PlayerFacingDir=1)
            q.invoke('ExpandedPose')
            index = power * address(bundle, 'XG_POSE_COUNT') + pose
            bank = bundle['raw'][location(bundle, 'XgLUIGIBanks') + index]
            ptr = bundle['raw'][location(bundle, 'XgLUIGIRightLo') + index] + 256 * bundle['raw'][location(bundle, 'XgLUIGIRightHi') + index]
            assert q.get('SmChrBank') == bank and q.get('SmPosePtr') + 256 * q.get('SmPosePtr', 1) == ptr
            poses.append(dict(power=power, name=name, pose=pose, actual_record=ptr, actual_legacy_chr=bank))
        q = Arena(bundle, char=8)
        q.put(PlayerStatus=power, GuestPowerupActive=0, GuestPowerupAge=0, VRAM_Buffer1_Offset=0)
        q.invoke('GuestPowerupPalette')
        colors = [q.get('VRAM_Buffer1', i) for i in range(3, 6)]
        assert colors == ([0x30, 0x27, 0x16] if power == 2 else [0x1a, 0x27, 0x17])
        palettes.append(dict(power=power, actual_source_palette=colors))
    output.mkdir()
    put(output / 'proof.json', dict(passed=True, source_CPU_only=True, native_executed=False, ROM_sha256=sha(rom),
        trajectory_cases=trajectories, transforms=transforms, palette_metadata=palettes, pose_metadata=poses,
        genuine_character=8, genuine_Mario_slot_variant=1, retained_controller_arc_source=arc,
        scope='40 freshly executed native movement component trajectories from visibly settled legal states with native residual subspeed retained, no terrain/actor collision/IRQ/PPU. Row/flower and static-worst-case Goomba geometry are conditional source feasibility, not native outcomes. Full120growth and nine actual pose/three palette components are isolated CPU calls.'))
    return palettes, poses


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    rom = SOURCE / 'candidate.nes'
    assert sha(rom) == SHA
    manifest = get(SOURCE / 'source-manifest.json')
    for f, h in manifest.items():
        assert sha(SOURCE / 'source' / f) == h, f
    proof = PARENT / 'native-result-freeze-v1/proof.json'
    assert sha(proof) == 'ad4d5ed99b9e91507b519207d05a500f651e21cd3838fe35f2a1207207ae1049'
    oldproof = get(proof)
    for f, h in oldproof['bindings'].items():
        assert sha(f) == h, f
    b = load(rom)
    folder = out / 'luigi-easy'
    folder.mkdir();(folder / 'frames').mkdir()
    parent = PARENT / 'mario-easy'
    original = ROOT / 'tools/audit/mario_flower900_native_v4.lua'
    module = ROOT / 'tools/audit/luigi_flower731_native_v1.lua'
    old = original.read_text()
    expected = old.replace("r('SelectedCharacter')==0", "r('SelectedCharacter')==C.character")
    expected = expected.replace("hook('MarioSourcePowerupUpdate',function()", "hook(C.growthOwner,function()")
    expected = expected.replace("r('MarioVariant')==0,'Real cold selected MarioEasy'", "r('MarioVariant')==C.variant,'Real cold selected LuigiEasy'")
    expected = expected.replace("character=0,variant=r('MarioVariant')", "character=C.character,variant=r('MarioVariant')")
    expected = expected.replace('One genuine MarioEasy mushroom then later flower', 'One genuine LuigiEasy mushroom then later flower')
    expected = expected.replace('-- One neutral ground update makes the source coast clamp its subpixel vx0.', '-- Neutral settles the visible speed; Luigi may retain native fractional speed.')
    assert module.read_text() == expected
    (out / 'identity-source-owner-only.diff').write_text(''.join(difflib.unified_diff(old.splitlines(keepends=True), expected.splitlines(keepends=True), fromfile=original.name, tofile=module.name)), encoding='utf-8', newline='\n')
    palettes, poses = feasibility(b, rom, module, out / 'luigi-source-feasibility-v1')
    before = get(parent / 'configuration.json')
    cfg = dict(before['roster'])
    cfg.update(name='luigi', character=8, variant=1, menuName='LUIGI', out=folder.as_posix() + '/',
               policy=(folder / 'policy.lua').as_posix(), audit=(folder / 'audit.lua').as_posix())
    item = dict(before['item'])
    item.update(character=8, variant=1, growthOwner='GuestPowerupUpdate', palettePoseMetadata=dict(palettes=palettes, poses=poses))
    item['hooks'] = {n: dict(address=address(b, n), bank=(location(b, n) - 16) // 8192,
                            bytes=list(b['raw'][location(b, n):location(b, n) + 3]))
                     for n in ['PwrUpJmp', 'MarioSourcePowerupCollision', 'GuestPowerupUpdate', 'MarioSourceFireballBrick', 'HandleEnemyFBallCol']}
    put(folder / 'configuration.json', dict(roster=cfg, item=item))
    for f in ['policy.lua', 'audit.lua', 'harness.lua']:
        shutil.copyfile(parent / f, folder / f)
        assert sha(parent / f) == sha(folder / f)
    script = ('ROSTER_CONFIG=' + lua(cfg) + '\nMARIO_FLOWER_CONFIG=' + lua(item) +
              '\ndofile(' + lua(module.as_posix()) + ')\ndofile(' + lua((folder / 'harness.lua').as_posix()) +
              ')\nassert(MARIO_POWERUP_INSTALL_CHR_DISPATCHER)()\n')
    (folder / 'run.lua').write_text(script, encoding='utf-8', newline='\n')
    assert not re.search(r'\bemu\.(?:write\w*|setState|loadSavestate|reset)\s*\(', script + expected + ''.join((folder / f).read_text() for f in ['policy.lua', 'audit.lua', 'harness.lua']))
    source_controls(b, rom, out / 'source-controls-v1')
    static = [sys.executable, '-B', str(ROOT / 'tools/audit/mario_powerups_current3cee_static_v2.py'), '--fixture', str(folder), '--rom', str(rom),
              '--lua-root', str(D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'), '--output', str(out / 'startup-static-v1')]
    z = subprocess.run(static, cwd=ROOT, capture_output=True, text=True)
    (out / 'static-host.log').write_text(z.stdout + z.stderr, encoding='utf-8')
    assert z.returncode == 0, z.stderr
    controller_controls(folder, module, b, rom, out / 'controller-source-controls-v1')
    env = get(PARENT / 'environment.json')
    for n in ['emulator', 'core', 'worker_settings', 'user_settings']:
        assert sha(env[n]) == env[n + '_sha256'], n
    report = ROOT / 'docs/qa/luigi-flower731-preparation-2026-10-26.txt'
    failure = D / 'luigi-flower731-east-v1/source-preparation-first-error-v1'
    deps = {Path(__file__), module, original, report, proof, failure / 'proof.json', failure / 'failed-quiet-oracle.py', ROOT / 'tools/audit/luigi_flower731_run_v1.py', SOURCE / 'proof.json', SOURCE / 'source-manifest.json',
            rom, rom.with_suffix('.dbg'), rom.with_suffix('.lbl'), PARENT / 'environment.json'}
    deps |= {Path(f) for f in oldproof['bindings']}
    deps |= {SOURCE / 'source' / f for f in manifest}
    deps |= {f for f in out.rglob('*') if f.is_file()}
    command = [sys.executable, '-B', str(ROOT / 'tools/audit/run_mesen_isolated.py'), '--output', str(folder), '--emulator', env['emulator'],
               str(folder / 'run.lua'), str(rom), '--timeout', '180'] + ['--option=' + v for v in env['deterministic_command_overrides']]
    ready = dict(passed=True, status='PREPARE_DO_NOT_RUN', native_executed=False, native_grant=False,
        ROM_sha256=SHA, native_workers=1, environment=env,
        profiles=[dict(name='luigi-easy', mode=0, character=8, variant=1, fixture=str(folder), limit_physical_frames=6500,
                       command=command, endpoint='Real Luigi mushroom/flower,120sourcegrowth, actual live enemy fireball contact, released45drain')],
        bindings={str(f): sha(f) for f in sorted(deps, key=str)}, no_game_state_or_settings_writes=True,
        Mario_PASS_and_all_historical_negatives_unchanged=True,
        limits='ONE source-supported LuigiEasy attempt is prepared, not native-proven. No fullroute/Hard/allitems/source-art/waveform claim.')
    put(out / 'readiness.json', ready)
    # The existing runner explicitly admits only mario-easy; prepare this
    # one-shot invocation with a source-bound identity-specific successor.
    runner = ROOT / 'tools/audit/luigi_flower731_run_v1.py'
    assert runner.is_file()
    assert str(runner) in ready['bindings']
    put(out / 'command.json', dict(not_executed=True, explicit_new_ROOT_grant_required=True,
        command=[sys.executable, '-B', str(runner), '--packet', str(out), '--expected-readiness-sha256', sha(out / 'readiness.json'), '--native-grant']))
    print(json.dumps(dict(passed=True, native_executed=False, profiles=1, bindings=len(ready['bindings']),
                         readiness_sha256=sha(out / 'readiness.json'), command_sha256=sha(out / 'command.json')), indent=2))


if __name__ == '__main__':
    main()

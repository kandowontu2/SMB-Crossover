"""Compare Mario and Mini Mario foreground costs in matched CPU arenas."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at
import profile_mini_busy_1108_v1 as P


R, N = P.R, P.N
ROM = R/'build/mini-box-transport-native-1110/candidate.nes'
PIN = '03c0cfe6d4562f6b7970199ce2d6ffa6f2f0f905a8cb8425945add6fcb71585d'
WITNESS = R/'build/mini-platform-actor-profile-1110/capture/instruction-sample.json'
KERNEL = R/'build/mini-projection-reuse-1110/kernel.bin'

BUCKETS = {
    'player_update': ('GuestGameRoutinesBridge',),
    'player_draw': ('PlayerOAMReservation', 'PlayerGfxHandler'),
    'enemy_loop': ('EnemiesAndLoopsCore',),
    'enemy_post_collision': ('GuestPostEnemyCollision',),
    'projectile_loop': ('HpProcessFireballsBridge',),
    'world_draw': ('SamusFreezeDrawAll',),
    'parser': ('AreaParserTaskHandler',),
    'other_world': ('BlockObjMT_Updater', 'BlockObjectsCore', 'MiscObjectsCore',
                    'ProcessCannons', 'ProcessWhirlpools', 'FlagpoleRoutine', 'RunGameTimer'),
}
DETAIL = (
    'GameCoreRoutine', 'PlayerCtrlRoutine', 'MarioSourceMovement', 'PlayerBGCollision',
    'PlayerMovementSubs', 'ScrollHandler', 'GetPlayerOffscreenBits', 'GetEnemyOffscreenBits',
    'RelativePlayerPosition', 'RelativeEnemyPosition', 'GuestBoxWriteback',
    'RemainingPlayerEnemyCollision', 'PlayerEnemyCollision', 'NormalEnemyBoundBox',
    'RunNormalEnemies', 'RunLargePlatform', 'LargePlatformCollision',
    'HpNativePlatformBBoxGate', 'DrawLargePlatform', 'DrawAllMetasprites',
    'EnemyGraphicsEngine', 'GuestDamage', 'BlockBufferCollision', 'MiniScene',
    'MiniCheck', 'MiniLiftTick', 'InventoryUiTick', 'FamilyMain',
)
KERNEL_DETAIL = ('MiniHostMain', 'MiniStep', 'MiniNativeTile', 'MiniAnimate', 'MiniHostBox',
                 'MiniHostDraw', 'MiniNativeDraw', 'MiniHostGraphics', 'MiniHostImportX',
                 'MiniHostImportY', 'MiniPlatformFloor')


def menu_key(memory, key):
    N.put(memory, CrossoverMenuButtons=0, SavedJoypad1Bits=key, SavedJoypad2Bits=0,
          VRAM_Buffer1_Offset=0)
    return N.invoke(memory, 'CrossoverMenuInput', p=0x30)


def cold(bundle, owner):
    m = N.fresh(bundle)
    N.put(m, CrossoverMenuIndex=0)
    for entry in ('MenuResolveCharacter', 'QueueSelection', 'DrawSelectionPreview'):
        N.invoke(m, entry)
    seen = []
    for _ in range(10):
        seen.append([N.get(m, 'MarioVariant'), N.get(m, 'SelectedCharacter')])
        if seen[-1][1] == owner:
            break
        menu_key(m, 32)
    assert seen[-1] == ([0, 0] if owner == 0 else [8, 41]), seen
    start = menu_key(m, 16)
    assert N.get(m, 'CrossoverMenuState') == 0
    assert P.address(bundle, 'ChkContinue') == 0xbc14
    N.invoke(m, 'ChkContinue',
             a=start['A'], x=start['X'], y=start['Y'], p=start['P'])
    N.invoke(m, 'PauseRoutine', a=0)
    for updates in range(600):
        if (N.get(m, 'OperMode_Task'), N.get(m, 'GameEngineSubroutine')) == (3, 8):
            break
        controls(m, 0)
        N.invoke(m, 'GameLoop', x=0, y=0)
        N.consume(m)
    else:
        raise AssertionError(('Cold entrance', owner))
    assert N.get(m, 'SelectedCharacter') == owner and N.get(m, 'PlayerStatus') == 0
    assert N.get(m, 'AreaAddrsLOffset') == 5 and N.get(m, 'AreaType') == 1
    installed = bytes(m.ram[3][:5120]) == KERNEL.read_bytes()
    assert installed == (owner == 41)
    if installed:
        cookie = bundle['raw'][16+65*8192+0x1003:16+65*8192+0x1013]
        assert all(bytes(m.ram[i][0x1fe0:0x1ff0]) == cookie for i in (2, 3))
        assert m.ram[2][0x300] in (1, 2)
    return m, dict(menu=seen, entrance_updates=updates, Mini_payload_loaded=installed,
                   initial_CHR=list(m.chr_latches), initial_mapper=list(m.rawtags))


def controls(m, key):
    N.put(m, SavedJoypadBits=key, SavedJoypad1Bits=key, SavedJoypad2Bits=0,
          A_B_Buttons=key&192, Left_Right_Buttons=key&3, Up_Down_Buttons=key&12,
          NmiDisable=255)


def place(m, name, slot, value):
    m[P.address(m.bundle, name)+slot] = value


def arena(m, scene, crowd):
    owner = N.get(m, 'SelectedCharacter')
    # Reset the camera and terrain to an identical flat diagnostic arena.
    # Both players keep the actual owner-specific runtime from cold entrance.
    camera, x = scene['camera_left'], scene['x']-16
    right = camera+255
    N.put(m, ScreenLeft_X_Pos=camera&255, ScreenLeft_PageLoc=camera>>8,
          ScreenRight_X_Pos=right&255, ScreenRight_PageLoc=right>>8,
          Player_X_Position=x&255, Player_PageLoc=x>>8, Player_Y_Position=176,
          Player_Y_HighPos=1, Player_State=0, Player_X_Speed=0, Player_Y_Speed=0,
          PlayerFacingDir=1, AreaParserTaskNum=0, ScrollThirtyTwo=0,
          EnemyDataOffset=29, EnemyFrenzyQueue=0, EnemyFrenzyBuffer=0,
          TimerControl=0, FrameCounter=2, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
    for name in ('Block_Buffer_1', 'Block_Buffer_2'):
        at = P.address(m.bundle, name)
        m[at:at+208] = bytes(176)+bytes([0x54])*32
    if owner == 41:
        # The ordinary native import can synchronize this explicit warp.
        # Set only the helper history to reflect the intended six-actor fixture.
        m.ram[2][0x30c] = 7
    controls(m, 0)
    N.invoke(m, 'GameLoop', x=0, y=0)
    N.consume(m)
    N.put(m, FrameCounter=2, AreaParserTaskNum=0, ScrollThirtyTwo=0,
          VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
    for row in scene['actors']:
        slot = row['slot']
        place(m, 'Enemy_Flag', slot, int(crowd))
        if not crowd:
            continue
        fields = {'Enemy_ID':row['id'], 'Enemy_PageLoc':row['x']>>8,
                  'Enemy_X_Position':row['x']&255, 'Enemy_Y_HighPos':row['y_high'],
                  'Enemy_Y_Position':row['y_low']}
        for name, value in fields.items():
            place(m, name, slot, value)
        N.put(m, ObjectOffset=slot)
        N.invoke(m, 'InitEnemyObject', x=slot, y=0)
        for name, value in fields.items():
            place(m, name, slot, value)
        place(m, 'Enemy_State', slot, row['state'])
        place(m, 'Enemy_BoundBoxCtrl', slot, row['box_control'])
        place(m, 'PlatformCollisionFlag', slot, 255)
    if owner == 41:
        m.ram[2][0x30b] = 4 if crowd else 0
    return m


def trace_points(bundle):
    points = {}
    missing = []
    groups = {name: group for group, names in BUCKETS.items() for name in names}
    for name in (*groups, *DETAIL):
        if name not in bundle['syms']:
            missing.append(name)
            continue
        offset = P.location(bundle, name)
        point = (((offset-16)//8192)|128, P.address(bundle, name))
        points.setdefault(point, []).append((name, groups.get(name)))
    for pc, name in re.findall(r'^al ([0-9A-F]+) \.(\w+)$', KERNEL.with_suffix('.lbl').read_text(), re.M):
        if name in KERNEL_DETAIL:
            points[3, int(pc, 16)] = [(name, None)]
    return points, missing


def position(m):
    return [N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
            N.get(m, 'Player_Y_Position'), N.get(m, 'Player_State'),
            N.get(m, 'ScreenLeft_X_Pos')+256*N.get(m, 'ScreenLeft_PageLoc')]


def live_actors(m):
    names = ('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc',
             'Enemy_Y_Position','Enemy_Y_HighPos','Enemy_BoundBoxCtrl','Enemy_X_Speed',
             'Enemy_Y_Speed','Enemy_Y_MoveForce','YPlatformTopYPos','YPlatformCenterYPos')
    return [[N.get(m, name, i) for name in names] for i in range(6)]


def profile(m, points, keys):
    controls(m, keys)
    before = position(m)
    c = cpu_at(m, P.address(m.bundle, 'GameLoop'), 252, 0x21, x=0, y=0)
    assert m.rawtags[(c.pc-0x8000)//8192] == 126|128
    active, inclusive, buckets, leaf, banks, transport = [], Counter(), Counter(), Counter(), Counter(), Counter()
    while (c.pc, c.sp) != (STOP, 252):
        pc, sp, start = c.pc, c.sp, c.processorCycles
        while active and active[-1][0] == (pc, sp):
            _, first, labels = active.pop()
            for name, _ in labels:
                inclusive[name] += start-first
        tag = m.rawtags[(pc-0x8000)//8192] if pc >= 0x8000 else -1
        if labels := points.get((tag, pc)):
            ret = (1+m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)])&65535
            active.append(((ret, (sp+2)&255), start, labels))
        if pc == 0x15a:
            transport[f'${c.a:02X}:${m[0x16c]+256*m[0x16d]:04X}'] += 1
        assert m[pc] and start < 100000
        c.step()
        cost = c.processorCycles-start
        group = next((group for _, _, labels in active for _, group in labels if group), 'unassigned')
        buckets[group] += cost
        banks[tag] += cost
        if active:
            leaf[active[-1][2][0][0]] += cost
        if 0x15a <= pc < 0x17b:
            leaf['farcall_trampoline'] += cost
    assert all(end == (STOP,252) for end, _, _ in active), active
    for _, first, labels in active:
        for name, _ in labels:
            inclusive[name] += c.processorCycles-first
    assert sum(buckets.values()) == sum(banks.values()) == c.processorCycles
    assert N.get(m, 'GameEngineSubroutine') == 8, (N.get(m,'SelectedCharacter'), before, position(m))
    return dict(cycles=c.processorCycles, before=before, after=position(m), buckets=buckets,
                inclusive=inclusive, leaf=leaf, banks=banks, farcalls=transport)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    raw = ROM.read_bytes()
    assert P.sha(raw) == PIN
    bundle = P.bundle(raw)
    points, missing = trace_points(bundle)
    scene = json.loads(WITNESS.read_text())['scene']
    assert [row['id'] for row in scene['actors']] == [6,6,6,37,37,37]
    # Arena setup deliberately advances the genuine area 1-1 actor cursor to
    # its terminator so inactive fixture slots do not load unrelated actors.
    assert raw[19023:19053] == bytes.fromhex('1ec2006b068b8663b70f05030623064bb7bb005bb7fb373bb70f0b1b37ff')
    seeds, boot = {}, {}
    for owner in (0, 41):
        seeds[owner], boot[owner] = cold(bundle, owner)
        print('Cold owner', owner, boot[owner], flush=True)
    results = {}
    for crowd in (False, True):
        pair = [arena(N.fork(seeds[owner]), scene, crowd) for owner in (0, 41)]
        assert live_actors(pair[0]) == live_actors(pair[1])
        trials = []
        for key in (0, 0, 193, 193, 1, 1):
            rows = [profile(m, points, key) for m in pair]
            trials.append(dict(input=key, Mario=rows[0], Mini=rows[1]))
            for m in pair:
                N.consume(m)
        label = 'six_actors' if crowd else 'empty'
        results[label] = trials
        print(label, [(q['Mario']['cycles'], q['Mini']['cycles']) for q in trials], flush=True)
    q = dict(passed=True, ROM_SHA256=PIN, cold=boot, trials=results,
             missing_symbol_hooks=missing, witness=scene,
             scope='Synthetic foreground CPU arenas after real independent menu and scene initialization. '
                   'Both owners receive the same flat collision buffers and matched native actor initialization. '
                   'A normal NMI advances state between samples, outside the foreground measure.')
    args.output.mkdir()
    (args.output/'profile.json').write_text(json.dumps(q, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()

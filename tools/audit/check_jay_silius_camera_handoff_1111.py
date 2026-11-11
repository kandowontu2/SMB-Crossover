"""Run the Jay camera and world handoff on authenticated, cold-loaded SMB RAM."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU

import check_jay_silius_cold_resident_1110 as Cold
import check_jay_silius_scene_lifecycle_1110 as C

ROOT = Path(__file__).resolve().parents[2]
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = '852712c9a2afce71c45f9f2c970e1f5c7969c58d878cfa0a250d2bdb7ba93383'
COOKIE = bytes.fromhex('a7102007de73e237c21c140b1055419b')
SOURCE = ROOT / 'tools/reference/jay_silius_camera_handoff_1111.s'
CONTROL_SOURCE = ROOT / 'tools/reference/jay_silius_control_tail_1111.s'
SYNC_SOURCE = ROOT / 'tools/reference/jay_silius_native_sync_1111.s'
PIT_SOURCE = ROOT / 'tools/reference/jay_silius_pit_boundary_1111.s'
W, N = C.W, C.N
STATES = ('OperMode', 'OperMode_Task', 'GameEngineSubroutine')
NATIVE = {
    'PlayerX': 'Player_X_Position', 'PlayerPage': 'Player_PageLoc',
    'PlayerY': 'Player_Y_Position', 'PlayerYPage': 'Player_Y_HighPos',
    'CameraPixel': 'ScreenLeft_X_Pos', 'CameraPage': 'ScreenLeft_PageLoc',
    'PlayerPosForScroll': 'Player_Pos_ForScroll', 'PlayerXScroll': 'Player_X_Scroll',
    'PlayerYSpeed': 'Player_Y_Speed', 'PlayerState': 'Player_State',
    'PlayerXSpeed': 'Player_X_Speed', 'PlayerFacing': 'PlayerFacingDir',
    'EnemyFlag': 'Enemy_Flag', 'EnemyID': 'Enemy_ID', 'EnemyY': 'Enemy_Y_Position',
    'EnemyYPage': 'Enemy_Y_HighPos', 'PlatformContact': 'PlatformCollisionFlag',
}
IDENTICAL = ('OperMode', 'OperMode_Task', 'GameEngineSubroutine', 'GamePauseStatus',
             'NmiDisable', 'FamilyMainCommit', 'SwimmingFlag', 'WorldNumber',
             'LevelNumber', 'SavedJoypadBits', 'FrameCounter')
PRIVATE = {'XHi': 0x10, 'XLo': 0x11, 'YHi': 0x12, 'YLo': 0x13, 'DonorVY': 0x15,
           'DonorFlags': 0x19, 'CameraXHi': 0x30, 'CameraXLo': 0x31,
           'PadNow': 0x162, 'PadPrevious': 0x163, 'DonorVX': 0x14,
           'DonorControl': 0x1C, 'DonorControlTimer': 0x51C}
ACTOR, ENTRY, OLD_END = 0xA000, 0xA785, 0xA8C0


def parent(raw=None, *, pin=PIN, cookie=COOKIE):
    if raw is None:
        raw = ROM.read_bytes()
    assert sha256(raw).hexdigest() == pin
    trial = W.Symbols.bundle()
    trial['raw'] = raw
    m = C.menu(trial, 1, {'images': {}})
    for tick in range(220):
        if tuple(N.get(m, name) for name in STATES) == (1, 3, 8):
            break
        C.Game.frame(m)
    else:
        raise AssertionError('Jay did not reach normal Main')
    assert C.Common.headers(m) == (cookie,) * 2
    assert (m.ram[2][0x33], m.ram[2][0x34]) == (0, 0)
    return m, trial, tick


def assemble_handoff(trial, template, *, origin=ENTRY, control_tail=False, native_sync=False,
                     native_helpers=None, pit_boundary=False):
    """Assemble the relocatable movement entry and publisher with exact native symbols."""
    linked = C.Jay.build()
    fields = {name: linked['ram'][logical] for name, logical in PRIVATE.items()}
    fields.update({alias: W.address(trial, name) for alias, name in NATIVE.items()})
    fields.update({name: W.address(trial, name) for name in IDENTICAL})
    fields.update(OperModeTask=W.address(trial, 'OperMode_Task'),
                  Actor=0xC000, Ready=0xC033, Epoch=0xC034, OldX=0xC035, Temp=0xC036,
                  OriginalInput=linked['symbols']['JayOriginalInput'],
                  PositionSetup=linked['symbols']['JayPositionSetup'],
                  Integrate=linked['symbols']['JayIntegrate'], StepAndPublish=0xB14E)
    if native_helpers is not None:
        step, reset = native_helpers
        fields.update(StepJayHelpers=step, ResetJayHelpers=reset)
    if pit_boundary:
        fields.update(TileStatus=0xC0F3, TileQueryY=0xC0F0,
                      EncodeTileClass=linked['symbols']['HostTile_EncodeClass'],
                      LegacyTileReject=linked['symbols']['HostTile_Reject']+3)
    constants = ''.join(f'{key} = ${value:04x}\n' for key, value in fields.items())
    assert template == bytes.fromhex('00030500020406000b0006000b00000060b00000000000000000000000030f'
                                     '0000000005060006ddc50000000000000100ff00')
    text = SOURCE.read_text().replace('TemplateBytes', ','.join(map(str, template)))
    if native_helpers is not None:
        text = text.replace(' jsr Construct\n', ' jsr ResetJayHelpers\n jsr Construct\n')
        text = text.replace(' sta Epoch\n', ' sta Epoch\n jsr StepJayHelpers\n')
        # Keep the scope branches local after the two additional calls.
        text = text.replace('Unsupported:\n clc\n rts\n\nConstruct:', 'Construct:')
        text = text.replace(' ora LevelNumber\n bne Unsupported\n',
                            ' ora LevelNumber\n beq Supported\nUnsupported:\n clc\n rts\nSupported:\n')
    if control_tail:
        text = text.replace(' jsr StepAndPublish', ' jsr AdvanceControl\n jsr StepAndPublish')
        text += '\n' + CONTROL_SOURCE.read_text()
    if native_sync:
        text = text.replace(' lda PadNow\n', ' jsr ImportNativePosition\n lda PadNow\n')
        text = text.replace(' sta PlayerYSpeed\n', ''' sta PlayerYSpeed
 lda DonorVX
 sta PlayerXSpeed
 lda DonorFlags
 and #2
 lsr A
 adc #1
 sta PlayerFacing
''')
        text += '\n' + SYNC_SOURCE.read_text()
    if pit_boundary:
        text += '\n' + PIT_SOURCE.read_text()
    work = C.HostAssemble(constants + text, {'HANDOFF': (origin, 1024)})
    return work, fields


def assemble(m, trial, *, origin=ENTRY, control_tail=False, native_sync=False, pit_boundary=False):
    ram = m.ram[3]
    work, fields = assemble_handoff(trial, bytes(ram[0x88D:0x8C0]), origin=origin,
                                    control_tail=control_tail, native_sync=native_sync,
                                    pit_boundary=pit_boundary)
    old = bytes(ram[0x785:0x8C0])
    assert old[0x2E:0x3E] == bytes.fromhex('0d1d070d1f07055cd03deaeaeaeaeaea')
    assert ram[0x1151:0x1154] == bytes.fromhex('4c34a8')
    data = work['images']['HANDOFF']
    stage = bytes(ram[:OLD_END-ACTOR])
    size = dict(handoff=len(data), origin=origin, decoded_stage=len(stage))
    if origin == ENTRY:
        assert not any(ram[0x8C0:0x785+len(data)])
        runtime = bytes(ram[:ENTRY-ACTOR]) + data
        old_packed, new_packed = (len(Cold.pack(code)) for code in (stage, runtime))
        size.update(overlay_runtime=len(runtime), old_packed=old_packed, new_packed=new_packed,
                    net_packed=new_packed-old_packed, current_carrier_spare=7)
    else:
        runtime = stage
        size.update(extension_runtime=len(data), extension_capacity=1024)
    return work, runtime, fields, size


def fixture(m, work, runtime):
    """Detached writable RAM overlay after real cold readback and authentication."""
    q = C.Vector.clone(m)
    entry = work['symbols']['PrivateUpdate']
    if entry == ENTRY:
        q.ram[3][:len(runtime)] = runtime
    else:
        at = entry - ACTOR
        data = work['images']['HANDOFF']
        assert q.ram[3][0x130E:0x1311] == bytes.fromhex('4c85a7')
        assert not any(q.ram[3][at:at+len(data)])
        q.ram[3][at:at+len(data)] = data
        q.ram[3][0x130F:0x1311] = entry.to_bytes(2, 'little')
    q.ram[3][0x1152:0x1154] = work['symbols']['PublishPosition'].to_bytes(2, 'little')
    if 'LowerTerrainGuard' in work['symbols']:
        q.ram[3][:OLD_END-ACTOR] = pit_runtime(bytes(q.ram[3][:OLD_END-ACTOR]), work)
    return q


def pit_runtime(runtime, work):
    """Retarget the exact original invalid-tile ingress; valid probes stay byte-exact."""
    assert len(runtime) == OLD_END-ACTOR
    at = C.Jay.build()['symbols']['HostTile_Reject']-ACTOR
    assert runtime[at:at+3] == bytes.fromhex('8ef3c0')
    target = work['symbols']['LowerTerrainGuard']
    return runtime[:at] + b'\x4c' + target.to_bytes(2, 'little') + runtime[at+3:]


def pit_stage(raw, runtime, work):
    """Repack the installed two-row cold stage after its three-byte terrain edit."""
    start = C.CHR + 331 * 1024
    boot = Cold.BOOT-0xD000

    def staged(code):
        stage, _, size = Cold.boot_stage(code)
        assert stage[boot:boot+3] == bytes.fromhex('4c00d0')
        return stage[:boot] + bytes.fromhex('4c00a0') + stage[boot+3:], size

    old, _ = staged(runtime)
    assert raw[start:start+2048] == old
    return staged(pit_runtime(runtime, work))


def position(m, fields):
    x = m[fields['PlayerPage']] * 256 + m[fields['PlayerX']]
    y = m[fields['PlayerYPage']] * 256 + m[fields['PlayerY']] - 256
    camera = m[fields['CameraPage']] * 256 + m[fields['CameraPixel']]
    return x, y, camera


def q4(m, fields, prefix):
    p = m.ram[2]
    return p[fields[prefix+'Hi']-0xC000] * 256 + p[fields[prefix+'Lo']-0xC000]


def control_pairs():
    """Compare control state to the original animator, stopping at pose dispatch."""
    raw = C.Donor.DONOR.read_bytes()
    assert sha256(raw).hexdigest() == C.Donor.PIN
    aliases = dict(DonorFlags=0x19, DonorControl=0x1C, DonorVX=0x14,
                   DonorControlTimer=0x51C)
    definitions = ''.join(f'{key}=${value:04x}\n' for key, value in aliases.items())
    work = C.HostAssemble(definitions + CONTROL_SOURCE.read_text(), {'HANDOFF': (0x6000, 256)})
    code = work['images']['HANDOFF']
    base = [0] * 65536
    base[0x8000:0xC000] = raw[16+6*16384:16+7*16384]
    base[0xC000:] = raw[16+7*16384:16+8*16384]
    base[0x6000:0x6000+len(code)] = code
    cases = 0
    for flags, control, timer, vx in product((0, 2, 4, 6, 8, 10, 16, 18, 128, 132),
                                            range(0, 64, 8), (0, 1, 2, 3, 4), (0, 24, 232)):
        outputs = []
        for entry in (0x8304, work['symbols']['AdvanceControl']):
            memory = base.copy()
            memory[0x19], memory[0x1C], memory[0x51C], memory[0x14] = flags, control, timer, vx
            cpu = MPU(memory=memory, pc=entry)
            cpu.stPushWord(0x5AFF)
            for _ in range(200):
                if cpu.pc in (0x5B00, 0xE46C):
                    break
                cpu.step()
            else:
                raise AssertionError(('control branch bound', flags, control, timer, vx, cpu.pc))
            outputs.append(tuple(memory[at] for at in (0x19, 0x1C, 0x51C)))
        assert outputs[0] == outputs[1], (flags, control, timer, vx, outputs)
        cases += 1
    return dict(cases=cases, bytes=len(code), original_pose_dispatch_excluded=True,
                donor_sha256=C.Donor.PIN, source_sha256=sha256(CONTROL_SOURCE.read_bytes()).hexdigest())


def coordinate_cases(seed, work, fields):
    """Exercise world/page conversions at vertical and horizontal boundaries."""
    q = C.Vector.clone(seed)
    q.raw_page(2, 2)
    N.put(q, CurrentBankC=2)
    count = 0
    for x, native_y in product((0, 15, 16, 255, 256, 511, 767, 4095),
                               (0, 15, 16, 239, 240, 255, 256, 271, 431, 432, 495, 496, 511, 4095)):
        q[fields['PlayerPage']], q[fields['PlayerX']] = divmod(x, 256)
        q[fields['PlayerYPage']], q[fields['PlayerY']] = divmod(native_y, 256)
        C.Common.invoke(q, work['symbols']['Construct'], bank=3)
        assert q4(q, fields, 'X') == x * 16
        assert q4(q, fields, 'Y') == ((native_y - 240) & 4095) * 16
        C.Common.invoke(q, work['symbols']['PublishPosition'], bank=3)
        assert q[fields['PlayerPage']] * 256 + q[fields['PlayerX']] == x
        assert q[fields['PlayerYPage']] * 256 + q[fields['PlayerY']] == native_y
        count += 1
    return dict(constructor_publisher_round_trips=count)


def support_cases(seed, work, fields):
    """Import genuine native positioning and reject incomplete support records."""
    if 'ImportNativePosition' not in work['symbols']:
        return dict(enabled=False)
    base = C.Vector.clone(seed)
    base.raw_page(2, 2)
    N.put(base, CurrentBankC=2)
    C.Common.invoke(base, work['symbols']['Construct'], bank=3)
    accepted = rejected = 0
    for slot, top in product(range(6), (176, 192, 208)):
        q = C.Vector.clone(base)
        for name, value in (('Enemy_Flag', 1), ('Enemy_ID', 0x25), ('Enemy_Y_Position', top),
                            ('Enemy_Y_HighPos', 1), ('PlatformCollisionFlag', slot)):
            q[W.address(q.bundle, name)+slot] = value
        N.put(q, Player_State=0)
        N.invoke(q, 'PositionPlayerOnVPlat', x=slot)
        assert q[fields['PlayerY']] == top-32 and q[fields['PlayerYPage']] == 1
        q.ram[2][fields['DonorFlags']-0xC000] |= 4
        q.ram[2][fields['DonorVY']-0xC000] = 60
        before = q4(q, fields, 'Y')
        for fault in (None, 'flag', 'id', 'contact', 'actor_page', 'foot_plane', 'airborne', 'velocity'):
            trial = C.Vector.clone(q)
            if fault == 'flag':
                trial[fields['EnemyFlag']+slot] = 0
            elif fault == 'id':
                trial[fields['EnemyID']+slot] = 6
            elif fault == 'contact':
                trial[fields['PlatformContact']+slot] = 255
            elif fault == 'actor_page':
                trial[fields['EnemyYPage']+slot] = 2
            elif fault == 'foot_plane':
                trial[fields['EnemyY']+slot] -= 1
            elif fault == 'airborne':
                trial[fields['PlayerState']] = 2
            elif fault == 'velocity':
                trial[fields['PlayerYSpeed']] = 1
            C.Common.invoke(trial, work['symbols']['ImportNativePosition'], bank=3)
            if fault is None:
                assert q4(trial, fields, 'Y') == (top-16)*16
                assert not trial.ram[2][fields['DonorFlags']-0xC000] & 4
                assert trial.ram[2][fields['DonorVY']-0xC000] == 0
                accepted += 1
            else:
                assert q4(trial, fields, 'Y') == before, (slot, top, fault)
                assert trial.ram[2][fields['DonorFlags']-0xC000] & 4, (slot, top, fault)
                assert trial.ram[2][fields['DonorVY']-0xC000] == 60, (slot, top, fault)
                rejected += 1
    return dict(enabled=True, actual_native_position_cases=accepted, support_fault_rejections=rejected,
                scope='Directed native positioning, with synthetic prior collision ownership')


def continued_pipe(m, fields, work, *, launch, target, updates=200, jump_hold=14):
    """Continue the same cold controller route to one later pipe."""
    samples = []
    start = None
    minimum = 176
    for update in range(updates):
        prior = position(m, fields)
        if start is None and prior[0] >= launch:
            start = update
        m.controller_pad = 1 | (128 if start is not None and update-start < jump_hold else 0)
        C.Game.frame(m)
        after = position(m, fields)
        minimum = min(minimum, after[1])
        if update % 20 == 0 or start is not None and update-start in (0, 20, 24, 28, 32, 40, 60):
            samples.append(dict(update=update, prior=prior, after=after))
        if after[0] >= target and after[1] == 176 or tuple(N.get(m, name) for name in STATES) != (1, 3, 8):
            break
    return dict(launch=launch, target=target, jump_hold=jump_hold, updates=update+1,
                terminal=after, apex=minimum, lives=N.get(m, 'NumberofLives'), samples=samples)


def directed_pit_fall(q, fields, *, boundary_fixed):
    """Start below the map's last row and follow the real native death path."""
    N.put(q, Player_Y_Position=225, Player_State=2)
    phases = {}
    for update in range(1, 161 if boundary_fixed else 61):
        q.controller_pad = 0
        C.Game.frame(q)
        engine = N.get(q, 'GameEngineSubroutine')
        lives = N.get(q, 'NumberofLives')
        phases.setdefault(engine, dict(update=update, position=position(q, fields), lives=lives))
        if lives < 2:
            break
    if boundary_fixed:
        assert lives == 1 and tuple(phases) == (8, 11, 6, 0)
    else:
        assert lives == 2 and tuple(phases) == (8,) and position(q, fields)[1] == 225
    return dict(updates=update, phases=phases, terminal=position(q, fields), lives=lives)


def assisted_route(m, fields, work):
    """Try a continuous native route through the first four pipes after cold load."""
    first = route(m, fields, work, patched=True)
    assert first['terminal'] == (505, 176, 393) and first['lives'] == 2
    trace, carry, jumps = [], [], {}
    phase = 'pipe2_approach'
    prior_fourth_top = None

    def actors():
        rows = []
        for slot in range(6):
            get = lambda name: N.get(m, name, slot)
            if get('Enemy_Flag') == 1 and get('Enemy_ID') == 37:
                rows.append((slot, get('Enemy_PageLoc')*256+get('Enemy_X_Position'),
                             get('Enemy_Y_Position'), get('PlatformCollisionFlag')))
        return rows

    def land_at(left, player_y):
        return next((row for row in actors() if row[1] == left and row[0] == row[3]
                     and row[2] == player_y+32), None)

    for update in range(600):
        x, y, camera = position(m, fields)
        if phase == 'pipe2_approach' and x >= 568:
            phase = 'pipe2_jump'
            jumps[phase] = update
        if phase == 'pipe2_jump' and update-jumps[phase] >= 14:
            phase = 'pipe2_top'
        if phase == 'pipe2_top' and x >= 625 and y == 128:
            phase = 'helper3_jump'
            jumps[phase] = update
        if phase == 'helper3_jump' and update-jumps[phase] >= 14:
            phase = 'helper3_board'
        if phase == 'helper3_board' and (platform := land_at(688, y)):
            phase = 'pipe3_jump'
            jumps[phase] = update
            carry.append(dict(pipe=3, update=update, position=(x, y, camera), platform=platform))
        if phase == 'pipe3_jump' and update-jumps[phase] >= 14:
            phase = 'pipe3_descent'
        if phase == 'pipe3_descent' and x >= 800 and y == 176:
            phase = 'helper4_approach'
        if phase == 'helper4_approach' and x >= 835:
            phase = 'helper4_wait'
        fourth = next((row for row in actors() if row[1] == 880), None)
        if (phase == 'helper4_wait' and fourth and prior_fourth_top is not None
                and fourth[2] > prior_fourth_top and fourth[2] >= 155):
            phase = 'helper4_jump'
            jumps[phase] = update
        if fourth:
            prior_fourth_top = fourth[2]
        if phase == 'helper4_jump' and update-jumps[phase] >= 14:
            phase = 'helper4_board'
        if phase == 'helper4_board' and (platform := land_at(880, y)):
            phase = 'pipe4_jump'
            jumps[phase] = update
            carry.append(dict(pipe=4, update=update, position=(x, y, camera), platform=platform))
        if phase == 'pipe4_jump' and update-jumps[phase] >= 14:
            phase = 'pipe4_descent'
        if phase == 'pipe4_descent' and x >= 995 and y == 176:
            break
        m.controller_pad = 0 if phase == 'helper4_wait' else 129 if phase.endswith('_jump') else 1
        C.Game.frame(m)
        if update % 15 == 0 or update in jumps.values():
            trace.append((update, phase, position(m, fields), actors(), N.get(m, 'Player_State')))
        if N.get(m, 'GameEngineSubroutine') != 8:
            break
    return dict(updates=update, phase=phase, terminal=position(m, fields), carry=carry,
                jump_starts=jumps, trace=trace, lives=N.get(m, 'NumberofLives'))


def late_route(m, fields, *, middle_hold=2, stop_at_middle=False):
    """Continue with native gaps, enemies, stairs and flagpole after pipe four."""
    waypoints = ((1082, 'gap1'), (1360, 'gap2'), (2428, 'gap3'), (2560, 'pipe5'),
                 (2816, 'pipe6'), (3130, 'flag'))
    gap_edges = {'gap1': (1104, 1136), 'gap2': (1376, 1424), 'gap3': (2448, 2480)}
    events, jumps = [], []
    gap_landings = {}
    phase, end_hold, furthest, advanced_at = 0, 0, 0, 0
    first_stair, stair_crossing, third_gap_cap = False, False, False
    last_scene = (1, 3, 8, 0)

    def enemies():
        rows = []
        for slot in range(6):
            get = lambda name: N.get(m, name, slot)
            if 0 < get('Enemy_Flag') < 128 and get('Enemy_ID') < 12:
                rows.append((slot, get('Enemy_ID'), get('Enemy_PageLoc')*256+get('Enemy_X_Position'),
                             get('Enemy_Y_Position'), get('Enemy_State')))
        return rows

    for update in range(2400):
        x, y, camera = position(m, fields)
        scene = tuple(N.get(m, name) for name in STATES + ('LevelNumber',))
        lives = N.get(m, 'NumberofLives')
        if scene != last_scene:
            events.append((update, 'scene', (x, y, camera), scene, lives))
            last_scene = scene
        if scene == (1, 3, 8, 1) or lives < 2 or scene[2] == 11:
            break
        if x > furthest and scene == (1, 3, 8, 0):
            advanced_at = update
            furthest = x
        if scene == (1, 3, 8, 0) and update-advanced_at >= 220:
            break
        ground = not m.ram[2][fields['DonorFlags']-0xC000] & 4
        if ground and 0 <= y <= 176 and scene == (1, 3, 8, 0):
            for _, label, _, _, _ in jumps:
                if label in gap_edges and x >= gap_edges[label][1]:
                    gap_landings.setdefault(label, (update, x, y))
        pad = 1 | (64 if update % 19 == 0 else 0)
        if update-end_hold >= 3 and ground and scene == (1, 3, 8, 0):
            upcoming = waypoints[phase] if phase < len(waypoints) else None
            reason, hold = None, 14
            if 2176 <= x < 2192 and y == 128 and not first_stair:
                if stop_at_middle:
                    break
                first_stair = True
                reason, hold = 'near-stair-cap', middle_hold
            elif first_stair and not stair_crossing and 2188 <= x < 2208 and y == 112:
                stair_crossing = True
                reason = 'paired-stair-crossing'
            elif 2398 <= x < 2416 and y == 128 and not third_gap_cap:
                third_gap_cap = True
                reason, hold = 'third-gap-cap', 2
            elif upcoming and x >= upcoming[0]:
                reason = upcoming[1]
                if reason in gap_edges and (x >= gap_edges[reason][0] or y > 176):
                    events.append((update, 'missed-gap-takeoff', reason, (x, y, camera)))
                    break
                phase += 1
            elif update-advanced_at >= 15 and update-end_hold >= 30:
                reason = 'wall-stall'
            elif not upcoming or upcoming[0]-x > 65:
                if any(20 <= row[2]-x <= 38 and abs(row[3]-y) < 25 and not row[4] & 32
                       for row in enemies()):
                    reason = 'enemy-hop'
            if reason:
                end_hold = update + hold
                jumps.append((update, reason, (x, y, camera), hold, enemies()))
        if update < end_hold:
            pad |= 128
        m.controller_pad = pad
        C.Game.frame(m)
        if update % 100 == 0:
            events.append((update, 'sample', position(m, fields), enemies(), ground))
    return dict(terminal=position(m, fields), scene=scene, lives=lives, updates=update,
                jumps=jumps, events=events, furthest=furthest, gap_landings=gap_landings)


def route(m, fields, work, *, patched, updates=440, jump_hold=12):
    totals, samples = Counter(), []
    first_scroll = first_page = None
    jump_start = None
    apex = 176
    for update in range(1, updates+1):
        prior = position(m, fields)
        m.controller_pad = 1 if update > 4 else 0
        if patched and prior[0] >= 400 and jump_start is None:
            jump_start = update
        if jump_start is not None and update - jump_start < jump_hold:
            m.controller_pad |= 128
        calls, published = Counter(), []
        native_head = W.address(m.bundle, 'JnHeadDispatch')
        tile = work['symbols']['JayHostTile'] if 'JayHostTile' in work['symbols'] else work['tile']
        status = work['status']

        def observe(memory, cpu):
            tag, pc = memory.rawtags[1], cpu.pc
            if tag == 224 and pc == 0xA2CB:
                calls['mike'] += 1
            if tag == 224 and pc == native_head:
                calls['native_head'] += 1
            if tag == 3 and pc == work['symbols']['PrivateUpdate']:
                calls['authenticated_entry'] += 1
            if tag == 3 and pc == 0xA369:
                calls['integrate'] += 1
            if tag == 3 and pc == tile:
                calls['native_terrain_query'] += 1
            if tag == 3 and pc == work['symbols']['PublishPosition']:
                calls['publish'] += 1
            if tag == 3 and pc == work['symbols']['PublishState'] + 2:
                published.append(position(m, fields))

        C.Game.frame(m, observe)
        after = position(m, fields)
        apex = min(apex, after[1])
        totals.update(calls)
        if patched and tuple(N.get(m, name) for name in STATES) == (1, 3, 8):
            assert calls['mike'] == 0 and calls['integrate'] == calls['publish'] == 1, (update, prior, after, calls)
            assert q4(m, fields, 'CameraX') == prior[2]*16, (update, prior, after, calls)
        if first_scroll is None and prior[2] > 0:
            first_scroll = dict(update=update, prior=prior, after=after, calls=dict(calls),
                                x_q4=q4(m, fields, 'X'), camera_q4=q4(m, fields, 'CameraX'))
        if first_page is None and after[0] >= 256:
            first_page = dict(update=update, prior=prior, after=after, calls=dict(calls),
                              x_q4=q4(m, fields, 'X'), camera_q4=q4(m, fields, 'CameraX'))
        if published and published[-1][:2] != after[:2]:
            totals['native_overwrite'] += 1
            if totals['native_overwrite'] <= 8:
                samples.append(dict(update=update, prior=prior, published=published[-1], after=after,
                                    status=m.ram[2][status-0xC000]))
        if update % 40 == 0 or jump_start is not None and update-jump_start < 45:
            samples.append(dict(update=update, prior=prior, after=after, calls=dict(calls)))
        if tuple(N.get(m, name) for name in STATES) != (1, 3, 8) or after[0] >= 500 and after[1] == 176:
            break
    return dict(first_scroll=first_scroll, first_page=first_page, updates=update, terminal=after,
                scene=tuple(N.get(m, name) for name in STATES), counts=dict(totals), samples=samples,
                jump_start=jump_start, jump_hold=jump_hold, apex=apex, lives=N.get(m, 'NumberofLives'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', type=lambda value: int(value, 0), default=ENTRY)
    parser.add_argument('--control-tail', action='store_true')
    parser.add_argument('--native-sync', action='store_true')
    parser.add_argument('--pit-boundary', action='store_true')
    parser.add_argument('--pipes', action='store_true')
    parser.add_argument('--assisted', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    m, trial, opening = parent()
    work, runtime, fields, size = assemble(m, trial, origin=args.origin,
                                         control_tail=args.control_tail, native_sync=args.native_sync,
                                         pit_boundary=args.pit_boundary)
    work['tile'] = C.Jay.build()['symbols']['JayHostTile']
    work['status'] = 0xC0F3
    baseline = dict(work, symbols=dict(work['symbols'], PrivateUpdate=ENTRY,
                                      PublishPosition=0xA834, PublishState=0xA88A))
    before = route(C.Vector.clone(m), fields, baseline, patched=False, updates=65)
    assert before['first_scroll']['update'] == 36 and before['first_scroll']['calls']['mike'] == 1
    q = fixture(m, work, runtime)
    coordinates = coordinate_cases(q, work, fields)
    supports = support_cases(q, work, fields)
    after = route(q, fields, work, patched=True)
    assert after['first_scroll']['calls']['integrate'] == 1
    assert after['terminal'] == (505, 176, 393) and after['lives'] == 2
    assert after['counts'].get('native_overwrite', 0) == 0
    later = {}
    if args.pipes:
        later['second'] = continued_pipe(q, fields, work, launch=568, target=670)
        assert later['second']['terminal'] == (671, 176, 559) and later['second']['lives'] == 2
        later['third_unassisted'] = continued_pipe(q, fields, work, launch=696, target=800, updates=120)
        assert later['third_unassisted']['terminal'][0] < 736
    pit = None
    if args.pit_boundary:
        old_work, old_runtime, old_fields, _ = assemble(m, trial, origin=args.origin,
                                                        control_tail=args.control_tail,
                                                        native_sync=args.native_sync)
        stage, stage_size = pit_stage(trial['raw'], bytes(m.ram[3][:OLD_END-ACTOR]), work)
        pit = dict(parent=directed_pit_fall(fixture(m, old_work, old_runtime), old_fields,
                                           boundary_fixed=False),
                   fixed=directed_pit_fall(fixture(m, work, runtime), fields, boundary_fixed=True),
                   new_stage=stage_size, stage_sha256=sha256(stage).hexdigest())
    assisted = None
    if args.assisted:
        import compose_jay_silius_1111 as Compose

        image, linked = Compose.proposal(trial['raw'])
        pin = sha256(image).hexdigest()
        cold, _, _ = parent(image, pin=pin, cookie=linked['cookie'])
        motion = dict(linked['motion'], tile=work['tile'], status=work['status'])
        assisted = assisted_route(cold, linked['motion_fields'], motion)
        assert assisted['terminal'][0] >= 995 and assisted['terminal'][1] == 176
        assert assisted['lives'] == 2 and [row['pipe'] for row in assisted['carry']] == [3, 4]
        assisted['composed_sha256'] = pin
        assisted['cookie'] = linked['cookie'].hex()
    result = dict(parent=PIN, initial_scene_tick=opening, funding=size, coordinates=coordinates,
                  support=supports, control_pairs=control_pairs() if args.control_tail else None,
                  baseline=before, candidate_fixture=after, later_pipes=later, pit_fall=pit,
                  assisted=assisted,
                  source_cpu_only=True, ROM_written=False, Mesen_run=False,
                  source_sha256={path.name:sha256(path.read_bytes()).hexdigest()
                                 for path in (SOURCE, CONTROL_SOURCE, SYNC_SOURCE, PIT_SOURCE, Path(__file__))})
    text = json.dumps(result, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + '\n')
    print(text, flush=True)


if __name__ == '__main__':
    main()

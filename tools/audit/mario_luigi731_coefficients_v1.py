"""Bounded actual731 Mario/Luigi coefficient/components audit; no native or patch."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
SOURCE = D / 'mm-proto-clean-menu-candidates-v1/clean-menu-irq'
OUT = D / 'mario-luigi731-physics-v1'
ROM = '731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c'
sys.path.insert(0, str(ROOT / 'tools/audit'))
from robots_weapon_cpu_v1 import Arena
from check_tmnt_render_oa import load, location


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p, value):
    assert not p.exists(), p
    p.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
def signed(n, bits):return n - (1 << bits) if n & (1 << (bits - 1)) else n
def q24(q, name):return signed(sum(q.get(name, i) << (8 * i) for i in range(3)), 24)
def native_vx(q):return signed(q.get('Player_X_Speed') * 256 + q.get('Player_X_MoveForce'), 16)
def coord(q, axis):return q.get('Player_' + ('PageLoc' if axis == 'X' else 'Y_HighPos')) * 256 + q.get('Player_' + axis + '_Position')


def make(b, char, mode):
    q = Arena(b, char)
    q.put(CrossoverBehaviorVersion=mode, Player_State=0, SwimmingFlag=0, AreaType=1,
          PlayerStatus=1, PlayerSize=0, Player_Y_Position=176, Player_Y_HighPos=1,
          Player_X_Position=96, Player_PageLoc=1, Player_CollisionBits=3,
          PlayerFacingDir=1, Player_MovingDir=1, Player_X_Speed=0,
          Player_XSpeedAbsolute=0, A_B_Buttons=0, PreviousA_B_Buttons=0,
          SavedJoypadBits=0, Left_Right_Buttons=0, Up_Down_Buttons=0)
    if char == 0:q.set('MarioSourceActive', 1)
    return q


def seed_vx(q, char, speed):
    q.put(Player_X_Speed=int(speed * 16) & 255, Player_XSpeedAbsolute=int(abs(speed) * 16))
    if char == 0:
        v = round(speed * 65536)
        q.array('MmVX', [(v >> (8 * i)) & 255 for i in range(3)])
        q.set('MmLastXSpeed', int(speed * 16) & 255)


def movement(q, buttons):
    q.put(SavedJoypadBits=buttons, A_B_Buttons=buttons & 192,
          Left_Right_Buttons=buttons & 3, Up_Down_Buttons=buttons & 12)
    q.invoke('PlayerMovementSubs')
    q.set('PreviousA_B_Buttons', buttons & 192)
    if q.get('Player_X_Speed'):
        q.set('Player_MovingDir', 2 if q.get('Player_X_Speed') >= 128 else 1)
    if q.get('RunningTimer'):q.set('RunningTimer', q.get('RunningTimer') - 1)
    q.set('FrameCounter', (q.get('FrameCounter') + 1) & 255)


def run():
    assert sha(SOURCE / 'candidate.nes') == ROM
    manifest = json.loads((SOURCE / 'source-manifest.json').read_text())
    source_names = ['src/player.s', 'src/mario_source.s', 'src/luigi_native.s',
                    'src/megaman_physics.s', 'src/characters.s', 'src/common.s', 'src/water.s']
    bindings = {str(SOURCE / 'source' / name): manifest[name] for name in source_names}
    for f, h in bindings.items():assert sha(f) == h, f
    b = load(SOURCE / 'candidate.nes');OUT.mkdir(exist_ok=False)
    tables = {}
    for name, expected in [('JumpMForceData', [32, 32, 30, 40, 40, 13, 4]),
                           ('FallMForceData', [112, 112, 96, 144, 144, 10, 9]),
                           ('PlayerYSpdData', [252, 252, 252, 251, 251, 254, 255]),
                           ('InitMForceData', [0, 0, 0, 0, 0, 128, 0]),
                           ('MaxLeftXSpdData', [216, 232, 240]),
                           ('MaxRightXSpdData', [40, 24, 16, 12]),
                           ('FrictionData', [228, 152, 208])]:
        offset = location(b, name);actual = list(b['raw'][offset:offset + len(expected)])
        assert actual == expected, (name, actual)
        tables[name] = dict(bytes=actual, file_offset=offset)
    put(OUT / 'compiled-native-tables.json', tables)

    helpers = dict(gravity=[], Mario_jumps=[], native_Luigi_jump_classes=[], traction=[], multipliers=[], caps=[])
    for mode, rise in itertools.product([0, 1], [0, 1]):
        q = make(b, 0, mode);q.set('MarioJumpRise', rise);cpu, _ = q.invoke('MarioSourceGravity')
        value = cpu.a + 256 * cpu.y
        assert value == (0 if rise else [12743, 13653][mode])
        helpers['gravity'].append(dict(mode=mode, rise=rise, Q0_16=value, pixels_per_update_squared=value / 65536))
    for mode, speed in itertools.product([0, 1], [0, 2.5]):
        q = make(b, 0, mode);seed_vx(q, 0, speed);q.invoke('MarioSourceJump')
        value = q24(q, 'MmVY');expected = [[-354987, -382293], [-218453, -229376]][mode][int(speed == 2.5)]
        assert value == expected
        helpers['Mario_jumps'].append(dict(mode=mode, horizontal_speed=speed, Q8_16=value,
            pixels_per_update=value / 65536, rise_flag=q.get('MarioJumpRise'),
            source_target_rise=432 - coord(q, 'Y') if mode == 0 else 432 - (q.get('MarioJumpEndHigh') * 256 + q.get('MarioJumpEnd'))))
    for mode, speed in itertools.product([0, 1], [0, 8, 9, 15, 16, 24, 25, 27, 28, 40]):
        q = make(b, 8, mode);q.put(Player_XSpeedAbsolute=speed, A_B_Buttons=128)
        q.invoke('PlayerPhysicsSub')
        idx = sum(speed >= boundary for boundary in [9, 16, 25, 28])
        vy = signed(q.get('Player_Y_Speed') * 256 + q.get('Player_Y_MoveForce'), 16)
        assert vy == (-1075 if idx < 3 else -1331)
        assert q.get('VerticalForce') == [32, 32, 30, 40, 40][idx]
        assert q.get('VerticalForceDown') == [112, 112, 96, 144, 144][idx]
        assert q.get('DiffToHaltJump') == 1
        helpers['native_Luigi_jump_classes'].append(dict(mode=mode, speed_abs_native_units=speed, jump_class=idx,
            Q8_8_initial_vy=vy, pixels_per_update=vy / 256, held_gravity=q.get('VerticalForce') / 256,
            released_falling_gravity=q.get('VerticalForceDown') / 256, native_minimum_rise_before_release=1))
    for force, direction in itertools.product([152, 228, 208, 304, 456], [0, 1, 2]):
        q = make(b, 8, 0);q.put(Player_X_Speed=20, Left_Right_Buttons=direction,
                               FrictionAdderLow=force & 255, FrictionAdderHigh=force >> 8)
        q.invoke('LuigiNativeTraction');actual = q.get('FrictionAdderLow') + 256 * q.get('FrictionAdderHigh')
        assert actual == (force if direction == 1 else force - (force >> 3))
        helpers['traction'].append(dict(initial_force=force, rightward_direction_bits=direction,
            resulting_force=actual, pixels_per_update_squared=actual / 4096))
    for name, expected in [('MarioWaterCoast', 62344), ('SamusFrictionY', 56210),
                           ('LuigiRunFrictionX', 61399), ('MmFrictionY', 52057)]:
        q = make(b, 0, 0);q.array('MmMul', [0, 0, 1]);q.invoke(name)
        actual = q24(q, 'MmMul');assert actual == expected
        helpers['multipliers'].append(dict(actual_helper=name, Q0_16=actual, factor=actual / 65536))
    for mode, buttons, air in itertools.product([0, 1], [0, 64], [0, 1]):
        q = make(b, 0, mode);seed_vx(q, 0, 4);q.put(SavedJoypadBits=buttons, Player_State=air)
        q.invoke('MarioSourceClamp');value = q24(q, 'MmVX')
        assert value == (163840 if buttons else [81920, 95573][mode])
        helpers['caps'].append(dict(mode=mode, B_held=bool(buttons), airborne=bool(air), cap_Q8_16=value, cap=value / 65536))
    put(OUT / 'actual-compiled-helpers.json', helpers)

    jump_rows = []
    for char, mode, speed, release in itertools.product([0, 8], [0, 1], [0, 1.25, 2.5], [None, 1, 8]):
        q = make(b, char, mode);seed_vx(q, char, speed);path = []
        for t in range(180):
            movement(q, 128 if release is None or t < release else 0)
            path.append(dict(update=t + 1, x=coord(q, 'X'), y=coord(q, 'Y'),
                native_vy= q.get('Player_Y_Speed'), Q8_16_vy=q24(q, 'MmVY') if char == 0 else None))
            if t > 0 and path[-1]['y'] >= 432:break
        else:raise AssertionError('No isolated return crossing')
        minimum = min(z['y'] for z in path)
        jump_rows.append(dict(character=char, mode=mode, initial_horizontal_speed=speed, A_held_updates=release,
            rise_pixels=432 - minimum, first_apex_update=next(z['update'] for z in path if z['y'] == minimum),
            return_crossing_update=len(path), path=path))
    held = [r for r in jump_rows if r['A_held_updates'] is None]
    assert [r['rise_pixels'] for r in held] == [73, 73, 85, 68, 68, 84, 73, 78, 90, 73, 78, 90]
    put(OUT / 'isolated-jump-trajectories.json', jump_rows)

    horizontal = []
    for char, mode, running in itertools.product([0, 8], [0, 1], [False, True]):
        q = make(b, char, mode);path = [];target = 2.5 if running else (1.5 if char == 8 else [1.25, 95573 / 65536][mode])
        for t in range(150):
            movement(q, 1 | (64 if running else 0))
            value = q24(q, 'MmVX') / 65536 if char == 0 else signed(q.get('Player_X_Speed'), 8) / 16
            path.append(dict(update=t + 1, x=coord(q, 'X'), source_velocity=value,
                full_native_velocity_accumulator=native_vx(q) / 4096 if char == 8 else None))
        assert path[-1]['source_velocity'] == target
        horizontal.append(dict(character=char, mode=mode, B_held=running, nominal_cap=target,
            first_cap_update=next(z['update'] for z in path if z['source_velocity'] == target), path=path))
    coast = []
    for char, mode in itertools.product([0, 8], [0, 1]):
        q = make(b, char, mode);seed_vx(q, char, 2.5)
        if char == 0:q.set('MarioRunCap', 1)
        path = []
        for t in range(150):
            movement(q, 0)
            value = q24(q, 'MmVX') / 65536 if char == 0 else signed(q.get('Player_X_Speed'), 8) / 16
            path.append(dict(update=t + 1, x=coord(q, 'X'), velocity=value,
                             retained_native_fraction=q.get('Player_X_MoveForce') if char == 8 else None))
            if value == 0:break
        else:raise AssertionError('No isolated horizontal stop')
        coast.append(dict(character=char, mode=mode, first_visible_stop_update=len(path),
                          displacement=coord(q, 'X') - 352, path=path))
    put(OUT / 'isolated-horizontal-components.json', dict(acceleration_to_cap=horizontal, coast=coast))

    falls = []
    for char, mode in itertools.product([0, 8], [0, 1]):
        q = make(b, char, mode);q.put(Player_State=2, VerticalForceDown=112);path = []
        for t in range(80):
            movement(q, 0)
            velocity = q24(q, 'MmVY') / 65536 if char == 0 else signed(q.get('Player_Y_Speed') * 256 + q.get('Player_Y_MoveForce'), 16) / 256
            path.append(dict(update=t + 1, y=coord(q, 'Y'), post_gravity_velocity=velocity))
        assert max(z['post_gravity_velocity'] for z in path) == (5 if char == 0 else 4.4375)
        falls.append(dict(character=char, mode=mode, path=path))
    put(OUT / 'isolated-fall-components.json', falls)
    for p in [Path(__file__), SOURCE / 'candidate.nes', SOURCE / 'candidate.dbg', SOURCE / 'source-manifest.json']:
        bindings[str(p)] = sha(p)
    for name in ['robots_weapon_cpu_v1.py', 'check_tmnt_render_oa.py', 'verify_native_relocation.py']:
        bindings[str(ROOT / 'tools/audit' / name)] = sha(ROOT / 'tools/audit' / name)
    for p in OUT.iterdir():bindings[str(p)] = sha(p)
    put(OUT / 'proof.json', dict(passed=True, native_executed=False, game_source_modified=False,
        ROM_sha256=ROM, bindings=bindings, compiled_table_count=7,
        helper_component_cases=sum(len(v) for v in helpers.values()), actual_movement_jump_cases=len(jump_rows),
        actual_horizontal_cases=len(horizontal) + len(coast), actual_fall_cases=len(falls),
        scope='Actual assembled 6502 components in explicit isolated states. PlayerMovementSubs plus documented controller/history/moving-dir/running-timer bookkeeping; no terrain/actor collision, landing, PlayerCtrlRoutine, audio, IRQ, NMI, PPU or physical-frame simulation. Counts are updates, not native video frames.'))
    print(json.dumps(dict(passed=True, proof_sha256=sha(OUT / 'proof.json'), jump_cases=len(jump_rows),
        held_jump_summary=[{k:v for k,v in r.items() if k != 'path'} for r in held],
        horizontal_summary=[{k:v for k,v in r.items() if k != 'path'} for r in horizontal],
        coast_summary=[{k:v for k,v in r.items() if k != 'path'} for r in coast]), indent=2))


def freeze():
    q = json.loads((OUT / 'proof.json').read_text());assert q['passed'] and not q['native_executed']
    for f, h in q['bindings'].items():assert sha(f) == h, f
    bindings = dict(q['bindings'])
    for p in [OUT / 'proof.json', ROOT / 'docs/qa/mario-luigi731-physics-2026-10-26.txt']:
        bindings[str(p)] = sha(p)
    put(OUT / 'final-proof.json', dict(passed=True, source_CPU_only=True, ROM_sha256=ROM, bindings=bindings,
        game_or_installed_source_modified=False, native_executed=False, recommendation_only=True))
    print(json.dumps(dict(passed=True, bindings=len(bindings), final_proof_sha256=sha(OUT / 'final-proof.json')), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('--freeze', action='store_true');a = p.parse_args()
    freeze() if a.freeze else run()

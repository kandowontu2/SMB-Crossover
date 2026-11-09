"""Exercise Getsu's source movement inside the current host's real collision loop."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

from check_getsu_fuma_motion_1110 import NAMES, SOURCE, SWORD
from check_mega_giant_geometry_1110_v1 import M, R, address, bundle, sha
from check_mega_giant_ppu_mapping_1110_v1 import start_stage
from prepare_mini_side_alias_1108 import compare_memory


HOST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN = 'c8bd2e2c75015b84fe7bc3c4dba5b24b87e517620ef914ff229b5d4249acbe48'
BRIDGE = R / 'tools/reference/getsu_fuma_host_motion_1110.s'
HOST_SWORD = R / 'tools/reference/getsu_fuma_host_sword_1110.s'
MOVE_PC, MOVE_BANK = 0xa5d7, 1
ENEMY_PC, ENEMY_BANK = 0x9659, 126
SIDE_PC, SIDE_BANKS = 0xe497, (119, 120, 125, 127)
BASE, STATE, STOP = 0x5600, 0x5b40, 0x5b00
FIELDS = NAMES + ('Initialized PreviousPad Fresh CrouchTime XFrac IssuedXSpeed IssuedYSpeed '
                 'SwordX SwordPage SwordYBias SwordDifference').split()
LOCAL = {name: STATE + i for i, name in enumerate(FIELDS)}
FIXTURE = '''
.segment "GETSU_FIXTURE"
.export GfFixtureEntry, GfFixtureEnemy, GfFixtureSide
GfFixtureEntry:
    php
    pha
    jsr GfHostMove
    bcc Original
    pla
    plp
    rts
Original:
    pla
    plp
    lda SelectedCharacter
    jmp $a5da

GfFixtureEnemy:
    lda SelectedCharacter
    cmp #42
    bne ForeignEnemy
    lda SelectedCharacter
    jsr NativeEnemy
    php
    pha
    txa
    pha
    tya
    pha
    ldx ObjectOffset
    jsr GfHostSwordContact
    pla
    tay
    pla
    tax
    pla
    plp
    rts
ForeignEnemy:
    lda SelectedCharacter
NativeEnemy:
    jmp $965c

GfFixtureSide:
    php
    pha
    lda SelectedCharacter
    cmp #42
    bne ForeignSide
    pla
    plp
    jmp $958b
ForeignSide:
    pla
    plp
    jmp $90e4
'''


def assemble(output, b):
    source = '\n'.join(p.read_text(encoding='utf-8') for p in (BRIDGE, HOST_SWORD, SOURCE, SWORD))
    names = {name for line in source.splitlines() if line.startswith('.import ')
             for name in line.removeprefix('.import ').split(', ')}
    definitions = {**{'Gf' + name: value for name, value in LOCAL.items()},
                   'GfStateStart': STATE, 'GfStateSize': len(LOCAL)}
    definitions.update({name: address(b, name) for name in names - definitions.keys()
                        if not name.startswith('Gf')})
    unresolved = names - definitions.keys()
    assert unresolved == {'GfHorizontalSpeed', 'GfJumpStart', 'GfVerticalSpeed', 'GfIntegrateY',
                          'GfSwordStart', 'GfSwordAdvance'}
    with tempfile.TemporaryDirectory(prefix='link-', dir=output) as directory:
        out = Path(directory)
        src, obj, cfg, binary, labels = (out / f'host.{ext}' for ext in ('s', 'o', 'cfg', 'bin', 'lbl'))
        defs = ''.join(f'{name}=${value:04x}\n' for name, value in definitions.items())
        body = re.sub(r'^\.(?:import .+|macpack longbranch)\n', '', source, flags=re.M)
        src.write_text('.macpack longbranch\n' + defs + FIXTURE + body)
        cfg.write_text('MEMORY { M:start=$5600,size=$500,file=%O; } SEGMENTS { '
                       'GETSU_FIXTURE:load=M,type=ro; GETSU_HOST_MOTION:load=M,type=ro; '
                       'GETSU_HOST_SWORD:load=M,type=ro; '
                       'GETSU_MOTION:load=M,type=ro; GETSU_SWORD:load=M,type=ro; }\n')
        cc = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', src, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
        symbols = {line.split()[2][1:]: int(line.split()[1], 16) for line in labels.read_text().splitlines()}
        code = binary.read_bytes()
        assert symbols['GfFixtureEntry'] == BASE and BASE + len(code) < STOP
        return code, symbols


def prepare(seed, code, symbols, native_side=False):
    before, after = M.fork(seed), M.fork(seed)
    for m in (before, after):
        m[BASE:BASE + len(code)] = code
    raw = bytearray(after.bundle['raw'])
    hooks = [(MOVE_BANK, MOVE_PC, 'GfFixtureEntry', 'ad0260'),
             (ENEMY_BANK, ENEMY_PC, 'GfFixtureEnemy', 'ad0260')]
    if native_side:
        hooks.extend((bank, SIDE_PC, 'GfFixtureSide', '4ce490') for bank in SIDE_BANKS)
    for bank, pc, name, preimage in hooks:
        off = 16 + bank * 8192 + (pc & 8191)
        assert raw[off:off + 3] == bytes.fromhex(preimage)
        dest = symbols[name]
        raw[off:off + 3] = bytes((0x4c, dest & 255, dest >> 8))
    after.bundle = dict(after.bundle, raw=bytes(raw))
    after.raw_page(1, 0x81)
    after.raw_page(0, 0xfe)
    if native_side:
        after.raw_page(3, after.rawtags[3])
        assert after[SIDE_PC] == 0x4c and after[SIDE_PC+1] == symbols['GfFixtureSide'] & 255
    return before, after


def position(m):
    x = M.get(m, 'Player_X_Position') + 256 * M.get(m, 'Player_PageLoc')
    y = M.get(m, 'Player_Y_Position') + 256 * (M.get(m, 'Player_Y_HighPos') - 1)
    return x, y


def frame(m, keys, symbols, goal_contacts=None):
    M.put(m, SavedJoypadBits=keys, SavedJoypad1Bits=keys, SavedJoypad2Bits=0, NmiDisable=255)
    cpu = M.NesMPU(memory=m, pc=address(m.bundle, 'GameLoop'))
    cpu.p, cpu.sp = 0x31, 252
    cpu.stPushWord(STOP - 1)
    counts = dict(movement=0, background=0, scroll=0)
    for _ in range(70_000):
        if cpu.pc == STOP:
            break
        if cpu.pc == symbols['GfHostMove']:
            counts['movement'] += 1
        elif cpu.pc == 0x9b5b and m.rawtags[0] == 254:
            counts['background'] += 1
        elif cpu.pc == 0xa9d4 and m.rawtags[1] == 129:
            counts['scroll'] += 1
        elif goal_contacts is not None and cpu.pc in (0xe497, symbols['GfFixtureSide'], 0x958b, 0x9cb6, 0x9e2d, 0x9e47):
            if len(goal_contacts) < 160:
                goal_contacts.append(dict(pc=cpu.pc, prg_tags=list(m.rawtags), x=position(m)[0], y=position(m)[1],
                                          a=cpu.a, index=cpu.y, probe_nibble=m[7], block_column=m[9],
                                          terrain_row=m[5], tile=m[6]))
        assert m[cpu.pc], ('native GameLoop BRK', hex(cpu.pc), m.rawtags, position(m), counts)
        cpu.step()
    else:
        raise AssertionError(('GameLoop step limit', hex(cpu.pc)))
    assert cpu.sp == 252
    M.consume(m)
    return counts


def native_solid(m, x, y):
    if not 32 <= y < 240:
        return False
    tile_address = 0x300 + ((x >> 8) & 1) * 0xd0 + (y & 0xf0) - 32 + ((x >> 4) & 15)
    return bool(m[0xef36 + m[tile_address]] & 1)


def actors(m):
    return [dict(slot=slot, flag=M.get(m, 'Enemy_Flag', slot), id=M.get(m, 'Enemy_ID', slot),
                 state=M.get(m, 'Enemy_State', slot),
                 x=M.get(m, 'Enemy_X_Position', slot) + 256 * M.get(m, 'Enemy_PageLoc', slot),
                 y=M.get(m, 'Enemy_Y_Position', slot))
            for slot in range(6) if 0 < M.get(m, 'Enemy_Flag', slot) < 128]


def goal_view(m, x, y):
    left = M.get(m, 'ScreenLeft_X_Pos') + 256 * M.get(m, 'ScreenLeft_PageLoc')
    tiles = []
    for col in range(x // 16 - 2, x // 16 + 5):
        at = 0x300 + (0xd0 if col & 16 else 0) + (col & 15)
        rows = [m[at + 16 * row] for row in range(13)]
        tiles.append(dict(world_x=16 * col, column=bytes(rows).hex()))
    return dict(x=x, y=y, camera_left=left, local_x=M.get(m, 'Player_Rel_XPos'),
                engine=M.get(m, 'GameEngineSubroutine'), tiles=tiles, actors=actors(m))


def route(m, symbols, all_pipes, full_stage, flag_takeoff=None):
    M.put(m, SelectedCharacter=42)  # Private fixture admission after the real stage entrance.
    rows, jump_starts, native_calls = [], [], dict(movement=0, background=0, scroll=0)
    pipes = [(448, 176, 404)]
    if all_pipes:
        pipes += [(608, 160, 563), (736, 144, 679), (912, 144, 855)]
    pits = [(1104, 1136), (1376, 1424), (2448, 2480)] if full_stage else []
    cap_witness = {}
    pit_witness = {}
    launched = set()
    jump = 0
    y_min = 256
    max_x = 0
    before_contact = None
    goal_samples = []
    goal_contacts = []
    next_goal_sample = 3040
    try:
        for tick in range(3500 if full_stage else 1000):
            x, y = position(m)
            max_x = max(x, max_x)
            if full_stage and next_goal_sample <= x < 3380 and len(goal_samples) < 24:
                goal_samples.append(goal_view(m, x, y))
                next_goal_sample += 16
            grounded = M.get(m, 'Player_State') == 0
            for left, top, _ in pipes:
                if left <= x + 8 < left + 32 and y + 32 <= top:
                    cap_witness.setdefault(left, dict(update=tick, x=x, y=y, top=top))
            for left, right in pits:
                if left <= x + 8 < right and y <= 176 and not grounded:
                    pit_witness.setdefault(left, dict(update=tick, x=x, y=y, right=right))
            stage_advanced = M.get(m, 'WorldNumber') == 0 and M.get(m, 'LevelNumber') == 1
            done = stage_advanced and M.get(m, 'GameEngineSubroutine') == 8 if full_stage else (
                x >= pipes[-1][0] + 38 and y == 176 and grounded)
            if done:
                assert set(cap_witness) == {p[0] for p in pipes}, cap_witness
                assert set(pit_witness) == {p[0] for p in pits}, pit_witness
                return dict(passed=True, updates=tick, terminal=[x, y], min_y=y_min,
                            max_x=max_x, full_stage=full_stage, launch=jump_starts,
                            cap_witness=cap_witness, pit_witness=pit_witness,
                            native_calls=native_calls, samples=rows, goal_samples=goal_samples,
                            goal_contacts=goal_contacts)
            if full_stage and x >= 3500 and not stage_advanced:
                raise AssertionError('passed the flag area without a native stage transition')
            near = actors(m)
            jump_gap = 34 if full_stage and x > 970 else 43
            threat = any(a['id'] <= 6 and not a['state'] & 32 and
                         23 <= a['x'] - x <= jump_gap and abs(a['y'] - y - 8) < 24 for a in near)
            next_pipe = next((left for left, _, takeoff in pipes
                              if left not in launched and takeoff <= x < left - 6), None)
            next_pit = next((left for left, _ in pits if left not in launched and left - 30 <= x < left), None)
            late_wall = full_stage and 970 < x < 3100 and native_solid(m, x + 25, y + 24)
            combat = threat and (x < 380 or full_stage and 970 < x < 3100)
            target = next_pipe if next_pipe is not None else next_pit
            if flag_takeoff is not None and flag_takeoff <= x < 3176 and 3168 not in launched:
                target = 3168
            if grounded and jump == 0 and (target is not None or combat or late_wall):
                jump = 23
                if target is not None:
                    launched.add(target)
                jump_starts.append(dict(update=tick, world_x=x, y=y, target=target))
            keys = 1 | (0x80 if jump else 0)
            active = M.get(m, 'GameEngineSubroutine') == 8
            before_contact = dict(update=tick, x=x, y=y, state=M.get(m, 'Player_State'),
                                  keys=keys, actors=near)
            counts = frame(m, keys, symbols, goal_contacts if 3153 <= x <= 3172 else None)
            if active and not stage_advanced:
                assert counts == dict(movement=1, background=1, scroll=1), counts
            for name, count in counts.items():
                native_calls[name] += count
            jump = max(jump - 1, 0)
            y_min = min(y_min, y)
            if tick % (32 if full_stage else 16) == 0:
                rows.append(dict(update=tick, x=x, y=y, state=M.get(m, 'Player_State'),
                                 action=m[LOCAL['Action']], vx=m[LOCAL['VXHi']], vy=m[LOCAL['VYHi']],
                                 lives=M.get(m, 'NumberofLives'), keys=keys))
            engine = M.get(m, 'GameEngineSubroutine')
            assert engine != 11 and (full_stage or engine == 8) and M.get(m, 'NumberofLives') == 2, (engine, x, y)
    except AssertionError as error:
        return dict(passed=False, reason=str(error), terminal=position(m), launch=jump_starts,
                    cap_witness=cap_witness, pit_witness=pit_witness, native_calls=native_calls,
                    pre_terminal=before_contact, terminal_actors=actors(m), samples=rows,
                    goal_samples=goal_samples, goal_contacts=goal_contacts)
    return dict(passed=False, reason='route bound', terminal=position(m), launch=jump_starts,
                cap_witness=cap_witness, pit_witness=pit_witness, native_calls=native_calls,
                samples=rows, goal_samples=goal_samples, goal_contacts=goal_contacts)


def crouch_sword(m, symbols):
    M.put(m, SelectedCharacter=42)
    poses, cues = set(), []
    for tick in range(40):
        keys = (4 if tick < 29 else 0) | (0x40 if tick == 2 else 0)
        counts = frame(m, keys, symbols)
        assert counts == dict(movement=1, background=1, scroll=1)
        assert M.get(m, 'GameEngineSubroutine') == 8 and M.get(m, 'NumberofLives') == 2
        if m[LOCAL['SwordActive']]:
            assert M.get(m, 'CrouchingFlag') == 4
            poses.add(m[LOCAL['SwordPose']])
        if m[LOCAL['SwordCue']]:
            cues.append(m[LOCAL['SwordCue']])
    assert poses >= {7, 8, 9, 10, 11} and cues == [0x25]
    assert not m[LOCAL['SwordActive']] and not M.get(m, 'CrouchingFlag')
    return dict(updates=40, poses=sorted(poses), cue=cues[0], source_crouch_released=True)


def defeat_first_goomba(m, symbols):
    M.put(m, SelectedCharacter=42)
    attack = None
    for tick in range(260):
        x, y = position(m)
        goomba = next((a for a in actors(m) if a['id'] == 6), None)
        keys = 1
        if attack is None and goomba is not None and 36 <= goomba['x'] - x <= 45:
            keys |= 0x40
            attack = dict(update=tick, x=x, y=y, target=goomba)
        frame(m, keys, symbols)
        assert M.get(m, 'GameEngineSubroutine') == 8 and M.get(m, 'NumberofLives') == 2
        if attack is not None and goomba is not None and M.get(m, 'Enemy_State', goomba['slot']) & 32:
            assert not goomba['state'] & 32 and m[LOCAL['SwordActive']]
            assert m[LOCAL['SwordPhase']] >= 2
            return dict(attack=attack, hit_update=tick, target_before=goomba,
                        source_phase=m[LOCAL['SwordPhase']], final_lives=M.get(m, 'NumberofLives'))
    raise AssertionError(('Fresh B did not defeat the natural first Goomba', position(m), attack, actors(m)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--all-pipes', action='store_true')
    parser.add_argument('--full-stage', action='store_true')
    parser.add_argument('--flag-takeoff', type=int)
    parser.add_argument('--native-side', action='store_true')
    args = parser.parse_args()
    assert sha(HOST) == PIN
    b = bundle(HOST.read_bytes())
    output = args.output.resolve()
    assert output.is_relative_to(R / 'build')
    output.mkdir(exist_ok=True)
    code, symbols = assemble(output, b)
    seed, boot = start_stage(b)
    before, after = prepare(seed, code, symbols, args.native_side)
    left, right = M.fork(before), M.fork(after)
    for keys in (0, 1, 2, 0x80, 0x40, 0, 4, 0x81):
        frame(left, keys, symbols)
        frame(right, keys, symbols)
        compare_memory(left, right)
    crouch = crouch_sword(M.fork(after), symbols)
    combat = defeat_first_goomba(M.fork(after), symbols)
    witness = route(after, symbols, args.all_pipes or args.full_stage, args.full_stage, args.flag_takeoff)
    q = dict(passed=witness['passed'], source_CPU_only=True, ROM_written=False, current_ROM_SHA256=PIN,
             fixture_component_bytes=len(code), fixture_component_SHA256=hashlib.sha256(code).hexdigest(),
             private_admission=42, renderer_installed=False, native_side=args.native_side, native_boot=boot,
             unchanged_Mario_updates=8, crouch_sword=crouch, goomba_sword=combat, route=witness,
             bindings={str(p.relative_to(R)): sha(p) for p in (Path(__file__), BRIDGE, HOST_SWORD, SOURCE, SWORD)})
    (output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in witness.items() if key not in ('samples', 'goal_samples')}))
    raise SystemExit(0 if witness['passed'] else 1)


if __name__ == '__main__':
    main()

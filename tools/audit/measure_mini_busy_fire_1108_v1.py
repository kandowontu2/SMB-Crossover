"""Source-linked CPU-only measurement of two native Mini busy-frame reductions."""

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import re

from py65.devices.mpu6502 import MPU

from prepare_mini_mario_chr_override_1103_v39 import assemble
from prepare_mini_mario_native_power_1103_v56 import N, address, bundle, location


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'build/mini-two-fireballs-1103/mini-empty-draw.nes'
PIN = '244734bbc2690b4e97e654cc72f8f153bedbe3fcc799f714e9508784e4f33af4'
OBJECT = ROOT / 'src/object.s'
COMMON = ROOT / 'src/common.s'
sha = lambda data: hashlib.sha256(data).hexdigest()


def source_proc(path, name):
    source = path.read_text()
    body, = re.findall(rf'^\.proc {name}\n(.*?)^\.endproc$', source, re.M | re.S)
    return body


def source_match(image, output, name, start, body, symbols):
    declarations = ''.join(f'{n} = ${address(image, n):04x}\n' for n in symbols)
    source = declarations + body
    data, _ = assemble(output / name, source, start, 0x2000 - (start & 0x1fff))
    return data


def extent(raw, bank, start, data, role):
    offset = 16 + bank * 8192 + (start & 8191)
    return dict(bank=bank, pc=start, offset=offset, preimage=raw[offset:offset+len(data)].hex(),
                replacement=data.hex(), role=role)


def fire_patches(image, output):
    raw = image['raw']
    start = address(image, 'FireballEnemyCollision')
    symbols = ('Fireball_State', 'FrameCounter', 'R1', 'Enemy_State', 'Enemy_Flag',
               'Enemy_ID', 'Goomba', 'EnemyOffscrBitsMasked', 'SprObjectCollisionCore',
               'ObjectOffset', 'HandleEnemyFBallCol')
    old = source_proc(OBJECT, 'FireballEnemyCollision')
    old_data = source_match(image, output, 'fire-original', start, old, symbols)
    prefix = old.split('FireballEnemyCDLoop:')[0]
    # Public caller FireballObjCore supplies slot 0 or 1. Its second ASL clears C.
    assert prefix.count('  clc\n') == 1
    prefix = prefix.replace('  clc\n', '')
    new = prefix + '''FireballEnemyCDLoop:
  stx R1
  lda Enemy_Flag,x
  beq NextEnemy
  lda Enemy_State,x
  and #%00100000
  bne NextEnemy
  lda Enemy_ID,x
  cmp #$24
  bcc GoombaDie
  cmp #$2b
  bcc NextEnemy
GoombaDie:
  cmp #Goomba
  bne NotGoomba
  lda Enemy_State,x
  cmp #$02
  bcs NextEnemy
NotGoomba:
  lda EnemyOffscrBitsMasked,x
  bne NextEnemy
  tya
  pha
  txa
  asl
  asl
  clc
  adc #$04
  tax
  jsr SprObjectCollisionCore
  bcc RestoreEnemy
  ldx ObjectOffset
  lda #%10000000
  sta Fireball_State,x
  ldx R1
  jsr HandleEnemyFBallCol
RestoreEnemy:
  pla
  tay
  ldx R1
NextEnemy:
  dex
  bpl FireballEnemyCDLoop
  tya
ExitFBallEnemy:
  ldx ObjectOffset
  rts
'''
    data = source_match(image, output, 'fire-successor', start, new, symbols)
    patch = extent(raw, 0, start, data, 'Original native FireballEnemyCollision footprint')
    assert len(data) == len(old_data) == 93
    assert bytes.fromhex(patch['preimage']) == old_data
    entry = location(image, 'FireballObjCore')
    # Reconfirm actual shared caller, and zero other source or linked symbol ingress.
    call = bytes((0x20, start & 255, start >> 8))
    assert raw[entry:entry+150].count(call) == 1
    assert [line.strip() for line in OBJECT.read_text().splitlines() if 'FireballEnemyCollision' in line] == [
        'jsr FireballEnemyCollision   ;do fireball to enemy collision detection and deal with collisions',
        '.proc FireballEnemyCollision',
    ]
    return patch


def y_patches(image, output):
    raw = image['raw']
    start = address(image, 'GetYOffscreenBits')
    helper = address(image, 'DividePDiff')
    assert (start, helper, address(image, 'TransposePlayers')) == (0x8b73, 0x8bc6, 0x8bdb)
    source = source_proc(COMMON, 'GetYOffscreenBits')
    old = source_match(image, output, 'offscreen-original', start, source,
                       ('R4', 'R5', 'R6', 'R7', 'SprObject_Y_Position', 'SprObject_Y_HighPos'))
    assert len(old) == helper - start
    assert raw[location(image, 'GetYOffscreenBits'):location(image, 'DividePDiff')] == old
    obsolete = source_proc(COMMON, 'DividePDiff')
    old_helper = source_match(image, output, 'retired-divider', helper, obsolete, ('R5', 'R6', 'R7'))
    assert len(old_helper) == 21
    usages = [(p.name, line.strip()) for p in (ROOT / 'src').rglob('*.s')
              for line in p.read_text(encoding='utf-8', errors='replace').splitlines()
              if re.search(r'\bDividePDiff\b', line.split(';')[0])]
    assert usages == [('common.s', '.proc DividePDiff')], usages
    # The vertical unit's top pass at high 1 is always zero. Even at low 0
    # where it writes R5/R6, the bottom pass writes those same values again.
    # Normal gameplay retains the original bottom pass with the original V/C.
    replacement = f'''  stx R4
  ldy #1
  lda SprObject_Y_HighPos,x
  cmp #1
  bne :+
  dey
: jmp ${start+4:04x}
  .res {len(old_helper)}-(*-YFastStart),$ea
'''
    replacement = 'YFastStart:\n' + replacement
    data = source_match(image, output, 'offscreen-fast-entry', helper, replacement,
                        ('R4', 'SprObject_Y_HighPos'))
    patch1 = extent(raw, 126, start, bytes((0x4c, helper & 255, helper >> 8, 0xea)),
                    'GetYOffscreenBits entry; original loop and tables retain their PCs')
    patch2 = extent(raw, 126, helper, data, 'Unused inlined DividePDiff source footprint')
    assert bytes.fromhex(patch2['preimage']) == old_helper and len(data) == len(old_helper)
    x = location(image, 'GetOffScreenBitsSet')
    assert bytes((0x20, start & 255, start >> 8)) in raw[x:x+32]
    cfg = (ROOT / 'smb1base-mmc5-expanded.cfg').read_text()
    assert re.findall(r'^[ \t]*PRGLow:.*$', cfg, re.M) == [
        '    PRGLow: start = $8000,  size = $2000, type = ro, file = %O, fill = yes, fillval = $ff, bank = $7e;'
    ]
    return patch1, patch2


def apply(raw, patches):
    result = bytearray(raw)
    for patch in patches:
        offset = patch['offset']
        old = bytes.fromhex(patch['preimage'])
        new = bytes.fromhex(patch['replacement'])
        assert len(old) == len(new) and result[offset:offset+len(old)] == old
        result[offset:offset+len(old)] = new
    return bytes(result)


def cpu_call(memory, start, a, x, y, p, cls=MPU):
    cpu = cls(memory=memory, pc=start)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 224
    cpu.stPushWord(0x5aff)
    for _ in range(12000):
        if cpu.pc == 0x5b00:
            assert cpu.sp == 224
            return (cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp), cpu.processorCycles
        assert memory[cpu.pc] != 0, ('Actual linked BRK', hex(cpu.pc))
        cpu.step()
    raise AssertionError(('Bounded source call', hex(cpu.pc)))


def compare_y(images):
    start = address(images[0], 'GetYOffscreenBits')
    high = address(images[0], 'SprObject_Y_HighPos')
    low = address(images[0], 'SprObject_Y_Position')
    memories = []
    for image in images:
        m = [0] * 65536
        m[0x8000:0xa000] = image['raw'][16+126*8192:16+127*8192]
        memories.append(m)
    cycles = {name: Counter() for name in ('normal_page', 'other_pages')}
    for hi, lo in itertools.product(range(256), repeat=2):
        x = (hi + lo) % 9
        flags = (0x20, 0x61, 0xa4, 0xe5)[(hi ^ lo) & 3]
        output = []
        timing = []
        for m in memories:
            m[3:11] = [113, 227, 145, 251, 59, 71, 83, 97]
            m[high+x], m[low+x] = hi, lo
            registers, cost = cpu_call(m, start, 53, x, 19, flags)
            output.append((registers, tuple(m[3:11])))
            timing.append(cost)
        assert output[0] == output[1], (hi, lo, output)
        cycles['normal_page' if hi == 1 else 'other_pages'][timing[0]-timing[1]] += 1
    return dict(exhaustive_vertical_words=65536, full_AXYPSP_and_R0_R7_equal=True,
                cycles_saved_histograms=cycles)


def fire_fixture(seed, image, rng, case):
    m = N.fork(seed)
    m.bundle = image
    for window, tag in enumerate(m.rawtags):
        if tag & 128:
            m.page(window, tag & 127)
    slot = case & 1
    N.put(m, SelectedCharacter=(41, 0, 1, 7, 32, 36, 39)[case % 7], ObjectOffset=slot,
          FrameCounter=0x20+(case % 11 == 0), BowserHitPoints=1+case % 2,
          WorldNumber=case % 8, DuplicateObj_Offset=5, AreaType=1)
    m[address(image, 'Fireball_State')+slot] = [1, 1, 1, 1, 1, 0, 128][case % 7]
    base = address(image, 'BoundingBox_UL_Corner')
    m[base+28+slot*4:base+32+slot*4] = [100, 168, 104, 172]
    for enemy in range(6):
        active = case % 4 != 0 and rng.randrange(4) != 0
        state = rng.choice([0, 0, 0, 1, 2, 32, 64, 128])
        identity = rng.choice([0, 1, 2, 6, 6, 8, 12, 13, 17, 20, 21, 35, 36, 42, 43, 45, 46, 47])
        for name, value in [('Enemy_Flag', int(active)), ('Enemy_State', state),
                            ('Enemy_ID', identity), ('EnemyOffscrBitsMasked', rng.choice([0, 0, 0, 4, 64])),
                            ('Enemy_X_Position', 100), ('Enemy_Y_Position', 168), ('Enemy_Y_HighPos', 1)]:
            m[address(image, name)+enemy] = value
        offset = base+4+enemy*4
        m[offset:offset+4] = rng.choice([[99, 167, 105, 174], [95, 173, 99, 177],
                                        [105, 167, 110, 175], [255, 167, 101, 175]])
    return m, slot


def compare_state(a, b):
    # Stack frames have returned. Their dead stack payload may differ.
    assert a[:0x100] == b[:0x100]
    assert a[0x200:0x8000] == b[0x200:0x8000]
    assert a.ram == b.ram and a.rawtags == b.rawtags
    for field in ('oam', 'ppuctrl', 'ppumask', 'chr_regs', 'ppu_vram'):
        assert getattr(a, field, None) == getattr(b, field, None), field


def compare_fire(images):
    b0, b1 = images
    seed = N.fresh(b0)
    counts = Counter()
    hit = 0
    for case in range(672):
        outcomes, memory = [], []
        for image in images:
            m, slot = fire_fixture(seed, image, random.Random(0x1643+case), case)
            outputs = N.invoke(m, 'FireballEnemyCollision', a=97, x=slot, y=191,
                               p=(0x20, 0x61, 0xa4, 0xe5)[case & 3])
            outcomes.append(outputs)
            memory.append(m)
        assert all(outcomes[0][key] == outcomes[1][key] for key in ('A', 'X', 'Y', 'P')), (case, outcomes)
        try:
            compare_state(*memory)
        except AssertionError as error:
            raise AssertionError(('fire loop state', case, outcomes)) from error
        counts[outcomes[0]['CPU']-outcomes[1]['CPU']] += 1
        hit += N.get(memory[1], 'Square1SoundQueue') == address(b1, 'Sfx_EnemySmack')
    assert hit > 0
    return dict(actual_native_shared_collision_cases=672, genuine_native_smack_results=hit,
                full_AXYP_native_RAM_overlay_maps_equal=True, cycles_saved_histogram=counts)


def game_seed(image, enemies):
    m = N.fresh(image)
    N.put(m, SelectedCharacter=41, OperMode=1, FamilyMainCommit=1, DisableScreenFlag=1,
          Mirror_PPUMASK=0, NmiDisable=255, Mirror_PPUCTRL=160)
    N.invoke(m, 'MiniScene')
    N.put(m, DisableScreenFlag=0, Mirror_PPUMASK=30, OperMode_Task=3, GameEngineSubroutine=8,
          PlayerStatus=0, PlayerSize=1, Player_X_Position=80, Player_PageLoc=0,
          Player_Y_Position=176, Player_Y_HighPos=1, PlayerFacingDir=1, FrameCounter=1,
          ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=0, ScreenRight_X_Pos=255,
          ScreenRight_PageLoc=0, TimerControl=0, GameTimerDisplay=4, AreaType=1)
    for name in ('Block_Buffer_1', 'Block_Buffer_2'):
        at = address(image, name)
        m[at:at+208] = [0]*176+[0x54]*32
    N.invoke(m, 'GameCoreRoutine', x=0, y=0)
    N.put(m, PlayerStatus=2, PlayerFacingDir=1)
    for enemy in range(enemies):
        for name, value in [('Enemy_Flag', 1), ('Enemy_ID', 6), ('Enemy_State', 0),
                            ('Enemy_X_Position', 112+enemy*24), ('Enemy_PageLoc', 0),
                            ('Enemy_Y_Position', 184), ('Enemy_Y_HighPos', 1),
                            ('Enemy_X_Speed', 248), ('Enemy_Y_Speed', 0),
                            ('Enemy_MovingDir', 2), ('Enemy_BoundBoxCtrl', 9)]:
            m[address(image, name)+enemy] = value
    return m


def game_cores(images):
    rows = []
    for enemies in (0, 1, 3, 5):
        machines = [game_seed(image, enemies) for image in images]
        costs = []
        peak_shots = 0
        for frame in range(32, 58):
            buttons = 64 if frame in (35, 37) else 0
            out = []
            for m in machines:
                N.put(m, FrameCounter=frame, SavedJoypadBits=buttons, SavedJoypad1Bits=buttons,
                      A_B_Buttons=buttons, PreviousA_B_Buttons=64 if frame in (36, 38) else 0,
                      Left_Right_Buttons=0, Up_Down_Buttons=0)
                out.append(N.invoke(m, 'GameCoreRoutine', x=0, y=0))
            assert all(out[0][key] == out[1][key] for key in ('A', 'X', 'Y', 'P'))
            try:
                compare_state(*machines)
            except AssertionError as error:
                raise AssertionError(('whole GameCore state', enemies, frame, out)) from error
            active = sum(N.get(machines[1], 'Fireball_State', i) == 1 for i in (0, 1))
            peak_shots = max(peak_shots, active)
            costs.append((out[0]['CPU'], out[1]['CPU'], active))
        saving = [old-new for old, new, _ in costs]
        rows.append(dict(enemy_slots=enemies, updates=len(costs), peak_live_shots=peak_shots,
                         baseline_range=[min(x[0] for x in costs), max(x[0] for x in costs)],
                         successor_range=[min(x[1] for x in costs), max(x[1] for x in costs)],
                         saved_range=[min(saving), max(saving)], saved_total=sum(saving),
                         rows=costs))
    assert max(row['peak_live_shots'] for row in rows if row['enemy_slots']) == 2
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(exist_ok=True)
    raw = PARENT.read_bytes()
    assert sha(raw) == PIN
    original = bundle(raw)
    patches = [fire_patches(original, args.output), *y_patches(original, args.output)]
    after = apply(raw, patches)
    images = original, bundle(after)
    fire = compare_fire(images)
    print('Shared fire enemy loop', json.dumps(fire), flush=True)
    vertical = compare_y(images)
    print('Vertical offscreen', json.dumps(vertical), flush=True)
    game = game_cores(images)
    receipt = dict(passed=True, parent_SHA256=PIN, expected_memory_only_SHA256=sha(after),
                   patches=patches, fire=fire, vertical=vertical, actual_GameCore=game,
                   scope='CPU only. Existing native source footprints and exact linked preimages. '
                         'Whole-GameCore comparison excludes the returned dead stack contents. '
                         'No ROM output or Mesen measurement.',
                   source_bindings={p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in
                                    (Path(__file__), OBJECT, COMMON, ROOT/'smb1base-mmc5-expanded.cfg')})
    (args.output/'result.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({**{k: receipt[k] for k in ('passed', 'parent_SHA256', 'expected_memory_only_SHA256')},
                      'actual_GameCore': [{k: v for k, v in row.items() if k != 'rows'} for row in game]}))


if __name__ == '__main__':
    main()

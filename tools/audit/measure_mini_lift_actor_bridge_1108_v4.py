"""Measure the source-native large platform's unnecessary foreign save frames."""
from collections import defaultdict
from itertools import product
from pathlib import Path
import json
import re
import subprocess

import check_mini_funded_actor_1108_v3 as F

A, N, R, OUT = F.A, F.N, F.R, F.OUT
BASE = R / 'build/mini-busy-pipeline-final-1108/candidate.nes'
PIN = '37bb9c1a69b993edda540c75cbe256aeac75396d55d34d9daf3d4de86deebeeb'
SOURCE = R / 'src/ryu_source_body.s'
MACROS = R / 'src/ryu_platform.s'
LEAVES = ('Z2LegacyPlatformPrepare', 'Z2LegacyPlatformFinish')
GATES = ('RyuSourceBodyPlatformPrepare', 'RyuSourceBodyPlatformFinish')
NAMES = ('R0', 'R7', 'RgTempX', 'RgTempPage', 'RgTempY', 'RgTemp2', 'RgTemp3',
         'RyuSourceBodyPlatformOverlap', 'RyuSourceBodyPlatformBasic', 'Player_X_Position',
         'ScreenLeft_X_Pos', 'BoundingBox_UL_Corner', 'BoundingBox_LR_Corner',
         'RyuSourceBodyProfile', 'RelativePlayerPosition', 'BoundingBoxCore', 'RyuSourceBodyBox',
         'SelectedCharacter', 'CHARACTER_RYU')


def assembly(stem, pc, defs, body):
    src = OUT / f'{stem}.s'
    cfg = OUT / f'{stem}.cfg'
    obj = OUT / f'{stem}.o'
    bin_path = OUT / f'{stem}.bin'
    src.write_text('.setcpu "6502"\n.segment "LIFT"\n' + defs + body)
    cfg.write_text(f'MEMORY{{P:start=${pc:04x},size=$100,file=%O;}}SEGMENTS{{LIFT:load=P,type=ro;}}\n')
    cc = R / 'tools/Windows/cc65/bin'
    subprocess.run([cc / 'ca65.exe', src, '-o', obj], check=True)
    subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', bin_path], check=True)
    obj.unlink()
    return bin_path.read_bytes()


def make_patches(b):
    defs = ''.join(f'{n}=${A.address(b, n):04x}\n' for n in NAMES)
    defs += '''
.macro phx
  txa
  pha
.endmacro
.macro phy
  tya
  pha
.endmacro
.macro plx
  pla
  tax
.endmacro
.macro ply
  pla
  tay
.endmacro
'''
    macro_source = MACROS.read_text()
    macros = macro_source[macro_source.index('.macro RP_Save'):macro_source.index('.segment "ROSTER"')]
    assert macros.count('.endmacro') == 2
    save = macros.split('.macro RP_Save\n', 1)[1].split('.endmacro', 1)[0]
    restore = macros.split('.macro RP_Restore\n', 1)[1].split('.endmacro', 1)[0]
    # The five RgTemps are untouched by the finite typed callees in these
    # two leaves. Keep the unrolled R0..7 save order and each original core.
    save = save[:save.index('  lda RgTempX')]
    restore = restore[restore.index('  .repeat 8'):]
    suffix = 'NotRyu:\n  pla\n  plp\n  rts\n'
    guard = '''  php
  pha
  lda SelectedCharacter
  cmp #CHARACTER_RYU
  bne NotRyu
  pla
  plp
'''
    patches = []
    for leaf in LEAVES:
        text = SOURCE.read_text().split(f'.proc {leaf}\n', 1)[1].split('.endproc', 1)[0].split('.endif\n', 1)[1]
        pc = A.address(b, leaf)
        at = A.location(b, leaf)
        assert (at - 16) // 8192 == 58 and text.count('  RP_Save\n') == text.count('  RP_Restore\n') == 1
        old = assembly(leaf + '-original', pc, defs + macros, text)
        assert b['raw'][at:at+len(old)] == old, (leaf, hex(pc), len(old))
        new_text = text.replace('  RP_Save\n', guard + save).replace('  RP_Restore\n', restore) + suffix
        new = assembly(leaf + '-fast', pc, defs, new_text)
        assert len(new) <= len(old), (leaf, len(new), len(old))
        patches.append(dict(role=leaf, physical_PRG=58, CPU_half_open=[pc, pc + len(old)],
                            file_offset=at, old_hex=old.hex(), new_hex=new.ljust(len(old), b'\xea').hex(),
                            original_bytes=len(old), live_successor_bytes=len(new)))
    return patches


def inject_witness(m, owner, variant, scene, slot):
    N.put(m, SelectedCharacter=owner, Z2Variant=variant, OperMode=1, GameEngineSubroutine=8,
          Player_X_Position=105 if scene != 'far' else 55, Player_PageLoc=0,
          Player_Y_Position=160, Player_Y_HighPos=1, Player_State=2, Player_Y_Speed=12,
          Player_OffscreenBits=0, GuestHurtTicks=0, RgCrouch=0, RgAttack=0,
          RyuSourceBodyProfile=25, TimerControl=0)
    F.set_actor(m, slot=slot, enemy=0x28 if scene != 'vertical' else 0x25,
                x=111, y=184 if scene != 'high' else 64, state=0 if scene != 'tagged' else 0x40)
    for name, value in [('Enemy_BoundBoxCtrl', 5), ('Enemy_Flag', 1)]:
        F.V.setslot(m, name, slot, value)
    base = A.address(m.bundle, 'BoundingBox_UL_Corner')
    m[base:base+4] = [107, 167, 119, 192]
    m[base+4*(slot+1):base+4*(slot+2)] = [111, 184, 143, 192]
    for name, value in zip(NAMES[2:7], (17, 53, 87, 101, 169)):
        m[A.address(m.bundle, name)] = value


def abi(images):
    saved = defaultdict(list)
    seeds = [A.fixture(b, 0, False, False) for b in images]
    for owner, variant, scene, slot, p in product(range(42), [0, 1], ['near', 'far', 'vertical', 'high', 'tagged'], [0, 5], [0x20, 0x71]):
        for symbol in GATES:
            result = []
            for seed in seeds:
                m = F.slim_fork(seed)
                inject_witness(m, owner, variant, scene, slot)
                z = N.invoke(m, symbol, a=0x87, x=slot, y=0x17, p=p)
                result.append((z, A.state(m)))
            (a, sa), (b, sb) = result
            assert sa == sb and all(a[k] == b[k] for k in ('A', 'X', 'Y', 'P')), (owner, variant, scene, slot, p, symbol, a, b)
            key = 'Ryu_source' if owner == 10 else 'Zelda_II_outer_gate' if owner == 4 and variant else 'native_foreign'
            saved[key].append(a['CPU'] - b['CPU'])
    return {k:dict(cases=len(v), cycles=sorted(set(v))) for k, v in saved.items()}


def main_cases(images):
    saved = []
    for enemy_count, with_lift, scroll in product([0, 3], [False, True], [False, True]):
        pair = [A.fixture(b, enemy_count, False, scroll) for b in images]
        for m in pair:
            if with_lift:
                m.bundle['segs']['current_mini_lift_spawn'] = dict(start=str(0xbcc7), ooffs=str(16 + 78*8192 + 0x1cc7))
                m.bundle['syms']['MiniLiftSpawn'] = dict(val=str(0xbcc7), seg='current_mini_lift_spawn')
                N.invoke(m, 'MiniLiftSpawn', a=125, y=0, x=5)
                assert N.get(m, 'Enemy_Flag', 5) == 1 and N.get(m, 'Enemy_ID', 5) == 0x25
        frames = []
        for frame in range(2, 18):
            ret = []
            for m in pair:
                key = 0x81 if 8 <= frame < 15 else 0
                N.put(m, FrameCounter=frame, SavedJoypadBits=key, SavedJoypad1Bits=key,
                      VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
                ret.append(N.invoke(m, 'GameCoreRoutine', x=0, y=0))
            assert A.state(pair[0]) == A.state(pair[1]) and all(ret[0][k] == ret[1][k] for k in ('A', 'X', 'Y', 'P'))
            frames.append([ret[0]['CPU'], ret[1]['CPU']])
        saved.append(dict(ordinary_enemies=enemy_count, source_spawned_lift=with_lift, parser_work=scroll, pairs=frames))
    return saved


def main():
    raw = BASE.read_bytes()
    assert A.sha(raw) == PIN
    original = A.bundle(raw)
    patches = make_patches(original)
    new = F.install(raw, patches)
    e90d = A.BASE.read_bytes()
    assert A.sha(e90d) == A.PIN
    old_parent_proposal = F.install(e90d, patches)
    images = [original, A.bundle(new)]
    bodies = abi(images)
    print('Platform public callbacks', bodies, flush=True)
    main = main_cases(images)
    print('GameCore minimum and maximum savings', [(row['source_spawned_lift'], min(a-b for a,b in row['pairs']), max(a-b for a,b in row['pairs'])) for row in main], flush=True)
    receipt = dict(passed=True, CPU_only=True, ROM_written=False, base_SHA256=PIN,
                   expected_memory_only_SHA256=A.sha(new), equivalent_preimages_e90d_SHA256=A.sha(old_parent_proposal),
                   patches=patches, callback_abi=bodies, GameCore=main,
                   source_domain='Bank58 wrappers keep the outer Zelda II gate unchanged. Foreign owners never enter either Ryu collision core. For Ryu, only original R0..7 may be written by the explicit platform overlap/box callees, and the same unrolled R0..7 save/restore executes. Five unrelated RgTemps are never read or written by those callees; all five remain untouched and compare exact.',
                   scope='Each original full linked leaf byte-reproduced before fitting successor in the same extent. No writer, mapper, header, terrain or engine changes. Exact native callback, whole GameCore, all ordinary platforms and Mini-source lift actor lifecycle within the stated fixture. Actual IRQ/lag and cold source funding follow-up pending.',
                   bindings={str(p):A.sha(p.read_bytes()) for p in [Path(__file__), BASE, A.BASE, SOURCE, MACROS,
                            R/'src/zelda2_link_platform.s', R/'src/sprite_render.s', R/'src/collision.s']})
    (OUT/'lift-bridge-v4.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Lift proposal', A.sha(new), flush=True)


if __name__ == '__main__':
    main()

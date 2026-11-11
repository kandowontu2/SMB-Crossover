"""Qualify Jay's two offscreen native platform constructors in real host RAM."""

from collections import Counter
from hashlib import sha256
import json

import check_jay_silius_shotgun_transport_1111 as T


C, H, N, W = T.C, T.H, T.N, T.W
SOURCE = H.ROOT / 'tools/reference/jay_silius_helpers_1111.s'
ORIGIN = 0xbd00
FIELDS = dict(HelperSeen=0xc03d, HelperIndex=0xc03e, HelperDelta=0xc03f, DropStage=0xc0d7)
NATIVE = {
    'ObjectOffset': 'ObjectOffset', 'AreaType': 'AreaType', 'WorldNumber': 'WorldNumber',
    'LevelNumber': 'LevelNumber', 'TimerControl': 'TimerControl',
    'ScreenLeftX': 'ScreenLeft_X_Pos', 'ScreenLeftPage': 'ScreenLeft_PageLoc',
    'EnemyFlag': 'Enemy_Flag', 'EnemyID': 'Enemy_ID', 'EnemyX': 'Enemy_X_Position',
    'EnemyPage': 'Enemy_PageLoc', 'EnemyY': 'Enemy_Y_Position', 'EnemyYHigh': 'Enemy_Y_HighPos',
    'EnemyBox': 'Enemy_BoundBoxCtrl', 'PlatformCenterY': 'Enemy_X_Speed',
}


def assemble(trial, *, origin=ORIGIN):
    fields = dict(FIELDS, **{name: W.address(trial, symbol) for name, symbol in NATIVE.items()})
    assert set(FIELDS.values()).isdisjoint(C.Jay.build()['ram'].values())
    constants = ''.join(f'{name}=${value:04x}\n' for name, value in fields.items())
    return H.assemble(constants + SOURCE.read_text(), {'HELPERS': (origin, 384)}), fields


def call(m, observe=None):
    m.raw_page(1, 3)
    N.put(m, CurrentBank=3)
    cpu = N.NesMPU(memory=m, pc=ORIGIN)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 83, 71, 109, 0x31, 224
    cpu.stPushWord(0x5aff)
    C.Vector.finish(m, cpu, (0x5b00, 224), observe)
    assert (cpu.a, cpu.x, cpu.y, cpu.p & 0xef) == (83, 71, 109, 0x21)


def main():
    raw = H.ROM.read_bytes()
    assert sha256(raw).hexdigest() == T.PIN
    trial = dict(W.Symbols.bundle(), raw=raw)
    program, fields = assemble(trial)
    native = W.address(trial, 'InitEnemyObject')
    assert native == 0xa74f and (W.location(trial, 'InitEnemyObject')-16)//8192 == 2
    results = Counter()
    for index, left in enumerate((688, 880)):
        for relative in (255, 256, 270, 287, 288):
            m = C.Common.blank(trial)
            C.Common.scene(m, 16)
            m[0x730b] = 32
            m.raw_page(2, 2)
            data = program['images']['HELPERS']
            m.ram[3][ORIGIN-0xa000:ORIGIN-0xa000+len(data)] = data
            for slot in range(6):
                m[fields['EnemyFlag']+slot] = 0
            camera = left - relative
            N.put(m, AreaType=1, WorldNumber=0, LevelNumber=0, TimerControl=0,
                  ScreenLeft_PageLoc=camera>>8, ScreenLeft_X_Pos=camera&255, ObjectOffset=2)
            m.ram[2][0x33] = 1
            m.ram[2][0x3d] = 2 if index == 0 else 1
            scratch = bytes(m[3:11])
            entered = []

            def observe(memory, cpu):
                if memory.rawtags[1] == 130 and cpu.pc == native:
                    entered.append(cpu.x)

            call(m, observe)
            admitted = 256 <= relative <= 287
            assert len(entered) == int(admitted), (index, relative, entered)
            assert bytes(m[3:11]) == scratch and N.get(m, 'ObjectOffset') == 2
            if admitted:
                slot, = entered
                get = lambda name: m[fields[name]+slot]
                assert (get('EnemyFlag'), get('EnemyID'), get('EnemyYHigh'), get('EnemyY'), get('EnemyBox')) == (1, 37, 1, 192, 5)
                assert get('EnemyPage')*256+get('EnemyX') == left
                assert get('PlatformCenterY') == (169, 161)[index]
                before = bytes(m[fields['EnemyFlag']:fields['EnemyFlag']+6])
                call(m)
                assert bytes(m[fields['EnemyFlag']:fields['EnemyFlag']+6]) == before
                assert m.ram[2][0x3d] == 3
                results['native_constructor_and_no_repeat'] += 1
            else:
                results['offscreen_window_decline'] += 1
    print(json.dumps(dict(passed=True, assembly=program['used'], cases=dict(results),
                          helpers=[dict(left=x, center=x+16, initial_top=192) for x in (688, 880)],
                          assisted_crossing_verified=False, output_files=0), sort_keys=True), flush=True)


if __name__ == '__main__':
    main()

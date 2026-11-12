"""Execute native actor admission, full rectangle and overlap together."""
import json
from py65.devices.mpu6502 import MPU
import check_steve_throw_enemy_rect_1112 as Rect

Live, H = Rect.Live, Rect.H
SOURCE = H.ROOT / 'tools/reference/steve_throw_target_1112.s'


def main():
    bundle = Live.W.Symbols.bundle()
    native = {name: Live.W.address(bundle, name) for name in
              ('Enemy_Flag', 'Enemy_ID', 'Enemy_State', 'Enemy_Y_HighPos',
               'Enemy_BoundBoxCtrl', 'Enemy_X_Position', 'Enemy_PageLoc',
               'Enemy_Y_Position', 'BoundBoxCtrlData', 'JnEnemyHurt')}
    raw = Live.DONOR.HOST.read_bytes()
    at = Live.W.location(bundle, 'BoundBoxCtrlData')
    table = raw[at:at+48]
    source = Live.bindings(native | Rect.Overlap.FIELDS)+Rect.SOURCE.read_text()+Rect.Overlap.SOURCE.read_text()+SOURCE.read_text()
    layout = {'ENEMY_RECT': (0xad00, 128), 'OVERLAP': (0xac00, 128), 'THROW_TARGET': (0xae00, 128)}
    linked = H.assemble(source, layout)
    count = 0

    def run(overrides, *, cooldown=0, x=255, point=260, multi=False):
        nonlocal count
        cpu = MPU()
        m = cpu.memory
        for key, (origin, _) in layout.items():
            code = linked['images'][key]
            m[origin:origin+len(code)] = code
        m[native['BoundBoxCtrlData']:native['BoundBoxCtrlData']+48] = table
        for slot in ((2, 5) if multi else (2,)):
            values = dict(Enemy_Flag=1, Enemy_ID=6, Enemy_State=0, Enemy_Y_HighPos=1,
                          Enemy_BoundBoxCtrl=3, Enemy_X_Position=x&255, Enemy_PageLoc=x>>8,
                          Enemy_Y_Position=176, JnEnemyHurt=cooldown) | overrides
            for name, value in values.items():
                m[native[name]+slot] = value
        for index, value in enumerate((point+0x8000, 0x8000+256+188)):
            p = Rect.Overlap.FIELDS['ThrowPoint']+index*2
            m[p:p+2] = value.to_bytes(2, 'little')
        cpu.pc, cpu.sp = linked['symbols']['SteveThrowFindTarget'], 0xf0
        cpu.stPushWord(0x4fff)
        for _ in range(1200):
            if cpu.pc == 0x5000:
                break
            cpu.step()
        else:
            raise AssertionError('target search did not return')
        assert cpu.sp == 0xf0
        assert m[native['JnEnemyHurt']+2] == cooldown
        count += 1
        return bool(cpu.p & 1), cpu.x

    for cooldown in (0, 1, 12, 255):
        for x in (0, 248, 255, 256, 511, 4000):
            assert run({}, cooldown=cooldown, x=x, point=x+5) == (True, 2)
            assert run({}, cooldown=cooldown, x=x, point=x-7)[0] is False
            assert run({}, cooldown=cooldown, x=x, point=x+22)[0] is False
    for overrides in ({'Enemy_Flag': 0}, {'Enemy_Flag': 128}, {'Enemy_ID': 12},
                      {'Enemy_ID': 21}, {'Enemy_State': 32}, {'Enemy_Y_HighPos': 2},
                      {'Enemy_BoundBoxCtrl': 2}, {'Enemy_BoundBoxCtrl': 12}):
        assert not run(overrides)[0], overrides
    assert run({}, multi=True) == (True, 5)
    print(json.dumps(dict(cases=count, bytes={key: len(code) for key, code in linked['images'].items()},
                          output_files=0, mounted=False)))


if __name__ == '__main__':
    main()

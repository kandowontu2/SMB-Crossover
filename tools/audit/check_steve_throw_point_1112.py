"""Execute robot Q4 conversion at page, fractional and 4096-pixel wraps."""
import json
from itertools import product
from py65.devices.mpu6502 import MPU
import check_steve_throw_controls_live_1111 as Controls

H, Live = Controls.H, Controls.Live


def main():
    _, info = Controls.proposal(Live.DONOR.HOST.read_bytes(), graphics=True)
    fields = info['throw_control_fields'] | dict(ThrowPoint=0, ThrowLow=4, ThrowHigh=8,
                                                ThrowDelta=12, ThrowExtent=14)
    bundle = Live.W.Symbols.bundle()
    for name in ('Enemy_BoundBoxCtrl', 'Enemy_X_Position', 'Enemy_PageLoc',
                 'Enemy_Y_Position', 'Enemy_Y_HighPos', 'BoundBoxCtrlData'):
        fields[name] = Live.W.address(bundle, name)
    source = H.ROOT / 'tools/reference/steve_throw_point_1112.s'
    sources = source.read_text()
    for name in ('steve_throw_enemy_rect_1112.s', 'steve_throw_overlap_1112.s', 'steve_throw_target_1112.s'):
        sources += '\n'+(source.parent/name).read_text()
    layout = {'THROW_POINT': (0xab00, 256), 'ENEMY_RECT': (0xac00, 256),
              'OVERLAP': (0xad00, 256), 'THROW_TARGET': (0xae00, 256)}
    linked = H.assemble(Live.bindings(fields)+sources, layout)
    code = linked['images']['THROW_POINT']
    cpu = MPU()
    for name, (origin, _) in layout.items():
        image = linked['images'][name]
        cpu.memory[origin:origin+len(image)] = image
    raw = Live.DONOR.HOST.read_bytes()
    at = Live.W.location(bundle, 'BoundBoxCtrlData')
    cpu.memory[fields['BoundBoxCtrlData']:fields['BoundBoxCtrlData']+48] = raw[at:at+48]
    count = contacts = 0
    for camera, delta, fraction, y in product(
            (0, 255, 256, 2047, 3840, 4095, 4096, 8191, 32768),
            (-128, -1, 0, 1, 255, 256, 384), (0, 1, 7, 15),
            (-257, -16, -1, 0, 1, 255, 2816, 3839, 4095)):
        m = cpu.memory
        xq4 = ((camera+delta)*16+fraction) & 65535
        for name, value, size in (('ScreenLeft_X_Pos', camera & 255, 1),
                                  ('ScreenLeft_PageLoc', camera >> 8, 1),
                                  ('SteveBotX', xq4, 2), ('SteveBotY', y & 65535, 2)):
            at = fields[name]
            m[at:at+size] = value.to_bytes(size, 'little')
        cpu.pc, cpu.sp = 0xab00, 0xf0
        cpu.stPushWord(0x4fff)
        for _ in range(200):
            if cpu.pc == 0x5000:
                break
            cpu.step()
        assert cpu.pc == 0x5000 and cpu.sp == 0xf0
        actual = (m[0]+256*m[1], m[2]+256*m[3])
        expected = ((camera+delta+0x8000) & 65535, (y//16+256+0x8000) & 65535)
        assert actual == expected, (camera, delta, fraction, y, actual, expected)
        assert m[fields['SteveBotX']:fields['SteveBotX']+2] == list(xq4.to_bytes(2, 'little'))
        count += 1
        if y == 2816 and 8 <= camera+delta < 65500:
            for offset, hit in ((-8, True), (40, False)):
                enemy_x = camera+delta+offset
                values = dict(Enemy_Flag=1, Enemy_ID=6, Enemy_State=0,
                              Enemy_BoundBoxCtrl=3, Enemy_Y_Position=164,
                              Enemy_Y_HighPos=1, Enemy_X_Position=enemy_x & 255,
                              Enemy_PageLoc=enemy_x >> 8)
                for name, value in values.items():
                    m[fields[name]+2] = value
                cpu.pc = linked['symbols']['SteveThrowFindTarget']
                cpu.stPushWord(0x4fff)
                for _ in range(1200):
                    if cpu.pc == 0x5000:
                        break
                    cpu.step()
                assert cpu.pc == 0x5000 and cpu.sp == 0xf0
                assert bool(cpu.p & 1) == hit, (camera, delta, fraction, offset)
                if hit:
                    assert cpu.x == 2
                contacts += 1
    print(json.dumps(dict(cases=count, composed_contacts=contacts, bytes=len(code), mounted=False, output_files=0)))


if __name__ == '__main__':
    main()

"""Compare native control-table rectangle construction across page carries."""
import json
from itertools import product
from py65.devices.mpu6502 import MPU
import check_steve_throw_overlap_1112 as Overlap

H, Live = Overlap.H, Overlap.Controls.Live
SOURCE = H.ROOT / 'tools/reference/steve_throw_enemy_rect_1112.s'


def main():
    bundle = Live.W.Symbols.bundle()
    native = {name: Live.W.address(bundle, name) for name in
              ('Enemy_BoundBoxCtrl', 'Enemy_X_Position', 'Enemy_PageLoc',
               'Enemy_Y_Position', 'Enemy_Y_HighPos', 'BoundBoxCtrlData')}
    raw = Live.DONOR.HOST.read_bytes()
    offset = Live.W.location(bundle, 'BoundBoxCtrlData')
    # Enemy controls 3..11 are the native SMB rectangles; player-only
    # crossover entries can contain signed offsets and are not admitted here.
    table = raw[offset:offset+48]
    assert table[12:16] == bytes((2, 9, 14, 21))
    linked = H.assemble(Live.bindings(native | Overlap.FIELDS)+SOURCE.read_text()+Overlap.SOURCE.read_text(),
                        {'ENEMY_RECT': (0xad00, 256), 'OVERLAP': (0xac00, 256)})
    cpu = MPU()
    code = linked['images']['ENEMY_RECT']
    cpu.memory[0xad00:0xad00+len(code)] = code
    overlap = linked['images']['OVERLAP']
    cpu.memory[0xac00:0xac00+len(overlap)] = overlap
    cpu.memory[native['BoundBoxCtrlData']:native['BoundBoxCtrlData']+48] = table
    count, hits = 0, 0
    for slot, control, x, y in product(range(6), range(3, 12),
                                      (0, 248, 255, 256, 511, 1023, 4000),
                                      (0x100, 0x1ef, 0x1ff, 0x200)):
        for name, value in (('Enemy_BoundBoxCtrl', control), ('Enemy_X_Position', x & 255),
                            ('Enemy_PageLoc', x >> 8), ('Enemy_Y_Position', y & 255),
                            ('Enemy_Y_HighPos', y >> 8)):
            cpu.memory[native[name]+slot] = value
        cpu.pc, cpu.x, cpu.sp = 0xad00, slot, 0xf0
        cpu.stPushWord(0x4fff)
        for _ in range(100):
            if cpu.pc == 0x5000:
                break
            cpu.step()
        else:
            raise AssertionError('rectangle did not return')
        left, top, right, bottom = table[control*4:control*4+4]
        expected = (x+left+0x8000, y+top+0x8000, x+right+0x8000, y+bottom+0x8000)
        actual = tuple(cpu.memory[a]+256*cpu.memory[a+1] for a in
                       (0x6004, 0x6006, 0x6008, 0x600a))
        assert actual == expected and cpu.x == slot and cpu.sp == 0xf0, (slot, control, x, y, actual)
        count += 1
        for px, py in product((x+left-9, x+left-8, x+right+7, x+right+8),
                              (y+top-9, y+top-8, y+bottom+8, y+bottom+9)):
            for i, value in enumerate((px+0x8000, py+0x8000)):
                at = Overlap.FIELDS['ThrowPoint']+i*2
                cpu.memory[at:at+2] = value.to_bytes(2, 'little')
            cpu.pc, cpu.x, cpu.sp = linked['symbols']['SteveThrowEnemyOverlap'], slot, 0xf0
            cpu.stPushWord(0x4fff)
            for _ in range(220):
                if cpu.pc == 0x5000:
                    break
                cpu.step()
            else:
                raise AssertionError('combined overlap did not return')
            expected_hit = x+left-8 <= px < x+right+8 and y+top-8 <= py <= y+bottom+8
            assert bool(cpu.p & 1) == expected_hit and cpu.x == slot and cpu.sp == 0xf0, (
                slot, control, x, y, px, py)
            hits += 1
    print(json.dumps(dict(cases=count, combined_overlap_cases=hits, bytes=len(code), output_files=0,
                          scope='Native table geometry; no actor admission or damage yet.')))


if __name__ == '__main__':
    main()

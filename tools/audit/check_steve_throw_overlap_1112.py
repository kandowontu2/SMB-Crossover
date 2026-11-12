"""Check the throw's expanded rectangle, including screen-edge carries."""

import json
from itertools import product
from py65.devices.mpu6502 import MPU
import check_steve_throw_controls_live_1111 as Controls

H = Controls.H
SOURCE = H.ROOT / 'tools/reference/steve_throw_overlap_1112.s'
FIELDS = dict(ThrowPoint=0x6000, ThrowLow=0x6004, ThrowHigh=0x6008,
              ThrowDelta=0x600c, ThrowExtent=0x600e)


def main():
    source = Controls.Live.bindings(FIELDS) + SOURCE.read_text()
    linked = H.assemble(source, {'OVERLAP': (0xac00, 256)})
    cpu = MPU()
    code = linked['images']['OVERLAP']
    cpu.memory[0xac00:0xac00+len(code)] = code
    count = 0

    def put(name, x, y):
        for index, value in enumerate((x, y)):
            value += 0x8000
            at = FIELDS[name]+index*2
            cpu.memory[at:at+2] = value.to_bytes(2, 'little')

    for left, top, width, height in product((-32, -8, 0, 248, 255, 256),
                                           (-16, 0, 224, 255), (8, 16, 32), (8, 16, 32)):
        right, bottom = left+width, top+height
        put('ThrowLow', left, top)
        put('ThrowHigh', right, bottom)
        for x, y in product((left-9, left-8, left, right+7, right+8, right+9),
                            (top-9, top-8, top, bottom+7, bottom+8, bottom+9)):
            put('ThrowPoint', x, y)
            cpu.pc, cpu.sp, cpu.p = linked['symbols']['SteveThrowOverlap'], 0xf0, 0x20
            cpu.stPushWord(0x4fff)
            for _ in range(160):
                if cpu.pc == 0x5000:
                    break
                cpu.step()
            else:
                raise AssertionError('Overlap leaf did not return')
            expected = left-8 <= x < right+8 and top-8 <= y <= bottom+8
            assert bool(cpu.p & 1) == expected, (left, top, width, height, x, y)
            assert cpu.sp == 0xf0
            count += 1
    print(json.dumps(dict(cases=count, bytes=len(code), output_files=0,
                          scope='Detached geometry only; native enemy admission and damage remain separate.')))


if __name__ == '__main__':
    main()

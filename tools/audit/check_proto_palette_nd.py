"""Exercise the compiled Proto Man palette append at every queue offset."""
from pathlib import Path
import argparse, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'build/verification/specialist-mario-easy-hard-source-a/deps'))
from py65.devices.mpu6502 import MPU


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    raw = a.rom.read_bytes()
    symbols, segments = {}, {}
    for line in a.rom.with_suffix('.dbg').read_text().splitlines():
        if not line.startswith(('seg\t', 'sym\t')):
            continue
        fields = dict(x.split('=', 1) for x in line[4:].split(','))
        if line.startswith('seg\t'):
            segments[int(fields['id'])] = fields
        elif 'val' in fields:
            symbols[fields['name'].strip('"')] = fields
    routine = symbols['ProtoQueueBasePalette']
    segment = segments[int(routine['seg'])]
    start, size, offset = (int(segment[n], 0) for n in ('start', 'size', 'ooffs'))
    address = lambda name: int(symbols[name]['val'], 0)
    b = address('VRAM_Buffer1')
    cases = 0
    for status in range(3):
        for queue_offset in range(256):
            memory = [0] * 65536
            memory[start:start+size] = raw[offset:offset+size]
            memory[b:b+400] = [0xa5]*400
            memory[address('PlayerStatus')] = status
            memory[address('VRAM_Buffer1_Offset')] = queue_offset
            memory[0x1e1:0x1e3] = [0xfe, 0x5d]
            cpu = MPU(memory=memory, pc=int(routine['val'], 0))
            cpu.sp = 0xe0
            for _ in range(100):
                if cpu.pc == 0x5dff:
                    break
                cpu.step()
            else:
                raise AssertionError(('timeout', status, queue_offset))
            expected = [0xa5]*400
            new_offset = queue_offset
            if queue_offset < 78:
                expected[queue_offset:queue_offset+7] = [0x3f, 0x11, 3, 0x0f, 0x16, 0x28 if status == 2 else 0x10, 0]
                new_offset += 6
            assert memory[b:b+400] == expected, (status, queue_offset)
            assert memory[address('VRAM_Buffer1_Offset')] == new_offset
            cases += 1
    report = dict(passed=True, ROM_sha256=hashlib.sha256(raw).hexdigest(),
                  compiled_cases=cases, exclusive_guard=78, append_bytes=6,
                  scope='Isolated compiled 6502 append, all offsets and three power states; native cold selection/lives checks are separate.')
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()

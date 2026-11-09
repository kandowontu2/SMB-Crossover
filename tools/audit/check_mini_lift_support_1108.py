"""Verify the linked Mini lift contact around both edges and page boundaries."""
import argparse
import itertools
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU

from prepare_selected_native_packet_v1 import sha


def call(memory, address):
    cpu = MPU(memory=memory, pc=address)
    cpu.sp = 0xe0
    cpu.stPushWord(0x5aff)
    for _ in range(800):
        if cpu.pc == 0x5b00:
            assert cpu.sp == 0xe0
            return bool(cpu.p & cpu.CARRY),cpu.processorCycles
        assert memory[cpu.pc]
        cpu.step()
    raise AssertionError('Mini lift contact did not return')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = args.candidate/'candidate.json'
    info = json.loads(manifest.read_text())
    source = args.candidate/'mini-lift.bin'
    code = source.read_bytes()
    assert sha(source) == info['kernel_SHA256']
    entry = info['labels']['MiniPlatformFloor']
    actor = info['labels']['MiniLiftActor']
    support = info['labels']['MiniLiftGround']
    m = bytearray(0x10000)
    m[0xa000:0xa000+len(code)] = code
    cases = 0
    limits = [0,0]
    for edge,top,slot,dx,old_y,next_y,latched in itertools.product(
            [0x200,0x2ff,0x330], [128,161,192], [0,5], [-256,-7,-6,-1,0,30,31,256],
            [-1,0,1], [-1,0,1], [False,True]):
        source_x = (edge+dx)*16+15
        candidate_y = (top-8+next_y)*16+15
        m[0xc250:0xc252] = source_x.to_bytes(2,'little')
        m[0xc270:0xc272] = candidate_y.to_bytes(2,'little')
        m[0x76+slot],m[0x5d+slot],m[0xbe+slot] = edge&255,edge>>8,top
        m[0x10+slot],m[0x17+slot],m[0x1f+slot] = 1,0x25,0x40
        m[0xbd],m[0xa4] = top-32+old_y,1
        m[actor],m[support] = slot+1,(slot+1 if latched else 0)
        hit,cycles = call(m,entry)
        expected = -6 <= dx <= 30 and (latched or (old_y<=0 and next_y>=0))
        assert hit == expected, (edge,top,slot,dx,old_y,next_y,latched,hit)
        expected_y = (top-8)*16 if expected else candidate_y
        assert int.from_bytes(m[0xc270:0xc272],'little') == expected_y
        assert m[support] == (slot+1 if expected else 0)
        limits[hit] = max(limits[hit],cycles)
        cases += 1
    m[actor],m[support] = 0,6
    assert not call(m,entry)[0] and not m[support]
    args.output.mkdir()
    report = dict(passed=True, linked_floor_cases=cases, worst_miss_cycles=limits[0],
                  worst_hit_cycles=limits[1], kernel_SHA256=sha(source),
                  scope='Actual linked floor instructions. Fixed actor slot fixture; full native spawn and traversal are separate.')
    (args.output/'floor-CPU.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()

"""Trace original donor palette/OAM consumers through controller input only.

Instruction model evidence, not native emulator qualification.
"""
from pathlib import Path
import argparse
import hashlib
import json
from collections import Counter

from benj_mario_donor_trace_1030_v1 import Bus, MPU, DONOR, EXPECTED, FRAME


class TraceBus(Bus):
    def __init__(self, raw):
        super().__init__(raw)
        self.palette_writes = []

    def __setitem__(self, addr, value):
        if addr < 0x4000 and addr & 7 == 7 and self.addr >= 0x3f00:
            self.palette_writes.append(dict(frame=self.cpu.processorCycles // FRAME,
                pc=self.cpu.pc, address=self.addr, value=value,
                source_fetches=list(self.last_rom)))
        super().__setitem__(addr, value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--frames', type=int, default=300)
    args = ap.parse_args()
    assert not args.output.exists() and 150 <= args.frames <= 400
    raw = DONOR.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    bus = TraceBus(raw)
    cpu = MPU(memory=bus, pc=None)
    bus.cpu = cpu
    cpu.reset()
    next_frame, instructions, snapshots = FRAME, 0, []
    while cpu.processorCycles < args.frames * FRAME:
        frame = cpu.processorCycles // FRAME
        bus.pad = 1 if any(65 + 10*i <= frame < 68 + 10*i for i in range(3)) else 0
        if 125 <= frame < 128:
            bus.pad = 16
        assert bus[cpu.pc] != 0, ('BRK', hex(cpu.pc), frame)
        cpu.step()
        instructions += 1
        assert instructions <= 6500000
        if cpu.processorCycles >= next_frame:
            bus.frame += 1
            if bus.ctrl & 128:
                cpu.nmi()
            if bus.frame in [120, 150, 200, 250, args.frames]:
                snapshots.append(dict(frame=bus.frame, palette=list(bus.vram[0x3f00:0x3f20]),
                    character=bus.ram[0x620b], custom_art=bus.ram[0x623f],
                    mode=bus.ram[0x770], task=bus.ram[0x772],
                    visible_oam=[list(bus.oam[i:i+4]) for i in range(0,256,4) if bus.oam[i]<240]))
            next_frame += FRAME
    args.output.mkdir(parents=True)
    for name, data in [('ram.bin',bus.ram[:0x8000]), ('ppu.bin',bus.vram),
                       ('oam.bin',bus.oam), ('chr-ram.bin',bus.chr)]:
        (args.output/name).write_bytes(data)
    result = dict(status='ORIGINAL_DONOR_CONTROLLER_PALETTE_TRACE_NOT_NATIVE',
        source_sha256=EXPECTED, tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        frames=args.frames, instructions=instructions, snapshots=snapshots,
        palette_writes=bus.palette_writes, final_banks=bus.banks,
        mapper_registers=bus.reg, mapper_select=bus.select)
    (args.output/'trace.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(instructions=instructions, snapshots=snapshots),indent=2))


if __name__ == '__main__':
    main()

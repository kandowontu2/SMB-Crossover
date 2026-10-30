"""Bounded instruction-level donor discovery; not a native PPU/timing test.

Run the exact v44 donor's reset, mapper, buffered CHR reads and serial input.
Retain the CHR-RAM upload provenance instead of assuming PRG bytes are tiles.
"""
from pathlib import Path
import argparse
import hashlib
import json
from collections import Counter
from py65.devices.mpu6502 import MPU

R = Path(__file__).resolve().parents[2]
DONOR = Path("C:/NES/the stash/SuperDuperMarioBros4P-v44-nes2header.nes")
EXPECTED = "840af2ccf798a935ab2e63e3d4409da159f48d68928f9d71ee33b608c4aa3ff4"
FRAME = 29781


class Bus:
    def __init__(self, raw):
        self.prg = raw[16:]
        self.ram = bytearray(65536)
        self.chr = bytearray(8192)
        self.vram = bytearray(16384)
        self.oam = bytearray(256)
        self.reg = [0, 2, 4, 5, 6, 7, 0, 1]
        self.select = self.ctrl = self.mask = self.addr = self.latch = 0
        self.buffer = self.oam_addr = self.pad = self.serial = self.strobe = 0
        self.cpu = None
        self.frame = 0
        self.uploads = Counter()
        self.last_rom = []
        self.upload_sources = {}
        self.chr_provenance = [-1] * 8192
        self.bank_writes = 0
        self.mirror = 0
        self.remap()

    def remap(self):
        last = len(self.prg) // 8192 - 1
        banks = [self.reg[6], self.reg[7], last - 1, last]
        if self.select & 64:
            banks[0], banks[2] = banks[2], banks[0]
        self.banks = [b & last for b in banks]
        for i, b in enumerate(self.banks):
            self.ram[0x8000 + i * 8192:0xa000 + i * 8192] = self.prg[b * 8192:(b + 1) * 8192]

    def chr_at(self, addr):
        pages = [self.reg[0] & 6, self.reg[0] | 1, self.reg[1] & 6,
                 self.reg[1] | 1, *self.reg[2:6]]
        if self.select & 128:
            pages = pages[4:] + pages[:4]
        return (pages[addr // 1024] & 7) * 1024 + addr % 1024

    def ppu_at(self, addr):
        addr &= 0x3fff
        if addr < 0x2000:
            return self.chr, self.chr_at(addr)
        if addr >= 0x3f00:
            addr = 0x3f00 | (addr & 31)
            if addr & 0x13 == 0x10:
                addr &= ~0x10
        else:
            addr = 0x2000 | ((addr - 0x2000) & 0xfff)
            table = (addr - 0x2000) // 1024
            physical = table // 2 if self.mirror else table % 2
            addr = 0x2000 + physical * 1024 + addr % 1024
        return self.vram, addr

    def __getitem__(self, addr):
        if isinstance(addr, slice):
            return [self[i] for i in range(*addr.indices(65536))]
        addr &= 0xffff
        if addr < 0x2000:
            return self.ram[addr & 0x7ff]
        if 0x2000 <= addr < 0x4000:
            reg = addr & 7
            if reg == 2:
                self.latch = 0
                cycle = self.cpu.processorCycles % FRAME
                # Instruction fixture only: no cycle-accurate sprite-zero model.
                return (128 if cycle >= 27300 else 0) | (64 if 14000 < cycle < 27300 else 0)
            if reg == 4:
                return self.oam[self.oam_addr]
            if reg == 7:
                mem, at = self.ppu_at(self.addr)
                value = mem[at] if self.addr >= 0x3f00 else self.buffer
                self.buffer = mem[at]
                self.addr = (self.addr + (32 if self.ctrl & 4 else 1)) & 0x3fff
                return value
            return 0
        if addr in (0x4016, 0x4017):
            if addr == 0x4017:
                return 0x40
            value = (self.pad >> (7 - min(self.serial, 7))) & 1 if self.serial < 8 else 1
            if not self.strobe:
                self.serial += 1
            return 0x40 | value
        if addr >= 0x8000:
            off = self.banks[(addr - 0x8000) // 8192] * 8192 + addr % 8192
            self.last_rom.append(off + 16)
            self.last_rom = self.last_rom[-5:]
        return self.ram[addr]

    def __setitem__(self, addr, value):
        addr &= 0xffff
        value &= 255
        if addr < 0x2000:
            self.ram[addr & 0x7ff] = value
        elif addr < 0x4000:
            reg = addr & 7
            if reg == 0:
                self.ctrl = value
            elif reg == 1:
                self.mask = value
            elif reg == 3:
                self.oam_addr = value
            elif reg == 4:
                self.oam[self.oam_addr] = value
                self.oam_addr = (self.oam_addr + 1) & 255
            elif reg == 5:
                self.latch ^= 1
            elif reg == 6:
                self.addr = ((value & 63) << 8) | (self.addr & 255) if not self.latch else (self.addr & 0x3f00) | value
                self.latch ^= 1
            elif reg == 7:
                mem, at = self.ppu_at(self.addr)
                mem[at] = value
                if self.addr < 0x2000:
                    pc = (self.cpu.pc - 3) & 0xffff
                    self.uploads[pc] += 1
                    if pc not in self.upload_sources:
                        self.upload_sources[pc] = list(self.last_rom)
                    if 0x7000 <= pc < 0x7400:
                        self.chr_provenance[at] = self.last_rom[-1]
                self.addr = (self.addr + (32 if self.ctrl & 4 else 1)) & 0x3fff
        elif addr == 0x4014:
            base = value * 256
            self.oam[:] = bytes(self[base + i] for i in range(256))
            self.cpu.processorCycles += 513
        elif addr == 0x4016:
            self.strobe = value & 1
            if self.strobe:
                self.serial = 0
        elif addr >= 0x8000:
            reg = addr & 0xe001
            if reg == 0x8000:
                self.select = value
                self.remap()
            elif reg == 0x8001:
                self.reg[self.select & 7] = value
                self.bank_writes += 1
                self.remap()
            elif reg == 0xa000:
                self.mirror = value & 1
        elif addr >= 0x6000:
            self.ram[addr] = value


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--frames", type=int, default=120)
    ap.add_argument("--right", type=int, default=0)
    a = ap.parse_args()
    assert 1 <= a.frames <= 600 and 0 <= a.right <= 3
    assert not a.output.exists()
    raw = DONOR.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    bus = Bus(raw)
    cpu = MPU(memory=bus, pc=None)
    bus.cpu = cpu
    cpu.reset()
    samples = []
    instructions = nmis = 0
    next_frame = FRAME
    while cpu.processorCycles < a.frames * FRAME:
        frame = cpu.processorCycles // FRAME
        bus.pad = 1 if any(65 + 10 * i <= frame < 68 + 10 * i for i in range(a.right)) else 0
        assert bus[cpu.pc] != 0, ("BRK", hex(cpu.pc), frame)
        cpu.step()
        instructions += 1
        assert instructions <= 6500000
        if cpu.processorCycles >= next_frame:
            bus.frame += 1
            if bus.ctrl & 128:
                cpu.nmi()
                nmis += 1
            if bus.frame in (30, 60, 90, 120, a.frames):
                samples.append(dict(frame=bus.frame, pc=cpu.pc, ctrl=bus.ctrl, mask=bus.mask,
                                    donor_ram_6205_6208=list(bus.ram[0x6205:0x6209]),
                                    oam_visible=sum(bus.oam[i] < 240 for i in range(0, 256, 4))))
            next_frame += FRAME
    a.output.mkdir(parents=True)
    for name, data in [("chr-ram.bin", bus.chr), ("oam.bin", bus.oam),
                       ("ppu.bin", bus.vram), ("ram.bin", bus.ram[:0x8000])]:
        (a.output / name).write_bytes(data)
    proof = dict(status="DONOR_INSTRUCTION_DISCOVERY_NOT_NATIVE_GRAPHICS_QUALIFICATION",
                 source=dict(path=str(DONOR), sha256=EXPECTED, bytes=len(raw)),
                 tool_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 frames=a.frames, right_presses=a.right, instructions=instructions, nmis=nmis,
                 mapper_writes=bus.bank_writes, mapper_registers=bus.reg,
                 mapper_select=bus.select, prg_banks=bus.banks, ctrl=bus.ctrl,
                 mask=bus.mask, samples=samples,
                 chr_ram_source_offsets=bus.chr_provenance,
                 chr_uploads=[dict(pc=hex(pc), bytes=n, source_fetch_example=bus.upload_sources[pc])
                              for pc, n in bus.uploads.items()],
                 limits="Approximate PPU status/sprite-zero and frame boundary NMI; IRQ not modeled. No visual, cadence, native playthrough, or readiness claim.")
    (a.output / "discovery.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps({k: proof[k] for k in ["status", "frames", "instructions", "nmis", "mapper_writes"]} |
                     dict(chr_upload_bytes=sum(bus.uploads.values()),
                          chr_upload_instruction_sites=len(bus.uploads),
                          final_visible_oam=samples[-1]["oam_visible"])))


if __name__ == "__main__":
    main()

"""Bounded instruction discovery for the supplied Infidelity SMB3+ donor.

Uses the previous small MMC3 fixture, with real PRG size and banked CHR ROM.
The fixture does not model the MMC3 scanline IRQ or native PPU raster timing.
"""
from pathlib import Path
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import benj_mario_donor_trace_1030_v1 as T

DONOR = Path("C:/NES/the stash/Super Mario Bros. 3+.nes")
EXPECTED = "be750155f9005314d6ba79874c4de5b979cad0526b6cb348194d2bd4f3b90c56"


class ChrRomBus(T.Bus):
    def __init__(self, raw):
        size = raw[4] * 16384
        super().__init__(raw[:16 + size])
        self.chr = bytearray(raw[16 + size:])
        assert len(self.prg) == 524288 and len(self.chr) == 262144

    def chr_at(self, addr):
        pages = [self.reg[0] & 254, self.reg[0] | 1,
                 self.reg[1] & 254, self.reg[1] | 1, *self.reg[2:6]]
        if self.select & 128:
            pages = pages[4:] + pages[:4]
        return pages[addr // 1024] * 1024 + addr % 1024

    def __getitem__(self, addr):
        if isinstance(addr, int) and addr == 0x4016:
            frame = self.cpu.processorCycles // T.FRAME
            self.pad = 16 if (65 <= frame < 69 or 180 <= frame < 184) else 0
        return super().__getitem__(addr)

    def __setitem__(self, addr, value):
        if 0x2000 <= addr < 0x4000 and addr & 7 == 7 and self.addr < 0x2000:
            # CHR-ROM rejects writes, unlike the original CHR-RAM donor fixture.
            self.addr = (self.addr + (32 if self.ctrl & 4 else 1)) & 0x3fff
            return
        super().__setitem__(addr, value)


def main():
    # Only the private imported module object is parameterized. The frozen v44
    # module, its source receipts and native donor artifacts stay byte-exact.
    T.DONOR = DONOR
    T.EXPECTED = EXPECTED
    T.Bus = ChrRomBus
    T.main()
    out = Path(sys.argv[sys.argv.index("--output") + 1])
    p = out / "discovery.json"
    h = json.loads(p.read_text())
    h.update(status="SMB3PLUS_INSTRUCTION_DISCOVERY_NOT_PORT_OR_NATIVE_QUALIFICATION",
             credit="Super Mario Bros. 3+ — Infidelity",
             wrapper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             input_script="Start held at frames65..68 and180..183; no other input.",
             limits="Approximate PPU status/sprite-zero and frame NMI; MMC3 IRQ unmodeled. No graphics, playthrough, physics, cadence, or readiness claim.")
    p.write_text(json.dumps(h, indent=2) + "\n")
    print(json.dumps(dict(status=h["status"], source_sha256=EXPECTED,
                          PRG_banks=h["prg_banks"], CHR_registers=h["mapper_registers"][:6],
                          ctrl=h["ctrl"], mask=h["mask"])))


if __name__ == "__main__":
    main()

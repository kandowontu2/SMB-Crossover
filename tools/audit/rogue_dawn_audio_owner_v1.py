"""Trace the actual Rogue Dawn C215 audio mapper, not dormant stock drivers.

Finite original RP2A03 CPU traces; no host import, allocation, native audio,
PPU/DMC timing, or exhaustive driver-closure claim.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools/audit")]
import rogue_dawn_map_v1 as ref
from verify_native_relocation import NesMPU

OUT = ROOT / "docs/qa/rogue-dawn-actual-audio-owner-2026-10-28.json"


class Memory(bytearray):
    def __init__(self, raw):
        super().__init__(65536)
        self.raw, self.banks, self.selected = raw, [2, 61, 62, 63], 7
        self.read_ROM, self.executed = set(), set()
        self.read_RAM, self.written_RAM = set(), set()
        self.apu_reads, self.apu_counts, self.maps = Counter(), Counter(), []
        self.apu_hash, self.apu_prefix = hashlib.sha256(), []
        for slot, bank in enumerate(self.banks):
            self.map(slot, bank)

    def map(self, slot, bank):
        assert 0 <= bank < 64
        self.banks[slot] = bank
        start = 16+bank*8192
        bytearray.__setitem__(self, slice(0x8000+slot*8192, 0xa000+slot*8192),
                              self.raw[start:start+8192])

    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= 0x8000:
                self.read_ROM.add((self.banks[(key-0x8000)//8192], key&8191))
            elif key < 0x800 or key >= 0x6000:
                self.read_RAM.add(key)
            elif 0x4000 <= key <= 0x4017:
                self.apu_reads[key] += 1
        return bytearray.__getitem__(self, key)

    def __setitem__(self, key, value):
        if isinstance(key, int):
            if key == 0x8000:
                assert not value&64, "Source audio mapper must remain MMC3 mode0"
                self.selected = value&7
                self.maps.append([key, value])
                return
            if key == 0x8001:
                assert self.selected in [6, 7]
                self.maps.append([key, value])
                self.map(self.selected-6, value)
                return
            assert key < 0x8000, ("ROM write outside actual mapper", hex(key), value)
            if key < 0x800 or key >= 0x6000:
                self.written_RAM.add(key)
            if 0x4000 <= key <= 0x4017:
                self.apu_counts[key] += 1
                self.apu_hash.update(bytes([key&255, key>>8, value]))
                if len(self.apu_prefix) < 20:
                    self.apu_prefix.append([key, value])
        return bytearray.__setitem__(self, key, value)


def call(m, pc):
    c = NesMPU(memory=m, pc=pc)
    c.sp = 0xfd
    c.stPushWord(0x5aff)
    minimum = 0xfd
    for _ in range(40000):
        if c.pc == 0x5b00:
            assert c.sp == 0xfd
            return c.processorCycles, minimum
        assert c.pc >= 0x8000, ("Unexpected original execution owner", hex(c.pc))
        m.executed.add((m.banks[(c.pc-0x8000)//8192], c.pc&8191))
        assert m[c.pc] != 0, ("Original BRK", hex(c.pc), m.banks)
        c.step()
        minimum = min(minimum, c.sp)
    raise AssertionError(("Source audio did not return", hex(c.pc)))


def ranges(addresses):
    result = []
    for address in sorted(addresses):
        if not result or result[-1][1] != address:
            result.append([address, address+1])
        else:
            result[-1][1] += 1
    return result


def main():
    assert not OUT.exists(), "Preserve frozen observation"
    raw = ref.ROM.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    # Actual C215..C237 and two real original area tables, not stock labels.
    fixed = 16+62*8192
    assert raw[fixed+0x215:fixed+0x224] == bytes.fromhex("a423b938c2a82024c24c70a74c47c2")
    music_banks = list(raw[fixed+0x238:fixed+0x23e])
    music_flags = list(raw[fixed+0x256:fixed+0x25c])
    assert music_banks == [52, 48, 53, 54, 50, 51]
    assert music_flags == [16, 1, 8, 64, 16, 128]
    rows, all_rom, all_code, all_ram_r, all_ram_w = [], set(), set(), set(), set()
    for area, (lower, flag) in enumerate(zip(music_banks, music_flags)):
        m = Memory(raw)
        m[0x23], m[0x1e], m[0x2f] = area, 3, 0x1d
        # Genuine source silence request enters B404 init through C215/A770.
        m[0x680] = 1
        call(m, 0xc215)
        assert m.banks[:2] == [lower, 49]
        m[0x62c] = 1  # Declared repeating-music source arena, not a host policy.
        m[0x685] = flag
        cycles, minimum, pointers, heard = [], 255, set(), Counter()
        for tick in range(2400):
            m[0x2d] = tick&255
            call(m, 0xc000)  # Original source LFSR; no invented random notes.
            cost, low = call(m, 0xc215)
            cycles.append(cost)
            minimum = min(minimum, low)
            pointers.add(tuple(bytearray.__getitem__(m, slice(0x630, 0x638))))
            heard[m[0x68d]] += 1
        # Separate finite valid producer cue samples; retains native priority
        # and real continuation state rather than entering individual leaves.
        cue_rows = []
        for address, bit in [(0x680, 2), (0x680, 4), (0x680, 8),
                             (0x681, 2), (0x681, 0x10), (0x681, 0x40),
                             (0x681, 0x80), (0x683, 4), (0x684, 0x40)]:
            m[address] |= bit
            cue_cost = []
            for tick in range(96):
                m[0x2d] = (tick+2400)&255
                call(m, 0xc000)
                cost, low = call(m, 0xc215)
                cue_cost.append(cost)
                minimum = min(minimum, low)
            cue_rows.append(dict(source_queue=hex(address), bit=bit, updates=96,
                                 CPU_range=[min(cue_cost), max(cue_cost)]))
        assert not m.apu_reads, dict(m.apu_reads)
        assert m.apu_counts[0x4017] >= 2400
        rows.append(dict(area=area, source_music_flag=flag, lower_bank=lower,
                         upper_bank=49, music_updates=2400, finite_cue_samples=cue_rows,
                         observed_music_flags=dict(heard), distinct_music_base_images=len(pointers),
                         CPU_range=[min(cycles), max(cycles)], minimum_SP=minimum,
                         APU_write_counts={hex(k): v for k, v in sorted(m.apu_counts.items())},
                         ordered_APU_sha256=m.apu_hash.hexdigest(), APU_prefix=m.apu_prefix))
        all_rom |= m.read_ROM
        all_code |= m.executed
        all_ram_r |= m.read_RAM
        all_ram_w |= m.written_RAM
    banks = []
    for bank in sorted(set(b for b, _ in all_rom)):
        selected = {o for b, o in all_rom if b == bank}
        spans = ranges(selected)
        banks.append(dict(bank=bank, observed_bytes=len(selected), ranges=[
            dict(offset_start=s, end_exclusive=e, bytes=e-s,
                 sha256=ref.digest(raw[16+bank*8192+s:16+bank*8192+e]))
            for s, e in spans], executed_instruction_PCs=sum(b == bank for b, _ in all_code)))
    report = dict(status="PASS_FINITE_ORIGINAL_AUDIO_OWNER_TRACE_NO_HOST_IMPORT", passed=True,
                  native_run=False, source=ref.binding(ref.ROM),
                  actual_path="Original NMI C0D9 calls C215 even when body update is skipped; C215/C224 maps PRG6 via C238, PRG7=49, then JMP A770 -> A776 transition owner -> B3B4",
                  source_area_music_banks=music_banks, source_area_music_flags=music_flags,
                  dormant_driver_warning="3/5/7/9 B3B4 and B200..BFD4 resemble stock code, but source C215 plays49 with six lower note banks. That resemblance cannot qualify stock Samus audio reuse.",
                  source_music_arena="Actual source running mode3, area0..5, original silence init, declared source repeat1, actual C000 LFSR and2D progression; no PPU/controller/native gameplay claim",
                  traces=rows, observed_source_ROM_regions=banks,
                  observed_borrowed_ZP_reads=[hex(a) for a in sorted(all_ram_r) if a < 256],
                  observed_borrowed_ZP_writes=[hex(a) for a in sorted(all_ram_w) if a < 256],
                  observed_RAM_write_ranges=ranges(a for a in all_ram_w if not 0x100 <= a < 0x200),
                  total_finite_observed_ROM_bytes=len(all_rom),
                  no_APU_status_reads_in_tested_domain=True,
                  remaining=["Static/transitive instruction and data closure for all valid native requests, transition phases, pause, source low-health cadence and title/scene cancellation",
                             "Storage mapping/repacking plus genuine source relocation and private RAM/ZP adapter",
                             "Atomic actual foreground cues/NMI acknowledgement, world mixing, host timing/native listening"],
                  bindings=[ref.binding(p) for p in [Path(__file__), ref.ROM,
                      ROOT / "tools/rogue_dawn_map_v1.py",
                      ROOT / "tools/audit/verify_native_relocation.py"]])
    OUT.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(dict(output=str(OUT), SHA256=ref.digest(OUT.read_bytes()),
                          updates=6*(2400+9*96), observed_ROM_bytes=len(all_rom),
                          observed_banks=[b["bank"] for b in banks])))


if __name__ == "__main__":
    main()

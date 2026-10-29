"""Bounded actual-cartridge Rogue songs/effects/pause/transition observation.

Produces one aggregate JSON; no captures, ROM copy or shared runtime changes.
"""
from collections import Counter
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools/audit")]
import rogue_dawn_map_v1 as ref
import rogue_dawn_audio_owner_v1 as owner
from verify_native_relocation import NesMPU

OUT = ROOT / "docs/qa/rogue-dawn-audio-campaigns-2026-10-28.json"
GRAPH = ROOT / "docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json"


def call(m, pc, graph, counts):
    c = NesMPU(memory=m, pc=pc)
    c.sp = 0xfd
    c.stPushWord(0x5aff)
    minimum = 0xfd
    for _ in range(40000):
        if c.pc == 0x5b00:
            assert c.sp == 0xfd
            return c.processorCycles, minimum
        assert c.pc >= 0x8000, (hex(c.pc), m.banks)
        bank = m.banks[(c.pc-0x8000)//8192]
        if bank == 49:
            assert c.pc in graph, ("Runtime instruction missing from actual static closure", hex(c.pc))
            counts[c.pc] += 1
        m.executed.add((bank, c.pc&8191))
        assert m[c.pc] != 0, ("Original BRK", hex(c.pc), m.banks)
        c.step()
        minimum = min(minimum, c.sp)
    raise AssertionError(("Original audio nonreturn", hex(c.pc)))


def main():
    assert not OUT.exists(), "Preserve frozen observation"
    raw = ref.ROM.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    graph_receipt = json.loads(GRAPH.read_text())
    graph = {r["pc"] for r in graph_receipt["graph"]["instructions"]}
    lower_banks = [52, 48, 53, 54, 50, 51]
    normal_flags = [16, 1, 8, 64, 16, 128]
    alternate_flags = [16, 16, 1, 1, 1, 1]
    rows, rom_reads, code_reads, ram_reads, ram_writes = [], set(), set(), set(), set()
    aggregate = Counter()
    total_updates = 0
    # All single-bit EFFECT requests use the cartridge's actual dispatch table,
    # including true no-op entries. This does not declare every music flag legal
    # in every source area: normal/alternate headers use C256/C25E exactly.
    effects = [(0x680, 1 << bit) for bit in range(1, 8)]
    effects += [(q, 1 << bit) for q in [0x681, 0x683] for bit in range(8)]
    for area, lower in enumerate(lower_banks):
        for kind, queue, flag, limit in [
                ("normal", 0x685, normal_flags[area], 8192),
                ("alternate", 0x685, alternate_flags[area], 8192),
                ("item", 0x684, 0x40, 1800),
                ("fade", 0x684, 0x80, 1800),
                ("transition", 0x685, normal_flags[area], 240),
                ("effects-and-pause", 0x685, normal_flags[area], len(effects)*96+96)]:
            m, counts = owner.Memory(raw), Counter()
            m[0x23], m[0x1e], m[0x2f] = area, 3, 0x1d
            m[0x680] = 1
            call(m, 0xc215, graph, counts)
            m[0x62c] = 1
            m[queue] = flag
            if kind == "transition":
                m[0x6ef] = 1  # Actual original producer INC, audio phases2..6.
            costs, minimum, completed, quiet = [], 255, False, 0
            phase_values, theme_values = set(), set()
            for tick in range(limit):
                m[0x2d] = tick & 255
                call(m, 0xc000, graph, counts)
                if kind == "effects-and-pause":
                    if tick < len(effects)*96 and tick % 96 == 0:
                        address, bit = effects[tick//96]
                        m[address] |= bit
                    # Genuine source mode5 enters the real B399 pause owner;
                    # NMI itself continues. The next32 updates resume mode3.
                    m[0x1e] = 5 if len(effects)*96 <= tick < len(effects)*96+64 else 3
                cost, low = call(m, 0xc215, graph, counts)
                costs.append(cost)
                minimum = min(minimum, low)
                phase_values.add(m[0x6ef])
                theme_values.add(m[0x6f0])
                total_updates += 1
                # Normal song restart is the actual second BF19 execution,
                # not a guessed note count or a timer-only completion claim.
                if kind in ["normal", "alternate"] and counts[0xbf19] >= 2:
                    completed = True
                    break
                if kind in ["item", "fade"]:
                    quiet = quiet+1 if not any(m[a] for a in [0x68c, 0x68d, 0x684, 0x685]) else 0
                    if quiet >= 16:
                        completed = True
                        break
            assert m.banks[:2] == [lower, 49]
            assert not m.apu_reads, dict(m.apu_reads)
            aggregate.update(counts)
            rom_reads |= m.read_ROM
            code_reads |= m.executed
            ram_reads |= m.read_RAM
            ram_writes |= m.written_RAM
            rows.append(dict(area=area, kind=kind, lower_bank=lower,
                             source_queue=queue, request=flag, updates=len(costs),
                             complete_song_restart_or_fanfare_quiet=completed,
                             BF19_initializations=counts[0xbf19],
                             CPU_range=[min(costs), max(costs)], minimum_SP=minimum,
                             transition_phases=sorted(phase_values),
                             source_theme_values=sorted(theme_values),
                             ordered_APU_sha256=m.apu_hash.hexdigest(),
                             APU_write_counts={hex(k): v for k,v in sorted(m.apu_counts.items())}))
            print(json.dumps(dict(area=area, kind=kind, updates=len(costs), complete=completed)), flush=True)
    bank_rows = []
    for bank in sorted({b for b,_ in rom_reads}):
        offsets = {o for b,o in rom_reads if b == bank}
        spans = owner.ranges(offsets)
        bank_rows.append(dict(bank=bank, bytes=len(offsets), ranges=[
            dict(start=s, end_exclusive=e, sha256=ref.digest(raw[16+bank*8192+s:16+bank*8192+e]))
            for s,e in spans]))
    report = dict(status="PASS_BOUNDED_ORIGINAL_AUDIO_CAMPAIGNS_NO_HOST_IMPORT", passed=True,
                  native_run=False, source=ref.binding(ref.ROM), campaigns=rows,
                  total_updates=total_updates, actual_code_PCs=len(code_reads),
                  actual49_instruction_PCs=len(aggregate),
                  static_graph_all_runtime49_PCs_admitted=True,
                  observed_ROM=bank_rows,
                  source_RAM_read_ranges=owner.ranges(ram_reads),
                  source_RAM_write_ranges=owner.ranges(ram_writes),
                  fixture_seeds="23area/1Emode/2Dclock/2FLFSRseed/62Crepeat/queues; transition additionally actual06EF=1; these producer writes are included in raw memory sets and are not all audio-owned",
                  scope="Source C215/NMI callback, all six C256/C25E normal/alternate selections, actual item/fade, phase1 transition, every single-bit noise/SQ1/triangle dispatch and true mode5 pause. Finite 96-update effects are not an exhaustive combined-priority or native-gameplay campaign.",
                  remaining=["Complete static ROM-data/read-bound closure beyond finite observed songs/effects",
                             "Source-to-host relocation and genuine assembled differential",
                             "Foreground transition/UI/low-health/life/area request protocols",
                             "Host mapper/RAM/ZP/APU mixing and native timing/listening"],
                  bindings=[ref.binding(p) for p in [Path(__file__), GRAPH,
                      ROOT / "tools/audit/rogue_dawn_audio_closure_v1.py",
                      ROOT / "tools/audit/rogue_dawn_audio_owner_v1.py",
                      ROOT / "tools/rogue_dawn_map_v1.py",
                      ROOT / "tools/audit/verify_native_relocation.py"]])
    OUT.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(dict(output=str(OUT.relative_to(ROOT)), updates=total_updates,
                          ROM_bytes=sum(row["bytes"] for row in bank_rows))))


if __name__ == "__main__":
    main()

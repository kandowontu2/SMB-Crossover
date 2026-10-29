"""Observe real Rogue weapon-audio context dependencies on the original CPU."""
from collections import Counter
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "tools/audit")]
import rogue_dawn_map_v1 as ref
import rogue_dawn_audio_owner_v1 as owner
import rogue_dawn_audio_campaigns_v1 as campaigns

OUT = ROOT / "docs/qa/rogue-dawn-audio-weapon-context-2026-10-28.json"


def main():
    assert not OUT.exists(), "Preserve frozen source evidence"
    raw = ref.ROM.read_bytes()
    assert ref.digest(raw) == ref.EXPECTED
    g = json.loads(campaigns.GRAPH.read_text())["graph"]
    graph = {r["pc"] for r in g["instructions"]}
    # These are actual absolute foreground reads, not random RAM dependency
    # noise. B09E's apparent STA061F is NOT in the actual dispatch CFG.
    assert 0xb09e not in graph and 0xb0ab not in graph
    for at, literal in [(0xb0b6, "ad0e01"), (0xb0bb, "ad7868"),
                        (0xb0f0, "ad0803"), (0xb74f, "ad1f06")]:
        assert bytes(raw[16+49*8192+(at&8191):16+49*8192+(at&8191)+3]).hex() == literal
    assert [a for a,b in g["static_edges"] if b == 0xb773] == [0xb772]
    assert [a for a,b in g["static_edges"] if b == 0xb772] == [0xb770]
    assert 0xb773 not in g["roots"] and 0xb772 not in g["roots"]
    rows, aggregate = [], Counter()
    for area, lower in enumerate([52, 48, 53, 54, 50, 51]):
        area_cases = []
        for missile in [0, 1]:
            for gear in [0, 0x40, 0x80, 0xc0]:
                for vy in [0, 4, 0xfc]:
                    for effect in ["beam", "screw"]:
                        m, counts = owner.Memory(raw), Counter()
                        m[0x23], m[0x1e], m[0x2f] = area, 3, 0x1d
                        m[0x680] = 1
                        campaigns.call(m, 0xc215, graph, counts)
                        actual_gear = gear | (8 if effect == "screw" else 0)
                        # Exact projected foreground owners needed by the
                        # audio port; never use host stack/SRAM at old addresses.
                        context = {0x10e: missile, 0x6878: actual_gear,
                                   0x308: vy, 0x61f: 0x80 | (1 if gear&128 and not missile else 0)}
                        for address, value in context.items():
                            m[address] = value
                        if effect == "beam":
                            m[0x681] = 0x10  # Actual Ice/normal beam dispatch.
                        else:
                            m[0x680] = 0x40  # Actual source Screw request.
                        costs = []
                        for tick in range(96):
                            m[0x2d] = tick
                            campaigns.call(m, 0xc000, graph, counts)
                            cost, _ = campaigns.call(m, 0xc215, graph, counts)
                            costs.append(cost)
                            assert all(m[a] == v for a,v in context.items()), "Audio changed a foreground read-only owner"
                        assert m.banks[:2] == [lower,49] and not m.apu_reads
                        aggregate.update(counts)
                        area_cases.append(dict(missile_mode=missile, gear=actual_gear,
                                               source_VY=vy, effect=effect,
                                               source_061F=context[0x61f],
                                               source_06EA_latched=m[0x6ea],
                                               CPU_range=[min(costs),max(costs)],
                                               ordered_APU_sha256=m.apu_hash.hexdigest()))
        rows.append(dict(area=area, cases=area_cases))
        print(json.dumps(dict(area=area, cases=len(area_cases))), flush=True)
    assert aggregate[0xb0b6] and aggregate[0xb0bb] and aggregate[0xb0f0]
    report = dict(status="PASS_ORIGINAL_WEAPON_AUDIO_CONTEXT_MATRIX_NO_HOST_IMPORT",
                  passed=True, native_run=False, cases=6*2*4*3*2,
                  source_updates=6*2*4*3*2*96, observations=rows,
                  required_foreground_projections={"010E":"RdMissileMode", "6878":"RdGear",
                                                    "0308":"RdVY", "061F":"RdBeamSfx"},
                  these_foreground_owners_remain_read_only=True,
                  B09E_B0AB_061F_store_is_not_in_actual_dispatch_CFG=True,
                  static_nonzero_table_predicate=dict(AND1_TAY="B770..B772",
                       indexed_load="B773 reads B778/Y0..1, literal93/81", branch="B776 BNE always",
                       sole_predecessors_verified=True),
                  retained_graph_setup_negatives=[
                      "First naive CFG followed impossible nonzero LDX/LDY BNE fallthrough into volume tableBCB4",
                      "Second conservative CFG followed impossible B776 fallthrough into literal B778=93; actual AND1/TAY plus93/81 proves nonzero"],
                  scope="Actual original49 sound execution in every source area across standing/rising/falling, missile selection and Wave/Ice gear context. No host port, playback quality, combined-priority exhaustion or native cadence claim.",
                  bindings=[ref.binding(p) for p in [Path(__file__), ref.ROM, campaigns.GRAPH,
                      ROOT / "tools/audit/rogue_dawn_audio_context_v1.py",
                      ROOT / "tools/audit/rogue_dawn_audio_campaigns_v1.py",
                      ROOT / "tools/audit/rogue_dawn_audio_owner_v1.py",
                      ROOT / "tools/rogue_dawn_map_v1.py",
                      ROOT / "tools/audit/verify_native_relocation.py"]])
    OUT.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(dict(output=str(OUT.relative_to(ROOT)), cases=report["cases"],
                          updates=report["source_updates"])))


if __name__ == "__main__":
    main()

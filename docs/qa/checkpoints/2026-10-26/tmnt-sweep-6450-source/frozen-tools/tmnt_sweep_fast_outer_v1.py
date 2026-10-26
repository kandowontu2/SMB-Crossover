"""Source-only complete37-identity mixer/caller differential for sweep helper."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load, address
from check_tmnt_audio_fallback_oc import execute
import check_tmnt_audio_fallback_oc
from final_item_matrix import ROSTER
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_multiply import MathMemory
from tmnt_native_storage_owners_cpu import FLAGS
from verify_native_relocation import NesMPU


def outcome(c, m):
    # Only discarded CPU stack and the explicitly newly owned TWO product
    # registers are outside RAM equality. Source/ordinary RAM and all SMC exact.
    ram = bytes(m[:0x1a0]) + bytes(m[0x200:0x5205]) + bytes(m[0x5207:0x8000])
    return c.a, c.x, c.y, c.p & 207, c.sp, ram, list(m.banks), [(at, v) for at, v in m.writes if 0x4000 <= at <= 0x4017 or 0x5000 <= at <= 0x5015]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    check_tmnt_audio_fallback_oc.Memory = MathMemory
    rows, count = [], 0
    for identity, slot, char, variant, value, family in ROSTER:
        for entry in ['AudioUpdate', 'ExpandedAudioUpdate']:
            if entry == 'ExpandedAudioUpdate' and char < 6: continue
            costs, cases = set(), 0
            for mode, flags, phase in itertools.product([0, 1], FLAGS, range(6)):
                seed = dict(SelectedCharacter=char, OperMode=1, CrossoverBehaviorVersion=mode,
                            AreaMusicQueue=[1, 0, 4, 128, 0, 64][phase], EventMusicQueue=[0, 4, 0, 0, 64, 8][phase],
                            GamePauseStatus=int(phase == 4), CurrentBank=215, CurrentBankC=166, XgAudioCharacter=255)
                if variant: seed[variant] = value
                c, m = execute(old, entry, seed, flags=flags)
                d, n = execute(new, entry, seed, flags=flags)
                assert outcome(c, m) == outcome(d, n), (identity, entry, mode, flags, phase)
                assert m.operands == n.operands and m.math_events == n.math_events
                assert m[0x5205:0x5207] == n[0x5205:0x5207]
                costs.add(d.processorCycles - c.processorCycles);cases += 1;count += 1
            rows.append(dict(identity=identity, entry=entry, cases=cases, added_cycles=sorted(costs)))
            print(rows[-1], flush=True)
    warm = []
    for variant, mode in itertools.product(range(4), [0, 1]):
        machines = []
        for b in [old, new]:
            m = MathMemory(b);m.page(2, 38)
            for name, value in dict(SelectedCharacter=19, TnVariant=variant, OperMode=1, CrossoverBehaviorVersion=mode,
                                    AreaMusicQueue=1, CurrentBank=215, CurrentBankC=166, XgAudioCharacter=255).items(): m[address(b, name)] = value
            machines.append((b, NesMPU(memory=m), m))
        parent_cycles, child_cycles, deltas, specifics = [], [], [], {}
        for tick in range(602):
            cycle = []
            for b, c, m in machines:
                c.pc, c.a, c.x, c.y, c.p, c.sp = address(b, 'AudioUpdate'), 85, 3, 7, FLAGS[tick % len(FLAGS)], 253
                m[510], m[511] = 255, 126;m.writes = [];start = c.processorCycles
                for _ in range(50000):
                    if c.pc == 0x7f00: break
                    m.executing_PC = c.pc;c.step()
                else: raise AssertionError(('Warm full outer timeout', variant, mode, tick))
                cycle.append(c.processorCycles - start)
            assert outcome(machines[0][1], machines[0][2]) == outcome(machines[1][1], machines[1][2]), ('Full warm audio state/APU', variant, mode, tick)
            assert cycle[1] <= cycle[0], ('Warm cost regression', variant, mode, tick, cycle)
            parent_cycles.append(cycle[0]);child_cycles.append(cycle[1]);deltas.append(cycle[1] - cycle[0])
            if tick in [407, 505]: specifics[str(tick)] = dict(parent=cycle[0], candidate=cycle[1], delta=cycle[1] - cycle[0])
            count += 1
        warm.append(dict(variant=variant, mode=mode, calls=602, parent_total=sum(parent_cycles), candidate_total=sum(child_cycles),
                         parent_peak=max(parent_cycles), candidate_peak=max(child_cycles), deltas=sorted(set(deltas)), actual_hot_calls=specifics))
    result = dict(passed=True, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate), identities=37,
                  cold_calls=sum(row['cases'] for row in rows), warm_TMNT_calls=8 * 602, total_calls=count,
                  exact_full_AXYP_SP_source_ordinary_RAM_SMC_final_banks_ordered_APU=True,
                  all_hardware_registers5205_5206_separately_exact=True,
                  every_identity_math_operand_and_stream_exact=True, actual_MMC5_product_model=True,
                  numeric_modes=[0, 1], rows=rows, warm=warm, source_only=True, native_run=False,
                  checker_sha256=sha(Path(__file__)), limits='Seeded cold contexts and consecutive complete CPU AudioUpdates. No physical DMC DMA/IRQ/PPU clock or native draw/cadence closure.')
    (a.output / 'proof.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['passed', 'identities', 'cold_calls', 'warm_TMNT_calls', 'total_calls']}))


if __name__ == '__main__':
    main()

"""Full outer audio differential for every unchanged playable identity."""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load
from check_tmnt_audio_fallback_oc import execute, result
from final_item_matrix import ROSTER
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_owners_cpu import FLAGS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    rows = []
    for identity, slot, character, variant, value, family in ROSTER:
        if character == 19: continue
        for entry in ['AudioUpdate', 'ExpandedAudioUpdate']:
            if entry == 'ExpandedAudioUpdate' and character < 6: continue
            count, costs = 0, set()
            for mode, flags, phase in itertools.product([0, 1], FLAGS, range(6)):
                seed = dict(SelectedCharacter=character, OperMode=1, CrossoverBehaviorVersion=mode,
                            AreaMusicQueue=[1, 0, 4, 128, 0, 64][phase],
                            EventMusicQueue=[0, 4, 0, 0, 64, 8][phase],
                            GamePauseStatus=int(phase == 4), CurrentBank=215,
                            CurrentBankC=166, XgAudioCharacter=255)
                if variant: seed[variant] = value
                c, m = execute(old, entry, seed, flags=flags)
                d, n = execute(new, entry, seed, flags=flags)
                assert result(c, m) == result(d, n), ('Full non-TMNT outer divergence', identity, entry, mode, hex(flags), phase,
                       [(hex(i), m[i], n[i]) for i in range(0x8000) if m[i] != n[i] and not 0x1a0 <= i < 0x200][:12],
                       (c.a, c.x, c.y, c.p, c.sp), (d.a, d.x, d.y, d.p, d.sp))
                costs.add(d.processorCycles - c.processorCycles)
                count += 1
            row = dict(identity=identity, entry=entry, cases=count, added_CPU_cycles=sorted(costs))
            rows.append(row)
            print(row, flush=True)
    proof = dict(passed=True, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 identities=len({r['identity'] for r in rows}), cases=sum(r['cases'] for r in rows),
                 numeric_behavior_modes=[0, 1], caller_flags=FLAGS, rows=rows,
                 exact_full_AXYP_SP_RAM_SMC_final_banks_ordered_APU=True,
                 ignored_RAM_only_discarded_stack_01A0_01FF=True, native_run=False,
                 production_changes=False, checker_sha256=sha(Path(__file__)),
                 limits='Seeded legal cold area/event/pause CPU contexts. Cost increases are explicit; no native cadence, real interrupt or waveform claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: proof[k] for k in ['passed', 'identities', 'cases']}))


if __name__ == '__main__':
    main()

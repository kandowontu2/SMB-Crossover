"""Exact current-parent cold-owner and consecutive warm outer CPU costs.

These are isolated CPU measurements, never native completed-frame cadence.
"""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load, Memory, address
from check_tmnt_audio_fallback_oc import execute, result
from verify_native_relocation import NesMPU
from final_item_matrix import ROSTER
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_owners_cpu import FLAGS


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--updates', type=int, default=120)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert 1 <= a.updates <= 600
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    owner_rows, count = [], 0
    for owner, status, char in itertools.product(range(4), [0, 16, 31], [0, 2, 5, 9, 19]):
        costs = set()
        for flags in FLAGS:
            seed = dict(SelectedCharacter=char, BassDmcActive=owner, Cv3DmcPriority=int(owner == 3),
                        GuestCombinedEnable=31, TnDmcDrain=0, TnAudioDacHold=0)
            common = {k: v for k, v in seed.items() if k not in ['TnDmcDrain', 'TnAudioDacHold']}
            common[address(new, 'TnDmcDrain')] = 0
            common[address(new, 'TnAudioDacHold')] = 0
            common.update({0x4015: status, 0x4011: 7, 0x5117: 253 if owner == 3 else 255})
            c, m = execute(old, 'GuestDmcStatus', common, a=31, flags=flags)
            d, n = execute(new, 'GuestDmcStatus', common, a=31, flags=flags)
            assert result(c, m) == result(d, n)
            costs.add(d.processorCycles - c.processorCycles)
            count += 1
        owner_rows.append(dict(entry='GuestDmcStatus', old_owner=owner, hardware4015=status,
                               character=char, cases=len(FLAGS), added_cycles=sorted(costs)))
    admission_rows = []
    for old_owner, new_owner in itertools.product(range(4), range(4)):
        costs = set()
        for flags in FLAGS:
            seed = dict(BassDmcActive=old_owner, Cv3DmcPriority=int(old_owner == 3),
                        GuestCombinedEnable=31, CurrentBankC=166)
            seed[address(new, 'TnDmcDrain')] = 0
            c, m = execute(old, 'Cv3DmcOwnerWrite', seed, a=new_owner, flags=flags)
            d, n = execute(new, 'Cv3DmcOwnerWrite', seed, a=new_owner, flags=flags)
            assert result(c, m) == result(d, n)
            costs.add(d.processorCycles - c.processorCycles)
            count += 1
        admission_rows.append(dict(entry='Cv3DmcOwnerWrite', old_owner=old_owner, new_owner=new_owner,
                                   cases=len(FLAGS), added_cycles=sorted(costs)))

    def make(b, character, variant, value, mode):
        m = Memory(b)
        m.page(2, 38)
        seed = dict(SelectedCharacter=character, OperMode=1, CrossoverBehaviorVersion=mode,
                    AreaMusicQueue=1, CurrentBank=215, CurrentBankC=166, XgAudioCharacter=255)
        if variant: seed[variant] = value
        for key, val in seed.items(): m[address(b, key)] = val
        c = NesMPU(memory=m)
        return c, m

    def call(b, c, m, flags):
        c.pc, c.a, c.x, c.y, c.p, c.sp = address(b, 'AudioUpdate'), 85, 3, 7, flags, 253
        m[510], m[511] = 255, 126
        m.writes = []
        start = c.processorCycles
        for _ in range(50000):
            if c.pc == 0x7f00: break
            c.step()
        else: raise AssertionError(('Warm outer timeout', hex(c.pc), m.banks))
        return c.processorCycles - start

    warm_rows, warm_count = [], 0
    for identity, slot, character, variant, value, family in ROSTER:
        if character == 19: continue
        for mode in [0, 1]:
            c, m = make(old, character, variant, value, mode)
            d, n = make(new, character, variant, value, mode)
            cold_delta = call(new, d, n, 0x20) - call(old, c, m, 0x20)
            assert result(c, m) == result(d, n), ('Cold warm-fixture divergence', identity, mode)
            costs, owners, cycles = {}, set(), [0, 0]
            for update in range(a.updates):
                owner = m[address(old, 'BassDmcActive')]
                assert owner == n[address(new, 'BassDmcActive')]
                owners.add(owner)
                x = call(old, c, m, FLAGS[update % len(FLAGS)])
                y = call(new, d, n, FLAGS[update % len(FLAGS)])
                assert result(c, m) == result(d, n), ('Consecutive warm divergence', identity, mode, update)
                costs.setdefault(owner, set()).add(y - x)
                cycles[0] += x
                cycles[1] += y
                warm_count += 1
            row = dict(identity=identity, character=character, mode=mode, cold_first_call_added_cycles=cold_delta,
                       consecutive_updates=a.updates, actual_observed_software_owners=sorted(owners),
                       warm_added_cycles_by_owner={str(k): sorted(v) for k, v in costs.items()},
                       parent_cycles=cycles[0], candidate_cycles=cycles[1])
            warm_rows.append(row)
            print(row, flush=True)
    proof = dict(passed=True, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 cold_owner_component_cases=count, owner_status_rows=owner_rows,
                 owner_admission_rows=admission_rows, consecutive_warm_cases=warm_count,
                 unchanged_identities=len({r['identity'] for r in warm_rows}), numeric_behavior_modes=[0, 1],
                 whole_AXYP_SP_RAM_SMC_banks_ordered_APU_exact=True, rows=warm_rows,
                 source_only=True, native_run=False, production_changes=False,
                 checker_sha256=sha(Path(__file__)),
                 limits='Consecutive isolated CPU music updates and arranged owner/status controls. Hardware4015 does not run a DMA clock; software owner readback is not physical completion. No live-game update/draw or OAM/vblank/cadence claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: proof[k] for k in ['passed', 'cold_owner_component_cases', 'consecutive_warm_cases', 'unchanged_identities']}))


if __name__ == '__main__':
    main()

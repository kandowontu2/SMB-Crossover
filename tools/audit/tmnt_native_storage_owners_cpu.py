"""Current-linked DMC owner4 coexistence, completion and delayed-tail controls.

CPU-only arranged audio component states. Hardware4015/DAC readbacks are
explicit test inputs, not real sample-clock or natural gameplay evidence.
"""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load, address
from check_tmnt_audio_fallback_oc import execute, result
from tmnt_native_storage_driver import ROOT, sha

FLAGS = [0x20, 0x21, 0x22, 0x60, 0x61, 0x62, 0xe0, 0xe1, 0xee, 0xff]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    counts = {}
    read = lambda b, m, name: m[address(b, name)]
    hw = lambda m: [(at, v) for at, v in m.writes if 0x4000 <= at <= 0x4017]
    count = 0
    for char, owner, status, acc, flags in itertools.product([0, 2, 5, 9, 19], range(4), [0, 16, 31], [0, 15, 16, 31, 255], FLAGS):
        priorities = [0, 1, 5] if owner == 3 else [0]
        for priority in priorities:
            seed = dict(SelectedCharacter=char, BassDmcActive=owner, Cv3DmcPriority=priority,
                        TnAudioDacHold=37, TnDmcDrain=0)
            common = {k: v for k, v in seed.items() if k not in ['TnAudioDacHold', 'TnDmcDrain']}
            # Bind the new aliases to the identical previously unused bytes.
            common[address(new, 'TnAudioDacHold')] = 37
            common[address(new, 'TnDmcDrain')] = 0
            common.update({0x4015: status, 0x4011: 7, 0x5117: 253 if priority else 255})
            c, m = execute(old, 'GuestDmcStatus', common, a=acc, flags=flags)
            d, n = execute(new, 'GuestDmcStatus', common, a=acc, flags=flags)
            assert result(c, m) == result(d, n), ('Existing owner completion differs', char, owner, status, acc, flags, priority)
            count += 1
    counts['existing_owner0_1_2_3_GuestDmcStatus_exact_all_RAM_APU_banks_ABI'] = count
    count = 0
    for status, acc, flags in itertools.product([0, 16, 31], [0, 15, 16, 31, 255], FLAGS):
        c, m = execute(new, 'GuestDmcStatus', dict(SelectedCharacter=19, BassDmcActive=4,
                       Cv3DmcPriority=0, TnAudioDacHold=37, TnDmcDrain=0) | {0x4015: status, 0x4011: 7}, a=acc, flags=flags)
        assert (c.a, c.x, c.y, c.p & 207, c.sp) == ((acc | 16) if status & 16 else (acc & 15), 3, 7,
                (flags & 0x4d) | (0x80 if (((acc | 16) if status & 16 else acc & 15) & 128) else 0) | (2 if not ((acc | 16) if status & 16 else acc & 15) else 0), 255)
        assert read(new, m, 'BassDmcActive') == (4 if status & 16 else 0)
        assert read(new, m, 'TnAudioDacHold') == (37 if status & 16 else 44)
        assert read(new, m, 'TnDmcDrain') == 0 and m[0x4011] == 7 and not hw(m)
        count += 1
    counts['native_completion_software_hold44_without_clearing_DAC'] = count
    count = 0
    for marker, char, mode, owner, flags in itertools.product([253, 255], [0, 2, 5, 9, 19], [0, 1], range(5), FLAGS):
        seed = dict(SelectedCharacter=char, OperMode=mode, XgAudioCharacter=marker,
                    BassDmcActive=owner, Cv3DmcPriority=0, GuestCombinedEnable=31,
                    TnDmcDrain=0, TnAudioDacHold=44) | {0x4015: 31, 0x4011: 44}
        c, m = execute(new, 'TnAudioGlobalGate', seed, a=85, flags=flags)
        assert (c.a, c.x, c.y, c.p & 207, c.sp) == (mode, 3, 7, (flags & 0x4d) | (2 if mode == 0 else 0), 255)
        exits = marker == 253 and (char != 19 or mode == 0)
        if exits and owner in [0, 4]:
            assert read(new, m, 'BassDmcActive') == 0 and read(new, m, 'TnAudioDacHold') == 0
            assert read(new, m, 'TnDmcDrain') == 1 and m[0x4011] == 0 and m[0x4015] == 15
        else:
            assert read(new, m, 'BassDmcActive') == owner and read(new, m, 'TnAudioDacHold') == 44
            assert read(new, m, 'TnDmcDrain') == 0 and m[0x4011] == 44 and not hw(m)
        assert read(new, m, 'XgAudioCharacter') == (255 if exits else marker)
        count += 1
    counts['global_exit_preserves_newer_foreign_owners_and_entry_ABI'] = count
    count = 0
    for owner, flags in itertools.product(range(5), FLAGS):
        c, m = execute(new, 'TnAudioGlobalGate', dict(SelectedCharacter=19, OperMode=1,
                       XgAudioCharacter=255, BassDmcActive=owner, TnDmcDrain=1, TnAudioDacHold=99) | {0x4011: 44}, flags=flags)
        assert read(new, m, 'TnDmcDrain') == 0 and read(new, m, 'BassDmcActive') == owner
        assert m[0x4011] == (0 if owner == 0 else 44) and read(new, m, 'TnAudioDacHold') == 99
        count += 1
    counts['delayed_tail_clear_preserves_newer_live_owners'] = count
    count = 0
    for previous, incoming, flags in itertools.product(range(5), range(5), FLAGS):
        seed = dict(BassDmcActive=previous, Cv3DmcPriority=0, TnDmcDrain=1,
                    TnAudioDacHold=44, GuestCombinedEnable=31) | {0x4015: 31, 0x4011: 71}
        c, m = execute(new, 'Cv3DmcOwnerWrite', seed, a=incoming, flags=flags)
        assert (c.a, c.x, c.y, c.p & 207, c.sp) == (incoming, 3, 7, flags & 207, 255)
        assert read(new, m, 'BassDmcActive') == incoming and m[0x4011] == 71
        if previous == 4 and incoming != 4:
            assert m[0x4015] == 15 and read(new, m, 'TnAudioDacHold') == 0
            assert read(new, m, 'TnDmcDrain') == int(incoming == 0)
        else:
            assert not hw(m) and read(new, m, 'TnAudioDacHold') == 44
            assert read(new, m, 'TnDmcDrain') == (0 if incoming == 4 else 1)
        count += 1
    counts['actual_Cv3_owner_store_TMNT_preemption_claim_stop_flags'] = count
    count = 0
    for request, flags in itertools.product([0x72, 0x74, 0x75, 0x76], FLAGS):
        common = dict(SelectedCharacter=5, Cv3DmcEntryA=request, Cv3DmcPriority=0,
                      Cv3DmcPending=request, GuestCombinedEnable=31) | {0x4015: 16, 0x4011: 44}
        c, m = execute(old, 'Cv3DmcStart', common | dict(BassDmcActive=0), flags=flags, cbank=125)
        d, n = execute(new, 'Cv3DmcStart', common | dict(BassDmcActive=4, TnAudioDacHold=44, TnDmcDrain=1), flags=flags, cbank=125)
        assert (c.a, c.x, c.y, c.p & 207, c.sp) == (d.a, d.x, d.y, d.p & 207, d.sp)
        assert read(new, n, 'BassDmcActive') == 3 and read(new, n, 'Cv3DmcPriority') == read(old, m, 'Cv3DmcPriority')
        assert n.banks == m.banks and n.banks[3] == 125
        assert [n[at] for at in [0x4010, 0x4011, 0x4012, 0x4013, 0x4015]] == [m[at] for at in [0x4010, 0x4011, 0x4012, 0x4013, 0x4015]]
        assert read(new, n, 'TnAudioDacHold') == read(new, n, 'TnDmcDrain') == 0
        assert hw(n) == hw(m)[:-1] + [(0x4015, 15)] + hw(m)[-1:]
        count += 1
    counts['actual_CV3_start_preempts_TMNT_retains_source_sample_priority_mirror'] = count
    count = 0
    for request, flags in itertools.product([0, 0x71, 0x73, 0x77, 255], FLAGS):
        common = dict(SelectedCharacter=5, Cv3DmcEntryA=request, Cv3DmcPriority=0,
                      Cv3DmcPending=request, GuestCombinedEnable=31, BassDmcActive=4) | {0x4015: 16, 0x4011: 44,
                      address(new, 'TnAudioDacHold'): 44, address(new, 'TnDmcDrain'): 1}
        c, m = execute(old, 'Cv3DmcStart', common, flags=flags, cbank=125)
        d, n = execute(new, 'Cv3DmcStart', common, flags=flags, cbank=125)
        assert result(c, m) == result(d, n) and not hw(n), ('Invalid/silent source request changed owner', request, flags)
        assert read(new, n, 'BassDmcActive') == 4 and read(new, n, 'TnAudioDacHold') == 44
        count += 1
    counts['CV3_silent73_and_invalid_request_controls_preserve_TMNT_owner'] = count
    proof = dict(passed=True, baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 cases=counts, total_cases=sum(counts.values()), source_only=True, native_run=False,
                 production_changes=False, checker_sha256=sha(Path(__file__)),
                 scope=__doc__, limits='Explicitly arranged CPU owner/status states and actual compiled routines; no claim of real DAC tail evolution, DMA completion, physical IRQ timing or gameplay reachability.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()

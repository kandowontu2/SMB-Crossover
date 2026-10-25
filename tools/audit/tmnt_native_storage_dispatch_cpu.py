"""Prove actual downstream entry flag liveness and full TMNT dispatch outcomes.

No incoming-A correlation shortcut: prefixes compare all256 A values and all64
meaningful P combinations on the Mario/expanded, Mac, and native paths. Legal
identity-specific outcomes are independently checked by full outer calls.
"""
from pathlib import Path
import argparse
import itertools
import json
from check_tmnt_render_oa import load, Memory, address
from check_tmnt_audio_fallback_oc import execute, result
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT, sha
from tmnt_native_storage_owners_cpu import FLAGS
from tmnt_native_storage_irq_cpu import ordinary, registers


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    # Physical original instructions prove overwritten A/C/N/Z before any use;
    # all other meaningful P bits V/D/I are unchanged by both LDA and CMP.
    for b in [old, new]:
        lm = address(b, 'LmNativeMusicGate')
        raw = b['raw'][16 + 126 * 8192 + lm - 0x8000:16 + 126 * 8192 + lm - 0x8000 + 5]
        assert raw == bytes([0xad]) + address(b, 'SelectedCharacter').to_bytes(2, 'little') + bytes([0xc9, 15])
        tm = address(b, 'TnAudioUpdate')
        raw = b['raw'][16 + 125 * 8192 + tm - 0xc000:16 + 125 * 8192 + tm - 0xc000 + 10]
        assert raw == bytes([0xa9, 0, 0x8d]) + address(b, 'TnAudioRequest').to_bytes(2, 'little') + bytes([0xad]) + address(b, 'XgAudioCharacter').to_bytes(2, 'little') + bytes([0xc9, 253])
    flag_states = [value for value in range(256) if value & 0x30 == 0x20]
    assert len(flag_states) == 64
    prefix_count = 0
    rows = []
    for char in [0, 15, 19]:
        machines = []
        for b in [old, new]:
            m = Memory(b)
            m[address(b, 'SelectedCharacter')] = char
            m[address(b, 'XgAudioCharacter')] = 253
            c = NesMPU(memory=m)
            stop = address(b, 'TnAudioUpdate') + 10 if char == 19 else address(b, 'LmNativeMusicGate') + 5
            stop_bank = 125 if char == 19 else 126
            machines.append((b, c, m, stop, stop_bank))
        costs = set()
        for acc, flags in itertools.product(range(256), flag_states):
            results, cycles = [], []
            for b, c, m, stop, stop_bank in machines:
                m.page(1, 63)
                m.page(2, 38)
                m[address(b, 'CurrentBank')] = 191
                m[address(b, 'CurrentBankC')] = 166
                c.pc, c.a, c.x, c.y, c.p, c.sp = address(b, 'TnAudioDispatch'), acc, 3, 7, flags, 253
                m[510], m[511] = 255, 126
                m.writes = []
                start = c.processorCycles
                for _ in range(40):
                    bank = m.banks[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else -1
                    if c.pc == stop and bank == stop_bank:
                        break
                    c.step()
                else:
                    raise AssertionError(('Dispatcher liveness prefix failed to reach real first CMP', char, acc, flags, hex(c.pc), m.banks))
                results.append((registers(c), list(m.banks), [(at, value) for at, value in m.writes if not 0x1d0 <= at <= 0x1ff]))
                cycles.append(c.processorCycles - start)
            assert results[0] == results[1], ('First live destination input differs', char, acc, flags, results)
            assert cycles[1] - cycles[0] == -14
            costs.add(cycles[1] - cycles[0])
            prefix_count += 1
        rows.append(dict(character=char, cases=256 * 64, added_cycles=sorted(costs)))
        print('prefix', char, prefix_count, flush=True)
    native_count, native_costs = 0, set()
    for variant, mode, flags, phase, acc in itertools.product(range(4), [0, 1], FLAGS, range(6), [0, 85, 255]):
        seed = dict(SelectedCharacter=19, TnVariant=variant, OperMode=1, CrossoverBehaviorVersion=mode,
                    AreaMusicQueue=[1, 0, 4, 128, 0, 64][phase], EventMusicQueue=[0, 4, 0, 0, 64, 8][phase],
                    GamePauseStatus=int(phase == 4), CurrentBank=215, CurrentBankC=166, XgAudioCharacter=255)
        for entry in ['AudioUpdate', 'ExpandedAudioUpdate']:
            c, m = execute(old, entry, seed, a=acc, flags=flags)
            d, n = execute(new, entry, seed, a=acc, flags=flags)
            assert result(c, m) == result(d, n), ('Native full outer changed', variant, mode, hex(flags), phase, acc, entry)
            delta = d.processorCycles - c.processorCycles
            # AudioUpdate paused/silenced paths may leave before dispatch.
            assert delta in [0, -14], (entry, phase, delta)
            native_costs.add(delta)
            native_count += 1
    print('native full outer', native_count, native_costs, flush=True)

    # Execute the real IRQ/RTI at every reachable dispatcher and initial live
    # downstream instruction boundary, then require the same full final result.
    irq_count, depths = 0, []
    for char in [6, 15, 19]:
        def setup():
            b = new
            m = Memory(b)
            m.page(1, 63)
            m.page(2, 38)
            seed = dict(SelectedCharacter=char, OperMode=1, XgAudioCharacter=255,
                        CurrentBank=191, CurrentBankC=166, AreaMusicQueue=1, TnDmcDrain=0)
            for key, value in seed.items(): m[address(b, key)] = value
            m[0x5204] = 128
            c = NesMPU(memory=m)
            c.pc, c.a, c.x, c.y, c.p, c.sp = address(b, 'TnAudioDispatch'), 85, 3, 7, 0x20, 253
            m[510], m[511] = 255, 126
            m.writes = []
            return c, m
        c, m = setup()
        target_indices = []
        for index in range(50000):
            if c.pc == 0x7f00: break
            bank = m.banks[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else -1
            if ((bank == 127 and address(new, 'TnAudioDispatch') <= c.pc < address(new, 'TnMusicInitCall')) or
                (bank == 126 and address(new, 'LmNativeMusicGate') <= c.pc < address(new, 'LmNativeMusicGate') + 5) or
                (bank == 125 and address(new, 'TnAudioUpdate') <= c.pc < address(new, 'TnAudioUpdate') + 10)):
                target_indices.append(index)
            c.step()
        else: raise AssertionError(('IRQ baseline timeout', char, hex(c.pc)))
        expected = registers(c), ordinary(m), list(m.banks), [(at, v) for at, v in m.writes if 0x4000 <= at <= 0x4017]
        for target in target_indices:
            d, n = setup()
            injected = False
            for index in range(50000):
                if d.pc == 0x7f00: break
                if index == target:
                    before = registers(d), ordinary(n), list(n.banks)
                    assert not d.p & 4
                    d.irq()
                    assert d.pc == 0x8000
                    minimum = d.sp
                    for _ in range(300):
                        if d.pc == before[0][0] and d.sp == before[0][-1]: break
                        minimum = min(minimum, d.sp)
                        d.step()
                    else: raise AssertionError(('IRQ dispatcher return timeout', char, target))
                    assert (registers(d), ordinary(n), list(n.banks)) == before
                    depths.append(255 - minimum)
                    injected = True
                d.step()
            else: raise AssertionError(('IRQ dispatcher final timeout', char, target))
            actual = registers(d), ordinary(n), list(n.banks), [(at, v) for at, v in n.writes if 0x4000 <= at <= 0x4017]
            assert injected and actual == expected
            irq_count += 1
    proof = dict(passed=True, donor_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 all_A_all_meaningful_P_prefix_cases=prefix_count, prefix_rows=rows,
                 physical_real_destination_A_C_N_Z_overwrite_proof=True, all_V_D_I_exact=True,
                 first_live_destination_registers_bank_writes_exact=True,
                 full_Turtles_outer_calls=native_count, full_Turtles_outer_added_cycles=sorted(native_costs),
                 real_dispatcher_IRQ_vector_handler_RTI_injections=irq_count, maximum_total_dispatch_IRQ_stack_depth=max(depths),
                 source_only=True, native_run=False, production_changes=False, checker_sha256=sha(Path(__file__)),
                 limits='CPU prefix/full outer and actual compiled IRQ/RTI only. Full non-TMNT outer suite is a separate proof. No physical IRQ timing, DMA/vblank/OAM/NMI or live cadence claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()

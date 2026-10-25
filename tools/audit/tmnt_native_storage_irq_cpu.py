"""Real compiled IRQ body injected at new TMNT helper instruction boundaries.

The CPU executes the actual vector/handler/RTI. No Mesen or PPU/scanline/DMA
clock is modeled. Nested NMI is not claimed: audio normally executes in NMI.
"""
from pathlib import Path
import argparse
import json
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU
from tmnt_native_storage_driver import ROOT, sha


def ordinary(m):
    return bytes(m[:0x1d0] + m[0x200:0x2000] + m[0x5c00:0x8000])


def registers(c):
    return c.pc, c.a, c.x, c.y, c.p & 207, c.sp


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    b = load(a.candidate)
    cases = [
        ('TnAudioGlobalGate', dict(SelectedCharacter=0), 85, False),
        ('TnAudioGlobalGate', dict(SelectedCharacter=19, TnDmcDrain=1, BassDmcActive=1), 85, False),
        ('GuestDmcStatus', {0x4015: 0}, 31, False),
        ('Cv3DmcOwnerWrite', {}, 0, False),
        ('Cv3DmcOwnerWrite', {}, 1, False),
        ('Cv3DmcOwnerWrite', {}, 4, False),
        ('Cv3DmcStart', dict(SelectedCharacter=5, Cv3DmcEntryA=0x72), 85, False),
        ('Cv3DmcStart', dict(SelectedCharacter=5, Cv3DmcEntryA=0x75), 85, False),
        ('TnMusicInitCall', dict(BassDmcActive=0), 85, False),
        ('TnMusicPlayCall', dict(BassDmcActive=0), 85, True),
    ]

    def setup(name, seed, acc, prime):
        m = Memory(b)
        m.page(1, 63)
        m.page(2, 125)
        base = dict(SelectedCharacter=19, OperMode=1, XgAudioCharacter=253,
                    BassDmcActive=4, Cv3DmcPriority=0, TnDmcDrain=0,
                    TnAudioDacHold=44, TnAudioSong=2, GuestCombinedEnable=31,
                    CurrentBank=191, CurrentBankC=253)
        base.update(seed)
        for key, value in base.items():
            m[key if isinstance(key, int) else address(b, key)] = value
        m[0x4011], m[0x5204] = 44, 128
        c = NesMPU(memory=m)
        if prime:
            c.pc, c.a, c.x, c.y, c.p, c.sp = address(b, 'TnMusicInitCall'), 85, 3, 7, 0x20, 253
            m[510], m[511] = 255, 126
            for _ in range(20000):
                if c.pc == 0x7f00: break
                c.step()
            else: raise AssertionError('IRQ fixture prime timeout')
        c.pc, c.a, c.x, c.y, c.p, c.sp = address(b, name), acc, 3, 7, 0x20, 253
        m[510], m[511] = 255, 126
        m.writes = []
        return c, m

    rows, total, depths, irq_stores = [], 0, [], set()
    for name, seed, acc, prime in cases:
        c, m = setup(name, seed, acc, prime)
        trace, seen = [], set()
        for index in range(30000):
            if c.pc == 0x7f00: break
            bank = m.banks[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else -1
            target = (bank in [125, 127] and 0xe941 <= c.pc < 0xeb3a) or (bank == 63 and 0xa02c <= c.pc < 0xa200)
            key = bank, c.pc
            if target and key not in seen:
                trace.append(index)
                seen.add(key)
            c.step()
        else: raise AssertionError(('IRQ fixture reference timeout', name, hex(c.pc)))
        expected = registers(c), ordinary(m), list(m.banks), [(at, value) for at, value in m.writes if 0x4000 <= at <= 0x4017]
        for target in trace:
            d, n = setup(name, seed, acc, prime)
            injected = False
            for index in range(30000):
                if d.pc == 0x7f00: break
                if index == target:
                    before = registers(d), ordinary(n), list(n.banks)
                    assert not d.p & 4
                    start = len(n.writes)
                    d.irq()
                    assert d.pc == 0x8000 and d.sp == (before[0][-1] - 3) & 255
                    depth = d.sp
                    for _ in range(300):
                        if d.pc == before[0][0] and d.sp == before[0][-1]: break
                        depth = min(depth, d.sp)
                        d.step()
                    else: raise AssertionError(('Actual IRQ failed to return', name, target, hex(d.pc)))
                    assert (registers(d), ordinary(n), list(n.banks)) == before, ('IRQ damaged interrupted state', name, target)
                    hardware = [(at, value) for at, value in n.writes[start:] if 0x2000 <= at < 0x6000]
                    assert hardware and all(at in [0x2005, 0x2006, 0x5128, 0x5130] for at, value in hardware)
                    irq_stores |= {at for at, value in hardware}
                    depths.append(255 - depth)
                    injected = True
                d.step()
            else: raise AssertionError(('Interrupted helper timeout', name, target, hex(d.pc)))
            assert injected
            actual = registers(d), ordinary(n), list(n.banks), [(at, value) for at, value in n.writes if 0x4000 <= at <= 0x4017]
            assert actual == expected, ('Final helper output changed after IRQ', name, target)
            total += 1
        rows.append(dict(entry=name, instruction_boundaries=len(trace), prime_actual_source_init=prime,
                         input_A=acc, seed=seed))
        print(name, len(trace), flush=True)
    proof = dict(passed=True, candidate_ROM_sha256=sha(a.candidate), real_compiled_IRQ_injections=total,
                 actual_vector_PC=0x8000, instruction_boundary_cases=rows,
                 interrupted_AXYP_SP_PC_SMC_RAM_PRG_banks_exact=True,
                 final_helper_source_APU_and_owned_state_exact=True,
                 IRQ_only_hardware_store_addresses=sorted(irq_stores), maximum_total_stack_depth=max(depths),
                 no_nested_NMI_claim=True, native_run=False, production_changes=False,
                 checker_sha256=sha(Path(__file__)), scope=__doc__,
                 limits='CPU actual vector/IRQ/RTI behavior with explicit pending-bit input. No physical MMC5 IRQ timing, PPU/OAM capture, real DMC DMA stalls or nested-NMI domain claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps({k: proof[k] for k in ['passed', 'real_compiled_IRQ_injections', 'maximum_total_stack_depth']}))


if __name__ == '__main__':
    main()

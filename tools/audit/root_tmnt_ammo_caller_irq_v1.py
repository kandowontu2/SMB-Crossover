"""Actual turtle draw callers and compiled IRQ boundaries for ammo lookup."""
from pathlib import Path
import argparse
import itertools
import json

from check_tmnt_render_oa import load, address
from check_tmnt_audio_fallback_oc import qualified
from tmnt_equipment_empty_scans_cpu_v1 import setup, execute, outcome, qualified_cache
from tmnt_equipment_empty_scans_irq_v1 import result
from tmnt_native_storage_irq_cpu import ordinary, registers
from tmnt_native_storage_driver import ROOT, sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ['baseline', 'candidate', 'output']:
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.candidate)
    for b, path in [(old, a.baseline), (new, a.candidate)]:
        qualified_cache[id(b)] = qualified(path)
    flags = [0x20 | (n & 15) | ((n & 16) << 2) | ((n & 32) << 2) for n in range(64)]
    rows = []
    for entry, ammo, variant, queue, flag in itertools.product(['TnDraw', 'TnDrawDispatch'],
             [0, 99, 199], range(4), [0, 77, 78], flags):
        cfg = dict(entry=entry, ammo=ammo, variant=variant, queue=queue, flags=flag,
                   hud_ammo=ammo ^ 255, shots=[(0, 73, 2), (1, 74, 2), (2, 75, 2)])
        c, m, _, _ = execute(old, cfg)
        d, n, _, _ = execute(new, cfg)
        assert outcome(c, m) == outcome(d, n), (entry, ammo, variant, queue, flag)
        rows.append(dict(cfg=cfg, delta=d.processorCycles - c.processorCycles))
    helper = address(new, 'TnAmmoDecimalLookup')
    irq_rows = []
    hardware = set()
    for ammo in [0, 99, 100, 255]:
        cfg = dict(ammo=ammo, hud_ammo=ammo ^ 255, flags=0x20)
        c, m = setup(new, cfg)
        m[0x5204] = 128
        m.writes = []
        trace = []
        for index in range(30000):
            if c.pc == 0x7f00:
                break
            if m.banks[1] == 87 and helper <= c.pc < helper + 0x100:
                trace.append((index, c.pc))
            c.step()
        else:
            raise AssertionError('Reference draw timeout')
        assert trace
        expected = result(c, m)
        for at, pc in trace:
            d, n = setup(new, cfg)
            n[0x5204] = 128
            n.writes = []
            for index in range(30000):
                if d.pc == 0x7f00:
                    break
                if index == at:
                    state = registers(d), ordinary(n), tuple(n.banks)
                    assert not d.p & 4
                    first = len(n.writes)
                    d.irq()
                    assert d.pc == 0x8000
                    for _ in range(300):
                        if d.pc == state[0][0] and d.sp == state[0][-1]:
                            break
                        d.step()
                    else:
                        raise AssertionError(('IRQ return timeout', hex(pc)))
                    assert (registers(d), ordinary(n), tuple(n.banks)) == state
                    writes = [(k, v) for k, v in n.writes[first:] if 0x2000 <= k < 0x6000]
                    assert writes and all(k in [0x2005, 0x2006, 0x5128, 0x5130] for k, v in writes)
                    hardware.update(k for k, v in writes)
                    # Remove only the separately validated IRQ event log.
                    # No emulated RAM/register/bank value is restored.
                    del n.writes[first:]
                d.step()
            else:
                raise AssertionError('Interrupted draw timeout')
            assert result(d, n) == expected, (ammo, hex(pc))
            irq_rows.append(dict(ammo=ammo, pc=pc))
    proof = dict(passed=True, source_only=True, native_run=False, accepted=False,
                 baseline_ROM_sha256=sha(a.baseline), candidate_ROM_sha256=sha(a.candidate),
                 complete_actual_draw_caller_cases=len(rows), actual_compiled_IRQ_injections=len(irq_rows),
                 complete_final_AXYP_SP_RAM_SMC_banks_ordered_OAM_VRAM_hardware_exact=True,
                 IRQ_hardware_writes=sorted(hardware), IRQ_exceptions='Only discarded upper stack and explicit actual IRQ hardware cells',
                 checker_sha256=sha(Path(__file__)),
                 limits='CPU-only complete actual draw callers and real vector/IRQ/RTI at every reached lookup instruction. No PPU/NMI/DMC DMA clocks, native cadence or deployment claim.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    (a.output / 'cases.json').write_text(json.dumps(dict(callers=rows, irq=irq_rows), separators=(',', ':')) + '\n')
    print(json.dumps(proof), flush=True)


if __name__ == '__main__':
    main()

"""Execute the actual old and shallow linked inventory queries, without stubs."""
from pathlib import Path
import argparse
import csv
import hashlib
import itertools
import json
from check_tmnt_render_oa import load, Memory, address
from verify_native_relocation import NesMPU


def run(bundle, spec, allow_irq=False):
    char, mode, roll, cv3, z2, flags, regs = spec
    m = Memory(bundle); m.page(1, 59)
    for name, value in dict(CurrentBank=187, SelectedCharacter=char,
            CrossoverBehaviorVersion=mode, RlVariant=roll, Cv3Variant=cv3, Z2Variant=z2).items():
        m[address(bundle, name)] = value
    m[0x1fe] = 0xef; m[0x1ff] = 0xff; m.writes = []
    c = NesMPU(memory=m, pc=address(bundle, 'InventoryLegacyClassic')); c.sp = 0xfd
    c.a, c.x, c.y = regs; c.p = flags
    minimum = 0xfd
    for _ in range(3000):
        if c.pc == 0xfff0:
            break
        c.step(); minimum = min(minimum, c.sp)
    else:
        raise AssertionError(('CPU timeout', spec, hex(c.pc)))
    allowed = set(range(0x100, 0x200)) | set(range(0x5114, 0x5118))
    for name in ['CurrentBank', 'CurrentBankC', 'safecall_a']:
        allowed.add(address(bundle, name))
    hardware = []
    if allow_irq:
        allowed |= {0x2005, 0x2006, 0x5128, 0x5204, address(bundle, 'IrqNewScroll')}
        assert m[address(bundle, 'IrqNewScroll')] == 0
        hardware = [(at, v) for at, v in m.writes if at in [0x2005, 0x2006, 0x5128, 0x5204]]
    app = {at: m[at] for at, value in m.writes if at not in allowed}
    assert not app, (spec, app)
    assert m.banks == [126, 59, 88, 127] and m[address(bundle, 'CurrentBank')] == 187
    return (c.a, c.x, c.y, c.p, c.sp), c.processorCycles, minimum, hardware


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True); p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    cases = set()
    for char, mode, flags, regs in itertools.product(range(256), [0, 1, 2, 255], [0x30, 0x71], [(0, 0, 0), (0xab, 0xfe, 0x81)]):
        cases.add((char, mode, 0, 0, 0, flags, regs))
    for char, mode, variant, flags in itertools.product([9, 5, 4], [0, 1, 2, 255], range(256), [0x30, 0x71]):
        variants = [0, 0, 0]; variants[{9: 0, 5: 1, 4: 2}[char]] = variant
        cases.add((char, mode, *variants, flags, (0x56, 7, 0xa3)))
    for char, mode, roll, cv3, z2, flags in itertools.product(range(20), [0, 1], [0, 1, 3, 4, 255], [0, 1, 3, 4, 255], [0, 1, 3, 4, 255], [0x30, 0x71]):
        cases.add((char, mode, roll, cv3, z2, flags, (0x56, 7, 0xa3)))
    minimum_saving = 10000; maximum_saving = 0; old_depth = 0; new_depth = 0
    with (a.output / 'cases.csv').open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['character', 'mode', 'Roll', 'CV3', 'Z2', 'flags', 'A', 'X', 'Y', 'old_cycles', 'new_cycles', 'old_stack_bytes', 'new_stack_bytes'])
        for spec in sorted(cases):
            x, y = run(old, spec), run(new, spec)
            assert x[0] == y[0], (spec, x, y)
            saving = x[1]-y[1]; assert saving > 0, (spec, saving)
            minimum_saving = min(minimum_saving, saving); maximum_saving = max(maximum_saving, saving)
            old_depth = max(old_depth, 0xfd-x[2]); new_depth = max(new_depth, 0xfd-y[2])
            w.writerow([*spec[:6], *spec[6], x[1], y[1], 0xfd-x[2], 0xfd-y[2]])
    q = dict(passed=True, ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
        baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), cases=len(cases),
        exact_registers='A/X/Y/full processor status/SP', application_RAM_writes=0,
        final_mapping='Exact A/C/low/fixed banks and logical CurrentBank',
        cycles_saved_per_query=[minimum_saving, maximum_saving],
        maximum_query_stack_bytes=dict(old=old_depth, new=new_depth),
        scope='Actual linked four-gate chain versus leaf, all256 IDs/modes0,1,2,255, all256 values of the three applicable selectors, legal IDs with cross-selector combinations, two flag/register seeds. No interrupt or native frame claim in this isolated CPU layer.')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2)+'\n'); print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()

"""Inject the linked IRQ at every boundary of every inventory predicate path."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import check_inventory_stack_og as component
import check_tmnt_primary_irq_od as irq
from check_tmnt_render_oa import load


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True); p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False); old, new = load(a.baseline), load(a.rom)
    component.NesMPU = irq.InterruptProbe
    paths = []; cases = 0
    profiles = [(0,0,0,0),(1,0,0,0),(2,0,0,0),(3,0,0,0),(4,0,0,0),(4,0,0,1),
        (4,0,0,2),(5,0,0,0),(5,0,1,0),(5,0,2,0),(5,0,3,0),(5,0,4,0),
        (6,0,0,0),(9,0,0,0),(9,1,0,0),(9,255,0,0),(11,0,0,0),
        (15,0,0,0),(19,0,0,0),(255,255,255,255)]
    for (char, roll, cv3, z2), mode, regs in itertools.product(profiles, [0,1,255], [(0x56,7,0xa3),(0,0xff,0)]):
        spec = (char, mode, roll, cv3, z2, 0x30, regs)
        irq.INJECT = 0; expected = component.run(old, spec, allow_irq=True)
        irq.INJECT = None; plain = component.run(new, spec)
        count = len(irq.LAST.path); assert plain[0] == expected[0]
        for instruction in range(count):
            irq.INJECT = instruction; actual = component.run(new, spec, allow_irq=True)
            assert irq.LAST.interrupted and actual[0] == expected[0] and actual[3] == expected[3], (spec, instruction)
            cases += 1
        paths.append(dict(profile=[char,roll,cv3,z2],mode=mode,registers=regs,instruction_boundaries=count))
    proof = dict(passed=True, ROM_sha256=hashlib.sha256(new['raw']).hexdigest(),
        baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(), cases=cases, paths=len(paths),
        scope='Actual linked MMC5 IRQ at every instruction of the query entry/farcall/leaf/return for each distinct gate/range path, three modes and two register seeds. Each IRQ restores PC/registers/meaningful flags/SP/live caller stack; complete query returns exact old A/X/Y/fullP/SP, final banks and ordered IRQ hardware stores. No timed audio-NMI claim in this CPU layer.')
    (a.output/'paths.json').write_text(json.dumps(paths,indent=2)+'\n')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n'); print(json.dumps(proof,indent=2))


if __name__ == '__main__':
    main()

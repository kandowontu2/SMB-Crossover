"""Interrupt every instruction of the two shallow render admission paths."""
from pathlib import Path
import argparse
import hashlib
import inspect
import itertools
import json
import check_render_dispatch_ov as component
import check_tmnt_primary_irq_od as irq
from check_tmnt_render_oa import load, address


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('rom', 'baseline', 'output'):
        p.add_argument('--' + name, type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    old['path'], new['path'] = a.baseline, a.rom
    maps = {path: component.qualified(path) for path in (a.baseline, a.rom)}
    source = inspect.getsource(component.run)
    anchor = '    application_writes = [(at, value) for at, value in m.writes if at not in ignored]'
    assert source.count(anchor) == 1
    source = source.replace(anchor, "    ignored |= {0x2005, 0x2006, 0x5128, 0x5204, address(bundle, 'IrqNewScroll')}\n" + anchor)
    anchor = 'mapper_writes=sum(at == 0x5115 for at, value in m.writes))'
    assert source.count(anchor) == 1
    source = source.replace(anchor, 'mapper_writes=sum(at == 0x5115 for at, value in m.writes),\n'
                            '                irq_stores=[(at, value) for at, value in m.writes if at in (0x2005, 0x2006, 0x5128, 0x5204)])')
    namespace = dict(component.__dict__, NesMPU=irq.InterruptProbe, qualified=lambda path: maps[path])
    exec(compile(source, '<actual IRQ render router>', 'exec'), namespace)
    run = namespace['run']
    cases = 0
    paths = []
    profiles = [(char, 0, char) for char in range(20)] + [(9, 1, 0x55), (9, 255, 255), (19, 0, 0), (255, 255, 255)]
    for entry, (char, variant, accumulator), flags in itertools.product(component.ENTRIES, profiles, (0x30, 0x71)):
        spec = (char, variant, accumulator, flags, 254, 129)
        irq.INJECT = 0
        expected = run(old, entry, spec)
        irq.INJECT = None
        plain = run(new, entry, spec)
        assert plain['admission'] == expected['admission'] and plain['result'] == expected['result']
        count = len(irq.LAST.path)
        for instruction in range(count):
            irq.INJECT = instruction
            actual = run(new, entry, spec)
            assert irq.LAST.interrupted
            assert actual['admission'] == expected['admission'] and actual['result'] == expected['result']
            assert actual['irq_stores'] == expected['irq_stores']
            cases += 1
        paths.append(dict(entry=entry, profile=spec, instruction_boundaries=count))
    q = dict(passed=True, accepted=False, cases=cases, paths=len(paths),
             ROM_sha256=hashlib.sha256(new['raw']).hexdigest(), baseline_ROM_sha256=hashlib.sha256(old['raw']).hexdigest(),
             component_sha256=hashlib.sha256(Path(component.__file__).read_bytes()).hexdigest(),
             driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             scope='Actual linked MMC5 IRQ at every executed instruction boundary of both actual public calls and shallow routing/return wrappers, with explicitly opaque existing render bodies. All20IDs plus Roll, turtle arbitraryA and unsupported fallback, two flag seeds. IRQ must restore PC/A/X/Y/meaningfulP/SP/live stack; owner/full-register admission, return, ordered IRQ stores and final mappings match the interrupted old router. No timed audio NMI, complete renderer or campaign claim.')
    (a.output / 'paths.json').write_text(json.dumps(paths, indent=2) + '\n')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__':
    main()

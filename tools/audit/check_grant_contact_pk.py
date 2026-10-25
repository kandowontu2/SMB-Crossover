"""Retain normal Grant contacts and interrupt the repaired linked grip paths."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import check_tmnt_primary_irq_od as irq
from check_tmnt_render_oa import load, Memory, address, location
from verify_native_relocation import NesMPU

FIELDS = ('Cv3Climb', 'Cv3ClimbDelay', 'Player_State', 'Cv3JumpActive', 'Cv3JumpPhase',
          'Cv3JumpIndex', 'Cv3AirVX', 'Cv3VxLo', 'Cv3VxHi', 'Cv3VyLo', 'Cv3VyHi',
          'Player_X_Position', 'Player_PageLoc', 'Player_Y_Position')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(bundle, spec, inject=False):
    side, tile, geometry, direction, block_x, gate = spec
    m = Memory(bundle)
    bank = (location(bundle, 'Cv3GrantClimb') - 16) // 8192
    m.page(1, bank)
    m[address(bundle, 'CurrentBank')] = bank | 128
    x = block_x - 15 if side == 1 else block_x + 16
    values = dict(Player_X_Position=x & 255, Player_PageLoc=x >> 8,
        Player_Y_Position=136, Player_State=1, SelectedCharacter=5, Cv3Variant=1,
        Cv3Climb=side, Cv3ClimbDelay=0, Cv3Fresh=0, Cv3AttackAge=0,
        Cv3VxLo=0, Cv3VxHi=0, Cv3VyLo=0, Cv3VyHi=0,
        Cv3JumpActive=1, Cv3JumpPhase=0, Cv3JumpIndex=47,
        SavedJoypadBits=side | direction)
    if gate == 'delay': values['Cv3ClimbDelay'] = 4
    elif gate == 'attack': values['Cv3AttackAge'] = 1
    elif gate == 'jump': values['Cv3Fresh'] = 128
    elif gate == 'admit': values['Cv3Climb'] = 0
    elif gate == 'ceiling': values['Cv3Climb'] = 3
    else: assert gate == 'ordinary'
    for name, value in values.items(): m[address(bundle, name)] = value
    base = address(bundle, 'Block_Buffer_1')
    for i in range(416): m[base + i] = 0
    rows = {'empty': (), 'body': (144,), 'foot': (160,), 'both': (144, 160)}[geometry]
    for y in rows:
        index = (block_x // 256) % 2 * 208 + ((y - 32) // 16) * 16 + (block_x % 256) // 16
        m[base + index] = tile
    m[0x1fe], m[0x1ff] = 0xef, 0xff
    m.writes = []
    c = (irq.InterruptProbe if inject else NesMPU)(memory=m, pc=address(bundle, 'Cv3GrantClimb'))
    c.sp, c.p = 0xfd, 0x30
    minimum = c.sp
    for _ in range(3000):
        if c.pc == 0xfff0: break
        c.step()
        minimum = min(minimum, c.sp)
    else: raise AssertionError(('Grip CPU timeout', spec, hex(c.pc)))
    ignored = set(range(0x100, 0x200)) | {0x2005, 0x2006, 0x5128, 0x5204}
    ignored.add(address(bundle, 'IrqNewScroll'))
    for name in ('R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'MmProbeX', 'MmProbePage', 'MmProbeY', 'Cv3Temp2', 'Cv3Temp3'):
        ignored.add(address(bundle, name))
    app = {at: m[at] for at, _ in m.writes if at not in ignored}
    registers = (c.a, c.x, c.y, c.p & 0xcf, c.sp)
    hardware = [(at, v) for at, v in m.writes if at in (0x2005, 0x2006, 0x5128, 0x5204)]
    assert m.banks == [126, bank, 88, 127]
    assert m[address(bundle, 'CurrentBank')] == bank | 128
    return dict(state=tuple(m[address(bundle, n)] for n in FIELDS), app=app,
        registers=registers, hardware=hardware, cycles=c.processorCycles,
        stack=0xfd - minimum, solid=(m[address(bundle, 'MTileAttribute') + tile] & 3) == 1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = load(a.baseline), load(a.rom)
    retained = repaired = 0
    overhead, depths = set(), [0, 0]
    for spec in itertools.product((1, 2), range(256), ('empty', 'body', 'foot', 'both'), (0, 4, 8), (256, 1744), ('ordinary',)):
        before, after = run(old, spec), run(new, spec)
        depths[0] = max(depths[0], before['stack']); depths[1] = max(depths[1], after['stack'])
        side, tile, geometry, direction, block_x, gate = spec
        if geometry == 'body' and after['solid']:
            assert before['state'][0] == 0 and after['state'][0] == side
            assert after['state'][9:11] == (0, 255 if direction == 8 else 1 if direction == 4 else 0)
            assert after['registers'][3] & 1
            repaired += 1
        else:
            assert after['state'] == before['state'], (spec, before['state'], after['state'])
            assert after['app'] == before['app'], spec
            # Empty fallback probes may leave different dead A/X/Y scratch.
            assert after['registers'][3:] == before['registers'][3:], spec
            retained += 1
            if geometry in ('foot', 'both') and after['solid']:
                overhead.add(after['cycles'] - before['cycles'])
    assert overhead == {19} and depths[1] == depths[0] + 2
    bypass = 0
    for spec in itertools.product((1, 2), (0, 0xc0), ('empty', 'body', 'foot', 'both'), (0, 4, 8), (256,), ('delay', 'attack', 'jump', 'admit', 'ceiling')):
        before, after = run(old, spec), run(new, spec)
        assert before['state'] == after['state'] and before['app'] == after['app'] and before['registers'] == after['registers'], spec
        bypass += 1
    irq_cases, paths = 0, []
    for spec in itertools.product((1, 2), (0xc0,), ('empty', 'body', 'foot', 'both'), (0, 8), (1744,), ('ordinary',)):
        irq.INJECT = None
        plain = run(new, spec, True)
        count = len(irq.LAST.path)
        irq.INJECT = 0
        reference = run(new, spec, True)
        assert irq.LAST.interrupted and reference['state'] == plain['state'] and reference['app'] == plain['app'] and reference['registers'] == plain['registers']
        for instruction in range(count):
            irq.INJECT = instruction
            actual = run(new, spec, True)
            assert irq.LAST.interrupted
            for key in ('state', 'app', 'registers', 'hardware'):
                assert actual[key] == reference[key], (spec, instruction, key)
            irq_cases += 1
        paths.append(dict(spec=spec, instruction_boundaries=count))
    q = dict(passed=True, accepted=False, ROM_sha256=sha(a.rom), baseline_ROM_sha256=sha(a.baseline),
        retained_contacts=retained, repaired_contacts=repaired, inactive_or_bypass_cases=bypass,
        actual_IRQ_injections=irq_cases, IRQ_paths=len(paths), maximum_foreground_stack_bytes=depths,
        unchanged_solid_foot_contact_added_cycles=sorted(overhead), driver_sha256=sha(Path(__file__)),
        scope='All256actual linked metatile classes, two facings, four contact geometries, three directions, page-boundary/interior origins; unchanged gameplay RAM outside declared dead probe scratch. Delay, attack, fresh wall leap, admission and ceiling paths retain old outputs. Actual linked MMC5 IRQ at every instruction boundary of16representative repaired/foot/empty paths restores registers/meaningful flags/SP/PC/live stack and exact application state/hardware-store sequence. No audio-NMI or whole-route claim in this CPU layer.')
    (a.output / 'paths.json').write_text(json.dumps(paths, indent=2) + '\n')
    (a.output / 'proof.json').write_text(json.dumps(q, indent=2) + '\n')
    print(json.dumps(q, indent=2))


if __name__ == '__main__': main()

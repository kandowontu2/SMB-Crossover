"""Finite direct-lift, no-draw continuation and real IRQ pivot controls."""
from pathlib import Path
import argparse
import hashlib
import inspect
import itertools
import json
import traceback
import mm_proto_construction_pivot_cpu_v5 as unit
import mm_proto_body_priority_callers_v3 as callers
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address, location

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def call(bundle, bus, name, x=0, irq=None):
    pc = address(bundle, name)
    bank = (location(bundle, name) - 16) // 8192
    window = (pc - 0x8000) // 8192
    bus.page(window, bank)
    if window in (1, 2):
        bus[address(bundle, 'CurrentBank' if window == 1 else 'CurrentBankC')] = bank | 128
    cpu = NesMPU(memory=bus, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = 0, x, 0, 0x20, 253
    cpu.stPushWord(0x7eff)
    bus.writes = []
    trace, interrupt_writes = [], []
    for ordinal in range(160000):
        if cpu.pc == 0x7f00:
            break
        if ordinal == irq:
            state = (cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p & 207, cpu.sp,
                     tuple(bus.banks), bytes(bus[:0x100] + bus[0x200:0x2000] + bus[0x5c00:0x8000]))
            assert not cpu.p & 4
            first = len(bus.writes)
            cpu.irq()
            for _ in range(500):
                if cpu.pc == state[0] and cpu.sp == state[5]:
                    break
                cpu.step()
            else:
                raise AssertionError(('IRQ timeout', name, ordinal))
            restored = (cpu.pc, cpu.a, cpu.x, cpu.y, cpu.p & 207, cpu.sp,
                        tuple(bus.banks), bytes(bus[:0x100] + bus[0x200:0x2000] + bus[0x5c00:0x8000]))
            assert restored == state, ('IRQ changed live state', name, ordinal)
            interrupt_writes = bus.writes[first:]
            assert all(at in [0x2005, 0x2006, 0x5128, 0x5130] or 0x100 <= at < 0x200
                       for at, value in interrupt_writes)
            del bus.writes[first:]
        bank = bus.banks[(cpu.pc - 0x8000) // 8192] if cpu.pc >= 0x8000 else -1
        trace.append((ordinal, cpu.pc, bank))
        cpu.step()
    else:
        raise AssertionError(('Call timeout', name, hex(cpu.pc)))
    assert cpu.sp == 253
    return cpu, trace, interrupt_writes


def seeded(bundle, cfg):
    return unit.draw(bundle, cfg)[1]


def lift_setup(bundle, cfg, offset=40):
    bus = seeded(bundle, cfg)
    fields = dict(CurrentOAMOffset=offset, ObjectOffset=0, Enemy_Rel_XPos=96,
                  Enemy_Rel_YPos=112, Enemy_OffscreenBits=cfg.get('offscreen', 0),
                  AreaPointer=cfg.get('area', 0x62), WorldNumber=cfg.get('worldnum', 1))
    for name, value in fields.items():
        bus[address(bundle, name)] = value
    bus[address(bundle, 'Enemy_Y_Position')] = cfg.get('lift_y', 112)
    bus[address(bundle, 'Enemy_State')] = 176
    return bus


def compare_partial(old, new, cfg, count):
    left, right = [lift_setup(b, cfg) for b in [old, new]]
    parent_body = unit.draw(old, cfg)[2]
    candidate_body = unit.draw(new, cfg)[2]
    tag = right[address(new, 'GuestOamRotationActive')]
    delta = tag & 252 if cfg.get('char', 1) == 1 else 0
    costs = []
    for index in range(count):
        before = [bytes(m[0x200:0x300]) for m in [left, right]]
        out = []
        for b, m in [(old, left), (new, right)]:
            c, trace, _ = call(b, m, 'DrawSmallPlatform')
            out.append((c, m, trace))
        a, b = out
        assert unit.outcome(a[0], a[1]) == unit.outcome(b[0], b[1]), ('Lift AXYP/SP/banks', cfg, index)
        excluded = set(range(0x100, 0x300)) | {address(old, 'GuestOamRotationActive')}
        diff = [(at, left[at], right[at]) for at in range(0x8000)
                if at not in excluded and left[at] != right[at]]
        assert not diff, ('Lift RAM/SMC', cfg, index, diff[:12])
        writes = [[(at, v) for at, v in m.writes if 0x200 <= at < 0x300] for m in [left, right]]
        assert writes[1] == [(0x200 + ((at - 0x200 + delta) & 255), v) for at, v in writes[0]]
        # Byte-for-byte translation, including transparent/native overlap,
        # prevents newly overwriting a relocated body or previous partial part.
        # The renderer clears only Y: previously unused tile/attribute/X
        # bytes have no whole-page rotation contract. Check every actual
        # store and body-byte overlap rather than inventing such a contract.
        touched = {at for at, value in writes[0]}
        for at in touched:
            assert right[0x200 + ((at - 0x200 + delta) & 255)] == left[at]
        original_overlap = {at for at, value in writes[0] if at in parent_body and before[0][at - 0x200] != value}
        translated_overlap = {at for at, value in writes[1] if at in candidate_body and before[1][at - 0x200] != value}
        assert translated_overlap == {0x200 + ((at - 0x200 + delta) & 255) for at in original_overlap}
        assert not any(0x300 <= at < 0x400 for at, value in right.writes), ('OAM overflow', cfg, index)
        costs.append(b[0].processorCycles - a[0].processorCycles)
    return dict(cfg=cfg, count=count, delta=delta, costs=costs,
                actual_entry='DrawSmallPlatform -> translated/original CrossoverDrawSmallPlatform',
                full_physical_flags_AXY_SP_RAM_SMC_banks_and_exact_store_translation=True)


def continuation(bundle, cfg):
    # Reuse the exact already qualified Main/Idle/NMI/next-GameLoop source
    # runner, supplying this candidate's actual complete renderer and genuine
    # no-draw tail. No source instruction, hook or assertion is normalized.
    text = inspect.getsource(callers.continuation)
    old = 'rendered, initial, drawtrace, drawmeta=partition.run(b,cfg)'
    assert text.count(old) == 1
    text = text.replace(old, 'rendered, initial, _body, drawmeta=unit.draw(b,cfg)')
    assert text.count('start=0x8438') == 1
    text = text.replace('start=0x8438', "start=l('SkipDrawingCauseLagged')")
    env = dict(vars(callers)) | dict(unit=unit)
    exec(compile(text, callers.__file__ + ':actual-pivot-no-draw', 'exec'), env)
    return env['continuation'](bundle, cfg)


def result(cpu, bus, irq=False):
    ram = bytearray(bus[:0x8000])
    if irq:
        ram[0x1c0:0x200] = bytes(64)
        for at in [0x2005, 0x2006, 0x5128, 0x5130]:
            ram[at] = 0
    return unit.outcome(cpu, bus), bytes(ram), tuple(bus.writes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ['parent', 'candidate', 'output']:
        parser.add_argument('--' + key, type=Path, required=True)
    a = parser.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    old, new = [unit.fixture.scoped_load(q) for q in [a.parent, a.candidate]]
    flags, lifts, main, interrupts = [], [], [], []
    try:
        for variant, physical in itertools.product([0, 1], range(64)):
            p = ((physical & 3) | ((physical & 12)) | ((physical & 48) << 2) | 32)
            cfg = dict(entry='DrawAllMetasprites', variant=variant, types=[1] * 4,
                       priorp=0, first=0, shuffle=physical & 1, flags=p)
            flags.append(unit.render(old, new, cfg)[0])
        for char, area, world, mask in [(1, 0x62, 1, 0), (1, 0x62, 4, 14),
                                         (1, 0x40, 0, 8), (1, 0x40, 0, 4),
                                         (1, 0x40, 0, 2), (1, 0x40, 0, 0),
                                         (0, 0x62, 1, 0), (2, 0x40, 0, 14),
                                         (3, 0x62, 4, 0), (18, 0x40, 0, 0)]:
            cfg = dict(entry='DrawAllMetasprites', char=char, variant=0, types=[1] * 4,
                       priorp=0, first=0, shuffle=0, flags=0x61,
                       area=area, worldnum=world, offscreen=mask)
            lifts.append(compare_partial(old, new, cfg, 6))
        for variant, shuffle, irqflag in itertools.product([0, 1], [0, 1], [0, 1]):
            cfg = dict(entry='DrawAllMetasprites', variant=variant, types=[1] * 4,
                       priorp=0, first=0, shuffle=shuffle, flags=0x20, irqflag=irqflag)
            c, m, x = continuation(old, cfg)
            d, n, y = continuation(new, cfg)
            assert (c.pc, unit.outcome(c, m)) == (d.pc, unit.outcome(d, n))
            excluded = set(range(0x100, 0x300)) | {address(old, 'GuestOamRotationActive')}
            diff = [(at, list.__getitem__(m, at), list.__getitem__(n, at)) for at in range(0x8000)
                    if at not in excluded and list.__getitem__(m, at) != list.__getitem__(n, at)]
            assert not diff, ('No-draw Main/NMI RAM', cfg, diff[:12])
            assert x['trace'] == y['trace'], ('No-draw Main/NMI control/writes', cfg)
            main.append(dict(cfg=cfg, NMI=x['actual_NMI'], cycles=[x['cycles'], y['cycles']],
                             complete_no_draw_Main_Idle_NMI_next_GameLoop_exact=True))
        for entry in ['DrawAllMetasprites', 'DrawSmallPlatform', 'DrawVine', 'MoveAllSpritesOffscreen']:
            cfg = dict(entry='DrawAllMetasprites', variant=0, types=[1] * 4,
                       priorp=0, first=0, shuffle=0, flags=0x20)
            def fresh():
                if entry == 'DrawAllMetasprites':
                    _, bus, _ = unit.fixture.fixture.setup(new, cfg)
                    bus[address(new, 'RgOamPlayerStart')] = cfg['priorp']
                    return bus
                if entry == 'DrawSmallPlatform':
                    return lift_setup(new, cfg)
                bus = seeded(new, cfg)
                if entry == 'DrawVine':
                    for name, value in dict(CurrentOAMOffset=40, Enemy_Rel_YPos=176,
                                            Enemy_Rel_XPos=96, Vine_Start_Y_Position=192,
                                            Vine_ObjOffset=5).items():
                        bus[address(new, name)] = value
                return bus
            c, trace, _ = call(new, fresh(), entry)
            expected_cpu, expected_bus = c, fresh()
            expected_cpu, _, _ = call(new, expected_bus, entry)
            # Every executed instruction boundary in the new dispatch/helpers;
            # unchanged generic emitter bulk is not redundantly expanded.
            spans = [(address(new, n), int(new['syms'][n]['size'], 0))
                     for n in ['MmConstructionPivotActive', 'MmConstructionPivotRejected',
                               'MmConstructionPivotClearTag', 'MmConstructionVine', 'MmConstructionSmallLift']]
            begin, end = address(new, 'MmConstructionPivotBegin'), address(new, 'MmConstructionPivotExit') + 39
            sites = {}
            for ordinal, pc, bank in trace:
                if (bank == 4 and (begin <= pc < end or any(st <= pc < st + size for st, size in spans))) or (
                        bank == 66 and any(st <= pc < st + size for st, size in spans)):
                    sites.setdefault((pc, bank), ordinal)
            for (pc, bank), ordinal in sites.items():
                bus = fresh()
                d, _, writes = call(new, bus, entry, irq=ordinal)
                assert result(d, bus, True) == result(expected_cpu, expected_bus, True), ('IRQ full return', entry, pc, bank)
                interrupts.append(dict(entry=entry, pc=pc, bank=bank, instruction_ordinal=ordinal, IRQ_writes=writes))
        (a.output / 'cases.json').write_text(json.dumps(dict(flags=flags, lifts=lifts, main=main, IRQ=interrupts), indent=2) + '\n')
        proof = dict(passed=True, source_only=True, native_launches=0,
                     parent_ROM_sha256=sha(a.parent), candidate_ROM_sha256=sha(a.candidate),
                     full_physical_flag_renderer_cases=len(flags), direct_lift_cases=len(lifts),
                     direct_lift_invocations=sum(q['count'] for q in lifts),
                     no_draw_Main_Idle_NMI_next_GameLoop_cases=len(main), actual_IRQ_cases=len(interrupts),
                     source_actors_staged=True, actual_native_pixels_and_cadence_unproved=True,
                     no_new_RAM_or_NMI_code=True, partial_lift_costs=sorted({v for q in lifts for v in q['costs']}),
                     cases_sha256=sha(a.output / 'cases.json'), tool_sha256=sha(__file__))
        (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
        print(json.dumps(proof, indent=2))
    except BaseException as error:
        (a.output / 'failure.json').write_text(json.dumps(dict(passed=False, error=repr(error),
            traceback=traceback.format_exc(), completed=[len(flags), len(lifts), len(main), len(interrupts)],
            tool_sha256=sha(__file__)), indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()

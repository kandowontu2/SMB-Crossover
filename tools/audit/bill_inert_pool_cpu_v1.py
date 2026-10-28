"""Finite real-assembly Bill inert-pool/caller/interrupt controls; no native."""
from pathlib import Path
import collections
import itertools
import json
import sys
import traceback

R = Path(__file__).resolve().parents[2]
B = R / 'build'
sys.path.insert(0, str(R / 'tools/audit'))
import bill_early_cache_cpu_v1 as H

BASE = B / 'zelda2_easy_glove.nes'
NEW = B / 'bill_inert_pool.nes'
OUT = B / 'bill_inert_pool_cpu.json'
FLAGS = H.FLAGS


class Readers(H.WatchMemory):
    def __init__(self, b):
        self.slot_fields = {H.address(b, n) for n in ('AvSlot', 'RgSlot')}
        self.slot_reads = []
        self.isr = False
        super().__init__(b)

    def __getitem__(self, at):
        v = super().__getitem__(at)
        if isinstance(at, int) and self.watch and self.isr and at in self.slot_fields:
            if sys._getframe(1).f_globals.get('__name__', '').startswith('py65.'):
                self.slot_reads.append((self.cpu.pc, at, v))
        return v


H.WatchMemory = Readers


def app(q):
    return H.app(q), bytes(q.m[0x100 + i] for i in range(q.m.cpu.sp + 1, 256))


def writes(q, row):
    # Exactly two private loop cursors have fewer intermediate publications.
    # Caller-live stack remains compared by app(); consumed return slots do not.
    end = max(int(s['start'], 0) + int(s['size'], 0) for s in q.b['segs'].values()
              if s['name'] in ('"SHORTRAM"', '"SMCCODE"'))
    return [(a, v) for _, _, a, v, _ in row['writes']
            if a not in q.m.slot_fields and not end <= a < 0x200]


def pair(old, new, pool=(), flags=0x20, function='RemainingWeapons', stop=None, **kwargs):
    qs = [H.setup(b, pool=pool, **kwargs) for b in (old, new)]
    results = [H.run(q, function, flags=flags, stop=stop) for q in qs]
    cs = [z[0] for z in results]
    assert H.regs(cs[0]) == H.regs(cs[1]), ('FULL AXYP/SP', pool, kwargs, [H.regs(c) for c in cs])
    # A stop inside AdvanceFreeze still has that genuine JSR's different
    # return PC on stack. Complete calls compare every caller-live byte.
    same = H.app(qs[0]) == H.app(qs[1]) if stop else app(qs[0]) == app(qs[1])
    assert qs[0].m.banks == qs[1].m.banks and same, ('Entire application/live stack/banks', pool, kwargs)
    assert writes(qs[0], results[0][1]) == writes(qs[1], results[1][1]), ('Other ordered writes', pool, kwargs)
    assert results[0][1]['prepares'] == results[1][1]['prepares']
    return cs[1].processorCycles - cs[0].processorCycles, results


def interrupt_readers(b, kind, flags, variant):
    q = H.setup(b, pool=(1,) * 4, variant=variant)
    q.set('NmiDisable', 255)  # Real foreground GameLoop ownership, not an ISR at idle.
    m = q.m
    c = H.NesMPU(memory=m, pc=0x5b00)
    c.a, c.x, c.y, c.p, c.sp = 0x67, 0x89, 0xab, flags, 0xfd
    before = H.regs(c)
    banks = m.banks[:]
    smc = {a: m[a] for a in H.smc_fields(b)}
    m.cpu, m.watch, m.isr = c, True, True
    getattr(c, kind.lower())()
    instructions = 0
    while c.pc != 0x5b00 and instructions < 50000:
        c.step()
        instructions += 1
    assert c.pc == 0x5b00 and c.sp == 0xfd, ('Actual interrupt returns', kind, hex(c.pc))
    assert (c.a, c.x, c.y, c.p & 0xcf, c.sp) == (before[0], before[1], before[2], before[3] & 0xcf, before[4])
    assert m.banks == banks and all(m[a] == v for a, v in smc.items())
    assert not m.slot_reads, ('IRQ/NMI reads private intermediate loop cursors', kind, m.slot_reads)
    return dict(kind=kind, flags=flags, variant=variant, instructions=instructions,
                loop_cursor_reads=0, actual_NmiDisable=255, source_cycles=c.processorCycles)


def main():
    assert not OUT.exists(), 'Preserve each first failure/receipt'
    old, new = H.scoped_load(BASE), H.scoped_load(NEW)
    assert H.sha(BASE) == '32694243361bb1366f6fd64c054ea2451f86b2517fc020d9c2b5d66bbf07bfa0'
    assert H.sha(NEW) == '44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'
    proof = dict(passed=False, native_run=False, parent_sha256=H.sha(BASE), candidate_sha256=H.sha(NEW),
                 counts={}, costs={}, IRQ=0, source_interrupt_readers=[])
    costs = collections.defaultdict(list)
    try:
        n = 0
        for kind, slot, select, flags in itertools.product(range(256), [0, 4, 9], [0, 0x20], [0x20, 0x21, 0x60, 0x61]):
            pool = [0] * 10
            pool[slot] = kind
            stop = 'RemainingWeapons::AdvanceFreeze' if 32 <= kind < 47 and kind not in (42, 43) else None
            delta, _ = pair(old, new, pool, flags, select=select, stop=stop)
            key = 'fresh_Select' if select else ('retained_advanced' if 32 <= kind < 47 else 'no_advanced')
            costs[key].append(delta)
            n += 1
        proof['counts']['all256_types_three_positions_Select_CV_admission_or_complete'] = n
        proof['all_byte_scope'] = 'All nonadvanced byte values and genuine Bill42/43 run complete. Foreign advanced32..41/44..46 compare fullAXYP/SP/application/SMC/banks at actual AdvanceFreeze entry, before executing another family source driver with Bill-owned C bank; nested JSR return PC is intentionally different at this interior boundary. The earlier invalid owner reference failure is retained, not repaired game code.'
        print(json.dumps(dict(section='all256', cases=n)), flush=True)

        patterns = [(), (1,) * 4, (0,) * 6 + (8,) * 4, tuple(range(1, 9)) + (0, 0),
                    (31,) * 10, (47,) * 10, (255,) * 10, (0, 31, 47, 255, 1, 8)]
        n = 0
        for pool, flags, frozen, mode, variant in itertools.product(patterns, FLAGS, [0, 1, 255], [0, 1], [0, 1]):
            delta, _ = pair(old, new, pool, flags, frozen=frozen, mode=mode, variant=variant)
            costs['complete_Remaining_allflags'].append(delta)
            n += 1
        proof['counts']['complete_Remaining_all64flags_modes_variants_freeze'] = n
        print(json.dumps(dict(section='allflags', cases=n)), flush=True)

        n = 0
        for char, pool, mode, flags in itertools.product([i for i in range(20) if i != 3],
                                                        [(), (1,) * 4, (1,) * 10], [0, 1], [0x20, 0x21, 0x60, 0x61]):
            delta, _ = pair(old, new, pool, flags, char=char, mode=mode)
            assert delta == 0, ('Foreign cycle regression/change', char, delta)
            costs['foreign'].append(delta)
            n += 1
        proof['counts']['foreign_complete_remaining'] = n

        n = 0
        for timer, engine, flags in itertools.product([0, 1, 255], range(16), FLAGS):
            qs = [H.setup(b, pool=(1,) * 4) for b in (old, new)]
            for q in qs:
                q.set('TimerControl', timer)
                q.set('GameEngineSubroutine', engine)
            results = [H.run(q, 'RemainingWeapons', flags=flags) for q in qs]
            assert H.regs(results[0][0]) == H.regs(results[1][0]) and app(qs[0]) == app(qs[1])
            assert qs[0].m.banks == qs[1].m.banks
            if timer or engine != 8:
                assert results[0][0].processorCycles == results[1][0].processorCycles
            n += 1
        proof['counts']['timer_engine_allflags_boundaries'] = n

        n = 0
        for pool, enemies, frozen, variant, mode, buttons in itertools.product(
                [(), (1,), (1,) * 4, (0,) * 6 + (2,) * 4, (3,) * 10],
                [0, 3, 6], [0, 1], [0, 1], [0, 1], [0, 0x41, 0x45, 0x21]):
            delta, results = pair(old, new, pool, function='ProcFireball_Bubble',
                                  enemies=enemies, frozen=frozen, variant=variant, mode=mode, buttons=buttons)
            assert all(not z[1]['reads_between_skipped_and_refresh'] for z in results)
            costs['complete_actual_ProcFireball_Bubble'].append(delta)
            n += 1
        proof['counts']['complete_actual_caller'] = n
        n = 0
        for pool, flags, mode, variant, buttons in itertools.product([(1,) * 4, (8,) * 10], FLAGS, [0, 1], [0, 1], [0, 0x41]):
            delta, _ = pair(old, new, pool, flags, function='ProcFireball_Bubble', mode=mode, variant=variant, buttons=buttons)
            costs['complete_actual_caller_allflags'].append(delta)
            n += 1
        proof['counts']['complete_actual_caller_all64flags'] = n
        print(json.dumps(dict(section='fullcaller', cases=proof['counts']['complete_actual_caller'] + n)), flush=True)

        helper = set(range(H.address(new, 'BillEarlyCachePool'), H.address(new, 'BillEarlyCachePool') + 24))
        helper.update(range(H.address(new, 'RemainingWeapons::SamusEmpty'), H.address(new, 'RemainingWeapons::AdvanceFreeze')))
        n = 0
        for pool, select in [((), 0), ((1,) * 4, 0), ((255,) * 10, 0), ((42,), 0), ((1,), 0x20)]:
            initial = H.setup(new, pool=pool, select=select)
            clean_c, clean = H.run(initial, 'ProcFireball_Bubble')
            boundaries = [i for i, (pc, bank, _) in enumerate(clean['trace']) if bank == 6 and pc in helper]
            for index in boundaries:
                q = H.setup(new, pool=pool, select=select)
                c, row = H.run(q, 'ProcFireball_Bubble', irq_at=index)
                assert row['irq_count'] == 1 and H.regs(c) == H.regs(clean_c)
                assert q.m.banks == initial.m.banks and app(q) == app(initial)
                n += 1
        proof['counts']['actual_IRQ_visited_new_boundaries'] = n
        for b in [old, new]:
            for kind, flags, variant in itertools.product(['IRQ', 'NMI'], [0x20, 0x60], [0, 1]):
                proof['source_interrupt_readers'].append(dict(ROM_sha256=H.sha(BASE if b is old else NEW),
                                                            **interrupt_readers(b, kind, flags, variant)))
        proof['costs'] = {k: dict(cases=len(v), minimum=min(v), maximum=max(v), mean=sum(v) / len(v)) for k, v in costs.items()}
        proof['contracts'] = dict(
            full_state='FullAXYP/SP, all application/SHORTRAM/SMC/SRAM/OAM and live stack compare exactly; no cache/V/SMC exception.',
            ordered_writes='Only fewer intermediate writes to the two exact private cursors AvSlot/RgSlot, and consumed CPU return-stack slots, are excluded from ordered-write comparison. Their final values and live stack compare exactly.',
            fast_domain='Bill owner3, nonpaused engine8, no freshSelect, no type32..46 in all ten slots. Entire byte-domain and mixed/capacity pools checked. No pool mutation occurs in AdvanceFreeze; it uses only loads/ORA/DEC/DEX/branches/JSR/STA and preservesC/V.',
            carry='Completed range scan retains slot0 C=0 below32/C=1 above46. The literal final basic/foreign Next comparisons produce that same carry for Bill. Freeze preserves it. Final LDA0 publishes originalNZ; all64 incoming flags compare.',
            other='FreshSelect/trueadvanced retain original cache and source loop. Samus CLC moves before only LDX/STX/DEX, preserving complete state/cycles. No allocation, newRAM, NMI code, audio omission or added mapper trip.',
            interrupt='Actual IRQ injected at every visited changed helper instruction; native lower stack/banks/fiveSMC checks and final wholecaller compare. Source-executed current IRQ and real NMI lag path (NmiDisableFF while Main owns buffer) inspect private cursor reads; no runtime observation/native qualification claimed.',
            performance='All measured deltas are real assembled source CPU under explicit typed arenas. Positive advanced scan costs are disclosed. No actual native frame recovery, faster whole-route or universal60Hz claim.')
        proof['passed'] = True
    except BaseException:
        proof['failure'] = traceback.format_exc()
        raise
    finally:
        proof['tool_sha256'] = H.sha(Path(__file__))
        proof['dependencies'] = {str(p): H.sha(p) for p in [Path(H.__file__), BASE, BASE.with_suffix('.dbg'), NEW, NEW.with_suffix('.dbg'), B / 'bill_inert_pool_build.json']}
        OUT.write_text(json.dumps(proof, indent=2) + '\n', newline='\n')
    print(json.dumps(dict(passed=proof['passed'], counts=proof['counts'], costs=proof['costs'], sha256=H.sha(OUT))))


if __name__ == '__main__':
    main()

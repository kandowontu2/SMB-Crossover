"""Finite assembled Bill admission/caller/cache-liveness controls. No native."""
from pathlib import Path
import argparse
import ast
import collections
import hashlib
import itertools
import json
import sys
import traceback
import zipfile

R = Path(__file__).resolve().parents[2]
B = R / 'build'
sys.path.insert(0, str(R / 'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load, Arena
from check_tmnt_render_oa import address, location, Memory
from verify_native_relocation import NesMPU

sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
BASE = B / 'samus_fixed_hud_current4a.nes'
NEW = B / 'bill_early_cache.nes'
FLAGS = [0x20 | (i & 3) | (i & 4) | (i & 8) | ((i & 16) << 2) | ((i & 32) << 2) for i in range(64)]


def cache_addresses(b):
    return {address(b, n) + i for n, count in [('GuestEnemyMask', 1), ('GuestEnemyX', 6),
        ('GuestEnemyY', 6), ('GuestEnemyMinY', 1), ('GuestEnemyMaxY', 1),
        ('GuestEnemyWrapY', 1), ('RgEnemiesPresent', 1)] for i in range(count)}


class WatchMemory(Memory):
    def __init__(self, b):
        self.cpu = None
        self.watch = False
        self.cache = cache_addresses(b)
        self.cache_reads = []
        self.phase = 'setup'
        super().__init__(b)

    def __getitem__(self, at):
        v = super().__getitem__(at)
        if self.watch and isinstance(at, int) and at in self.cache:
            self.cache_reads.append((self.cpu.pc, at, v, self.phase))
        return v


def setup(b, char=3, variant=0, mode=1, pool=(), select=0, enemies=3, frozen=0, buttons=0):
    q = Arena(b, char)
    q.m = WatchMemory(b)
    q.put(SelectedCharacter=char, BillVariant=variant, ProtoVariant=variant, RlVariant=variant,
        CrossoverBehaviorVersion=mode, PlayerStatus=0, OperMode=1, OperMode_Task=3,
        GameEngineSubroutine=8, Player_Y_HighPos=1, Player_X_Position=96, Player_PageLoc=1,
        Player_Y_Position=160, PlayerFacingDir=1, ScreenLeft_PageLoc=1,
        ScreenLeft_X_Pos=0, DisableScreenFlag=1, AreaType=1, AreaPointer=194,
        InvFresh=select, SavedJoypadBits=buttons, A_B_Buttons=buttons & 0xc0,
        PreviousA_B_Buttons=0, RgPreviousButtons=0, AvStopwatch=frozen)
    q.set('InvSelected', 0, char)
    for slot in range(10):
        kind = pool[slot] if slot < len(pool) else 0
        for name, v in [('RgShotType', kind), ('RgShotDir', 1), ('RgShotX', 112 + 3 * slot),
                        ('RgShotPage', 1), ('RgShotY', 160), ('RgShotYHigh', 1),
                        ('RgShotAge', 6), ('RgShotVXLo', 102), ('RgShotVXHi', 2)]:
            q.set(name, v, slot)
    for slot in range(6):
        active = slot < enemies
        q.set('Enemy_Flag', int(active), slot)
        q.set('Enemy_ID', 6, slot)
        q.set('Enemy_State', 0, slot)
        q.set('Enemy_X_Position', 120 + 16 * slot, slot)
        q.set('Enemy_PageLoc', 1, slot)
        q.set('Enemy_Y_Position', 160, slot)
        q.set('Enemy_Y_HighPos', 1, slot)
        q.set('AvFrozen', frozen, slot)
        q.set('MmEnemyHealthLo', 0, slot)
        q.set('MmEnemyHealthHi', 0, slot)
    for i, at in enumerate(sorted(q.m.cache)):
        q.m[at] = (0x93 + 17 * i) & 255
    # The real foreground caller inherits the selected character C bank from
    # CrossoverGraphicsBank. Memory's generic C88 default is TMNT art, not
    # Bill's source scalar/bounds code ABI in physical19.
    run(q, 'CrossoverGraphicsBank')
    return q


def run(q, name, flags=0x20, stop=None, irq_at=None):
    b, m = q.b, q.m
    bank = (location(b, name) - 16) // 8192
    pc = address(b, name)
    window = (pc - 0x8000) // 8192
    m.page(window, bank)
    if window in (1, 2):
        q.set('CurrentBank' if window == 1 else 'CurrentBankC', bank | 128)
    c = NesMPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = 0x67, 0x89, 0xab, flags, 0xfd
    c.stPushWord(0x5aff)
    m.cpu, m.watch, m.phase = c, True, 'entry'
    m.writes, m.cache_reads = [], []
    prepare = address(b, 'GuestPrepareEnemies')
    remaining = address(b, 'RemainingWeapons')
    roster = address(b, 'RosterWeapons')
    ready = address(b, 'RemainingWeapons::EnemiesReady')
    prepare_count = 0
    prepare_returns = []
    roster_seen = False
    trace, writes, forbidden = [], [], []
    stop_pc = address(b, stop) if stop else 0x5b00
    irq_count = 0
    v_taint = False
    stack_status = {}
    v_writers = []
    status_saves = 0

    def step():
        nonlocal v_taint, status_saves
        op = m[c.pc]
        if v_taint:
            assert op not in (0x50, 0x70), ('Live V branch before overwrite', name, hex(c.pc))
        if op == 0x08:  # PHP is a tracked save, not an escape into an application byte.
            stack_status[0x100 + c.sp] = v_taint
            status_saves += int(v_taint)
        elif op == 0x48:
            stack_status[0x100 + c.sp] = False
        elif op == 0x20:
            stack_status[0x100 + c.sp] = False
            stack_status[0x100 + (c.sp - 1) % 256] = False
        elif op == 0x68:
            assert not stack_status.get(0x100 + (c.sp + 1) % 256, False), ('Status escaped to A', name, hex(c.pc))
        elif op in (0x28, 0x40):
            v_taint = stack_status.get(0x100 + (c.sp + 1) % 256, False)
        elif op == 0xb8 or op in (0x24, 0x2c) or NesMPU.disassemble[op][0] in ('ADC', 'SBC'):
            if v_taint:
                v_writers.append((c.pc, m.banks[(c.pc - 0x8000) // 8192] if c.pc >= 0x8000 else -1, op))
            v_taint = False
        c.step()

    for index in range(100000):
        at = c.pc
        actual_bank = m.banks[(at - 0x8000) // 8192] if at >= 0x8000 else -1
        if at == stop_pc:
            m.watch = False
            return c, dict(prepares=prepare_count, trace=trace, writes=writes,
                cache_reads=m.cache_reads, reads_between_skipped_and_refresh=forbidden,
                irq_count=irq_count, returned_V_potentially_different=v_taint,
                dead_V_independent_overwrites=v_writers, dead_V_PHP_saves=status_saves)
        if at == remaining and actual_bank == 6:
            m.phase = 'remaining'
        if at == ready and actual_bank == 6:
            m.phase = 'after_early_admission'
            if prepare_count == 0 and q.get('SelectedCharacter') == 3 and any(1 <= q.get('RgShotType', i) <= 8 for i in range(10)):
                v_taint = True
        if at == roster and actual_bank == 8:
            roster_seen = True
        if at == prepare and actual_bank == 8:
            prepare_count += 1
            ret = (m[0x100 + (c.sp + 1) % 256] | m[0x100 + (c.sp + 2) % 256] << 8) + 1
            prepare_returns.append((ret, (c.sp + 2) % 256,
                'after_retained_refresh' if roster_seen else 'after_early_admission'))
            m.phase = 'cache_refresh'
        if prepare_returns and (at, c.sp) == prepare_returns[-1][:2]:
            m.phase = prepare_returns.pop()[2]
        if irq_at == index:
            assert not c.p & 4
            before = (c.a, c.x, c.y, c.p & 0xcf, c.sp, c.pc)
            banks = m.banks[:]
            smc = {address(b, n) + 1 for n in ['NextBank_SMC', 'SafecallA_SMC', 'SafereturnA_SMC', 'FarcallJmpTarget_SMC']}
            smc.add(address(b, 'FarcallJmpTarget_SMC') + 2)
            values = {a: m[a] for a in smc}
            before_taint = v_taint
            stack_status[0x100 + (c.sp - 2) % 256] = v_taint
            c.irq()
            for _ in range(3000):
                if (c.a, c.x, c.y, c.p & 0xcf, c.sp, c.pc) == before:
                    break
                step()
            else:
                raise AssertionError(('IRQ return', name, index))
            assert banks == m.banks and all(m[a] == v for a, v in values.items())
            assert before_taint == v_taint
            irq_count += 1
        start_writes, start_reads = len(m.writes), len(m.cache_reads)
        trace.append((at, actual_bank, c.sp))
        try:
            step()
        except BaseException as error:
            raise AssertionError(('CPU fixture execution', name, repr(error), trace[-120:], m.banks)) from error
        writes += [(at, actual_bank, a, v, m.phase) for a, v in m.writes[start_writes:]]
        forbidden += [r for r in m.cache_reads[start_reads:] if r[3] == 'after_early_admission']
    raise AssertionError(('CPU timeout', name, hex(c.pc)))


def regs(c):
    return c.a, c.x, c.y, c.p, c.sp


def smc_fields(b):
    fields = {address(b, n) + 1 for n in ['NextBank_SMC', 'SafecallA_SMC', 'SafereturnA_SMC', 'FarcallJmpTarget_SMC']}
    fields.add(address(b, 'FarcallJmpTarget_SMC') + 2)
    return fields


def app(q, exclude=()):
    excluded = set(exclude)
    live_end = max(int(s['start'], 0) + int(s['size'], 0) for s in q.b['segs'].values()
                   if s['name'] in ('"SHORTRAM"', '"SMCCODE"'))
    return bytes(q.m[a] if a not in excluded else 0 for a in list(range(live_end)) +
                 list(range(0x200, 0x800)) + list(range(0x5c00, 0x8000)))


def actual_smc_liveness(old, new):
    """Five precise operand bytes: source reads must follow their overwrite."""
    original = globals()['WatchMemory']

    class Guard(original):
        def __init__(self, b):
            self.smc = smc_fields(b)
            self.pending = set()
            self.started = False
            self.first_overwrites = []
            self.before_overwrite_reads = []
            super().__init__(b)

        def __setattr__(self, name, value):
            if name == 'phase' and value == 'after_early_admission' and self.watch and not self.started:
                self.pending = set(self.smc)
                self.started = True
            super().__setattr__(name, value)

        def __getitem__(self, at):
            value = super().__getitem__(at)
            # Exclude the checking harness's own snapshots, not CPU reads.
            # The py65 instruction/operand fetch methods are bound dependencies.
            if isinstance(at, int) and self.watch and at in self.pending and sys._getframe(1).f_globals.get('__name__', '').startswith('py65.'):
                self.before_overwrite_reads.append((self.cpu.pc, at, value))
            return value

        def __setitem__(self, at, value):
            if isinstance(at, int) and self.watch and at in self.pending:
                self.first_overwrites.append((at, self.cpu.pc, value))
                self.pending.remove(at)
            return super().__setitem__(at, value)

    counts, examples = 0, []
    try:
        globals()['WatchMemory'] = Guard
        for pool, buttons, mode in itertools.product([(1,), (0,) * 6 + (1,) * 4, (2,) * 6, (3,) * 10], [0, 0x41], [0, 1]):
            q = setup(new, pool=pool, buttons=buttons, mode=mode)
            c, row = run(q, 'ProcFireball_Bubble', flags=0x60)
            assert q.m.started and not q.m.pending
            assert not q.m.before_overwrite_reads
            assert len(q.m.first_overwrites) == 5
            assert not row['returned_V_potentially_different']
            examples.append(dict(pool=list(pool), buttons=buttons, mode=mode,
                first_overwrites=[list(v) for v in q.m.first_overwrites]))
            counts += 1
    finally:
        globals()['WatchMemory'] = original
    return dict(cases=counts, source_reads_before_overwrite=0,
        exact_five_operand_addresses=sorted(smc_fields(new)), examples=examples)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finish-partial', action='store_true')
    args = parser.parse_args()
    old, new = scoped_load(BASE), scoped_load(NEW)
    assert sha(BASE) == '6be48337ffee66a22b22de9ce134d5db323649fb4de620c43bad4ca98b80f193'
    assert sha(NEW) == '9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
    output = B / 'bill_early_cache_controls.json'
    assert not output.exists()
    proof = dict(passed=False, source_CPU_only=True, native_run=False,
        parent_sha256=sha(BASE), candidate_sha256=sha(NEW), counts={}, costs={})
    if args.finish_partial:
        prior = B / 'bill_early_cache_foreign_cost_negative.json'
        assert sha(prior) == 'df672d3a8523f75ff84224bcae616dd5629588fe697251c0d470014d220d44e5'
        proof = json.loads(prior.read_text())
        assert proof['passed'] is False and "('foreign added overhead', 11, -2)" in proof['failure']
        assert proof['counts'] == {'admission_all256_types_three_slots_Select': 1536,
            'complete_remaining_basic_all64flags': 16128,
            'isolated_return_V_differences_NOT_standalone_ABI_claim': 6912,
            'retained_advanced_prefix_all64flags': 5760,
            'actual_complete_ProcFireball_Bubble': 480,
            'actual_complete_caller_all64flags_V_liveness': 3072}
        with zipfile.ZipFile(B / 'bill_early_cache_foreign_cost_tools.zip') as z:
            source = z.read(Path(__file__).name).decode()
        before = {n.name: ast.dump(n) for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        after = {n.name: ast.dump(n) for n in ast.parse(Path(__file__).read_text()).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        for name in ['cache_addresses', 'WatchMemory', 'setup', 'run', 'regs', 'smc_fields', 'app']:
            assert before[name] == after[name], ('Changed inherited CPU core', name)
        proof['inherited_successfully_completed_sections'] = dict(prior_FALSE_sha256=sha(prior),
            prior_tool_sha256=proof['tool_sha256'], same_ROMs_and_CPU_helpers_AST_exact=True,
            scope='Only completed sections before foreign cost assertion are inherited. Original overallFALSE retained; new foreign/IRQ/boundary/liveness controls execute below.')
        del proof['failure']
    try:
        if not args.finish_partial:
            n = 0
            for kind, slot, select in itertools.product(range(256), [0, 4, 9], [0, 0x20]):
                pool = [0] * 10
                pool[slot] = kind
                qs = [setup(b, pool=pool, select=select) for b in [old, new]]
                results = [run(q, 'RemainingWeapons', stop='RemainingWeapons::EnemiesReady') for q in qs]
                assert results[0][1]['prepares'] == int(bool(select or kind))
                assert results[1][1]['prepares'] == int(bool(select or 32 <= kind < 47))
                n += 1
            proof['counts']['admission_all256_types_three_slots_Select'] = n
            n = 0
            costs = collections.defaultdict(list)
            isolated_V_differences = 0
            for pool, enemies, frozen, variant, mode, flags in itertools.product(
                    [(), (1,), (1,) * 4, (1,) * 10, (0,) * 6 + (2,) * 4,
                     (3,) * 10, (8,) * 10], [0, 1, 6], [0, 1, 255], [0, 1], [0, 1], FLAGS):
                qs = [setup(b, pool=pool, enemies=enemies, frozen=frozen, variant=variant, mode=mode) for b in [old, new]]
                results = [run(q, 'RemainingWeapons', flags=flags) for q in qs]
                cs = [z[0] for z in results]
                assert (cs[0].a, cs[0].x, cs[0].y, cs[0].sp) == (cs[1].a, cs[1].x, cs[1].y, cs[1].sp)
                assert (cs[0].p ^ cs[1].p) in (0, 0x40) and qs[0].m.banks == qs[1].m.banks
                if cs[0].p != cs[1].p:
                    assert any(pool) and results[0][1]['prepares'] == 1 and results[1][1]['prepares'] == 0
                    assert results[1][1]['returned_V_potentially_different']
                    isolated_V_differences += 1
                assert app(qs[0], qs[0].m.cache | smc_fields(old)) == app(qs[1], qs[1].m.cache | smc_fields(new))
                # Precise five farcall bytes are private intermediate differences;
                # the complete caller tests below require them all exact again.
                delta = {at for at in smc_fields(old) if qs[0].m[at] != qs[1].m[at]}
                assert delta <= smc_fields(old)
                for h in ['MmEnemyHealthLo', 'MmEnemyHealthHi', 'MmEnemyKind', 'MmEnemyHealthSeen']:
                    if h in old['syms']:
                        assert [qs[0].get(h, i) for i in range(6)] == [qs[1].get(h, i) for i in range(6)]
                costs['basic_nonempty' if any(pool) else 'empty'].append(cs[1].processorCycles - cs[0].processorCycles)
                n += 1
            proof['counts']['complete_remaining_basic_all64flags'] = n
            proof['counts']['isolated_return_V_differences_NOT_standalone_ABI_claim'] = isolated_V_differences
            proof['costs'].update({k: dict(min=min(v), max=max(v), cases=len(v)) for k, v in costs.items()})
            # Fresh Select and true remaining-inventory consumers retain the real
            # preparation. Whole continuation is unchanged after its return.
            n = 0
            retained_cost = []
            for kind, slot, flags, select in itertools.product(range(32, 47), [0, 4, 9], FLAGS, [0, 0x20]):
                pool = [1] * 10
                pool[slot] = kind
                qs = [setup(b, pool=pool, select=select) for b in [old, new]]
                results = [run(q, 'RemainingWeapons', flags=flags, stop='RemainingWeapons::EnemiesReady') for q in qs]
                assert all(r[1]['prepares'] == 1 for r in results)
                assert regs(results[0][0]) == regs(results[1][0]) and qs[0].m.banks == qs[1].m.banks
                assert app(qs[0], smc_fields(old)) == app(qs[1], smc_fields(new))
                retained_cost.append(results[1][0].processorCycles - results[0][0].processorCycles)
                n += 1
            proof['counts']['retained_advanced_prefix_all64flags'] = n
            proof['costs']['retained_advanced_prefix'] = dict(min=min(retained_cost), max=max(retained_cost))
            n = 0
            full_cost = []
            full_examples = []
            patterns = [(), (1,), (0,) * 6 + (1,) * 4, (2,) * 6, (3,) * 10]
            for pool, enemies, frozen, variant, mode, buttons in itertools.product(
                    patterns, [0, 3, 6], [0, 1], [0, 1], [0, 1], [0, 0x41, 0x45, 0x21]):
                qs = [setup(b, pool=pool, enemies=enemies, frozen=frozen,
                            variant=variant, mode=mode, buttons=buttons) for b in [old, new]]
                results = [run(q, 'ProcFireball_Bubble') for q in qs]
                assert regs(results[0][0]) == regs(results[1][0]) and qs[0].m.banks == qs[1].m.banks
                assert app(qs[0]) == app(qs[1]), ('complete caller application state', pool, enemies, buttons)
                assert not results[1][1]['reads_between_skipped_and_refresh'], ('live cache before barrier', pool, enemies, buttons)
                assert all(qs[0].m[a] == qs[1].m[a] for a in smc_fields(old))
                assert not results[1][1]['returned_V_potentially_different'], ('unretired V at native caller', pool, enemies, buttons)
                delta = results[1][0].processorCycles - results[0][0].processorCycles
                full_cost.append(delta)
                if variant == mode == 0 and frozen == buttons == 0:
                    full_examples.append(dict(pool=list(pool), enemies=enemies, old_cycles=results[0][0].processorCycles,
                        new_cycles=results[1][0].processorCycles, old_preparations=results[0][1]['prepares'],
                        new_preparations=results[1][1]['prepares']))
                n += 1
            proof['counts']['actual_complete_ProcFireball_Bubble'] = n
            proof['costs']['actual_complete_caller'] = dict(min=min(full_cost), max=max(full_cost), examples=full_examples)
            n = 0
            v_examples = set()
            for pool, variant, mode, enemy_y, buttons, flags in itertools.product(
                    [(0,) * 6 + (1,) * 4, (2,) * 6, (3,) * 10], [0, 1], [0, 1],
                    [120, 160], [0, 0x41], FLAGS):
                qs = [setup(b, pool=pool, variant=variant, mode=mode, buttons=buttons) for b in [old, new]]
                for q in qs:
                    for i in range(6):
                        q.set('Enemy_Y_Position', enemy_y, i)
                results = [run(q, 'ProcFireball_Bubble', flags=flags) for q in qs]
                assert regs(results[0][0]) == regs(results[1][0]) and qs[0].m.banks == qs[1].m.banks
                assert app(qs[0]) == app(qs[1])
                assert not results[1][1]['returned_V_potentially_different']
                assert not results[1][1]['reads_between_skipped_and_refresh']
                v_examples.update(results[1][1]['dead_V_independent_overwrites'])
                n += 1
            proof['counts']['actual_complete_caller_all64flags_V_liveness'] = n
            proof['actual_V_overwrite_instructions'] = [list(v) for v in sorted(v_examples)]
        # Every foreign family plus all flags for the only changed foreign
        # empty continuation (Samus/Sophia). Nonempty foreign route is old code.
        n = 0
        foreign_costs = []
        for char in range(20):
            if char == 3:
                continue
            for pool, mode, flags in itertools.product([(), (1,), (1,) * 10], [0, 1], FLAGS if char in (2, 11) else [0x20, 0x63, 0xa8, 0xef]):
                qs = [setup(b, char=char, pool=pool, mode=mode) for b in [old, new]]
                results = [run(q, 'RemainingWeapons', flags=flags) for q in qs]
                assert regs(results[0][0]) == regs(results[1][0]) and qs[0].m.banks == qs[1].m.banks
                assert app(qs[0]) == app(qs[1]), ('foreign full app', char, pool, flags)
                delta = results[1][0].processorCycles - results[0][0].processorCycles
                assert delta in (0, -2), ('foreign added overhead', char, delta)
                foreign_costs.append(delta)
                n += 1
        proof['counts']['foreign_complete_remaining'] = n
        proof['costs']['foreign_complete_remaining'] = dict(min=min(foreign_costs), max=max(foreign_costs))
        # Injection at every actually visited new helper/local trampoline
        # boundary. The unchanged true IRQ must restore the interrupted live
        # registers/banks/5SMC and the complete native caller endpoint.
        n = 0
        helper_pcs = set(range(address(new, 'BillEarlyCacheGate'), address(new, 'BillEarlyCacheGate') + 15))
        helper_pcs.update(range(address(new, 'BillEarlyCachePool'), address(new, 'BillEarlyCachePool') + 24))
        helper_pcs.add(address(new, 'RemainingWeapons::BillEarlyCacheJump'))
        for pool, select in [((), 0), ((1,) * 4, 0), ((3,) * 10, 0), ((1,), 0x20)]:
            initial = setup(new, pool=pool, select=select)
            clean_c, clean = run(initial, 'ProcFireball_Bubble')
            boundaries = sorted({i for i, (pc, bank, _) in enumerate(clean['trace']) if bank == 6 and pc in helper_pcs})
            for index in boundaries:
                q = setup(new, pool=pool, select=select)
                c, row = run(q, 'ProcFireball_Bubble', irq_at=index)
                assert row['irq_count'] == 1
                assert regs(c) == regs(clean_c) and q.m.banks == initial.m.banks
                assert app(q) == app(initial)
                assert not row['reads_between_skipped_and_refresh']
                n += 1
        proof['counts']['actual_IRQ_helper_boundaries'] = n
        proof['actual_SMC_overwrite_liveness'] = actual_smc_liveness(old, new)
        proof['contracts'] = dict(
            state='All full caller application RAM includes SHORTRAM and allSMCCODE, not merely zero-page/SRAM. FullAXYP/SP/banks exact. Dead hardware CPU-stack bytes below returnedSP are not caller state.',
            intermediate='Only17 enumerated cache bytes plus precisely5 farcall operands may differ after isolated RemainingWeapons. Complete ProcFireball_Bubble requires every application byte and all5SMC exact again. No blanket SRAM/SMC mask.',
            flags='Standalone RemainingWeapons may return different V from omitted Bill SEC/SBC8. This real negative is retained; no standalone fullAXYP equivalence claim. All64flags complete native caller require FULLP exact and V provenance retired; taintedV may only PHP/PLP-save/restore, never BVS/BVC or PLA into A before an independent ADC/SBC/BIT/CLV overwrite. No global V mask.',
            cache='No source reads of17 cache fields between skipped earlier admission and first retained preparation in every complete caller case. GuestPrepareEnemies is147B and has noJSR/health initialization; native health fields compare exact.',
            cost='Whole actual callers include both scan/helper routing and retained later preparation. SourceCPU arenas are explicit typed setups, not natural native acquisition or60Hz evidence.',
            scope='Bill owner3 includes BillVariant0/1; no other owner pays new overhead. FreshSelect/advanced cases have an explicit measured positive routing cost; no universal speedup claim.')
        proof['passed'] = True
    except BaseException:
        proof['failure'] = traceback.format_exc()
        raise
    finally:
        proof['tool_sha256'] = sha(Path(__file__))
        output.write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof))


if __name__ == '__main__':
    main()

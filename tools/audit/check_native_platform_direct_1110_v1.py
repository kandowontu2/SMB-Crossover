"""Compare the original no-rider $25 path and its local bank-zero dispatch."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import subprocess

import check_native_platform_collision_dispatch_1110_v1 as D
from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import checkpoint, cpu_at


P, N, R = D.P, D.N, D.R
ROM = R / 'build/mini-body-platform-native-1110/candidate.nes'
PIN = '14a4e10058c683605344564d118202970da6ccae4482bf1dfca76b9ad743aacc'
PROFILE = R / 'build/mini-body-peak-1110/capture/instruction-sample.json'
SOURCE = R / 'tools/reference/native_platform_direct_1110_v1.s'
MOTION = 0xb489
BOX = 0xbe6f
STOP = 0x5b00
SCRATCH = frozenset((7, 8, 9, 10, 0x162, 0x16a, 0x16c, 0x16d, 0x179))
PREIMAGES = (
    (MOTION, bytes.fromhex('8d6a01a9408d6c01a9ae8d6d01a99a205a0160eaeaea')),
    (BOX, bytes.fromhex('b517c925f004c928d019b51f2940f0138d6a01a94b8d6c01a9b08d6d01'
                        'a99a205a01604c259f') + bytes([0xea])*9),
)


class ObservedBus(N.Bus):
    """Record actual reads before the first overwrite after direct admission."""

    watch = False

    def __getitem__(self, at):
        if self.watch and isinstance(at, int) and at in self.pending:
            self.first_reads.setdefault(at, self.point)
        return super().__getitem__(at)

    def __setitem__(self, at, value):
        if self.watch and isinstance(at, int) and at in self.pending:
            self.first_writes[at] = self.point
            self.pending.remove(at)
        super().__setitem__(at, value)


def bound_bytes(raw, bank, start, expected):
    at = 16 + 8192*bank + (start & 8191)
    assert raw[at:at+len(expected)] == expected, (bank, hex(start))


def compile_pair(raw, out):
    b = P.bundle(raw)
    for name, pc in (('RunLargePlatform', 0xb436), ('YMovingPlatform', 0xb642),
                     ('HpActorOwner', 0x73ae), ('HpNativePlatformBBoxGate', BOX),
                     ('FlagpoleGfxHandler', 0xbe9e), ('LargePlatformBoundBox', 0x9f25)):
        assert P.address(b, name) == pc, name
    bound_bytes(raw, 0, 0xb436, bytes.fromhex('20e98a20a08a206fbe208eb9ad4a07d0032089b4'))
    bound_bytes(raw, 26, 0xae40, bytes.fromhex('b517c925f004c928d021b51f29c0c940d019'))
    bound_bytes(raw, 26, 0xb04b, bytes.fromhex('e8201a8bcac9fe'))
    assert raw[16:8208].count(bytes.fromhex('2089b4')) == 1
    assert raw[16:8208].count(bytes.fromhex('206fbe')) == 1
    out.mkdir(exist_ok=True)
    cfg, obj, binary = (out/f'direct.{ext}' for ext in ('cfg', 'o', 'bin'))
    cfg.write_text('MEMORY{M:start=$B489,size=22,file=%O; B:start=$BE6F,size=47,file=%O;}\n'
                   'SEGMENTS{MOTION:load=M,type=ro; BOX:load=B,type=ro;}\n')
    cc = R/'tools/Windows/cc65/bin'
    subprocess.run([cc/'ca65.exe', SOURCE, '-o', obj], check=True)
    subprocess.run([cc/'ld65.exe', '-C', cfg, obj, '-o', binary], check=True)
    obj.unlink()
    new = binary.read_bytes()
    assert len(new) == 69 and new[16:19] == bytes.fromhex('4c42b6')
    rows = []
    for (pc, preimage), after in zip(PREIMAGES, (new[:22], new[22:])):
        bound_bytes(raw, 0, pc, preimage)
        rows.append(dict(file_offset=D.file_pc(pc), physical_PRG=0,
                         CPU_half_open=[pc, pc+len(preimage)], old_hex=preimage.hex(), new_hex=after.hex()))
    return install(raw, rows), rows


def begin_watch(m):
    m.watch = True
    m.pending = set(SCRATCH)
    m.first_reads = getattr(m, 'first_reads', {})
    m.first_writes = getattr(m, 'first_writes', {})


def visit(c):
    m = c.memory
    m.point = D.point(c)
    if m.point == (128, MOTION):
        m.map_start = len(m.writes)
    elif m.point == (128, 0xb44a) and m.map_start is not None:
        m.motion_maps.append(tuple(value for at, value in m.writes[m.map_start:] if at == 0x5115))
        m.map_start = None
    if m.point == (128, 0xb499):
        m.direct += 1
        begin_watch(m)
    if m.point == (128, 0xb6f2):
        m.riders += 1


def execute(c, end, retain_pending=False):
    m = c.memory
    m.direct = m.riders = 0
    m.map_start, m.motion_maps = None, []
    m.watch = retain_pending and bool(getattr(m, 'pending', ()))
    m.first_reads = {}
    m.first_writes = {}
    m.writes.clear()
    run(c, end, visit)
    m.watch = False


def state(c, scrub=()):
    m = c.memory
    values = {at: m[at] for at in scrub}
    for at in values:
        list.__setitem__(m, at, 0)
    try:
        return registers(c, 0xef), live_stack(c), D.memory(m)
    finally:
        for at, value in values.items():
            list.__setitem__(m, at, value)


def note_reads(m, result):
    if hasattr(m, 'first_reads'):
        for at, (tag, pc) in m.first_reads.items():
            result[f'{at:04x} at {tag:02x}:{pc:04x}'] += 1


def set_slot(m, name, slot, value):
    m[P.address(m.bundle, name)+slot] = value


def actor_cases(images):
    seeds = [P.fixture(b, 0, False, False) for b in images]
    savings, reads, kinds = Counter(), Counter(), Counter()
    cases = product(range(42), range(0x24, 0x2b), (0, 0x40), (0, 1, 4),
                    ('contact', 'distant', 'leftclip'), (0, 1), (0x21, 0x65))
    for who, actor, tag, owner, scene, timer, p in cases:
        if who not in (0, 4, 10, 41) and (actor not in (0x25, 0x28) or scene == 'leftclip'):
            continue
        cpus = [D.actor_setup(m, who, int(who == 4), actor, tag, scene, timer, p) for m in seeds]
        for c in cpus:
            m = c.memory
            set_slot(m, 'HpActorOwner', 5, owner)
            if actor == 0x24:
                set_slot(m, 'Enemy_State', 5, 0x80)
            if owner == 1 and actor in (0x25, 0x28):
                for name, value in (('HpActorSlot', 6), ('HpVisible', 1), ('HpWidth', 32),
                                    ('HpKind', int(actor == 0x25)), ('HpXLo', 126),
                                    ('HpY', 184), ('HpCount', 1)):
                    set_slot(m, name, 0, value)
            execute(c, D.end)
        a, b = cpus
        key = (who, actor, tag, owner, scene, timer, p)
        direct = b.memory.direct
        assert a.memory.riders == b.memory.riders, key
        assert not direct or (actor == 0x25 and owner == timer == b.memory.riders == 0), key
        kinds['direct' if direct else 'fallback'] += 1
        kinds['rider'] += b.memory.riders
        scrub = SCRATCH if direct else ()
        left, right = state(a, scrub), state(b, scrub)
        assert left == right, (key, left[:2], right[:2],
                               [i for i, (x, y) in enumerate(zip(left[2], right[2])) if x != y])
        if direct:
            note_reads(b.memory, reads)
            assert a.memory.motion_maps == [(154, 128, 154, 128)], (key, a.memory.motion_maps)
            assert b.memory.motion_maps == [()], (key, b.memory.motion_maps)
        else:
            assert a.memory.motion_maps == b.memory.motion_maps, key
        savings[direct, a.processorCycles-b.processorCycles] += 1
    assert all(kinds[name] for name in ('direct', 'fallback', 'rider'))
    return dict(kinds=dict(kinds), reads=dict(reads),
                cycles=[[*key, count] for key, count in sorted(savings.items())])


def whole(images):
    reads, tails = Counter(), Counter()
    results = []
    for lifts, actors, variant in product((1, 3), (0, 2, 3), ('normal', 'skip', 'death', 'transition')):
        if lifts + actors > 6:
            continue
        pair = [D.scene_seed(b, lifts, actors) for b in images]
        stats, admitted = [], 0
        for i in range(8):
            cpus = []
            for m in pair:
                key = 0 if i < 4 else 192
                N.put(m, SavedJoypadBits=key, SavedJoypad1Bits=key,
                      VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0, NmiDisable=0,
                      ShouldSkipDrawSprites=int(variant == 'skip'),
                      FramesSinceLastSpriteDraw=i if variant == 'skip' else 0)
                if variant == 'death' or (variant == 'transition' and i >= 5):
                    N.put(m, GameEngineSubroutine=11)
                if variant == 'transition':
                    N.put(m, GamePauseStatus=int(i in (2, 3)))
                c = cpu_at(m, P.address(m.bundle, 'GameLoop'), 252, 0x21, x=0, y=0)
                execute(c, lambda z: (z.pc, z.sp) == (STOP, 252), retain_pending=True)
                cpus.append(c)
            a, b = cpus
            admitted += b.memory.direct
            live = SCRATCH if hasattr(b.memory, 'pending') else ()
            if live:
                note_reads(b.memory, reads)
                for at in live:
                    if a.memory[at] != b.memory[at]:
                        tails[f'{variant}:{at:04x}'] += 1
            left, right = state(a), state(b)
            assert left == right, (lifts, actors, variant, i, left[:2], right[:2],
                                   [k for k, (x, y) in enumerate(zip(left[2], right[2])) if x != y])
            assert len(a.memory.motion_maps) == len(b.memory.motion_maps)
            maps_removed = 0
            for old_map, new_map in zip(a.memory.motion_maps, b.memory.motion_maps):
                if old_map != new_map:
                    assert old_map == (154, 128, 154, 128) and not new_map
                    maps_removed += 1
            assert maps_removed == b.memory.direct
            stats.append(a.processorCycles-b.processorCycles)
        results.append(dict(lifts=lifts, actors=actors, scene=variant, direct=admitted,
                            saved_cycles=[min(stats), max(stats)]))
    assert not tails and not reads
    return dict(scenes=results, reads=dict(reads), residual_at_GameLoop_return=dict(tails))


def fork_cpu(c, base=None):
    m = slim_fork(c.memory)
    if base is not None:
        m.bundle = base
        for i, tag in enumerate(m.rawtags[:]):
            m.raw_page(i, tag)
    q = N.NesMPU(memory=m, pc=c.pc)
    q.a, q.x, q.y, q.p, q.sp = registers(c)
    return q


def interrupt_checkpoint(c):
    m = c.memory
    watching = m.watch
    m.watch = False
    try:
        return checkpoint(c)
    finally:
        m.watch = watching


def interrupt(c, kind, lag, regular, watch=None):
    pc, sp = c.pc, c.sp
    if kind == 'lag_FF':
        assert N.get(c.memory, 'NmiDisable') == 255
        c.nmi()
    else:
        assert not c.p & 4
        c.irq()
    lag_hits = 0

    def observe(z):
        nonlocal lag_hits
        z.memory.point = D.point(z)
        assert z.pc != regular
        lag_hits += z.pc == lag
        if watch is not None:
            watch(z)

    run(c, lambda z: (z.pc, z.sp) == (pc, sp), observe)
    assert lag_hits == (kind == 'lag_FF')
    c.memory.point = D.point(c)


def vectors(images):
    base, new = images
    seed = D.scene_seed(new, 3, 3)
    lag, regular = lag_pcs(seed)
    totals, deepest, sites = Counter(), {}, set()
    minima = [255, 255]

    def same_cut(c, kind, nested=False):
        result = []
        owner = N.get(c.memory, 'SelectedCharacter')
        checked_poison = False
        for original in (False, True):
            q = fork_cpu(c, base if original else None)
            m = q.memory
            # Change only the omitted bytes, and only when no dispatch is
            # currently using those operands. The real IRQ must tolerate
            # the alternate values until the foreground replaces them.
            dead = m.pending.copy() if m.watch else ()
            checked_poison = bool(dead)
            if original:
                for at in dead:
                    list.__setitem__(m, at, m[at] ^ 255)
            m.first_reads = {}
            before = interrupt_checkpoint(q)

            def watch(z):
                minima[1] = min(minima[1], z.sp)
                if original or kind != 'lag_FF' or z.p & 4:
                    return
                # Hold only the deepest I-clear handler context per owner
                # and pending-operand state. Other cuts share the same IRQ.
                key = owner, bool(m.watch and m.pending)
                if key not in deepest or z.sp < deepest[key].sp:
                    deepest[key] = fork_cpu(z)

            interrupt(q, kind, lag, regular, watch)
            assert interrupt_checkpoint(q) == before, (kind, owner, D.point(c))
            assert not m.first_reads, (kind, owner, D.point(c), m.first_reads)
            m.watch = False
            result.append((state(q, dead), m.writes[:], q.processorCycles))
        assert result[0] == result[1], (kind, owner, D.point(c))
        totals['nested_IRQ' if nested else kind] += 1
        if checked_poison:
            totals['poisoned_nested' if nested else f'poisoned_{kind}'] += 1

    def exercise(c, end):
        seen = set()
        c.memory.direct = c.memory.riders = 0
        c.memory.map_start, c.memory.motion_maps = None, []
        c.memory.watch = False

        def probe(z):
            visit(z)
            tag, pc = D.point(z)
            if tag != 128 or not (MOTION <= pc < MOTION+22 or BOX <= pc < BOX+47 or pc == 0xb642):
                return
            key = pc, z.sp, z.p & 4
            if key in seen:
                return
            seen.add(key)
            sites.add(pc)
            minima[0] = min(minima[0], z.sp)
            same_cut(z, 'lag_FF')
            if not z.p & 4:
                same_cut(z, 'IRQ')

        run(c, end, probe)
        assert seen
        return len(seen)

    cases = []
    for who in range(42):
        where = 'contact' if who % 2 else 'distant'
        c = D.actor_setup(seed, who, int(who == 4), 0x25, 0x40, where, 0, 0x21)
        cases.append(exercise(c, D.end))
    for actor, owner, scene, p in product((0x25, 0x28), (0, 1, 4), ('distant', 'contact'), (0x21, 0x65)):
        c = D.actor_setup(seed, 41, 0, actor, 0x40, scene, 0, p)
        set_slot(c.memory, 'HpActorOwner', 5, owner)
        cases.append(exercise(c, D.end))
    for p in (0x21, 0x65):
        m = slim_fork(seed)
        N.put(m, NmiDisable=0, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
        c = cpu_at(m, P.address(new, 'GameLoop'), 252, p, x=0, y=0)
        cases.append(exercise(c, lambda z: (z.pc, z.sp) == (STOP, 252)))
    for c in deepest.values():
        same_cut(c, 'IRQ', nested=True)
    assert all(totals[x] for x in ('lag_FF', 'IRQ', 'nested_IRQ', 'poisoned_lag_FF',
                                   'poisoned_IRQ', 'poisoned_nested')) and minima[1] > 0x7a
    return dict(cuts=dict(totals), changed_sites=sorted(sites), scenarios=len(cases),
                minimum_SP=minima, actual_lag_PC=lag, forbidden_regular_PC=regular)


def catchup(images):
    totals = Counter()
    rows = []
    for cut, busy in (('lag_FF', False), ('lag_FF', True), ('IRQ', False)):
        results = []
        for b in images:
            m = D.scene_seed(b, 3, 3)
            lag, regular = lag_pcs(m)
            N.put(m, NmiDisable=1, NmiSkipped=0, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
            N.put(m, AreaParserTaskNum=7 if busy else 0, ScrollThirtyTwo=0)
            idle, loop = (P.address(b, n) for n in ('IdleLoop', 'GameLoop'))
            c = cpu_at(m, idle, 252, 0x21, x=0, y=0)
            hits = Counter()
            m.direct = m.riders = 0
            m.map_start, m.motion_maps = None, []
            m.watch = False

            def probe(z):
                visit(z)
                tag, pc = D.point(z)
                hits['loops'] += pc == loop
                if pc == loop and N.get(m, 'ShouldSkipDrawSprites'):
                    hits['skip_loops'] += 1
                if (tag, pc) == (128, 0xb642) and not hits['vectors']:
                    hits['vectors'] += 1
                    before = interrupt_checkpoint(z)
                    interrupt(z, cut, lag, regular)
                    assert interrupt_checkpoint(z) == before

            m.writes.clear()
            run(c, lambda z: (z.pc, z.sp) == (idle, 250) and z.processorCycles > 0, probe)
            m.watch = False
            reads = getattr(m, 'first_reads', {})
            assert hits['vectors'] == 1 and not reads, (cut, hits, reads)
            resumed = cut == 'lag_FF' and not busy
            assert hits['loops'] == 1 + resumed, (cut, busy, hits)
            assert hits['skip_loops'] == resumed, (cut, busy, hits)
            writes = [w for w in m.writes if 0x2000 <= w[0] < 0x6000 and w[0] != 0x5115]
            results.append((state(c), writes, hits, c.processorCycles))
            totals[cut] += 1
        assert results[0][:3] == results[1][:3], cut
        rows.append(dict(vector=cut, secondary_queue=busy, native_loops=results[0][2]['loops'],
                         catchup_skips=results[0][2]['skip_loops'],
                         saved_cycles=results[0][3]-results[1][3]))
    return dict(cuts=dict(totals), cases=rows)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    out = cli.parse_args().output
    raw = ROM.read_bytes()
    assert P.sha(raw) == PIN
    candidate, rows = compile_pair(raw, out)
    images = [P.bundle(q) for q in (raw, candidate)]
    old_bus = N.Bus
    N.Bus = ObservedBus
    try:
        one = actor_cases(images)
        print('Actor tests', one, flush=True)
        assert not one['reads']
        loop = whole(images)
        print('Whole-loop observations', loop, flush=True)
        real_catchup = catchup(images)
        print('Real IdleLoop continuations', real_catchup, flush=True)
        async_result = vectors(images)
        print('Real vectors', async_result, flush=True)
    finally:
        N.Bus = old_bus
    profile = json.loads(PROFILE.read_text())
    assert profile['foreground_opcodes']['0:b489'] == 12
    assert profile['foreground_opcodes'].get('0:b6f2', 0) == 0
    paths = (Path(__file__), SOURCE, PROFILE, R/'src/object.s', R/'src/crossover_helpers.s',
             R/'src/crossover_helper_ram.s', R/'src/sprite_render.s', R/'src/native_platform_bbox_gate.s',
             R/'src/game.s', R/'src/reset.s', R/'src/mmc5.s', R/'tools/audit/freeze_level_variants_agent.py')
    note = dict(parent_SHA256=PIN, expected_memory_only_SHA256=P.sha(candidate), patches=rows,
                actor=one, game_loop=loop, actual_idle_loop=real_catchup, vectors=async_result,
                native_profile=dict(frame=profile['scene']['frame'], stock_untethered=3,
                                    estimate_cycles_saved=630), passed=True, ROM_written=False,
                bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes()) for p in paths})
    (out/'proof.json').write_text(json.dumps(note, indent=2)+'\n')


if __name__ == '__main__':
    main()

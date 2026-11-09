"""Measure the exact Mini visibility shortcut against linked native callers."""
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import json
import subprocess

import profile_mini_busy_1108_v1 as P
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork

R, N = P.R, P.N
OUT = R / 'build/mini-visibility-dispatch-1110'
BASE = R / 'build/mini-current-peak-1110/adder/candidate.nes'
PIN = 'd7a91c05b27d080e89ff60c0e1420e23eb07d762a386ff6a28a81117d8d87c3c'
SOURCE = R / 'tools/reference/mini_visibility_dispatch_1110_v1.s'
AT = 16 + 78 * 8192 + 0x19bf
START, END = 0xb9bf, 0xba1d
OLD = bytes.fromhex(
    '08482008b8b01468288d6a01a9858d6c01a9a28d6d01a9dd4c5a01'
    '68288d6a01a9e08d6c01a9ad8d6d01a9cf4c5a01'
    '08482008b8b01468288d6a01a9ec8d6c01a9a38d6d01a9dd4c5a01'
    '68288d6a01a9e48d6c01a9ad8d6d01a9cf4c5a01')
CALLS = {'player': (129, 0xa2cd, 0xa2d0), 'status': (129, 0xedd4, 0x5b00),
         'rogue_visible': (223, 0xb939, 0x5b00), 'rogue_status': (223, 0xb969, 0x5b00)}


def assemble(out):
    out.mkdir(parents=True, exist_ok=True)
    cfg, obj, data, lbl = (out / f'visibility.{suffix}' for suffix in ['cfg', 'o', 'bin', 'lbl'])
    cfg.write_text('MEMORY{C:start=$B9BF,size=$5E,file=%O;}SEGMENTS{CODE:load=C,type=ro;}\n')
    cc = R / 'tools/Windows/cc65/bin'
    subprocess.run([cc / 'ca65.exe', SOURCE, '-o', obj], check=True)
    subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', data, '-Ln', lbl], check=True)
    obj.unlink()
    labels = {row.split()[2][1:]: int(row.split()[1], 16) for row in lbl.read_text().splitlines()}
    assert labels['RlInjuryStatusDispatch'] == START and labels['RlVisibleDispatch'] == 0xb9ee
    assert labels['VisibleEnd'] == END
    return data.read_bytes(), labels


def address_in_rom(bank, pc):
    return 16 + bank * 8192 + (pc & 0x1fff)


def require_bytes(raw, bank, pc, expected):
    at = address_in_rom(bank, pc)
    assert raw[at:at + len(expected)] == expected, (bank, hex(pc))


def references(raw, low, high):
    # The two source macros expand to these literal public farcall packets.
    prefix = bytes.fromhex(f'8d6a01a9{low:02x}8d6c01a9{high:02x}8d6d01a9ce')
    return [at for at in range(16, 16 + 128 * 8192) if raw.startswith(prefix, at)]


def contract(raw):
    require_bytes(raw, 78, START, OLD)
    require_bytes(raw, 78, 0xb808, bytes.fromhex('ad0260c909d007adeb5ff00238601860'))
    require_bytes(raw, 84, 0xb43b, bytes.fromhex('4ce4b3'))
    require_bytes(raw, 84, 0xb3e4, bytes.fromhex('3860'))
    require_bytes(raw, 1, 0xa2cd, bytes.fromhex('202b91b0034c8ca3'))
    assert references(raw, 0xee, 0xb9) == [address_in_rom(95, 0xb957), address_in_rom(126, 0x912b)]
    assert references(raw, 0xbf, 0xb9) == ([address_in_rom(95, 0xb978)] +
           [address_in_rom(bank, 0xedd4) for bank in [119, 120, 125, 127]])


def memory(m):
    return (bytes(m[:0x100]), bytes(m[0x200:0x800]), bytes(m[0x6000:0x8000]),
            bytes(m[0x15a:0x17b]), tuple(m.rawtags), tuple(map(bytes, m.ram)),
            bytes(m.vram), tuple(m.ppu_log), m.ppuctrl, m.ppu_addr, m.toggle, m.buffer,
            tuple(m.chr_latches), m.upper, m.lastset, tuple(m.protection), m.ppu_reads,
            bytes(m[0x5c00:0x6000]))


def state(c):
    return registers(c, 0xef), live_stack(c), memory(c.memory)


def local(seed, role, fields, a, x, y, p):
    bank, pc, end = CALLS[role]
    m = slim_fork(seed)
    m.raw_page(1, bank)
    N.put(m, CurrentBank=bank, **fields)
    c = N.NesMPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, y, p, 224
    if end == 0x5b00:
        c.stPushWord(end - 1)
    return c, end


def step_local(seed, role, fields, a, x, y, p, visit=None):
    c, end = local(seed, role, fields, a, x, y, p)
    run(c, lambda z: (z.pc, z.sp) == (end, 224), visit)
    return c


def foreground(images):
    seeds = [N.fresh(b) for b in images]
    counts, savings = Counter(), Counter()
    old_minis = Counter()

    def observe(z):
        if z.memory.rawtags[1] == 212 and z.pc == 0xb3e4:
            old_minis['constant'] += 1

    def compare(role, fields, a, x, y, p, mini=False):
        start = old_minis['constant']
        old = step_local(seeds[0], role, fields, a, x, y, p, observe if mini else None)
        new = step_local(seeds[1], role, fields, a, x, y, p)
        left, right = state(old), state(new)
        assert left == right, (role, fields, (a, x, y, p), left[:2], right[:2],
                               [i for i, (v, w) in enumerate(zip(left[2], right[2])) if v != w])
        if mini:
            assert old_minis['constant'] == start + 1 and old.a == a and old.p & 1
        counts[role] += 1
        savings[(role, fields['SelectedCharacter'] == 41, old.processorCycles - new.processorCycles)] += 1

    for raw, role, phase in product(range(256), CALLS, [0, 1]):
        fields = dict(SelectedCharacter=raw, FrameCounter=phase, MarioVariant=phase * 8,
                      RlVariant=phase, OperMode=1, GameEngineSubroutine=8,
                      InjuryTimer=phase, PlayerStatus=phase, MmDeathFlag=phase)
        compare(role, fields, 0x55 + phase * 0xaa, 7, 91, 0x71 if phase == 0 else 0xa4,
                mini=raw == 41 and role in ('player', 'rogue_visible'))

    # Raw41 visibility remains constant under engine/menu changes and across
    # injury/blink/death inputs, independently of the component being loaded.
    for role, engine, injury, phase, p in product(['player', 'rogue_visible'], [0, 5, 6, 7, 8, 9, 10, 11, 255],
                                                   [0, 1, 128, 255], [0, 1], [0x20, 0x65, 0xa0, 0xef]):
        fields = dict(SelectedCharacter=41, FrameCounter=phase, MarioVariant=8,
                      RlVariant=0, OperMode=1 if engine else 0, GameEngineSubroutine=engine,
                      InjuryTimer=injury, PlayerStatus=phase, MmDeathFlag=injury)
        compare(role, fields, [0, 127, 128, 255][p % 4], 6, 17, p, mini=True)

    full = {}
    for actors, parser in [(0, False), (4, False), (4, True), (6, True)]:
        active = [P.fixture(b, actors, False, parser) for b in images]
        samples = []
        for age in range(24):
            key = 0 if age < 8 else 1 if age < 16 else 129
            returns = []
            for m in active:
                N.put(m, FrameCounter=(N.get(m, 'FrameCounter') + 1) & 255, SavedJoypadBits=key,
                      SavedJoypad1Bits=key, VRAM_Buffer1_Offset=0, VRAM_Buffer_AddrCtrl=0)
                returns.append(N.invoke(m, 'GameCoreRoutine', x=0, y=0))
            assert memory(active[0]) == memory(active[1]), (actors, parser, age)
            assert all(returns[0][n] == returns[1][n] for n in 'AXYP'), (actors, parser, age, returns)
            samples.append([r['CPU'] for r in returns])
        full[f'{actors}_parser_{int(parser)}'] = dict(updates=len(samples),
            minimum_saved=min(a-b for a, b in samples), maximum_saved=max(a-b for a, b in samples),
            old_range=[min(a for a, _ in samples), max(a for a, _ in samples)],
            new_range=[min(b for _, b in samples), max(b for _, b in samples)])
    return dict(calls=dict(counts), raw41_original_SEC_entries=old_minis['constant'],
                local_savings=[list(k) + [v] for k, v in sorted(savings.items())], whole_GameCore=full)


def vectors(images):
    seed = N.fresh(images[1])
    counts, minimum = Counter(), [255, 255]
    deepest = {}

    def clone(c, baseline=False):
        m = slim_fork(c.memory)
        if baseline:
            m.bundle = images[0]
            for i, tag in enumerate(m.rawtags[:]):
                m.raw_page(i, tag)
        z = N.NesMPU(memory=m, pc=c.pc)
        z.a, z.x, z.y, z.p, z.sp = registers(c)
        return z

    def interrupt(c, kind):
        z = clone(c)
        ret = z.pc, z.sp
        before = state(z)
        z.memory.writes.clear()
        if kind == 'lag_FF':
            assert N.get(z.memory, 'NmiDisable') == 255
            z.nmi()
        else:
            assert not z.p & 4
            z.irq()

        def inspect(q):
            minimum[1] = min(minimum[1], q.sp)
            if kind != 'lag_FF' or q.p & 4:
                return
            bank = q.memory.rawtags[(q.pc - 0x8000) // 0x2000] if q.pc >= 0x8000 else -1
            key = bank, q.pc
            if key not in deepest or q.sp < deepest[key].sp:
                deepest[key] = clone(q)

        run(z, lambda q: (q.pc, q.sp) == ret, inspect)
        after = state(z)
        # The native IRQ deliberately publishes scroll/CHR registers. Compare
        # every such effect to the unpatched vector on the same interrupted
        # state; those bus writes are not an effect of this foreground patch.
        ref = clone(c, baseline=True)
        ref.memory.writes.clear()
        getattr(ref, 'nmi' if kind == 'lag_FF' else 'irq')()
        run(ref, lambda q: (q.pc, q.sp) == ret)
        assert after == state(ref) and z.memory.writes == ref.memory.writes, (kind, ret)
        assert after[:2] == before[:2] and after[2][3:6] == before[2][3:6], (kind, ret)
        assert after[2][2][2] == before[2][2][2], ('SelectedCharacter', kind, ret)
        assert after[2][-1][0x3eb] == before[2][-1][0x3eb], ('RlVariant', kind, ret)
        if kind != 'lag_FF':
            assert after[2][:7] == before[2][:7] and after[2][-1] == before[2][-1], (kind, ret)
        counts[kind] += 1

    for role, who, phase, p in product(CALLS, [0, 9, 15, 19, 25, 41], [0, 1], [0x20, 0x65]):
        seen = set()

        def visit(c):
            if c.memory.rawtags[1] != 206 or not (START <= c.pc < END or 0xb808 <= c.pc < 0xb818):
                return
            key = c.pc, c.sp, c.p & 4
            if key in seen:
                return
            seen.add(key)
            minimum[0] = min(minimum[0], c.sp)
            interrupt(c, 'lag_FF')
            if not c.p & 4:
                interrupt(c, 'IRQ')

        fields = dict(SelectedCharacter=who, FrameCounter=phase, RlVariant=phase,
                      MarioVariant=phase * 8, OperMode=1, GameEngineSubroutine=8,
                      NmiDisable=255, InjuryTimer=phase, PlayerStatus=phase, MmDeathFlag=phase)
        step_local(seed, role, fields, 0x55, 7, 91, p, visit)
    for c in deepest.values():
        interrupt(c, 'nested_IRQ')
    assert all(counts[k] for k in ['lag_FF', 'IRQ', 'nested_IRQ']) and minimum[1] > 0x7a
    return dict(cuts=dict(counts), minimum_foreground_SP=minimum[0], minimum_ISR_SP=minimum[1])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', type=Path, default=BASE)
    ap.add_argument('--sha', default=PIN)
    ap.add_argument('--output', type=Path, default=OUT)
    args = ap.parse_args()
    raw = args.base.read_bytes()
    assert P.sha(raw) == args.sha
    contract(raw)
    data, labels = assemble(args.output)
    assert len(data) == len(OLD) == END - START
    patch = dict(file_offset=AT, old_hex=OLD.hex(), new_hex=data.hex(), physical_PRG=78,
                 start='B9BF', end_exclusive='BA1D', public_labels=labels)
    image = install(raw, [patch])
    images = [P.bundle(x) for x in [raw, image]]
    normal = foreground(images)
    print('Foreground', normal, flush=True)
    irqs = vectors(images)
    print('Vectors', irqs, flush=True)
    result = dict(passed=True, ROM_written=False, base_SHA256=args.sha, memory_only_SHA256=P.sha(image),
                  patch=patch, foreground=normal, vectors=irqs,
                  scope='Same two public PRG78 entries and footprint; strict full GameCore SMC, AXYP, RAM and mapper parity. No native cadence claim.',
                  bindings={str(p.relative_to(R)): P.sha(p.read_bytes()) for p in
                            [Path(__file__), SOURCE, R/'src/roll_dispatch.s', R/'src/guest_injury.s',
                             R/'src/guest_body_contact.s', R/'src/rogue_dawn_host_lifecycle.s', R/'src/reset.s', R/'src/mmc5.s']})
    (args.output/'visibility-proof.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()

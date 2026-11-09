"""Qualify funded native actor changes, including real vector and foreign paths."""
from collections import Counter
from copy import deepcopy
from itertools import product
from pathlib import Path
import json

import measure_mini_funded_actor_1108_v2 as V

A, N, R, OUT = V.A, V.N, V.R, V.OUT
CPU = N.NesMPU
PRIVATE = R / 'build/mini-native-side-dispatch-rom-1108/candidate.nes'
PRIVATE_SHA = 'b3bda384a54b2685e4cfc8a857304de71f390edc0460d52d051a2d68de746d1f'


def install(raw, patches):
    image = bytearray(raw)
    for patch in patches:
        at = patch['file_offset']
        old, new = (bytes.fromhex(patch[k]) for k in ('old_hex', 'new_hex'))
        assert raw[at:at + len(old)] == old and len(old) == len(new)
        image[at:at + len(new)] = new
    return bytes(image)


def slim_fork(m):
    clone = list.__new__(type(m))
    list.extend(clone, list.__iter__(m))
    for key, value in vars(m).items():
        if key in ('writes', 'ram_writes', 'ppu_log'):
            value = []
        elif key != 'bundle':
            value = deepcopy(value)
        setattr(clone, key, value)
    return clone


def live_stack(c):
    return bytes(list.__getitem__(c.memory, slice(0x101 + c.sp, 0x200)))


def registers(c, status_mask=255):
    return c.a, c.x, c.y, c.p & status_mask, c.sp


def new_cpu(m, pc, a, x, p):
    c = CPU(memory=m, pc=pc)
    c.a, c.x, c.y, c.p, c.sp = a, x, 73, p, 224
    c.stPushWord(0x5aff)
    return c


def run(c, stop, visit=None):
    for _ in range(24000):
        if stop(c):
            return
        if visit:
            visit(c)
        assert c.memory[c.pc], ('BRK in bounded native execution', hex(c.pc), c.sp)
        c.step()
    raise AssertionError(('Native execution bound', hex(c.pc), c.sp))


def set_actor(m, *, slot=0, enemy=6, x=40, page=0, y=184, direction=2, state=0, cell='flat'):
    N.put(m, ObjectOffset=slot, ScreenLeft_X_Pos=0, ScreenLeft_PageLoc=page,
          ScreenRight_X_Pos=255, ScreenRight_PageLoc=page, FrameCounter=2)
    for name, value in [('Enemy_ID', enemy), ('Enemy_Flag', 1), ('Enemy_X_Position', x),
                        ('Enemy_PageLoc', page), ('Enemy_Y_Position', y), ('Enemy_Y_HighPos', 1),
                        ('Enemy_MovingDir', direction), ('Enemy_State', state),
                        ('Enemy_X_Speed', 248 if direction == 2 else 8), ('Enemy_BoundBoxCtrl', 3)]:
        V.setslot(m, name, slot, value)
    if cell != 'flat':
        base = A.address(m.bundle, 'Block_Buffer_2' if page & 1 else 'Block_Buffer_1')
        row = y & 0xf0
        if cell == 'hole' and 0 <= row + ((x + 8) >> 4) < 208:
            m[base + row + ((x + 8) >> 4)] = 0
        side = ((y + 20) & 0xf0) - 32 + ((x + (16 if direction == 1 else 0)) >> 4)
        if cell == 'wall' and 0 <= side < 208:
            m[base + side] = 0xc3


def foreground(images):
    seeds = [A.fixture(b, 0, False, False) for b in images]
    for m in seeds:
        m.raw_page(1, 128)
        N.put(m, CurrentBank=128)
    stats = Counter()
    for x, page, direction, cell, y, p in product([0, 15, 16, 23, 24, 39, 40, 231, 238, 239, 240, 255],
            [0, 1], [1, 2], ['flat', 'wall', 'hole'], [167, 168, 184, 192], [0x20, 0x71]):
        results = []
        for seed in seeds:
            m = slim_fork(seed)
            set_actor(m, x=x, page=page, y=y, direction=direction, cell=cell)
            if y == 168 and cell != 'hole':
                base = A.address(m.bundle, 'Block_Buffer_2' if page else 'Block_Buffer_1')
                m[base + (y & 240) + ((x + 8) >> 4)] = 0x54
            c = new_cpu(m, V.TERRAIN, 83, 0, p)
            native = []
            def observe(z):
                if z.pc == A.address(m.bundle, 'EnemyToBGCollisionDet'):
                    native.append(z.pc)
            run(c, lambda z: z.pc == 0x5b00, observe)
            assert c.sp == 224
            results.append((registers(c), live_stack(c), A.state(m), bool(native), c.processorCycles))
        a, b = results
        assert a[:4] == b[:4], (x, page, direction, cell, y, p, a[:2], b[:2])
        stats[cell, 'native' if a[3] else 'fast', a[4] - b[4]] += 1
    by_dispatch = Counter()
    table = bytes(images[0]['raw'][16 + 0x4cb:16 + 0x4f5])
    assert len(table) == 42 and table == images[1]['raw'][16 + 0x4cb:16 + 0x4f5]
    for owner, enemy, slot, state, p in product([0, 41], range(21), [0, 5], [0, 0x20, 0x40, 0x80], [0x20, 0x71]):
        target = int.from_bytes(table[enemy * 2:enemy * 2 + 2], 'little')
        results = []
        for seed in seeds:
            m = slim_fork(seed)
            N.put(m, SelectedCharacter=owner)
            set_actor(m, slot=slot, enemy=enemy, state=state)
            c = new_cpu(m, 0xa4ba, 83, slot, p)
            if enemy == 6:
                # For Goomba, compare through the complete actual integrator.
                run(c, lambda z: z.pc == 0x5b00)
            else:
                # At all other original destinations, every live entry bit is exact.
                run(c, lambda z: z.pc == target)
            results.append((registers(c), live_stack(c), A.state(m), c.processorCycles))
        a, b = results
        assert a[:3] == b[:3], (owner, enemy, slot, state, p, target, a[0], b[0])
        by_dispatch[enemy, a[3] - b[3]] += 1
    return dict(terrain=[[cell, path, delta, n] for (cell, path, delta), n in sorted(stats.items())],
                dispatch=[[enemy, delta, n] for (enemy, delta), n in sorted(by_dispatch.items())])


def async_paths(b, patches):
    class StackGuard(N.Bus):
        def __getitem__(self, at):
            floor = getattr(self, 'entry_sp', None)
            # $015A..$017A is resident SMC code rather than discarded stack.
            if floor is not None and isinstance(at, int) and 0x17b <= at <= 0x100 + floor:
                assert at in self.replaced, ('Read of uninitialized discarded stack', hex(at), floor)
            return super().__getitem__(at)

        def __setitem__(self, at, value):
            if getattr(self, 'entry_sp', None) is not None and isinstance(at, int) and 0x100 <= at < 0x200:
                self.replaced.add(at)
            super().__setitem__(at, value)

    before = N.Bus
    N.Bus = StackGuard
    try:
        seed = A.fixture(b, 0, False, False)
    finally:
        N.Bus = before
    ranges = [tuple(row['CPU_half_open']) for row in patches]
    deepest = {}
    count = Counter()
    mins = [255, 255]

    def clone(c):
        z = CPU(memory=slim_fork(c.memory), pc=c.pc)
        z.a, z.x, z.y, z.p, z.sp = registers(c)
        return z

    def state(c):
        m = c.memory
        actor = tuple(bytes(m[A.address(m.bundle, name):A.address(m.bundle, name) + 6])
                      for name in ('Enemy_ID', 'Enemy_Flag', 'Enemy_State', 'Enemy_PageLoc', 'Enemy_X_Position',
                                   'Enemy_Y_Position', 'Enemy_MovingDir', 'Enemy_X_Speed', 'Enemy_X_MoveForce'))
        return (registers(c, 0xef), live_stack(c), bytes(m[0:9]), bytes(m[0x15a:0x17b]),
                bytes(m[0x200:0x4a0]), actor, tuple(m.rawtags), tuple(bytes(x) for x in m.ram),
                N.get(m, 'CurrentBank'), N.get(m, 'CurrentBankC'))

    def interrupt(c, kind):
        m = c.memory
        z = clone(c)
        old = state(z)
        ret = z.pc, z.sp
        z.memory.entry_sp = z.sp
        z.memory.replaced = set()
        if kind == 'lag_FF':
            assert N.get(m, 'NmiDisable') == 255
            z.nmi()
        else:
            assert not z.p & 4
            z.irq()

        def observe(x):
            mins[1] = min(mins[1], x.sp)
            if kind == 'lag_FF' and not x.p & 4:
                tag = x.memory.rawtags[(x.pc - 0x8000) // 8192] if x.pc >= 0x8000 else -1
                key = tag, x.pc, N.get(x.memory, 'SelectedCharacter')
                if key not in deepest or x.sp < deepest[key].sp:
                    deepest[key] = clone(x)

        run(z, lambda x: (x.pc, x.sp) == ret, observe)
        z.memory.entry_sp = None
        assert state(z) == old, ('Changed live actor interrupt state', kind, ret)
        assert not any(0x200 <= at < 0x304 or at == 0x4014 for at, _ in z.memory.writes)
        count[kind] += 1

    # Run the actual native actor entry with typed foreign/ground/fallback lanes.
    for owner, scene, p in product([0, 41], ['right', 'left', 'wall', 'hole', 'defeated', 'other'], [0x20, 0x24]):
        m = slim_fork(seed)
        m.raw_page(1, 128)
        N.put(m, SelectedCharacter=owner, CurrentBank=128, NmiDisable=255)
        set_actor(m, x=39, direction=1 if scene in ('right', 'wall') else 2,
                  state=0x20 if scene == 'defeated' else 0, enemy=0 if scene == 'other' else 6,
                  cell=scene if scene in ('wall', 'hole') else 'flat')
        c = new_cpu(m, 0xa458, 83, 0, p)
        m.entry_sp = c.sp
        m.replaced = set()
        seen = set()

        def observe(z):
            if m.rawtags[1] != 128 or not any(a <= z.pc < end for a, end in ranges):
                return
            key = z.pc, z.sp, z.p & 4
            if key in seen:
                return
            seen.add(key)
            mins[0] = min(mins[0], z.sp)
            interrupt(z, 'lag_FF')
            if not z.p & 4:
                interrupt(z, 'IRQ')

        run(c, lambda z: z.pc == 0x5b00, observe)
        assert c.sp == 224 and seen, (owner, scene, p)
    for c in deepest.values():
        interrupt(c, 'nested_IRQ')
    assert mins[1] > 0x7a and count['IRQ'] and count['lag_FF'] and count['nested_IRQ']
    return dict(cuts=dict(count), min_foreground_SP=mins[0], min_handler_SP=mins[1])


def main():
    manifest_path = OUT / 'funded-v2.json'
    manifest = json.loads(manifest_path.read_text())
    raw = A.BASE.read_bytes()
    assert A.sha(raw) == manifest['base_SHA256'] == A.PIN
    new = install(raw, manifest['patches'])
    assert A.sha(new) == manifest['expected_memory_only_SHA256']
    private = PRIVATE.read_bytes()
    assert A.sha(private) == PRIVATE_SHA
    composed = install(private, manifest['patches'])
    images = [A.bundle(z) for z in [raw, new]]
    fore = foreground(images)
    print('Foreground parity', sum(x[3] for x in fore['terrain']), sum(x[2] for x in fore['dispatch']), flush=True)
    interrupts = async_paths(images[1], manifest['patches'])
    report = dict(passed=True, CPU_only=True, ROM_written=False, base_SHA256=A.PIN,
                  actor_memory_SHA256=A.sha(new), side_private_base_SHA256=PRIVATE_SHA,
                  side_private_composed_SHA256=A.sha(composed), foreground=fore, async_actual=interrupts,
                  scope='Exact complete actor native outputs or unchanged native non-Goomba target entry, all 21 movement rows, reached real vectors in modified spans, deepest IRQ contexts within real lag-NMI. Discarded-stack reads require a preceding write. The private side candidate accepts identical nonoverlapping exact preimages.',
                  bindings={str(p):A.sha(p.read_bytes()) for p in [Path(__file__), manifest_path, Path(V.__file__),
                            A.BASE, PRIVATE, R/'src/object.s', R/'src/ground_goomba_terrain.s', R/'src/reset.s']})
    (OUT/'funded-v3-CPU.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Interrupts', interrupts, 'private combined', A.sha(composed), flush=True)


if __name__ == '__main__':
    main()

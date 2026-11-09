"""Check actual interrupt cuts and finite scratch use of the lift-body optimization."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import measure_mini_lift_actor_bridge_1108_v4 as L

F, A, N, R, OUT = L.F, L.A, L.N, L.R, L.OUT
IRQ_I = 4


def main():
    manifest_path = OUT / 'lift-bridge-v4.json'
    manifest = json.loads(manifest_path.read_text())
    raw = L.BASE.read_bytes()
    assert A.sha(raw) == L.PIN == manifest['base_SHA256']
    new = F.install(raw, manifest['patches'])
    assert A.sha(new) == manifest['expected_memory_only_SHA256']
    b = A.bundle(new)
    old_image = A.bundle(raw)
    current = raw[16+58*8192:16+59*8192]
    bank0 = raw[16:16+8192]
    targets = []
    for outer, leaf, row in zip(L.GATES, L.LEAVES, manifest['patches']):
        pc = A.address(b, leaf)
        lo, hi = pc & 255, pc >> 8
        # Actual typed tail from the Zelda II selector. No other same-bank
        # JSR/JMP encoding targets the old body or reads the claimed entry.
        assert current.count(bytes([0x4c, lo, hi])) == 1
        assert current.count(bytes([0x20, lo, hi])) == 0
        gate = A.address(b, outer)
        assert current[gate-0xa000:gate-0xa000+39].endswith(bytes([0x68, 0x28, 0x4c, lo, hi]))
        operand = bytes([0xa9, gate & 255, 0x8d, 0x6c, 1, 0xa9, gate >> 8, 0x8d, 0x6d, 1, 0xa9, 186])
        assert bank0.count(operand) == 1
        targets.append([outer, gate, leaf, *row['CPU_half_open']])

    ranges = [tuple(row['CPU_half_open']) for row in manifest['patches']]
    rg_temps = {A.address(b, n) for n in L.NAMES[2:7]}
    protected_sram = rg_temps | {A.address(b, n) for n in ('SelectedCharacter', 'RyuSourceBodyProfile', 'Z2Variant')}

    class Bus(N.Bus):
        mode = None
        stack_cut = None

        def __getitem__(self, at):
            if isinstance(at, int):
                if self.mode == 'body':
                    assert at not in rg_temps, ('Unanticipated private-temp read', hex(at))
                if self.stack_cut is not None and 0x17b <= at <= 0x100 + self.stack_cut:
                    assert at in self.stack_overwritten, ('Read of discarded private stack', hex(at))
            return super().__getitem__(at)

        def __setitem__(self, at, value):
            if isinstance(at, int):
                if self.mode == 'body':
                    assert at not in rg_temps, ('Unanticipated private-temp write', hex(at))
                if self.stack_cut is not None and 0x17b <= at < 0x200:
                    self.stack_overwritten.add(at)
            super().__setitem__(at, value)

    original_bus = N.Bus
    N.Bus = Bus
    try:
        seed = A.fixture(b, 0, False, False)
    finally:
        N.Bus = original_bus
    counts = Counter()
    deepest = {}
    mins = [255, 255]
    witness = Counter()
    gate_pc = A.address(b, 'RyuSourceBodyLargePlatformBridge')
    platform_pc = A.address(b, 'RunLargePlatform')
    hooks = {A.address(b, n): n for n in ['RyuSourceBodyBox', 'RyuSourceBodyPlatformOverlap',
                                         'RyuSourceBodyPlatformBasic', 'BoundingBoxCore', 'RelativePlayerPosition']}

    def snapshot(c):
        m = c.memory
        native = bytes(list.__getitem__(m, slice(0x200, 0x700)))
        return (F.registers(c, 0xef), F.live_stack(c), native, bytes(m[:11]),
                bytes(list.__getitem__(m, slice(0x15a, 0x17b))), bytes(m[0x6000:0x8000]),
                tuple(map(bytes, m.ram)), tuple(m.rawtags), N.get(m, 'CurrentBank'), N.get(m, 'CurrentBankC'),
                tuple(m.chr_latches), tuple(m.protection))

    def clone(c):
        z = F.CPU(memory=F.slim_fork(c.memory), pc=c.pc)
        z.a, z.x, z.y, z.p, z.sp = F.registers(c)
        z.memory.mode = None
        z.memory.stack_cut = None
        return z

    def interrupt(c, kind):
        z = clone(c)
        before = snapshot(z)
        ret = z.pc, z.sp
        z.memory.stack_cut = z.sp
        z.memory.stack_overwritten = set()
        if kind == 'lag_FF':
            assert N.get(z.memory, 'NmiDisable') == 255
            z.nmi()
        else:
            assert not z.p & IRQ_I
            z.irq()
        def watch(q):
            mins[1] = min(mins[1], q.sp)
            assert q.memory.rawtags[1] != 186 or not any(a <= q.pc < end for a, end in ranges)
            if kind == 'lag_FF' and not q.p & IRQ_I:
                tag = q.memory.rawtags[(q.pc-0x8000)//8192] if q.pc >= 0x8000 else -1
                key = tag, q.pc, N.get(q.memory, 'SelectedCharacter')
                if key not in deepest or q.sp < deepest[key].sp:
                    deepest[key] = clone(q)

        F.run(z, lambda q: (q.pc, q.sp) == ret, watch)
        z.memory.stack_cut = None
        after = snapshot(z)
        assert after[:5] == before[:5] and after[6:] == before[6:], (kind, ret, [i for i in range(len(after)) if after[i] != before[i]])
        assert all(after[5][addr-0x6000] == before[5][addr-0x6000] for addr in protected_sram)
        if after[5] != before[5]:
            # Source audio advances its own SRAM while the host is late. For
            # every such cut, replay the original native handler from exactly
            # the same foreground snapshot and require all bytes/writes equal.
            assert kind == 'lag_FF'
            previous = clone(c)
            previous.memory.bundle = old_image
            for window, tag in enumerate(previous.memory.rawtags[:]):
                previous.memory.raw_page(window, tag)
            previous.nmi()
            F.run(previous, lambda q: (q.pc, q.sp) == ret)
            assert snapshot(previous) == after and previous.memory.writes == z.memory.writes
            counts['lag_audio_state_paired_exact'] += 1
        assert not any(0x200 <= at < 0x304 or at == 0x4014 for at, _ in z.memory.writes)
        counts[kind] += 1

    for owner, variant, scene, p in product([0, 4, 10, 41], [0, 1], ['near', 'tagged'], [0x20, 0x24]):
        m = F.slim_fork(seed)
        m.raw_page(1, 128)
        N.put(m, CurrentBank=128, NmiDisable=255)
        L.inject_witness(m, owner, variant, scene, 0)
        # Initialize the physical CHR latches through the real lag vector.
        # The cold CPU fixture starts those write-only latches at model zero.
        prime = F.CPU(memory=m, pc=0x5b00)
        prime.sp = 224
        prime.nmi()
        F.run(prime, lambda q: (q.pc, q.sp) == (0x5b00, 224))
        c = F.new_cpu(m, platform_pc, 0x87, 0, p)
        m.stack_cut = c.sp
        m.stack_overwritten = set()
        seen = set()
        body_sp = None

        def watch(z):
            nonlocal body_sp
            bank58 = m.rawtags[1] == 186
            in_span = bank58 and any(a <= z.pc < end for a, end in ranges)
            if bank58 and z.pc in {start for start, _ in ranges}:
                body_sp = z.sp
                m.mode = 'body'
                witness[owner, 'legacy'] += 1
            if body_sp is not None and z.sp > body_sp:
                body_sp = None
                m.mode = None
            if body_sp is not None and z.pc in hooks:
                witness[owner, hooks[z.pc]] += 1
            if m.rawtags[1] == 128 and z.pc == gate_pc:
                witness[owner, 'bridge'] += 1
            key = z.pc, z.sp, z.p & IRQ_I
            if in_span and key not in seen:
                seen.add(key)
                mins[0] = min(mins[0], z.sp)
                interrupt(z, 'lag_FF')
                if not z.p & IRQ_I:
                    interrupt(z, 'IRQ')

        F.run(c, lambda z: z.pc == 0x5b00, watch)
        assert c.sp == 224
        assert bool(seen) == (owner != 4 or not variant), (owner, variant, scene, p, seen)
    for cut in deepest.values():
        interrupt(cut, 'nested_IRQ')
    assert all(counts[k] for k in ['lag_FF', 'IRQ', 'nested_IRQ']) and mins[1] > 0x7a
    assert all(witness[10, name] for name in hooks.values())
    assert all(witness[owner, 'bridge'] and witness[owner, 'legacy'] for owner in [0, 4, 10, 41])
    assert not any(witness[owner, name] for owner in [0, 4, 41] for name in hooks.values())
    receipt = dict(passed=True, CPU_only=True, ROM_written=False, base_SHA256=L.PIN,
                   expected_memory_only_SHA256=A.sha(new), compiled_caller_edges=targets,
                   native_callee_witnesses=[[owner, n, ct] for (owner, n), ct in sorted(witness.items()) if ct],
                   actual_vectors=dict(counts), min_foreground_SP=mins[0], min_vector_SP=mins[1],
                   protected='Live AXYP/SP, live stack, native OAM/tile scratch, R0..7, owner/private RAM, original SMC, PRG and CHR mapping, no lag DMA or discarded-stack read before overwrite.',
                   source_domain='Actual legacy prepare only calls original overlap→Basic; legacy finish only calls Basic, RelativePlayerPosition, BoundingBoxCore and RyuSourceBodyBox. All five removed RgTemp accesses absent across actual typed descendants; all positive Ryu roots reached. Zelda II owner variant1 never enters rewritten legacy roots.',
                   audio_scratch_scope='Any lag-induced SRAM update is replayed with the actual original vectors from the identical cut and requires exact full SRAM and ordered write parity. Strict protected owner and lift-body SRAM always remains byte-identical.',
                   bindings={str(p):A.sha(p.read_bytes()) for p in [Path(__file__), manifest_path, Path(L.__file__),
                             L.BASE, R/'src/reset.s', L.SOURCE, L.MACROS, R/'src/zelda2_link_platform.s', R/'src/roster_audio.s']})
    (OUT/'lift-bridge-v5-CPU.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('Lift bridge real vectors', dict(counts), 'minSP', mins, flush=True)


if __name__ == '__main__':
    main()

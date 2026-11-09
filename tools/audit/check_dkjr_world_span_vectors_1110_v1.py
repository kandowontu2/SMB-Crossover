"""Rebind actual IRQ and lag-NMI checks to the signed-world successor."""
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_dkjr_world_span_1110_v1 as V
from check_mini_visibility_dispatch_1110_v1 import state


def main():
    raw, _, cookie, _ = V.R.pinned_inputs()
    proof = V.OUT / 'span-proof.json'
    q = json.loads(proof.read_text())
    assert q['passed'] and q['base_SHA256'] == V.R.PIN
    for name, digest in q['bindings'].items():
        assert V.I.sha((V.R.R / name).read_bytes()) == digest, name
    data = (V.OUT / 'span.bin').read_bytes()
    first = q['first_helper_bytes']
    new, old_payload, new_payload, new_cookie, rows = V.proposal(raw, data[:first], data[first:], cookie)
    assert V.I.sha(new) == q['memory_only_SHA256'] and rows == q['patches']
    seed = V.make_seed(new, new_payload)
    for bank in [2, 3]:
        seed.ram[bank][0x1fe0:0x1ff0] = new_cookie
    seed.ram[2][0x8fe] = 2
    baseline_bundle = V.I.SYMBOLS.bundle()
    baseline_bundle['raw'] = raw
    deepest = {}
    counts = Counter()
    minimum = [255, 255]

    def clone(c, original=False):
        m = V.slim_fork(c.memory)
        if original:
            m.bundle = baseline_bundle
            for window, tag in enumerate(m.rawtags[:]):
                m.raw_page(window, tag)
        z = V.N.NesMPU(memory=m, pc=c.pc)
        z.a, z.x, z.y, z.p, z.sp = V.registers(c)
        return z

    def check(c, kind):
        z, ref = clone(c), clone(c, original=True)
        before = state(z)
        ret = z.pc, z.sp

        def observe(q):
            minimum[1] = min(minimum[1], q.sp)
            m = q.memory
            tag = m.rawtags[(q.pc - 0x8000)//8192] if q.pc >= 0x8000 else -1
            assert tag not in [2, 3], ('Native vector entered mutable DK private code', hex(q.pc), tag)
            if kind == 'FF_lag_NMI' and not q.p & 4:
                key = tag, q.pc
                if key not in deepest or q.sp < deepest[key].sp:
                    deepest[key] = clone(q)

        for p, inspect in [(z, observe), (ref, None)]:
            p.memory.writes.clear()
            if kind == 'FF_lag_NMI':
                assert V.N.get(p.memory, 'NmiDisable') == 255
                p.nmi()
            else:
                assert not p.p & 4
                p.irq()
            V.run(p, lambda x: (x.pc, x.sp) == ret, inspect)
        after = state(z)
        assert after == state(ref) and z.memory.writes == ref.memory.writes, (kind, ret)
        assert before[:2] == after[:2] and before[2][3:7] == after[2][3:7], (kind, ret)
        assert not any(a == 0x4014 for a, _ in z.memory.writes)
        counts[kind] += 1

    exact = {}
    shapes = {'right_231_camera_0': (0, 231, 239, 0, 191, 206),
              'native_wall_433_camera_435': (435, -2, 239, 0, 191, 206),
              'camera_end_lock_over_255': (435, 273, 239, 0, 191, 206),
              'native_page_rollover': (65530, 231, 239, 0, 191, 206),
              'nonwrapped': (260, 80, 60, 92, 191, 206)}
    for (name, shape), kind in product(shapes.items(), range(4)):
        seen = set()

        def visit(c):
            pc = c.pc
            tag = c.memory.rawtags[(pc - 0x8000)//8192] if pc >= 0x8000 else -1
            if not (tag == 3 and 0xb38f <= pc < 0xb3b7 or tag == 2 and
                    (V.LEFT <= pc < V.LEFT + first or V.RIGHT <= pc < V.RIGHT + len(data) - first)):
                return
            key = tag, pc, c.sp, c.p & 4
            if key in seen:
                return
            seen.add(key)
            minimum[0] = min(minimum[0], c.sp)
            check(c, 'FF_lag_NMI')
            if not c.p & 4:
                check(c, 'IRQ')

        _, cells = V.scan(seed, (*shape, kind), visit)
        assert seen and cells == V.expected(*shape, kind)
        exact[f'{name}_kind{kind}'] = cells
    for cpu in deepest.values():
        check(cpu, 'nested_IRQ')
    assert all(counts[n] for n in ['FF_lag_NMI', 'IRQ', 'nested_IRQ']) and minimum[1] > 0x7a
    receipt = dict(passed=True, ROM_written=False, memory_only_SHA256=q['memory_only_SHA256'],
                   cuts=dict(counts), minimum_foreground_SP=minimum[0], minimum_ISR_SP=minimum[1],
                   exact_scan_columns=exact,
                   bindings={p.relative_to(V.R.R).as_posix(): V.I.sha(p.read_bytes())
                             for p in [Path(__file__), Path(V.__file__), proof, V.SOURCE]},
                   scope='Actual native IRQ, FF lag NMI and nested IRQ at reached changed source cuts. Full private RAM, SMC, maps, AXYP/SP and live stack strict. Original native vector effects compared byte for byte.')
    (V.OUT/'span-vectors.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('DK Jr signed-world vectors', dict(counts), minimum, flush=True)


if __name__ == '__main__':
    main()

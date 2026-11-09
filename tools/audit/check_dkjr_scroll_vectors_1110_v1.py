"""Check the scroll helper and inlined terrain at genuine interrupt cuts."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import check_dkjr_scroll_publish_1110_v1 as S
from check_mini_visibility_dispatch_1110_v1 import state

V, R, I, N = S.V, S.R, S.I, S.N


def main():
    proof = S.OUT/'camera-proof.json'
    q = json.loads(proof.read_text())
    for name, sha in q['bindings'].items():
        assert I.sha((R.R/name).read_bytes()) == sha, name
    raw, _, _, _ = R.pinned_inputs()
    raw = R.OAM.compose(raw, json.loads(S.SPAN.read_text())['patches'])
    after = R.OAM.compose(raw, q['patches'])
    assert I.sha(raw) == q['base_SHA256'] and I.sha(after) == q['memory_only_SHA256']
    pages = [817, 833, 847, 856, 867, 881, 882, 883, 959, 960, 961]
    payload = b''.join(after[V.CHR+p*1024:V.CHR+(p+1)*1024] for p in pages)
    seed = V.make_seed(after, payload)
    seed.ram[2][0x8fe] = 2
    for bank in [2, 3]:
        seed.ram[bank][0x1fe0:0x1ff0] = bytes.fromhex(q['cookie'])
    reference = I.SYMBOLS.bundle()
    reference['raw'] = raw
    minimum = [255, 255]
    counts = Counter()
    deepest = {}

    def clone(c, previous=False):
        m = V.slim_fork(c.memory)
        if previous:
            m.bundle = reference
            for i, tag in enumerate(m.rawtags[:]):
                m.raw_page(i, tag)
        new = N.NesMPU(memory=m, pc=c.pc)
        new.a, new.x, new.y, new.p, new.sp = V.registers(c)
        return new

    def interrupt(c, kind):
        z, ref = clone(c), clone(c, previous=True)
        before = state(z)
        target = z.pc, z.sp

        def inspect(p):
            minimum[1] = min(minimum[1], p.sp)
            tag = p.memory.rawtags[(p.pc-0x8000)//8192] if p.pc >= 0x8000 else -1
            assert tag not in [2,3]
            if kind == 'FF' and not p.p & 4:
                key = tag, p.pc
                if key not in deepest or p.sp < deepest[key].sp:
                    deepest[key] = clone(p)

        for p, hook in [(z, inspect), (ref, None)]:
            p.memory.writes.clear()
            if kind == 'FF':
                assert N.get(p.memory, 'NmiDisable') == 255
                p.nmi()
            else:
                assert not p.p & 4
                p.irq()
            V.run(p, lambda k: (k.pc,k.sp) == target, hook)
        got = state(z)
        assert got == state(ref) and z.memory.writes == ref.memory.writes, (kind, target)
        assert got[:2] == before[:2] and got[2][3:7] == before[2][3:7], (kind, target)
        assert z.memory[0x75a] == c.memory[0x75a] and not any(a == 0x4014 for a, _ in z.memory.writes)
        counts[kind] += 1

    def watch(c):
        tag = c.memory.rawtags[(c.pc-0x8000)//8192] if c.pc >= 0x8000 else -1
        if not (tag == 3 and 0xb345 <= c.pc < 0xb3b7 or tag == 2 and
                (0xd240 <= c.pc < 0xd25e or 0xd2d5 <= c.pc < 0xd2f7 or c.pc == 0xd66d)):
            return
        key = tag, c.pc, c.sp, c.p & 4
        if key in seen:
            return
        seen.add(key)
        minimum[0] = min(minimum[0], c.sp)
        interrupt(c, 'FF')
        if not c.p & 4:
            interrupt(c, 'IRQ')

    for camera, relative, p in product([0, 435, 0xfff0], [-2, 30, 231, 273], [0x21, 0x65]):
        seen = set()
        c = V.prep(seed, camera, relative, 239, 0, 191, 206, 0)
        c.pc, c.p = 0xd66d, p
        V.run(c, lambda z: z.pc == 0xd540, watch)
        assert N.get(c.memory, 'Player_Pos_ForScroll') == max(0,min(255,relative))
        assert seen
    for camera, relative, kind in product([0, 435], [-2, 231, 273], range(4)):
        seen = set()
        args = camera,relative,239,0,191,206,kind
        _, cells = V.scan(seed, args, watch)
        assert seen and cells == V.expected(*args)
    for cpu in deepest.values():
        interrupt(cpu, 'nested_IRQ')
    assert all(counts[k] for k in ['FF','IRQ','nested_IRQ']) and minimum[1] > 0x7a
    receipt = dict(passed=True, ROM_written=False, memory_only_SHA256=q['memory_only_SHA256'],
                   cuts=dict(counts), minimum_foreground_SP=minimum[0], minimum_ISR_SP=minimum[1],
                   bindings={f.relative_to(R.R).as_posix(): I.sha(f.read_bytes()) for f in
                             [Path(__file__), proof, S.SOURCE, Path(S.__file__)]},
                   scope='Exact scroll publication and signed geometry. Actual native IRQ/FF/nested effects matched prior vectors. Protected source state, SMC, maps, 075A and live stack.')
    (S.OUT/'camera-vectors.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('DK Jr scroll vectors', dict(counts), minimum, flush=True)


if __name__ == '__main__':
    main()

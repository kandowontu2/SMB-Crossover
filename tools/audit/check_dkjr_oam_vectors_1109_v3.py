"""Check genuine FF-lag NMI and IRQ cuts in the repaired DK Jr renderer."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import check_dkjr_oam_slot_1109_v2 as B

P, I, N, OUT = B.P, B.I, B.N, B.OUT


def main():
    proposal_path = OUT/'oam-source.json'
    proposal = json.loads(proposal_path.read_text())
    raw = P.compose(P.PRIVATE.read_bytes(), proposal['patches'])
    cookie = bytes.fromhex(proposal['patches'][-1]['new_hex'])
    assert P.sha(raw) == proposal['memory_only_hashes'][P.PIN]
    # Capture the genuine cold/entrance fixture immediately before its first
    # GameCore; its original actor/headers are constructed by real loaders.
    class Captured(Exception):
        pass

    seed = None
    invoke = N.invoke

    def hold(m, name, *args, **kwargs):
        nonlocal seed
        if name == 'GameCoreRoutine':
            seed = m
            raise Captured
        return invoke(m, name, *args, **kwargs)

    N.invoke = hold
    try:
        I.cpu(raw, cookie)
    except Captured:
        pass
    finally:
        N.invoke = invoke
    assert seed and seed.ram[2][0x8fe] == 1
    N.put(seed, FrameCounter=1, NmiDisable=255, VRAM_Buffer1_Offset=0)
    N.invoke(seed, 'GameCoreRoutine', x=0, y=0, a=83)
    assert seed.ram[2][0x8fe] == 2
    I.C.clear(seed)
    counts = Counter()
    deepest = {}
    mins = [255,255]
    cpu = N.NesMPU

    def snapshot(c):
        m = c.memory
        return (c.a, c.x, c.y, c.p & 0xef, c.sp, tuple(m.rawtags),
                bytes(m[:11]), bytes(m[0x15a:0x17b]), bytes(m[0x101+c.sp:0x200]),
                bytes(m[0x200:0x304]), N.get(m,'CurrentOAMOffset'),
                N.get(m,'CurrentBank'), N.get(m,'CurrentBankC'),
                N.get(m,'GuestOamRotationActive'), N.get(m,'RgOamRotation'),
                tuple(map(bytes, m.ram)), bytes(m[0x6b05:0x6b08]))

    def clone(c):
        m = N.fork(c.memory)
        I.C.clear(m)
        q = cpu(memory=m, pc=c.pc)
        q.a,q.x,q.y,q.p,q.sp = c.a,c.x,c.y,c.p,c.sp
        return q

    def run(z, stop, visit):
        for _ in range(25000):
            if stop(z):
                return
            visit(z)
            assert z.memory[z.pc], (hex(z.pc), z.sp)
            z.step()
        raise AssertionError(('Vector return bound', hex(z.pc)))

    def interrupt(c, kind):
        z = clone(c)
        before = snapshot(z)
        ret = z.pc, z.sp
        if kind == 'lag_FF':
            assert N.get(z.memory,'NmiDisable') == 255
            z.nmi()
        else:
            assert not z.p & 4
            z.irq()

        def visit(q):
            mins[1] = min(mins[1], q.sp)
            if kind == 'lag_FF' and not q.p & 4:
                tag = q.memory.rawtags[(q.pc-0x8000)//8192] if q.pc>=0x8000 else -1
                key = tag, q.pc
                if key not in deepest or q.sp < deepest[key].sp:
                    deepest[key] = clone(q)

        run(z, lambda q: (q.pc,q.sp)==ret, visit)
        after = snapshot(z)
        assert after == before, (kind, ret, [i for i in range(len(after)) if after[i]!=before[i]])
        assert not any(0x200<=a<0x300 or a==0x4014 for a,v in z.memory.writes)
        counts[kind] += 1

    for cursor, rotation, case, p in product([0, 236, 252], [0,252,255], ['body','fruit','reject'], [0x20,0x24]):
        m = N.fork(seed)
        I.C.clear(m)
        m.raw_page(1,3)
        m.raw_page(2,2)
        N.put(m,CurrentBank=3,CurrentBankC=2,NmiDisable=255,GuestOamRotationActive=1,
              RgOamRotation=rotation,CurrentOAMOffset=cursor)
        m.ram[2][0x200:0x210] = bytes([255])*16
        m.ram[2][0x230:0x300] = bytes([255])*208
        if case == 'fruit':
            m.ram[2][0x9a] = 1
            m.ram[2][0x434] = 1
            m.ram[2][0x42c] = 0xa4
            m.ram[2][0x420] = 96
            m.ram[2][0x428] = 80
        if case == 'reject':
            m.ram[2][0x211] |= 1
        c=cpu(memory=m,pc=proposal['labels']['DkNativeDraw'])
        c.a,c.x,c.y,c.p,c.sp = 83,7,23,p,211
        c.stPushWord(0x5aff)
        seen = set()

        def visit(z):
            key = z.pc,z.sp,z.p&4
            if key in seen or m.rawtags[1]!=3 or not any(lo<=z.pc<hi for lo,hi in proposal['source_render_extents']):
                return
            seen.add(key)
            mins[0] = min(mins[0],z.sp)
            interrupt(z,'lag_FF')
            if not z.p&4:
                interrupt(z,'IRQ')

        run(c,lambda z:z.pc==0x5b00,visit)
        assert c.sp==211 and seen
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert all(counts[k] for k in ('IRQ','lag_FF','nested_IRQ')) and mins[1]>0x7a
    result=dict(passed=True, CPU_only=True, ROM_written=False, memory_only_SHA256=P.sha(raw),
                actual_cuts=dict(counts), min_foreground_SP=mins[0], min_ISR_SP=mins[1],
                protected='AXYP/SP, live stack, full private SRAM, both PRG maps, SMC, native OAM and logical/physical allocation. No lag DMA.',
                bindings={str(p):P.sha(p.read_bytes()) for p in [Path(__file__),proposal_path,OUT/'oam-CPU.json',
                           P.R/'src/reset.s',P.R/'src/metasprite_engine.s',P.PRIVATE]})
    (OUT/'oam-IRQ.json').write_text(json.dumps(result,indent=2)+'\n')
    print(dict(counts),mins,flush=True)


if __name__=='__main__':
    main()

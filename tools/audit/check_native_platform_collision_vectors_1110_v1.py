"""Rebind the native platform admission to actual asynchronous cuts."""

from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_platform_collision_dispatch_1110_v1 as P
from check_mini_funded_actor_1108_v3 import install,registers,run,slim_fork
from check_mini_lift_admission_async_1108_v1 import final as actor_final,lag_pcs

N,R,OUT = P.N,P.R,P.OUT


class Guard(N.Bus):
    stale = None

    def __getitem__(self,at):
        if self.stale is not None and isinstance(at,int):
            assert at not in self.stale,('stale skipped transport operand read',hex(at))
        return super().__getitem__(at)

    def __setitem__(self,at,v):
        if self.stale is not None and isinstance(at,int):
            self.stale.discard(at)
        super().__setitem__(at,v)


def qualify(before_raw,after_raw):
    images = [P.P.bundle(raw) for raw in (before_raw,after_raw)]
    base_bus = N.Bus
    N.Bus = Guard
    try:
        seed = P.P.fixture(images[1],0,False,False)
        six = P.scene_seed(images[1],3,3)
    finally:
        N.Bus = base_bus
    lag,normal = lag_pcs(seed)
    counts,minimum = Counter(),[255,255]
    deepest = {}

    def clone(c, original=False):
        m = slim_fork(c.memory)
        m.stale = None
        if original:
            m.bundle = images[0]
            for i,tag in enumerate(m.rawtags[:]):
                m.raw_page(i,tag)
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def vector(c,kind):
        ret = c.pc,c.sp
        initial = P.state(clone(c))
        nmi = kind=='lag_FF'
        if nmi:
            assert N.get(c.memory,'NmiDisable')==255
        else:
            assert not c.p&4
        results = []
        for original in (False,True):
            z = clone(c,original)
            getattr(z,'nmi' if nmi else 'irq')()
            hits = 0

            def observe(q):
                nonlocal hits
                minimum[1] = min(minimum[1],q.sp)
                if nmi:
                    assert q.pc!=normal
                    hits += int(q.pc==lag)
                    if not original and not q.p&4:
                        key = (*P.point(q),q.a,q.p&1,N.get(q.memory,'SelectedCharacter'))
                        if key not in deepest or q.sp<deepest[key].sp:
                            deepest[key] = clone(q)

            run(z,lambda q:(q.pc,q.sp)==ret,observe)
            assert hits==int(nmi)
            assert not any(0x200<=at<0x304 or at==0x4014 for at,_ in z.memory.writes)
            results.append((P.state(z),z.memory.writes))
        assert results[0]==results[1],(kind,P.point(c),ret)
        actual = results[0][0]
        assert actual[:2]==initial[:2]
        assert actual[2][3:6]==initial[2][3:6],(kind,ret,'SMC, mapper or private RAM')
        assert actual[2][1][:0x104]==initial[2][1][:0x104]
        counts[kind] += 1

    def exercise(c,finish,name):
        m = c.memory
        selected = N.get(m,'SelectedCharacter')
        seen = set()
        checked_after = 0
        guarded = False
        pending = []

        def observe(q):
            nonlocal guarded,checked_after
            tag,pc = P.point(q)
            # In the fast admitted lane, require every obsolete transport
            # operand to be freshly written before any foreground use.
            if tag==128 and pc==0xb453 and selected>=11 and not N.get(m,'TimerControl'):
                m.stale = {0x162,0x16c,0x16d,0x179}
                guarded = True
            if tag==128 and pc==0xb44a and guarded:
                assert m.stale==set(),(name,m.stale)
                m.stale = None
                guarded = False
                checked_after += 1
            role = tag==128 and (P.POLICY<=pc<P.POLICY+11 or P.BRIDGE<=pc<P.BRIDGE+44)
            key = tag,pc,q.p&4
            if not role or key in seen:
                return
            seen.add(key)
            minimum[0] = min(minimum[0],q.sp)
            for kind in ('lag_FF','IRQ'):
                if kind=='IRQ' and q.p&4:
                    continue
                vector(q,kind)
                if kind not in {k for k,_ in pending}:
                    fork = clone(q)
                    getattr(fork,'nmi' if kind=='lag_FF' else 'irq')()
                    run(fork,lambda z:(z.pc,z.sp)==(q.pc,q.sp))
                    pending.append((kind,fork))

        run(c,finish,observe)
        assert seen and m.stale is None,(name,seen,m.stale)
        if selected>=11 and not N.get(m,'TimerControl'):
            assert checked_after>0,(name,selected,checked_after)
        expected = actor_final(c)
        for kind,z in pending:
            run(z,finish)
            assert actor_final(z)==expected,(name,kind)
            counts['resumed_'+kind] += 1
        counts['foreground_transport_dead_packet_rewrites'] += checked_after

    for raw,variant,where,timer,p in product((0,4,10,11,41),(0,1),
            ('contact','leftclip'),(0,1),(0x20,0x65)):
        if variant and raw!=4:
            continue
        c = P.actor_setup(seed,raw,variant,0x25,0x40,where,timer,p)
        exercise(c,P.end,(raw,variant,where,timer,p))

    # Exact reset-to-IdleLoop-to-GameLoop stack with the three actual helpers.
    idle = P.P.address(images[1],'IdleLoop')
    game_loop = P.P.address(images[1],'GameLoop')
    fixed = after_raw[16+127*8192:16+128*8192]
    jsr = bytes([0x20,idle&255,idle>>8])
    assert fixed.count(jsr)==1
    assert bytes(six[idle+9:idle+12])==bytes([0x20,game_loop&255,game_loop>>8])
    N.put(six,NmiDisable=255)
    cpu = N.NesMPU(memory=six,pc=idle)
    cpu.p,cpu.sp = 0x31,255
    cpu.stPushWord(0xe000+fixed.index(jsr)+2)
    exercise(cpu,lambda q:(q.pc,q.sp)==(idle+12,252),'real six-actor GameLoop')
    for cut in deepest.values():
        vector(cut,'nested_IRQ')
    assert all(counts[k] for k in ('IRQ','lag_FF','nested_IRQ','foreground_transport_dead_packet_rewrites'))
    assert minimum[1]>0x7a
    return dict(cuts=dict(counts),minimum_foreground_SP=minimum[0],minimum_ISR_SP=minimum[1],
                actual_lag_pc=lag,forbidden_regular_nmi_pc=normal,
                scope='Real IRQ and FF-NMI cuts on the changed collision policy and wrapper; nested audio IRQ, whole actor resume and exact six-actor native GameLoop. The unneeded intermediate packet is proven overwritten before any foreground consumption.')


def main():
    source = OUT/'proof.json'
    q = json.loads(source.read_text())
    old = P.BASE.read_bytes()
    new = install(old,q['patches'])
    assert P.P.sha(old)==P.PIN==q['parent_SHA256']
    assert P.P.sha(new)==q['expected_memory_only_SHA256']
    result = qualify(old,new)
    result.update(passed=True,parent_SHA256=P.PIN,expected_memory_only_SHA256=P.P.sha(new),
                  bindings={f.relative_to(R).as_posix():P.P.sha(f.read_bytes())
                            for f in (source,Path(__file__),R/'src/reset.s')})
    (OUT/'vectors.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result,flush=True)


if __name__=='__main__':
    main()

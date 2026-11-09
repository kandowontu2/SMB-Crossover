"""Qualify interrupt cuts in the shared native motion/box footprint."""

from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_platform_box_1110_v1 as B
from check_mini_funded_actor_1108_v3 import install,registers,run,slim_fork
from check_mini_lift_admission_async_1108_v1 import final,lag_pcs

N,R,OUT,P,D = B.N,B.R,B.OUT,B.P,B.D


class Guard(N.Bus):
    isr = False

    def __getitem__(self,at):
        if self.isr and isinstance(at,int):
            assert not 0x658<=at<0x674,('ISR read a partly built actor box',hex(at))
        return super().__getitem__(at)

    def __setitem__(self,at,v):
        if self.isr and isinstance(at,int):
            assert not 0x658<=at<0x674,('ISR wrote actor box',hex(at))
        super().__setitem__(at,v)


def qualify(before,after):
    images = [P.bundle(raw) for raw in (before,after)]
    old_bus = N.Bus
    N.Bus = Guard
    try:
        seed = P.fixture(images[1],0,False,False)
        actual = D.scene_seed(images[1],3,3)
    finally:
        N.Bus = old_bus
    lag,normal = lag_pcs(seed)
    counts,minimum = Counter(),[255,255]
    deepest = {}

    def clone(c,original=False):
        m = slim_fork(c.memory)
        if original:
            m.bundle = images[0]
            for i,tag in enumerate(m.rawtags[:]):
                m.raw_page(i,tag)
        m.isr = False
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def apply_vector(c,kind,keep=False):
        pc,sp = c.pc,c.sp
        nmi = kind=='lag_FF'
        if nmi:
            assert N.get(c.memory,'NmiDisable')==255
        else:
            assert not c.p&4
        m = c.memory
        old = D.state(c)
        m.isr = True
        getattr(c,'nmi' if nmi else 'irq')()
        saw = 0

        def watch(z):
            nonlocal saw
            minimum[1] = min(minimum[1],z.sp)
            if nmi:
                assert z.pc!=normal
                saw += z.pc==lag
                if keep and not z.p&4:
                    key = (*D.point(z),z.a,z.p&1,N.get(z.memory,'SelectedCharacter'))
                    if key not in deepest or z.sp<deepest[key].sp:
                        deepest[key] = clone(z)

        run(c,lambda q:(q.pc,q.sp)==(pc,sp),watch)
        m.isr = False
        assert saw==int(nmi)
        assert not any(0x200<=at<0x304 or at==0x4014 for at,_ in m.writes)
        after = D.state(c)
        assert old[:2]==after[:2] and old[2][3:6]==after[2][3:6]
        return after,m.writes[:]

    def pair_vector(c,kind):
        original = clone(c,original=True)
        candidate = clone(c)
        assert apply_vector(candidate,kind,keep=True)==apply_vector(original,kind),(kind,c.pc,c.sp)
        counts[kind] += 1
        return candidate

    def exercise(c,end,lane):
        seen,pending = set(),{}

        def visit(z):
            tag,pc = D.point(z)
            if tag!=154 or not (B.MOTION<=pc<B.MOTION_END or B.GATE<=pc<B.GATE+5):
                return
            key = pc,z.p&4,z.sp
            if key in seen:
                return
            seen.add(key)
            minimum[0] = min(minimum[0],z.sp)
            for kind in ('lag_FF','IRQ'):
                if kind=='IRQ' and z.p&4:
                    continue
                cut = pair_vector(z,kind)
                if kind not in pending:
                    pending[kind] = cut

        run(c,end,visit)
        assert seen,(lane,'did not reach updated code')
        for kind,cut in pending.items():
            run(cut,end)
            assert final(cut)==final(c),(lane,kind)
            counts['resumed_'+kind] += 1

    for actor,p in product(range(0x24,0x2b),(0x20,0x65)):
        c = D.actor_setup(seed,41,0,actor,0x40 if actor in (0x25,0x28) else 0,
                          'distant',0,p)
        if actor==0x24:
            for name,value in [('Enemy_State',4),('Player_Y_Position',32)]:
                if name=='Enemy_State':
                    B.set_named(c.memory,name,5,value)
                else:
                    N.put(c.memory,Player_Y_Position=value)
            for name,value in [('Enemy_State',5),('Enemy_Flag',1),('Enemy_ID',0x24),
                               ('Enemy_Y_HighPos',1),('Enemy_Y_Position',192)]:
                B.set_named(c.memory,name,4,value)
        exercise(c,D.end,(actor,p))
    for ctrl,tag,p in product((4,5,6),(0x40,0x60),(0x20,0x65)):
        c = B.cold_box(seed,5,560,577,185,ctrl,tag,p)
        N.put(c.memory,NmiDisable=255)
        exercise(c,D.end,(ctrl,tag,p))

    idle = P.address(images[1],'IdleLoop')
    game = P.address(images[1],'GameLoop')
    fixed = after[16+127*8192:16+128*8192]
    boot = bytes((0x20,idle&255,idle>>8))
    assert fixed.count(boot)==1 and bytes(actual[idle+9:idle+12])==bytes((0x20,game&255,game>>8))
    N.put(actual,NmiDisable=255)
    cpu = N.NesMPU(memory=actual,pc=idle)
    cpu.p,cpu.sp = 0x31,255
    cpu.stPushWord(0xe000+fixed.index(boot)+2)
    exercise(cpu,lambda z:(z.pc,z.sp)==(idle+12,252),'real six actor GameLoop')
    for cut in deepest.values():
        pair_vector(cut,'nested_IRQ')
    assert all(counts[k] for k in ('lag_FF','IRQ','nested_IRQ')) and minimum[1]>0x7a
    return dict(cuts=dict(counts),minimum_foreground_SP=minimum[0],minimum_ISR_SP=minimum[1],
                actual_lag_pc=lag,forbidden_regular_nmi_pc=normal,
                scope='Changed physical bank26 instruction cuts, strict real vector scratch/mapper/audio parity, resumed actors and real six-actor native stack. Actual interrupt never observes an intermediate rectangle.')


def main():
    receipt = OUT/'proof.json'
    q = json.loads(receipt.read_text())
    raw = B.BASE.read_bytes()
    after = install(raw,q['patches'])
    assert P.sha(raw)==B.PIN==q['parent_SHA256']
    assert P.sha(after)==q['expected_memory_only_SHA256']
    data = qualify(raw,after)
    data.update(passed=True,parent_SHA256=B.PIN,expected_memory_only_SHA256=P.sha(after),
                bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())
                          for p in (receipt,Path(__file__),R/'src/reset.s')})
    (OUT/'vectors.json').write_text(json.dumps(data,indent=2)+'\n')
    print(data,flush=True)


if __name__=='__main__':
    main()

"""Verify true lag NMI and IRQ across the relocated internal graphics paths."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_mini_lift_admission_async_1108_v1 as Q
import check_mini_player_graphics_visibility_1110 as G
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard


M,N,R = G.M,G.N,G.R


def vectors(before,after):
    old,new = [M.bundle(raw) for raw in (before,after)]
    previous = N.Bus
    N.Bus = StackGuard
    try:
        seed = N.fresh(new)
        mini = G.P.fixture(new,4,False,True)
    finally:
        N.Bus = previous
    lag,regular = lag_pcs(seed)
    counts = Counter()
    minimum = [255,255]
    deepest = {}
    reached = set()

    def clone(c,base=False):
        m = slim_fork(c.memory)
        if base:
            m.bundle = old
            m.raw_page(1,m.rawtags[1])
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def interrupt(c,kind):
        saved = Q.live(c)
        ret = c.pc,c.sp
        results = []
        for base in (False,True):
            z = clone(c,base)
            m = z.memory
            m.vector_floor,m.written_stack = 0x100+z.sp,set()
            skipped = N.get(m,'NmiSkipped')
            if kind=='lag_FF':
                assert N.get(m,'NmiDisable')==255
                z.nmi()
            else:
                assert not z.p&4
                z.irq()
                assert (Q.tags(z),z.pc)==(254,0x8000)
            hits = 0

            def observe(q):
                nonlocal hits
                minimum[1] = min(minimum[1],q.sp)
                if kind!='lag_FF':
                    return
                assert q.pc!=regular
                hits += q.pc==lag
                if not base and not q.p&4:
                    k = Q.tags(q),q.pc,q.a,q.p&1
                    if k not in deepest or q.sp<deepest[k].sp:
                        deepest[k] = clone(q)
                        deepest[k].memory.vector_floor = None

            run(z,lambda q:(q.pc,q.sp)==ret,observe)
            m.vector_floor = None
            actual = Q.live(z)
            if actual!=saved:
                # A lag vector can publish an already-written A shadow when
                # the interrupted farcall is just before its actual bus STA.
                assert kind=='lag_FF' and actual[0]==saved[0] and actual[2:]==saved[2:],(kind,ret)
                assert bytes(c.memory[c.pc-3:c.pc+3])==bytes.fromhex('8d45018d1551'),(kind,ret)
                assert c.a==saved[2]==actual[1][1] and saved[1][1]!=actual[1][1]
                assert actual[1][:1]+actual[1][2:]==saved[1][:1]+saved[1][2:]
                if not base:
                    counts['pending_A_map'] += 1
            assert hits==int(kind=='lag_FF')
            assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
            assert not any(at==0x4014 or 0x200<=at<0x304 for at,_ in m.writes)
            results.append((z,G.state(z),tuple(m.writes),tuple(m.ram_writes)))
        assert results[0][1:]==results[1][1:],(kind,ret)
        counts[kind] += 1
        return results[0][0]

    def exercise(c,stop,watch):
        cuts,resume = set(),[]

        def cut(z):
            if not watch(z):
                return
            k = Q.tags(z),z.pc,z.sp,z.p&4,tuple(z.memory.rawtags)
            if k in cuts:
                return
            cuts.add(k)
            reached.add(k[:2])
            minimum[0] = min(minimum[0],z.sp)
            resume.append(interrupt(z,'lag_FF'))
            if not z.p&4:
                resume.append(interrupt(z,'IRQ'))

        run(c,stop,cut)
        assert cuts
        expected = Q.final(c),bytes(c.memory[:11])
        for z in resume:
            run(z,stop)
            assert (Q.final(z),bytes(z.memory[:11]))==expected,(hex(z.pc),c.sp)
        counts['resumed'] += len(resume)

    for owner,phase in product(range(42),(0,1)):
        fields = G.sample(owner,8 if not phase else 11,phase,phase)
        fields.update(NmiDisable=255,RlVariant=phase,MarioVariant=phase*3)
        c = G.local(mini if owner==41 else seed,fields,0x80,7,19,0x21 if not phase else 0x64)
        exercise(c,lambda z:(z.pc,z.sp)==(G.STOP,224),
                 lambda z:Q.tags(z)==129 and G.ENTRY<=z.pc<G.END)

    idle,loop,core = (M.address(new,name) for name in ('IdleLoop','GameLoop','GameCoreRoutine'))
    assert bytes(seed[0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(seed[idle+9:idle+12])==bytes((0x20,loop&255,loop>>8))
    entries = {}
    c = N.NesMPU(memory=slim_fork(mini),pc=idle)
    N.put(c.memory,SelectedCharacter=41,MmDeathFlag=0,SavedJoypadBits=0x81,NmiDisable=255)
    c.sp,c.p = 255,0x31
    c.stPushWord(0xe33b)
    active = False

    def watch(z):
        nonlocal active
        tag,pc = Q.tags(z),z.pc
        if tag==254 and pc in (loop,core):
            entries[pc] = z.sp
        if (tag,pc)==(129,G.ENTRY):
            active = True
        if (tag,pc)==(254,0x83ee):
            active = False
        return active and (0x15a<=pc<0x17b or (tag==129 and G.ENTRY<=pc<G.END))

    exercise(c,lambda z:(z.pc,z.sp)==(idle+12,252),watch)
    assert entries=={loop:250,core:248} and (129,G.COMMON) in reached
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert all(counts[k] for k in ('lag_FF','IRQ','nested_IRQ','resumed')) and min(minimum)>0x7a
    return dict(cuts=dict(counts),min_SP=minimum,unique_changed_or_transport_sites=len(reached),
                actual_GameLoop_SP=250,actual_GameCore_SP=248,
                scope='Paired actual FF and IRQ compare exact live AXYP/stack/mapper/SMC, output state and hardware writes. Resume each candidate cut to the exact uninterrupted foreground result. No native route timing claim.')


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    out = cli.parse_args().output.resolve()
    assert not (out/'irq.json').exists()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    before = G.ROM.read_bytes()
    assert proof['passed'] and M.sha(before)==G.PIN==proof['parent_SHA256']
    for name,digest in proof['bindings'].items():
        assert M.sha((R/name).read_bytes())==digest,name
    after = install(before,proof['patches'])
    assert M.sha(after)==proof['expected_memory_only_SHA256']
    result = vectors(before,after)
    receipt = result|dict(passed=True,ROM_written=False,parent_SHA256=G.PIN,
                          expected_memory_only_SHA256=M.sha(after),
                          bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes())
                                    for p in (path,Path(__file__),Path(Q.__file__),R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()

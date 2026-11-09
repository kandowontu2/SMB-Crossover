"""Check actual IRQ and lag NMI across the Mini body transport and lifecycle."""

import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_box_transport_1110 as T
import check_mini_lift_admission_async_1108_v1 as Q
import check_mini_sweep_center_irq_1110 as S
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import cpu_at, memory, lag_pcs
from check_native_relative_offscreen_irq_1110 import StackGuard


D, N, M, R = T.D,T.N,T.M,T.R
FF = 'lag_FF'


def vectors(before,after):
    old,new = D.L.bundles(before,after)
    previous = N.Bus
    N.Bus = StackGuard
    try:
        mini = D.L.fixture(new,0,False,False)
        native = N.fresh(new)
    finally:
        N.Bus = previous
    idle,loop,core = (M.address(new,name) for name in ('IdleLoop','GameLoop','GameCoreRoutine'))
    lag,regular = lag_pcs(native)
    assert bytes(native[0xe339:0xe33c])==bytes((0x20,idle&255,idle>>8))
    assert bytes(native[idle+9:idle+12])==bytes((0x20,loop&255,loop>>8))
    cuts,early,states = Counter(),Counter(),{}
    minima = [255,255]
    deepest = {}

    def clone(c,baseline=False):
        m = slim_fork(c.memory)
        if baseline:
            m.bundle = old
            m.raw_page(1,m.rawtags[1])
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def interrupt(c,kind):
        snapshot = Q.live(c)
        r = bytes(c.memory[:11])
        ret = c.pc,c.sp
        variants = []
        for baseline in (False,True):
            z = clone(c,baseline)
            m = z.memory
            skipped = N.get(m,'NmiSkipped')
            m.vector_floor,m.written_stack = 0x100+z.sp,set()
            if kind==FF:
                assert N.get(m,'NmiDisable')==255
                z.nmi()
            else:
                assert not z.p&4
                z.irq()
                assert (Q.tags(z),z.pc)==(254,0x8000)
            hits = 0

            def inspect(q):
                nonlocal hits
                minima[1] = min(minima[1],q.sp)
                if kind!=FF:
                    return
                assert q.pc!=regular
                hits += q.pc==lag
                if not baseline and not q.p&4:
                    key = Q.tags(q),q.pc
                    if key not in deepest or q.sp<deepest[key].sp:
                        deepest[key] = clone(q)
                        deepest[key].memory.vector_floor = None

            run(z,lambda q:(q.pc,q.sp)==ret,inspect)
            m.vector_floor = None
            actual = Q.live(z)
            changed = [i for i,(a,b) in enumerate(zip(snapshot,actual,strict=True)) if a!=b]
            if changed:
                # FF saves the already-published shadow and can finish the
                # exact pending bus write early. A resumes on that same STA.
                assert kind==FF and changed==[1],(kind,ret,changed)
                op = bytes(c.memory[c.pc:c.pc+3])
                shadow_store = {b'\x8d\x15\x51':b'\x8d\x45\x01',
                                b'\x8d\x16\x51':b'\x8d\xa1\x7d',
                                b'\x8e\x16\x51':b'\x8e\xa1\x7d'}
                assert op in shadow_store and bytes(c.memory[c.pc-3:c.pc])==shadow_store[op],(kind,ret,op)
                window = op[1]-0x14
                bank = c.x if op[0]==0x8e else c.a
                assert snapshot[1][window]!=snapshot[window+1]==actual[1][window]==bank
                assert all(a==b for i,(a,b) in enumerate(zip(snapshot[1],actual[1])) if i!=window)
                if not baseline:
                    early[hex(op[1]+0x5100)] += 1
            assert hits==int(kind==FF) and bytes(m[:11])==r,(kind,ret)
            assert N.get(m,'NmiSkipped')==(skipped+int(kind==FF))&255
            assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in m.writes)
            variants.append((z,memory(m),tuple(m.writes),tuple(m.ram_writes)))
        assert variants[0][1:]==variants[1][1:],(kind,ret)
        cuts[kind] += 1
        return variants[0][0]

    def exercise(name,c,stop,watch):
        reached, resume = set(),[]

        def visit(z):
            if not watch(z):
                return
            key = Q.tags(z),z.pc,z.sp,z.p&4,tuple(z.memory.rawtags)
            if key in reached:
                return
            reached.add(key)
            minima[0] = min(minima[0],z.sp)
            resume.append(interrupt(z,FF))
            if not z.p&4:
                resume.append(interrupt(z,'IRQ'))

        run(c,stop,visit)
        assert reached,name

        def final(z):
            m = z.memory
            return Q.final(z),bytes(m[:11]),bytes(m[0x500:0x6c0])

        expected = final(c)
        for z in resume:
            run(z,stop)
            assert final(z)==expected,('Interrupted path continuation',name,hex(z.pc))
        cuts['resumed'] += len(resume)
        states[name] = len(reached)
        return {(tag,pc) for tag,pc,*_ in reached}

    for name,flags in (('warm',0x31),('warm_I1',0x35),('stale_full',0x31),
                       ('zero_full',0x31),('bad_ram2',0x31),('bad_ram3',0x31)):
        m = slim_fork(mini)
        S.setup(m,1511,135,13,5602,-6144,0xc1,0)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,flags
        c.stPushWord(0xe33b)
        entries = {}
        active = False

        def watch(z):
            nonlocal active
            tag,pc = Q.tags(z),z.pc
            if tag==254 and pc in (loop,core):
                entries[pc] = z.sp
            if (tag,pc)==(221,0xa703):
                active = True
                if name=='stale_full':
                    m.ram[2][0x3f0] ^= 1
                elif name=='zero_full':
                    N.put(m,FrameCounter=0)
                    m.ram[2][0x3f0] = 0
                elif name.startswith('bad_ram'):
                    m.ram[int(name[-1])][0x1fe0] = 0
            if not active:
                return False
            if (tag,pc)==(221,0xa776):
                active = False
            return (0x15a<=pc<0x17b or tag in (221,214,193,213,3) or
                    tag==254 and (0x80c2<=pc<0x80c9 or pc==0x9f4e))

        sites = exercise(name,c,lambda z:(z.pc,z.sp)==(idle+12,252),watch)
        assert entries=={loop:250,core:248} and (221,0xa776) in sites
        assert (214,0xa36a) in sites and (213,0xb0bc) in sites
        assert ((214,0xa521) in sites)==name.startswith('warm'),(name,sites)
        assert ((193,0xb0bc) in sites)==(not name.startswith('warm')),(name,sites)
        assert ((254,0x9f4e) in sites)==name.startswith('bad_ram'),(name,sites)
        assert ((3,0xa030) in sites)==(not name.startswith('bad_ram')),(name,sites)

    # The relocated lifecycle remains the same bank-86 UI ingress. Include
    # all selected owners' actual IRQ/audio policies plus the real setters.
    for owner in range(42):
        m = slim_fork(native)
        m.raw_page(1,214)
        N.put(m,CurrentBank=214,SelectedCharacter=owner,OperMode=1,OperMode_Task=3,
              GameEngineSubroutine=8,NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30)
        vars = T.VARS
        m[vars['X5BounceOwner']] = owner if owner in (5,14,16) else 0
        m[vars['Cv3Variant']] = 2 if owner==5 else 0
        for key,value in dict(MmDeathFlag=0,AreaPointer=35,X5BounceArea=35,NumberofLives=2,
                              X5BounceLife=2,WorldNumber=1,LevelNumber=2,X5BounceKey=6,
                              Player_State=1,Player_Y_Speed=3,X5BounceHi=128,CdVYHi=3).items():
            m[vars[key]] = value
        c = cpu_at(m,0xa2b8,245,0x31)
        exercise(f'lifecycle_{owner}',c,lambda z:(z.pc,z.sp)==(0x5b00,245),
                 lambda z:Q.tags(z)==214 and 0xa2b8<=z.pc<0xa36a)

    for cut in deepest.values():
        interrupt(cut,'nested_IRQ')
    assert all(cuts[name] for name in (FF,'IRQ','nested_IRQ','resumed')) and minima[1]>0x7a
    return dict(cuts=dict(cuts),foreground_sites_per_context=states,actual_FF_PC=lag,
                minimum_foreground_SP=minima[0],minimum_ISR_SP=minima[1],
                pending_map_commits=dict(early),exact_GameLoop_SP=250,exact_GameCore_SP=248)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert not (out/'irq.json').exists()
    proof = out/'proof.json'
    q = json.loads(proof.read_text())
    raw = T.BASE.read_bytes()
    assert M.sha(raw)==T.PIN==q['parent_SHA256'] and q['passed']
    for name,digest in q['bindings'].items():
        assert M.sha((R/name).read_bytes())==digest,name
    after = install(raw,q['patches'])
    assert M.sha(after)==q['expected_memory_only_SHA256']
    result = vectors(raw,after)
    result.update(passed=True,ROM_written=False,parent_SHA256=T.PIN,
                  expected_memory_only_SHA256=M.sha(after),
                  bindings={p.resolve().relative_to(R).as_posix():M.sha(p.read_bytes())
                            for p in (Path(__file__),proof,Path(Q.__file__),Path(S.__file__),R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()

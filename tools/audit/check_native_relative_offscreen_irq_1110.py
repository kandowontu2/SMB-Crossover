"""Verify real vectors, including resuming every watched shared leaf cut."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_mini_shared_offscreen_irq_1110_v1 as V
import check_mini_lift_admission_async_1108_v1 as Q
import check_native_relative_offscreen_1110 as T
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork


P,N,R = T.P,T.N,T.R


class StackGuard(N.Bus):
    vector_floor = None

    def __getitem__(self,at):
        if self.vector_floor is not None and isinstance(at,int) and 0x17b<=at<=self.vector_floor:
            assert at in self.written_stack,('Read of stale discarded stack',hex(at))
        return super().__getitem__(at)

    def __setitem__(self,at,value):
        if self.vector_floor is not None and isinstance(at,int) and 0x100<=at<0x200:
            self.written_stack.add(at)
        super().__setitem__(at,value)


def vectors(before,after):
    old,new = [P.bundle(q) for q in (before,after)]
    previous = N.Bus
    N.Bus = StackGuard
    try:
        seed = N.fresh(new)
        live = [P.fixture(new,n,False,n==6) for n in (2,6)]
    finally:
        N.Bus = previous
    lag,regular = V.lag_pcs(seed)
    counts,minima,sites,deepest = Counter(),[255,255],set(),{}

    def clone(c,base=False):
        m = slim_fork(c.memory)
        if base:
            m.bundle = old
            m.raw_page(0,m.rawtags[0])
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def interrupt(c,kind):
        snapshot = Q.live(c)
        scratch = bytes(c.memory[:11])
        ret = c.pc,c.sp
        variants = []
        for base in (False,True):
            z = clone(c,base)
            m = z.memory
            skipped = N.get(m,'NmiSkipped')
            m.vector_floor,m.written_stack = 0x100+z.sp,set()
            if kind=='lag_FF':
                assert N.get(m,'NmiDisable')==255
                z.nmi()
            else:
                assert not z.p&4
                z.irq()
                assert z.pc==0x8000 and Q.tags(z)==254
            hits = 0

            def inspect(q):
                nonlocal hits
                minima[1] = min(minima[1],q.sp)
                if kind!='lag_FF':
                    return
                assert q.pc!=regular
                hits += q.pc==lag
                if not base and not q.p&4:
                    # Keep the deepest actual context at each physical lag
                    # instruction. Each owner already gets full direct IRQ
                    # and FF checks at the foreground cuts.
                    key = Q.tags(q),q.pc
                    if key not in deepest or q.sp<deepest[key].sp:
                        deepest[key] = clone(q)
                        deepest[key].memory.vector_floor = None

            run(z,lambda q:(q.pc,q.sp)==ret,inspect)
            m.vector_floor = None
            assert hits==int(kind=='lag_FF') and Q.live(z)==snapshot,(kind,ret)
            assert bytes(m[:11])==scratch,(kind,ret,'native scratch')
            assert N.get(m,'NmiSkipped')==(skipped+int(kind=='lag_FF'))&255
            variants.append((z,V.memory(m),tuple(m.writes),tuple(m.ram_writes)))
        assert variants[0][1:]==variants[1][1:],(kind,ret)
        counts[kind] += 1
        return variants[0][0]

    def exercise(c,sp):
        seen,resume = set(),[]
        stop = lambda z:(z.pc,z.sp)==(V.STOP,sp)

        def visit(z):
            pc = z.pc
            if Q.tags(z)!=254 or not any(lo<=pc<hi for lo,hi in T.SPANS):
                return
            key = pc,z.sp,z.p&4
            if key in seen:
                return
            seen.add(key)
            sites.add(pc)
            minima[0] = min(minima[0],z.sp)
            resume.append(interrupt(z,'lag_FF'))
            if not z.p&4:
                resume.append(interrupt(z,'IRQ'))

        run(c,stop,visit)
        assert seen
        def result(z):
            return Q.final(z),bytes(z.memory[:11]),bytes(z.memory[0x500:0x6c0])
        expected = result(c)
        for z in resume:
            run(z,stop)
            assert result(z)==expected,('Resumed original control path',sp,z.pc)
            counts['resumed'] += 1

    edges = ((43,0,42,1,192,0),(43,0,42,1,39,0),(43,0,42,1,39,1),
             (43,0,42,1,50,0),(43,0,42,1,43,1),(255,255,254,0,5,0))
    # Every audio owner gets a real lag handler during shared scratch use.
    # The leaf input values include every horizontal default and near lane.
    for who in range(42):
        for pc in (T.ENTRIES['RelativeEnemyPosition'],0x8b1a):
            m = slim_fork(seed)
            left,lpage,right,rpage,x,page = edges[who%len(edges)]
            N.put(m,SelectedCharacter=who,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
                  NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,
                  ScreenLeft_X_Pos=left,ScreenRight_X_Pos=right,ScreenLeft_PageLoc=lpage,
                  ScreenRight_PageLoc=rpage,Enemy_X_Position=x,Enemy_PageLoc=page,
                  Enemy_Y_Position=184,Enemy_Y_HighPos=1)
            exercise(V.cpu_at(m,pc,232,0x21,x=int(pc==0x8b1a)),232)

    # The resident helper paths also execute on real linked GameLoop stacks.
    game = P.address(new,'GameLoop')
    for pristine,edge,flags in product(live,('ordinary','right','left'),(0x21,0x25)):
        m = slim_fork(pristine)
        if edge!='ordinary':
            m[P.address(new,'Enemy_X_Position')] = 248 if edge=='right' else 0
        N.put(m,SavedJoypadBits=193,SavedJoypad1Bits=193,NmiDisable=255,VRAM_Buffer1_Offset=0)
        exercise(V.cpu_at(m,game,252,flags,x=0,y=0),252)
        counts['actual_GameLoop'] += 1

    for cut in deepest.values():
        interrupt(cut,'nested_IRQ')
    assert counts['nested_IRQ'] and min(minima)>0x7a and all(lo in sites for lo,hi in T.SPANS)
    return dict(cuts=dict(counts),minimum_foreground_SP=minima[0],minimum_ISR_SP=minima[1],
                reached_foreground_sites=sorted(sites),raw_owners=42,actual_FF_PC=lag)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    path = out/'proof.json'
    proof = json.loads(path.read_text())
    before = T.BASE.read_bytes()
    assert proof['passed'] and P.sha(before)==T.PIN==proof['parent_SHA256']
    for file,digest in proof['bindings'].items():
        assert P.sha(Path(file).read_bytes())==digest,file
    after = install(before,proof['patches'])
    assert P.sha(after)==proof['expected_memory_only_SHA256']
    result = vectors(before,after)
    q = result|dict(passed=True,ROM_written=False,parent_SHA256=T.PIN,
                    expected_memory_only_SHA256=P.sha(after),
                    bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in
                              (Path(__file__),Path(V.__file__),Path(Q.__file__),path,R/'src/reset.s')})
    (out/'irq.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='reached_foreground_sites'}),flush=True)


if __name__=='__main__':
    main()

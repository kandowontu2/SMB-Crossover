"""Qualify exact bounds-tail continuation and real interrupt cuts."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_actor_bounds_1110 as B
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, cpu_at, lag_pcs


D, P, N, M = B.D, B.P, B.N, B.M
IRQ_DELAY = (254,0x8026)
IRQ_TAIL = bytes.fromhex('a9002403eaeaea8a4a4a4a0d37018e05208d06208e3701eaeaeaeaea68aa6840')


class IrqBoundsBus(B.BoundsBus):
    def __getitem__(self,at):
        if at==3 and at in self.bounds_pending and self.bounds_pc==IRQ_DELAY:
            # The fixed scanline delay uses BIT only for three cycles.
            # TXA/LSRs replace its NZ; no later IRQ branch observes V.
            self.dead_delay_reads+=1
            return B.StackGuard.__getitem__(self,at)
        return super().__getitem__(at)


def watch(m):
    m.kills,m.hits,m.in_bounds=Counter(),Counter(),False
    m.bounds_pc=(0,0)
    m.dead_delay_reads=0


def snapshot(c):
    m=c.memory
    raw=lambda a,b: bytes(list.__getitem__(m,slice(a,b)))
    return (registers(c,0xef),c.pc,tuple(m.rawtags),live_stack(c),raw(0,11),raw(0x15a,0x17b),
            raw(0x200,0x304),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'))


def interrupt(c,kind,lag,regular,observe=None):
    m=c.memory
    before=snapshot(c)
    stop=c.pc,c.sp
    skipped=N.get(m,'NmiSkipped')
    m.vector_floor,m.written_stack=0x100+c.sp,set()
    if kind=='IRQ':
        assert not c.p&4
        c.irq()
        assert D.bank_pc(c)==(254,0x8000)
    else:
        assert N.get(m,'NmiDisable')==(255 if kind=='FF' else 0)
        c.nmi()
    hits=Counter()

    def visit(q):
        m.bounds_pc=D.bank_pc(q)
        if q.pc in (lag,regular):
            hits[q.pc]+=1
        if observe:
            observe(q)

    run(c,lambda q:(q.pc,q.sp)==stop,visit)
    m.vector_floor=None
    assert hits[lag]==int(kind=='FF') and hits[regular]==int(kind=='NMI')
    assert N.get(m,'NmiSkipped')==(skipped+int(kind=='FF'))&255
    after=snapshot(c)
    differences=[i for i,(a,b) in enumerate(zip(before,after,strict=True)) if a!=b]
    if kind=='NMI':
        assert set(differences)<={4,5,6}, (kind,differences)
    else:
        assert not differences,(kind,differences)


def prepare(seed,scene):
    m=B.scene_seed(slim_fork(seed),scene)
    watch(m)
    M.controls(m,scene['keys'])
    return cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)


def vector_cuts(images,seeds,scenes,lag,regular):
    counts,depths,sites=Counter(),[255,255],set()
    low={}

    def compare(c,kind):
        results=[]
        for index,bundle in enumerate(images):
            q=fork(c,bundle)

            def inspect(z):
                depths[1]=min(depths[1],z.sp)
                if index==1 and kind=='FF' and not z.p&4:
                    key=N.get(z.memory,'SelectedCharacter')
                    if key not in low or z.sp<low[key].sp:
                        low[key]=fork(z)
                        low[key].memory.vector_floor=None

            interrupt(q,kind,lag,regular,inspect)
            pending=q.memory.bounds_pending
            q.memory.bounds_pending=frozenset()
            results.append((semantic(q),q.memory.writes[:],q.processorCycles,pending))
        assert results[0]==results[1],(D.bank_pc(c),kind)
        counts[kind]+=1
        counts['inert_IRQ_BIT_reads']+=q.memory.dead_delay_reads-c.memory.dead_delay_reads

    for owner,scene in product(seeds,scenes):
        c=prepare(seeds[owner][1],scene)
        seen=set()

        def visit(q):
            B.trace_bounds(q)
            tag,pc=D.bank_pc(q)
            if tag!=128 or not (B.POSE<=pc<B.END or pc in (0xa493,0xb44d,0xb450,B.STOCK)):
                return
            mark=pc,q.sp,q.p&4,q.memory.bounds_pending
            if mark in seen:
                return
            seen.add(mark)
            sites.add(pc)
            depths[0]=min(depths[0],q.sp)
            compare(q,'FF')
            if not q.p&4:
                compare(q,'IRQ')

        run(c,lambda q:(q.pc,q.sp)==(STOP,252),visit)
        assert seen
        compare(c,'NMI')
    for c in low.values():
        compare(c,'IRQ')
        counts['nested_IRQ']+=1
    assert len(low)==len(seeds) and {B.RETURN,B.TAIL,B.FAST}<=sites
    return dict(cuts=dict(counts),site_PCs=sorted(sites),minimum_SP=depths)


def paired_resumes(images,seeds,scenes,lag,regular):
    rows=[]
    for owner,scene,pc,kind in product(seeds,scenes,(0xa493,0xb44d),('FF','IRQ','NMI')):
        if pc==0xb44d and (kind=='NMI' or all(r['id']!=37 for r in scene['actors'])):
            continue
        cpus=[]
        cuts=[]
        for side,seed in enumerate(seeds[owner]):
            c=prepare(seed,scene)
            visit=B.trace_bounds if side else None
            stop=lambda q:(q.pc,q.sp)==(STOP,252)
            if kind!='NMI':
                run(c,lambda q:D.bank_pc(q)==(128,pc),visit)
                interrupt(c,kind,lag,regular)
            run(c,stop,visit)
            if kind=='NMI':
                cuts.append(sorted(c.memory.bounds_pending))
                interrupt(c,kind,lag,regular)
            cpus.append(c)
        remaining=B.state(*cpus)
        # Probe the following frame with the actual post-NMI RAM, preserving
        # the pending-byte watcher instead of resetting the temporary.
        if kind=='NMI':
            for side,c in enumerate(cpus):
                m=c.memory
                m.writes.clear()
                m.ram_writes.clear()
                m.ppu_log.clear()
                M.controls(m,0)
                c=cpu_at(m,P.address(m.bundle,'GameLoop'),252,0x21,x=0,y=0)
                run(c,lambda q:(q.pc,q.sp)==(STOP,252),B.trace_bounds if side else None)
                cpus[side]=c
            B.state(*cpus)
        rows.append(dict(owner=owner,actor_count=sum(r['flag']==1 for r in scene['actors']),
                         tail_PC=pc,vector=kind,remaining=remaining,published_watch=cuts))
    return rows


def vectors(before,after):
    images=[P.bundle(q) for q in (before,after)]
    for raw in (before,after):
        D.check_span(raw,126,0x8024,IRQ_TAIL)
    old=B.BoundsBus
    B.BoundsBus=IrqBoundsBus
    try:
        seeds=B.cold_pair(images,(0,2,25,32,41))
    finally:
        B.BoundsBus=old
    scenes=[json.loads(p.read_text())['scene'] for p in (B.PEAK,B.LATE)]
    lag,regular=lag_pcs(seeds[41][1])
    result=vector_cuts(images,seeds,scenes,lag,regular)
    print('Vector cuts',result,flush=True)
    result['paired_GameLoop_resumes']=paired_resumes(images,seeds,scenes,lag,regular)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    raw=B.ROM.read_bytes()
    cpu=args.output/'proof.json'
    q=json.loads(cpu.read_text())
    assert P.sha(raw)==q['parent_SHA256']==B.PIN
    image=install(raw,q['patches'])
    assert P.sha(image)==q['expected_memory_only_SHA256']
    result=vectors(raw,image)
    files=Path(__file__),Path(B.__file__),cpu,B.R/'src/reset.s'
    result.update(passed=True,parent_SHA256=B.PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
                  bindings={str(p):P.sha(p.read_bytes()) for p in files})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Paired full resumes',len(result['paired_GameLoop_resumes']),flush=True)


if __name__=='__main__':
    main()

"""Exercise actual IRQ and NMI entry and native resume through enemy pairs."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_enemy_ordinary_dispatch_irq_1110 as IRQ
import check_native_enemy_pair_offsets_1110 as Pair
from check_mini_funded_actor_1108_v3 import install, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import lag_pcs


Q, N, P, D, R = Pair.Q,Pair.N,Pair.P,Pair.D,Pair.R
OLD_CALL = 0x991c


def return_pc(c):
    m = c.memory
    return m[0x101+c.sp]+256*m[0x102+c.sp]+1


def vectors(before,after,labels):
    images = [P.bundle(q) for q in (before,after)]
    seeds = Q.cold(images)
    lag,normal = lag_pcs(seeds[41][1])
    counts, sites, nested = Counter(),set(),{}
    minima = [255,255]

    def observe(c,kind,owner):
        minima[1] = min(minima[1],c.sp)
        if kind!='FF' or c.p&4:
            return
        key = owner,tuple(c.memory.rawtags)
        if key not in nested or c.sp<nested[key].sp:
            nested[key] = fork(c)
            nested[key].memory.vector_floor = None

    def inject(c,kind,owner,mirror=None,collect=False):
        a = fork(c)
        b = fork(c,mirror) if mirror is not None else None
        pair = [a] if b is None else [a,b]
        results = []
        for i,z in enumerate(pair):
            m = z.memory
            if kind=='normal':
                N.put(m,NmiDisable=0)
            m.writes.clear()
            m.ram_writes.clear()
            m.ppu_log.clear()
            visit = (lambda q:observe(q,kind,owner)) if i==0 and collect else None
            cycles = IRQ.interrupt(z,kind,lag,normal,visit)
            results.append((cycles,Pair.state(z)))
        if b is not None:
            assert results[0]==results[1],(D.bank_pc(c),kind,owner)
        return a

    # The old and new paths have different instruction locations. At each
    # real cut use the other linked image as a handler oracle only. Resume
    # the foreground in its own image after the actual handler returns.
    for owner,side,overlap in product((0,25,41),(0,1),(False,True)):
        c = Pair.actor_fixture(seeds[owner][side],slot=5,eid=0,prior=6,
                               first=(103,155,117,171),
                               second=(113,155,129,171) if overlap else (134,155,150,171),
                               state=0x80 if overlap else 0)
        seen = set()
        def visit(z):
            tag,pc = D.bank_pc(z)
            if tag!=254 or not (Pair.ENTRY<=pc<Pair.END or pc in (Pair.BOX,Pair.END)):
                return
            key = pc,z.sp,z.p&4
            if key in seen:
                return
            seen.add(key)
            sites.add((side,pc))
            minima[0] = min(minima[0],z.sp)
            for kind in ('FF','IRQ','normal'):
                if kind=='IRQ' and z.p&4 or kind=='normal' and pc!=Pair.ENTRY:
                    continue
                resume = inject(z,kind,owner,images[1-side],collect=side==1)
                run(resume,Pair.at_join)
                counts[kind]+=1
        run(c,Pair.at_join,visit)
        assert seen

    resumes = []
    for owner,mode,kind in product((0,2,25,32,41),('dispatch','box'),('FF','IRQ','normal')):
        pairs = []
        for side,seed in enumerate(seeds[owner]):
            c = Q.Edge.prepare(seed,Q.read_scene(Q.LATE),False)
            pair_call = OLD_CALL if side==0 else labels['PairCoreCall']
            if mode=='dispatch':
                pred = lambda z:D.bank_pc(z)==(254,Pair.ENTRY)
            else:
                pred = lambda z:D.bank_pc(z)==(254,Pair.BOX) and return_pc(z)==pair_call+3
            run(c,pred)
            resumed = inject(c,kind,owner)
            hardware = IRQ.hardware(resumed)
            run(resumed,Q.at_end)
            pairs.append((Q.state(resumed),hardware))
        assert pairs[0]==pairs[1],(owner,mode,kind)
        resumes.append([owner,mode,kind])

    for c in nested.values():
        inject(c,'IRQ',N.get(c.memory,'SelectedCharacter'),images[0])
        counts['nested_IRQ']+=1
    assert all(counts[kind] for kind in ('FF','IRQ','normal','nested_IRQ')) and minima[1]>0x7a
    return dict(cuts=dict(counts),site_PCs=sorted(sites),minimum_SP=minima,paired_GameLoop_resumes=resumes,
                actual_lag_PC=lag,actual_normal_PC=normal)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    path = args.output/'proof-v2.json'
    proof = json.loads(path.read_text())
    before = Q.BASE.read_bytes()
    assert proof['passed'] and proof['parent_SHA256']==P.sha(before)==Q.PIN
    for file,digest in proof['bindings'].items():
        assert P.sha(Path(file).read_bytes())==digest,file
    after = install(before,proof['patches'])
    assert P.sha(after)==proof['expected_memory_only_SHA256']
    report = vectors(before,after,proof['labels'])
    inputs = (Path(__file__),path,R/'src/reset.s',R/'src/game.s')
    report.update(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(after),ROM_written=False,
                  bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in inputs})
    (args.output/'irq-v2.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['cuts'],report['minimum_SP'],flush=True)


if __name__=='__main__':
    main()

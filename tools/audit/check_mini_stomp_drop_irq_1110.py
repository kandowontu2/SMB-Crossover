"""Resume the real stomp path through IRQ and NMI around the no-drop leaf."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_mini_stomp_drop_1110 as T
from check_mini_funded_actor_1108_v3 import install, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, lag_pcs


D,P,N,Q,R,Audio=T.D,T.P,T.N,T.Q,T.R,T.Audio


def vectors(before,after,kernel=Q.KERNEL,kernel_sha=Q.KERNEL_PIN):
    images,seeds,scene=T.with_seeds(before,after,kernel,kernel_sha,owners=(41,))
    sites=Audio.Shadow.copies(before)
    assert Audio.Shadow.copies(after)==sites
    lag,regular=lag_pcs(seeds[41][1])
    cuts,pc_set,deepest,copy_count=Counter(),set(),{},Counter()
    minima=[255,255]

    def compare(c,kind,role,nested=False):
        outputs=[]
        for side,im in enumerate(images):
            z=fork(c,im)

            def visit(q):
                minima[1]=min(minima[1],q.sp)
                if side and kind=='FF' and not q.p&4 and (role not in deepest or q.sp<deepest[role].sp):
                    deepest[role]=fork(q)
                    deepest[role].memory.vector_floor=None

            copied=Audio.trace(z,sites,kind,lag,regular,visit)
            z.memory.shadow_watch=False
            outputs.append((Audio.T.snapshot(z),z.memory.writes[:],copied,z.processorCycles))
        assert outputs[0]==outputs[1],(D.bank_pc(c),kind,role)
        cuts['nested_IRQ' if nested else kind]+=1
        copy_count[role]+=sum(map(len,copied))

    for owner,eid in ((41,6),(41,7),(0,6),(2,6),(25,6)):
        c=T.begin(seeds[41][1],scene)
        N.put(c.memory,SelectedCharacter=owner)
        c.memory[0x17]=eid
        visited=set()

        def visit(q):
            tag,pc=D.bank_pc(q)
            if tag!=194 or not (T.WORKER<=pc<T.END or pc==T.CALLER):
                return
            key=pc,q.sp,q.p&4
            if key in visited:
                return
            visited.add(key)
            pc_set.add(pc)
            minima[0]=min(minima[0],q.sp)
            compare(q,'FF',(owner,eid))
            if not q.p&4:
                compare(q,'IRQ',(owner,eid))

        run(c,lambda q:D.bank_pc(q)==(194,T.JOIN),visit)
        assert visited
        compare(c,'FF',(owner,eid))
        compare(c,'IRQ',(owner,eid))
    for role,c in deepest.items():
        compare(c,'IRQ',role,True)

    paired=[]
    for phase,cut,kind in product((0,7),('call','join'),('FF','IRQ')):
        rows=[]
        for seed in seeds[41]:
            c=T.begin(seed,dict(scene,frame=scene['frame']+phase))
            join=lambda z:D.bank_pc(z)==(194,T.JOIN)
            stop=lambda z:(z.pc,z.sp)==(STOP,252)
            if cut=='join':
                run(c,join)
            packet=T.raw_packet(c.memory)
            copied=Audio.trace(c,sites,kind,lag,regular)
            if cut=='call':
                Audio.resume(c,join)
            # At the real old/new common continuation only packet bytes
            # differ. Monitor their first overwrite through the score call.
            c.memory.taint.update({at:at for at in T.PACKET})
            Audio.resume(c,stop)
            c.memory.shadow_watch=False
            initial=T.game_end(c)
            publication_copies=Audio.trace(c,sites,'NMI',lag,regular)
            c.memory.shadow_watch=False
            rows.append((initial,Audio.T.snapshot(c),packet,list(map(len,copied)),
                         list(map(len,publication_copies))))
        assert rows[0][:2]==rows[1][:2],(phase,cut,kind,rows[0][2:],rows[1][2:])
        assert (rows[0][2]==rows[1][2])==(cut=='call')
        paired.append(dict(phase=phase,cut=cut,vector=kind,packet=[row[2] for row in rows],
                           vector_copies=[row[3] for row in rows],normal_NMI_copies=[row[4] for row in rows]))
    return dict(cuts=dict(cuts),minimum_SP=minima,sites=sorted(pc_set),paired_resumes=paired,
                copy_counts=[[role,n] for role,n in sorted(copy_count.items())])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    prior=args.output/'proof.json'
    q=json.loads(prior.read_text())
    raw=T.ROM.read_bytes()
    assert P.sha(raw)==q['parent_SHA256']==T.PIN
    image=install(raw,q['patches'])
    assert P.sha(image)==q['expected_memory_only_SHA256']
    result=vectors(raw,image)
    refs=(Path(__file__),Path(T.__file__),Path(Audio.__file__),prior,T.ROM,Q.KERNEL,R/'src/reset.s')
    result.update(passed=True,parent_SHA256=T.PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
                  bindings={str(p):P.sha(p.read_bytes()) for p in refs})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['cuts'],result['minimum_SP'],len(result['paired_resumes']),flush=True)


if __name__=='__main__':
    main()

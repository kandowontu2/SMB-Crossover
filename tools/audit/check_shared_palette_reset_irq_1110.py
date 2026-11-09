"""Exercise real IRQ, FF and audio SMC shadows on shared palette routes."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

import check_native_actor_bounds_irq_1110 as I
import check_shared_draw_retarget_irq_1110 as Shadow
import check_shared_palette_reset_1110 as T
from check_mini_funded_actor_1108_v3 import install, run
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, lag_pcs


B,D,P,N,Q,R=T.B,T.D,T.P,T.N,T.Q,T.R
MODES=((0,0,True),(2,1,True),(2,0,True),(24,0,True),(25,0,True),(25,0,False),
       (32,0,True),(41,0,True))
STACK_LOADS={(202,pc):addr for pc,addr in zip(range(0xbd1b,0xbd2f,4),
                                            (0x16a,0x16c,0x16d,0x162,0x179),strict=True)}


class PaletteBus(Shadow.DrawBus):
    def __getitem__(self,at):
        if self.shadow_watch and isinstance(at,int) and at in self.taint and STACK_LOADS.get(self.point)==at:
            self.stack_copies.append((self.point,at))
            return Shadow.StackGuard.__getitem__(self,at)
        return super().__getitem__(at)


def packet(m):
    return tuple(list.__getitem__(m,i) for i in T.PACKET)


def trace(c,sites,kind,lag,regular,observe=None):
    m=c.memory
    m.copy_sites,m.transports,m.transfer,m.stack_copies=sites,[],None,[]
    m.taint={addr:addr for addr in Shadow.SAVED}
    m.shadow_watch=True

    def visit(z):
        m.point=D.bank_pc(z)
        if observe:
            observe(z)

    I.interrupt(c,kind,lag,regular,visit)
    assert m.transfer is None
    m.taint={addr:origin for addr,origin in m.taint.items() if addr in Shadow.SHADOW}
    return list(m.transports),list(m.stack_copies)


def resume(c,point):
    def visit(z):
        z.memory.point=D.bank_pc(z)

    run(c,point,visit)


def vectors(before,after,kernel=Q.KERNEL,kernel_sha=Q.KERNEL_PIN):
    sites=Shadow.copies(before)
    assert Shadow.copies(after)==sites
    for raw in (before,after):
        D.check_span(raw,74,0xbd1b,bytes.fromhex('ad6a0148ad6c0148ad6d0148ad620148ad790148'))
        D.check_span(raw,74,0xbd5f,bytes.fromhex('688d7901688d6201688d6d01688d6c01688d6a01'))
        D.check_span(raw,118,0xae1f,bytes.fromhex('0848ad0260c919d003ee2e5c682860'))
    old=B.BoundsBus
    B.BoundsBus=PaletteBus
    try:
        images,seeds,scene=T.with_seeds(before,after,kernel,kernel_sha)
    finally:
        B.BoundsBus=old
    lag,regular=lag_pcs(seeds[41][1])
    counts,deep,pcs,shadow_reads=Counter(),{},set(),Counter()
    minimum=[255,255]

    def compare(c,kind,role,nested=False):
        rows=[]
        for side,b in enumerate(images):
            z=fork(c,b)

            def observe(q):
                minimum[1]=min(minimum[1],q.sp)
                if side and kind=='FF' and not q.p&4 and (role not in deep or q.sp<deep[role].sp):
                    deep[role]=fork(q)
                    deep[role].memory.vector_floor=None

            z.memory.shadow_watch=False
            transport=trace(z,sites,kind,lag,regular,observe)
            z.memory.shadow_watch=False
            rows.append((T.snapshot(z),z.memory.writes[:],transport,z.memory.taint,z.processorCycles))
        assert rows[0]==rows[1],(kind,role,D.bank_pc(c))
        counts['nested_IRQ' if nested else kind]+=1
        shadow_reads[role]+=sum(map(len,transport))

    for mode,side in product(MODES,range(2)):
        owner,alt,auth=mode
        seed=seeds.get(owner,seeds[0])[side]
        c=T.take_context(seed,scene)
        T.set_route(c,*mode,0x23,0x21)
        seen=set()

        def visit(z):
            tag,pc=D.bank_pc(z)
            if not (tag==207 and T.ENTRY<=pc<T.END or pc in (0x15a,0x161,0xa54c,0xaa21)):
                return
            key=tag,pc,z.sp,packet(z.memory)
            if key in seen:
                return
            seen.add(key)
            pcs.add((side,tag,pc))
            minimum[0]=min(minimum[0],z.sp)
            compare(z,'FF',mode)
            if not z.p&4:
                compare(z,'IRQ',mode)

        run(c,lambda z:D.bank_pc(z)==(254,T.JOIN),visit)
        assert seen
    for role,c in deep.items():
        compare(c,'IRQ',role,True)

    resumes=[]
    for mode,kind in product(MODES,('FF','IRQ','NMI')):
        owner=mode[0]
        pair=[]
        for seed in seeds.get(owner,seeds[0]):
            c=T.take_context(seed,scene)
            T.set_route(c,*mode,0x23,0x21)
            stop=lambda z:(z.pc,z.sp)==(STOP,252)
            if kind=='NMI':
                run(c,stop)
            else:
                run(c,lambda z:z.pc==0x161 and packet(z.memory)[2:] in (
                    (0x21,0xaa,packet(z.memory)[4]),(0x4c,0xa5,packet(z.memory)[4]),
                    (0x4f,0xbf,packet(z.memory)[4]),(0xd3,0xbc,packet(z.memory)[4])))
            payload=packet(c.memory)
            transport=trace(c,sites,kind,lag,regular)
            resume(c,stop)
            c.memory.shadow_watch=False
            pair.append((T.snapshot(c),payload,list(map(len,transport)),tuple(sorted(c.memory.taint))))
        assert pair[0][0]==pair[1][0],(mode,kind,pair[0][1:],pair[1][1:])
        resumes.append(dict(mode=mode,vector=kind,packets=[row[1] for row in pair],
                            shadow_copies=[row[2] for row in pair],retained=[row[3] for row in pair]))
    assert any(copies for mode,copies in shadow_reads.items() if mode[0] in (2,25))
    return dict(cuts=dict(counts),minimum_SP=minimum,sites=sorted(pcs),paired_GameLoop_resumes=resumes,
                tracked_shadow_transports=[[mode,n] for mode,n in sorted(shadow_reads.items())])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    prior=args.output/'proof.json'
    q=json.loads(prior.read_text())
    raw=Q.ROM.read_bytes()
    assert P.sha(raw)==q['parent_SHA256']==Q.PIN
    image=install(raw,q['patches'])
    assert P.sha(image)==q['expected_memory_only_SHA256']
    result=vectors(raw,image)
    files=(Path(__file__),Path(T.__file__),Path(Shadow.__file__),prior,Q.ROM,Q.KERNEL,R/'src/reset.s',
           R/'src/smb2_roster_audio_host_v8.s',R/'src/smb2_roster_core.s')
    result.update(passed=True,parent_SHA256=Q.PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
                  bindings={str(p):P.sha(p.read_bytes()) for p in files})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['cuts'],result['tracked_shadow_transports'],len(result['paired_GameLoop_resumes']),flush=True)


if __name__=='__main__':
    main()

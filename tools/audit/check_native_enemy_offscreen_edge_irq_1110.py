"""Rebind the edge leaf to 76bd and exercise real native/SMB2 IRQ cuts."""

import argparse
from collections import Counter
from contextlib import contextmanager
from itertools import product
import json
from pathlib import Path

import check_native_actor_bounds_irq_1110 as I
import check_native_enemy_offscreen_edge_1110 as E
from check_mini_funded_actor_1108_v3 import install, run
from check_mini_inactive_weapon_gate_1110_v1 import semantic
from check_mini_inactive_weapon_gate_irq_1110_v1 import fork
from check_mini_shared_offscreen_irq_1110_v1 import STOP, lag_pcs


B,D,P,N,M,R=E.B,E.D,E.P,E.N,E.M,E.R
ROM=R/'build/mini-lift-afterbg-audio-bounds-native-1110/candidate.nes'
PIN='76bd6772112ec63d086865210f4e20f62f59156d182136f23bd627db0df3d811'
KERNEL=R/'build/mini-lift-seen-fast-1110/kernel.bin'
KERNEL_PIN='8f014397d7f3934fd462a5785acd898cd92207b99ead5fa050f66a2a951a50ed'
SMB2=(246,0xbd19)
OWNERS=(0,2,25,32,41)


@contextmanager
def cold_kernel(kernel,kernel_sha):
    old=(B.KERNEL,B.KERNEL_PIN)
    B.KERNEL,B.KERNEL_PIN=kernel,kernel_sha
    try:
        yield
    finally:
        B.KERNEL,B.KERNEL_PIN=old


def whole(before,after,kernel=KERNEL,kernel_sha=KERNEL_PIN):
    with cold_kernel(kernel,kernel_sha):
        return E.whole(before,after)


def prepare(seed,scene,held):
    c=I.prepare(seed,scene)
    if held:
        slot=2
        run(c,lambda q:D.bank_pc(q)==(128,0xa458) and q.x==slot)
        m=c.memory
        assert N.get(m,'SelectedCharacter')==25 and N.get(m,'Enemy_Flag',slot)==1
        x=(m[0x071d]<<8)+m[0x071f]+249
        # Set a private source-owned carried actor at the live native ingress
        # after the ordinary SMB2 body update has already run this frame.
        for addr,value in ((0x5c04,1),(0x5c14,7),(0x5c79,slot),(0x5c01,x&255),
                           (0x5c11,x>>8),(0x5c0b,184),(0x5c1b,0)):
            m[addr]=value
    c.memory.writes.clear()
    c.memory.ram_writes.clear()
    c.memory.ppu_log.clear()
    return c


def vectors(before,after,kernel=KERNEL,kernel_sha=KERNEL_PIN):
    images=[P.bundle(q) for q in (before,after)]
    with cold_kernel(kernel,kernel_sha):
        seeds=B.cold_pair(images,OWNERS)
    lag,regular=lag_pcs(seeds[41][1])
    scene=json.loads(E.PEAK.read_text())['scene']
    sites,counts,deepest=set(),Counter(),{}
    minimum=[255,255]

    def compare(c,kind,role):
        rows=[]
        for side,image in enumerate(images):
            q=fork(c,image)

            def observe(z):
                minimum[1]=min(minimum[1],z.sp)
                key=role,N.get(z.memory,'SelectedCharacter')
                if side and kind=='FF' and not z.p&4 and (key not in deepest or z.sp<deepest[key].sp):
                    deepest[key]=fork(z)
                    deepest[key].memory.vector_floor=None

            I.interrupt(q,kind,lag,regular,observe)
            rows.append((semantic(q),q.memory.writes[:],q.processorCycles))
        assert rows[0]==rows[1],(kind,role,D.bank_pc(c))
        counts[role,kind]+=1

    for owner,held in (*((n,False) for n in OWNERS),(25,True)):
        c=prepare(seeds[owner][1],scene,held)
        seen=set()
        packet=False

        def visit(q):
            nonlocal packet
            tag,pc=D.bank_pc(q)
            if (tag,pc)==SMB2:
                packet=True
            if not (tag==128 and E.ENTRY<=pc<E.END or (tag,pc)==SMB2):
                return
            role='SMB2_owned' if packet and q.x==2 else 'ordinary'
            mark=(tag,pc,q.sp,q.p&4,role)
            if mark in seen:
                return
            seen.add(mark)
            sites.add((tag,pc))
            minimum[0]=min(minimum[0],q.sp)
            compare(q,'FF',role)
            if not q.p&4:
                compare(q,'IRQ',role)

        run(c,lambda q:(q.pc,q.sp)==(STOP,252),visit)
        assert packet==held and seen,(owner,held,packet)

    assert counts['SMB2_owned','FF'] and counts['ordinary','FF']
    for (role,_),c in deepest.items():
        compare(c,'IRQ','nested_'+role)

    resumes=[]
    for (owner,held),kind in product((*((n,False) for n in OWNERS),(25,True)),('FF','IRQ')):
        pair=[]
        for seed in seeds[owner]:
            c=prepare(seed,scene,held)
            stop=lambda q:(q.pc,q.sp)==(STOP,252)
            hit=SMB2 if held else (128,E.ENTRY)
            run(c,lambda q:D.bank_pc(q)==hit)
            if held:
                run(c,lambda q:D.bank_pc(q)==(128,E.ENTRY))
            I.interrupt(c,kind,lag,regular)
            run(c,stop)
            m=c.memory
            pair.append((semantic(c),bytes(m[D.SMC]),[(a,v) for a,v in m.writes if 0x200<=a<0x300]))
        assert pair[0]==pair[1],(owner,held,kind)
        resumes.append(dict(owner=owner,SMB2_owned=held,vector=kind))
    return dict(cuts=[[role,kind,n] for (role,kind),n in sorted(counts.items())],
                site_PCs=sorted(sites),minimum_SP=minimum,paired_GameLoop_resumes=resumes)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    prior=args.output/'proof.json'
    proof=json.loads(prior.read_text())
    raw=ROM.read_bytes()
    assert P.sha(raw)==PIN and proof['parent_SHA256']==B.PIN and proof['passed']
    callers=E.census(raw)
    image=install(raw,proof['patches'])
    direct=E.direct(raw,image)
    assert direct==proof['leaf']
    loops=whole(raw,image)
    result=vectors(raw,image)
    files=Path(__file__),Path(E.__file__),prior,ROM,KERNEL,R/'src/smb2_roster_objects.s',R/'src/reset.s'
    out=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=P.sha(image),ROM_written=False,
             patches=proof['patches'],ingress=callers,leaf=direct,whole_GameLoop=loops,vectors=result,
             bindings={str(p):P.sha(p.read_bytes()) for p in files})
    (args.output/'current-proof.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['expected_memory_only_SHA256'],result,flush=True)


if __name__=='__main__':
    main()

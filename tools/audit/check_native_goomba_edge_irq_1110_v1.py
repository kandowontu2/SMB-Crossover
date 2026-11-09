"""Qualify actual MMC5 interrupts at the native Goomba clip and OAM boundaries."""

import argparse
from collections import Counter
import json
from pathlib import Path

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import checkpoint, cpu_at
from check_mini_visibility_dispatch_1110_v1 import memory
from check_native_goomba_edge_1110_v1 import END,N,P,PROFILE,ROM,START,V,actor,seed


def vectors(old,new):
    base=seed(new)
    lag,regular=lag_pcs(base)
    counts=Counter()
    minimum=[255,255]
    deepest={}
    sites=set()

    def clone(c,baseline=False):
        m=slim_fork(c.memory)
        if baseline:
            m.bundle=old
            m.raw_page(1,m.rawtags[1])
        z=N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=registers(c)
        return z

    def state(c):
        m=c.memory
        return checkpoint(c),bytes(m[3:11]),m[0x06de],bytes(m[0x0200:0x0300])

    def interrupt(c,kind):
        owner=N.get(c.memory,'SelectedCharacter')
        before=state(c)
        effects=[]
        for baseline in (False,True):
            z=clone(c,baseline)
            m=z.memory
            hits=0
            if kind=='lag_FF':
                assert N.get(m,'NmiDisable')==255
                z.nmi()
            else:
                assert not z.p&4
                z.irq()

            def visit(q):
                nonlocal hits
                minimum[1]=min(minimum[1],q.sp)
                if kind!='lag_FF':
                    return
                assert q.pc!=regular
                hits+=q.pc==lag
                if not baseline and not q.p&4 and (owner not in deepest or q.sp<deepest[owner].sp):
                    deepest[owner]=clone(q)

            run(z,lambda q:(q.pc,q.sp)==(c.pc,c.sp),visit)
            assert hits==(kind=='lag_FF') and state(z)==before,(kind,owner,hex(c.pc))
            effects.append((memory(m),m.writes,m.ram_writes,z.processorCycles))
        assert effects[0]==effects[1],(kind,owner,hex(c.pc))
        counts[kind]+=1

    def observer(seen):
        def check(c):
            pc=c.pc
            if c.memory.rawtags[1]!=132 or not (START<=pc<END or 0xa65e<=pc<=0xa66e):
                return
            key=pc,c.sp,c.p&4
            if key in seen:
                return
            seen.add(key)
            sites.add(pc)
            minimum[0]=min(minimum[0],c.sp)
            interrupt(c,'lag_FF')
            if not c.p&4:
                interrupt(c,'IRQ')
        return check

    def direct(owner,ptr,xy,cursor,rot,active,p):
        m=slim_fork(base)
        x,xh,y,yh=xy
        N.put(m,SelectedCharacter=owner,GuestAudioCharacter=owner,R0=ptr&255,R1=ptr>>8,
              R3=0x8b,R4=x,R5=xh,R6=y,R7=yh,CurrentOAMOffset=cursor,
              GuestOamRotationActive=active,RgOamRotation=rot)
        c=cpu_at(m,START,227,p,x=0x4d,y=9)
        seen=set()
        run(c,lambda q:(q.pc,q.sp)==(V.STOP,227),observer(seen))
        assert seen

    for owner in range(42):
        direct(owner,0xaf2f,(249,0,184,1),12,204,1,0x21)
    for owner,ptr,xy,cursor,rot,active,p in (
        (0,0xaf38,(247,0,247,1),12,0,0,0x21),
        (41,0xaf41,(255,0,247,1),248,204,1,0x21),
        (41,0xaf4a,(255,0,248,1),12,249,1,0x25),
        (41,0xaf4a,(249,1,184,1),251,251,0x81,0x21),
        (12,0xaf2f,(249,0,184,2),12,204,1,0x21),
    ):
        direct(owner,ptr,xy,cursor,rot,active,p)
    scene=json.loads(PROFILE.read_text())['scene']
    for row in scene['actors']:
        if row['id']==6:
            seen=set()
            actor(base,row,scene['camera_left'],0x68,2,visit=observer(seen))
            assert seen
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert len(deepest)==42 and minimum[1]>0x7a
    return dict(cuts=dict(counts),raw_owners=42,reached_sites=len(sites),minimum_foreground_SP=minimum[0],
                minimum_ISR_SP=minimum[1],APU_mapper_OAM_writes_exact=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    path=args.output/'proof.json'
    proof=json.loads(path.read_text())
    for file,digest in proof['bindings'].items():
        assert P.sha(Path(file).read_bytes())==digest,file
    raw=ROM.read_bytes()
    assert proof['passed'] and P.sha(raw)==proof['parent_SHA256']
    image=install(raw,proof['patches'])
    assert P.sha(image)==proof['expected_memory_only_SHA256']
    q=vectors(P.bundle(raw),P.bundle(image))
    q.update(passed=True,ROM_written=False,parent_SHA256=P.sha(raw),memory_only_SHA256=P.sha(image),
             bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),path,ROM)})
    (args.output/'irq.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k!='bindings'}),flush=True)


if __name__=='__main__':
    main()

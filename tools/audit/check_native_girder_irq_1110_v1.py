"""Check real IRQ and FF NMI with live girder/death/Goomba state."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import checkpoint, cpu_at
from check_mini_visibility_dispatch_1110_v1 import memory
from check_native_girder_draw_1110_v1 import DIRECT_TYPED, DISPATCH, GIRDERS, GOOMBA, N, P, ROM, V


def vectors(old,new,proof):
    seed=N.fresh(new)
    seed.raw_page(1,132)
    N.put(seed,CurrentBank=132,NmiDisable=255,OperMode=1,OperMode_Task=3,
          GameEngineSubroutine=8,DisableScreenFlag=0,Mirror_PPUMASK=30)
    lag,regular=lag_pcs(seed)
    extents=[(p['start'],p['end_exclusive']) for p in proof['patches']]
    counts=Counter()
    minimum=[255,255]
    deepest={}
    sites=set()

    def clone(c, baseline=False):
        m=slim_fork(c.memory)
        if baseline:
            m.bundle=old
            m.raw_page(1,m.rawtags[1])
        z=N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=registers(c)
        return z

    def stable(c):
        m=c.memory
        return (checkpoint(c),bytes(m[3:11]),m[0x06de],m[0x6009],
                bytes(m[0x600f:0x6012]))

    def interrupt(c,kind):
        owner=N.get(c.memory,'SelectedCharacter')
        before=stable(c)
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

            def see(q):
                nonlocal hits
                minimum[1]=min(minimum[1],q.sp)
                if kind!='lag_FF':
                    return
                assert q.pc!=regular
                hits+=q.pc==lag
                if not baseline and not q.p&4 and (owner not in deepest or q.sp<deepest[owner].sp):
                    deepest[owner]=clone(q)

            run(z,lambda q:(q.pc,q.sp)==(c.pc,c.sp),see)
            assert hits==(kind=='lag_FF') and stable(z)==before,(kind,owner,hex(c.pc))
            effects.append((memory(m),m.writes,m.ram_writes,z.processorCycles))
        assert effects[0]==effects[1],(kind,owner,hex(c.pc))
        counts[kind]+=1

    def call(m,entry,p,death=False):
        c=cpu_at(m,entry,227,p,x=0x4d,y=9)
        seen=set()

        def visit(z):
            pc=z.pc
            if m.rawtags[1]!=132:
                return
            inside=any(lo<=pc<hi for lo,hi in extents)
            if not inside and not (death and 0xb8ed<=pc<=0xb965 or
                                   not death and (0xa5ba<=pc<=0xa5e9 or 0xbead<=pc<=0xbeca)):
                return
            key=pc,z.sp,z.x if death and pc==0xb965 else 0
            if key in seen:
                return
            seen.add(key)
            sites.add(pc)
            minimum[0]=min(minimum[0],z.sp)
            interrupt(z,'lag_FF')
            if not z.p&4:
                interrupt(z,'IRQ')

        run(c,lambda z:(z.pc,z.sp)==(V.STOP,227),visit)
        assert seen

    def draw(owner,entry,pointer,pos,cursor,rot,p):
        m=slim_fork(seed)
        x,xh,y,yh=pos
        N.put(m,SelectedCharacter=owner,GuestAudioCharacter=owner,
              R0=pointer&255,R1=pointer>>8,R3=0x8b,R4=x,R5=xh,R6=y,R7=yh,
              CurrentOAMOffset=cursor,GuestOamRotationActive=1,RgOamRotation=rot)
        call(m,entry,p)

    for owner in range(42):
        draw(owner,DISPATCH,GIRDERS[0],(104,0,168,1),60,204,0x21)
    for owner,entry,pointer,pos,cursor,p in (
        (41,DISPATCH,GIRDERS[0],(24,1,191,1),12,0x21),
        (41,DISPATCH,GIRDERS[0],(232,255,58,1),28,0x21),
        (41,DISPATCH,GIRDERS[1],(252,127,193,1),8,0x21),
        (41,DISPATCH,GIRDERS[1],(254,0,254,1),239,0x21),
        (41,DISPATCH,GIRDERS[1],(2,0,194,1),240,0x21),
        (41,DISPATCH,GIRDERS[1],(2,0,194,0),28,0x25),
        (6,DISPATCH,0xb34b,(2,0,194,1),8,0x21),
        (1,DISPATCH,GOOMBA[0],(2,0,194,1),8,0x21),
        (1,DISPATCH,0xaf30,(2,0,194,1),8,0x21),
        (1,DIRECT_TYPED,GOOMBA[0],(2,0,194,1),8,0x21),
        (41,DIRECT_TYPED,GOOMBA[1],(255,0,194,1),8,0x21),
    ):
        draw(owner,entry,pointer,pos,cursor,204,p)
    for owner,age,mode in product((1,12,41),(0,18,19,127,128,168,169,255),(0,1)):
        m=slim_fork(seed)
        N.put(m,SelectedCharacter=owner,GuestAudioCharacter=owner,
              MmDeathAge=age,MmDeathPit=0,MmDeathX=125,MmDeathPage=0,
              MmDeathY=178,MmDeathYHigh=1,CurrentOAMOffset=12,GuestOamRotationActive=mode,RgOamRotation=251)
        call(m,V.DEATH_ENTRY,0x21,True)
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert len(deepest)==42 and minimum[1]>0x7a
    return dict(cuts=dict(counts),minimum_foreground_SP=minimum[0],minimum_ISR_SP=minimum[1],
                raw_owners=42,reached_sites=len(sites),APU_mapper_writes_exact=True)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--rom',type=Path,default=ROM)
    args=cli.parse_args()
    path=args.output/'proof.json'
    proof=json.loads(path.read_text())
    for file,digest in proof['bindings'].items():
        assert P.sha(Path(file).read_bytes())==digest,file
    raw=args.rom.read_bytes()
    assert proof['passed'] and proof['parent_SHA256']==P.sha(raw)
    image=install(raw,proof['patches'])
    assert P.sha(image)==proof['expected_memory_only_SHA256']
    result=vectors(P.bundle(raw),P.bundle(image),proof)
    result.update(passed=True,ROM_written=False,parent_SHA256=P.sha(raw),memory_only_SHA256=P.sha(image),
                  bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),path,args.rom)})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'}),flush=True)


if __name__=='__main__':
    main()

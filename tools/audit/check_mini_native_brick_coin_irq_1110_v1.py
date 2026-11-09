"""Qualify actual vectors while native static draw and cached death state are live."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import checkpoint, cpu_at
from check_mini_visibility_dispatch_1110_v1 import memory
from check_mini_native_brick_coin_draw_1110_v1 import BRICK, COIN, DEATH_ENTRY, DRAW_ENTRY, N, P, ROM, STOP


def qualify(images, proof):
    old,new = images
    seed = N.fresh(new)
    seed.raw_page(1,132)
    N.put(seed,CurrentBank=132,NmiDisable=255,OperMode=1,OperMode_Task=3,
          GameEngineSubroutine=8,DisableScreenFlag=0,Mirror_PPUMASK=30)
    lag,regular = lag_pcs(seed)
    counts = Counter()
    deepest = {}
    minimum = [255,255]
    extents = [(p['start'],p['end_exclusive']) for p in proof['patches']]

    def clone(c, baseline):
        m = slim_fork(c.memory)
        if baseline:
            m.bundle = old
            m.raw_page(1,m.rawtags[1])
        z = N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp = registers(c)
        return z

    def stable(c):
        m=c.memory
        # The shared generic header uses the initial cursor across a cut.
        # Mega Man's native death loop now keeps the two bytes across all
        # eight outer draws instead of rewriting them in each iteration.
        return checkpoint(c),bytes(m[3:11]),m[0x06de],m[0x6009],bytes(m[0x600f:0x6012])

    def interrupt(c,kind):
        before=stable(c)
        owner=N.get(c.memory,'SelectedCharacter')
        outcomes=[]
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

            def observe(q):
                nonlocal hits
                minimum[1]=min(minimum[1],q.sp)
                if kind!='lag_FF':
                    return
                assert q.pc!=regular
                hits+=int(q.pc==lag)
                if not baseline and not q.p&4 and (owner not in deepest or q.sp<deepest[owner].sp):
                    deepest[owner]=clone(q,False)

            run(z,lambda q:(q.pc,q.sp)==(c.pc,c.sp),observe)
            assert hits==(kind=='lag_FF')
            assert stable(z)==before,(kind,owner,hex(c.pc))
            outcomes.append((memory(m),m.writes,m.ram_writes,z.processorCycles))
        assert outcomes[0]==outcomes[1],(kind,owner,hex(c.pc))
        counts[kind]+=1

    def call(m,entry,p,death=False):
        c=cpu_at(m,entry,227,p,x=0x4d,y=9)
        seen=set()

        def visit(z):
            pc=z.pc
            if m.rawtags[1]!=132:
                return
            if not any(lo<=pc<hi for lo,hi in extents) and not (death and 0xb8ed<=pc<=0xb965):
                return
            key=pc,z.sp,z.x if death and pc==0xb965 else 0
            if key in seen:
                return
            seen.add(key)
            minimum[0]=min(minimum[0],z.sp)
            interrupt(z,'lag_FF')
            if not z.p&4:
                interrupt(z,'IRQ')

        run(c,lambda z:(z.pc,z.sp)==(STOP,227),visit)
        assert seen

    for owner in range(42):
        m=slim_fork(seed)
        N.put(m,SelectedCharacter=owner,R0=BRICK&255,R1=BRICK>>8,R3=3,R4=104,R5=0,R6=142,R7=1,
              CurrentOAMOffset=12,GuestOamRotationActive=1,RgOamRotation=249)
        call(m,DRAW_ENTRY,0x21)
    for pointer,cursor,(x,y),p in product((COIN,0xada9,0xaf30),(28,252),((109,122),(251,248)),(0x21,0x25)):
        m=slim_fork(seed)
        N.put(m,SelectedCharacter=41,R0=pointer&255,R1=pointer>>8,R3=0x8b,R4=x,R5=0,R6=y,R7=1,
              CurrentOAMOffset=cursor,GuestOamRotationActive=1,RgOamRotation=249)
        call(m,DRAW_ENTRY, p)
    for owner,age,mode in product((1,12,41),(0,127,128,168,169,255),(0,1)):
        m=slim_fork(seed)
        N.put(m,SelectedCharacter=owner,MmDeathAge=age,MmDeathPit=0,MmDeathX=125,MmDeathPage=0,
              MmDeathY=178,MmDeathYHigh=1,CurrentOAMOffset=12,GuestOamRotationActive=mode,RgOamRotation=251)
        call(m,DEATH_ENTRY,0x21,True)
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert len(deepest)==42 and minimum[1]>0x7a
    return dict(cuts=dict(counts),minimum_foreground_SP=minimum[0],minimum_ISR_SP=minimum[1],raw_owners=42)


def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--rom',type=Path,default=ROM)
    args=cli.parse_args()
    path=args.output/'proof.json'
    proof=json.loads(path.read_text())
    raw=args.rom.read_bytes()
    assert proof['passed'] and proof['parent_SHA256']==P.sha(raw)
    for filename,digest in proof['bindings'].items():
        assert P.sha(Path(filename).read_bytes())==digest,filename
    image=install(raw,proof['patches'])
    assert P.sha(image)==proof['expected_memory_only_SHA256']
    result=qualify([P.bundle(r) for r in (raw,image)],proof)
    result.update(passed=True,ROM_written=False,parent_SHA256=P.sha(raw),memory_only_SHA256=P.sha(image),
                  bindings={str(p):P.sha(p.read_bytes()) for p in (Path(__file__),path,args.rom)})
    (args.output/'irq.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='bindings'}),flush=True)


if __name__=='__main__':
    main()

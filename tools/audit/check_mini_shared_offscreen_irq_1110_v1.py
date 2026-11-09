"""Rebind real IRQ and lag-NMI cuts to the exact shared offscreen patch."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, run, slim_fork
from measure_mini_shared_offscreen_1110_v1 import EXTENTS, N, P, PIN, R, ROM
from check_mini_visibility_dispatch_1110_v1 import memory


STOP=0x5b00


def cpu_at(m,pc,sp,p,x=1,y=1):
    c=N.NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.sp,c.p=0x55,x,y,sp,p
    c.stPushWord(STOP-1)
    return c


def checkpoint(c):
    m=c.memory
    return (registers(c,0xef),c.pc,live_stack(c),bytes(m[7:11]),bytes(m[0x15a:0x17b]),tuple(m.rawtags))


def vectors(images):
    old,new=images
    seed=N.fresh(new)
    lag,regular=lag_pcs(seed)
    counts=Counter()
    deepest={}
    sites=set()
    minima=[255,255]

    def clone(c,baseline=False):
        m=slim_fork(c.memory)
        if baseline:
            m.bundle=old
            m.raw_page(0,m.rawtags[0])
        cpu=N.NesMPU(memory=m,pc=c.pc)
        cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=registers(c)
        return cpu

    def interrupt(c,kind):
        variant=N.get(c.memory,'SelectedCharacter')
        parent=checkpoint(c)
        result=[]
        for baseline in (False,True):
            q=clone(c,baseline)
            m=q.memory
            hits=0
            if kind=='lag_FF':
                assert N.get(m,'NmiDisable')==255
                q.nmi()
            else:
                assert not q.p&4
                q.irq()

            def inspect(z):
                nonlocal hits
                minima[1]=min(minima[1],z.sp)
                if kind=='lag_FF':
                    assert z.pc!=regular
                    hits+=int(z.pc==lag)
                    if not baseline and not z.p&4 and (variant not in deepest or z.sp<deepest[variant].sp):
                        deepest[variant]=clone(z)

            run(q,lambda z:(z.pc,z.sp)==(c.pc,c.sp),inspect)
            assert hits==(kind=='lag_FF')
            assert checkpoint(q)==parent,(kind,variant,hex(c.pc),checkpoint(q),parent)
            result.append((memory(m),m.writes,m.ram_writes,q.processorCycles))
        assert result[0]==result[1],(kind,variant,hex(c.pc))
        counts[kind]+=1

    def watch(c,seen):
        pc=c.pc
        if c.memory.rawtags[0]!=254 or not any(lo<=pc<hi for lo,hi in EXTENTS):
            return
        key=pc,c.sp,c.p&4
        if key in seen:
            return
        seen.add(key)
        sites.add(pc)
        minima[0]=min(minima[0],c.sp)
        interrupt(c,'lag_FF')
        if not c.p&4:
            interrupt(c,'IRQ')

    # Actual common entry under each owner's asynchronous environment.
    # The fixture uses live shared enemy slot0 with its real arrays.
    offscreen=P.address(new,'GetOffScreenBitsSet')
    for raw in range(42):
        m=slim_fork(seed)
        N.put(m,SelectedCharacter=raw,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,
              NmiDisable=255,DisableScreenFlag=0,Mirror_PPUMASK=30,
              ScreenLeft_X_Pos=43,ScreenRight_X_Pos=42,ScreenLeft_PageLoc=0,ScreenRight_PageLoc=1,
              Enemy_X_Position=192,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1)
        seen=set()
        c=cpu_at(m,offscreen,232,0x21)
        run(c,lambda z:(z.pc,z.sp)==(STOP,232),lambda z:watch(z,seen))
        assert seen

    # Both fixed native collision/renderer callers arise at their genuine
    # GameLoop stack depth, including edge, ordinary and off-height actors.
    live=[]
    for actor_count,edge,p in product((2,5),('ordinary','right','height'),(0x21,0x25)):
        m=P.fixture(new,actor_count,False,False)
        if edge=='right':
            m[P.address(new,'Enemy_X_Position')]=248
        if edge=='height':
            m[P.address(new,'Enemy_Y_Position')]=242
            m[P.address(new,'Enemy_Y_HighPos')]=0
        N.put(m,SavedJoypadBits=193,SavedJoypad1Bits=193,NmiDisable=255,VRAM_Buffer1_Offset=0)
        c=cpu_at(m,P.address(new,'GameLoop'),252,p,x=0,y=0)
        seen=set()
        run(c,lambda z:(z.pc,z.sp)==(STOP,252),lambda z:watch(z,seen))
        assert seen
        live.append(dict(actors=actor_count,geometry=edge,I=bool(p&4),cuts=len(seen)))
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert all(counts[k] for k in ('IRQ','lag_FF','nested_IRQ')) and minima[1]>0x7a
    return dict(cuts=dict(counts),reached_sites=sorted(sites),raw_owners=42,actual_GameLoop=live,
                minimum_foreground_SP=minima[0],minimum_ISR_SP=minima[1],lag_PC=lag,forbidden_regular_NMI_PC=regular)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    proof_path=args.output/'proof.json'
    proof=json.loads(proof_path.read_text())
    raw=ROM.read_bytes()
    assert proof['passed'] and proof['parent_SHA256']==P.sha(raw)==PIN
    for path,digest in proof['bindings'].items():
        assert P.sha(Path(path).read_bytes())==digest,path
    image=install(raw,proof['patches'])
    assert P.sha(image)==proof['expected_memory_only_SHA256']
    result=vectors([P.bundle(q) for q in (raw,image)])
    report=dict(passed=True,ROM_written=False,base_SHA256=PIN,memory_only_SHA256=P.sha(image),**result,
                bindings={str(q):P.sha(q.read_bytes()) for q in (Path(__file__),proof_path,ROM,R/'src/reset.s')},
                scope='Actual shared IRQ/FF and nested IRQ. Exact parent-versus-candidate ISR bytes on the same '
                      'reached foreground state, including native bus and inherited OAM effects.')
    (args.output/'irq.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('bindings','actual_GameLoop','reached_sites')}),flush=True)


if __name__=='__main__':
    main()

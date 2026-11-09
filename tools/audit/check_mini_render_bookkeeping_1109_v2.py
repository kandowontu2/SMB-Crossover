"""Check actual IRQ/lag cuts and joint firebar/small-lift order."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import measure_mini_render_bookkeeping_1109_v1 as V
from check_mini_funded_actor_1108_v3 import install, slim_fork, live_stack, registers, new_cpu, run

A, N, R, OUT = V.A, V.N, V.R, V.OUT


def main():
    path = OUT/'measurement.json'
    q = json.loads(path.read_text())
    raw = V.ROM.read_bytes()
    successor = install(raw,[q['patch']])
    assert A.sha(raw)==V.PIN and A.sha(successor)==q['memory_only_SHA256']
    images=[A.bundle(r) for r in [raw,successor]]
    old,new=images
    at=q['patch']['file_offset']
    assert raw[at:at+7].hex() == '2008ad202fad60'
    window=raw[16+71*8192:16+72*8192]
    for address in [0xad08,0xad2f]:
        low,high=address&255,address>>8
        assert window.count(bytes([0x20,low,high]))==1 and window.count(bytes([0x4c,low,high]))==0
    bindings=[Path(__file__),path,Path(V.__file__),V.ROM,V.SRC,V.LEGACY,R/'src/reset.s']
    seeds=[A.fixture(b,0,False,False) for b in images]
    counts=Counter()
    mins=[255,255]
    deepest={}

    def state(c):
        m=c.memory
        return registers(c,0xef),live_stack(c),bytes(m[:11]),bytes(m[0x15a:0x17b]),bytes(m[0x200:0x304]), \
               bytes(m[0x6000:0x8000]),tuple(m.rawtags),tuple(map(bytes,m.ram)),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC')

    def clone(c, bundle=None):
        m=slim_fork(c.memory)
        if bundle:
            m.bundle=bundle
            for index,tag in enumerate(m.rawtags[:]):m.raw_page(index,tag)
        z=N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=registers(c)
        return z

    def interrupt(c,kind):
        z=clone(c)
        before=state(z)
        ret=z.pc,z.sp
        if kind=='lag_FF':
            assert N.get(z.memory,'NmiDisable')==255
            z.nmi()
        else:
            assert not z.p&4
            z.irq()

        def visit(k):
            mins[1]=min(mins[1],k.sp)
            assert k.memory.rawtags[1]!=199 or not V.START<=k.pc<V.JOIN
            if kind=='lag_FF' and not k.p&4:
                tag=k.memory.rawtags[(k.pc-0x8000)//8192] if k.pc>=0x8000 else -1
                key=tag,k.pc,N.get(k.memory,'SelectedCharacter')
                if key not in deepest or k.sp<deepest[key].sp:deepest[key]=clone(k)

        run(z,lambda k:(k.pc,k.sp)==ret,visit)
        after=state(z)
        assert before[:5]==after[:5] and before[6:]==after[6:],(kind,ret,[i for i in range(len(before)) if before[i]!=after[i]])
        if before[5]!=after[5]:
            assert kind=='lag_FF'
            ref=clone(c,old)
            ref.nmi()
            run(ref,lambda k:(k.pc,k.sp)==ret)
            assert state(ref)==after and ref.memory.writes==z.memory.writes
            counts['full_original_audio_SRAM_parity']+=1
        assert not any(0x200<=a<0x304 or a==0x4014 for a,_ in z.memory.writes)
        counts[kind]+=1

    def witness(seed,owner,case,slot,rotate):
        m=slim_fork(seed)
        enemy={'low':6,'firebar':0x1b,'lift':0x2b,'mixed':0x1b,'stale':0x2c}[case]
        V.init(m,slot,enemy,0 if case=='stale' else 1,owner,rotate)
        if case=='mixed':
            j=5-slot
            for n,v in [('Enemy_Flag',1),('Enemy_ID',0x2c),('Enemy_Y_HighPos',1),('Enemy_Y_Position',104),
                        ('Enemy_PageLoc',0),('Enemy_X_Position',128)]:
                m[A.address(m.bundle,n)+j]=v
        return m

    paired=0
    for owner,slot,rotate in product([0,4,41],[0,5],[0,1]):
        pair=[]
        for seed in seeds:
            m=witness(seed,owner,'mixed',slot,rotate)
            z=N.invoke(m,'Z2LateWorldAdmission',x=7,y=23,a=83,p=0x71)
            pair.append(V.state(m,z))
        assert pair[0]==pair[1]
        paired+=1

    for owner,case,slot,p in product([0,4,41],['low','firebar','lift','mixed','stale'],[0,5],[0x20,0x24]):
        m=witness(seeds[1],owner,case,slot,1)
        m.raw_page(1,199)
        N.put(m,CurrentBank=199,NmiDisable=255)
        c=new_cpu(m,V.START,83,7,p)
        seen=set()

        def visit(z):
            key=z.pc,z.sp,z.p&4
            if m.rawtags[1]!=199 or not V.START<=z.pc<V.JOIN or key in seen:return
            seen.add(key)
            mins[0]=min(mins[0],z.sp)
            interrupt(z,'lag_FF')
            if not z.p&4:interrupt(z,'IRQ')

        run(c,lambda z:z.pc==0x5b00,visit)
        assert c.sp==224 and seen
    for c in deepest.values():interrupt(c,'nested_IRQ')
    assert mins[1]>0x7a and all(counts[n] for n in ['IRQ','lag_FF','nested_IRQ'])
    receipt=dict(passed=True,CPU_only=True,ROM_written=False,base_SHA256=V.PIN,
                 memory_only_SHA256=A.sha(successor),mixed_actor_cases=paired,actual_cuts=dict(counts),
                 minimum_foreground_SP=mins[0],minimum_ISR_SP=mins[1],
                 protected='Live AXYP/SP, maps, exact SMC, private SRAM, native scratch and OAM across actual vectors. No lag DMA. Any audio-induced SRAM change is compared with the original native ISR from the identical cut and actual write order.',
                 bindings={str(p):A.sha(p.read_bytes()) for p in bindings})
    (OUT/'actual-vectors.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('Mixed',paired,'actual vectors',dict(counts),'minSP',mins,flush=True)


if __name__=='__main__':main()

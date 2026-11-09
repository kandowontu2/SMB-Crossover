"""Qualify actual IRQ, FF lag NMI and nesting on no-special and real world draws."""

import argparse
from collections import Counter
import json
from pathlib import Path

from check_mini_busy_fire_interrupts_1108_v3 import lag_pcs
from check_mini_funded_actor_1108_v3 import install, registers, run, slim_fork
from check_mini_shared_offscreen_irq_1110_v1 import checkpoint
from check_mini_visibility_dispatch_1110_v1 import memory
from check_native_firebar_admission_1110_v1 import ENTRY,N,P,ROM,SCENE_START,positive_seed,render,setup


def vectors(old,new,proof):
    counts=Counter()
    deepest={}
    sites=set()
    minimum=[255,255]
    publication_sites=set()
    extents=[(p['start'],p['end_exclusive']) for p in proof['patches']]

    def clone(c,base=False):
        m=slim_fork(c.memory)
        if base:
            m.bundle=old
            m.raw_page(1,m.rawtags[1])
        z=N.NesMPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=registers(c)
        return z

    def stable(z):
        m=z.memory
        return checkpoint(z),bytes(m[3:11]),m[0x7eb4],m[0x06de]

    def interrupt(c,kind):
        owner=N.get(c.memory,'SelectedCharacter')
        before=stable(c)
        effects=[]
        for baseline in (False,True):
            z=clone(c,baseline)
            m=z.memory
            lag,regular=lag_pcs(m)
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
                if kind=='lag_FF':
                    assert q.pc!=regular
                    hits+=q.pc==lag
                    if not baseline and not q.p&4 and (owner not in deepest or q.sp<deepest[owner].sp):
                        deepest[owner]=clone(q)

            run(z,lambda q:(q.pc,q.sp)==(c.pc,c.sp),see)
            after=stable(z)
            if after!=before:
                # The inherited firebar drawer publishes its C shadow before
                # the hardware store. FF NMI can complete that publication.
                pc=c.pc
                original=c.memory
                assert kind=='lag_FF' and original.rawtags[1]==135,(kind,owner,hex(pc))
                if pc in (0xb5b7,0xb5b9):
                    assert bytes(original[0xb5b4:0xb5bc])==bytes.fromhex('8da17da9938d1651')
                else:
                    assert pc==0xb675 and bytes(original[0xb672:0xb678])==bytes.fromhex('8da17d8d1651')
                old_maps=before[0][-1]
                assert old_maps[2]!=original[0x7da1]
                expected=old_maps[:2]+(original[0x7da1],)+old_maps[3:]
                assert after==(before[0][:-1]+(expected,),)+before[1:]
                publication_sites.add(pc)
            assert hits==(kind=='lag_FF'),(kind,owner,hex(c.pc),m.rawtags)
            effects.append((memory(m),m.writes,m.ram_writes,z.processorCycles))
        assert effects[0]==effects[1],(kind,owner,hex(c.pc))
        counts[kind]+=1

    def trace(m,owner,entry=ENTRY):
        N.put(m,SelectedCharacter=owner,GuestAudioCharacter=owner)
        seen=set()

        def visit(z):
            tag,pc=z.memory.rawtags[1],z.pc
            if tag==132:
                reached=any(lo<=pc<hi for lo,hi in extents)
            elif tag==199:
                reached=0xad01<=pc<=0xad58
            elif tag==135:
                reached=0xb5ae<=pc<=0xb678
            else:
                reached=False
            if not reached or (tag,pc,z.sp) in seen:
                return
            seen.add((tag,pc,z.sp))
            sites.add((tag,pc))
            minimum[0]=min(minimum[0],z.sp)
            interrupt(z,'lag_FF')
            if not z.p&4:
                interrupt(z,'IRQ')

        result,_=render(m,entry,visit=visit)
        assert seen
        return result

    for owner in range(42):
        trace(setup(new),owner)
    for owner,ident,index,parity in ((18,0x1b,1,0),(18,0x1f,4,1),(41,0x22,4,1),
                                    (18,0x2b,1,0),(41,0x2c,4,1)):
        m=positive_seed(new,ident,index)
        N.put(m,FrameCounter=parity)
        assert trace(m,owner,SCENE_START)[3],(owner,ident)
    for c in deepest.values():
        interrupt(c,'nested_IRQ')
    assert len(deepest)==42 and minimum[1]>0x7a
    return dict(cuts=dict(counts),raw_owners=42,reached_sites=len(sites),minimum_foreground_SP=minimum[0],
                minimum_ISR_SP=minimum[1],ISR_APU_mapper_OAM_writes_exact=True,
                inherited_C_publication_sites=sorted(publication_sites))


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

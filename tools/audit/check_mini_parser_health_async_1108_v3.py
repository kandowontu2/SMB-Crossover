"""Check whether actual lag NMI/IRQ can observe reordered parser writes."""
from collections import Counter
from itertools import product
from pathlib import Path
import json

import measure_mini_parser_health_batch_1108_v2 as B

A,N,R,OUT,sha = B.A,B.N,B.R,B.OUT,B.sha
FF = 255


def main():
    manifest_path=OUT/'health-batch-v2.json'
    manifest=json.loads(manifest_path.read_text())
    raw=A.ROM.read_bytes();assert sha(raw)==manifest['base_SHA256']==A.PIN
    new=bytearray(raw)
    for row in manifest['patches']:
        at=row['file_offset']; old=bytes.fromhex(row['old_hex']); replacement=bytes.fromhex(row['new_hex'])
        assert new[at:at+len(old)]==old
        new[at:at+len(old)]=replacement
    assert sha(new)==manifest['expected_memory_only_SHA256']
    b=A.bundle(new); CPU=N.NesMPU; Base=N.Bus; cnt=Counter(); lower=255; foreground_low=255
    target_ranges=[(A.address(b,n),size,n) for n,size in [('Block_Buffer_1',208),('Block_Buffer_2',208),
                        ('MmBrickHealth',416),('MmCoinHits',416),('MmSolidTerrain',416),
                        ('GuestTerrainColumn',13),('MetatileBuffer',13),('M0',2),('R6',2)]]
    target_addresses={a for base,n,_ in target_ranges for a in range(base,base+n)}
    handler_depth={}; watched=[]; nested_best={}

    class Bus(Base):
        guarded=False
        def __getitem__(self,at):
            if self.guarded and isinstance(at,int):
                assert at not in target_addresses, ('Interrupt read transient parser state',hex(at))
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if self.guarded and isinstance(at,int):
                assert at not in target_addresses, ('Interrupt write transient parser state',hex(at))
            super().__setitem__(at,value)

    def clone(c):
        m=N.fork(c.memory);z=CPU(memory=m,pc=c.pc)
        m.guarded=False
        z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z

    def registers(c):return (c.a,c.x,c.y,c.p&0xef,c.sp)

    def stable(c):
        m=c.memory
        return (registers(c),tuple(m.rawtags),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'),
                bytes(m[0x15a:0x17b]),bytes(m[0x101+c.sp:0x200]),
                tuple(bytes(m[base:base+count]) for base,count,_ in target_ranges))

    def run_handler(c,kind,record=False):
        nonlocal lower
        z=clone(c); before=stable(z); ret=(z.pc,z.sp)
        if kind=='IRQ':
            assert not z.p&4
            z.irq()
        else:
            assert N.get(z.memory,'NmiDisable')==FF
            z.nmi()
        z.memory.guarded=True
        low=z.sp
        for _ in range(20000):
            if (z.pc,z.sp)==ret:break
            low=min(low,z.sp)
            if record and not z.p&4:
                tag=z.memory.rawtags[(z.pc-0x8000)//8192] if z.pc>=0x8000 else -1
                key=(tag,z.pc,N.get(z.memory,'SelectedCharacter'))
                if key not in nested_best or z.sp<nested_best[key].sp:nested_best[key]=clone(z)
            assert z.memory[z.pc]!=0, ('ISR BRK',kind,hex(z.pc),ret)
            z.step()
        else:raise AssertionError(('ISR bounded return',kind,ret,hex(z.pc)))
        z.memory.guarded=False
        assert stable(z)==before, ('ISR resumed altered live state',kind,ret)
        cnt[kind]+=1; lower=min(lower,low)
        return low

    def probe(c,kind):
        # A paired execution starts at a real qualified instruction cut in
        # the transformed source, using the unchanged current native vectors.
        return run_handler(c,kind,record=kind=='lag_FF')

    N.Bus=Bus
    seeds=[]
    try:
        for owner,mode,pattern,p in product([0,41],[0,1],['plain','match','mismatch'],[0x21,0x25]):
            m=N.fresh(b)
            N.put(m,SelectedCharacter=owner,OperMode=1,DisableScreenFlag=mode,
                  Mirror_PPUMASK=30 if not mode else 0,NmiDisable=FF,
                  AreaPointer=0x25,AreaParserTaskNum=4,FamilyMainCommit=1,Mirror_PPUCTRL=160)
            N.invoke(m,'GetAreaDataAddrs')
            m.raw_page(1,130);N.put(m,CurrentBank=130)
            N.invoke(m,'GetBlockBufferAddr',a=0 if pattern=='plain' else 31)
            for row in range(13):
                m[A.address(b,'MetatileBuffer')+row]=0x54
                m[A.address(b,'GuestTerrainColumn')+row]=dict(plain=0,match=0x54,mismatch=0x52)[pattern]
            for addr,value in [(0x7d8,2),(0x7db,4)]:m[addr]=value if pattern!='plain' else 0
            c=CPU(memory=m,pc=B.PC_TAIL);c.a,c.x,c.y,c.p,c.sp=83,7,91,p,219;c.stPushWord(0x5aff)
            seen=set()
            for _ in range(4000):
                if c.pc==0x5b00:break
                tag=m.rawtags[(c.pc-0x8000)//8192]
                foreground_low=min(foreground_low,c.sp)
                key=(tag,c.pc)
                if key not in seen:
                    seen.add(key)
                    probe(c,'lag_FF')
                    if not c.p&4:probe(c,'IRQ')
                    if owner==41 and (not watched or c.sp<watched[0].sp):watched[:]=[clone(c)]
                c.step()
            else:raise AssertionError('foreground bound')
            assert c.sp==219
            seeds.append([owner,mode,pattern,p,len(seen)])
    finally:N.Bus=Base
    for ctx in nested_best.values():run_handler(ctx,'IRQ')
    assert lower>0x7a and watched
    assert cnt['lag_FF'] and len(nested_best)
    result=dict(passed=True,CPU_only=True,ROM_written=False,base_SHA256=A.PIN,
                memory_image_SHA256=sha(new),foreground_scenarios=seeds,
                cuts=dict(cnt),nested_lag_NMI_IRQ_contexts=len(nested_best),min_foreground_SP=foreground_low,min_handler_SP=lower,
                protected_read_write_ranges=[dict(start=a,length=n,name=label) for a,n,label in target_ranges],
                source='Native active GameLoop and ScreenRoutines calls run under NmiDisable FF. Actual lag path runs audio and optional HUD IRQ; native IRQ may use R0 as delay but has no parser or health reader.',
                scope='Actual current IRQ and lag-NMI instructions at every distinct reached parser-tail PC for Mario and Mini with rendering on/off, different original terrain branches, I0/I1, plus deepest measured nested IRQ contexts. No arbitrary foreign asynchronous state claim.',
                bindings={str(p):sha(p.read_bytes()) for p in [Path(__file__),manifest_path,R/'src/reset.s',R/'src/game.s',R/'src/screen_render.s',R/'src/level_tiles.s',A.ROM]})
    (OUT/'health-batch-async-v3.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['passed','cuts','nested_lag_NMI_IRQ_contexts','min_foreground_SP','min_handler_SP']}),flush=True)


if __name__=='__main__':main()

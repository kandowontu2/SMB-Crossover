"""Focused cold, foreign, and native IRQ/FF boundaries for the Mini packet."""
import argparse
from collections import Counter
import json
from pathlib import Path

import check_mini_direct_native_1103 as T
N,R,address=T.N,T.R,T.address
SOUND=[0x7d8,0x7da,0x7db,0x7dc]


def view(m):
    native=bytearray(m[0x200:0x800])
    for at in SOUND:native[at-0x200]=0
    return ([bytes(x)for x in m.ram],bytes(m[3:11]),bytes(m[0x15a:0x17b]),bytes(native),
            N.get(m,'SelectedCharacter'),N.get(m,'CurrentBank'),N.get(m,'CurrentBankC'))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();out=args.output.resolve()
    after,patches=T.compose(out);images=[T.bundle(T.PARENT.read_bytes()),T.bundle(after)]
    seeds=[T.machine(image)for image in images]
    for epoch in [1,2]:
        for m in seeds:
            N.put(m,FrameCounter=epoch)
            N.invoke(m,'GameCoreRoutine',x=0,y=0)
    cold=0
    # Ready0/1 cannot dispatch privately until both full cookies pass. Each
    # of the actual 32 header-byte faults must still be refused on that path.
    for ready in [0,1]:
        for bank in [2,3]:
            for byte in range(16):
                pair=[N.fork(m)for m in seeds];results=[]
                for m in pair:
                    N.put(m,FrameCounter=3)
                    m.ram[2][0x300]=ready
                    m.ram[bank][0x1fe0+byte]^=1
                    results.append(N.invoke(m,'NrMovement',a=83,x=7,y=91,p=0x21))
                T.compare(pair,results,('cold-fault',ready,bank,byte));cold+=1
    # The warm source invariant is deliberately the valid-last live markers,
    # not a claim of recovering arbitrary RAM corruption or old save states.
    marker=0
    for bank in [2,3]:
        for byte in [0,1]:
            pair=[N.fork(m)for m in seeds];results=[]
            for m in pair:
                N.put(m,FrameCounter=3)
                m.ram[bank][0x1fe0+byte]^=1
                results.append(N.invoke(m,'NrMovement',a=83,x=7,y=91,p=0x21))
            T.compare(pair,results,('warm-marker',bank,byte));marker+=1
    foreign=0
    for raw in list(range(41))+[42,255]:
        for x in [0,9,14]:
            for p in [0x20,0xe1]:
                states=[]
                for seed in seeds:
                    m=N.fork(seed);N.put(m,SelectedCharacter=raw,CurrentBank=252)
                    m.raw_page(1,252)
                    c=N.NesMPU(memory=m,pc=0xa506)
                    c.a,c.x,c.y,c.p,c.sp=83,x,121,p,220
                    for _ in range(20):
                        if c.pc==0xa509:break
                        c.step()
                    else:raise AssertionError(('foreign continuation',raw,x,c.pc))
                    states.append((c.a,c.x,c.y,c.p,c.sp,bytes(m[0x15a:0x17b]),m.rawtags[:]))
                assert states[0]==states[1],('foreign',raw,x,p,states)
                foreign+=1

    CPU=N.NesMPU;counts=Counter();seen=set();minimum=224
    def clone(c,old=False):
        m=N.fork(c.memory)
        if old:
            m.bundle=images[0]
            for win,tag in enumerate(m.rawtags[:]):
                if tag&128:m.raw_page(win,tag)
        z=CPU(memory=m,pc=c.pc)
        z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
        return z
    def finish(c,ret):
        nonlocal minimum
        for _ in range(100000):
            if(c.pc,c.sp)==ret:return
            minimum=min(minimum,c.sp)
            assert c.memory[c.pc]!=0,('ISR BRK',hex(c.pc),c.sp)
            c.step()
        raise AssertionError(('ISR bound',ret,hex(c.pc),c.sp))
    def probe(c,kind):
        z=clone(c);ref=clone(c,True)
        ret=(c.pc,c.sp);regs=(c.a,c.x,c.y,c.p&0xef,c.sp)
        before=view(z.memory);maps=z.memory.rawtags[:]
        live=bytes(z.memory[0x101+c.sp:0x200])
        z.irq()if kind=='IRQ'else z.nmi()
        ref.irq()if kind=='IRQ'else ref.nmi()
        finish(z,ret);finish(ref,ret)
        assert(z.a,z.x,z.y,z.p&0xef,z.sp)==regs,('ISR AXYP',kind,hex(c.pc))
        assert view(z.memory)==before,('ISR foreground',kind,hex(c.pc))
        assert bytes(z.memory[0x101+c.sp:0x200])==live,('ISR live stack',kind,hex(c.pc))
        assert view(z.memory)==view(ref.memory),('ISR old-handler parity',kind,hex(c.pc))
        assert (bytes(z.memory.vram),z.memory.chr_latches,z.memory.ppu_addr,z.memory.toggle,
                z.memory.buffer,z.memory.ppuctrl,tuple(z.memory[a]for a in SOUND)) == (
                bytes(ref.memory.vram),ref.memory.chr_latches,ref.memory.ppu_addr,ref.memory.toggle,
                ref.memory.buffer,ref.memory.ppuctrl,tuple(ref.memory[a]for a in SOUND))
        if z.memory.rawtags!=maps:
            ins=bytes(z.memory[c.pc:c.pc+3])
            assert ins==bytes.fromhex('8d1651'),('pending mapper',kind,hex(c.pc),ins.hex())
            assert z.memory.rawtags[2]==N.get(z.memory,'CurrentBankC')
            assert all(z.memory.rawtags[i]==maps[i]for i in [0,1,3])
            counts['pending_C_store']+=1
        counts[kind]+=1
    class Trace(CPU):
        def step(self):
            tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else -1
            relevant=(tag==0xd4 and any(pc<=self.pc<pc+len((out/(name+'.bin')).read_bytes())
                       for name,bank,pc,_,_ in T.SPANS if bank==84)) or self.pc in [0x80c2,0x80c5]
            key=(scenario,tag,self.pc,bool(self.p&4))
            if relevant and key not in seen:
                seen.add(key);probe(self,'FF')
                if not self.p&4:probe(self,'IRQ')
            super().step()
    N.NesMPU=Trace
    try:
        for scenario in ['cold','hot']:
            for flags in [0x21,0x25]:
                m=N.fork(seeds[1]);N.put(m,FrameCounter=3,NmiDisable=255)
                if scenario=='cold':m.ram[2][0x300]=1
                N.invoke(m,'NrMovement',a=83,x=7,y=91,p=flags)
    finally:N.NesMPU=CPU
    report=dict(passed=True,source_CPU_only=True,ROM_written=False,
                full_cold_header_byte_faults=cold,warm_marker_faults=marker,
                foreign_native_continuations=foreign,ISR=dict(counts),minimum_ISR_SP=minimum,
                warm_authority='Actual cold copy verifies code/data before descending15to0 cookie commit in both RAM banks; retirement clears both validity bytes before reuse. Fresh0to1 and first Main1to2 belong this loaded Mini image. Ready2 plus both live A7/29 markers and engine8 is an initialized-owner predicate independent of frame counter. Arbitrary non-marker RAM corruption and old save-state recovery are outside this source invariant.',
                source_bindings={str(p.relative_to(R)):T.sha(p)for p in[
                    Path(__file__),R/'tools/reference/mini_mario_direct_native_1103.s',
                    R/'build/mini-mario-owner-1103-v15/owner-final-v28.s',
                    R/'build/mini-mario-owner-1103-v15/source-boundaries-v27.json',
                    R/'build/mini-zero-visible-direct/mini-zero.s']})
    (out/'boundaries.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()

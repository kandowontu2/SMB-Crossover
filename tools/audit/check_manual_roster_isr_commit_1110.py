"""Locate the exact baseline/candidate ISR write to FamilyMainCommit5FFF."""
from hashlib import sha256
import json
from pathlib import Path

import check_manual_roster_ff_foot_1110 as F

I,P,N,R=F.I,F.P,F.N,F.R


def main():
    proof=I.OUT/'ff-foot-proof.json';q=json.loads(proof.read_text())
    base=I.BASE.read_bytes();raw=P.install(base,q['patches'])
    assert I.SHA(raw)==q['expected_memory_only_SHA256']
    pc=[0];events=[]
    class Probe(P.StackGuard):
        isr_probe=False
        def __setitem__(self,at,value):
            if self.isr_probe and at==0x5fff:
                tag=self.rawtags[(pc[0]-0x8000)//8192] if pc[0]>=0x8000 else -1
                events.append(dict(PC=pc[0],tag=tag,bytes=bytes(self[pc[0]:pc[0]+6]).hex(),
                    before=self[at],after=value))
            return super().__setitem__(at,value)
    old=N.Bus;N.Bus=Probe
    try:m=F.Motion.scene(F.bundle(raw,q['labels']),22,0)
    finally:N.Bus=old
    m[0x73d1]=128;m[0x73d2]=m[0x73d3]=0
    N.put(m,SavedJoypadBits=0x28,SavedJoypad1Bits=0x28,NmiDisable=255,CurrentPlayer=0)
    c=N.NesMPU(memory=m,pc=P.L.M.address(m.bundle,'IdleLoop'))
    c.sp,c.p=255,0x31;c.stPushWord(0xe33b)
    P.run(c,lambda z:(z.pc,z.sp)==(0x837b,245))
    results={}
    for name,image in (('candidate',raw),('baseline',base)):
        z=P.clone(c);memory=z.memory
        memory.bundle=dict(memory.bundle,raw=image)
        for win,tag in enumerate(tuple(memory.rawtags)):
            if tag&128:memory.raw_page(win,tag)
        memory.vector_floor=0x100+z.sp;memory.written_stack=set();memory.isr_probe=True
        events.clear();entry=z.pc,z.sp;before=memory[0x5fff]
        z.nmi()
        P.run(z,lambda z:(z.pc,z.sp)==entry,lambda z:pc.__setitem__(0,z.pc))
        results[name]=dict(before=before,after=memory[0x5fff],writes=list(events))
        print(name,results[name],flush=True)
    assert results['candidate']==results['baseline']
    result=dict(passed=True,expected_memory_only_SHA256=q['expected_memory_only_SHA256'],
        baseline_SHA256=I.PIN,field='FamilyMainCommit',address=0x5fff,identical_actual_ISR_write=results,
        bindings={Path(__file__).relative_to(R).as_posix():sha256(Path(__file__).read_bytes()).hexdigest()})
    (I.OUT/'isr-family-commit.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()

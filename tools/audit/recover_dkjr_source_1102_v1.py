"""Small private original DK Jr orientation; never modifies a host cartridge."""
from pathlib import Path
import sys,json,collections,hashlib
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import dkjr_original_cpu_1102_v1 as D
from py65.disassembler import Disassembler
O=R/'build/dkjr-source-1102-v1'

def main():
    O.mkdir(parents=True,exist_ok=True)
    c=D.boot();d=Disassembler(c);lines=[];a=0xc000
    while a<0x10000:
        n,t=d.instruction_at(a);lines.append(f'{a:04X}: {t}');a+=n
    (O/'donor-linear.txt').write_text('\n'.join(lines)+'\n')
    cases=[]
    for name,controls in [('idle',[0]*180),('walk-right',[1]*180),
        ('right-jump',[1]*48+[0x81]*60+[1]*90),
        ('right-up-jump',[1]*48+[0x88]*60+[8]*90),
        ('right-down',[1]*48+[4]*90),('left',[2]*120)]:
        c,boot_frames=D.active();calls=collections.Counter();pcs=set();samples=[];changes=[]
        def trace(q):
            pcs.add(q.pc)
            if q.memory[q.pc]==0x20:
                target=q.memory[q.pc+1]+256*q.memory[q.pc+2];calls[target]+=1
        old=D.state(c)
        for f,pad in enumerate(controls):
            D.frame(c,pad,trace);z=D.state(c)
            if f%12==0:samples.append(dict(frame=f,**z))
            if z['state']!=old['state']:changes.append(dict(frame=f,old=old['state'],**z))
            old=z
        cases.append(dict(name=name,boot_frames=boot_frames,frames=len(controls),
                          samples=samples,transitions=changes,
                          calls={f'{k:04X}':v for k,v in sorted(calls.items())},
                          original_executed_PCs=len(pcs)))
    result=dict(donor_sha256=D.SHA,scope='Untimed original instructions, natural reset/start sequences; no host/native claim',cases=cases)
    (O/'orientation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(O),cases=[dict(name=z['name'],transitions=z['transitions'],final=z['samples'][-1])for z in cases])))
if __name__=='__main__':main()

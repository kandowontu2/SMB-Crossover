"""Finite real-6502 interrupt/scratch contract for the isolated WWF component.

This is not the MMC5/common cartridge interrupt implementation. Native donor
callbacks remain dynamic oracles; cuts surround their assembled marshaling.
"""
from pathlib import Path
import copy,json,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from py65.devices.mpu6502 import MPU
from private_build_outputs_v1 import validate
import wwf_c2_relocation_model_v2 as M
T=M.T;O=R/'build/wwf-c2-interrupt-controls-v1'

def compile_probe():
    base=(M.L/'irq.s').read_text().split('WfProbeIRQ:\n',1)[1]
    # NMI permits a legal nested IRQ after its own eight borrowed bytes are saved.
    nmi=base.replace(' lda #$5a',' cli\n lda #$5a',1)
    text='.setcpu "6502"\n'+''.join(f'WfR{i}=${a:02x}\n'for i,a in enumerate(M.SCOPED))
    text+='.segment "PROBE_NMI"\n'+nmi+'.segment "PROBE_IRQ"\n'+base
    (O/'probe.s').write_text(text)
    (O/'probe.cfg').write_text('MEMORY { N:start=$7800,size=$80,file="'+str(O/'probe.bin').replace('\\','/')+'",fill=yes; I:start=$7880,size=$80,file="'+str(O/'probe.bin').replace('\\','/')+'",fill=yes; }\nSEGMENTS { PROBE_NMI:load=N,type=ro; PROBE_IRQ:load=I,type=ro; }\n')
    commands=[['ca65.exe',str(O/'probe.s'),'-o',str(O/'probe.o'),'-l',str(O/'probe.lst'),'--create-dep',str(O/'probe.dep')],['ld65.exe','-C',str(O/'probe.cfg'),str(O/'probe.o'),'-o',str(O/'probe.bin'),'-m',str(O/'probe.map')]]
    for i,cmd in enumerate(commands):
        cmd[0]=str(R/'tools/Windows/cc65/bin'/cmd[0]);guard=validate(cmd,O,cwd=R)
        z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        T.save(O/f'build-{i}.json',dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stderr
    return (O/'probe.bin').read_bytes()

def clone(b,c):
    memo={id(v):v for v in [b.prg,b.proof,b.labels,b.map,b.inverse]}
    d=copy.deepcopy(b,memo);d.hook=None;d.cpu=None;d.ram=M.StateProjection(d)
    n=MPU(memory=d,pc=c.pc);n.a,n.x,n.y,n.p,n.sp=c.a,c.x,c.y,c.p,c.sp;n.processorCycles=c.processorCycles
    return d,n

def resume(b,c):
    for _ in range(100000):
        if c.pc==0x7f00:return
        if c.pc in b.oracles:M.native_callback(b,c,b.oracles[c.pc]);continue
        b.mark(c);assert b[c.pc]!=0,hex(c.pc);c.step()
    raise AssertionError(('Resume bound',hex(c.pc)))

def probe(b,c,kind,code):
    before=(c.pc,T.cpu_state(c),bytes(b.mem[:0x100]),bytes(b.mem[0x200:0x800]),bytes(b.mem[c.sp+0x101:0x200]),bytes(b.mem[0xc000:0xe000]))
    b.mem[0x7800:0x7900]=code;b.mem[0xfffa:0xfffc]=(0x7800).to_bytes(2,'little');b.mem[0xfffe:]=(0x7880).to_bytes(2,'little')
    if kind=='IRQ':assert not c.p&4;c.irq()
    else:c.nmi()
    low=c.sp;nested=False
    for i in range(1000):
        if i and c.pc==before[0]and c.sp==before[1][-1]:break
        if kind=='NMI+IRQ'and not nested and not c.p&4:
            assert 0x7800<=c.pc<0x7880;c.irq();nested=True
        low=min(low,c.sp);c.step()
    else:raise AssertionError(('Probe return',kind,hex(c.pc),c.sp,before[:2]))
    assert kind!='NMI+IRQ'or nested
    after=(c.pc,T.cpu_state(c),bytes(b.mem[:0x100]),bytes(b.mem[0x200:0x800]),bytes(b.mem[c.sp+0x101:0x200]),bytes(b.mem[0xc000:0xe000]))
    assert before==after,('Actual RTI preservation',kind,before[:2],after[:2])
    return low

def main():
    assert not O.exists();O.mkdir();report=dict(passed=False,isolated_CPU_lab=True,native_host=False,no_host_allocation=True,cuts=[])
    seen=set();low=255;code=compile_probe();prior=json.loads((T.L/'build-proof.json').read_text());prg=T.W.W.raw();snapshot=(T.W.N/'capture/ram-match-entry.bin').read_bytes()
    try:
        def hook(b,c):
            nonlocal low
            if c.pc in seen:return
            seen.add(c.pc);start=len(b.state_events);cb=len(b.callbacks)
            uninterrupted,u=clone(b,c);resume(uninterrupted,u)
            kinds=['NMI','NMI+IRQ']+([]if c.p&4 else['IRQ'])
            for kind in kinds:
                interrupted,n=clone(b,c);low=min(low,probe(interrupted,n,kind,code));resume(interrupted,n)
                assert T.cpu_state(n)==T.cpu_state(u)
                assert interrupted.shadow==uninterrupted.shadow and interrupted.mem[0xc000:0xe000]==uninterrupted.mem[0xc000:0xe000]
                assert interrupted.mem[:0x100]==uninterrupted.mem[:0x100]and interrupted.mem[0x200:0x800]==uninterrupted.mem[0x200:0x800]
                assert interrupted.mem[n.sp+0x101:0x200]==uninterrupted.mem[u.sp+0x101:0x200]
                assert [e for e in interrupted.state_events[start:]if e is not None]==[e for e in uninterrupted.state_events[start:]if e is not None]
                assert interrupted.callbacks[cb:]==uninterrupted.callbacks[cb:]and interrupted.io==uninterrupted.io and interrupted.apu==uninterrupted.apu and interrupted.bank==uninterrupted.bank
                assert interrupted.pointer_pending==uninterrupted.pointer_pending
                report['cuts'].append(dict(PC=c.pc,original_PC=b.reverse.get(c.pc),kind=kind,foreground_SP=c.sp,returned=T.cpu_state(n)))
        # Reach actual helper, wrapper, branch and callback seams from both actors.
        for actor in [0,1]:
            for ch in T.W.W.tables(prg):
                b=M.C2Bus(prg,snapshot,prior,'relocated');b.hook=hook
                b.ram[0x2a+int(actor==0)],b.ram[0x2b-int(actor==0)]=ch['id'],(ch['id']+1)%6
                M.call(b,'WfInitDescriptors')
                for at in [0x3c,0x3d,0x3e,0x3f,0x40,0x41,0x8b,0x8c,0xa2,0xa3,0xa4,0xa5,0xcb,0xcc,0xc0,0xc1]:b.ram[at]=0
                b.ram[0xd+2*actor],b.ram[0xe+2*actor]=0xc0,0xc0
                M.call(b,'WfSelectAction',x=actor,y=2*actor);M.call(b,'WfAdoptRequests')
                b.ram[0xd+2*actor]=b.ram[0xe+2*actor]=0
                for tick in range(32):
                    b.ram[0x71]=(tick*2+actor)%6;b.ram[0x8d]=(snapshot[0x8d]+tick*2+actor)&255;M.call(b,'WfVmTick')
            print(json.dumps(dict(actor=actor,seams=len(seen),cuts=len(report['cuts']))),flush=True)
        report.update(passed=True,seams=len(seen),actual_interrupt_cuts=len(report['cuts']),minimum_interrupt_SP=low,probe_bytes=len(code),scope='Actual assembled private NMI/IRQ scratch-saving probes and legal nested IRQ. Every captured instruction resumes the same compiled API to completion. Native donor callbacks execute dynamically between assembled wrapper cuts; their internal instructions and actual common/MMC5 interrupt code are not claimed.')
    except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        files=[Path(__file__),Path(M.__file__),M.L/'build-proof.json',M.L/'vm.bin',M.L/'c2.bin',M.L/'environment.bin',O/'probe.s',O/'probe.cfg',O/'probe.bin',O/'build-0.json',O/'build-1.json']
        report['bindings']={str(p.resolve()):T.sha(p)for p in files};T.save(O/'controls.json',report);print(json.dumps({k:report.get(k)for k in ['passed','seams','actual_interrupt_cuts','minimum_interrupt_SP','error']}),flush=True)
if __name__=='__main__':main()

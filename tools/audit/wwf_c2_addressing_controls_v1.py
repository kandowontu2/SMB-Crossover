"""Actual linked instruction/pointer helpers, bounded actor index semantics."""
from pathlib import Path
import json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from py65.devices.mpu6502 import MPU
import wwf_c2_relocation_model_v2 as M
T=M.T;O=R/'build/wwf-c2-addressing-controls-v1'

def main():
    assert not O.exists();O.mkdir();report=dict(passed=False,source_CPU_lab=True,checks={})
    original=T.W.W.raw();vm=(M.L/'vm.bin').read_bytes();c2=(M.L/'c2.bin').read_bytes();cases=0
    try:
        sites=[(int(pc),v)for pc,v in M.P['instructions'].items()if v['mode']in['zpx','zpy']]
        assert len(sites)==405 and all(v['mode']=='zpx'and v['value']<255 for _,v in sites)
        for pc,v in sites:
            old=bytearray(65536);new=bytearray(65536);old[0x8000:0x8002]=original[pc-0x8000:pc-0x8000+2]
            at=M.P['labels'][f'WfN_{pc:04X}'];new[0x8000:0x8003]=vm[at-0xa000:at-0xa000+3]
            oc,nc=MPU(memory=old,pc=0x8000),MPU(memory=new,pc=0x8000)
            om,omod=oc.disassemble[old[0x8000]];nm,nmod=nc.disassemble[new[0x8000]]
            assert om==nm and omod=='zpx'and nmod=='abx'
            assert new[0x8001]+256*new[0x8002]==0xc000+v['value']
            for x in [0,1]:
                address=v['value']+x;assert address<256
                for bits in range(64):
                    flags=0x30|(bits&15)|((bits&48)<<2)
                    for value in [0,1,127,128,255]:
                        old[address]=new[0xc000+address]=value
                        for cpu in [oc,nc]:cpu.pc=0x8000;cpu.a=0x53;cpu.x=x;cpu.y=0x7b;cpu.p=flags;cpu.sp=0xed;cpu.step()
                        assert T.cpu_state(oc)==T.cpu_state(nc)and old[address]==new[0xc000+address],('Actual indexed instruction',hex(pc),x,flags,value)
                        cases+=1
        report['checks']['actor_indexed']=dict(passed=True,actual_source_sites=405,cases=cases,X_domain=[0,1],formal_effective_address='base+X<=255 for every declared actor0/1 indexed state site; absoluteC000+base+X equals relocated nativeZP address. Same actual opcode operation, CVDI/NZ flags compared.',limitation='Illegal external actorX is not an API. Constructor indexed palette loop is originally absolute and retains full16-bit addressing.')
        pc=0xe9bb;at=M.P['labels']['WfN_E9BB'];old=bytearray(65536);new=bytearray(65536)
        old[0x8000:0x8003]=original[pc-0x8000:pc-0x8000+3];new[0x8000:0x8003]=vm[at-0xa000:at-0xa000+3]
        assert bytes(new[0x8000:0x8003])==bytes([0x99,0xd3,0xc0])
        count=0
        for y in range(256):
            for bits in range(64):
                flags=0x30|(bits&15)|((bits&48)<<2)
                for a in [0,1,127,128,255]:
                    for data in [old,new]:data[(0 if data is old else 0xc000)+0xd3+y]=0x96
                    oc,nc=MPU(memory=old,pc=0x8000),MPU(memory=new,pc=0x8000)
                    for cpu in [oc,nc]:cpu.a=a;cpu.x=1;cpu.y=y;cpu.p=flags;cpu.sp=0xed;cpu.step()
                    assert T.cpu_state(oc)==T.cpu_state(nc)and old[0xd3+y]==new[0xc0d3+y]==a
                    count+=1
        report['checks']['absolute_indexed_stack_alias']=dict(passed=True,cases=count,actual_source_PC=pc,Y_domain=[0,255],Y_FF='Original00D3+FF=01D2 is deliberately preserved at selectedC1D2, not silently wrapped or written to the host stack.')
        counts=0;helper_bytes={}
        for p,pair in [(int(p,16),pair)for p,pair in M.P['pair_helpers'].items()]:
            data=bytearray(65536);data[0xc000:0xe000]=c2;data[0xc000+p:0xc002+p]=(0xc600).to_bytes(2,'little')
            data[0xc600:0xc700]=bytes((i*37+11)&255 for i in range(256));entry=M.P['labels'][f'WfReadPair{p:02X}']
            for y in range(256):
                for bits in range(64):
                    flags=0x30|(bits&15)|((bits&48)<<2)
                    for x in [0,1]:
                        for i,a in enumerate(M.SCOPED):data[a]=0xa0+i
                        c=MPU(memory=data,pc=entry);c.a=0x53;c.x=x;c.y=y;c.p=flags;c.sp=253;c.stPushWord(0x7eff)
                        for _ in range(10):
                            if c.pc==0x7f00:break
                            c.step()
                        assert c.pc==0x7f00 and c.sp==253 and c.x==x and c.y==y
                        value=data[0xc600+y];expected=(flags&~0x82)|(0x80 if value&128 else 0)|(2 if value==0 else 0)
                        assert c.a==value and c.p==expected
                        assert all(data[a]==(0 if i==pair else 0xc6 if i==pair+1 else 0xa0+i)for i,a in enumerate(M.SCOPED))
                        counts+=1
            helper_bytes[hex(p)]=dict(pair=pair,entry=entry,bytes=list(data[entry:entry+13]))
        report['checks']['indirect_helpers']=dict(passed=True,cases=counts,helpers=helper_bytes,physical_scoped_pairs=M.SCOPED,aliases='1F and25 share the same pair in separate read-helper phases; each reloads the canonical C2 pointer before dereference. Dispatch1F is absolute indirect and does not borrow a pair.',live_flags='LDA resultNZ; originalCVDI,X,Y and actual returnSP retained. Only the declared two scratch bytes change before outer compiled scope restores all8.')
        report.update(passed=True)
    except Exception as e:report.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        report['bindings']={str(p.resolve()):T.sha(p)for p in [Path(__file__),Path(M.__file__),M.L/'build-proof.json',M.L/'vm.bin',M.L/'c2.bin',T.W.W.ROM]}
        T.save(O/'controls.json',report);print(json.dumps(dict(passed=report['passed'],checks={k:v.get('cases')for k,v in report['checks'].items()},error=report.get('error'))))
if __name__=='__main__':main()

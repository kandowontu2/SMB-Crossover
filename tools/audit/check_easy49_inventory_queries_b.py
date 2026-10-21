"""Execute compiled mode/ownership queries with independent semantic oracles.

All physical RAM is checked, including precisely predicted6502 stack writes.
Hard/later-character results also compare full registers with the user ROM.
No native hardware, pickup traversal or full Easy implementation is claimed.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import time

R=Path(__file__).resolve().parents[2]
H=R/'build/verification/root49-easy-inventory-base-a'
B=R/'build/verification/root49-easy-hard-user-baseline-a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
RETURN=0x5d00


def main():
    sys.dont_write_bytecode=True
    from py65.devices.mpu6502 import MPU
    sys.path.insert(0,str(R/'build/verification/agent49g-samus-crouch-fix-proposal-b'))
    from image import Image
    report_path=H/'query-cpu-b.json';assert not report_path.exists()
    prep=json.loads((H/'build-review-b.json').read_text())
    assert prep['status']=='PASS_PRIVATE_LEGACY_INVENTORY_BOUNDARY_LAYOUT_ONLY'
    assert all(sha(H/'source'/n)==h for n,h in prep['actual_source_hashes'].items())
    baseline=json.loads((B/'baseline.json').read_text())
    assert all(sha(R/n)==h for n,h in baseline['current_source_hashes'].items())
    template=bytes((i*37+19)&255 for i in range(10240))
    class Memory:
        def __init__(self,im,bank):
            self.im=im;self.bank=bank;self.ram=bytearray(template);self.writes=[]
        @staticmethod
        def physical(a):
            if a<0x2000:return a&2047
            if 0x6000<=a<0x8000:return 2048+a-0x6000
            raise AssertionError(('Unexpected hardware access',hex(a)))
        def __getitem__(self,a):
            if a>=0x8000:
                bank=62 if a<0xa000 else self.bank if a<0xc000 else 0 if a<0xe000 else 63
                return self.im.raw[16+bank*8192+(a&8191)]
            return self.ram[self.physical(a)]
        def __setitem__(self,a,v):
            v&=255;self.ram[self.physical(a)]=v;self.writes.append((a,v))
        def put(self,n,v,i=0):self.ram[self.physical(self.im.ram[n]+i)]=v&255
    def execute(im,name,case):
        mode,char,power,item,lo,hi,p=case
        hook=im.hook(name);mem=Memory(im,hook['physical_bank'])
        mem.put('CrossoverBehaviorVersion',mode);mem.put('SelectedCharacter',char);mem.put('PlayerStatus',power)
        if name!='InventorySupported':
            mem.put('InvOwnedLo',lo,char);mem.put('InvOwnedHi',hi,char)
        cpu=MPU(memory=mem,pc=hook['address']);cpu.a=item;cpu.x=0xa5;cpu.y=0x5a;cpu.p=p;cpu.sp=0xe4
        mem.ram[0x1e5]=(RETURN-1)&255;mem.ram[0x1e6]=(RETURN-1)>>8
        initial=bytes(mem.ram);stack=[];steps=0
        while cpu.pc!=RETURN:
            pc=cpu.pc;op=mem[pc];sp=cpu.sp
            if op==0x20:
                stack.extend([(0x100+sp,((pc+2)>>8)&255),(0x100+((sp-1)&255),(pc+2)&255)])
            elif op==0x48:stack.append((0x100+sp,cpu.a))
            elif op==0x08:stack.append((0x100+sp,cpu.p|0x30))
            cpu.step();steps+=1;assert steps<256,(name,case,pc)
        assert mem.writes==stack,('Queries may only perform exact ISA stack writes',name,case,mem.writes,stack)
        expected=bytearray(initial)
        for a,v in stack:expected[Memory.physical(a)]=v
        assert mem.ram==expected,'All10240 physical RAM bytes including stack exact'
        return dict(carry=cpu.p&1,regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc),
            cycles=cpu.processorCycles,initial=initial,final=bytes(mem.ram),stack=stack)
    report=dict(status='RUNNING_COMPILED_MODE_QUERY_COMPONENT',script_sha256=sha(__file__),
        build_review_sha256=sha(H/'build-review-b.json'),baseline_sha256=sha(B/'baseline.json'),results=[],
        complete_Easy_behavior=False,main_changed=False,accepted_release=False,goal_complete=False)
    def save():report_path.write_text(json.dumps(report,indent=2)+'\n')
    save();t=time.monotonic()
    for mapper in ['mmc3','mmc5']:
        old=Image(B/('smb-crossover-'+mapper+'.nes'))
        new=Image(H/('source/build/smb-crossover-'+mapper+'.nes'))
        assert old.ram==new.ram
        digest=hashlib.sha256();counts={};differential=0;executions=0
        def one(name,case):
            nonlocal differential,executions
            mode,char,power,item,lo,hi,p=case
            classic=mode==0 and 1<=char<=5
            if name=='InventorySupported':wanted=not classic and char in [1,2,3,4,5,9,10,11]
            else:
                owned=bool((lo|(hi<<8))&(1<<item))
                wanted=not classic and owned and(name=='InventoryHasRaw'or power>0)
            actual=execute(new,name,case);executions+=1
            assert bool(actual['carry'])==bool(wanted),(mapper,name,case,actual['regs'],wanted)
            if not classic:
                control=execute(old,name,case);executions+=1
                assert actual['initial']==control['initial']
                assert actual['regs']==control['regs'],('Hard/later ABI',mapper,name,case,actual['regs'],control['regs'])
                # Candidate adds a helper call; predict its exact stack effects,
                # never ignore stack or mask broad RAM ranges in the comparison.
                assert {a for a,v in control['stack']}<={a for a,v in actual['stack']}
                expected=bytearray(control['final'])
                for a,v in actual['stack']:expected[Memory.physical(a)]=v
                assert actual['final']==expected
                differential+=1
            counts[name]=counts.get(name,0)+1
            digest.update(bytes((mode,char,power,item,lo,hi,p,actual['carry'])))
        for mode,char,p in itertools.product(range(2),range(14),range(256)):
            one('InventorySupported',(mode,char,2,0x37,0,0,p))
        masks=[(0,0),(255,0),(0,255),(255,255),(170,85),(85,170)]
        chars=[1,2,3,4,5,9,10,11]
        for mode,char,item,mask,p in itertools.product(range(2),chars,range(16),masks,[0,1,2,8,64,128,255]):
            one('InventoryHasRaw',(mode,char,2,item,*mask,p))
        for mode,char,power,item,mask,p in itertools.product(range(2),chars,range(3),range(16),masks,[0,128,255]):
            one('InventoryHas',(mode,char,power,item,*mask,p))
        report['results'].append(dict(mapper=mapper,semantic_cases=sum(counts.values()),groups=counts,
            actual_compiled_executions=executions,full_ABI_and_RAM_nonclassic_differentials=differential,
            digest=digest.hexdigest(),ROM_sha256=sha(new.path),user_control_ROM_sha256=sha(old.path),
            physical_RAM_bytes_checked_per_call=10240,stack_writes_predicted_individually=True))
        save();print(mapper,counts,'PASS',flush=True)
    assert all(sha(R/n)==h for n,h in baseline['current_source_hashes'].items())
    report.update(status='PASS_COMPILED_LEGACY_INVENTORY_QUERY_BOUNDARY',elapsed_seconds=time.monotonic()-t,
        semantic_cases=sum(q['semantic_cases']for q in report['results']),
        actual_compiled_executions=sum(q['actual_compiled_executions']for q in report['results']),
        limits='RP2A03 pure query component viaNMOS py65; no hardware interrupts, ordinary pickups/energy drops, Spend commit or full characterEasy behavior claim. Native checks and integration remain pending.')
    save();print(report['status'],sha(report_path),flush=True)


if __name__=='__main__':main()

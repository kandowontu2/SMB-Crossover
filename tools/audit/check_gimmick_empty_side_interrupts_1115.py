"""Paired actual IRQ/busy-NMI at reached Gimmick query/shift instructions."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json
import check_gimmick_empty_side_components_1115 as Units

C,N,W=Units.C,Units.N,Units.W


def run(actual):
    raw,proposal=C.current_proposal(actual);assert C.current_inverse(raw)==actual
    base=N.NesMPU;seen=set();rows=[];counts=Counter();effects=Counter();minimum=255;trace=sha256()
    class Bus(N.Bus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'checking',False)and 0xb872<=at<0xb92d and self.rawtags[1]==152:
                raise AssertionError(('ISR read changed Gimmick code/data',hex(at)))
            return super().__getitem__(at)
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),m.rawtags[:],m.chr_latches[:])
    def pair(cpu,kind):
        nonlocal minimum
        regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc);machines=[];before=[]
        for image in(raw,actual):
            m=N.fork(cpu.memory);m.__class__=Bus;m.bundle=dict(m.bundle,raw=image)
            for window,tag in enumerate(m.rawtags[:]):
                if tag&128:m.raw_page(window,tag)
            c=base(memory=m,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            before.append(dict(transport=transport(m),upper=bytes(m[0x101+c.sp:0x200]),native=bytes(m[:0x800]),private=[bytes(b)for b in m.ram]))
            m.checking=True;m[0x5204]=128;c.irq()if kind=='IRQ'else c.nmi();machines.append((c,m))
        for step in range(100000):
            a,ma=machines[0];b,mb=machines[1]
            ra=(a.a,a.x,a.y,a.p&239,a.sp,a.pc);rb=(b.a,b.x,b.y,b.p&239,b.sp,b.pc)
            assert ra==rb,('Paired ISR CPU',kind,regs,ra,rb)
            minimum=min(minimum,a.sp,b.sp)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and b.sp<=regs[4]
            instruction=bytes(ma[a.pc:a.pc+3]);assert instruction==bytes(mb[b.pc:b.pc+3])and ma.rawtags==mb.rawtags
            trace.update(bytes((a.pc&255,a.pc>>8,a.sp,a.p&239))+instruction)
            assert ma[a.pc]and mb[b.pc];a.step();b.step()
        else:raise AssertionError('Actual ISR return bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:]),('Interrupted ABI',kind,regs)
        for i,(c,m)in enumerate(machines):
            m.checking=False
            assert transport(m)==before[i]['transport'],('Interrupted live scratch/SMC/maps',kind,regs)
            assert bytes(m[0x101+regs[4]:0x200])==before[i]['upper'],'ISR above caller SP'
        left,right=(m for c,m in machines)
        assert bytes(left[:0x800])==bytes(right[:0x800]),'Exact native RAM/audio/stack pair'
        assert left.ram==right.ram,'Exact private RAM pair, including clock/input effects'
        for at,(old,new)in enumerate(zip(before[0]['native'],bytes(left[:0x800]))):
            if old!=new and not 0x100<=at<0x200:effects[(kind,at,old,new)]+=1
        counts[kind]+=1
    class CPU(base):
        def step(self):
            m=self.memory
            if hasattr(m,'rawtags')and m.bundle.get('raw')==raw and m.rawtags[1]==152 and 0xb872<=self.pc<0xb92d:
                key=(self.pc,self.sp,self.p&193)
                if key not in seen:
                    assert not self.p&4;seen.add(key);assert len(seen)<=512
                    pair(self,'IRQ');assert N.get(m,'NmiDisable')==255;pair(self,'busyNMI')
                    rows.append(dict(PC=self.pc,SP=self.sp,P=self.p))
            return super().step()
    m=Units.seed(Units.bundle(raw,True));calls=0
    with patch.object(N,'NesMPU',CPU):
        for owner in(26,0):
            for index in range(7):
                for tile in(0,35,81,96):
                    N.put(m,SelectedCharacter=owner)
                    x,y=207,137;xx=x+1024+(8,5,11,5,5,11,11)[index]
                    ptr=W.address(m.bundle,'Block_Buffer_2'if xx//256&1 else'Block_Buffer_1')+(xx%256)//16
                    row=((((y+(18,32,32,22,30,22,30)[index])&255)&240)-32)&255;m[(ptr+row)&65535]=tile
                    role='GmHead'if index==0 else'GmFoot'if index<3 else'GmSide'
                    N.invoke(m,role,a=93,x=77,y=index-1 if role=='GmFoot'else index,p=0xe1);calls+=1
        for slot in(0,1):
            N.put(m,SelectedCharacter=26,GmRam00AE=239,GmRam00B8=4,GmRam009A=143,GmRam00A4=10,ScreenLeft_X_Pos=255,ScreenLeft_PageLoc=3)
            N.invoke(m,'GmScreenPoint',a=83,x=slot,y=77,p=0xe1);calls+=1
    assert counts['IRQ']==counts['busyNMI']==len(rows)and len(rows)>90
    return dict(passed=True,runtime_SHA256=sha256(raw).hexdigest(),parent16a_SHA256=sha256(actual).hexdigest(),declared_component_calls=calls,
        paired_interrupt_counts=dict(counts),reached_contexts=len(rows),reached_PCs=sorted({q['PC']for q in rows}),minimum_ISR_SP=minimum,
        exact_ISR_path_SHA256=trace.hexdigest(),all_AXYP_SP_and_live_R0_R7_SMC_maps_preserved=True,
        exact_paired_native_private_audio_stack_effects=True,no_changed_code_or_data_ISR_reads=True,
        native_effects=[dict(kind=k[0],address=k[1],before=k[2],after=k[3],cases=v)for k,v in sorted(effects.items())],
        scope='Reached CPU component contexts; actual unchanged IRQ/busyNMI bodies, no ISR stubs or native execution',outputs=0,Mesen_run=False)


if __name__=='__main__':
    actual=C.ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Gimmick ISR check attempted files/launch')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch('subprocess.Popen',forbid):q=run(actual)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)

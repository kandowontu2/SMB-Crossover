"""Reached f7 helper IRQ/busyNMI transport, plus8 actual post-head states."""
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from collections import Counter
import inspect,json
import check_sonic_hidden_native_callback_f7c9_1116 as Source

F=Source.F
SOURCE_SHA='76442c0f0362192ef95cbefbc9a80b00892c702622c7927f916bc14f4e9108b1'


def slim(m):
    z=list.__new__(type(m));list.extend(z,list.__iter__(m))
    for k,v in vars(m).items():setattr(z,k,[]if k in('writes','ram_writes','ppu_log','blocked')else v if k=='bundle'else deepcopy(v))
    return z


def run(raw):
    assert F.H(Path(Source.__file__).read_bytes())==SOURCE_SHA
    parent=F.C.inverse(raw);N=F.N;q=F.bindings(raw);base=N.NesMPU
    seen=set();counts=Counter();cuts=[];trajectory=[];minimum=255;active_return=None;runtime=None;head=False;nativehead=None
    def tag(m,pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def regs(c):return(c.a,c.x,c.y,c.p&239,c.sp,c.pc)
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),list(m.rawtags),list(m.chr_latches))
    def back(m,old):
        m.bundle=dict(m.bundle,raw=parent if old else raw)
        m.ram[3][0x1b26:0x1b39]=F.C.OLD if old else F.C.NEW
        m.ram[2][0x1344:0x1371]=b'\xff'*45 if old else F.C.HELPER
        for k in(2,3):m.ram[k][0x1fe0:0x1ff0]=F.C.OLD_COOKIE if old else F.C.COOKIE
        for slot,t in enumerate(m.rawtags):
            if t&128:m.raw_page(slot,t)
    def finish(m,c,stop):
        for _ in range(150000):
            if(c.pc,c.sp,tag(m,c.pc))==stop:return
            assert m[c.pc],('ContinuationBRK',hex(c.pc),c.sp);base.step(c)
        raise AssertionError(('Actual dynamic Main continuation bound',hex(c.pc),c.sp,stop))
    def paired(c,kind):
        nonlocal minimum
        original=c.memory;before=regs(c);pairs=[];snap=[]
        assert active_return is not None
        for old in(False,True):
            m=slim(original);back(m,old);z=base(memory=m,pc=c.pc);z.a,z.x,z.y,z.p,z.sp=c.a,c.x,c.y,c.p,c.sp
            snap.append(dict(private=[bytes(v)for v in m.ram],live=bytes(m[0x101+z.sp:0x200]),transport=transport(m),skip=N.get(m,'NmiSkipped')))
            z.irq()if kind=='IRQ'else z.nmi();pairs.append((m,z))
        for _ in range(50000):
            (a,ca),(b,cb)=pairs;minimum=min(minimum,ca.sp,cb.sp)
            assert regs(ca)==regs(cb)and a.rawtags==b.rawtags
            if(ca.pc,ca.sp)==(c.pc,c.sp):break
            assert a[ca.pc]and bytes(a[ca.pc:ca.pc+3])==bytes(b[cb.pc:cb.pc+3]),('Actual ISR opcode parity',kind,hex(ca.pc))
            base.step(ca);base.step(cb)
        else:raise AssertionError('Actual ISR bounded return')
        for(m,z),old in zip(pairs,snap,strict=True):
            assert regs(z)==before and[bytes(v)for v in m.ram]==old['private']and transport(m)==old['transport']
            assert bytes(m[0x101+z.sp:0x200])==old['live']
            assert N.get(m,'NmiSkipped')==(old['skip']+int(kind=='busyNMI'))&255
        assert bytes(pairs[0][0][:0x800])==bytes(pairs[1][0][:0x800])
        for m,z in pairs:back(m,False);finish(m,z,active_return)
        (a,ca),(b,cb)=pairs
        assert regs(ca)==regs(cb)and[bytes(v)for v in a.ram]==[bytes(v)for v in b.ram]
        assert bytes(a[:0x800])==bytes(b[:0x800])and bytes(a[0x6000:0x8000])==bytes(b[0x6000:0x8000])and transport(a)==transport(b)
        assert bytes(a[0x101+ca.sp:0x200])==bytes(b[0x101+cb.sp:0x200])
        counts[kind]+=1;counts['paired_actual_Main_returns']+=2
    class CPU(base):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self.audit_worker_return=None
        def step(self):
            nonlocal active_return,head,nativehead
            m=self.memory;t=tag(m,self.pc)
            if m.bundle.get('raw')is raw:
                if(t,self.pc)==(q['hooks']['GameLoop']['tag'],q['hooks']['GameLoop']['PC']):
                    sp=self.sp;pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                    active_return=(pc,(sp+2)&255,tag(m,pc))
                if(t,self.pc)==(3,0xbbb0):
                    sp=self.sp;pc=(m[0x100+((sp+1)&255)]+256*m[0x100+((sp+2)&255)]+1)&65535
                    self.audit_worker_return=(pc,(sp+2)&255,tag(m,pc))
                if(t,self.pc)==(q['hooks']['PlayerHeadCollision']['tag'],q['hooks']['PlayerHeadCollision']['PC'])and self.a==96:
                    head=True;nativehead=dict(PC=self.pc,SP=self.sp,sourceY=list(m.ram[2][0x73:0x76]),sourceVY=list(m.ram[2][0x60:0x63]),flags=m.ram[2][0x30])
                if self.audit_worker_return==(self.pc,self.sp,t):
                    self.audit_worker_return=None
                    if head and len(trajectory)<8:
                        getter=runtime.globals().SONIC_SOURCE_POLICY
                        trajectory.append(dict(PC=self.pc,tag=t,SP=self.sp,C=self.p&1,nativeY=N.get(m,'Player_Y_Position'),
                            sourceY=list(m.ram[2][0x73:0x76]),sourceVY=list(m.ram[2][0x60:0x63]),flags=m.ram[2][0x30],
                            requested=m.controller_pad,saved=N.get(m,'SavedJoypadBits'),sourceInput=m.ram[2][0xa8],
                            HeadPending=m.ram[2][0x122],policy=list(getter())))
                if(t,self.pc)==(3,0xbb26)or(t==2 and 0xd344<=self.pc<0xd371):
                    tile=m.ram[2][0x104];category=tile if tile in(0x5f,0x60,0x67,0x68)else'ordinary'
                    key=t,self.pc,self.sp,self.p&239,m.ram[2][0xb7],m.ram[2][0xb8],category
                    if key not in seen:
                        seen.add(key);assert len(seen)<=256,'Distinct reached contexts bounded256'
                        assert N.get(m,'NmiDisable')==255
                        if not self.p&4:paired(self,'IRQ')
                        else:counts['I_masked_shapes']+=1
                        paired(self,'busyNMI')
                        cuts.append(dict(tag=t,PC=self.pc,SP=self.sp,P=self.p,A=self.a,X=self.x,Y=self.y,axis=key[4],negative=key[5],tile_class=category))
            return super().step()
    source=inspect.getsource(Source.run)
    old="rt.execute(fixture);rt.execute('SONIC_SOURCE_START()')"
    new="fixture=fixture.replace('SONIC_SOURCE_START=function()', 'SONIC_SOURCE_POLICY=function()return policy.lastJump,policy.hold,policy.clock,policy.phase,pad end;SONIC_SOURCE_START=function()');rt.execute(fixture);rt.execute('SONIC_SOURCE_START()');_runtime(rt)"
    assert source.count(old)==1;source=source.replace(old,new)
    def capture(rt):
        nonlocal runtime
        runtime=rt
    ns=dict(Source.__dict__,_runtime=capture);exec(compile(source,'<unchanged native observer plus read-only source policy export>','exec'),ns)
    with patch.object(N,'NesMPU',CPU):natural=ns['run'](raw,'sonic',900)
    assert natural['passed']and counts['IRQ']and counts['busyNMI']and len(trajectory)==8
    assert any(r['tile_class']==96 and r['PC']>=0xd357 for r in cuts)
    out=dict(passed=True,ROM_SHA256=F.PIN,source_SHA256=F.H(Path(__file__).read_bytes()),natural_callback_receipt=natural['receipt_SHA256'],
        counts=dict(counts),minimum_ISR_SP=minimum,reached_cuts=cuts,actual_head=nativehead,first8_post_head_original_returns=trajectory,
        X_Y_dependency='New classifier does not consume X/Y; each distinct reached PC/status/axis/negative/tileclass/SP context preserves actual AXYP and all live stack bytes through both ISRs and dynamic Main return.',
        regularNMI_scope='Actual new PCs are inside busyMain (NmiDisableFF); no regularNMI arm is invented.',
        no_whole_RAM_or_stack_mask=True,no_native_or_ROM_output=True,outputs=0)
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Reached ISR source gate attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(F.load_current_image())
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)

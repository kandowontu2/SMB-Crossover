"""Declared54b action/ABI/cold/foreign/lifecycle components; RAM only."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_rogue_missile_dispatch_54b_v2_1116 as J

C,N,W,Frames=J.C,J.N,J.W,J.Frames
REGS=('A','X','Y','P','minimum_SP')


def backing(m,raw):
    m.bundle=dict(m.bundle,raw=raw)
    for slot,tag in enumerate(list(m.rawtags)):
        if tag&128:m.raw_page(slot,tag)
    return m


def same(a,b):
    assert a.rawtags==b.rawtags and a.chr_latches==b.chr_latches
    assert [bytes(x)for x in a.ram]==[bytes(x)for x in b.ram]
    assert bytes(a[:0x800])==bytes(b[:0x800])
    assert bytes(a[0x15a:0x17b])==bytes(b[0x15a:0x17b])


def record(m,action,*,slot=208,x=108,y=123,vx=4,vy=0,onscreen=1,hit=0):
    # Deliberate source ABI component, never a natural shot/item witness.
    N.put(m,RdSlot=slot,RdFresh=0,RdHeld=0,RdRepeat=0)
    vals=dict(RdWAction=action,RdWRadiusY=2,RdWRadiusX=2,RdWFrame=40,
        RdWDelay=0,RdWReset=27,RdWAnim=27,RdWVY=vy,RdWVX=vx,RdWHit=hit,
        RdWOnScreen=onscreen,RdWHi=x>>8,RdWY=y,RdWX=x&255,RdWAge=2)
    for name,value in vals.items():m[W.address(m.bundle,name)+slot]=value
    if action==11:
        for name,value in(('RdWAnim',141),('RdWReset',141),('RdWAge',255)):
            m[W.address(m.bundle,name)+slot]=value


def flat(raw):
    parent=C.inverse(raw);mem=[]
    for image in(parent,raw):
        q=bytearray(65536);q[0xa000:0xc000]=image[16+121*8192:16+122*8192]
        q[0x5c2f]=208;mem.append(q)
    stops={0xafe2,0xb019,0xafcb,0xb0a5,0xaf80,0xb10a};counts=Counter()
    def execute(q,action,flags,a=85,x=7,y=91):
        q[0x5c40]=action;c=N.NesMPU(memory=q,pc=0xaf60);c.a,c.x,c.y,c.p,c.sp=a,x,y,flags|48,224
        for _ in range(60):
            if c.pc in stops:return(c.pc,c.a,c.x,c.y,c.p|48,c.sp,c.processorCycles)
            c.step()
        raise AssertionError(('Classifier bound',action,hex(c.pc)))
    for action in range(256):
        for p in range(256):
            if p&48:continue
            old,new=(execute(q,action,p)for q in mem)
            if action==11:assert(old[0],new[0])==(0xb10a,0xafe2)
            else:assert old==new,(action,p,old,new)
            counts['changed11'if action==11 else'exact_non11']+=1
    return dict(cases=sum(counts.values()),counts=dict(counts),all64meaningful_flag_combinations=True,
        no_native_or_gameplay_claim=True)


def interrupts(seed):
    import check_metal_head_bridge_1112 as Async
    base=N.NesMPU;m=N.fork(seed);record(m,11);m.controller_pad=0
    cuts=[];seen=set();counts=Counter();minimum=255;main_return=None
    def regs(c):return(c.pc,c.sp,c.a,c.x,c.y,c.p|48)
    def clone(model,c):
        q=N.fork(model);d=base(memory=q,pc=c.pc)
        d.a,d.x,d.y,d.p,d.sp=c.a,c.x,c.y,c.p,c.sp
        return q,d
    def finish(model,c,stop):
        for _ in range(200000):
            if(c.pc,c.sp)==stop:return
            assert model[c.pc],('Interrupted public continuation BRK',hex(c.pc));base.step(c)
        raise AssertionError(('Interrupted public continuation bound',hex(c.pc),stop))
    def compare_continuation(plain,cp,changed,ci,kind):
        assert regs(cp)==regs(ci)
        assert plain.rawtags==changed.rawtags and plain.chr_latches==changed.chr_latches
        assert [bytes(x)for x in plain.ram]==[bytes(x)for x in changed.ram]
        assert bytes(plain[0x15a:0x17b])==bytes(changed[0x15a:0x17b])
        assert bytes(plain[0x101+cp.sp:0x200])==bytes(changed[0x101+ci.sp:0x200])
        skipped=W.address(plain.bundle,'NmiSkipped')
        for at in list(range(0x100))+list(range(0x200,0x800)):
            expected=(plain[at]+1)&255 if kind=='lagNMI'and at==skipped else plain[at]
            assert changed[at]==expected,('Actual ISR native effect',kind,hex(at),plain[at],changed[at])
    class CPU(base):
        def step(self):
            nonlocal main_return,minimum
            if self.memory is m:
                tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if(tag,self.pc)==(254,33497):
                    main_return=((m[0x101+self.sp]+256*m[0x102+self.sp]+1)&65535,(self.sp+2)&255)
                if tag==249 and(self.pc==0xaf76 or 0xafe2<=self.pc<0xb019)and self.pc not in seen:
                    seen.add(self.pc);assert main_return is not None
                    for kind in('IRQ','lagNMI'):
                        if kind=='IRQ'and self.p&4:
                            q,c=clone(m,self);before=(regs(c),c.processorCycles);c.irq()
                            assert before==(regs(c),c.processorCycles);counts['maskedIRQ']+=1;continue
                        q,c=clone(m,self);plain,cp=clone(m,self);prior=regs(c)
                        minimum=min(minimum,Async.inject(c,base,kind))
                        assert regs(c)==prior
                        finish(q,c,main_return);finish(plain,cp,main_return)
                        compare_continuation(plain,cp,q,c,kind);counts[kind]+=1
                    cuts.append(dict(PC=self.pc,SP=self.sp,P=self.p,action=N.get(m,'RdWAction',208),
                        actual_Main_return_PC=main_return[0],actual_Main_return_SP=main_return[1]))
            return super().step()
    with patch.object(N,'NesMPU',CPU):Frames.frame(m,whole_pass=True)
    assert {0xaf76,0xafe2,0xafe4,0xafe7}<=seen and counts['lagNMI']and counts['IRQ']
    return dict(passed=True,cuts=cuts,counts=dict(counts),minimum_SP=minimum,
        actual_public_GameLoop_continuations_equal=True,all_meaningful_flags_SP_live_stack_SMC33_maps_private_exact=True,
        native_effect_exception='Only actual busyNMI NmiSkipped increment; dead ISR stack below returned SP is not live',
        declared_action11_record_component=True,natural_shot_claim=False)


def run(raw):
    composition=C.proposal(C.inverse(raw))[1];q=J.bindings(raw);seed=J.cold(raw);W.clear_logs(seed)
    # Actual normal cold executes owning image, all actor fields remain genuine.
    cold=[]
    for _ in range(4):seed.controller_pad=0;Frames.frame(seed,whole_pass=True)
    assert N.get(seed,'NumberofLives')==2 and N.get(seed,'RdVariant')==1
    for name in('RdHostEnabled','WxEnabled'):
        cold.append(dict(name=name,result=N.invoke(seed,name)))
        assert cold[-1]['result']['P']&1
    W.clear_logs(seed);parent=C.inverse(raw);full=Counter();cycles=Counter()
    for action in range(256):
        if action==11:continue
        for p in(0x31,0xf1):
            a,b=(backing(N.fork(seed),image)for image in(parent,raw))
            record(a,action);record(b,action)
            ra,rb=(N.invoke(m,'RdWxPreStep',p=p,x=255,y=0)for m in(a,b))
            assert ra==rb,('Actual complete PreStep non11 ABI/cost',action,p,ra,rb)
            same(a,b);full['non11_full_PreStep']+=1
    for action in(0,1,2,3,4,8,9,10):
        a,b=(backing(N.fork(seed),image)for image in(parent,raw));record(a,action);record(b,action)
        for _ in range(2):
            a.controller_pad=b.controller_pad=0;Frames.frame(a,whole_pass=True);Frames.frame(b,whole_pass=True)
        same(a,b);full['non11_two_complete_public_frames']+=1
    for owner,variant in((2,0),(0,0),(1,0),(3,0),(16,32),(16,64),(37,0),(40,0),(43,0)):
        a,b=(backing(N.fork(seed),image)for image in(parent,raw))
        for m in(a,b):N.put(m,SelectedCharacter=owner,RdVariant=variant)
        ra,rb=(N.invoke(m,'RdWxPreStep',p=0xf1)for m in(a,b));assert ra==rb;same(a,b)
        full['declared_foreign_preStep_reject']+=1
    # Current contact geometry and source lifetime primitives, not seeded
    # natural actors or a claim to a real earned missile.
    life=[]
    for label,values in(('motion',{}),('real static floor impact',dict(x=100,y=209)),
        ('offscreen-left',dict(x=65000)),('source hitflag impact',dict(hit=1))):
        a,b=(backing(N.fork(seed),image)for image in(parent,raw));record(a,11,**values);record(b,11,**values)
        before={n:N.get(b,n,208)for n in('RdWAction','RdWX','RdWY','RdWAnim','RdWFrame')}
        ra,rb=(N.invoke(m,'RdWxPreStep',p=0x31)for m in(a,b))
        after={n:N.get(b,n,208)for n in before};delta=rb['CPU']-ra['CPU'];cycles[label]=delta
        if label=='motion':assert after['RdWX']==before['RdWX']+4 and after['RdWFrame']==37
        elif label in('real static floor impact','source hitflag impact'):assert after['RdWAction']==4 and after['RdWFrame']==103
        else:assert after['RdWAction']==0
        life.append(dict(component=label,before=before,after=after,old_cycles=ra['CPU'],new_cycles=rb['CPU'],extra_cycles=delta))
    out=dict(passed=True,owning_SHA256=J.PIN,source_only=True,input=dict(J.INPUT),composition=composition,
        classifier=flat(raw),cold=cold,fullcaller_counts=dict(full),declared_lifecycle=life,interrupts=interrupts(seed),
        restored_cost_cycles=dict(cycles),AXYP_SP_full_private_native_transport_exact_non11=True,
        all_non11_code_and_cookie_bytes_exact=True,declared_record_components_not_natural_acquisition=True,outputs=0,native=False)
    out['receipt_SHA256']=J.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    raw=J.load_current_image()
    def deny(*a,**kw):raise AssertionError('Missile components attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=run(raw)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)

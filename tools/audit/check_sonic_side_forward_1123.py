"""Bounded linked-source proof of Sonic's exactffd708 side forwarder.

No files/native launch. Standing/walking/movement equality and actual native
ISR continuations; instruction savings do not qualify physical cadence.
"""
import json,time
from collections import Counter
from pathlib import Path
from unittest.mock import patch
from py65.devices.mpu6502 import MPU

import compose_sonic_side_forward_1123 as C
import check_dkjr_side_epoch_fast_1123 as F
import check_contra_force_fixed_layout_1122 as Layout

Q,N,W,B,H=F.Q,F.N,F.W,F.B,C.H
started=time.monotonic()


def emit(stage,**q):
    print('SONIC_SIDE '+json.dumps(dict(stage=stage,seconds=round(time.monotonic()-started,2),**q),separators=(',',':')),flush=True)


def deny(*a,**k):raise AssertionError('No outputs/native')


def cold(raw,owner):
    m=Q.enter(raw,owner)
    for i in range(300):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):return m,i
        B.main_step(m,0)
    raise AssertionError(('Cold bound',owner))


def foreign(parent,candidate):
    pages=[r[C.off(33,0xa000):C.off(33,0xa000)+8192]for r in(parent,candidate)]
    memories=[]
    for page in pages:
        m=[0]*65536;m[0xa000:0xc000]=page;memories.append(m)
    count=0;timing=Counter()
    for owner in range(256):
        if owner==43:continue
        for status in range(32,256):
            if not status&32:continue
            for accepted in((False,True)if owner==0 else(False,)):
                results=[];cost=[]
                for m in memories:
                    m[0x6002],m[0x16a],m[0x162],m[0x179]=owner,85,0,0
                    c=MPU(memory=m,pc=0xbea2);c.a,c.x,c.y,c.p,c.sp=85,7,91,status,236;c.stPushWord(0x5aff)
                    for _ in range(140):
                        if c.pc==0xbf38:break
                        if c.pc==0x15a:
                            if m[0x16c]+256*m[0x16d]!=0xbfb0:break
                            c.a=m[0x16a];c.p=(c.p&~1)|int(accepted);c.pc=c.stPopWord()+1;continue
                        assert m[c.pc],('Foreign BRK',owner,hex(c.pc));c.step()
                    else:raise AssertionError('Foreign bound')
                    results.append((c.pc,*F.registers(c,0xef),F.live_stack(c),m[0x16a],m[0x16c],m[0x16d],m[0x162],m[0x179]))
                    cost.append(c.processorCycles)
                assert results[0]==results[1],('Foreign ABI',owner,status,results)
                timing[(owner,cost[1]-cost[0])]+=1;count+=1
    histogram=Counter()
    for (owner,delta),n in timing.items():histogram[delta]+=n
    return dict(cases=count,added_cycles_histogram=dict(histogram),DK_added_cycles=sorted({d for o,d in timing if o==40}),
                native33_42_exact_cycles=all(d==0 for o,d in timing if o in(33,42)))


def qualify(parent):
    candidate,composition=C.proposal(parent);emit('composition',**composition)
    result=dict(composition=composition)
    result['foreign']=foreign(parent,candidate);emit('foreign',**result['foreign'])
    cuts={};counts=Counter();savings=Counter();seeds={}
    def collect(c,stop):
        tag,pc=F.point(c)
        if(tag==161 and(pc==C.HOOK or C.START<=pc<C.END))or pc in(0x15a,0x15d,0x16b,0x16e,0x174,0x17a):
            key=tag,pc,c.sp,c.p&5
            if key not in cuts:
                z=Q.clone(c);z.memory.combined_terminal=stop;cuts[key]=z
    def query(original,image,change=None,trace=False):
        c=F.rebound(original,image)
        if change:change(c.memory)
        stop=F.endpoint(c);hits=Counter()
        def watch(z):
            for label,point in(('public14',(193,0xb0b6)),('full',(193,0xaf27)),('epoch',(213,0xa8dc)),('generic',(217,0xbc58))):
                if F.point(z)==point:hits[label]+=1
            if trace:collect(z,stop)
        F.finish(c,stop,watch);return c,hits
    def paired(c,change=None,label='',trace=False):
        a,ac=query(c,parent,change);b,bc=query(c,candidate,change,trace)
        F.equal(a,b,label)
        assert ac['full']==bc['full']and ac['epoch']==bc['epoch'],('Check path differs',label,ac,bc)
        return a,b,ac,bc
    for owner in('Sonic','Super'):
        seed,start=cold(parent,owner)
        for _ in range(4):B.main_step(seed,0)
        seeds[owner]=seed;captures=[]
        class Capture:
            def run(self,c,stop):
                F.finish(c,stop,lambda z:captures.append(Q.clone(z))if F.point(z)==(254,0x90e4)else None)
        B.main_step(seed,0,Capture())
        assert len(captures)==4 and {c.y for c in captures}=={3,4,5,6},('Reached Sonic probes',owner)
        for original in captures:
            for status in range(32,256):
                if not status&32:continue
                for a,x in((0,0),(85,7),(255,255)):
                    c=Q.clone(original);c.a,c.x,c.p=a,x,status
                    old,new,ac,bc=paired(c,label=(owner,'ABI',original.y,status,a,x),trace=(status,a,x)==(0x21,85,7))
                    assert ac['generic']==1 and bc['generic']==0 and ac['public14']==bc['public14']==1,('Transport path',owner,original.y,status,a,x,ac,bc)
                    savings[old.processorCycles-new.processorCycles]+=1;counts['AXYP']+=1
            for epoch in range(256):
                def stale(m,epoch=epoch):m.ram[2][0x3f0]=epoch
                paired(original,stale,(owner,'epoch',original.y,epoch),epoch in(0,1))
                counts['epoch']+=1
            for bank in(2,3):
                for byte in range(16):
                    def bad(m,bank=bank,byte=byte):m.ram[bank][0x1fe0+byte]^=1;m.ram[2][0x3f0]=0
                    _,new,_,bc=paired(original,bad,(owner,'header',bank,byte),byte==0)
                    assert not new.p&1 and bc['full']==1
                    counts['complete_bad_header']+=1
                for byte in(0,1):
                    def prefix(m,bank=bank,byte=byte):m.ram[bank][0x1fe0+byte]^=1
                    _,new,_,bc=paired(original,prefix,(owner,'prefix',bank,byte),True)
                    assert not new.p&1 and bc['full']==1
                    counts['live_bad_prefix']+=1
            for field,value in(('FrameCounter',0),('GameEngineSubroutine',7),('GamePauseStatus',1),('TimerControl',1),('FamilyMainCommit',0)):
                paired(original,lambda m,field=field,value=value:N.put(m,**{field:value}),(owner,'scope',field,value),True)
                counts['scope']+=1
        for probe in(3,6):
            for tile in range(256):
                for p in(0x21,0x60,0xa5):
                    c=F.Side.new_leaf(seed,43,0,8,probe,253,176,tile,p)
                    paired(c,label=(owner,'cell',probe,tile,p))
                    counts['tile']+=1
        emit('owner_queries',owner=owner,cases=dict(counts),saved_cycles=dict(savings))
    for owner in(37,38,39,41,44,255):
        c=F.Side.new_leaf(seeds['Sonic'],owner,0,8,3,253,176,0,0x21)
        paired(c,label=('foreign continuation',owner),trace=True)
    result['queries']=dict(cases=dict(counts),saved_cycles_histogram=dict(savings))
    emit('queries',**result['queries'])
    profiles=[]
    for owner in('Sonic','Super','DK','Mini'):
        machines=[Q.enter(raw,owner)for raw in(parent,candidate)]
        for i in range(300):
            ready=[tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)for m in machines]
            assert ready[0]==ready[1]
            if all(ready):break
            for m in machines:B.main_step(m,0)
            F.foreground_equal(*machines,('cold',owner,i))
        else:raise AssertionError('Paired cold bound')
        phases={}
        sequence=(('settle',0,4),('idle',0,8),('Right',1,16),('tap',129,1),('air',1,10),('land',0,30),
                  ('down',4,2),('charge',132,1),('hold',4,2),('release',0,8))
        for name,pad,n in sequence:
            total=[0,0];nm=[0,0]
            for _ in range(n):
                for j,m in enumerate(machines):a,b=B.main_step(m,pad);total[j]+=a;nm[j]+=b
                F.foreground_equal(*machines,(owner,name))
            phases[name]=dict(returns=n,parent_Main=total[0]/n,candidate_Main=total[1]/n,saved_cycles=(total[0]-total[1])/n,NMI=[x/n for x in nm])
        row=dict(owner=owner,cold_Main=i,phases=phases);profiles.append(row);emit('profile',**row)
    result['profiles']=profiles
    result['upper']=Q.Old.upper_predicate(seeds['Sonic'],parent,candidate)
    needed={C.HOOK}|{i['pc']for i in C.program()['instructions']}
    reached={pc for tag,pc,sp,p in cuts if tag==161}
    eligible={pc for tag,pc,sp,p in cuts if tag==161 and not p&4}
    # The DK branch is reached by a real DK profile, separately collect its exact leaf.
    missing=needed-reached
    if missing:
        seed,_=cold(parent,'DK');captures=[]
        class DkCapture:
            def run(self,c,stop):F.finish(c,stop,lambda z:captures.append(Q.clone(z))if F.point(z)==(254,0x90e4)else None)
        B.main_step(seed,0,DkCapture())
        for c in captures:paired(c,label='DK changed ingress',trace=True)
        reached={pc for tag,pc,sp,p in cuts if tag==161};eligible={pc for tag,pc,sp,p in cuts if tag==161 and not p&4}
    assert needed<=reached and needed<=eligible,('Owned ISR coverage',sorted(needed-reached),sorted(needed-eligible))
    irq=Counter();minimum=255
    for original in cuts.values():
        for kind in('IRQ','busyNMI'):
            if kind=='IRQ'and original.p&4:continue
            a,b=Q.clone(original),Q.clone(original)
            for c in(a,b):N.put(c.memory,NmiDisable=255)
            before=F.registers(b,0xef);stack=F.live_stack(b);private=tuple(map(bytes,b.memory.ram));smc=bytes(b.memory[0x15a:0x17b])
            target=b.pc,b.sp
            if kind=='IRQ':b.irq()
            else:b.nmi()
            F.finish(b,target);minimum=min(minimum,b.sp)
            assert F.registers(b,0xef)==before and F.live_stack(b)==stack
            assert tuple(map(bytes,b.memory.ram))==private and bytes(b.memory[0x15a:0x17b])==smc
            for c in(a,b):F.finish(c,original.memory.combined_terminal)
            assert F.registers(a,0xef)==F.registers(b,0xef)and F.live_stack(a)==F.live_stack(b)
            assert tuple(map(bytes,a.memory.ram))==tuple(map(bytes,b.memory.ram))
            assert a.memory.rawtags==b.memory.rawtags and a.memory.chr_latches==b.memory.chr_latches
            assert Q.Old.state(a.memory)==Q.Old.state(b.memory)
            irq[kind]+=1
    result['interrupts']=dict(cuts=len(cuts),cases=dict(irq),minimum_return_SP=minimum,all_owned_instructions_reached=True,
        actual_handlers_and_full_continuations=True)
    result.update(passed=True,outputs=0,native=False,walking_frames_qualified=False,
        bindings={Path(p).name:H(Path(p).read_bytes())for p in(C.__file__,__file__)})
    result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    emit('PASS',**result)
    return result


if __name__=='__main__':
    invoke=N.invoke
    def current_invoke(m,name,*a,**k):
        if name=='PauseRoutine':
            old=m.bundle['syms'][name];m.bundle=dict(m.bundle,syms=dict(m.bundle['syms'],PauseRoutine=dict(old,val=hex(Layout.NEW_PAUSE))))
        return invoke(m,name,*a,**k)
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(N,'invoke',current_invoke):
        qualify(C.M.ROM.read_bytes())

"""Leased current palette mapper/Pair/lifecycle/ISR checks, all in memory."""
from collections import Counter
from hashlib import sha256
import inspect,json
from pathlib import Path
from py65.devices.mpu6502 import MPU
import compose_bub_native_palette_current_1115 as C
from check_ff_head_lifetime_irq_1110 import clone

B,W,N=C.B,C.W,C.N

def finite(raw):
    memory=bytearray(65536);memory[0xa000:0xc000]=C.code(raw)
    cpu=MPU(memory=memory);count=0;cycles={}
    for identity in(0,1,2,255):
      memory[0xc300]=identity
      for y in(0x10,0xff):
       for side,entry in((0,0xb43e),(4,0xb438)):
        for value in range(256):
         memory[0xc102+side+y]=value
         for p in range(256):
            cpu.pc,cpu.sp,cpu.a,cpu.x,cpu.y,cpu.p=entry,224,83,(value+p)&255,y,p
            cpu.stPushWord(0x5aff);start=cpu.processorCycles
            for _ in range(32):
                if cpu.pc==0x5b00:break
                cpu.step()
            else:raise AssertionError('Mapper finite bound')
            expected=value&252 if identity==0 and value&3==3 else value
            ep=(p&~130)|(128 if expected&128 else 0)|(2 if expected==0 else 0)
            assert(cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p)==(expected,(value+p)&255,y,224,ep),(identity,y,side,value,p)
            assert memory[0xc102+side+y]==value
            cycles[identity,side,value&3,y]=cpu.processorCycles-start
            count+=1
    return dict(passed=True,full_byte_status_cases=count,identities=[0,1,2,255],
        cycles=sorted(set(cycles.values())),source_attributes_unchanged=True,AXY_SP_CVID_exact=True)

def cold_contracts(raw):
    import replay_bub_combined_route_1113 as Old
    source=inspect.getsource(Old.cold_contracts)
    source=source.replace('parent=U.combined_reverse(raw)','parent=Palette.inverse(raw)',1)
    source=source.replace('sha256(parent).hexdigest()==B.PIN','sha256(parent).hexdigest()==Palette.PARENT',1)
    source=source.replace(C.OLD_COOKIE.hex(),raw[C.COOKIE:C.COOKIE+16].hex())
    ns=dict(Old.__dict__,Palette=C,PIN=C.CANDIDATE)
    exec(compile(source,__file__+':strict-current-cold','exec'),ns)
    return ns['cold_contracts'](raw)

def call(m,pc,observe=None,*,x=46,y=0):
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,x,y,0x61,224;c.stPushWord(0x5aff)
    for _ in range(300000):
        if(c.pc,c.sp)==(0x5b00,224):return c
        if observe:observe(m,c)
        assert m[c.pc],('BRK',hex(c.pc));c.step()
    raise AssertionError(('Call bound',hex(pc),hex(c.pc)))

def paired(raw):
    parent=C.inverse(raw);rows=[]
    for identity in(0,1):
        a,_=B.cold(parent,identity);b,_=B.cold(raw,identity)
        def compare(m,n):
            # All original actor/OAM/upgrade/input/scratch state is exact.
            assert bytes(m.ram[2][:0x3e0])==bytes(n.ram[2][:0x3e0])
            for k,(x,y)in enumerate(zip(m.ram[2],n.ram[2])):
                if x==y:continue
                assert k in(0x3e2,0x3e6,0x13bb)or 0x1fe0<=k<0x1ff0,(identity,hex(k),x,y)
                if k in(0x3e2,0x3e6):assert identity==0 and x&3==3 and y==x&252
            assert C.code(parent)==bytes(m.ram[3]) or bytes(m.ram[3][:0x1fe0])==C.code(parent)[:0x1fe0]
            assert bytes(n.ram[3][:0x1fe0])==C.code(raw)[:0x1fe0]
            assert bytes(m[3:11])==bytes(n[3:11])and m.rawtags==n.rawtags
            # Native gameplay RAM equal; only hardware OAM palette attributes
            # of the privately rendered hero/bubbles may change.
            for at in range(0x800):
                x,y=m[at],n[at]
                if x==y:continue
                assert identity==0 and 0x202<=at<0x300 and at%4==2 and x&3==3 and y==x&252,(identity,hex(at),x,y)
            for at,(x,y)in enumerate(zip(m.vram,n.vram)):
                if x!=y:assert identity==0 and at in(0x3f11,0x3f12,0x3f13,0x3f1d,0x3f1e,0x3f1f),(hex(at),x,y)
        compare(a,b);cost=[];by_pairs={}
        for pad in([0]*8+[1]*8+[64]*12+[0]*12):
            a.controller_pad=b.controller_pad=pad
            cp=[]
            ca=B.frame(a,lambda _m,c:cp.__setitem__(slice(None),[c]),whole_pass=True)
            da=cp[0];pair_count=[0]
            def observe(mm,c):
                cp[:]=[c]
                if c.pc==0xbdc9 and mm.rawtags[1]==3:pair_count[0]+=1
            cb=B.frame(b,observe,whole_pass=True);db=cp[0]
            assert(da.a,da.x,da.y,da.p,da.sp)==(db.a,db.x,db.y,db.p,db.sp)
            compare(a,b);cost.append(cb-ca);by_pairs.setdefault(pair_count[0],[]).append(cb-ca)
        rows.append(dict(identity=identity,ordinary_Main_pairs=40,cycle_delta=[min(cost),max(cost)],
            actual_Pair_costs={str(k):[min(v),max(v)]for k,v in sorted(by_pairs.items())},
            palette0=list(b.vram[0x3f10:0x3f14]),palette3=list(b.vram[0x3f1c:0x3f20]),
            original_private_and_native_gameplay_equal=True,terminal=B.state(b)))
    return dict(passed=True,rows=rows)

def lifecycle(raw):
    lab=json.loads((C.R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())['labels']
    rows=[];parent=C.inverse(raw)
    for identity in(0,1):
        original,_=B.cold(parent,identity);candidate,_=B.cold(raw,identity)
        for area in range(4):
          for offset in(0,36,40,41,44,45,112):
            models=[];returns=[];native_before=[]
            for source in(original,candidate):
                m=clone(source);m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2,AreaType=area,VRAM_Buffer1_Offset=offset)
                native_before.append(bytes(m[:0x800]));maps=m.rawtags[:]
                before=bytes(m.ram[2][:0x400]);c=call(m,lab['BbHelperColors'])
                assert before==bytes(m.ram[2][:0x400])and m.rawtags==maps
                models.append(m);returns.append((c.a,c.x,c.y,c.p,c.sp))
            assert returns[0]==returns[1]
            for at in range(0x4ae,0x530):
                x,y=models[0][at],models[1][at]
                if x!=y:assert identity==0 and x==29 and y==17 and 0x4af<=at<0x52f,(identity,area,offset,hex(at),x,y)
            for at in range(0x800):
                if 0x4ae<=at<0x530:continue
                assert(models[0][at]-native_before[0][at])&255==(models[1][at]-native_before[1][at])&255,(identity,area,offset,'unexpected helper native delta',hex(at))
            rows.append(dict(identity=identity,area=area,queue_offset=offset,AXYP_SP_equal=True))
        for case in('warm','new-life','foreign'):
            models=[];returns=[]
            for source in(original,candidate):
                m=clone(source);m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
                if case=='new-life':N.put(m,NumberofLives=1)
                elif case=='foreign':N.put(m,SelectedCharacter=0)
                c=call(m,lab['BbNativeFresh']);models.append(m);returns.append((c.a,c.x,c.y,c.p,c.sp))
            assert returns[0]==returns[1]
            for k,(x,y)in enumerate(zip(models[0].ram[2],models[1].ram[2])):
                if x!=y:assert k in(0x3e2,0x3e6,0x13bb)or 0x1fe0<=k<0x1ff0,(case,hex(k),x,y)
    return dict(passed=True,palette_queue_cases=len(rows),areas=4,identities=2,
        warm_new_life_foreign_Fresh_pairs=6,original_attributes_owners_inputs_unchanged=True)

def interrupts(raw):
    import check_bub_head_interrupts_1102_v57 as I
    counts=Counter();seen=set();minimum=255;pcs=set()
    for identity in(0,1):
        m,_=B.cold(raw,identity)
        for pad in([0]*4+[64]*12+[0]*4):
            reference=clone(m);reference.controller_pad=pad;last=[]
            # Stop at this actual Main return, before IdleLoop compares the
            # changed skipped-NMI counter and legally starts a catch-up Main.
            B.frame(reference,lambda _m,c:last.__setitem__(slice(None),[c]))
            target=(last[0].pc,last[0].sp);expected=I.state(reference)
            expected_regs=(last[0].a,last[0].x,last[0].y,last[0].p&0xef,last[0].sp)
            def cut(mm,c):
                nonlocal minimum
                if mm.rawtags[1]!=3 or not(0xb438<=c.pc<0xb455 or c.pc in(0xbdfa,0xbe00)):return
                key=(identity,c.pc,c.sp,c.p&4)
                if key in seen:return
                seen.add(key);pcs.add(c.pc)
                assert N.get(mm,'NmiDisable')==255
                for kind in('IRQ','busyNMI'):
                    if kind=='IRQ'and c.p&4:continue
                    q,d=clone(mm,c);regs=(d.pc,d.a,d.x,d.y,d.p&0xef,d.sp)
                    before=I.state(q);live=bytes(q[0x101+d.sp:0x200]);maps=q.rawtags[:]
                    skipped=N.get(q,'NmiSkipped');lag,regular=I.I.path(q);lh=rh=0
                    d.irq()if kind=='IRQ'else d.nmi()
                    for _ in range(200000):
                        minimum=min(minimum,d.sp)
                        if(d.pc,d.sp)==(regs[0],regs[5]):break
                        lh+=d.pc==lag;rh+=d.pc==regular
                        assert q[d.pc],('ISR BRK',kind,hex(d.pc));d.step()
                    else:raise AssertionError('ISR return bound')
                    assert regs==(d.pc,d.a,d.x,d.y,d.p&0xef,d.sp)
                    assert I.state(q)==before and live==bytes(q[0x101+d.sp:0x200])and maps==q.rawtags
                    assert(lh,rh)==((1,0)if kind=='busyNMI'else(0,0))
                    assert N.get(q,'NmiSkipped')==(skipped+(kind=='busyNMI'))&255
                    for _ in range(500000):
                        if(d.pc,d.sp)==target:break
                        assert q[d.pc];d.step()
                    else:raise AssertionError('ISR resumed Main bound')
                    after=I.state(q)
                    assert after==expected,dict(kind=kind,identity=identity,pc=hex(c.pc),
                        fields=[i for i,(x,y)in enumerate(zip(after,expected))if x!=y],
                        RAM=[(bank,hex(i),x,y)for bank,(aa,bb)in enumerate(zip(after[0],expected[0]))for i,(x,y)in enumerate(zip(aa,bb))if x!=y][:16],
                        native=[(hex(i+0x200),x,y)for i,(x,y)in enumerate(zip(after[4],expected[4]))if x!=y][:16])
                    assert(d.a,d.x,d.y,d.p&0xef,d.sp)==expected_regs
                    counts[kind]+=1
            m.controller_pad=pad;B.frame(m,cut)
            assert I.state(m)==expected
    return dict(passed=True,counts=dict(counts),distinct_changed_PCs=len(pcs),minimum_SP=minimum)

def flashing(raw):
    """Declared grace/Star semantic fixtures, not natural item/injury gates."""
    lab=json.loads((C.R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())['labels']
    count=0;main_cases=[];parent=C.inverse(raw)
    for identity in(0,1):
        a,_=B.cold(parent,identity);b,_=B.cold(raw,identity)
        actor,y=(0x2e,0)if identity==0 else(0x42,8)
        for grace in(0,128):
          for phase in(0,4):
           for value in range(256):
            models=[];returns=[]
            for seed in(a,b):
                m=clone(seed);m.raw_page(1,3);m.raw_page(2,2);N.put(m,CurrentBank=3,CurrentBankC=2)
                m.ram[2][actor+2]=grace;m.ram[2][0x1f]=phase
                m.ram[2][0x102+y]=m.ram[2][0x106+y]=value
                c=call(m,lab['BbOriginal_D5A4'],x=actor,y=y)
                models.append(m);returns.append((c.a,c.x,c.y,c.p,c.sp))
            assert returns[0]==returns[1]
            assert bytes(models[0].ram[2][:0x3e0])==bytes(models[1].ram[2][:0x3e0])
            count+=1
        for timer in(0,1,7,35):
            models=[];returns=[]
            for seed in(a,b):
                m=clone(seed);N.put(m,StarInvincibleTimer=timer);m.controller_pad=0;last=[]
                B.frame(m,lambda _m,c:last.__setitem__(slice(None),[c]),whole_pass=True)
                models.append(m);returns.append((last[0].a,last[0].x,last[0].y,last[0].p,last[0].sp))
            assert returns[0]==returns[1]
            assert bytes(models[0].ram[2][:0x3e0])==bytes(models[1].ram[2][:0x3e0])
            assert models[0][W.address(models[0].bundle,'Player_SprAttrib')]==models[1][W.address(models[1].bundle,'Player_SprAttrib')]
            assert list(models[1].vram[0x3f1c:0x3f20])==[15,15,54,23]
            main_cases.append(dict(identity=identity,Star_timer_fixture=timer,original_private_state_equal=True))
    return dict(passed=True,original_grace_attribute_cases=count,actual_Main_Star_timer_cases=main_cases,
        natural_Star_or_injury_claim=False)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--gate',choices=('finite','cold','paired','lifecycle','isr','flash'),required=True);a=ap.parse_args()
    raw,composition=C.proposal(C.ROM.read_bytes());assert C.proposal(C.inverse(raw))[0]==raw
    fn={'finite':finite,'cold':cold_contracts,'paired':paired,'lifecycle':lifecycle,'isr':interrupts,'flash':flashing}[a.gate]
    result=fn(raw);text=json.dumps(result,sort_keys=True,separators=(',',':'))
    print('RESULT '+json.dumps(dict(gate=a.gate,composition=composition,result=result,receipt_SHA256=sha256(text.encode()).hexdigest(),output_files=0),separators=(',',':')),flush=True)

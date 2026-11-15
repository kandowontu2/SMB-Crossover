"""Actual owning candidate Main/lifecycle/ISR, separate from natural routes."""
import argparse
from collections import Counter
from hashlib import sha256
import json

import check_bub_selected_star_palette_ace_1115 as P
import check_bub_head_interrupts_1102_v57 as I
from check_ff_head_lifetime_irq_1110 import clone

C,B,W,N,LAB=P.C,P.B,P.W,P.N,P.LAB


def tracker(identity,candidate=True):
    pending=None;addresses=set();counts=Counter();phases=Counter()
    def observe(m,c):
        nonlocal pending
        bank=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
        if pending and(c.pc,c.sp)==pending['return']:
            assert pending['writes']==2
            pending=None
        if bank==3 and c.pc==LAB['BbNativePair']:
            y=c.y;selected=y==identity*8
            assert pending is None
            pending=dict(y=y,selected=selected,timer=N.get(m,'StarInvincibleTimer'),native=N.get(m,'Player_SprAttrib'),
                attrs=[m.ram[2][0x102+y],m.ram[2][0x106+y]],writes=0,
                return_=(m[0x101+c.sp]+256*m[0x102+c.sp]+1,c.sp+2))
            pending['return']=pending.pop('return_')
        if pending and bytes(m[c.pc:c.pc+3])==bytes.fromhex('9d0202'):
            k=pending['writes'];assert k<2
            value=pending['attrs'][k]
            want=P.expected(identity,pending['y'],pending['timer']if candidate else 0,value,pending['native'])&0xf3
            assert c.a==want,('actual selected/scanned OAM store',pending,hex(c.pc),c.a,want)
            if pending['selected']:
                addresses.add(0x202+c.x)
                if pending['timer']:phases[pending['native']&3]+=1
            pending['writes']+=1;counts['selected'if pending['selected']else'scan']+=1
    return observe,addresses,counts,phases


def compare(a,b,parent,allowed_oam):
    # Compare every backing byte after substituting only exact immutable code
    # and header preimages in the comparison values, not in either live CPU.
    for bank,(aa,bb)in enumerate(zip(a.ram,b.ram)):
        for at,(x,y)in enumerate(zip(aa,bb)):
            if x==y:continue
            if bank==3 and 0x1438<=at<0x1470:
                assert x==C.code(parent)[at] and y==C.NEW[at-0x1438]
            elif bank in(2,3)and 0x1fe0<=at<0x1ff0:
                assert x==C.OLD_COOKIE[at-0x1fe0] and y==C.cookie(b.bundle['raw'])[at-0x1fe0]
            else:assert(bank,at)in((2,0x3e2),(2,0x3e6)),('private difference',bank,hex(at),x,y)
    for at in range(0x800):
        if a[at]!=b[at]:assert at in allowed_oam,('native difference',hex(at),a[at],b[at])
    assert a.rawtags==b.rawtags and bytes(a.vram)==bytes(b.vram)


def mains(raw):
    parent=C.inverse(raw);rows=[]
    for identity in(0,1):
        seeds=[B.cold(image,identity)[0]for image in(parent,raw)]
        for timer in(0,1,35):
            a,b=[clone(m)for m in seeds]
            for m in(a,b):N.put(m,StarInvincibleTimer=timer,IntervalTimerControl=0)
            oa,aa,ca,pa=tracker(identity,False);ob,ab,cb,pb=tracker(identity,True)
            costs=[];timers=[];held=[0]*6+[1]*6+[64]*12+[0]*24
            for pad in held:
                regs=[];cy=[]
                for m,observer in((a,oa),(b,ob)):
                    last=[];m.controller_pad=pad
                    def observe(mm,c):observer(mm,c);last[:]=[c]
                    cy.append(B.frame(m,observe));c=last[0];regs.append((c.a,c.x,c.y,c.p,c.sp))
                assert regs[0]==regs[1]
                assert aa==ab
                compare(a,b,parent,ab)
                assert list(b.vram[0x3f1c:0x3f20])==[15,15,54,23]
                costs.append(cy[1]-cy[0]);timers.append(N.get(b,'StarInvincibleTimer'))
            if timer==1:assert 0 in timers,'Actual original timer expiry reached'
            rows.append(dict(identity=identity,declared_timer_fixture=timer,actual_Main_pairs=len(held),
                source_cycle_deltas=sorted(set(costs)),actual_selected_store_phases=dict(pb),
                actual_store_counts=dict(cb),terminal_timer=timers[-1],expiry_reached=timer==1 and 0 in timers,
                exact_world_palette_PPU_and_original_state=True))
    return dict(passed=True,rows=rows,scope='Declared Star clock fixtures through real Main, not natural Star acquisition',
        audio_output_or_native_graphics_claim=False)


def lifecycle(raw):
    parent=C.inverse(raw);rows=[];grace=0
    for identity in(0,1):
        seeds=[B.cold(image,identity)[0]for image in(parent,raw)]
        actor,y=(0x2e,0)if identity==0 else(0x42,8)
        for area in range(4):
          for offset in(0,36,40,41,44,45,112):
            models=[];regs=[]
            for seed in seeds:
                m=P.setup(seed);N.put(m,AreaType=area,VRAM_Buffer1_Offset=offset)
                c,_=P.call(m,LAB['BbHelperColors']);models.append(m);regs.append((c.a,c.x,c.y,c.p,c.sp))
            assert regs[0]==regs[1];compare(*models,parent,set())
            rows.append([identity,area,offset])
        for name in('warm','new-life','foreign','retire','repeat-retire'):
            models=[];regs=[]
            for seed in seeds:
                m=P.setup(seed)
                if name=='new-life':N.put(m,NumberofLives=1)
                elif name=='foreign':N.put(m,SelectedCharacter=0)
                if'retire'in name:
                    N.put(m,SelectedCharacter=0)
                    import check_bubble_bobble_common_cold_1102_v4 as Cold
                    if name=='repeat-retire':Cold.call(m,0xae0a)
                    q=Cold.call(m,0xae0a);regs.append((q['A'],q['X'],q['Y'],q['P']))
                else:
                    c,_=P.call(m,LAB['BbNativeFresh']);regs.append((c.a,c.x,c.y,c.p))
                models.append(m)
            assert regs[0]==regs[1]
            compare(*models,parent,set())
        for flag in(0,128):
          for phase in(0,4):
           for value in range(256):
            models=[];regs=[]
            for seed in seeds:
                m=P.setup(seed);m.ram[2][actor+2]=flag;m.ram[2][0x1f]=phase
                m.ram[2][0x102+y]=m.ram[2][0x106+y]=value
                c,_=P.call(m,LAB['BbOriginal_D5A4'],x=actor,y=y)
                models.append(m);regs.append((c.a,c.x,c.y,c.p,c.sp))
            assert regs[0]==regs[1];compare(*models,parent,set());grace+=1
    return dict(passed=True,unchanged_palette_queue_cases=len(rows),areas=4,
        warm_new_life_foreign_retire_cases=10,original_grace_attribute_cases=grace,
        all_world_PPU_queue_and_private_ownership_equal=True)


def expiry(raw):
    parent=C.inverse(raw);rows=[]
    for identity in(0,1):
        models=[B.cold(image,identity)[0]for image in(parent,raw)]
        for m in models:N.put(m,StarInvincibleTimer=1,IntervalTimerControl=20)
        trackers=[tracker(identity,k==1)for k in range(2)]
        timers=[];active=False;expired=False;cost=[]
        for epoch in range(48):
            regs=[];cycles=[]
            for m,(observe,addresses,counts,phases)in zip(models,trackers):
                m.controller_pad=0;last=[]
                cycles.append(B.frame(m,lambda mm,c:(observe(mm,c),last.__setitem__(slice(None),[c]))))
                c=last[0];regs.append((c.a,c.x,c.y,c.p,c.sp))
            assert regs[0]==regs[1]
            compare(*models,parent,trackers[1][1])
            timers.append(N.get(models[1],'StarInvincibleTimer'))
            active|=bool(trackers[1][3]);expired|=active and timers[-1]==0
            cost.append(cycles[1]-cycles[0])
            if expired and epoch>=32:break
        assert active and expired,('Need actual active1 then expired0 draw lifecycle',identity,timers)
        rows.append(dict(identity=identity,actual_Main_pairs=epoch+1,timer_values=sorted(set(timers)),
            active_selected_phases=dict(trackers[1][3]),active_then_expired=True,
            source_cycle_deltas=sorted(set(cost)),normal_palette_and_all_original_state_restored=True))
    return dict(passed=True,rows=rows,scope='Declared timer/interval fixture, real Main expiry; not natural Star duration')


def boundaries(raw):
    parent=C.inverse(raw);rows=[]
    for identity in(0,1):
      for timer in(0,35):
        models=[B.cold(image,identity)[0]for image in(parent,raw)]
        for m in models:N.put(m,GameEngineSubroutine=11,StarInvincibleTimer=timer)
        tracks=[tracker(identity,k==1)for k in range(2)]
        for _ in range(8):
            regs=[]
            for m,(observe,addresses,counts,phases)in zip(models,tracks):
                m.controller_pad=0;last=[]
                B.frame(m,lambda mm,c:(observe(mm,c),last.__setitem__(slice(None),[c])))
                c=last[0];regs.append((c.a,c.x,c.y,c.p,c.sp))
            assert regs[0]==regs[1];compare(*models,parent,tracks[1][1])
        rows.append(dict(identity=identity,declared_death_engine=11,initial_Star=timer,actual_Main_pairs=8,
            actual_store_counts=dict(tracks[1][2]),terminal=B.state(models[1])))
    # A genuine compiled default menu/Start witness on both owning images,
    # rather than initializing a foreign actor or calling a stale component.
    foreign=[]
    for image in(parent,raw):
        bundle=dict(W.Symbols.bundle(),raw=image);old=N.Bus;N.Bus=W.ControllerBus
        try:m=W.UI.seed(bundle,0)
        finally:N.Bus=old
        name=W.UI.menu_name(m)[0];start=W.UI.key(m,16)
        N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
        N.invoke(m,'PauseRoutine',a=0)
        for _ in range(700):
            if(N.get(m,'OperMode'),N.get(m,'OperMode_Task'),N.get(m,'GameEngineSubroutine'))==(1,3,8):break
            m.controller_pad=0;B.frame(m,cold=True)
        else:raise AssertionError('Foreign genuine cold bound')
        assert N.get(m,'SelectedCharacter')!=39
        foreign.append((m,name))
    assert foreign[0][1]==foreign[1][1]
    a,b=(v[0]for v in foreign)
    for _ in range(16):
        regs=[]
        for m in(a,b):
            m.controller_pad=1;last=[];B.frame(m,lambda _m,c:last.__setitem__(slice(None),[c]))
            c=last[0];regs.append((c.a,c.x,c.y,c.p,c.sp))
        assert regs[0]==regs[1]
        assert a.ram==b.ram and bytes(a[:0x800])==bytes(b[:0x800])
        assert a.rawtags==b.rawtags and a.vram==b.vram
    return dict(passed=True,declared_death_boundary_rows=rows,genuine_foreign_menu_Start=foreign[0][1],
        foreign_actual_Right_Main_pairs=16,foreign_RAM_PPU_AXYP_SP_maps_exact=True,
        scope='Death engine fixtures are explicit; foreign Start/Right is controller-only; no natural death or full-stage claim')


def interrupts(raw):
    counts=Counter();seen=set();pcs=set();minimum=255;between=Counter();contexts=Counter()
    from py65.disassembler import Disassembler
    memory=[0]*65536;memory[0xb438:0xb470]=C.NEW
    decoder=Disassembler(MPU:=N.NesMPU(memory=memory));expected_pcs=set();pc=0xb438
    while pc<0xb470:
        expected_pcs.add(pc);size,_=decoder.instruction_at(pc);pc+=size
    assert pc==0xb470
    def cut(mm,c,*,resume=None,final=None,context):
        nonlocal minimum
        if mm.rawtags[1]!=3 or not 0xb438<=c.pc<0xb470:return
        key=(context,c.pc,c.sp,c.p&4)
        if key in seen:return
        seen.add(key);pcs.add(c.pc);contexts[context]+=1
        assert N.get(mm,'NmiDisable')==255
        for kind in('IRQ','busyNMI'):
            if kind=='IRQ'and c.p&4:continue
            q,d=clone(mm,c);regs=(d.pc,d.a,d.x,d.y,d.p&0xef,d.sp)
            before=I.state(q);live=bytes(q[0x101+d.sp:0x200]);maps=q.rawtags[:]
            attr=N.get(q,'Player_SprAttrib');skipped=N.get(q,'NmiSkipped');lag,regular=I.I.path(q);lh=rh=0
            d.irq()if kind=='IRQ'else d.nmi()
            for _ in range(200000):
                minimum=min(minimum,d.sp)
                if(d.pc,d.sp)==(regs[0],regs[5]):break
                lh+=d.pc==lag;rh+=d.pc==regular
                assert q[d.pc];d.step()
            else:raise AssertionError('ISR return bound')
            assert regs==(d.pc,d.a,d.x,d.y,d.p&0xef,d.sp)
            assert before==I.state(q)and live==bytes(q[0x101+d.sp:0x200])and maps==q.rawtags
            assert N.get(q,'Player_SprAttrib')==attr
            assert(lh,rh)==((1,0)if kind=='busyNMI'else(0,0))
            assert N.get(q,'NmiSkipped')==(skipped+(kind=='busyNMI'))&255
            if c.pc in(0xb457,0xb459):between[kind]+=1
            if resume is not None:
                for _ in range(500000):
                    if(d.pc,d.sp)==resume:break
                    assert q[d.pc];d.step()
                else:raise AssertionError('ISR continuation bound')
                assert I.state(q)==final[0]
                assert(d.a,d.x,d.y,d.p&0xef,d.sp)==final[1]
            counts[kind]+=1
    for identity in(0,1):
        seed,_=B.cold(raw,identity)
        for timer in(0,35):
            m=clone(seed);N.put(m,StarInvincibleTimer=timer)
            for pad in([0]*2+[64]*6+[0]*2):
                reference=clone(m);reference.controller_pad=pad;last=[]
                B.frame(reference,lambda _m,c:last.__setitem__(slice(None),[c]))
                r=last[0];target=(r.pc,r.sp);final=(I.state(reference),(r.a,r.x,r.y,r.p&0xef,r.sp))
                m.controller_pad=pad
                B.frame(m,lambda mm,c:cut(mm,c,resume=target,final=final,context=f'actualMain id{identity} Star{timer}'))
                assert I.state(m)==final[0]
        # Exact component caller fixture supplies the old palette1 grace
        # branch without claiming a natural injury; all mapper PCs must close.
        m=P.setup(seed);m.ram[2][0x100]=m.ram[2][0x104]=100
        m.ram[2][0x103]=96;m.ram[2][0x107]=104
        m.ram[2][0x101]=0;m.ram[2][0x105]=2
        m.ram[2][0x102]=m.ram[2][0x106]=1
        P.call(m,LAB['BbNativePair'],observe=lambda mm,c:cut(mm,c,context=f'declaredPair grace id{identity}'))
    assert pcs==expected_pcs,dict(missing=[hex(x)for x in sorted(expected_pcs-pcs)])
    assert all(between[k]>0 for k in('IRQ','busyNMI'))
    return dict(passed=True,counts=dict(counts),all_mapper_instruction_PCs=len(pcs),minimum_SP=minimum,
        actual_Main_and_declared_component_contexts=dict(contexts),between0587reads_cuts=dict(between),
        native0587_stable=True,live_stack_maps_and_actual_continuations_exact=True,
        existing_oracle_audio_clock_exclusions=[0x7d8,0x7da,0x7db])


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--gate',choices=('cold','main','lifecycle','expiry','boundaries','isr'),required=True);args=ap.parse_args()
    raw,composition=C.proposal(C.load_current())
    result={'cold':P.cold,'main':mains,'lifecycle':lifecycle,'expiry':expiry,'boundaries':boundaries,'isr':interrupts}[args.gate](raw)
    text=json.dumps(result,sort_keys=True,separators=(',',':'))
    print('RESULT '+json.dumps(dict(gate=args.gate,composition=composition,result=result,
        receipt_SHA256=sha256(text.encode()).hexdigest(),output_files=0),separators=(',',':')),flush=True)

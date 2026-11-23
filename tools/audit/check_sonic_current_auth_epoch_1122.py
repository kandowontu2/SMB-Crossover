"""Actual-machine exact59 Sonic auth candidate; source-only, no output files.

Cold compiled menu and ordinary Main comparison; reached collision predicates;
owner/scope/header fallback and native IRQ/busy-NMI cuts. DMA and physical
scanline cadence are deliberately outside this instruction-cycle proof.
"""
from collections import Counter
import json
from pathlib import Path
from unittest.mock import patch

import compose_sonic_current_auth_epoch_1122 as C
import profile_sonic_empty_cpu_1110 as B
from check_mini_funded_actor_1108_v3 import registers, run, slim_fork, live_stack

N,W,UI=B.N,B.W,B.UI

def enter(raw,form):
    bundle=W.Symbols.bundle();bundle['raw']=raw
    original=N.Bus;N.Bus=W.ControllerBus
    try:m=UI.seed(bundle,25)
    finally:N.Bus=original
    m.ram[2][0x3f0]=0x77  # Cold owner initialization must erase stale Mini epoch.
    for _ in range(form):UI.key(m,32)
    assert UI.menu_name(m)[0]==('SONIC'if form==3 else 'SUPER SONIC')
    assert N.get(m,'SelectedCharacter')==43 and m[0x5ffe]==form
    start=UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    return m

def state(m):
    names=('SelectedCharacter','CurrentPlayer','OperMode','OperMode_Task','GameEngineSubroutine',
           'NumberofLives','PlayerStatus','Player_X_Position','Player_PageLoc','Player_Y_Position',
           'Player_Y_HighPos','Player_State','FrameCounter','GamePauseStatus','TimerControl',
           'CurrentBank','CurrentBankC','ObjectOffset')
    actor=('Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position',
           'Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','FloateyNum_Control')
    private=bytearray(m.ram[2][:0x400]);private[0x3f0]=0
    return tuple(N.get(m,n)for n in names),tuple(bytes(m[W.address(m.bundle,n):W.address(m.bundle,n)+6])for n in actor),bytes(private),tuple(m.rawtags),tuple(m.chr_latches)

class Observe:
    def __init__(self,collect=True,cuts=None):self.count=Counter();self.rows=[];self.cuts=cuts if cuts is not None else{};self.upper=[];self.collect=collect
    def run(self,c,stop):
        c.memory.auth_epoch_terminal=stop
        for _ in range(500000):
            if(c.pc,c.sp)==stop:return
            m=c.memory;t=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            if(t,c.pc)==(193,0xaf27):self.count['full_header']+=1;self.rows.append((m[0x16c]-0x8c)//3)
            if(t,c.pc)==(213,0xa8dc):self.count['epoch_try']+=1
            if(t,c.pc)==(254,0x9c6e):self.count['native_side']+=1
            if(t,c.pc)==(210,0xb16d):self.count['Prince_upper_predicate']+=1;self.upper.append((c.a,c.x,c.y,c.p))
            if(t,c.pc)==(3,0xbbb0):self.count['motor']+=1
            if(t,c.pc)==(2,0xda40):self.count['private_scope_guard']+=1
            if self.collect and((t==193 and(0xa740<=c.pc<0xa7c5 or 0xa7d5<=c.pc<0xa7da))or(t==213 and(0xa8dc<=c.pc<0xa900 or 0xb06b<=c.pc<0xb08c or 0xb8f0<=c.pc<0xb900))or(t==2 and 0xda40<=c.pc<0xda88)):
                key=t,c.pc,c.sp,c.p&5
                if key not in self.cuts:self.cuts[key]=clone(c)
            assert m[c.pc],(hex(c.pc),t)
            ri,wi=len(m.ram_writes),len(m.writes)
            live=(m[0x6002]==43 and m[0x5fff]&1 and m[0x1f9]==0x52 and m[0x1fa]==0x83 and m.ram[2][0x11a]==1 and m.ram[2][0x11b]==m[0x0e])
            c.step()
            if live:
                assert not any(bank in(2,3)and 0x1fe0<=at<0x1ff0 for bank,at,_ in m.ram_writes[ri:]),'Header mutated inside granted scope'
                assert not any(at in(0x6002,0x5ffe)for at,_ in m.writes[wi:]),'Owner/form mutated inside granted scope'
        raise AssertionError(('Main bound',hex(c.pc)))

def clone(c):
    m=slim_fork(c.memory);z=N.NesMPU(memory=m,pc=c.pc)
    z.a,z.x,z.y,z.p,z.sp=registers(c)
    return z

def profile(parent,candidate,form):
    machines=[enter(raw,form)for raw in(parent,candidate)]
    cold=Counter();first_auth=[]
    for frame in range(300):
        ready=[tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)for m in machines]
        assert ready[0]==ready[1]
        if all(ready):break
        traces=[Observe(False),Observe(False)]
        for m,tr in zip(machines,traces,strict=True):B.main_step(m,0,tr)
        assert state(machines[0])==state(machines[1]),('Cold state mismatch',form,frame)
        cold.update(traces[1].count)
    else:raise AssertionError('Cold bound')
    assert machines[0].ram[2][0x3f0]==machines[1].ram[2][0x3f0]==0,'Actual Sonic cold did not clear stale shared epoch'
    cold_frames=frame;allcuts={};phases={}
    for phase,pad,length in(('settle',0,4),('idle',0,16),('Right',1,16),('tap',0x81,1),('air',1,10),('release',0,8)):
        oldcycles=[];newcycles=[];counts=Counter();upper=Counter()
        for frame in range(length):
            traces=[Observe(False),Observe(cuts=allcuts)];cycles=[]
            for m,tr in zip(machines,traces,strict=True):cycles.append(B.main_step(m,pad,tr)[0])
            assert state(machines[0])==state(machines[1]),('Gameplay state mismatch',form,phase,frame)
            oldcycles.append(cycles[0]);newcycles.append(cycles[1]);counts.update(traces[1].count)
            assert traces[0].upper==traces[1].upper,('Native upper predicate input changed',phase,frame)
            allcuts.update(traces[1].cuts)
            if traces[0].count['motor']:
                assert traces[1].count['motor']==traces[0].count['motor']
            if phase in('idle','Right'):
                assert traces[0].count['full_header']==14
                assert traces[1].count['full_header']==1,(phase,frame,traces[1].count,traces[1].rows)
                assert traces[1].rows==[0]
            if phase=='settle' and frame==0:first_auth=traces[1].rows
        phases[phase]=dict(returns=length,parent_mean=sum(oldcycles)/length,candidate_mean=sum(newcycles)/length,cycles_removed_mean=(sum(oldcycles)-sum(newcycles))/length,candidate_entries=dict(counts))
    return machines[1],dict(form=form,cold_Main_returns=cold_frames,cold_entries=dict(cold),first_ordinary_full_check_rows=first_auth,phases=phases),allcuts

def public(m,row=9):
    # Genuine public target and standard FarCall stack; the dispatch itself
    # preserves the original caller's AXYP while observing live owner state.
    m[0x16a],m[0x16c],m[0x16d]=0,0x8c+row*3,0xb0
    c=N.NesMPU(memory=m,pc=0x15a);c.a,c.x,c.y,c.p,c.sp=193,7,11,0x31,224
    c.stPushWord(0x5aff);tr=Observe();tr.run(c,(0x5b00,224))
    return c,tr

def fallbacks(seed,cuts=None):
    counts=Counter()
    # A detached call cannot reuse a previously successful ordinary Main.
    for kind in('busy','root_high','root_low','ready','have_epoch','engine','pause','timer','host_epoch','cache_epoch','zero_epoch'):
        m=slim_fork(seed);m[0x5fff]=1;m[0x1f9]=0x52;m[0x1fa]=0x83
        m.ram[2][0x119]=m.ram[2][0x11a]=1
        m.ram[2][0x11b]=m.ram[2][0x3f0]=N.get(m,'FrameCounter')
        N.put(m,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0)
        if kind=='busy':m[0x5fff]=0
        elif kind=='root_high':m[0x1fa]^=1
        elif kind=='root_low':m[0x1f9]^=1
        elif kind=='ready':m.ram[2][0x119]=0
        elif kind=='have_epoch':m.ram[2][0x11a]=0
        elif kind=='engine':N.put(m,GameEngineSubroutine=7)
        elif kind=='pause':N.put(m,GamePauseStatus=1)
        elif kind=='timer':N.put(m,TimerControl=1)
        elif kind=='host_epoch':m.ram[2][0x11b]^=1
        elif kind=='cache_epoch':m.ram[2][0x3f0]^=1
        elif kind=='zero_epoch':N.put(m,FrameCounter=0);m.ram[2][0x11b]=m.ram[2][0x3f0]=0
        _,tr=public(m);assert tr.count['full_header']==1,(kind,tr.count);counts[kind]+=1
        if cuts is not None:cuts.update(tr.cuts)
    # Complete-cookie failure must remain closed before any ordinary grant.
    for bank in(2,3):
        for byte in range(16):
            m=slim_fork(seed);m[0x5fff]=0;m.ram[bank][0x1fe0+byte]^=1
            c,tr=public(m);assert tr.count['full_header']==1
            assert not c.p&1,(bank,byte,registers(c));counts['full_cookie_corruption']+=1
            if cuts is not None:cuts.update(tr.cuts)
    for kind in('zero_cache','stale_cache','foreign_prefix'):
        m=slim_fork(seed);m.ram[2][0x1a40]=0  # Reaching private code now traps.
        if kind=='zero_cache':m.ram[2][0x3f0]=0
        elif kind=='stale_cache':m.ram[2][0x3f0]=N.get(m,'FrameCounter')^1
        else:m.ram[2][0x1fe1]^=1
        _,tr=public(m);assert tr.count['full_header']==1 and not tr.count['private_scope_guard']
        counts['ROM_only_'+kind]+=1
    return dict(counts)

def rebind(m,raw):
    old=m.bundle['raw'];m.bundle=dict(m.bundle,raw=raw)
    for bank in(2,3):
        for i in range(16):m.ram[bank][0x1fe0+i]^=old[C.M.COOKIE_AT+i]^raw[C.M.COOKIE_AT+i]
    kernel=C.M.kernel(raw);m.ram[3][:len(kernel)]=kernel
    m.ram[2][0x1800:0x1c00]=C.M.page(raw,334)
    for window,value in enumerate(m.rawtags):
        if value&128:m.raw_page(window,value)

def upper_predicate(seed,parent,candidate):
    # Actual current 126:9C88 caller through the real 82:B16D predicate,
    # including pipe, climb and special tile25. These are explicit fixtures.
    machines=[slim_fork(seed),slim_fork(seed)]
    for m,raw in zip(machines,(parent,candidate),strict=True):rebind(m,raw);m.raw_page(0,254)
    count=0;branches=Counter()
    for owner in(0,38,43):
        for tile in range(256):
            results=[]
            for m in machines:
                N.put(m,SelectedCharacter=owner,GameEngineSubroutine=8)
                m[7],m[9],m[0x75]=7,6,0x5f
                c=N.NesMPU(memory=m,pc=0x9c88);c.a,c.x,c.y,c.p,c.sp=tile,0,56,0x31|int(tile==0)*2,201
                maps=tuple(m.rawtags)
                for _ in range(1000):
                    if c.pc in(0x9c9e,0x9cb6):break
                    assert m[c.pc],hex(c.pc);c.step()
                else:raise AssertionError(('Upper predicate bound',owner,tile,hex(c.pc)))
                assert c.sp==201 and tuple(m.rawtags)==maps
                results.append((registers(c),c.pc,m[7],m[9],m[0x75]))
            assert results[0]==results[1],(owner,tile,results)
            branches[hex(results[0][1])]+=1;count+=1
    return dict(actual_native_caller_cases=count,continuations=dict(branches),special_tile25_and_pipe_climb_preserved=True)

def selector_controls(seed,parent,candidate):
    cases=Counter()
    for owner in(0,36,37,38,39,40,41,42,43,255):
        for high in(0xaa,0xaf,0xb0,0xb1):
            for low in sorted({0,0x87,0x88,0x8b,0xfe,0xff,*range(0x8c,0xfe,3)}):
                malformed_mini=owner==41 and high!=0xaa and not(high==0xb0 and 0x8c<=low<0xfe)
                results=[]
                for raw in(parent,candidate):
                    if raw==parent and malformed_mini:continue
                    m=slim_fork(seed);rebind(m,raw);m.raw_page(1,193)
                    N.put(m,SelectedCharacter=owner,CurrentBank=193,FamilyMainCommit=0,FrameCounter=9)
                    if 37<=owner<=43:
                        index=owner-37;pointer=raw[C.off(65,0xabaf)+index]+256*raw[C.off(65,0xabb7)+index]
                        bank=126 if pointer<0xa000 else 65
                        cookie=raw[C.off(bank,pointer):C.off(bank,pointer)+16]
                        assert cookie[:2]==bytes((0xa7,owner))
                        for bank in(2,3):m.ram[bank][0x1fe0:0x1ff0]=cookie
                    m[0x16c],m[0x16d]=low,high
                    c=N.NesMPU(memory=m,pc=0xa743);c.a,c.x,c.y,c.p,c.sp=73,11,19,0x31,210
                    run(c,lambda q:q.pc in(0xab12,0xab4f,0xb031))
                    # AB4F intentionally replaces A and invokes the native
                    # typed failure; its incoming arithmetic flags are dead.
                    # AB12 reloads the original input AXYP from the mapped
                    # Co frame; selector's temporary X/P have no ABI output.
                    results.append((c.pc,c.sp,c.a if c.pc==0xab12 else None,m[0x16c],m[0x16d],m[0x179]if owner==38 and c.pc==0xab12 else None,tuple(m.rawtags)))
                if malformed_mini:
                    assert results[0][0]==0xab4f and results[0][1]==210
                    cases['old_unsafe_Mini_malformed_now_bounded']+=1
                else:
                    assert results[0]==results[1],('Foreign/edge selector parity',owner,high,low,results)
                    cases['all_owner_high_low_edges']+=1
    for raw in(parent,candidate):
        m=slim_fork(seed);rebind(m,raw);m.raw_page(1,193)
        N.put(m,SelectedCharacter=41,CurrentBank=193,FamilyMainCommit=0,FrameCounter=9)
        m.ram[2][0x3f0]=9
        for bank in(2,3):m.ram[bank][0x1fe0:0x1fe2]=bytes((0xa7,41))
        m[0x16c],m[0x16d]=0xa7,0xb0
        c=N.NesMPU(memory=m,pc=0xa743);c.a,c.x,c.y,c.p,c.sp=73,11,19,0x31,210
        tr=Observe(False)
        try:tr.run(c,(0xab12,210))
        except Exception:
            print('MINI FAST DIAGNOSTIC '+json.dumps(dict(ROM=C.H(raw),pc=c.pc,SP=c.sp,regs=registers(c),SMC=bytes(m[0x15a:0x17b]).hex(),maps=m.rawtags,entries=dict(tr.count))),flush=True);raise
        assert c.a==0xa0 and m[0x16c]==27 and not tr.count['full_header']
        cases['existing_Mini_fast_semantics']+=1
    return dict(cases)

def interrupts(cuts):
    counts=Counter();minimum=255
    # All executed epoch/helper instructions in genuine Main, not a synthetic
    # replacement ISR. Each cut resumes and reaches the same native Main end.
    for original in cuts.values():
        for kind in('IRQ','busyNMI'):
            if kind=='IRQ' and original.p&4:continue
            baseline=clone(original);c=clone(original);m=c.memory
            N.put(m,NmiDisable=255)
            N.put(baseline.memory,NmiDisable=255)
            before=registers(c),c.pc;stack=live_stack(c)
            private=tuple(bytes(q)for q in m.ram)
            if kind=='IRQ':c.irq()
            else:c.nmi()
            run(c,lambda z:(registers(z),z.pc)==before)
            minimum=min(minimum,c.sp)
            assert live_stack(c)==stack and tuple(bytes(q)for q in m.ram)==private,(kind,before)
            # Native lag audio may finish a shadow mapper store interrupted
            # immediately before its bus write; completion still must match.
            for z in(baseline,c):
                idle=W.address(z.memory.bundle,'IdleLoop')
                terminal=getattr(z.memory,'auth_epoch_terminal',(idle+12,252))
                for _ in range(500000):
                    if(z.pc,z.sp)==terminal:break
                    assert z.memory[z.pc],hex(z.pc)
                    z.step()
                else:raise AssertionError(('Interrupted Main continuation bound',kind,hex(z.pc)))
            assert state(baseline.memory)==state(c.memory),(kind,before)
            assert registers(baseline)==registers(c)
            counts[kind]+=1
    return dict(cuts=len(cuts),cases=dict(counts),minimum_return_SP=minimum)

def qualify(raw):
    candidate,composition=C.proposal(raw)
    print('SONIC AUTH CANDIDATE '+composition['candidate_SHA256'],flush=True)
    profiles=[];cuts={};seed=None
    for form in(3,4):
        seed,q,c=profile(raw,candidate,form);profiles.append(q);cuts.update(c)
        print('SONIC AUTH FORM '+json.dumps(q,separators=(',',':')),flush=True)
    fallback=fallbacks(seed,cuts)
    print('SONIC AUTH FALLBACK '+json.dumps(fallback,separators=(',',':')),flush=True)
    upper=upper_predicate(seed,raw,candidate)
    print('SONIC AUTH UPPER '+json.dumps(upper,separators=(',',':')),flush=True)
    foreign=selector_controls(seed,raw,candidate)
    print('SONIC AUTH SELECTOR '+json.dumps(foreign,separators=(',',':')),flush=True)
    irq=interrupts(cuts)
    return dict(passed=True,composition=composition,profiles=profiles,fallback=fallback,upper_predicate=upper,selector_controls=foreign,interrupts=irq,outputs=0,Mesen=False,physical_cadence_qualified=False)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);group=parser.add_mutually_exclusive_group();group.add_argument('--controls-only',action='store_true');group.add_argument('--fallbacks-only',action='store_true');args=parser.parse_args()
    def deny(*a,**k):raise AssertionError('Source proof attempted file/process output')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        raw=C.M.ROM.read_bytes()
        if args.controls_only or args.fallbacks_only:
            candidate,composition=C.proposal(raw);seed=enter(candidate,3)
            for _ in range(300):
                if tuple(N.get(seed,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
                B.main_step(seed,0)
            else:raise AssertionError('Controls cold bound')
            if args.controls_only:q=dict(passed=True,composition=composition,upper_predicate=upper_predicate(seed,raw,candidate),selector_controls=selector_controls(seed,raw,candidate),outputs=0,Mesen=False)
            else:
                for _ in range(4):B.main_step(seed,0)
                cuts={};fallback=fallbacks(seed,cuts)
                q=dict(passed=True,composition=composition,fallback=fallback,interrupts=interrupts(cuts),outputs=0,Mesen=False)
        else:q=qualify(raw)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('SONIC AUTH RESULT '+json.dumps(q,separators=(',',':')),flush=True)

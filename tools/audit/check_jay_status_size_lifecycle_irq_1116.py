"""Current candidate lifecycle and reached interrupt qualification; RAM only."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import current_jay_status_size_publication_00bb_1116 as J

C,N,W=J.C,J.N,J.W
C_SHA='7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c'
J_SHA='ffe06f7b53421b24a07da2918b846a67a3de28469ee7eed2d7e67d42816bf8f3'


def heart_seed(raw):
    """Capture the real first-heart prefix at a completed idle boundary."""
    import check_jay_natural_fsl_routes_1116 as Base
    import jay_natural_fsl_controls_v3_1116 as V3
    assert J.H(Path(Base.__file__).read_bytes())=='407f51f1a089a12e31c418af919ae9fb620e790bc2efdb42e6e8b5e5353010f0'
    assert J.H(Path(V3.__file__).read_bytes())=='6746cbe6239e67c08ee6d5cdd9207902bd3b83f86c4d4e1c3fd1be5ef2e58704'
    body=V3.text();source=inspect.getsource(Base.run);captured=[]
    def save(m,row):
        assert not captured and m.bundle['raw']is raw
        assert N.get(m,'JnStars')==128 and N.get(m,'PlayerStatus')==1 and N.get(m,'PlayerSize')==0
        assert(N.get(m,'JnHealth'),N.get(m,'JnMaxHearts'),N.get(m,'JnOwnedTier'))==(8,4,1)
        captured.append((m,row))
    edits=(('metadata91dc_only=J.Frozen.PIN','metadata00bb_only=J.Previous.PIN'),
        ('done=False;fault=None','done=False;fault=None;heart_credit=None'),
        ('                if done:break',
        '''                if collected and collected[0]['label']=='mushroom':
                    first=collected[0]
                    if heart_credit is None and state()['score']>=first['before']['score']+1000:
                        heart_credit=dict(Main=counts['Main_returns'],motor=counts['motor_returns'],state=state())
                    if heart_credit and counts['motor_returns']>=heart_credit['motor']+25:
                        assert len(collected)==1 and first['item']['private']==129
                        assert private_returns and private_returns[-1]['C']==1 and 32 in sound
                        assert N.get(m,'SelectedCharacter')==16 and m[0x730b]&96==32
                        _capture(m,dict(collector=first,credit=heart_credit,completed=state(),
                            actual_postcredit_returns=counts['motor_returns']-heart_credit['motor'],
                            actual_postcollector_returns=counts['motor_returns']-first['motor'],pending_workers=0))
                        break
                if done:break'''))
    for a,b in edits:assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
    class Recipe:
        @staticmethod
        def read_text():return body
        @staticmethod
        def read_bytes():return body.encode()
    ns=dict(Base.__dict__,J=J,N=N,W=W,Frames=J.Frames,POLICY=Recipe,_capture=save)
    exec(compile(source,'<same ordinaryV3 firstheart capture after completed frame>','exec'),ns)
    result=ns['run'](raw,'flower',700)
    assert result['fault']is None and len(captured)==1,('Real firstheart capture failed',result)
    m,row=captured[0]
    before={n:N.get(m,n)for n in('PlayerSize','PlayerStatus','JnStars','MmBlockAttack')}
    oracle=N.fork(m);head=N.invoke(oracle,'CrossoverBlockSize',a=51,x=0,y=before['PlayerSize'],p=0x31)
    assert before==dict(PlayerSize=0,PlayerStatus=1,JnStars=128,MmBlockAttack=0)and head['Y']==0
    assert {n:N.get(oracle,n)for n in before}==before
    row.update(actual_native_fields=before,native_large_head_oracle=head,parent_route_receipt=result['receipt_SHA256'],policy_SHA256=J.H(body.encode()),
        derived_observer_SHA256=J.H(source.encode()),natural_prefix_only=True,no_gameplay_seeds=True,
        original_entry_and_return_counts_equal=result['counts']['JayIntegrate_entered']==result['counts']['JayIntegrate_returned'])
    row['receipt_SHA256']=J.H(json.dumps(row,sort_keys=True,separators=(',',':')).encode())
    return m,row


def lifecycle(raw):
    q=J.bindings(raw);base=N.NesMPU;counts=Counter();events=[];frames=0
    native={n:(128+((W.location(q['bundle'],n)-16)//8192),W.address(q['bundle'],n))for n in('JnEnsure','JnAreaReset','JnClearGear','JnPreparePickup')}
    ensure_before_first_mirror=False
    def tag(m,pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
    def state(m):return dict(stars=N.get(m,'JnStars'),status=N.get(m,'PlayerStatus'),size=N.get(m,'PlayerSize'),max=N.get(m,'JnMaxHearts'),
        stage=m[0x5f3f],world=N.get(m,'WorldNumber'),level=N.get(m,'LevelNumber'),ready=m.ram[2][0x33],epoch=m.ram[2][0x34],
        frame=N.get(m,'FrameCounter'),life=N.get(m,'NumberofLives'),hp=N.get(m,'JnHealth'))
    class CPU(base):
        def step(self):
            nonlocal ensure_before_first_mirror
            m=self.memory
            if hasattr(m,'bundle')and m.bundle.get('raw')is raw:
                key=tag(m,self.pc),self.pc
                for name,point in native.items():
                    if key==point:
                        counts[name]+=1
                        if name=='JnEnsure'and not counts['mirror']:ensure_before_first_mirror=True
                        if len(events)<12:events.append(dict(name=name,PC=self.pc,SP=self.sp,fields=state(m)))
                if key==(3,0xb82c):
                    counts['mirror']+=1
                    assert N.get(m,'JnMaxHearts')>0,('Publication before persistent initialization',state(m))
                    assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(C.COOKIE,C.COOKIE)
                if key==(3,0xb832):
                    counts['post_mirror']+=1
                    assert N.get(m,'PlayerStatus')==N.get(m,'JnStars')>>7 and N.get(m,'PlayerSize')==0,('Post-publication parity/size',state(m))
            return super().step()
    with patch.object(N,'NesMPU',CPU):
        seed=J.cold(raw)
        for _ in range(4):seed.controller_pad=0;J.Frames.frame(seed,whole_pass=True);frames+=1
    assert ensure_before_first_mirror and counts['mirror']and counts['JnEnsure']
    assert seed.ram[2][0x33]and N.get(seed,'PlayerStatus')==N.get(seed,'JnStars')>>7
    rows=[dict(name='genuine compiled cold plus4 neutral updates',fields=state(seed),counts=dict(counts))]
    # Explicit lifecycle components, separate from natural item acquisition:
    # a private actor reset does not reset the persistent native food parity.
    earned,heart=heart_seed(raw)
    for label,original in(('cold parity0',seed),('real earned-heart parity80',earned)):
        for ready,level,frame in((0,0,254),(0,1,255),(1,0,255),(1,1,0)):
            m=N.fork(original);m.ram[2][0x33]=ready
            N.put(m,LevelNumber=level,FrameCounter=frame)
            before=state(m);prior=counts['mirror']
            with patch.object(N,'NesMPU',CPU):
                for _ in range(2):m.controller_pad=0;J.Frames.frame(m,whole_pass=True)
            assert counts['mirror']>prior and N.get(m,'PlayerStatus')==N.get(m,'JnStars')>>7
            assert N.get(m,'NumberofLives')==before['life']and N.get(m,'JnHealth')==before['hp']
            assert N.get(m,'JnStars')&128==before['stars']&128
            rows.append(dict(name='declared Ready/stage/epoch lifecycle component',seed=label,before=before,after=state(m)))
    # Every expected-header byte is faulted only in declared resident RAM.
    # The actual existing scene may reject or repair it before admission.
    header=[]
    for label,original in(('cold parity0',seed),('real earned-heart parity80',earned)):
        for bank in(1,2,3):
            for index in range(16):
                m=N.fork(original);m.ram[bank][0x1fe0+index]^=1;prior=counts['mirror']
                with patch.object(N,'NesMPU',CPU):m.controller_pad=0;J.Frames.frame(m,whole_pass=True)
                entered=counts['mirror']-prior
                if entered:assert tuple(bytes(m.ram[k][0x1fe0:0x1ff0])for k in(2,3))==(C.COOKIE,)*2
                if entered:assert N.get(m,'PlayerStatus')==N.get(m,'JnStars')>>7
                role='Steve-only R1 header outside JayHot admission'if bank==1 else('repaired-before-admission'if entered else'rejected-no-mirror')
                header.append(dict(seed=label,bank=bank,index=index,entered=entered,role=role))
    return dict(passed=True,scope='Genuine compiled cold witness plus declared resident Ready/stage/epoch/header-fault components',
        candidate_SHA256=J.PIN,all_three_cold_headers_new=True,first_JnEnsure_precedes_first_new_mirror=ensure_before_first_mirror,
        counts=dict(counts),initial_events=events,actual_earned_heart_seed=heart,lifecycle=rows,header_cases=len(header),
        header_fault_outcomes=dict(Counter(r['role']for r in header)),
        retained_fixture_negative81572='Incorrectly required Steve-only RAM1 header for JayHot, whose actual loop owns only RAM3/2. No code or gameplay change.',
        Starspolicy='Initialization clears the16B persistent block; stage gear clear and original drop writers preserve bit7; only actual typed collector togglesbit7.',
        no_new_food_or_weapons_seeded=True,outputs=0)


def irq(raw):
    """Pair actual parent/candidate ISRs at reached candidate header/leaf PCs."""
    parent=C.inverse(raw);base=N.NesMPU;seed,heart=heart_seed(raw)
    cold=J.cold(raw);counts=Counter();seen=set();cuts=[];effects=Counter();minimum=255
    owned_native=[(at,len(old))for at,old,_ in C.spans()if at<1048592]
    class Bus(W.ControllerBus):
        def __getitem__(self,at):
            if isinstance(at,int)and getattr(self,'_audit_ISR',False)and at in(0x759,0x75b):
                self._publication_reads.append((self._isr_pc,at))
            if isinstance(at,int)and getattr(self,'_audit_ISR',False)and at>=0x8000:
                tag=self.rawtags[(at-0x8000)//8192];off=at&8191
                if tag&128:
                    file=16+(tag&127)*8192+off
                    if any(lo<=file<lo+n for lo,n in owned_native):self._changed_reads.append(at)
                elif(tag==3 and(0x17f6<=off<0x1832 or 0x1ed7<=off<0x1edf))or(tag in(1,2,3)and 0x1fe0<=off<0x1ff0):
                    self._changed_reads.append(at)
            return super().__getitem__(at)
    def fork(m):
        t=N.fork(m);t.__class__=Bus;t._audit_ISR=False;t._changed_reads=[];t._publication_reads=[];t._isr_pc=0;return t
    def backing(m,old):
        m.bundle=dict(m.bundle,raw=parent if old else raw)
        m.ram[3][0x17f6:0x1800]=b'\xea'*10 if old else C.TAIL
        m.ram[3][0x1800:0x1832]=C.OLD_MAIN if old else C.NEW_MAIN
        m.ram[3][0x1ed7:0x1edf]=b'\xea'*8 if old else C.LEAF
        for bank in(1,2,3):m.ram[bank][0x1fe0:0x1ff0]=C.OLD_COOKIE if old else C.COOKIE
        if bytes(m.ram[1][0x1b9d:0x1bad])in(C.OLD_COOKIE,C.COOKIE):
            m.ram[1][0x1b9d:0x1bad]=C.OLD_COOKIE if old else C.COOKIE
        for slot,tag in enumerate(m.rawtags):
            if tag&128:m.raw_page(slot,tag)
    def regs(c):return(c.a,c.x,c.y,c.p&239,c.sp,c.pc)
    def transport(m):return(bytes(m[3:11]),bytes(m[0x15a:0x17b]),list(m.rawtags),list(m.chr_latches))
    def critical(m):return tuple(N.get(m,n)for n in('SelectedCharacter','NumberofLives','JnStars','PlayerStatus',
        'JnHealth','JnMaxHearts','JnOwnedTier','JnSelected','PlayerSize','GameEngineSubroutine','Player_X_Position','Player_PageLoc',
        'Player_Y_Position','Player_Y_HighPos','Player_State','Player_Y_Speed'))
    def finish(m,c,stop):
        entered=0
        for _ in range(500000):
            if(c.pc,c.sp)==stop:return entered
            if c.pc==q['hooks']['GameLoop']['PC']and m.rawtags[(c.pc-0x8000)//8192]==q['hooks']['GameLoop']['tag']:entered+=1
            assert m[c.pc],('ContinuationBRK',hex(c.pc));base.step(c)
        raise AssertionError(('Complete caller continuation bound',hex(c.pc),c.sp,stop))
    def paired(cpu,kind,stop):
        nonlocal minimum
        before_regs=regs(cpu);original=cpu.memory;models=[];prior=[]
        for old in(False,True):
            m=fork(original);backing(m,old);c=base(memory=m,pc=cpu.pc)
            c.a,c.x,c.y,c.p,c.sp=cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp
            prior.append(dict(private=[bytes(v)for v in m.ram],transport=transport(m),critical=critical(m),
                native=bytes(m[:0x800]),live=bytes(m[0x101+c.sp:0x200]),skip=N.get(m,'NmiSkipped')))
            m._audit_ISR=True
            c.irq()if kind=='IRQ'else c.nmi();models.append((m,c))
        for _ in range(100000):
            (a,ca),(b,cb)=models;minimum=min(minimum,ca.sp,cb.sp)
            assert regs(ca)==regs(cb)
            if(ca.pc,ca.sp)==(cpu.pc,cpu.sp):break
            assert a.rawtags==b.rawtags and a[ca.pc]and bytes(a[ca.pc:ca.pc+3])==bytes(b[cb.pc:cb.pc+3])
            a._isr_pc,b._isr_pc=ca.pc,cb.pc
            base.step(ca);base.step(cb)
        else:raise AssertionError('Actual ISR return bound')
        assert regs(ca)==regs(cb)==before_regs
        native=[]
        for(m,c),saved in zip(models,prior,strict=True):
            m._audit_ISR=False;assert not m._changed_reads,('ISR reads changed publication bytes',m._changed_reads)
            assert not m._publication_reads,('ISR observes size/status store order',m._publication_reads)
            assert[bytes(v)for v in m.ram]==saved['private']and transport(m)==saved['transport']and critical(m)==saved['critical']
            assert bytes(m[0x101+c.sp:0x200])==saved['live']
            assert N.get(m,'NmiSkipped')==(saved['skip']+int(kind=='busyNMI'))&255
            native.append(bytes(m[:0x800]))
        assert native[0]==native[1]
        for at,(a,b)in enumerate(zip(prior[0]['native'],native[0])):
            if a!=b and not 0x100<=at<0x200:effects[kind,at,a,b]+=1
        plain=fork(original);cp=base(memory=plain,pc=cpu.pc);cp.a,cp.x,cp.y,cp.p,cp.sp=cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp
        assert active_main_return is not None
        finish(plain,cp,active_main_return)
        for m,c in models:backing(m,False);finish(m,c,active_main_return)
        a,ca=models[0];b,cb=models[1]
        assert regs(ca)==regs(cb)==regs(cp),('Complete GameLoop meaningful registers',kind,hex(cpu.pc),regs(ca),regs(cb),regs(cp))
        assert[bytes(v)for v in a.ram]==[bytes(v)for v in b.ram]==[bytes(v)for v in plain.ram]
        assert transport(a)==transport(b)==transport(plain)and critical(a)==critical(b)==critical(plain)
        assert bytes(a[:0x800])==bytes(b[:0x800])
        assert bytes(a[0x101+ca.sp:0x200])==bytes(b[0x101+cb.sp:0x200])==bytes(plain[0x101+cp.sp:0x200])
        counts['complete_GameLoop_returns_no_extra_ISR']+=2
        # NmiSkipped is a real native busy-NMI effect. The idle caller may
        # therefore run a catch-up GameLoop, which must pair parent/candidate
        # exactly but cannot be equated with a no-extra-NMI idle pass.
        again_a=finish(a,ca,stop);again_b=finish(b,cb,stop)
        assert again_a==again_b
        assert regs(ca)==regs(cb)and[bytes(v)for v in a.ram]==[bytes(v)for v in b.ram]
        assert transport(a)==transport(b)and critical(a)==critical(b)and bytes(a[:0x800])==bytes(b[:0x800])
        counts[kind+':native_catchup_Main_entries']+=again_a
        counts[kind]+=1;counts['complete_idle_returns_paired']=counts['complete_idle_returns_paired']+2
    q=J.bindings(raw);stop=(W.address(seed.bundle,'IdleLoop'),253);active_label='';active_main_return=None
    class CPU(base):
        def step(self):
            nonlocal active_main_return
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if(tag,self.pc)==(q['hooks']['GameLoop']['tag'],q['hooks']['GameLoop']['PC']):
                active_main_return=((m[0x101+self.sp]+256*m[0x102+self.sp]+1)&65535,(self.sp+2)&255)
            own=tag==3 and(self.pc in(0xb825,0xb828,0xb82a,0xb82b,0xb82c,0xb82f,0xb832,0xb835)or 0xb7f6<=self.pc<0xb800 or 0xbed7<=self.pc<0xbedf)
            if own:
                key=(self.pc,self.sp,self.p&207,N.get(m,'JnStars'),m.ram[2][0x33])
                if key not in seen:
                    seen.add(key);assert len(seen)<128
                    if not self.p&4:paired(self,'IRQ',stop)
                    else:counts['masked_IRQ_shapes']+=1
                    assert N.get(m,'NmiDisable')==255
                    paired(self,'busyNMI',stop)
                    cuts.append(dict(seed=active_label,PC=self.pc,SP=self.sp,P=self.p,stars=N.get(m,'JnStars'),ready=m.ram[2][0x33],size=N.get(m,'PlayerSize'),status=N.get(m,'PlayerStatus')))
            return super().step()
    for label,m in(('genuine cold parity0',cold),('genuine earned-heart parity80',seed)):
        active_label=label
        with patch.object(N,'NesMPU',CPU):
            for _ in range(2):m.controller_pad=0;J.Frames.frame(m,whole_pass=True)
    assert counts['IRQ']and counts['busyNMI']and any(r['PC']==0xbedb and r['stars']==128 for r in cuts)
    assert any(r['PC']==0xbeda and r['stars']==128 for r in cuts)
    assert any(r['PC']==0xb7fc for r in cuts)and not any(r['PC']==0xb7ff for r in cuts)
    return dict(passed=True,candidate_SHA256=J.PIN,parent_native_backing_SHA256=C.PIN,actual_heart_seed=heart,
        counts=dict(counts),reached_cuts=cuts,minimum_ISR_SP=minimum,
        full_AXYP_and_native_parent_ISR_effects_equal=True,all_private_SMC_maps_live_stack_preserved=True,
        actual_ISR_PlayerSize_and_PlayerStatus_reads=0,between_stores_cuts_qualified=True,
        complete_GameLoop_return_matches_no_extra_ISR=True,complete_idle_catchup_returns_paired=True,no_changed_ISRs_or_cookie_reads=True,
        retained73680_fixture_negative='Whole idle compared to no-extra-NMI despite actual NmiSkipped catch-up control; strict comparison now stops at dynamic GameLoop return, then full idle is paired native-parent/candidate.',
        native_effects=[dict(kind=k[0],address=k[1],before=k[2],after=k[3],cases=v)for k,v in sorted(effects.items())],
        scope='Reached cold0 and realheart80 full status/size tail/both stores; strict actual GameLoop return and paired full idle/catch-up, no deepest-nesting or fullstage claim',outputs=0)


def run(kind):
    assert J.H(Path(C.__file__).read_bytes())==C_SHA and J.H(Path(J.__file__).read_bytes())==J_SHA
    raw=J.load_current_image()
    q=(lifecycle if kind=='lifecycle'else irq)(raw);q.update(C_SHA256=C_SHA,J_SHA256=J_SHA,source_SHA256=J.H(Path(__file__).read_bytes()))
    q['receipt_SHA256']=J.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=('lifecycle','irq'),default='lifecycle');a=p.parse_args()
    print('RESULT '+json.dumps(run(a.kind),separators=(',',':')),flush=True)



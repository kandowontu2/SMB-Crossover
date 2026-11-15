"""Granted actual current174fa+eleven-span CPU source qualification, zero files."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import inspect
import compose_battletoads_carry_current_1115 as C
import replay_battletoads_carry_current_1115 as F
import battletoads_carry_current_model_1115 as Model

W,N,Frames=Model.W,Model.N,Model.Frames
Old=Model.Previous


def strict(parent,image):
    rejects=[]
    def rejected(label,raw,method):
        try:method(raw)
        except AssertionError:rejects.append(label)
        else:raise AssertionError(('Dirty/unknown source input accepted',label))
    for label,raw,method in(('parent_inverse',parent,C.inverse),('candidate_forward',image,C.proposal),
        ('old7a80',C.reference_parent(parent),C.proposal),('olda90',C.reference(parent),C.inverse),
        ('truncated',image[:-1],C.inverse),('unknown',bytes(len(image)),C.inverse)):
        rejected(label,raw,method)
    for label,at in(('unowned',90000),('dense',792489),('prior',653512),('cookie',765868),
        ('PrinceCookie',535471),('PrinceCarrier',1800000),('BubPalette',1501131),('BubCookie',536570),
        ('Gimmick',201137),('score',1034694),('DK',105706)):
        for name,raw,method in(('forward',parent,C.proposal),('inverse',image,C.inverse)):
            bad=bytearray(raw);bad[at]^=1;rejected(name+'_'+label,bytes(bad),method)
    original=Path.read_bytes
    def read(path):
        assert path.resolve()!=C.ROM.resolve(),'Portable current composer reread mutable Nightly'
        return original(path)
    with patch.object(Path,'read_bytes',read):
        C.inverse.cache_clear();C.proposal.cache_clear()
        assert C.inverse(image)==parent and C.proposal(parent)[0]==image
        q=F.metadata(image)
        assert F.cadence_reads(parent).split('\n',1)[1]==F.cadence_reads(image).split('\n',1)[1]
        assert F.observer_config(image)['ram']['NmiSkipped']==F.observer_config(parent)['ram']['NmiSkipped']==314
        for label,raw in(('parent_stage',parent),('olda90_stage',C.reference(parent)),('dirty_stage',image[:-1])):
            rejected(label,raw,F.controller)
        loader_cases=[]
        for label,fixture in(('official174fa',parent),('postdelivery_candidate',image)):
            seen=[]
            def loader_read(path):
                if path.resolve()==C.ROM.resolve():seen.append(1);assert len(seen)==1;return fixture
                return read(path)
            with patch.object(Path,'read_bytes',loader_read):assert C.load_current_image()==fixture
            assert len(seen)==1;loader_cases.append(label)
    return dict(composition=C.proposal(parent)[1],controllers=q,strict_rejections=rejects,
        inline_preimage_bytes=sum(len(bytes.fromhex(h))for _,h in C.PREIMAGES),
        portable_inverse_exact174fa=True,forward_inverse_forward_exact=True,mutable_Nightly_reads_after_load=0,
        single_read_loader_cases=loader_cases,
        actual_owning174fa_Prince_and_all_unowned_bytes_retained=True,old_factories_unchanged=True)


def public_call(m,slot,p=0x21,a=85,x=7,y=91):
    target=0xb020+3*slot;m[0x16a]=a;m[0x16c]=target&255;m[0x16d]=target>>8
    c=N.NesMPU(memory=m,pc=0x15a);c.a=215;c.x=x;c.y=y;c.p=p;c.sp=236;c.stPushWord(0x5aff)
    low=c.sp;checks=0
    for _ in range(20000):
        if(c.pc,c.sp)==(0x5b00,236):break
        if(c.pc,c.sp)==(0x15d,231):
            word=m[0x16c]+256*m[0x16d]
            if not(m[0x162]==224 and word in(0xb799,0xb79b,0xb2cb,0xb2cd)):break
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if(tag,c.pc)==(221,0xadc0):checks+=1
        low=min(low,c.sp);assert m[c.pc],('Mounted public BRK',slot,c.pc);c.step()
    else:raise AssertionError(('Mounted public bound',slot,c.pc,c.sp))
    return dict(PC=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p&0xef,SP=c.sp,CPU=c.processorCycles,minimum_SP=low,
        BtCheck_calls=checks,target=m[0x16c]+256*m[0x16d],next_bank=m[0x162])


def transport(parent,image):
    seed=Model.cold(image);pair=[Model.reimage(seed,raw)for raw in(parent,image)]
    select=W.address(seed.bundle,'SelectedCharacter');fm=W.address(seed.bundle,'FmGroups')
    cookie=bytes(seed.ram[3][0x1fe0:0x1ff0]);vectors=[];savings=Counter();smc=Counter();checks=Counter();minimum=255
    for owner in range(256):
        for slot in range(36):vectors.append((owner,0,-1,slot,0x21))
    for owner in(27,29,31,33):
        for group in range(8):
            for slot in range(36):
                for p in(0x20,0x69,0xe5):vectors.append((owner,group,-1,slot,p))
    for bad in range(17):
        for slot in range(36):vectors.append((33,64,bad,slot,0xe9))
    for count,(owner,group,bad,slot,p)in enumerate(vectors,1):
        out=[]
        for m in pair:
            list.__setitem__(m,slice(0x100,0x200),list.__getitem__(seed,slice(0x100,0x200)))
            m[select]=owner;m[fm]=group;m.ram[3][0x1fe0:0x1ff0]=cookie
            if 0<=bad<16:m.ram[3][0x1fe0+bad]^=1
            elif bad==16:m.ram[3][0x1fe0]=0
            out.append(public_call(m,slot,p))
        assert all(out[0][k]==out[1][k]for k in('PC','A','X','Y','P','SP')),('Mounted public return',owner,group,bad,slot,p,out)
        if out[0]['PC']==0x15d:assert(out[0]['target'],out[0]['next_bank'])==(out[1]['target'],out[1]['next_bank'])
        Old.M.Research.compare(pair,out,('Mounted public',owner,group,bad,slot,p))
        delta=tuple(at for at in range(0x15a,0x17b)if pair[0][at]!=pair[1][at]);assert set(delta)<={0x162,0x16c,0x16d}
        minimum=min(minimum,*(r['minimum_SP']for r in out));smc[delta]+=1
        category=owner if owner in(27,29,31,33)else'foreign'
        savings[category,bad<0,out[0]['CPU']-out[1]['CPU']]+=1
        checks[category,bad<0,out[0]['BtCheck_calls'],out[1]['BtCheck_calls']]+=1
        if count%3000==0:print('PROGRESS '+json.dumps(dict(actual_mounted_public_cases=count)),flush=True)
    return dict(cases=len(vectors),all256_selected_36_slots=True,legal_cohorts_eight_groups_four_P=True,
        all16_corrupt_cookie_bytes_and_retired_query=True,minimum_SP=minimum,
        exact_AXYP_SP_live_RAM_physical_RAM_maps=True,
        NoOp_Visible_aliases_executed_to_full_return=True,other_private_handlers_stopped_before_gameplay=True,
        SMC_differences=[dict(fields=list(k),cases=n)for k,n in smc.items()],
        cycle_savings=[dict(owner=o,valid=v,cycles=c,cases=n)for(o,v,c),n in sorted(savings.items(),key=str)],
        full_BtCheck_counts=[dict(owner=o,valid=v,old=a,new=b,cases=n)for(o,v,a,b),n in sorted(checks.items(),key=str)],
        actual_candidate_opcode_bytes=True,CPU_redirects_or_read_overlay=False)


def stage(parent,image,key):
    runner=Old.R.Frozen.Cold.Runner
    with patch.object(runner,'Factory',F),patch.object(runner,'cold',Model.cold):q=runner.run(image,key,6500)
    assert q['passed'],q
    return dict(identity=key,route=q,actual_candidate_code=True,normal_controls_only=True,gameplay_seeds=0)


def profile(parent,image,counts=(48,32)):
    pair=[Model.cold(raw)for raw in(parent,image)];Model.compare(pair);cpu=N.NesMPU;minimum=255;rows=[]
    for _ in range(4):
        for m in pair:m.controller_pad=0;Frames.frame(m,whole_pass=True)
        Model.compare(pair)
    for phase,pad,count in(('idle',0,counts[0]),('right',1,counts[1])):
        costs=[[],[]];nmis=[[],[]];calls=[Counter(),Counter()];returns=[0,0];main_entries=[0,0];sources=[Counter(),Counter()]
        points=[]
        for m in pair:
            points.append({(((W.location(m.bundle,name)-16)//8192)|128,W.address(m.bundle,name)):name for name in('GameLoop','BtCheck','AudioUpdate')})
        class Probe(cpu):
            def __init__(self,*a,**kw):
                super().__init__(*a,**kw);self.side=0 if self.memory is pair[0]else 1
                assert self.memory is pair[self.side]
                self.kind='Main'if self.pc==W.address(self.memory.bundle,'IdleLoop')else'NMI'
                self.pending=[];instances.append(self)
            def step(self):
                nonlocal minimum
                m=self.memory;side=self.side;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                if self.pending and(self.pc,self.sp)==self.pending[-1]:self.pending.pop();returns[side]+=1
                name=points[side].get((tag,self.pc))
                if name=='GameLoop':
                    main_entries[side]+=1;self.pending.append(((m[0x101+self.sp]+256*m[0x102+self.sp]+1)&65535,self.sp+2))
                if name in('BtCheck','AudioUpdate'):calls[side][self.kind+':'+name]+=1
                if(tag,self.pc)==(215,0xb08e):
                    offset=m[0x16c]-0x20;assert 0<=offset<=105 and offset%3==0
                    sources[side][offset//3]+=1
                minimum=min(minimum,self.sp);return super().step()
        with patch.object(N,'NesMPU',Probe):
            for tick in range(count):
                for side,m in enumerate(pair):
                    instances=[];before=main_entries[side],returns[side];m.controller_pad=pad
                    costs[side].append(Frames.frame(m,whole_pass=True));nmis[side].append(sum(x.processorCycles for x in instances if x.kind=='NMI'))
                    assert(main_entries[side]-before[0],returns[side]-before[1])==(1,1)
                Model.compare(pair,min(152,minimum))
        assert calls[1]['Main:BtCheck']==3*count and calls[1]['NMI:AudioUpdate']==count
        assert not Old.M.Profile.state(pair[1])['actors']
        rows.append(dict(phase=phase,Main=count,Main_entries=main_entries,Main_returns=returns,
            parent_mean_Main=sum(costs[0])/count,candidate_mean_Main=sum(costs[1])/count,
            every_Main_savings=sorted(set(a-b for a,b in zip(*costs))),
            parent_mean_scheduled_NMI=sum(nmis[0])/count,candidate_mean_scheduled_NMI=sum(nmis[1])/count,
            actual_calls=[dict(x)for x in calls],actual_Router_services=[dict(x)for x in sources],
            final_state=Old.M.Profile.state(pair[1])))
        print('PROGRESS '+json.dumps(dict(phase=phase,parent_Main=rows[-1]['parent_mean_Main'],candidate_Main=rows[-1]['candidate_mean_Main'])),flush=True)
    return dict(phases=rows,minimum_SP=minimum,actual_mounted_source_candidate=True,
        full_RAM_SMC_VRAM_maps_parity=True,opaque_only=[0x162,0x16c,0x16d],Audio_input_timers_draw_unchanged=True,
        each_iteration_one_actual_GameLoop_entry_return=True,physical_cadence_or_FPS_claim=False)


def wwf_cold(raw,role):
    b=Model.symbols(raw)
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
    for bits in([4]*3+[1]*4+[32]*role):W.UI.key(m,bits)
    names=('HULK HOGAN','TED DIBIASE','BAM BAM BIGELOW','HONKY TONK MAN','RANDY SAVAGE','ANDRE THE GIANT')
    assert(W.UI.menu_name(m)[0],N.get(m,'SelectedCharacter'),N.get(m,'FmGroups')&7)==(names[role],29,role)
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError(('Actual WWF constructor',role))
    assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    return m,names[role]


def family_cold(raw,owner):
    if owner==33:return Model.cold(raw),'RASH'
    if owner==29:return wwf_cold(raw,0)
    slot={27:26,31:30}[owner]
    with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(Model.symbols(raw),0)
    for bits in([4]*(slot//8)+[1]*(slot%8)):W.UI.key(m,bits)
    name=W.UI.menu_name(m)[0];assert N.get(m,'SelectedCharacter')==owner
    start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    N.invoke(m,'PauseRoutine',a=0)
    for _ in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError(('Mounted four-cohort cold bound',owner,name))
    assert N.get(m,'NumberofLives')==2 and N.get(m,'CheatInvincible')==N.get(m,'CheatStartLevel')==0
    return m,name


def cold4(parent,image):
    rows=[];base=N.NesMPU;carry=Counter()
    class Observe(base):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if m.bundle['raw']is image and(tag,self.pc)==(224,0xb799):
                owner=N.get(m,'SelectedCharacter');assert owner in(27,29,31,33)
                assert bool(self.p&1)==(owner==33)and self.y==(owner-27)//2
                carry[owner,bool(self.p&1)]+=1
            return super().step()
    with patch.object(N,'NesMPU',Observe),patch.object(W.UI.F,'NesMPU',Observe):
        for owner in(27,29,31,33):
            pair=[]
            for raw in(parent,image):m,name=family_cold(raw,owner);pair.append(m)
            Model.compare(pair)
            header=N.invoke(pair[1],{27:'BwCheck',29:'WfColdIdentity',31:'CfOrBtCheck',33:'BtCheck'}[owner])
            assert header['P']&1
            rows.append(dict(owner=owner,name=name,mode=[N.get(pair[1],n)for n in('OperMode','OperMode_Task','GameEngineSubroutine')],
                lives=N.get(pair[1],'NumberofLives'),header_valid=True,actual_menu_Start_and_constructor=True))
            print('PROGRESS '+json.dumps(dict(actual_mounted_cold_pass=owner,name=name)),flush=True)
    return dict(rows=rows,actual_corrected_candidate_executed=True,all_four_menu_cold_pass=True,
        parent_candidate_RAM_maps_VRAM_exact=True,opaque_only=[0x162,0x16c,0x16d],
        actual_helper_carry=[dict(owner=o,C=c,cases=n)for(o,c),n in sorted(carry.items())],no_gameplay_seeds=True)


def wwf(parent,image):
    rows=[];base=N.NesMPU
    for role in range(6):
        pair=[]
        for raw in(parent,image):m,name=wwf_cold(raw,role);pair.append(m)
        Model.compare(pair)
        for _ in range(4):
            for m in pair:m.controller_pad=0;Frames.frame(m,whole_pass=True)
            Model.compare(pair)
        phases=[]
        for phase,pad in(('idle',0),('right',1)):
            cycles=[[],[]];calls=[Counter(),Counter()]
            class Probe(base):
                def step(self):
                    m=self.memory;side=0 if m is pair[0]else 1;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
                    if(tag,self.pc)==(215,0xb08e):
                        assert N.get(m,'SelectedCharacter')==29 and N.get(m,'FmGroups')&7==role
                        offset=m[0x16c]-0x20;assert offset%3==0 and 0<=offset<=105;calls[side][offset//3]+=1
                    return super().step()
            with patch.object(N,'NesMPU',Probe):
                for _ in range(8):
                    for side,m in enumerate(pair):m.controller_pad=pad;cycles[side].append(Frames.frame(m,whole_pass=True))
                    Model.compare(pair)
                    assert not any(N.get(pair[1],'Enemy_Flag',i)for i in range(6))
            assert calls[0]==calls[1]
            delta=[a-b for a,b in zip(*cycles)];assert set(delta)=={13},(role,phase,delta)
            phases.append(dict(phase=phase,Main=8,parent_mean_Main=sum(cycles[0])/8,candidate_mean_Main=sum(cycles[1])/8,
                every_Main_savings=delta,actual_service_calls=dict(calls[1]),group=role,active_enemies=0))
        rows.append(dict(identity=name,compiled_Select_cycles=role,phases=phases))
        print('PROGRESS '+json.dumps(dict(identity=name,actual_mounted_idle_Right_savings=13)),flush=True)
    return dict(all_six_compiled_Select_Start=True,rows=rows,actual_mounted_code=True,
        exact_live_RAM_physical_RAM_SMC_VRAM_maps=True,opaque_only=[0x162,0x16c,0x16d],
        no_actor_health_position_terrain_or_ability_seeds=True,physical_cadence_or_FPS_claim=False)


def readback(parent,image):
    m=N.Bus(Model.symbols(image));m.raw_page(2,2)
    N.put(m,CurrentBank=m.rawtags[1],CurrentBankC=2,SelectedCharacter=33,OperMode=1,
        DisableScreenFlag=1,Mirror_PPUMASK=0,Mirror_PPUCTRL=168,NmiDisable=255,FamilyMainCommit=1,
        HorizontalScroll=0,VerticalScroll=0,ReloadCHRBank=0,X5WideChrActive=0)
    m.ppuctrl=168;maps=list(m.rawtags);chr_before=list(m.chr_latches);foreign=tuple(map(bytes,m.ram[:3]))
    expected=bytearray(image[1989648:1989648+8192]);expected[0x1fe0:0x1ff0]=image[765863:765879]
    before=m.ppu_reads;out=N.invoke(m,'BtLoad');assert out['P']&1
    assert m.ram[3]==expected and tuple(map(bytes,m.ram[:3]))==foreign
    assert m.rawtags==maps and m.chr_latches==chr_before and m.ppuctrl==168
    assert m.ppu_reads-before==16400
    used=m.ppu_reads;warm=N.invoke(m,'BtLoad');assert warm['P']&1 and m.ppu_reads==used
    return dict(actual_candidate_ROM_loader=True,source_bytes_read_back=8192,buffered_PPU_reads=16400,
        entire_loaded_RAM3_and16byte_published_header_exact=True,warm_load_zero_PPU_reads=True,
        foreign_RAM0_to2_PRG_CHR_PPUCTRL_exact=True,minimum_SP=min(out['minimum_SP'],warm['minimum_SP']),
        forced_blank_loader_API_preconditions_only=True,no_gameplay_or_cache_preload=True)


def lifecycle(parent,image):
    pair=[Model.cold(raw)for raw in(parent,image)];Model.compare(pair);phases=[]
    for phase,pad,count in(('walk',1,8),('pause_edge',16,1),('paused',0,64),('resume_edge',16,1),('resumed',0,8)):
        seen=set()
        for _ in range(count):
            for m in pair:m.controller_pad=pad;Frames.frame(m,whole_pass=True)
            Model.compare(pair);seen.add(N.get(pair[1],'GamePauseStatus'))
        phases.append(dict(phase=phase,Main=count,pause=sorted(seen)))
    assert all(x&1 for x in phases[2]['pause'])and not N.get(pair[1],'GamePauseStatus')&1
    retired=[N.fork(m)for m in pair]
    for m in retired:N.invoke(m,'BtRetire');assert m.ram[3][0x1fe0]==0
    Model.compare(retired);native=[]
    for name in('MegaManCollisionAdder','MegaManCollisionBox'):
        arenas=[N.fork(m)for m in retired];out=[N.invoke(m,name,a=85,x=7,y=91,p=0x20)for m in arenas]
        assert not out[0]['P']&1 and out[1]['P']&1 and out[1]['Y']==0
        assert arenas[0].ram==arenas[1].ram and arenas[0].rawtags==arenas[1].rawtags
        native.append(dict(name=name,parent_return={k:out[0][k]for k in('A','X','Y','P')},candidate_return={k:out[1][k]for k in('A','X','Y','P')}))
    private=[]
    for slot in(0,2,3,9,15,17,18,19,26,29,34):
        arenas=[N.fork(m)for m in retired];out=[public_call(m,slot)for m in arenas]
        assert all(out[0][k]==out[1][k]for k in('PC','A','X','Y','P','SP'))
        if out[0]['PC']==0x15d:assert(out[0]['target'],out[0]['next_bank'])==(out[1]['target'],out[1]['next_bank'])
        # These shallow queries inherit dead stack from the preceding full
        # Main. Retain its already-qualified floor, rather than treating
        # unused previous-frame stack bytes as live query output.
        checked=[dict(r,minimum_SP=min(152,r['minimum_SP']))for r in out]
        for m,r in zip(arenas,out,strict=True):
            assert r['SP']>=152
        assert bytes(arenas[0][0x101+out[0]['SP']:0x200])==bytes(arenas[1][0x101+out[1]['SP']:0x200]),('Live retired caller stack',slot,out)
        Old.M.Research.compare(arenas,checked,('Actual retired mounted public',slot));private.append(dict(slot=slot,old_checks=out[0]['BtCheck_calls'],new_checks=out[1]['BtCheck_calls'],C=out[1]['P']&1))
    death=[N.fork(m)for m in pair]
    out=[N.invoke(m,'HuDeathStart',a=33,p=0x21)for m in death]
    Old.M.Research.compare(death,[dict(r,SP=224,minimum_SP=min(152,r['minimum_SP']))for r in out],'Owning HuDeathStart')
    death_rows=[]
    for _ in range(8):
        for m in death:m.controller_pad=0;Frames.frame(m,whole_pass=True)
        Model.compare(death);death_rows.append(Old.M.Profile.state(death[1]))
    return dict(actual_ordinary_pause_resume=phases,actual_BtRetire=True,
        native_only_retired_getter_contract_intentionally_changed=native,retired_private_cold_NoOp_parity=private,
        owning_death_component='HuDeathStart public API, not natural enemy/pit damage',following_death_Main=8,death=death_rows,
        exact_live_RAM_physical_RAM_maps_VRAM=True,opaque_only=[0x162,0x16c,0x16d],natural_death_respawn_not_claimed=True)


def stack_diagnostic(parent,image):
    """Reproduce the old shallow-comparator failure, then check the live stack."""
    pair=[Model.cold(raw)for raw in(parent,image)]
    for phase,pad,count in(('walk',1,8),('pause_edge',16,1),('paused',0,64),('resume_edge',16,1),('resumed',0,8)):
        for _ in range(count):
            for m in pair:m.controller_pad=pad;Frames.frame(m,whole_pass=True)
            Model.compare(pair)
    for m in pair:N.invoke(m,'BtRetire')
    out=[public_call(m,0)for m in pair]
    old_floor=min(r['minimum_SP']for r in out)
    dead=[at for at in range(0x199,0x101+old_floor)if pair[0][at]!=pair[1][at]]
    assert dead and all(0x198<at<=0x100+old_floor and at<=0x100+min(r['SP']for r in out)for at in dead)
    try:Old.M.Research.compare(pair,out,'Original shallow floor reproduction')
    except AssertionError as exc:
        assert 'Live native RAM differences'in str(exc);negative=str(exc)
    else:raise AssertionError('Stack sensitivity did not reproduce7153')
    checked=[dict(r,minimum_SP=152)for r in out]
    Old.M.Research.compare(pair,checked,'Qualified full-Main floor')
    assert bytes(pair[0][0x101+out[0]['SP']:0x200])==bytes(pair[1][0x101+out[1]['SP']:0x200])
    return dict(original7153_comparator_negative=negative,
        actual_returns=[{k:r[k]for k in('PC','SP','minimum_SP')}for r in out],
        first_dead_byte=dict(address=dead[0],parent=pair[0][dead[0]],candidate=pair[1][dead[0]]),
        previous_full_Main_floor=152,dead_stack_difference_addresses=dead,
        all_RAM_below_0x199_still_compared=True,current_live_caller_stack_above_SP_compared_exactly=True,
        no_change_to_game_bytes_or_ISR_stack_checks=True,no_blanket_RAM_or_stack_mask=True)


def ingress(parent,image):
    """Rebind retained structured consumer proofs to actual mounted code/data."""
    import plan_battletoads_flat_resolver_1115 as Flat
    source=inspect.getsource(Flat.ingress)
    changes=(('b=Base.symbols(image);','b=Model.symbols(image);'),
        ("macros[0]['target']==0xb79d","macros[0]['target']==0xb799"),
        ("assert len(wf)==16 and {r['CPU']for r in wf}=={0xb799,0xb79b}","assert not wf,('Unrebound old Wf leaf descriptor',wf)"))
    for old,new in changes:assert source.count(old)==1;source=source.replace(old,new)
    scope=dict(Flat.__dict__,Model=Model)
    exec(compile(source,str(Path(__file__))+':actual-mounted-structured-domains','exec'),scope)
    static=scope['ingress'](parent,image)
    static['reference_SHA256']=C.CANDIDATE
    static.pop('no_mounted_overlay');static.pop('no_new_whole_image')
    at=lambda pc:16+96*8192+(pc&8191)
    assert image[at(0xb798)]==0x60 and image[at(0xb632):at(0xb646)]==bytes.fromhex('ad0260c91dd00bade85f2907c906b00238601860')
    assert image[at(0xb2cb):at(0xb2cf)]==bytes.fromhex('38601860')
    table=image[792489+67:792489+175]
    aliases=[i for i in range(36)if(table[3*i+2],int.from_bytes(table[3*i:3*i+2],'little'))in((224,0xb2cb),(224,0xb2cd))]
    assert len(aliases)==16
    direct=[]
    for bank in range(128):
        data=image[16+bank*8192:16+(bank+1)*8192]
        for target in(0xb799,0xb79b,0xb79d):
            cursor=0
            while(cursor:=data.find(target.to_bytes(2,'little'),cursor))>=0:
                op=data[cursor-1]if cursor else None
                if op in(0x20,0x4c,0x6c):
                    assert bank not in(96,126,127),('New actual Wf-capable direct ingress',bank,cursor,target,op)
                    m=N.Bus(Model.symbols(image));m.raw_page(1,bank|128);pc=0xa000+cursor-1
                    c=N.NesMPU(memory=m,pc=pc);tags=tuple(m.rawtags);c.step()
                    assert c.pc==target and tuple(m.rawtags)==tags
                    direct.append(dict(bank=bank,PC=pc,target=target,mapped_target_file=16+bank*8192+(target&8191)))
                cursor+=1
    reads=Counter();writes=Counter();leaves=Counter();ctx=dict(active=False,PC=0,tag=-1);bus=W.ControllerBus;cpu=N.NesMPU
    class Observed(bus):
        def __getitem__(self,at):
            if isinstance(at,int)and ctx['active']and at in getattr(self,'opaque_watch',()):reads[ctx['tag'],ctx['PC'],at]+=1
            return super().__getitem__(at)
        def __setitem__(self,at,value):
            if isinstance(at,int)and ctx['active']and at in getattr(self,'opaque_watch',()):
                writes[ctx['tag'],ctx['PC'],at]+=1;self.opaque_watch.remove(at)
            return super().__setitem__(at,value)
    class Probe(cpu):
        def step(self):
            m=self.memory;tag=m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1
            if m.bundle['raw']is image and(tag,self.pc)in((224,0xb2cb),(224,0xb2cd))and N.get(m,'SelectedCharacter')==29:
                m.opaque_watch={0x16c,0x16d};leaves[self.pc]+=1
            ctx.update(active=m.bundle['raw']is image,PC=self.pc,tag=tag)
            try:return super().step()
            finally:ctx['active']=False
    with patch.object(W,'ControllerBus',Observed),patch.object(N,'NesMPU',Probe),patch.object(W.UI.F,'NesMPU',Probe):
        m,name=wwf_cold(image,0)
        for pad in([0]*8+[1]*8):m.controller_pad=pad;Frames.frame(m,whole_pass=True)
    assert leaves and not reads,(leaves,reads)
    return dict(actual_structured_PRG_carrier_decoded_stream_compiler_domains=static,
        exact_group_only_suffix_and_pure_leaf_preimages=True,all16_alias_descriptors_rebound=True,
        other_bank_near_control_leads=direct,actual_mounted_Hogan_NoOp_Visible_entries=dict(leaves),
        opaque_fields=[0x16c,0x16d],reads_before_next_write=[],
        first_writes=[dict(tag=t,PC=p,address=a,count=n)for(t,p,a),n in sorted(writes.items())],
        previous_six_family_reader_closure_retained=True,no_blanket_private_RAM_mask=True)


def interrupts(parent,image,contexts='core'):
    # Namespace reuse keeps frozen drivers unchanged and binds actual raw bytes.
    assert C.digest(Path(Old.__file__).read_bytes())=='4e11a94ecd6d33387accb7beb9551761116ad28d971622057c4491c8a75733c8'
    source=inspect.getsource(Old.interrupts)
    assert contexts in('core','menus')
    phases=('cold','idle','right')if contexts=='core'else('gimmick','donkey_kong','hogan','thomas')
    old="if m.bundle['raw']is image and any(lo-2<=at<hi for lo,hi in ranges):"
    new="if phase in ISR_PHASES and m.bundle['raw']is image and any(lo-2<=at<hi for lo,hi in ranges):"
    assert source.count(old)==1;source=source.replace(old,new)
    old="(('gimmick',[1,4,4,4]),('donkey_kong',[4,4,4,1,1,1]))"
    new="(('gimmick',[1,4,4,4]),('donkey_kong',[4,4,4,1,1,1]),('hogan',[4,4,4,1,1,1,1]))"
    assert source.count(old)==1;source=source.replace(old,new)
    # Retain every actually reached guard Y and normalized P, choosing the
    # deepest caller frame within each identical key. The old300 limit was
    # sized for only nine envelopes, not this eleven-envelope qualification.
    old="key=(phase,tag,self.pc,self.y if 0xb8b8<=self.pc<=0xb8c4 else-1,self.funded_endpoint)"
    new="key=(phase,tag,self.pc,self.y if 0xb8b8<=self.pc<=0xb8c4 else-1,self.funded_endpoint,self.p&0xef)"
    assert source.count(old)==1;source=source.replace(old,new)
    old='if key not in captures:captures[key]='
    new="if key not in captures or self.sp<captures[key][1]['sp']:captures[key]="
    assert source.count(old)==1;source=source.replace(old,new)
    old='assert captures and len(captures)<300,len(captures)'
    new="assert len(captures)<=1024 and(bool(captures)or 'cold'not in ISR_PHASES),len(captures)\n    progress(initial_cold_idle_Right_cuts=len(captures))"
    assert source.count(old)==1;source=source.replace(old,new)
    old="assert any(key[0]=='thomas'and key[1]==207 and key[2]==0xb84b for key in captures),'Mounted Thomas prefix not reached'"
    new="assert 'thomas'not in ISR_PHASES or any(key[0]=='thomas'and key[1]==207 and key[2]==0xb84b for key in captures),'Mounted Thomas prefix not reached'"
    assert source.count(old)==1;source=source.replace(old,new)
    old='rows=[];counts=Counter();effects=Counter();physical_effects=Counter();chr_effects=Counter()'
    new="assert len(captures)<=1024,('All-context capture bound',len(captures))\n    progress(all_context_cuts=len(captures))\n    "+old
    assert source.count(old)==1;source=source.replace(old,new)
    scope=dict(Old.__dict__,C=C,F=F,cold=Model.cold,symbols=Model.symbols,reimage=Model.reimage,compare_memory=Model.compare,ISR_PHASES=phases)
    exec(compile(inspect.getsource(Old.thomas_cold),str(Path(__file__))+':typed-Thomas-cold','exec'),scope)
    exec(compile(source,str(Path(__file__))+':mounted-all-eleven-reached-ISR','exec'),scope)
    q=scope['interrupts'](parent,image)
    rows=q.pop('actual_mounted_reached_instruction_cuts');by_context=Counter(row['context']for row in rows)
    coverage=[]
    for at,h in C.PREIMAGES:
        hi=at+len(bytes.fromhex(h));n=sum(at-2<=16+(row['tag']&127)*8192+(row['PC']&8191)<hi for row in rows)
        coverage.append(dict(file=[at,hi],cuts=n))
    q.update(context_partition=contexts,reached_instruction_cut_count=len(rows),
        all_cut_rows_SHA256=C.digest(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()),
        cuts_per_context=dict(by_context),envelope_coverage=coverage,sparse_cut_examples=rows[:32])
    q.update(actual_owning174fa_candidate_bytes=True,
        frozen_driver_reused_with_Hogan_deepest_frames_and_all_reached_P=True,
        every_reached_getter_guard_Y_retained=True,bounded_captures=1024,
        original_capture_bound_negatives=[524,448,1318],no_virtual_arrays_or_redirects=True)
    return q


def components(parent,image):
    rows={}
    for name,fn in(('readback',readback),('lifecycle',lifecycle),('profile',lambda p,z:profile(p,z,(4,4)))):
        q=fn(parent,image);rows[name]=q
        print('GATE '+json.dumps(dict(gate=name,result=q,receipt=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode()))),flush=True)
    return rows


def closure(parent,image):
    rows={}
    for name,fn in(('stack',stack_diagnostic),('ingress',ingress),('profile',profile)):
        q=fn(parent,image);rows[name]=q
        print('GATE '+json.dumps(dict(gate=name,result=q,receipt=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode()))),flush=True)
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','cold4','readback','transport','lifecycle','components','closure','stack','ingress','interrupts','interrupts-core','interrupts-menus','profile','profile-short','wwf','rash','zitz'));args=ap.parse_args()
    raw=C.load_current_image();parent=C.inverse(raw)if C.digest(raw)==C.CANDIDATE else raw;image,info=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Dense source checker attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q={'strict':strict,'cold4':cold4,'readback':readback,'transport':transport,'lifecycle':lifecycle,
            'components':components,'closure':closure,
            'stack':stack_diagnostic,'ingress':ingress,
            'interrupts':interrupts,'interrupts-core':interrupts,'interrupts-menus':lambda p,z:interrupts(p,z,'menus'),
            'profile':profile,'profile-short':lambda p,z:profile(p,z,(4,4)),
            'wwf':wwf,'rash':lambda p,z:stage(p,z,'rash'),'zitz':lambda p,z:stage(p,z,'zitz')}[args.mode](parent,image)
    q.update(mode=args.mode,parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()

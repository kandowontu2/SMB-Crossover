"""Granted actual current40a+eleven-span CPU source qualification, zero files."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse,json
import compose_battletoads_dense_current_1115 as C
import replay_battletoads_dense_current_1115 as F
import battletoads_dense_current_model_1115 as Model

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
        ('PrinceCookie',535471),('PrinceCarrier',1800000),('Gimmick',201137),('score',1034694),('DK',105706)):
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
    return dict(composition=C.proposal(parent)[1],controllers=q,strict_rejections=rejects,
        inline_preimage_bytes=sum(len(bytes.fromhex(h))for _,h in C.PREIMAGES),
        portable_inverse_exact40a=True,forward_inverse_forward_exact=True,mutable_Nightly_reads_after_load=0,
        actual_owning40a_Prince_and_all_unowned_bytes_retained=True,old_factories_unchanged=True)


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
            delta=[a-b for a,b in zip(*cycles)];assert set(delta)=={78},(role,phase,delta)
            phases.append(dict(phase=phase,Main=8,parent_mean_Main=sum(cycles[0])/8,candidate_mean_Main=sum(cycles[1])/8,
                every_Main_savings=delta,actual_service_calls=dict(calls[1]),group=role,active_enemies=0))
        rows.append(dict(identity=name,compiled_Select_cycles=role,phases=phases))
        print('PROGRESS '+json.dumps(dict(identity=name,actual_mounted_idle_Right_savings=78)),flush=True)
    return dict(all_six_compiled_Select_Start=True,rows=rows,actual_mounted_code=True,
        exact_live_RAM_physical_RAM_SMC_VRAM_maps=True,opaque_only=[0x162,0x16c,0x16d],
        no_actor_health_position_terrain_or_ability_seeds=True,physical_cadence_or_FPS_claim=False)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=('strict','transport','profile','profile-short','wwf','rash','zitz'));args=ap.parse_args()
    raw=C.load_current_image();parent=C.inverse(raw)if C.digest(raw)==C.CANDIDATE else raw;image,info=C.proposal(parent)
    def deny(*a,**kw):raise AssertionError('Dense source checker attempted output/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch.object(C.Prior.Packet.Frozen.Cold.Runner.Native,'run',deny):
        q={'strict':strict,'transport':transport,'profile':profile,'profile-short':lambda p,z:profile(p,z,(4,4)),
            'wwf':wwf,'rash':lambda p,z:stage(p,z,'rash'),'zitz':lambda p,z:stage(p,z,'zitz')}[args.mode](parent,image)
    q.update(mode=args.mode,parent_SHA256=C.PIN,candidate_SHA256=C.CANDIDATE,source_only=True,outputs=0,Mesen_run=False)
    q['source_receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode())
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)


if __name__=='__main__':main()

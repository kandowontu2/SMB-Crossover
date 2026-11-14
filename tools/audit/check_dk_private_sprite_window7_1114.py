"""Granted DK three-byte source qualification, stdout and zero outputs."""
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch
from copy import deepcopy

import compose_dk_private_sprite_window7_1114 as C
import replay_dk_private_sprite_window7_1114 as Replay
import check_shared_world_sprite_images_1114 as Source
import check_current_world_sprite_windows_1114 as Resource
import check_bub_current_budget_1113 as Frames

W,N=Replay.W,Replay.N


def strict(parent):
    candidate,info=C.proposal(parent)
    assert C.inverse(candidate)==parent and C.proposal(C.inverse(candidate))[0]==candidate
    rejects=[]
    for method,inputs in((C.proposal,('parent421','dirty82','candidate')),(C.inverse,('parent82','dirty_candidate','unknown'))):
        for name in inputs:
            wrong={'parent421':C.Common.inverse(parent),'dirty82':parent[:90000]+bytes((parent[90000]^1,))+parent[90001:],
                'candidate':candidate,'parent82':parent,'dirty_candidate':candidate[:105706]+bytes((candidate[105706]^1,))+candidate[105707:],'unknown':candidate[:-1]}[name]
            try:method(wrong)
            except AssertionError:rejects.append(name)
            else:raise AssertionError(('Bad image accepted',name))
    original=Path.read_bytes;loader_cases=[]
    for label,image in(('delivered82ec',parent),('postdelivery1daca',candidate)):
        reads=[]
        def boundary(path):
            if path.resolve()==Replay.ROM.resolve():reads.append(str(path));assert len(reads)==1;return image
            return original(path)
        with patch.object(Path,'read_bytes',boundary):assert C.load_current_image()==candidate
        assert len(reads)==1;loader_cases.append(label)
    return candidate,dict(info,strict_inverse_roundtrip=True,rejections=rejects,mutable_Downloads_dependency=False,
        explicit_single_read_loader_boundary_cases=loader_cases)


def cold(raw,key='donkey_kong'):
    with patch.object(Source,'Factory',Replay):return Source.cold(raw,key)


def pose_units(parent):
    raw,info=strict(parent)
    with patch.object(Source,'Factory',Replay.Previous):old=Source.cold(parent,'donkey_kong')
    new=cold(raw);b=new.bundle
    cases=0;flags=set();windows=set();fields=('DkPose','DkRenderPage','DkSlot','DkTemp','CurrentOAMOffset')
    for pose in range(10):
        for facing in(1,2):
            for p in(0x20,0x21,0x60,0x61,0xa0,0xa1,0xe0,0xe1):
                pair=[N.fork(old),N.fork(new)]
                for m in pair:
                    N.put(m,PlayerFacingDir=facing,CurrentOAMOffset=0,GuestOamRotationActive=0)
                    N.invoke(m,'DkSetPose',a=83,x=pose,y=109,p=p)
                    N.put(m,DkShots=0);N.invoke(m,'DkDraw',a=83,x=71,y=109,p=p)
                    pointer=N.get(m,'SmPosePtr')+256*N.get(m,'SmPosePtr',1)
                    N.put(m,R0=pointer&255,R1=pointer>>8,R3=0,R4=96,R5=0,R6=100,R7=1)
                    N.invoke(m,'MetaspriteRenderLoop',a=83,x=71,y=109,p=p)
                assert bytes(pair[0][512:768])==bytes(pair[1][512:768])
                assert all(N.get(pair[0],f)==N.get(pair[1],f)for f in fields)
                assert N.get(pair[1],'CurrentCHRBank',1)==20 and pair[1][0x73e1]==0
                assert N.get(pair[1],'CurrentCHRBank',7)==55 and pair[1][0x73e7]==131
                flags.add(p);cases+=1
    barrel_cases=0
    for pose in range(6):
        for p in range(256):
            pair=[N.fork(old),N.fork(new)];returns=[]
            for m in pair:
                N.put(m,CurrentOAMOffset=0,GuestOamRotationActive=0)
                at=W.address(b,'DkShots');m[at:at+36]=bytes(36)
                m[at:at+8]=bytes((1,pose,0,0,96,0,100,1))
                returns.append(N.invoke(m,'DkDraw',a=83,x=71,y=109,p=p))
            assert tuple(returns[0][f]for f in('A','X','Y','P'))==tuple(returns[1][f]for f in('A','X','Y','P'))
            before,after=bytes(pair[0][512:520]),bytes(pair[1][512:520])
            assert all(before[i]==after[i]for i in(0,2,3,4,6,7))
            for i in(1,5):
                assert after[i]==(before[i]&63)|193 and Resource.tile_window(after[i])==7
                assert after[i]&62==before[i]&62
            windows.add(7);barrel_cases+=1
    return dict(composition=info,body_pose_facing_flags_cases=cases,barrel_pose_all256_flags_cases=barrel_cases,
        valid_barrel_leaf_return_ABI_exact=True,no_barrel_Y_difference='old1 to new7; actual caller liveness is a separate gate',
        barrel_geometry_attributes_pair_offsets_exact=True,current_world_window1_retained=True,
        candidate_window7=sorted(windows),outputs=0,Mesen_run=False)


def image_route(parent):
    raw,info=strict(parent)
    with patch.object(Source,'Factory',Replay):q=Source.run(raw,'donkey_kong')
    assert q['passed'],q
    assert all(s['actual_sprite_banks'][1:4]==[16,17,18]and s['actual_sprite_banks'][7]==823 for s in q['shots'])
    return dict(composition=info,route=q,source_world_pages_correct=True,outputs=0,Mesen_run=False)


def capture_draws(raw):
    base=N.NesMPU;captures={};kills={};menu_calls=0
    read_y={0x84,0x8c,0x94,0x98,0xc0,0xc4,0xcc,0x88,0xc8,0x11,0x31,0x51,0x71,0x91,0xb1,0xd1,0xf1,
        0xb9,0xbe,0x19,0x39,0x59,0x79,0x99,0xd9,0xf9,0x96}
    write_y={0xa0,0xa4,0xac,0xb4,0xbc,0xa8}
    class Trace(base):
        def step(self):
            nonlocal menu_calls
            m=self.memory
            if getattr(self,'watch_y',False):
                opcode=m[self.pc]
                assert opcode not in read_y,('DkDraw caller reads changed Y',hex(self.pc),hex(opcode))
                if opcode in write_y:
                    key=(self.pc,m.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1,opcode)
                    kills[key]=kills.get(key,0)+1;self.watch_y=False
            if self.pc==0xdcae and m.rawtags[2]==140:
                assert N.get(m,'SelectedCharacter')==28
                if N.get(m,'OperMode')==0:menu_calls+=1
                else:
                    at=W.address(m.bundle,'DkShots')
                    kind='barrel'if any(m[at+i]and m[at+i+1]<6 for i in(0,12,24))else'empty'
                    if kind not in captures:
                        captures[kind]=(N.fork(m),{n:getattr(self,n)for n in('pc','sp','a','x','y','p')})
            tail=self.pc==0xdd6d and m.rawtags[2]==140
            result=super().step()
            if tail:self.watch_y=True
            return result
    with patch.object(N,'NesMPU',Trace),patch.object(W.UI.F,'NesMPU',Trace):
        m=cold(raw)
        for tick in range(40):
            m.controller_pad=64 if tick<4 else 0
            Frames.frame(m,whole_pass=True)
    assert set(captures)=={'empty','barrel'} and kills
    return captures,dict(menu_DkDraw_calls=menu_calls,actual_caller_Y_definitions=[dict(PC=k[0],raw_tag=k[1],opcode=k[2],calls=v)for k,v in kills.items()],
        source_normal_B_barrel=True,post_draw_Y_reads_before_definition=0)


def interrupts(parent):
    raw,info=strict(parent);captures,callers=capture_draws(raw);base=N.NesMPU;minimum=255;rows=[]
    for name,(arena,registers)in captures.items():
        sp=registers['sp'];ret=(arena[256+((sp+1)&255)]+256*arena[256+((sp+2)&255)]+1)&65535
        boundaries=[]
        def execute(cut=None,kind=None):
            nonlocal minimum
            m=N.fork(arena);cpu=base(memory=m,pc=registers['pc'])
            for key,value in registers.items():setattr(cpu,key,value)
            index=0;injected=False;check={}
            for _ in range(20000):
                if(cpu.pc,cpu.sp)==(ret,(sp+2)&255):break
                minimum=min(minimum,cpu.sp)
                tag=m.rawtags[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1
                owned=tag==140 and cpu.pc in(0xdcd9,0xdcdb,0xdd1b,0xdd1d,0xdd23,0xdd25)
                setter=tag==190 and 0xa275<=cpu.pc<0xa289 and cpu.y==7
                if owned or setter:
                    if cut is None:boundaries.append((index,cpu.pc,tag))
                    if cut==index:
                        regs=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                        before=dict(private=tuple(map(bytes,m.ram)),maps=m.rawtags[:],smc=bytes(m[0x15a:0x17b]),
                            modes=bytes(m[0x73e0:0x73ef]),latches=m.chr_latches[:],upper=m.upper,
                            skipped=N.get(m,'NmiSkipped'),NmiDisable=N.get(m,'NmiDisable'))
                        assert before['NmiDisable']&128,'Actual Main caller is busy, not an invented regular arm'
                        if kind=='IRQ'and cpu.p&4:check={'masked_by_actual_I':True}
                        else:
                            cpu.irq()if kind=='IRQ'else cpu.nmi()
                            for _ in range(200000):
                                minimum=min(minimum,cpu.sp)
                                if(cpu.pc,cpu.sp)==regs[:2]:break
                                assert m[cpu.pc],('ISR BRK',kind,hex(cpu.pc));base.step(cpu)
                            else:raise AssertionError('ISR return bound')
                            actual=tuple(getattr(cpu,n)for n in('pc','sp','a','x','y','p'))
                            assert actual[:5]==regs[:5]and actual[5]&0xef==regs[5]&0xef
                            assert tuple(map(bytes,m.ram))==before['private']and m.rawtags==before['maps']
                            assert bytes(m[0x15a:0x17b])==before['smc']and bytes(m[0x73e0:0x73ef])==before['modes']
                            assert m.chr_latches==before['latches']and m.upper==before['upper']
                            assert N.get(m,'NmiDisable')==before['NmiDisable']
                            assert(N.get(m,'NmiSkipped')-before['skipped'])&255==(kind=='NMI')
                            check={'actual_NmiDisable':before['NmiDisable'],'registers_private_maps_SMC_modes_CHR_and_upper_exact':True}
                        injected=True
                    index+=1
                assert m[cpu.pc],('Draw continuation BRK',hex(cpu.pc));base.step(cpu)
            else:raise AssertionError('Captured actual draw return bound')
            assert cut is None or injected
            return m,tuple(getattr(cpu,n)for n in('a','x','y','p','sp')),check
        baseline,regs,_=execute();counts={'IRQ':0,'NMI':0}
        for index,pc,tag in boundaries:
            for kind in('IRQ','NMI'):
                m,returned,check=execute(index,kind)
                assert returned[:3]==regs[:3]and returned[3]&0xef==regs[3]&0xef and returned[4]==regs[4]
                assert bytes(m[512:768])==bytes(baseline[512:768])
                assert bytes(m[0x73e0:0x73ef])==bytes(baseline[0x73e0:0x73ef])
                counts[kind]+=1
        rows.append(dict(context=name,actual_entry=registers,actual_return_PC=ret,actual_return_SP=(sp+2)&255,
            instruction_boundaries=len(boundaries),PCs=sorted({pc for _,pc,_ in boundaries}),cuts=counts))
    return dict(composition=info,actual_callers=callers,actual_instruction_cut_contexts=rows,minimum_SP=minimum,
        regular_NMI_inside_busy_unreachable=True,regular_post_update_NMI='Naturally exercised by source image route and ordinary frame scheduler',
        outputs=0,Mesen_run=False)


def death_restart(parent):
    raw,info=strict(parent);m=cold(raw);phase='approach';age=0;death=None;restart=None;first_life=2;portrait=[]
    base=N.NesMPU;portrait_pc=W.address(m.bundle,'DkPortrait');portrait_tag=((W.location(m.bundle,'DkPortrait')-16)//8192)|128
    class Trace(base):
        def step(self):
            mm=self.memory
            if self.pc==portrait_pc and mm.rawtags[(self.pc-0x8000)//8192]==portrait_tag:
                if len(portrait)<12:portrait.append(dict(engine=N.get(mm,'GameEngineSubroutine'),task=N.get(mm,'OperMode_Task'),lives=N.get(mm,'NumberofLives')))
            return super().step()
    with patch.object(N,'NesMPU',Trace):
        for tick in range(1600):
            x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
            engine=N.get(m,'GameEngineSubroutine');life=N.get(m,'NumberofLives')
            if phase=='approach'and x>=220:phase='throw-left';age=0
            if phase=='throw-left'and age>=24:phase='fatal-right';age=0
            if phase in('approach','fatal-right'):m.controller_pad=1
            elif phase=='throw-left':m.controller_pad=66 if age<4 else 2
            else:m.controller_pad=0
            if engine==11 and death is None:
                death=dict(Main=tick,x=x,Y=N.get(m,'Player_Y_Position'),lives=life,
                    shots=list(m[W.address(m.bundle,'DkShots'):W.address(m.bundle,'DkShots')+36]))
                phase='restart';m.controller_pad=0
            Frames.frame(m,whole_pass=True);age+=1
            if life<first_life and tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):
                restart=dict(Main=tick+1,x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),Y=N.get(m,'Player_Y_Position'),
                    lives=N.get(m,'NumberofLives'),ready=N.get(m,'DkReady'),power=N.get(m,'PlayerStatus'),star=N.get(m,'StarInvincibleTimer'))
                break
        else:raise AssertionError(('Natural death/restart bound',phase,x,engine,life))
    assert death and restart and restart['lives']==1 and restart['power']==restart['star']==0
    assert N.get(m,'DkReady')==68 and all(N.get(m,'DkShots',i)==0 for i in range(36))
    for _ in range(25):m.controller_pad=0;Frames.frame(m,whole_pass=True)
    assert N.get(m,'Player_State')==0 and N.get(m,'NumberofLives')==1
    assert m.chr_latches[1:4]==[16,17,18]and m.chr_latches[7]==823
    return dict(composition=info,natural_death=death,natural_restart=restart,actual_lives_portrait_calls=portrait,
        shots_cleared=True,post_restart_grounded_updates=25,actual_published_banks=m.chr_latches,
        gameplay_seeds=0,outputs=0,Mesen_run=False)


def foreign_menu(parent):
    raw,info=strict(parent);seed=cold(raw);b=seed.bundle;cases=0
    for owner in range(256):
        if owner==28:continue
        for flags in(0x20,0xe1):
            m=N.fork(seed);N.put(m,SelectedCharacter=owner)
            before=(bytes(m[0x5c00:0x5c80]),bytes(m[512:768]),bytes(m[0x73e0:0x73ef]))
            result=N.invoke(m,'DkDraw',a=83,x=71,y=109,p=flags)
            assert(result['A'],result['X'],result['Y'])==(83,71,109)
            assert before==(bytes(m[0x5c00:0x5c80]),bytes(m[512:768]),bytes(m[0x73e0:0x73ef]))
            cases+=1
    rows=[]
    for target,slot,cycle in((0,0,0),(9,9,1),(18,17,1)):
        with patch.object(N,'Bus',W.ControllerBus):m=W.UI.seed(b,0)
        for bits in Replay.bindings(raw)['navigation']:W.UI.key(m,bits)
        assert N.get(m,'SelectedCharacter')==28
        # A declared resource fixture carries an admitted old DK lease into
        # the real menu transition. All navigation/owner publication is real.
        N.invoke(m,'X5SetPhysicalChr',a=55,x=3,y=7)
        while N.get(m,'CrossoverMenuIndex')//8>slot//8:W.UI.key(m,8)
        while N.get(m,'CrossoverMenuIndex')%8>slot%8:W.UI.key(m,2)
        while N.get(m,'CrossoverMenuIndex')%8<slot%8:W.UI.key(m,1)
        for _ in range(cycle):W.UI.key(m,32)
        assert N.get(m,'SelectedCharacter')==target,(target,N.get(m,'CrossoverMenuIndex'),N.get(m,'SelectedCharacter'),W.UI.menu_name(m)[0])
        N.invoke(m,'X5PublishChr',a=0,x=0,y=0)
        row=dict(target=target,actual_name=W.UI.menu_name(m)[0],menu= N.get(m,'CrossoverMenuState'),
            modes=list(m[0x73e0:0x73ec]),actual_banks=m.chr_latches[:8])
        if target in(9,18):assert m.chr_latches[7]!=823 and m[0x73e7]&128
        else:assert m[0x73e7]==0
        rows.append(row)
    return dict(composition=info,defensive_foreign_owner_flags_cases=cases,
        defensive_units_not_gameplay=True,real_UI_retirement_with_old_lease_fixture=rows,
        unconditional_foreign_publishers_called=False,outputs=0,Mesen_run=False)


def parent_parity(parent):
    raw,info=strict(parent)
    class Reference:
        ROM=Replay.ROM
        class Frozen:
            LuaRuntime=Replay.Frozen.LuaRuntime
            normalize=staticmethod(Replay.Previous.Frozen.normalize)
        @staticmethod
        def bindings(image,key):
            assert image==parent and key=='donkey_kong'
            c=deepcopy(Replay.bindings(raw,key));c['sha']=C.PIN
            return c
        @staticmethod
        def controller(image,key):
            c=Reference.bindings(image,key);text=Replay.controller(raw,key)
            prefix='local C='+Replay.Previous.Previous.Frozen.lua(Replay.bindings(raw,key))+'\n'
            assert text.startswith(prefix)
            text='local C='+Replay.Previous.Previous.Frozen.lua(c)+'\n'+text[len(prefix):]
            old='(tile&1)*4+(tile>>6)==7';new='(tile&1)*4+(tile>>6)==1 and (tile&62)<48'
            assert text.count(old)==1;text=text.replace(old,new,1)
            assert text.count('spriteBanks[7]==823')==1;text=text.replace('spriteBanks[7]==823','spriteBanks[1]==823',1)
            return text
        @staticmethod
        def metadata(image,key):
            return dict(ROM_SHA256=C.PIN,controller_SHA256=sha256(Reference.controller(image,key).encode()).hexdigest(),reference_only=True)
    fields=('Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State',
        'Player_X_Speed','Player_Y_Speed','GameEngineSubroutine','OperMode','OperMode_Task','NumberofLives','PlayerStatus',
        'DkAttack','DkAge','DkTier','DkReady','TimerControl','A_B_Buttons','PreviousA_B_Buttons')
    def view(m):return tuple(N.get(m,n)for n in fields)+tuple(N.get(m,'DkShots',i)for i in range(36))
    # Genuine cold and a normal leftward throw followed by fatal contact.
    with patch.object(Source,'Factory',Replay.Previous):old=Source.cold(parent,'donkey_kong')
    new=cold(raw);pair=[old,new];phase='approach';age=0;death=None;retired=[]
    for tick in range(600):
        x=N.get(new,'Player_X_Position')+256*N.get(new,'Player_PageLoc')
        if phase=='approach'and x>=220:phase='throw-left';age=0
        if phase=='throw-left'and age>=24:phase='fatal-right';age=0
        if N.get(new,'GameEngineSubroutine')==11:
            death=death or dict(Main=tick,x=x,y=N.get(new,'Player_Y_Position'),lives=N.get(new,'NumberofLives'))
            phase='death'
        pad=1 if phase in('approach','fatal-right')else 66 if phase=='throw-left'and age<4 else 2 if phase=='throw-left'else 0
        for m in pair:m.controller_pad=pad;Frames.frame(m,whole_pass=True)
        assert view(old)==view(new),('Death source parity',tick,view(old),view(new))
        if death:assert all(N.get(new,'DkShots',i)==0 for i in range(36))
        age+=1
    assert death and N.get(new,'GameEngineSubroutine')==11
    death_terminal=dict(Main=600,x=x,y=N.get(new,'Player_Y_Position'),engine=11,lives=N.get(new,'NumberofLives'))
    # Independently replay both genuine three-spot openings. The reference
    # adapter only observes old barrel window1; candidate factory is frozen.
    held=[];original=Source.cold;receipts=[]
    def retain(image,key):
        m=original(image,key);held.append(m);return m
    for image,factory in((parent,Reference),(raw,Replay)):
        with patch.object(Source,'Factory',factory),patch.object(Source,'cold',retain):q=Source.run(image,'donkey_kong')
        assert q['passed'];receipts.append(q['source_receipt_SHA256'])
    old,new=held;assert view(old)==view(new)
    phase='approach';age=0
    for tick in range(250):
        x=N.get(new,'Player_X_Position')+256*N.get(new,'Player_PageLoc');ground=N.get(new,'Player_State')==0
        if phase=='approach'and x>=396 and ground:phase='jump';age=0
        pad=1|(128 if phase=='jump'and age<38 else 0)
        for m in(old,new):m.controller_pad=pad;Frames.frame(m,whole_pass=True)
        assert view(old)==view(new),('Pipe source parity',tick,view(old),view(new))
        age+=1
    assert x==417 and N.get(new,'Player_Y_Position')==176 and N.get(new,'NumberofLives')==2
    # Existing transition primitives are also exact; these explicit finite
    # component calls must not be presented as a natural pipe/restart success.
    transitions=[]
    for name in('DkEnterScene','DkConstruct','DkHostDeathStart','DkPortrait','FmNativePrepare'):
        outcomes=[]
        for m in(old,new):
            outcome=N.invoke(m,name,a=83,x=9,y=109,p=0x61)
            outcomes.append(tuple(outcome[n]for n in('A','X','Y','P')))
        assert outcomes[0]==outcomes[1]and view(old)==view(new)
        transitions.append(dict(entry=name,registers_equal=True,gameplay_state_equal=True))
    assert bytes(new[0x73e0:0x73ec])==bytes(12)
    return dict(composition=info,parent_candidate_death_parity_Main=600,natural_death=death,death_terminal=death_terminal,
        restart_success_claimed=False,parent_candidate_first_pipe_parity_Main=250,
        pipe_terminal=dict(x=x,y=176,engine=8,lives=2),pipe_success_claimed=False,
        opening_receipts=receipts,transition_component_units=transitions,private_lease_retired_by_existing_prepare=True,
        scope='Identical preexisting source-probe limitations, preserved as separate stage/death work; no graphics regression',
        gameplay_seeds=0,component_fixtures_explicit=True,outputs=0,Mesen_run=False)


def area_route(parent):
    raw,info=strict(parent);held=[];original=Source.cold
    def retain(image,key):
        m=original(image,key);held.append(m);return m
    with patch.object(Source,'Factory',Replay),patch.object(Source,'cold',retain):q=Source.run(raw,'donkey_kong')
    assert q['passed']and len(held)==1;m=held[0]
    pipes=[(396,480),(556,640),(684,768),(844,928)];index=0;phase='approach';age=0;rows=[];underground=0
    for tick in range(1400):
        x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc');y=N.get(m,'Player_Y_Position');ground=N.get(m,'Player_State')==0
        assert N.get(m,'NumberofLives')==2 and N.get(m,'GameEngineSubroutine')!=11,('Pipe route life',tick,x,y,phase)
        if N.get(m,'AreaType')==2:
            m.controller_pad=0
            if N.get(m,'GameEngineSubroutine')==8 and ground:underground+=1
            if underground>=25:break
        elif index<4:
            start,right=pipes[index]
            if phase=='approach'and x>=start and ground:phase='jump';age=0;rows.append(dict(pipe=index+1,Main=tick,x=x,y=y))
            if index==3 and ground and 892<=x<=920 and y<=114:phase='enter'
            if phase=='enter':m.controller_pad=4
            elif phase=='jump':
                m.controller_pad=1|(128 if age<38 else 0)
                if age>8 and ground and x>right+8:index+=1;phase='approach';age=0
            else:m.controller_pad=1
        else:m.controller_pad=0
        Frames.frame(m,whole_pass=True);age+=1
        if tick%250==249:print(json.dumps(dict(pipe_progress=tick+1,index=index,phase=phase,x=x,y=y)),flush=True)
    assert underground==25,('Natural pipe route bound',index,phase,x,y,rows)
    assert N.get(m,'WorldNumber')==N.get(m,'LevelNumber')==0
    assert m.chr_latches[1:4]==[16,17,18]and m.chr_latches[7]==823
    return dict(composition=info,ordinary_opening_receipt=q['source_receipt_SHA256'],natural_pipe_waypoints=rows,
        same_level_pipe_area2_grounded_updates=25,extra_Main=tick+1,terminal=dict(x=x,y=y,lives=N.get(m,'NumberofLives'),area=2),
        actual_published_banks=m.chr_latches,gameplay_seeds=0,outputs=0,Mesen_run=False)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--poses',action='store_true');p.add_argument('--images',action='store_true');p.add_argument('--interrupts',action='store_true');p.add_argument('--death-restart',action='store_true');p.add_argument('--area',action='store_true');p.add_argument('--foreign-menu',action='store_true');p.add_argument('--parent-parity',action='store_true');a=p.parse_args()
    raw=C.load_current_image();parent=C.inverse(raw)
    def forbid(*args,**kwargs):raise RuntimeError('Memory-only DK qualification attempted file/Mesen')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid),patch.object(Source.Native,'run',forbid):
        q=parent_parity(parent)if a.parent_parity else foreign_menu(parent)if a.foreign_menu else area_route(parent)if a.area else death_restart(parent)if a.death_restart else interrupts(parent)if a.interrupts else pose_units(parent)if a.poses else image_route(parent)if a.images else strict(parent)[1]
    q['file_and_Mesen_traps']=True;print(json.dumps(q,separators=(',',':')),flush=True)

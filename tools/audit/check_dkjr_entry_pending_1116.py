"""Real native parsed1-2 entry component; no position/floor/health outcome seed."""
from collections import Counter
from hashlib import sha256
import json

import compose_dkjr_forced_entry_current_1116 as C
import check_dkjr_carry_camera_route_1116 as Route
import check_dkjr_footer_ryu_1116 as Common

N,Q=Route.N,Common.Q
H=lambda value:sha256(value).hexdigest()


def run():
    raw,composition=C.current_proposal(C.BT.ROM.read_bytes())
    _,m=Route.cold(raw);_,labels=C.Camera.Plan.source_inputs()
    # Declared real room-parser input, not a controller-earned stage clear.
    # All actor positions, floor data, gravity and health are produced by code.
    N.put(m,WorldNumber=0,LevelNumber=1,AreaNumber=2)
    N.invoke(m,'LoadAreaPointer');N.invoke(m,'ChgAreaMode')
    packet=C.Camera.payload(raw);section=packet[0xbc74-0xa000:0xbd45-0xa000]
    offsets=[i for i in range(len(section)-2)if section[i:i+3]==bytes.fromhex('990002')]
    assert len(offsets)==1
    body_store=0xbc74+offsets[0]
    counts=Counter();events={};last_ready=None;wrapper=None;work=None;tick=0;previous=None
    phase,move,clock=(labels[name]for name in('DkjrNativeSourcePhase','DkjrMove','DkjrClock'))
    gravity_pc=N.address(m.bundle,'ImposeGravitySprObj')
    gravity_file=N.location(m.bundle,'ImposeGravitySprObj')
    gravity_tag=((gravity_file-16)//8192)|128
    assert gravity_pc==0x8bf8
    def state(memory,c=None):
        r=memory.ram[2];row=dict(Route.B.state(memory),tick=tick,ready=r[0x8fe],phase=r[0x6b],prior=r[0x6c],
            origin=r[0x76],limit=r[0x7b],area=N.get(memory,'AreaPointer'),area_type=N.get(memory,'AreaType'),
            entrance=N.get(memory,'PlayerEntranceCtrl'),native_VY=N.get(memory,'Player_Y_Speed'))
        if c is not None:row.update(PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,previous=previous)
        return row
    def token(memory,c):
        return ((memory[0x100+((c.sp+1)&255)]+256*memory[0x100+((c.sp+2)&255)]+1)&65535,(c.sp+2)&255)
    def healthy(memory):
        r=memory.ram[2]
        return N.get(memory,'GameEngineSubroutine')==8 and N.get(memory,'NumberofLives')==2 and\
            N.get(memory,'Player_X_Position')==40 and N.get(memory,'Player_PageLoc')==0 and\
            N.get(memory,'Player_Y_Position')==176 and N.get(memory,'Player_Y_HighPos')==1 and\
            N.get(memory,'Player_State')==0 and r[0x8fe]==2 and r[0x6b]==r[0x6c]==1 and r[0x210]==191
    def watch(memory,c):
        nonlocal last_ready,wrapper,work,previous
        r=memory.ram[2];tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        engine=N.get(memory,'GameEngineSubroutine')
        if engine==8 and r[0x8fe]==1 and N.get(memory,'Player_State')==2:
            events.setdefault('first-pending',state(memory,c))
        if r[0x8fe]==2 and last_ready==1 and 'first-pending'in events:
            events.setdefault('actual-ready2-admission',state(memory,c))
        last_ready=r[0x8fe]
        if(tag,c.pc)==(2,0xd65e):
            assert wrapper is None;wrapper=token(memory,c)
            counts['D65E_wrapper_entries']+=1
            if r[0x8fe]==1:counts['pending_wrapper_entries']+=1
        if wrapper==(c.pc,c.sp):counts['D65E_wrapper_returns']+=1;wrapper=None
        if(tag,c.pc)==(3,phase):
            assert r[0x8fe]==2,'Original donor work entered before native admission'
            assert work is None;work=dict(token=token(memory,c),move=False,clock=False)
            counts['original_SourcePhase_entries']+=1
        if work and(tag,c.pc)==(3,move):work['move']=True;counts['actual_original_Move_calls']+=1
        if work and(tag,c.pc)==(3,clock):work['clock']=True;counts['actual_original_Clock_calls']+=1
        if work and work['token']==(c.pc,c.sp):
            counts['original_SourcePhase_returns']+=1
            complete=work['move']and work['clock']and healthy(memory)
            counts['grounded_original_returns']=counts['grounded_original_returns']+1 if complete else 0
            work=None
        if r[0x8fe]==1 and engine==8:
            for key,where in(('actual_native_vertical_AB48',(129,0xab48)),('actual_native_BmVertical',(190,0xbaf9)),
                              ('actual_native_gravity_leaf',(190,0xba75)),('actual_native_ImposeGravity',(gravity_tag,gravity_pc))):
                if(tag,c.pc)==where:counts[key]+=1
            if(tag,c.pc)==(3,body_store):
                assert c.a==r[0x210+c.x]==(N.get(memory,'Player_Y_Position')+15)&255
                assert r[0x213]==((N.get(memory,'Player_X_Position')-N.get(memory,'ScreenLeft_X_Pos')-8)&255)
                counts['pending_native_OAM_Y_stores']+=1
                key='visible-after-native-ground'if N.get(memory,'Player_State')==0 else'visible-during-native-fall'
                events.setdefault(key,state(memory,c))
            if memory[c.pc]==0x85 and memory[(c.pc+1)&65535]==0x1e and c.a==0 and N.get(memory,'Player_State')==2:
                assert tag&128,'Pending ground must be native-owned'
                events.setdefault('first-native-ground-writer',state(memory,c))
        previous=dict(PC=c.pc,tag=tag,A=c.a,SP=c.sp,bytes=bytes(memory[(c.pc+i)&65535]for i in range(3)).hex())
    for tick in range(1,1201):
        Q.frame(m,0,watch)
        if counts['grounded_original_returns']>=25 and wrapper is None and work is None and healthy(m):break
    assert tick<1200,dict(reason='Native parser/pending component bounded',counts=counts,events=events,terminal=state(m))
    assert counts['pending_wrapper_entries']>0 and all(counts[key]>0 for key in
        ('actual_native_vertical_AB48','actual_native_BmVertical','actual_native_gravity_leaf','actual_native_ImposeGravity','pending_native_OAM_Y_stores')),dict(counts=dict(counts),events=events,terminal=state(m))
    assert all(key in events for key in('first-pending','first-native-ground-writer','visible-during-native-fall',
        'visible-after-native-ground','actual-ready2-admission'))
    assert events['first-pending']['ready']==1 and events['first-pending']['phase']==1
    assert events['actual-ready2-admission']['y']==176 and events['actual-ready2-admission']['source_y']==191
    assert m.ram[2][0x7b]==22 and m.ram[2][0x76]==0
    return dict(passed=True,candidate_SHA256=H(raw),source_component_only=True,real_LoadAreaPointer_and_ChgAreaMode=True,
        declared_inputs=dict(WorldNumber=0,LevelNumber=1,AreaNumber=2),
        no_position_floor_actor_health_outcome_seeds=True,updates=tick,counts=dict(counts),events=events,
        terminal=state(m),original_fall_limit22_and_origin_zero_unchanged=True,
        actual_gravity_binding=dict(PC=gravity_pc,tag=gravity_tag,file=gravity_file,preimage16=raw[gravity_file:gravity_file+16].hex()),outputs=0,
        scope='Declared parser-driven real native1-2 entry, actual gravity/BG/OAM and25 grounded original Move+Clock returns; not an ordinary1-1 route or native emulator claim.')


if __name__=='__main__':
    report=run();text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_PENDING '+text,flush=True)
    print('DKJR_ENTRY_PENDING_SHA256 '+H(text.encode()),flush=True)

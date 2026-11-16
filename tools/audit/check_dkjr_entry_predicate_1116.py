"""Actual new-entry classifier and unchanged-anchor ABI; no route fixtures."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json

import check_dkjr_entry_components_1116 as K

C,N=K.C,K.N
H=lambda value:sha256(value).hexdigest()


def prepared(seed,**fields):
    m=K.fork(seed)
    N.put(m,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,PlayerEntranceCtrl=1,
        Player_State=2,Player_Y_Speed=0,Player_Y_HighPos=1,Player_Y_Position=48,
        TimerControl=0,DisableCollisionDet=0,JumpspringAnimCtrl=0,SwimmingFlag=0)
    r=m.ram[2];r[0x8fe]=1;r[0x4a]=1;r[0x68]=0
    for name,value in fields.items():
        if name=='profile':r[0x4a]=value
        elif name=='hurt':r[0x68]=value
        elif name=='ready':r[0x8fe]=value
        else:N.put(m,**{name:value})
    return m


def run():
    parent,raw,composition,fit,labels,sites,allowed,seeds,openings=K.setup()
    forced=next(member['PC']for row in fit['fragments']for member in row['members']if member['name']=='FORCED_VY_QUALIFIED')
    tests=[dict(Player_State=state,Player_Y_Speed=vy)for state,vy in product(range(256),(0,255))]
    tests += [dict(Player_Y_Speed=vy)for vy in range(256)]
    rejected=[('OperMode',0),('OperMode',2),('OperMode_Task',2),('OperMode_Task',4),
        ('profile',0),('profile',2),('GameEngineSubroutine',7),('GameEngineSubroutine',9),
        ('GameEngineSubroutine',11),('DisableCollisionDet',1),('JumpspringAnimCtrl',1),
        ('SwimmingFlag',1),('hurt',1),('Player_Y_HighPos',0),('Player_Y_HighPos',2),
        ('PlayerEntranceCtrl',0),('PlayerEntranceCtrl',2),('PlayerEntranceCtrl',7)]
    tests += [dict([item])for item in rejected]
    count=0;minimum=255;digest=sha256();admitted=Counter()
    for fields,p in product(tests,(0x20,0x61,0x69,0xff)):
        m=prepared(seeds[1],**fields);before=K.snapshot(m,N.NesMPU(memory=m));code=bytes(m.ram[3])
        c,depth=K.execute(m,forced,0x5b00,p=p,whole=True,x=37,y=91)
        minimum=min(minimum,depth)
        expected=not any(fields.get(name,default)!=default for name,default in
            (('OperMode',1),('OperMode_Task',3),('profile',1),('GameEngineSubroutine',8),
             ('DisableCollisionDet',0),('JumpspringAnimCtrl',0),('SwimmingFlag',0),('hurt',0),
             ('Player_Y_HighPos',1),('PlayerEntranceCtrl',1)))and fields.get('Player_State',2)==2 and fields.get('Player_Y_Speed',0)<128
        assert bool(c.p&1)==expected,(fields,p,c.p)
        assert(c.x,c.y,c.sp)==(37,91,224)and c.p&0x4c==p&0x4c
        after=K.snapshot(m,c)
        assert before[1:]==after[1:]and bytes(m.ram[3])==code,'Classifier wrote observable state'
        # Only C is consumed by the real BCC; both successors overwrite A/N/Z.
        admitted[expected]+=1;digest.update(bytes((c.a,c.x,c.y,c.p,c.sp)));count+=1
    anchor_cases=[dict(ready=ready)for ready in(0,2,3,255)]
    anchor_cases += [dict([item])for item in rejected]
    anchor_cases += [dict(Player_Y_Speed=vy)for vy in(128,255)]
    abi=0
    for fields,p in product(anchor_cases,range(256)):
        outputs=[]
        for seed in seeds:
            m=prepared(seed,**fields)
            c,depth=K.execute(m,0xbfc1,0x5b00,p=p,whole=True,x=37,y=91)
            minimum=min(minimum,depth);outputs.append(K.snapshot(m,c))
        assert outputs[0]==outputs[1],('Unchanged actual anchor ABI',fields,p,outputs[0][0],outputs[1][0])
        abi+=1
    paused=[]
    phase=labels['DkjrNativeSourcePhase']
    for timer,vy in product((0,1,254,255),(0,2)):
        m=prepared(seeds[1],TimerControl=timer,Player_Y_Speed=vy);calls=Counter()
        before_y=N.get(m,'Player_Y_Position');before_clock=m.ram[2][0x49]
        def watch(memory,c):
            tag=memory.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            if(tag,c.pc)==(129,0xab48):calls['native_vertical']+=1
            if(tag,c.pc)==(3,phase):calls['original_donor_work']+=1
        c,depth=K.execute(m,0xd65e,0x5b00,p=0x69,whole=True,watch=watch)
        assert not calls['original_donor_work']and calls['native_vertical']==int(timer==0)
        assert m.ram[2][0x8fe]==1 and m.ram[2][0x49]==before_clock
        assert m.ram[2][0x6b]==1 and m.ram[2][0x76]==0 and m.ram[2][0x7b]==22 and not c.p&1
        assert m.ram[2][0x210]==N.get(m,'Player_Y_Position')+15
        if timer:assert N.get(m,'Player_Y_Position')==before_y
        paused.append(dict(timer=timer,VY=vy,actual_native_vertical=calls['native_vertical'],
            actual_original_work=calls['original_donor_work'],returned_C=bool(c.p&1),source_ready=1,
            native_Y=N.get(m,'Player_Y_Position'),projected_source_Y=m.ram[2][0x210]))
    return dict(passed=True,candidate_SHA256=H(raw),classifier_cases=count,admitted_by_C=dict(admitted),
        all256_native_states_and_VY_factored=True,complete256P_unchanged_anchor_cases=abi,
        complete_AXYP_SP_data_maps_SMC33_live_stack_equal_on_unchanged_cases=True,
        classifier_C_VID_XY_SP_readonly_contract=True,classifier_caller_C_only_then_A_NZ_overwritten=True,
        zero_original_work_below_guard_pending=paused,minimum_SP=minimum,aggregate_SHA256=digest.hexdigest(),
        declared_components_only=True,outputs=0)


if __name__=='__main__':
    report=run();text=json.dumps(report,sort_keys=True,separators=(',',':'))
    print('DKJR_ENTRY_PREDICATE '+text,flush=True)
    print('DKJR_ENTRY_PREDICATE_SHA256 '+H(text.encode()),flush=True)

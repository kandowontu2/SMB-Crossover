"""Actual compiled36 common callers, foreign cold owners and cycle accounting."""
from collections import Counter
from pathlib import Path
from unittest.mock import patch
import json
import current_mini_weapon_owner_1116 as Current

C,N,W,Frames=Current.Compose,Current.N,Current.W,Current.Frames

def public(m,slot,a=85,x=7,y=91,p=0x31):
    raw=m.bundle['raw'];pc=0xb600+16*slot;at=16+79*8192+(pc&8191)
    assert raw[at:at+11]==bytes.fromhex('8d6a01089848a0')+bytes((slot,))+bytes.fromhex('4c40b8')
    N.put(m,**{})
    m[W.address(m.bundle,'SafecallA_SMC')+1]=a;m[W.address(m.bundle,'FarcallJmpTarget_SMC')+1]=pc&255;m[W.address(m.bundle,'FarcallJmpTarget_SMC')+2]=pc>>8
    c=N.NesMPU(memory=m,pc=W.address(m.bundle,'FarCallCommon'));c.a=207;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    low=c.sp;hits=Counter();samples=[];foreign_pc=0xb53c if C.H(raw)==C.CANDIDATE else 0xb53d
    for _ in range(500000):
        if c.pc==0x5b00:break
        low=min(low,c.sp)
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        role=None
        if tag==207 and c.pc==foreign_pc:role='Foreign'
        elif tag==207 and c.pc==0xb53a:role='Roll_exit';assert c.p&128
        elif tag==217 and c.pc==0xbcc0:role='Mini_native_weapon'if N.get(m,'SelectedCharacter')==41 else'Unexpected_foreign_Mini_native_weapon'
        elif tag==3 and c.pc==0xa066:role='Mini_weapon_vector'if N.get(m,'SelectedCharacter')==41 else'Foreign_source_weapon_vector'
        elif tag==3 and c.pc==0xa3e5 and N.get(m,'SelectedCharacter')==41:role='MiniStep'
        if role:
            hits[role]+=1
            if len(samples)<12:samples.append(dict(role=role,PC=c.pc,SP=c.sp,A=c.a,X=c.x,Y=c.y,P=c.p,tag=tag))
        assert m[c.pc],('Actual public BRK',slot,c.pc,tag);c.step()
    else:raise AssertionError(('Actual full public bound',slot,c.pc))
    assert c.sp==224
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,CPU=c.processorCycles,minimum_SP=low,hits=dict(hits),samples=samples)

def parent_clone(seed,parent):
    m=N.fork(seed);m.bundle=dict(m.bundle,raw=parent)
    for i,tag in enumerate(m.rawtags):
        if tag&128:m.raw_page(i,tag)
    return m

def state(m):return(bytes(m[:0x800]),bytes(m[0x5c00:0x8000]),tuple(bytes(v)for v in m.ram),tuple(m.rawtags),tuple(m.chr_latches))

def cold_owner(raw,owner,roll=False):
    b=dict(W.Symbols.bundle(),raw=raw);found=None
    with patch.object(N,'Bus',W.ControllerBus):
        for index in range(32):
            m=W.UI.seed(b,index);first=W.UI.menu_name(m)[0]
            for variant in range(10):
                if N.get(m,'SelectedCharacter')==owner and(not roll or W.UI.menu_name(m)[0]=='ROLL'and N.get(m,'RlVariant')==1):found=(m,index,variant);break
                W.UI.key(m,32)
                if W.UI.menu_name(m)[0]==first:break
            if found:break
    assert found,('Actual compiled owner absent',owner)
    m,index,variant=found;label=W.UI.menu_name(m)[0];start=W.UI.key(m,16)
    N.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P']);N.invoke(m,'PauseRoutine',a=0)
    for tick in range(700):
        if tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
        m.controller_pad=0;Frames.frame(m,cold=True)
    else:raise AssertionError(('Foreign compiled constructor bound',owner))
    assert N.get(m,'SelectedCharacter')==owner
    return m,dict(owner=owner,name=label,RlVariant=N.get(m,'RlVariant'),compiled_menu_index=index,Select=variant,parser_passes=tick+1,menu_index_fixture=True,no_gameplay_state_seed=True)

def run(parent):
    raw,_=C.proposal(parent);seed,cold=Current.cold(raw,True);rows=[];cases=0
    for slot in range(36):
        for flags in(0x30,0x31,0x70,0xf1):
            a=parent_clone(seed,parent);b=N.fork(seed)
            for m in(a,b):N.put(m,FrameCounter=(N.get(m,'FrameCounter')+1)&255)
            beforeA=bytes(a[0x1e1:0x200]);beforeB=bytes(b[0x1e1:0x200]);left=public(a,slot,p=flags);right=public(b,slot,p=flags)
            for field in('A','X','Y','P','SP','minimum_SP'):assert left[field]==right[field],(slot,flags,field,left,right)
            assert state(a)==state(b),(slot,flags,'Whole native/private/SMC/maps differ')
            assert bytes(a[0x1e1:0x200])==beforeA and bytes(b[0x1e1:0x200])==beforeB
            delta=right['CPU']-left['CPU'];count=right['hits'].get('Foreign',0);assert delta==4*count,(slot,delta,left,right)
            cases+=1
            if flags==0x31:rows.append(dict(slot=slot,parent_cycles=left['CPU'],candidate_cycles=right['CPU'],Foreign=count,extra_cycles=delta))
    foreign=[]
    for owner in(34,9):
        m,opening=cold_owner(raw,owner,roll=owner==9)
        for mode,pad in(('idle',0),('weapon',64)):
            a=parent_clone(m,parent);b=N.fork(m)
            for t in(a,b):
                N.put(t,SavedJoypadBits=pad,SavedJoypad1Bits=pad,A_B_Buttons=pad,PreviousA_B_Buttons=0,FrameCounter=(N.get(t,'FrameCounter')+1)&255)
                # Actual movement computes this owner's fresh input before tail.
                public(t,0)
            left=public(a,34);right=public(b,34)
            for field in('A','X','Y','P','SP','minimum_SP'):assert left[field]==right[field],(owner,mode,field,left,right)
            assert state(a)==state(b),(owner,mode,'Foreign full state differs')
            delta=right['CPU']-left['CPU'];count=right['hits'].get('Foreign',0);assert delta==4*count,(owner,mode,delta,left,right)
            if owner==9:assert right['hits'].get('Roll_exit',0)>0
            assert not right['hits'].get('Unexpected_foreign_Mini_native_weapon',0)
            foreign.append(dict(owner=owner,mode=mode,opening=opening,parent=left,candidate=right,extra_cycles=delta))
    q=dict(passed=True,ROM_SHA256=C.CANDIDATE,compiled_Mini_cold=cold,all36_compiled_wrapper_cases=cases,Mini_cases=rows,foreign=foreign,
        AXYP_stack_native_private_SMC_maps_exact=True,cycle_rule='Actual total extra cycles =4 per reached universal Foreign dispatch; actual Roll exit BMI/JMP both3.',
        primitive_component_input_seeds=True,natural_pickup_claim=False,outputs=0,Mesen=False)
    q['receipt_SHA256']=C.H(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Mini public ABI attempted artifacts/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)

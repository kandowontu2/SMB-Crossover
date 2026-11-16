"""Detached maturity/caller finite tests; no changed NesBus code mount."""
from pathlib import Path
from itertools import product
from unittest.mock import patch
import json
import plan_battletoads_mature8_6a3_1116 as Plan
import plan_battletoads_food_gate_6a3_1116 as Prior

Current,W,N=Plan.Current,Plan.W,Plan.N

def call(cache,smc,b,values,state,*,a=0,x=5,y=0,p=0x32):
    m=[0]*65536;m[0x100:0x180]=smc;m[0xa000:0xc000]=cache
    for n,v in values.items():m[W.address(b,n)]=v
    m[(W.address(b,'Enemy_State')+x)&255]=state
    m[W.address(b,'SafecallA_SMC')+1]=a;at=W.address(b,'FarcallJmpTarget_SMC')
    m[at+1]=Plan.ENTRY&255;m[at+2]=Plan.ENTRY>>8;m[W.address(b,'CurrentBank')]=252
    c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a=3;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff);minimum=c.sp;trace=[]
    for _ in range(180):
        if c.pc==0x5b00:break
        if c.pc in(range(Plan.STUB,Plan.STUB+8))or c.pc==Plan.RETURN:trace.append(c.pc)
        minimum=min(minimum,c.sp);assert m[c.pc],('Flat mature8 BRK',c.pc);c.step()
    else:raise AssertionError(('Flat mature8 bound',c.pc,c.sp))
    assert c.sp==224 and(c.x,c.y)==(x,y)and m[W.address(b,'CurrentBank')]==252
    assert all(m[W.address(b,n)]==v for n,v in values.items())
    assert m[(W.address(b,'Enemy_State')+x)&255]==state
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,CPU=c.processorCycles,minimum_SP=minimum,stub_trace=trace)

def growth_component(raw,seed):
    b=seed.bundle;base=N.NesMPU;entry=W.address(b,'NrPickupCollision');rows=[]
    for kind,state in product((0,1),(0,1,5,6,16,17,18,127,128,192)):
        m=N.fork(seed)
        for name,value in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=state,PowerUpType=kind,Enemy_X_Position=80,
            Enemy_PageLoc=1,Enemy_Y_Position=136,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=3).items():m[W.address(b,name)+5]=value
        N.put(m,FrameCounter=0,TimerControl=0);seen=[]
        class CPU(base):
            def step(self):
                if self.pc==entry and self.memory.rawtags[(entry-0x8000)//8192]==252:
                    seen.append(dict(PC=self.pc,SP=self.sp,state=N.get(self.memory,'Enemy_State',5),kind=N.get(self.memory,'PowerUpType',5)))
                return super().step()
        with patch.object(N,'NesMPU',CPU):result=N.invoke(m,'PowerUpObjHandler',a=0,x=5,y=0,p=0x32)
        rows.append(dict(initial_kind=kind,initial_state=state,actual_NrPickupCollision_entries=seen,
            final_state=N.get(m,'Enemy_State',5),actual_parent_return=result))
    return rows

def run(raw):
    old,new,q=Plan.proposal(raw);b=Current.bundle(raw);seed,opening=Current.cold(raw,'rash',True);smc=list(seed[0x100:0x180])
    base=dict(BtHostReady=1,SelectedCharacter=33,OperMode=1,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0)
    counts=dict(ABI=0,all256_each_Active_guard=0,all256_maturity_states_each_kind=0);minimum=255;representatives=[]
    def trial(values,state,expected,**regs):
        nonlocal minimum
        left,right=call(old,smc,b,values,state,**regs),call(new,smc,b,values,state,**regs)
        assert left['P']&1==0 and bool(right['P']&1)==expected
        assert(left['X'],left['Y'],left['SP'])==(right['X'],right['Y'],right['SP'])
        assert(left['P']^right['P'])&0x4c==0
        if state<128:assert right['stub_trace']==[0xb603,0xb605,0xb606,0xb602]
        else:assert right['stub_trace']==[0xb603,0xb605,0xb606,0xb608]
        minimum=min(minimum,left['minimum_SP'],right['minimum_SP']);return left,right
    for a,p,x,y in product((0,85,255),range(256),range(6),(0,23)):
        trial(base,128,True,a=a,p=p,x=x,y=y);counts['ABI']+=1
    for field in base:
        for v in range(256):
            values=dict(base,**{field:v});expected=values['BtHostReady']==1 and values['SelectedCharacter']==33 and values['OperMode']==1 and values['GameEngineSubroutine']==8 and values['GamePauseStatus']&1==0 and values['TimerControl']==0
            trial(values,128,expected);counts['all256_each_Active_guard']+=1
    for kind,state in product(range(4),range(256)):
        # Kind is not read by this MSB admission. All four native stock actors
        # must mature; final food and Star/L dispatch leaves remain unchanged.
        trial(base,state,state>=128);counts['all256_maturity_states_each_kind']+=1
    for state in(0,6,17,127,128,192):
        left,right=trial(base,state,state>=128);representatives.append(dict(state=state,old=left,new=right))
    off=W.address(b,'OffscreenBoundsCheck');at=W.location(b,'OffscreenBoundsCheck');prefix=raw[at:at+4]
    assert off==0xa504 and prefix[:3]==bytes.fromhex('b517c9')
    for a,p in product(range(256),range(256)):
        m=[0]*65536;m[off:off+4]=prefix;m[0x17+5]=46
        c=N.NesMPU(memory=m,pc=off);c.a=a;c.x=5;c.y=0;c.p=p;c.step();c.step()
        assert c.pc==off+4 and c.a==46 and c.p&0x4c==p&0x4c
        assert c.p&0x83==(1 if 46>=prefix[3]else 0)|(2 if 46==prefix[3]else 0)|(128 if(46-prefix[3])&128 else 0)
    cookie=raw[Current.COOKIE:Current.COOKIE+16];after=bytes.fromhex(q['spans'][2]['new'])
    header=raw[Current.HEADER:Current.HEADER+487];delta=Current.COOKIE-Current.HEADER;new_header=header[:delta]+after+header[delta+16:]
    headers=0
    for h,cookie in((header,cookie),(new_header,after)):
        for owner in range(256):assert bool(Prior.flat_check(h,cookie,b,owner=owner)['P']&1)==(owner==33);headers+=1
        for p in range(256):assert Prior.flat_check(h,cookie,b,p=p)['P']&1;headers+=1
        for i in range(16):
            bad=bytearray(cookie);bad[i]^=1;assert Prior.flat_check(h,bad,b)['P']&1==0;headers+=1
        assert Prior.flat_check(h,bytes(16),b)['P']&1==0;headers+=1
    growing=growth_component(raw,seed)
    # Source CPU public component uses ONLY the unchanged current parent.
    # Any immature current entry would return C0 under the detached new leaf;
    # there is no assumption that growth never invokes the public gate.
    for row in growing:
        for entry in row['actual_NrPickupCollision_entries']:
            out=call(new,smc,b,base,entry['state']);assert bool(out['P']&1)==(entry['state']>=128)
    q.update(passed=True,actual_parent_cold=opening,flat_only_no_changed_NesBus_mount=True,finite_counts=counts,minimum_SP=minimum,
        representative_maturity=representatives,C0_caller=dict(PC=off,first4=prefix.hex(),all65536_A_P_dead_output_cases=True),
        C1_caller='Frozen19-plan6ff42 independently proves A496 first6 killA/N/Z/C,65536cases',
        A_N_Z_changes_are_explicit_dead_outputs_not_an_AXYP_preservation_claim=True,
        actual_full16_BtCheck_cases=headers,actual_unmodified_parent_growth_components=growing,
        mature_admission_is_checked_before_vanilla_fallback=True,gameplay_qualification=False)
    q['receipt_SHA256']=Current.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    raw=Plan.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Detached mature8 attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Current.Cold.Runner.Native,'run',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)

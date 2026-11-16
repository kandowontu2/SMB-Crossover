"""Detached API ingress/growing-food and unchanged-parent fatal-call closure."""
from pathlib import Path
from itertools import product
from unittest.mock import patch
import json
import plan_battletoads_food_gate_6a3_1116 as Plan

Current,W,N=Plan.Current,Plan.W,Plan.N
PLAN_SHA='ad2cf7660ac7aefb341f1097732874f83c9dfda7c246fa1396cbf3df1fe1b64a'

def flat_pickup(cache,smc,b,kind,state,p):
    m=[0]*65536;m[0x100:0x180]=smc;m[0xa000:0xc000]=cache
    fields=dict(PowerUpType=kind,Enemy_State=state,PlayerStatus=0,GuestPowerupActive=0)
    for n,v in fields.items():m[W.address(b,n)+(5 if n in('PowerUpType','Enemy_State')else 0)]=v
    m[W.address(b,'BtSrc_Objects_Life')]=43
    target=0xa048;m[W.address(b,'SafecallA_SMC')+1]=0
    at=W.address(b,'FarcallJmpTarget_SMC');m[at+1]=target&255;m[at+2]=target>>8
    before=m[:];c=N.NesMPU(memory=m,pc=W.address(b,'FarCallCommon'));c.a=3;c.x=5;c.y=0;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    for _ in range(100):
        if c.pc==0x5b00:break
        assert m[c.pc],('Growing food flat BRK',c.pc);c.step()
    else:raise AssertionError('Growing food flat bound')
    assert c.sp==224 and c.x==5 and c.y==0
    assert m[W.address(b,'BtSrc_Objects_Life')]==43 and m[W.address(b,'PlayerStatus')]==0
    assert m[W.address(b,'Enemy_State')+5]==state and m[W.address(b,'GuestPowerupActive')]==0
    assert m[W.address(b,'Square2SoundQueue')]==0 and m[W.address(b,'FloateyNum_Control')+5]==0
    # No erase, popup or source HP write occurs before this ordinary BPL RTS.
    return dict(A=c.a,P=c.p,SP=c.sp)

def parent_public(m,slot):
    m[0x16a]=0;m[0x16c]=(0xb020+slot*3)&255;m[0x16d]=(0xb020+slot*3)>>8
    c=N.NesMPU(memory=m,pc=0x15a);c.a=215;c.x=5;c.y=0;c.p=0x32;c.sp=224;c.stPushWord(0x5aff)
    minimum=c.sp;reached=[]
    b=m.bundle;points={W.address(b,n):n for n in('BtInjury','BtApplyDamage18','KillPlayer')}
    for _ in range(40000):
        if c.pc==0x5b00:break
        tag=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
        if c.pc in points:
            if points[c.pc]=='KillPlayer'or tag==3:reached.append(dict(name=points[c.pc],PC=c.pc,SP=c.sp,tag=tag))
        minimum=min(minimum,c.sp);assert m[c.pc],('Unchanged parent public BRK',c.pc,tag);c.step()
    else:raise AssertionError(('Unchanged parent public bound',slot,c.pc,c.sp))
    assert c.sp==224
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,minimum_SP=minimum,reached=reached)

def run(raw):
    assert Current.digest(Path(Plan.__file__).read_bytes())==PLAN_SHA
    old,new,proposal=Plan.proposal(raw);b=Current.bundle(raw);seed,opening=Current.cold(raw,'rash',True)
    # Only detached cache arrays are examined; no changed code enters NesBus.
    assert old[:0x45]==new[:0x45]and old[0x48:]==new[0x48:]
    table=[]
    for i in range(36):
        at=3*i;left,right=old[at:at+3],new[at:at+3]
        assert left[0]==right[0]==0x4c
        assert(left!=right)==(i==23)
        table.append(dict(slot=i,old_target=int.from_bytes(left[1:],'little'),new_target=int.from_bytes(right[1:],'little')))
    public=W.location(b,'BtServiceVeneers');pc=W.address(b,'BtServiceVeneers')
    assert pc==0xb020 and public==716848
    vectors=raw[public:public+108];assert all(vectors[3*i:3*i+3]==bytes.fromhex('4c8eb0')for i in range(36))
    labels=[n for n,s in b['syms'].items()if int(s.get('val','0'),0)in(0xa046,0xa047)]
    smc=list(seed[0x100:0x180]);growing=0
    for cache,kind,state,p in product((old,new),(0,1),range(128),(0x20,0x69,0xed)):
        flat_pickup(cache,smc,b,kind,state,p);growing+=1
    # Actual unchanged parent public service, explicitly primitive-seeded HP.
    # This is death-rule isolation, not earned gameplay or candidate mounting.
    deaths=[]
    for key in('rash','zitz'):
        m,front=Current.cold(raw,key,True)
        N.put(m,InjuryTimer=0,CurrentPlayer=0,GameEngineSubroutine=8,NumberofLives=2)
        m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191]=3
        m.ram[3][W.address(b,'BtSrc_Objects_death_timer')&8191]=0
        result=parent_public(m,5)
        health=m.ram[3][W.address(b,'BtSrc_Objects_Life')&8191]
        death=m.ram[3][W.address(b,'BtSrc_Objects_death_timer')&8191]
        engine=N.get(m,'GameEngineSubroutine')
        assert health==0 and death==0xc0 and engine==11 and any(r['name']=='KillPlayer'for r in result['reached'])
        values=dict(BtHostReady=1,SelectedCharacter=33,OperMode=1,GameEngineSubroutine=engine,GamePauseStatus=0,TimerControl=N.get(m,'TimerControl'))
        rejected=Plan.flat_call(new,smc,b,values);assert rejected['P']&1==0
        deaths.append(dict(identity=key,real_compiled_cold=front,primitive_only=True,HP_before=3,HP_after=health,
            source_death_timer=death,actual_native_engine=engine,actual_parent_public=result,detached_new_gate=rejected))
    # Exact zero HP does not trigger the donor's underflow death. Keep that
    # original distinction; do not add a guessed health>0 predicate to Active.
    q=dict(passed=True,owning_parent_SHA256=Plan.PIN,proposal=proposal,
        public36_vectors_SHA256=Current.digest(vectors),public23_PC=pc+23*3,public_common_PC=0xb08e,
        private36_table=table,private_table_has_only_aligned_JMP_entries=True,
        private_slot23_half_open=[0xa045,0xa048],interior_symbol_aliases=labels,
        ingress_scope='Existing public87 B020+3*slot, clamped0..35; unchanged public23 B065 -> existing privateA045; no new entry, fallthrough or storage',
        direct_external_undecoded_alias_universe_claim=False,
        growing_food_unchanged_BPL_rejections=growing,maturity_scope='M/F0..127 still return without erase/heal/cue; native Star/L policy unchanged',
        actual_parent_death_rule_cases=deaths,zeroHP_without_underflow_is_original_live_state=True,
        no_changed_NesBus_mount=True,no_ROM_composition=True,gameplay_qualification=False,outputs=0)
    q['receipt_SHA256']=Current.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    raw=Plan.ROM.read_bytes()
    def deny(*args,**kw):raise AssertionError('Detached closure attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny),patch.object(Current.Cold.Runner.Native,'run',deny):q=run(raw)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)

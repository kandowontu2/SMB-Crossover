"""Actual assembled object/drop owner controls; explicit CPU RAM, no native claim."""
from pathlib import Path
import argparse, hashlib, itertools, json
from collections import Counter
from final_roll_items_cpu import ready
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

BASE='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
FIXED='3eedadc826c285ebf14335dbc3e8f75a25df44ad235a3c0533494a3997416987'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
DROP=['InvDropKind','InvDropX','InvDropPage','InvDropY','InvDropVY',
      'InvDropVYMid','InvDropVYHi','InvDropFraction','InvDropFractionHi',
      'InvDropAge','InvDropAgeHi','AvDropItem']


def invoke(q,name,a=0,x=0,y=0):
    b,m=q.b,q.m;s=b['syms'][name];g=b['segs'][s['seg']]
    pc=address(b,name);window=(pc-0x8000)//8192
    physical=(int(g['ooffs'],0)-16)//8192;m.page(window,physical)
    if window in (1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',physical|128)
    # $100..159 is application RAM; $15a..17a is live farcall SMC.
    sentinels={p:(p*73+29)&255 for p in range(0x17b,0x1c0)}
    for p,v in sentinels.items():m[p]=v
    m.writes=[];c=NesMPU(memory=m,pc=pc)
    c.a,c.x,c.y,c.p,c.sp=a,x,y,0x30,0xfd;c.stPushWord(0x5aff)
    names=['GameLoop','GameLoop::PauseSkip','ProcFireball_Bubble',
           'Z2UpdateDropsGate','InventoryUpdateDrops','RlWeapons',
           'InventoryEnemyDrop','RlWeapons::Done','ProcFireball_Bubble::ProcAirBubbles']
    hooks={(address(b,n),(location(b,n)-16)//8192):n for n in names}
    events=[];writes=[];min_sp=255
    for _ in range(100000):
        if c.pc==0x5b00:
            assert c.sp==0xfd and all(m[p]==v for p,v in sentinels.items())
            for n,i in [('CurrentBank',1),('CurrentBankC',2)]:assert q.get(n)==m.banks[i]|128
            return dict(registers=[c.a,c.x,c.y,c.p,c.sp],events=events,writes=writes,
                        cycles=c.processorCycles,min_sp=min_sp,banks=m.banks.copy())
        at=c.pc;bank=m.banks[(at-0x8000)//8192]if at>=0x8000 else-1
        if(at,bank)in hooks:events.append(hooks[at,bank])
        min_sp=min(min_sp,c.sp);start=len(m.writes);c.step()
        writes.extend(dict(pc=at,bank=bank,address=p,value=v)for p,v in m.writes[start:])
    raise AssertionError(('CPU timeout',name,hex(c.pc),m.banks))


def state(q):return{n:[q.get(n,i)for i in range(4)]for n in DROP}


def seed(b,mode,kind=1,meter=128,age=0,trajectory='air',slot=3):
    q=ready(b,mode,12,8)
    q.put(AreaType=1,Player_Y_Position=176,ObjectOffset=4)
    for n,v in dict(InvDropKind=kind,InvDropX=168,InvDropPage=1,
                    InvDropY=192,InvDropVY=85,InvDropVYMid=85,
                    InvDropVYHi=254,InvDropAge=age&255,
                    InvDropAgeHi=age>>8,AvDropItem=meter).items():q.set(n,v,slot)
    if trajectory=='floor':
        for n in ['InvDropVY','InvDropVYMid','InvDropVYHi']:q.set(n,0,slot)
        for page in range(2):
            for row in [11,12]:
                for col in range(16):q.set('Block_Buffer_1',0x54,page*208+row*16+col)
    elif trajectory=='contact':q.set('InvDropX',104,slot)
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--expected-base-sha256',default=BASE)
    p.add_argument('--expected-candidate-sha256',default=FIXED)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert sha(a.baseline)==a.expected_base_sha256 and sha(a.candidate)==a.expected_candidate_sha256
    a.output.mkdir(parents=True,exist_ok=False);old,new=map(scoped_load,[a.baseline,a.candidate]);rows=[]
    # Whole native object dispatcher must equal the actual shared update called
    # once, for actor state and selected/other resource. No fake physics stub.
    for mode,kind,meter,age,trajectory,slot in itertools.product(
            [0,1],[1,2],[0,128],[0,238,239,240,418,419],['air','floor','contact'],[0,3]):
        qs=[seed(b,mode,kind,meter,age,trajectory,slot)for b in [old,new,new]]
        baseline=invoke(qs[0],'ProcFireball_Bubble');fixed=invoke(qs[1],'ProcFireball_Bubble')
        oracle=invoke(qs[2],'InventoryUpdateDrops')
        assert state(qs[1])==state(qs[2]),(mode,kind,meter,age,trajectory,slot)
        for n in ['RlHealth','RlEnergy','RlFoodKind','Square2SoundQueue']:
            assert qs[1].get(n)==qs[2].get(n),(n,mode,kind,meter,age,trajectory,slot)
        assert baseline['events'].count('InventoryUpdateDrops')==2
        assert fixed['events'].count('InventoryUpdateDrops')==1
        assert fixed['events'].index('InventoryUpdateDrops')<fixed['events'].index('RlWeapons')
        assert qs[1].get('ObjectOffset')==4
        rows.append(dict(case='actual_dispatch_equals_one_shared_update',mode=mode,kind=kind,meter=meter,
                         age=age,trajectory=trajectory,slot=slot,
                         before=baseline['cycles'],after=fixed['cycles'],min_sp=fixed['min_sp'],
                         baseline_age=state(qs[0])['InvDropAge'][slot]+256*state(qs[0])['InvDropAgeHi'][slot],
                         candidate_age=state(qs[1])['InvDropAge'][slot]+256*state(qs[1])['InvDropAgeHi'][slot]))
    # CPU-only final-hit setup. Native default75HP/three-pellet chronology is
    # separately preserved in the live first-write trace; no natural claim here.
    for mode,large,meter in itertools.product([0,1],[0,192],[0,128]):
        observations=[]
        for b in [old,new]:
            q=ready(b,mode);q.put(AreaType=1,Player_Y_Position=176,
                Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=160,
                Enemy_PageLoc=1,Enemy_Y_Position=184,Enemy_Y_HighPos=1,
                Enemy_BoundBoxCtrl=9,Enemy_MovingDir=2,MmEnemyHealthLo=25,
                MmEnemyHealthHi=0,MmEnemyFlash=0)
            q.set('PseudoRandomBitReg',0,1);q.set('PseudoRandomBitReg',large,2)
            q.set('PseudoRandomBitReg',1 if meter else 0,3)
            for n,v in dict(MmBulletType=1,MmBulletX=157,MmBulletPage=1,
                            MmBulletY=194,MmBulletDir=1).items():q.set(n,v,3)
            r=invoke(q,'ProcFireball_Bubble')
            assert q.get('Enemy_State')==34 and q.get('MmEnemyHealthLo')==0
            assert q.get('InvDropKind',3)==(2 if large else 1)
            assert q.get('AvDropItem',3)==meter
            observations.append(dict(age=q.get('InvDropAge',3),y=q.get('InvDropY',3),events=r['events']))
        assert observations[0]['age']==1 and observations[1]['age']==0
        events=observations[1]['events']
        assert events.index('InventoryUpdateDrops')<events.index('RlWeapons')<events.index('InventoryEnemyDrop')
        rows.append(dict(case='real_final_hit_birth_after_shared_owner',mode=mode,kind=2 if large else 1,meter=meter,observations=observations))
    # Cold ordinary Bass is outside Roll admission; entire actual kernel stays
    # byte-for-byte identical in writes/registers/cycles, not merely age.
    for mode,variant,joy in itertools.product([0,1],[0],[0,64]):
        r=[]
        for b in [old,new]:
            q=seed(b,mode);q.put(RlVariant=variant,SavedJoypadBits=joy,A_B_Buttons=joy)
            r.append(invoke(q,'ProcFireball_Bubble'))
        assert r[0]==r[1]
        rows.append(dict(case='ordinary_bass_whole_kernel_exact',mode=mode,buttons=joy,cycles=r[1]['cycles']))
    count=address(new,'CHARACTER_COUNT')
    for mode,char,variant in itertools.product([0,1],range(count),[0,1,2,3]):
        q=Arena(new,char);q.put(CrossoverBehaviorVersion=mode,RlVariant=variant)
        c,_=q.invoke('RlIsActive');assert bool(c.p&1)==(char==9 and variant!=0)
        rows.append(dict(case='actual_variant_admission',mode=mode,character=char,variant=variant,active=bool(c.p&1)))
    # Timer and actual native death engine prevent actor progression. Both
    # object dispatcher sequences must match, even though the inactive local
    # call still differs in code reached only after RlWeapons' early gate.
    for mode,condition in itertools.product([0,1],['timer','death_engine','other_engine']):
        rs=[]
        for b in [old,new]:
            q=seed(b,mode)
            if condition=='timer':q.set('TimerControl',1)
            elif condition=='death_engine':q.put(TimerControl=255,GameEngineSubroutine=11,MmDeathFlag=1)
            else:q.set('GameEngineSubroutine',7)
            r=invoke(q,'ProcFireball_Bubble');assert q.get('InvDropAge',3)==0
            rs.append(r)
        assert rs[0]==rs[1]
        rows.append(dict(case='inactive_order_exact',mode=mode,condition=condition,cycles=rs[1]['cycles']))
    # Execute the actual whole paused GameLoop, including pause/UI/RNG/top-score
    # work and its normal return. No operation tree/drop/weapon entry occurs.
    for mode in [0,1]:
        rs=[]
        for b in [old,new]:
            q=seed(b,mode);q.put(GamePauseStatus=1,OperMode_Task=3)
            r=invoke(q,'GameLoop');assert q.get('InvDropAge',3)==0
            assert 'GameLoop::PauseSkip'in r['events']
            assert not any(n in r['events']for n in ['ProcFireball_Bubble','InventoryUpdateDrops','RlWeapons'])
            rs.append(r)
        assert rs[0]==rs[1]
        rows.append(dict(case='actual_paused_whole_gameloop_exact',mode=mode,cycles=rs[1]['cycles']))
    proof=dict(passed=True,native_passed=False,goal_complete=False,scope=__doc__,
        baseline_SHA256=a.expected_base_sha256,candidate_SHA256=a.expected_candidate_sha256,script_SHA256=sha(__file__),
        case_counts=dict(Counter(r['case']for r in rows)),cases=len(rows),checks=rows,
        preserved=['OnlyRoll active route reaches the removed local call.','Object-global update precedes Roll weapon/contact/drop birth.','Actual dispatch drop state equals one actual standalone shared update, including expiry/contact/physics.','Free lower-stack guard17b..1bf preserved, returnSPFD, actual/shadow A/C banks agree after each invocation.','OrdinaryBass and inactive/pause paths retain exact ordered writes, registers and cycles.'],
        limits=['Explicit CPU RAM, including final-hit enemy HP and RNG controls. Native natural birth/write evidence exists separately; this is not another native run.','No interrupts, PPU/display publication, audio cadence or native lifecycle timing claim.','AfteractiveRoll call, removed shared function scratch/register clobbers are no longer reproduced. Actual following ProcAirBubbles initializes its live A/X/Y inputs; application drop behavior is checked through the whole object dispatcher.'])
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in proof.items()if k not in ['checks','preserved','limits']}))


if __name__=='__main__':main()

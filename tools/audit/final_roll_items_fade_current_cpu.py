"""Current-parent exact object ownership controls; declared CPU state only."""
from pathlib import Path
import argparse,hashlib,itertools,json
from collections import Counter
from final_roll_items_single_owner_cpu import invoke,seed,state
from final_roll_items_cpu import ready
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--private',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    build=json.loads((a.private/'proof.json').read_text(encoding='utf-8'));oldrom=a.private/'baseline/candidate.nes';newrom=a.private/'candidate.nes'
    assert sha(oldrom)==build['base_sha256']and sha(newrom)==build['candidate_sha256']
    old,new=map(scoped_load,[oldrom,newrom]);rows=[]
    for mode,kind,meter,age,trajectory,slot in itertools.product([0,1],[1,2],[0,128],[0,238,239,240,418,419],['air','floor','contact'],[0,3]):
        qs=[seed(b,mode,kind,meter,age,trajectory,slot)for b in [old,new,new]]
        before,after=[invoke(q,'ProcFireball_Bubble')for q in qs[:2]];oracle=invoke(qs[2],'InventoryUpdateDrops')
        assert before==after and state(qs[0])==state(qs[1])==state(qs[2])
        assert after['events'].count('InventoryUpdateDrops')==1 and after['events'].index('InventoryUpdateDrops')<after['events'].index('RlWeapons')
        for n in ['RlHealth','RlEnergy','RlFoodKind','Square2SoundQueue']:assert qs[0].get(n)==qs[1].get(n)==qs[2].get(n)
        rows.append(dict(case='whole_dispatch_exact_current_parent_and_one_owner',mode=mode,kind=kind,meter=meter,age=age,trajectory=trajectory,slot=slot,cycles=after['cycles'],min_sp=after['min_sp']))
    for mode,large,meter in itertools.product([0,1],[0,192],[0,128]):
        observations=[]
        for b in [old,new]:
            q=ready(b,mode);q.put(AreaType=1,Player_Y_Position=176,Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=160,Enemy_PageLoc=1,Enemy_Y_Position=184,Enemy_Y_HighPos=1,Enemy_BoundBoxCtrl=9,Enemy_MovingDir=2,MmEnemyHealthLo=25,MmEnemyHealthHi=0,MmEnemyFlash=0)
            q.set('PseudoRandomBitReg',0,1);q.set('PseudoRandomBitReg',large,2);q.set('PseudoRandomBitReg',1 if meter else 0,3)
            for n,v in dict(MmBulletType=1,MmBulletX=157,MmBulletPage=1,MmBulletY=194,MmBulletDir=1).items():q.set(n,v,3)
            result=invoke(q,'ProcFireball_Bubble');assert q.get('Enemy_State')==34 and q.get('MmEnemyHealthLo')==0 and q.get('InvDropAge',3)==0 and q.get('InvDropKind',3)==(2 if large else 1)and q.get('AvDropItem',3)==meter
            observations.append(result)
        assert observations[0]==observations[1];rows.append(dict(case='explicit_CPU_final_hit_birth_order_exact',mode=mode,large=large,meter=meter))
    for mode,joy in itertools.product([0,1],[0,64]):
        pair=[]
        for b in [old,new]:
            q=seed(b,mode);q.put(RlVariant=0,SavedJoypadBits=joy,A_B_Buttons=joy);pair.append(invoke(q,'ProcFireball_Bubble'))
        assert pair[0]==pair[1];rows.append(dict(case='ordinary_Bass_dispatch_exact',mode=mode,buttons=joy))
    for mode,char,variant in itertools.product([0,1],range(address(new,'CHARACTER_COUNT')),[0,1,2,3]):
        pair=[]
        for b in [old,new]:
            q=Arena(b,char);q.put(CrossoverBehaviorVersion=mode,RlVariant=variant);c,_=q.invoke('RlIsActive');pair.append(bool(c.p&1))
        assert pair[0]==pair[1]==(char==9 and variant!=0);rows.append(dict(case='actual_variant_admission_exact',mode=mode,character=char,variant=variant))
    for mode,condition in itertools.product([0,1],['timer','death_engine','other_engine']):
        pair=[]
        for b in [old,new]:
            q=seed(b,mode)
            if condition=='timer':q.set('TimerControl',1)
            elif condition=='death_engine':q.put(TimerControl=255,GameEngineSubroutine=11,MmDeathFlag=1)
            else:q.set('GameEngineSubroutine',7)
            pair.append(invoke(q,'ProcFireball_Bubble'));assert q.get('InvDropAge',3)==0
        assert pair[0]==pair[1];rows.append(dict(case='inactive_order_exact',mode=mode,condition=condition))
    for mode in [0,1]:
        pair=[]
        for b in [old,new]:
            q=seed(b,mode);q.put(GamePauseStatus=1,OperMode_Task=3);r=invoke(q,'GameLoop');assert q.get('InvDropAge',3)==0 and 'GameLoop::PauseSkip'in r['events']and not any(n in r['events']for n in ['ProcFireball_Bubble','InventoryUpdateDrops','RlWeapons']);pair.append(r)
        assert pair[0]==pair[1];rows.append(dict(case='whole_paused_GameLoop_exact',mode=mode))
    proof=dict(passed=True,native_passed=False,goal_complete=False,baseline_sha256=sha(oldrom),candidate_sha256=sha(newrom),build_proof_sha256=sha(a.private/'proof.json'),cases=len(rows),case_counts=dict(Counter(x['case']for x in rows)),checks=rows,tool_sha256=sha(Path(__file__)),scope=__doc__,limits=['Explicit CPU actor/resources/RNG/HP for isolated code comparisons; no natural/native claim.','Exact full ordered application/SMC/bank writes, CPU registers/cycles and return stack versus current parent for object dispatcher and pause controls; standalone shared owner oracle. No interrupts/PPU.'])
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items()if k not in ['checks','limits']}))
if __name__=='__main__':main()

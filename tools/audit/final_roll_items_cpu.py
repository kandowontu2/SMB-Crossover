"""Actual assembled Roll resource controls; explicit CPU RAM, no native claim."""
from pathlib import Path
import argparse, hashlib, json
from collections import Counter
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address

TARGET='8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def ready(b,mode=0,hp=28,energy=28):
    q=Arena(b,9)
    q.put(CrossoverBehaviorVersion=mode,RlVariant=1,NumberofLives=2,
          AreaPointer=0,WorldNumber=0,ScreenLeft_PageLoc=1,
          ScreenRight_PageLoc=1,ScreenRight_X_Pos=255)
    q.invoke('RlEnsure')
    q.put(RlHealth=hp,RlEnergy=energy)
    return q


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',default=TARGET)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert sha(a.rom)==a.expected_sha256
    a.output.mkdir(parents=True,exist_ok=False)
    b=scoped_load(a.rom);rows=[]
    for mode in (0,1):
        for hp in range(29):
            for energy in range(29):
                for kind in (0,1):
                    q=ready(b,mode,hp,energy)
                    q.set('PowerUpType',kind,5)
                    c,_=q.invoke('RlCollect',x=5)
                    assert c.p&1 and (q.get('RlHealth'),q.get('RlEnergy'),q.get('RlFoodKind'),q.get('PlayerStatus'))==(28,28,1,1)
                    assert q.get('Square2SoundQueue')==address(b,'Sfx_PowerUpGrab')
                    rows.append(dict(case='food_leaf',mode=mode,hp=hp,energy=energy,type=kind,result=[28,28]))
        for kind in (2,3):
            q=ready(b,mode,12,8);q.set('PowerUpType',kind,5)
            c,_=q.invoke('RlCollect',x=5)
            assert not c.p&1 and (q.get('RlHealth'),q.get('RlEnergy'))==(12,8)
            rows.append(dict(case='star_oneup_bypass_leaf',mode=mode,type=kind))
        for meter in (0,128):
            for value in range(29):
                for other in (0,17,28):
                    for raw_amount in (8,40):
                        for slot in range(4):
                            q=ready(b,mode,value if meter else other,other if meter else value)
                            q.set('InvDropSlot',slot);q.set('AvDropItem',meter,slot)
                            q.invoke('RlRefillDispatch',a=raw_amount)
                            result=min(28,value+raw_amount//4)
                            assert (q.get('RlHealth'),q.get('RlEnergy'))==((result,other)if meter else(other,result))
                            assert q.get('Square2SoundQueue')==address(b,'Sfx_CoinGrab')
                            rows.append(dict(case='capsule_refill_leaf',mode=mode,meter=meter,value=value,other=other,amount=raw_amount//4,slot=slot,result=result))
        for hp in range(29):
            for energy in range(29):
                q=ready(b,mode,hp,energy);q.put(RlDirty=1,VRAM_Buffer1_Offset=0)
                q.invoke('RlUi')
                data=[q.get('VRAM_Buffer1',i)for i in range(32)]
                assert data[:5]==[32,4,12,17,25]
                assert data[5:7]==[hp//10,hp%10] and data[11:13]==[energy//10,energy%10]
                assert q.get('VRAM_Buffer1_Offset')==31 and data[31]==0 and q.get('RlDirty')==0
                rows.append(dict(case='hud_command_digits',mode=mode,hp=hp,energy=energy,digits=[data[5:7],data[11:13]]))
        q=ready(b,mode,12,8);q.put(RlDirty=1,VRAM_Buffer1_Offset=53)
        q.invoke('RlUi');assert q.get('VRAM_Buffer1_Offset')==53 and q.get('RlDirty')==1
        rows.append(dict(case='hud_capacity_refusal',mode=mode,offset=53))
        for energy in range(29):
            q=ready(b,mode,28,energy);q.put(SavedJoypadBits=64,RlFresh=64)
            observed=[]
            for t in range(61):
                q.invoke('RlWeapons');observed.append([q.get('RlCharge'),q.get('RlEnergy'),q.get('RlChargeFired')])
                q.set('RlFresh',0)
            if energy>=4:
                assert [r[0]for r in observed[:60]]==list(range(1,61))
                assert all(r[1:]==[energy,0]for r in observed[:60])
                assert observed[-1]==[0,energy-4,1]
            else:
                assert all(r==[0,energy,0]for r in observed)
            rows.append(dict(case='held_charge_61_source_calls',mode=mode,energy=energy,first=observed[0],at60=observed[59],at61=observed[60]))
        q=ready(b,mode);q.put(RlCharge=60,SavedJoypadBits=64,RlFresh=0)
        for i in range(4):
            q.set('MmBulletType',1,i);q.set('MmBulletX',120,i);q.set('MmBulletPage',1,i);q.set('MmBulletY',177,i);q.set('MmBulletDir',1,i)
        q.invoke('RlWeapons')
        assert(q.get('RlEnergy'),q.get('RlCharge'),q.get('RlChargeFired'))==(28,60,0)
        rows.append(dict(case='explicit_full_pool_no_charge_payment',mode=mode,scope='Direct CPU pool state, not native reachability.'))
        q=ready(b,mode,12,8);q.put(RlCharge=32,RlAttack=9,InvDropKind=1,MmBulletType=1)
        q.set('AreaPointer',1);q.invoke('RlEnsure')
        assert(q.get('RlHealth'),q.get('RlEnergy'),q.get('RlFoodKind'))==(12,8,0)
        assert all(q.get('InvDropKind',i)==q.get('MmBulletType',i)==0 for i in range(4)) and q.get('RlCharge')==0
        rows.append(dict(case='explicit_area_reset_preserves_resources_cleans_volatile',mode=mode))
        q=ready(b,mode,4,8);q.put(RlFoodKind=1,NumberofLives=1,RlCharge=60,InvDropKind=1,MmBulletType=1)
        q.invoke('RlResetOwn')
        assert(q.get('RlHealth'),q.get('RlEnergy'),q.get('RlFoodKind'))==(28,28,0)
        assert all(q.get('InvDropKind',i)==q.get('MmBulletType',i)==0 for i in range(4)) and q.get('RlCharge')==0
        rows.append(dict(case='explicit_life_loss_reset_full_resources_and_cleanup',mode=mode))
        for hp in range(9,29):
            for enemy,damage in [(6,4),(address(b,'Bowser'),8)]:
                for protection in (0,1,64):
                    q=ready(b,mode,hp,8);q.put(RlInvul=protection,ObjectOffset=0,RlCharge=30,RlAttack=8)
                    q.set('Enemy_ID',enemy);q.invoke('RlInjury')
                    assert q.get('RlHealth')==hp-(damage if protection==0 else 0)
                    if protection==0:assert(q.get('RlInvul'),q.get('RlHurt'),q.get('RlCharge'),q.get('RlAttack'))==(64,16,0,0)
                    rows.append(dict(case='nonlethal_injury_and_protection_leaf',mode=mode,hp=hp,enemy=enemy,protection=protection,result=q.get('RlHealth')))
    counts=dict(Counter(q['case']for q in rows))
    result=dict(passed=True,native_passed=False,goal_complete=False,ROM_sha256=a.expected_sha256,script_sha256=sha(Path(__file__)),cases=len(rows),case_counts=counts,checks=rows,scope=__doc__,limits=['Direct CPU RAM controls; no natural resource acquisition, native timing/reachability, committed PPU or acoustic proof.','Charge measured as60 accumulation calls then an attempt on61; full pool leaves60 and pays nothing.','Actual mobile gameplay executable unavailable; production behavior is documented adaptation, not mobile timing/audio certification.'])
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k not in ['checks','limits']}))


if __name__=='__main__':main()

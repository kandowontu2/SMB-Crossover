"""Real defeat indices/side effects and vector interruptions of RAM3 combat.

Offline explicitly preloaded virtual image. No loader, Main or native claim.
"""
from pathlib import Path
import copy,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v3 as T
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import address
C=T.C;make=T.make;put=T.put;get=T.get;setv=T.setv;actor=T.actor;run=T.run;sha=T.sha
P=R/'build/final-fantasy-host-combat-v2';O=R/'build/final-fantasy-host-combat-controls-v4'

def defeat_indices(b):
    rows=[]
    for name,x,old,p in itertools.product(['Goomba','HammerBro','PiranhaPlant','Bowser'],range(6),range(6),C.flags()):
        m=make(b);kind=address(b,name);actor(m,x=x,kind=kind,px=144,y=160)
        put(m,FfDamage=75,WorldNumber=7,ObjectOffset=old,DuplicateObj_Offset=(x+1)%6)
        setv(m,'MmEnemyHealthLo',75,x)
        before_other=[(get(m,'Enemy_State',i),get(m,'MmEnemyHealthLo',i),get(m,'MmEnemyHealthHi',i))for i in range(6)]
        c,tr,_=run(m,'FfHostDamage',x=x,p=p)
        assert c.x==x and c.p&1 and get(m,'ObjectOffset')==old
        assert C.hp(m,x)==0 and get(m,'Enemy_State',x)&32
        expected=9 if name=='Bowser'else 1 if name=='Goomba'else 6 if name=='HammerBro'else 2
        assert get(m,'FloateyNum_Control',x)==expected and get(m,'FloateyNum_Timer',x)==48
        assert get(m,'Square1SoundQueue')==address(b,'Sfx_EnemySmack')
        assert get(m,'Enemy_Y_Speed',x)==(254 if name=='Bowser'else 253)
        if name=='Bowser':assert get(m,'BowserHitPoints')==0 and get(m,'Square2SoundQueue')==address(b,'Sfx_BowserFall')
        for i in range(6):
            if i!=x:assert (get(m,'Enemy_State',i),get(m,'MmEnemyHealthLo',i),get(m,'MmEnemyHealthHi',i))==before_other[i]
        assert m.rawtags[1:3]==[215,216] and get(m,'CurrentBankC')==216
        rows.append([name,x,old,p,expected,c.processorCycles])
    return dict(cases=len(rows),all64_flags=True,all_native_slots_and_saved_ObjectOffset_values=True,
                actual_score_timer_SFX_direction_vertical_speed=True,rows=rows)

def simultaneous(b):
    rows=[]
    for kind in ['Goomba','HammerBro','BuzzyBeetle','Podoboo','BulletBill_FrenzyVar','BulletBill_CannonVar']:
        m=make(b);put(m,FfVariant=1,FfPower=2,FfAction=1)
        for x in range(6):actor(m,x=x,kind=address(b,kind),px=140,y=160)
        for off in [0,12,24]:
            at=address(b,'FfProjectile')+off
            for i,v in {0:4,4:147,7:178,8:1,10:2}.items():m[at+i]=v
        c,tr,_=run(m,'FfHostWeapons')
        hits=[get(m,'FfProjectile',off+9)for off in [0,12,24]]
        immune=kind in ['BuzzyBeetle','Podoboo','BulletBill_FrenzyVar','BulletBill_CannonVar']
        if immune:
            assert all(C.hp(m,x)==0 and get(m,'Enemy_State',x)==0 for x in range(6))
            assert get(m,'FfHits')==63 and hits==[63,63,63]
        else:
            assert all(C.hp(m,x)==0 and get(m,'Enemy_State',x)&32 for x in range(6))
            if kind=='Goomba':assert hits==[63,0,0] and get(m,'FfHits')==63
            else:assert hits==[63,63,0] and get(m,'FfHits')==63
            count=sum(pc==address(b,'ShellOrBlockDefeat')for pc,tag in tr)
            assert count==6,('single actual native defeat per identity',kind,count)
        rows.append(dict(kind=kind,cycles=c.processorCycles,melee_mask=get(m,'FfHits'),projectile_masks=hits))
    return dict(cases=len(rows),all6_native_targets_3source_shots=True,rows=rows)

def interrupt_controls(b):
    fields=list(range(0x5c00,0x5c80))+list(range(0x5fc1,0x5fcf))+[0x5fef]
    def scenario(name,oldA=215,oldC=216,lag=255):
        m=make(b);m.raw_page(1,oldA);m.raw_page(2,oldC);put(m,CurrentBank=oldA,CurrentBankC=oldC,NmiDisable=lag)
        if name=='FfHostNewEnemy':
            put(m,FfHits=63)
            for off in [0,12,24]:setv(m,'FfProjectile',63,off+9)
            args=dict(a=0x59,x=2,y=0xa7,p=0x31)
        else:
            actor(m,x=2,kind=address(b,'HammerBro'),px=140,y=160)
            put(m,FfDamage=255,ObjectOffset=5)
            args=dict(x=2,p=0x31)
        return m,args
    rows=[]
    for name in ['FfHostNewEnemy','FfHostDamage']:
        m,args=scenario(name);c=C.E.start(m,name,True,**args);seen=set();cuts=[]
        for step in range(10000):
            if c.pc==0x5b00:break
            raw=m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1
            key=c.pc,raw
            # Every actual public-combat instruction and all33SMC boundaries,
            # plus sampled genuine native defeat/score/drop instructions.
            if key not in seen and (0xb700<=c.pc<0xb8ec and raw==3 or c.pc<0x200 or step%23==0):cuts.append((step,c.pc))
            seen.add(key);c.step()
        else:raise AssertionError('discovery bounded')
        for step,pc in cuts:
            for oldA,oldC in [(215,216),(3,2),(131,130)]:
                for kind,lag in [('IRQ',255),('NMI',255),('NMI',0)]:
                    q,args=scenario(name,oldA,oldC,lag);d=C.E.start(q,name,True,**args)
                    for _ in range(step):d.step()
                    assert d.pc==pc
                    if kind=='IRQ'and d.p&4:continue
                    before=bytes(q[i]for i in fields)
                    proof=C.E.interrupt(q,d,kind)
                    assert bytes(q[i]for i in fields)==before
                    for _ in range(10000):
                        if d.pc==0x5b00:break
                        assert q[d.pc];d.step()
                    else:raise AssertionError('postISR bounded')
                    assert q.rawtags[1:3]==[oldA,oldC]
                    rows.append(dict(entry=name,step=step,PC=pc,oldA=oldA,oldC=oldC,lag=lag,**proof))
    return dict(real_vector_cases=len(rows),all143FFbytes_and_33SMC_unchanged=True,
                raw3_not_ROM83=True,normal_lag_NMI_and_IRQ=True,rows=rows)

def main():
    assert not O.exists();O.mkdir()
    b=C.bundle(P);proof=json.loads((P/'build-proof.json').read_text())
    for p,h in proof['bindings'].items():assert sha(p)==h,p
    d=dict(passed=False,native=False,host_Main=False,fixture_RAM3_preloaded=True,checks={},failures={})
    for n,f in [('defeat_indices',defeat_indices),('simultaneous',simultaneous),('interrupts',interrupt_controls)]:
        try:d['checks'][n]=f(b)
        except Exception as e:d['failures'][n]=dict(error=repr(e),traceback=traceback.format_exc())
    d['passed']=not d['failures']
    deps=[Path(__file__),Path(T.__file__),Path(C.__file__),P/'build-proof.json',
          R/'tools/audit/ff_ram3_execution_controls_v2.py',R/'tools/audit/arthur_cache_host_controls_v1.py',
          R/'tools/audit/verify_native_relocation.py',R/'tools/audit/check_tmnt_render_oa.py']
    d['bindings']={**proof['bindings'],**{str(p.resolve()):sha(p)for p in deps}}
    (O/'controls.json').write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(passed=d['passed'],checks=list(d['checks']),failures=d['failures'])))
    assert d['passed']
if __name__=='__main__':main()

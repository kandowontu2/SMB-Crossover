"""Full compiled GameLoop earned-copy/health and Meta action controls.

Source CPU only. Each native-ready unit will stage complete legal map/player/
enemy actors; no copy, mouth, HP, hurt, shot, combo or outcome state is seeded.
"""
from pathlib import Path
import argparse
import hashlib
import json

from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_rygar_powerups_prepare_v1 import setup as base_scene,ALLOWED

ROOT=Path(__file__).resolve().parents[2]
ROM=ROOT/'build/mega_proto_body_palette_9ea.nes'
EXPECTED='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
FAMILIES=[('Goomba','ground-charge'),('GreenKoopa','bouncing-shell'),('RedKoopa','returning-shell'),
 ('BuzzyBeetle','guard'),('HammerBro','hammer-arc'),('Bloober','upward-jet'),('GreyCheepCheep','bubble'),
 ('RedCheepCheep','wave'),('GreenParatroopaJump','high-jump'),('Lakitu','cloud-hover'),
 ('Spiny','three-needles'),('PiranhaPlant','bite'),('Podoboo','short-flame'),('BulletBill_FrenzyVar','bullet-dash')]
FORBIDDEN='KbHealth KbCopy KbMouth KbMouthCopy KbFloat KbFloatAge KbFresh KbPrevious KbInputFrame KbAction KbActionAge KbHurt KbHurtMove KbHeal KbCooldown KbShotType KbShotKind KbDropKind MkCombo MkMoveTick MkHitBits MkDamage InvAmmo InvOwnedLo InvOwnedHi InvSelected PlayerStatus PlayerSize GuestPowerupActive GuestPowerupTarget InjuryTimer GuestHurtTicks MmDeathFlag StarInvincibleTimer TimerControl AvStopwatch CheatInvincible GameTimerDisplay FrameCounter'.split()


def plans(unit,b):
    if unit.startswith('copies-'):
        start=0 if unit=='copies-low'else 7
        return [dict(name=FAMILIES[i][1],kind='copy',family=i+1,enemy=address(b,FAMILIES[i][0]),limit=430,image=True)for i in range(start,start+7)]
    common=[dict(name='real-hurt-1',kind='hurt',limit=170),dict(name='real-hurt-2',kind='hurt',limit=170),dict(name='mushroom-heal',kind='food',power=0,limit=80,image=True),dict(name='real-hurt-3',kind='hurt',limit=170),dict(name='real-hurt-4',kind='hurt',limit=170),dict(name='flower-heal',kind='food',power=1,limit=80,image=True)]
    if unit=='basics':
        return [dict(name='inhale-and-spit-star',kind='spit',limit=180,image=True)]+common+[dict(name='inflate-and-air-puff',kind='float',limit=220,image=True),dict(name='down-A-slide',kind='slide',limit=180,image=True)]
    return common+[dict(name='no-inflation-flight',kind='no-flight',limit=130)]+[dict(name=n,kind='sword',combo=i,limit=200,image=True)for i,n in enumerate(['slash','up-triple','select-lunge','air-spin','air-plunge','direction-charge'])]


def pool(q):return sum(q.get('KbShotType',i)!=0 for i in range(3))
def world(q):return q.get('Player_X_Position')+256*q.get('Player_PageLoc')


def actor(q,id,x,y=184,slot=0):
    for n,v in dict(Enemy_Flag=1,Enemy_ID=id,Enemy_State=0,Enemy_X_Position=x&255,Enemy_PageLoc=x>>8,
      Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,
      Enemy_MovingDir=2,Enemy_BoundBoxCtrl=9,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,
      MmEnemyHealthLo=0,MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0).items():q.set(n,v,slot)


def scene(q,task):
    assert pool(q)==0 and q.get('KbMouth')==0 and q.get('KbCopy')==0 and q.get('KbDropKind')==0
    base_scene(q,dict(kind='idle',face=1,hit=False))
    if task['kind']=='food':
        actor(q,0x2e,112,184,5)
        for n,v in dict(Enemy_State=128,Enemy_BoundBoxCtrl=3,PowerUpType=task['power'],InvPickupOwner=13,InvPickup=0xfc).items():q.set(n,v,5)
    elif task['kind']=='hurt':actor(q,6,116,184)


def buttons(task,stage,age,q,rec):
    if stage=='warm':return 64
    if stage=='swallow':return 4 if q.get('KbMouth')else 0
    if stage=='discard':return 32 if q.get('KbCopy')else 0
    if stage=='spit':return 64 if age>=3 and q.get('KbMouth')and not q.get('KbPrevious')&64 else 0
    if task['kind']=='copy'and stage=='use':
        if task['family']==10:return 128 if age<12 else 64 if 12<=age<42 else 0
        return 64 if age>=4 and (age<24 if task['family']==4 else rec['attack_entries']==0)else 0
    if task['kind']=='float':return 8 if age<38 else 64 if age>=42 and q.get('KbFloat')and not q.get('KbPrevious')&64 else 0
    if task['kind']=='slide':return 132 if age>=4 and not rec.get('slide_started')else 0
    if task['kind']=='no-flight':return (128 if 5<=age<16 or 25<=age<29 else 0)|(8 if 25<=age<60 else 0)
    if task['kind']=='sword':
        k=task['combo']
        started=rec['owners'].get('MkWeapons::Start',0)>0
        if k in [0,1]:return (64|(8 if k==1 else 0))if age>=5 and not started else 0
        if k==2:return 32 if age>=5 and not started else 0
        if k==3:return (128 if 5<=age<35 else 0)|(64 if age>=20 and not started else 0)
        if k==4:return (128 if 5<=age<35 else 0)|(68 if age>=25 and not started else 0)
        return (65 if age>=5 and not started else 1 if 9<=age<45 else 0)
    return 0


def target(q,task,rec):
    if rec['target']:return
    kind=task['kind'];x=y=None
    if kind=='sword':
        if q.get('KbAction')!=7 or q.get('MkCombo')!=task['combo']or q.get('MkDamage')==0 or q.get('MkMoveTick')<6:return
        x=q.get('MkRectX')+256*q.get('MkRectPage')+q.get('MkRectW')-2;y=min(192,q.get('MkRectY')-8)
    elif kind=='copy'and task['family']in [1,4,9,12,14]:
        if q.get('KbAction')!=4:return
        x=world(q)+(4 if task['family']in [4,9]else 32);y=q.get('Player_Y_Position')+8
    elif kind=='slide':
        if q.get('KbAction')!=5:return
        x=world(q)+24;y=q.get('Player_Y_Position')+8
    else:
        for i in range(3):
            if not q.get('KbShotType',i):continue
            x=q.get('KbShotX',i)+256*q.get('KbShotPage',i)+2;y=q.get('KbShotY',i)-3;break
    if x is not None and 8<=x<232 and 40<=y<=200:
        actor(q,6,x,y);rec.update(target=True,target_x=x,target_y=y)


def campaign(b,unit):
    variant=int(unit=='meta');q=Arena(b,13)
    q.put(KbVariant=variant,CrossoverBehaviorVersion=1,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('KbGlobalInit::ClearEntry')
    plan=plans(unit,b);calls=0;rows=[];rec=None;stage='init';age=0;task={};min_y=176
    names=['GameLoop','KbMovementDispatch','KbMovement','KbInputs','KbWeaponsDispatch','KbWeapons',
      'KbWeapons::Suction','KbWeapons::Capture','KbWeapons::Swallow','KbWeapons::CopyAttack','KbWeapons::Spawn',
      'KbDropCopy','KbBodyContact','KbInjuryStatus','KbInjuryStart','KbPickupDispatch','KbHealPickup',
      'MkWeapons','MkWeapons::Start','MkWeapons::Defeat','KbWeapons::Defeat','KbWeapons::BiteNext',
      'KbBodyContact::Defeat','ShellOrBlockDefeat']
    owners={(address(b,n),(location(b,n)-16)//8192):n for n in names};original=NesMPU.step
    def step(cpu):
        k=q.m.banks[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1;n=owners.get((cpu.pc,k))
        if n and rec is not None:
            rec['owners'][n]=rec['owners'].get(n,0)+1
            if n=='KbWeapons::Capture':
                assert stage=='warm'and q.get('Enemy_ID',cpu.x)==(task.get('enemy',6))
                rec['capture_entries']+=1
            elif n=='KbWeapons::Swallow':
                assert q.get('KbMouth')and q.get('KbMouthCopy')==task['family'];rec['swallows']+=1
            elif n=='KbWeapons::CopyAttack':
                assert q.get('KbCopy')==task['family'];rec['attack_entries']+=1
            elif n=='KbWeapons::Spawn':rec['spawn_requests'].add(cpu.a)
            elif n=='KbPickupDispatch':assert cpu.x==5 and q.get('PowerUpType',5)==task['power'];rec['pickup_entries']+=1
            elif n=='KbHealPickup':assert cpu.a==task['power'];rec['heal_entries']+=1
            elif n=='KbInjuryStart':rec['injury_entries']+=1
            elif n=='KbBodyContact'and task.get('family')==4 and q.get('KbAction')==4 and cpu.x==0:rec['guard_entries']+=1
            elif n=='ShellOrBlockDefeat':
                # Actual native leaf plus genuine caller stack, not intercepted.
                ret=q.m[0x100+(cpu.sp+1)%256]+256*q.m[0x100+(cpu.sp+2)%256]
                rec['defeats'].append(dict(PC=cpu.pc,bank=k,return_PC=ret+1,callerA=q.m.banks[1],object=q.get('ObjectOffset')))
        original(cpu)
    def tick(bits):
        nonlocal calls,min_y
        # Source model supplies the normal video FrameCounter progression;
        # native fixture never writes this clock or input edge state.
        q.put(FrameCounter=(q.get('FrameCounter')+1)&255,SavedJoypadBits=bits)
        q.invoke('GameLoop');calls+=1;min_y=min(min_y,q.get('Player_Y_Position'))
        assert q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8
        if variant:assert q.get('KbCopy')==q.get('KbMouth')==q.get('KbFloat')==0
        if rec is not None:
            if q.get('KbAction')==5:rec['slide_started']=True
            for i in range(3):
                if q.get('KbShotType',i):rec['shot_types'].add(q.get('KbShotType',i));rec['shot_kinds'].add(q.get('KbShotKind',i))
            rec['minimum_y']=min(rec['minimum_y'],q.get('Player_Y_Position'))
        ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
    NesMPU.step=step
    try:
        for task in plan:
            scene(q,task);stage='warm'if task['kind']in ['copy','spit']else'use';age=0;min_y=176
            rec=dict(name=task['name'],kind=task['kind'],owners={},before_hp=q.get('KbHealth'),before_food=q.get('KbFoodKind'),capture_entries=0,swallows=0,attack_entries=0,pickup_entries=0,heal_entries=0,injury_entries=0,guard_entries=0,spawn_requests=set(),shot_types=set(),shot_kinds=set(),defeats=[],target=False,minimum_y=176,transitions=[])
            rows.append(rec);stage_age=0;total=0;added=False;removed=False;hover=[];started=False
            while total<task['limit']:
                if stage=='warm'and not added and q.get('KbAction')==1 and q.get('KbActionAge')==0:
                    actor(q,task.get('enemy',6),world(q)+8,q.get('Player_Y_Position')+8);added=True
                if stage in ['use','spit']:
                    if task['kind']=='copy'and task['family']!=10 or task['kind']in ['spit','float','slide','sword']:target(q,task,rec)
                tick(buttons(task,stage,stage_age,q,rec));total+=1;stage_age+=1
                if task['kind']=='hurt':
                    if q.get('KbHealth')<rec['before_hp']:
                        assert q.get('KbHealth')==rec['before_hp']-1 and rec['injury_entries']>=1
                        if not removed:q.set('Enemy_Flag',0);removed=True
                        if q.get('KbHurt')==q.get('KbHurtMove')==q.get('InjuryTimer')==0 and q.get('Player_State')==0:break
                elif task['kind']=='food':
                    if stage_age>=25:
                        assert rec['pickup_entries']==rec['heal_entries']==1 and q.get('Enemy_Flag',5)==0
                        assert q.get('KbHealth')==min(6,rec['before_hp']+2)and q.get('KbFoodKind')==rec['before_food']^1;break
                elif stage=='warm'and q.get('KbMouth'):
                    assert rec['capture_entries']==1 and q.get('KbMouth')==task.get('enemy',6)+1 and q.get('KbCopy')==0 and q.get('Enemy_Flag')==0
                    stage='swallow'if task['kind']=='copy'else'spit';stage_age=0;rec['transitions'].append(stage)
                elif stage=='swallow'and stage_age>=28:
                    assert q.get('KbCopy')==task['family']and q.get('KbMouth')==0 and rec['swallows']==1
                    stage='use';stage_age=0;rec['transitions'].append(stage)
                elif stage in ['use','spit']:
                    if task['kind']=='copy'and task['family']==4 and rec['guard_entries']>0 and stage_age>=18 and not rec.get('guard_protected'):
                        assert q.get('KbHealth')==rec['before_hp']and q.get('Enemy_Flag')==1,(task,stage_age,rec,q.get('KbHealth'),q.get('Enemy_Flag'),q.get('Enemy_State'),q.get('KbCopy'),q.get('KbAction'))
                        q.set('Enemy_Flag',0);rec['guard_protected']=True
                    if task['kind']=='copy'and task['family']==10 and 18<=stage_age<=38:
                        assert q.get('KbAction')==4 and q.get('MmVY',1)==q.get('MmVY',2)==0;hover.append(q.get('Player_Y_Position'))
                    if task['kind']=='no-flight'and stage_age>=110:
                        assert rec['minimum_y']<=112;break
                    if stage_age>=110 and pool(q)==0 and q.get('Player_State')==0 and q.get('KbAction')==0:
                        if task['kind']=='copy':
                            assert rec['attack_entries']>0
                            if task['family']==4:assert rec.get('guard_protected')
                            elif task['family']==10:assert len(hover)>=16 and max(hover)-min(hover)<=3
                            else:assert rec['target']and rec['defeats'],('Native copy target',task,rec)
                            assert q.get('KbHealth')==rec['before_hp']
                            stage='discard';stage_age=0;rec['transitions'].append(stage)
                        else:
                            assert rec['target']and rec['defeats'],('Native basic/sword target',task,rec)
                            if task['kind']=='float':assert 2 in rec['shot_types']
                            if task['kind']=='spit':assert 1 in rec['shot_types']and q.get('KbMouth')==0
                            if task['kind']=='sword':assert rec['owners'].get('MkWeapons::Start')and rec['owners'].get('MkWeapons::Defeat')
                            assert q.get('KbHealth')==rec['before_hp'];break
                elif stage=='discard':
                    if stage_age==5:assert q.get('KbCopy')==0 and q.get('KbDropKind')==task['family']
                    if stage_age>=260:
                        assert q.get('KbCopy')==q.get('KbMouth')==q.get('KbDropKind')==0;break
            else:raise AssertionError(('Bounded source stage',task,stage,stage_age,rec,q.get('KbAction'),q.get('Player_State'),q.get('KbCopy'),q.get('KbMouth'),q.get('KbHealth')))
            rec.update(updates=total,after_hp=q.get('KbHealth'),after_food=q.get('KbFoodKind'),ending_copy=q.get('KbCopy'),ending_mouth=q.get('KbMouth'),ending_pool=pool(q))
            for n in ['spawn_requests','shot_types','shot_kinds']:rec[n]=sorted(rec[n])
            assert q.get('KbCopy')==q.get('KbMouth')==q.get('KbDropKind')==0
    finally:NesMPU.step=original
    assert calls<=3000,('Finite source unit',calls)
    return dict(passed=True,native_run=False,source_CPU_only=True,ROM_sha256=EXPECTED,unit=unit,variant=variant,mode=1,GameLoop_calls=calls,plan=plan,cases=rows,
      setup='Complete legal map/position/velocity/NPC or mature mushroom/flower only. All copy acquisition is actual warmed inhale/capture/Down. All health deficits actual injury; no tested resource/ability/edge/outcome state seeded. Source clock399 and incrementing FrameCounter model normal video environment, never native fixture writes.',
      limits='Not Lua/native/PPU/cadence/audio proof. Appropriate enemies staged inside real active mouth before their normal AI update; no Stopwatch/forcedfreeze or RNG claim. No native natural emergence/full route/allpixel claim.')


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--unit',choices=['basics','copies-low','copies-high','meta'],required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
    assert hashlib.sha256(ROM.read_bytes()).hexdigest()==EXPECTED
    z=campaign(scoped_load(ROM),a.unit);a.output.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,path=str(a.output),unit=a.unit,calls=z['GameLoop_calls'],cases=len(z['cases']))))

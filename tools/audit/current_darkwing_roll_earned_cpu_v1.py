"""Finite real GameLoop acquisition/actions; legal actor scenes, no resource seeds."""
from pathlib import Path
import json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_rygar_powerups_prepare_v1 import ALLOWED as BASE_ALLOWED,setup as base_scene

R=Path(__file__).resolve().parents[2];B=R/'build'
EXPECTED='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
EXTRA_DROP='InvDropX InvDropPage InvDropY InvDropVY InvDropVYMid InvDropVYHi InvDropFraction InvDropFractionHi InvDropAge InvDropAgeHi AvDropItem'.split()
ALLOWED=BASE_ALLOWED+EXTRA_DROP
FORBIDDEN='DwHealth DwGas DwAdaptor DwMode RlHealth RlEnergy RlReady RlFoodKind RlCharge RlChargeFired RlInvul RlHurt InvOwnedLo InvOwnedHi InvSelected InvAmmo PlayerStatus PlayerSize GuestPowerupActive GuestPowerupTarget RgShotType MmBulletType InjuryTimer GuestHurtTicks MmDeathFlag CheatInvincible GameTimerDisplay PseudoRandomBitReg'.split()

def plans(identity):
    if identity=='darkwing':
        return [dict(name='cold-basic',kind='use',weapon=0,mode=0,proxy=1,contact=1,limit=420,image=True),
          dict(name='hurt-for-small-aid',kind='hurt',limit=140),dict(name='small-aid',kind='collect',item=0x22,limit=80,image=True),
          dict(name='hurt-for-full-aid',kind='hurt',limit=140),dict(name='full-aid',kind='collect',item=0x23,limit=80,image=True),
          dict(name='small-gas',kind='collect',item=0x25,limit=80),dict(name='large-gas',kind='collect',item=0x24,limit=80,image=True),
          dict(name='earn-arrow',kind='collect',item=0x26,limit=80),dict(name='arrow',kind='use',weapon=2,mode=1,proxy=3,contact=5,limit=420,image=True),
          dict(name='earn-heavy',kind='collect',item=0x27,limit=80),dict(name='heavy',kind='use',weapon=1,mode=1,proxy=2,contact=4,limit=420,image=True),
          dict(name='earn-thunder',kind='collect',item=0x28,limit=80),dict(name='thunder',kind='use',weapon=3,mode=1,proxy=1,contact=7,limit=420,image=True),
          dict(name='select-back-to-basic',kind='use',weapon=0,mode=0,proxy=1,contact=1,limit=420,image=True)]
    return [dict(name='cold-buster',kind='use',charges=0,proxy=1,contact=1,limit=250,image=True),
      dict(name='autocharge',kind='use',charges=1,proxy=3,contact=3,limit=320,image=True),
      dict(name='hurt-before-mushroom',kind='hurt',limit=140),dict(name='mushroom-full-restore',kind='collect',item=0xfc,power=0,limit=80,image=True),
      dict(name='three-earned-energy-debits',kind='use',charges=3,proxy=3,contact=3,limit=420),
      dict(name='small-energy',kind='capsule',drop=1,health=False,limit=80,image=True),dict(name='large-energy',kind='capsule',drop=2,health=False,limit=80,image=True),
      dict(name='hurt-before-small-health',kind='hurt',limit=140),dict(name='small-health',kind='capsule',drop=1,health=True,limit=80,image=True),
      dict(name='hurt-for-large-health-1',kind='hurt',limit=140),dict(name='hurt-for-large-health-2',kind='hurt',limit=140),
      dict(name='large-health',kind='capsule',drop=2,health=True,limit=80,image=True),
      dict(name='hurt-before-flower',kind='hurt',limit=140),dict(name='spend-before-flower',kind='use',charges=1,proxy=3,contact=3,limit=320),
      dict(name='flower-full-restore',kind='collect',item=0xfc,power=1,limit=80,image=True),
      dict(name='select-is-not-Bass-inventory',kind='select-no-inventory',limit=40)]

def pool(q,identity):return sum(bool(q.get('RgShotType'if identity=='darkwing' else'MmBulletType',i))for i in range(10 if identity=='darkwing'else 4))

def snapshot(q):return {n:q.get(n)for n in ['DwHealth','DwGas','DwAdaptor','DwMode','RlHealth','RlEnergy','RlFoodKind','RlChargeFired','PlayerStatus']}

def setup(q,identity,task):
    assert pool(q,identity)==0
    base_scene(q,dict(kind='idle',face=1,hit=False))
    if task['kind']=='collect':
        for n,v in dict(Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,Enemy_BoundBoxCtrl=3,
            Enemy_X_Position=112,Enemy_PageLoc=0,Enemy_Y_Position=184,Enemy_Y_HighPos=1,
            Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_SprAttrib=0,PowerUpType=task.get('power',1),
            InvPickupOwner=12 if identity=='darkwing'else 9,InvPickup=task['item']).items():q.set(n,v,5)
    elif task['kind']=='hurt':enemy(q,116,184,2)
    elif task['kind']=='capsule':
        fields=dict(InvDropKind=task['drop'],InvDropX=120,InvDropPage=0,InvDropY=192,
          InvDropVY=0,InvDropVYMid=0,InvDropVYHi=0,InvDropFraction=0,InvDropFractionHi=0,
          InvDropAge=0,InvDropAgeHi=0,AvDropItem=128 if task['health']else 0)
        for n,v in fields.items():q.set(n,v,0)
    elif identity=='darkwing'and task.get('weapon')==2:
        # Native Arrow face at208/Y193, well ahead of the player; no player overlap.
        q.set('Block_Buffer_1',0x54,10*16+13)

def enemy(q,x,y,direction=1):
    for n,v in dict(Enemy_Flag=1,Enemy_ID=6,Enemy_State=0,Enemy_X_Position=x,Enemy_PageLoc=0,
      Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,
      Enemy_MovingDir=direction,Enemy_BoundBoxCtrl=9,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,
      MmEnemyHealthLo=0,MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0).items():q.set(n,v,0)

def place_target(q,identity,task):
    if identity=='darkwing':
        for i in (range(9,-1,-1)if task['weapon']==3 else range(10)):
            if q.get('RgShotType',i)!=task['contact']:continue
            if task['weapon']==3 and q.get('RgShotVYHi',i)<128:continue
            x,y,page=q.get('RgShotX',i),q.get('RgShotY',i),q.get('RgShotPage',i)
            if page==0 and x>=152 and x<224 and 48<=y<216:
                enemy(q,x-6,y-(12 if task['weapon']==3 else 8));return True
    else:
        for i in range(4):
            if q.get('MmBulletType',i)!=task['contact']:continue
            x,y,page=q.get('MmBulletX',i),q.get('MmBulletY',i),q.get('MmBulletPage',i)
            if page==0 and 152<=x<224 and 48<=y<216:
                enemy(q,x-6,y-8);return True
    return False

def expected_collect(before,identity,task):
    result=dict(before)
    if identity=='darkwing':
        item=task['item']
        if item==0x22:result['DwHealth']=min(4,before['DwHealth']+1)
        elif item==0x23:result['DwHealth']=4
        else:
            if item>=0x26:result['DwAdaptor']={0x26:2,0x27:1,0x28:3}[item]
            result['DwGas']=min(99,before['DwGas']+(1 if item==0x25 else 10))
    else:result.update(RlHealth=28,RlEnergy=28,RlFoodKind=1,PlayerStatus=1)
    return result

def campaign(b,identity):
    char=12 if identity=='darkwing'else 9;q=Arena(b,char)
    q.put(**{('DarkwingVariant'if identity=='darkwing'else'RlVariant'):1})
    q.put(CrossoverBehaviorVersion=1,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('DwInventoryInit')
    plan=plans(identity);rows=[];calls=0;case=None;pending=None;refill_pending=None;stage_age=0
    names=['GameLoop','HpProcessFireballsBridge','ProcFireball_Bubble','RlWeaponsDispatch','RlMovementDispatch',
      'RlCollectDispatch','MarioSourcePowerupCollision','RlInjuryDispatch','GuestInjuryStatus',
      'DwScroogeWeapons','DwScroogeMovement','DwLaunch','DwShotInit','DwCollectPickup','DwGiveItem',
      'DwInjuryStatus','DwInjuryStart','DwHeavyBurst','DwAttachArrow','DwArrowActor','DwExpandedEnemyHit',
      'RlWeapons','RlWeapons::Spawn','RlWeapons::ResetCharge','RlInjury','RlCollect','RlRefillDispatch',
      'InventoryUpdateDrops','MegaManWeapons::DamageEnemy','RlUi','DwHud','LmCollectGate','Cv3CollectPickupGate','Z2CollectPickupGate',
      'RlRefillDispatch::EnergySave','RlRefillDispatch::HealthSave']
    owners={(address(b,n),(location(b,n)-16)//8192):n for n in names};original=NesMPU.step
    def step(cpu):
        nonlocal pending,refill_pending
        k=q.m.banks[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else -1;n=owners.get((cpu.pc,k))
        if n:
            if n not in case['owners']:case['owners'].append(n)
            if n=='MarioSourcePowerupCollision':case['physical_collision']+=1;assert cpu.x==5
            elif n in ['DwCollectPickup','RlCollect']and task['kind']=='collect':
                assert cpu.x==5 and q.get('Enemy_Flag',5)==q.get('Enemy_State',5)==0
                case['collect_owner']+=1
            elif n=='DwGiveItem'and task['kind']=='collect':assert cpu.a==task['item'];case['reward']+=1
            elif n=='DwLaunch'and task['kind']=='use':pending=dict(before=q.get('DwGas'),kind=task['weapon'])
            elif n=='DwShotInit'and task['kind']=='use':
                assert pending and q.get('RgTemp')==pending['kind'];cost=[0,2,3,2][pending['kind']]
                assert q.get('DwGas')==pending['before']-cost
                case['debits'].append(dict(before=pending['before'],cost=cost,after=q.get('DwGas'),age=stage_age));pending=None
            elif n=='RlWeapons::Spawn'and task['kind']=='use'and cpu.a==3:
                pending=dict(before=q.get('RlEnergy'),fired=q.get('RlChargeFired'))
            elif n=='RlWeapons::ResetCharge'and pending and identity=='roll':
                assert q.get('RlEnergy')==pending['before']-4 and q.get('RlChargeFired')==pending['fired']+1
                case['debits'].append(dict(before=pending['before'],cost=4,after=q.get('RlEnergy'),age=stage_age));pending=None
            elif n=='RlRefillDispatch'and identity=='roll':
                assert refill_pending is None and cpu.a in [8,40]
                health=bool(q.get('AvDropItem',q.get('InvDropSlot'))&128)
                refill_pending=dict(health=health,before=q.get('RlHealth'if health else'RlEnergy'),amount=cpu.a//4,request=cpu.a)
                if task['kind']=='capsule':
                    assert cpu.a==(8 if task['drop']==1 else 40)and health==task['health'];case['refills']+=1
            elif n in ['RlRefillDispatch::EnergySave','RlRefillDispatch::HealthSave']and identity=='roll':
                assert refill_pending and refill_pending['health']==(n.endswith('HealthSave'))
                assert cpu.a==min(28,refill_pending['before']+refill_pending['amount'])
                refill_pending.update(after=cpu.a,delta=cpu.a-refill_pending['before'],PC=cpu.pc,bank=k)
                case['credits'].append(refill_pending);refill_pending=None
            elif n=='MegaManWeapons::DamageEnemy'and task['kind']=='use':
                assert cpu.x==0 and q.get('MmBulletType',q.get('MmSlot')if identity=='roll'else 0)==task['proxy'];case['contacts']+=1
        original(cpu)
    def tick(bits=0):
        nonlocal calls
        q.put(SavedJoypadBits=bits);_,writes=q.invoke('GameLoop');calls+=1
        assert refill_pending is None,'Complete native refill writer returned'
        assert q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8,(identity,task['name'],stage_age,'death')
        for w in writes:
            if w['address']in[address(b,'MmEnemyHealthLo'),address(b,'MmEnemyHealthHi')]:case['HP_writes']+=1
            if address(b,'RgShotType')<=w['address']<address(b,'RgShotType')+10 and w['value']:case['shot_types'].add(w['value'])
            if address(b,'MmBulletType')<=w['address']<address(b,'MmBulletType')+4 and w['value']:case['bullet_types'].add(w['value'])
        ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0)
        q.invoke('SamusFreezeUpdateScreen');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
    NesMPU.step=step
    try:
        # Real movement/Ensure owns initialRoll28/28, not this setup.
        task=dict(name='cold-initialization',kind='idle');case=dict(owners=[],physical_collision=0,collect_owner=0,reward=0,debits=[],credits=[],contacts=0,refills=0,HP_writes=0,shot_types=set(),bullet_types=set())
        setup(q,identity,task)
        for stage_age in range(3):tick()
        cold=snapshot(q);assert (cold['DwHealth'],cold['DwGas'],cold['DwAdaptor'],cold['DwMode'])==(4,0,0,0)if identity=='darkwing'else(cold['RlHealth'],cold['RlEnergy'])==(28,28)
        init_owners=case['owners']
        for task in plan:
            setup(q,identity,task);before=snapshot(q);pending=None
            case=dict(name=task['name'],kind=task['kind'],before=before,owners=[],physical_collision=0,collect_owner=0,reward=0,debits=[],credits=[],contacts=0,refills=0,HP_writes=0,shot_types=set(),bullet_types=set(),target=False)
            rows.append(case)
            if identity=='darkwing'and task['kind']=='use':
                for stage_age in range(32):
                    if q.get('DwMode')==task['mode']:break
                    tick(32 if stage_age%8 in [2,3]else 0)
                assert q.get('DwMode')==task['mode'],'ActualSelect may only select carried adaptor'
            for stage_age in range(task['limit']):
                if task['kind']=='use'and not case['target']:case['target']=place_target(q,identity,task)
                if identity=='darkwing':bits=64 if task['kind']=='use'and 5<=stage_age<8 else 0
                else:
                    firing=task['kind']=='use'and stage_age>=5 and(len(case['debits'])<task.get('charges',0)if task.get('charges',0)else stage_age<8)
                    bits=64 if firing else 0
                    if task['kind']=='select-no-inventory':bits=32 if stage_age%8 in[2,3]else 0
                tick(bits)
                if task['kind']=='hurt':
                    hp='DwHealth'if identity=='darkwing'else'RlHealth';damage=1 if identity=='darkwing'else 4
                    if q.get(hp)<before[hp]:
                        assert q.get(hp)==before[hp]-damage
                        q.set('Enemy_Flag',0,0)
                        ready=q.get('InjuryTimer')==0 and(q.get('RgBillBurst')==q.get('RgBillBurstDelay')==0 if identity=='darkwing'else q.get('RlInvul')==q.get('RlHurt')==0)
                        if ready:break
                elif task['kind']=='collect':
                    if stage_age>=24:
                        assert case['physical_collision']==case['collect_owner']==1
                        after=snapshot(q);want=expected_collect(before,identity,task)
                        assert all(after[n]==v for n,v in want.items()),(task,after,want)
                        if identity=='darkwing':assert case['reward']==1
                        break
                elif task['kind']=='capsule':
                    if stage_age>=24:
                        assert case['refills']==1 and q.get('InvDropKind',0)==0
                        meter='RlHealth'if task['health']else'RlEnergy';amount=2 if task['drop']==1 else 10
                        assert q.get(meter)==min(28,before[meter]+amount),(task,snapshot(q))
                        break
                elif task['kind']=='use':
                    enough=len(case['debits'])==(1 if identity=='darkwing'else task['charges'])
                    if stage_age>=210 and enough and case['target']and case['contacts']and not pool(q,identity):
                        assert case['HP_writes']>0
                        if identity=='roll':
                            gained=sum(c['delta']for c in case['credits']if not c['health'])
                            assert q.get('RlEnergy')==before['RlEnergy']-4*task['charges']+gained
                        if identity=='darkwing'and task['weapon']==1:assert {3,4}<=case['shot_types']
                        if identity=='darkwing'and task['weapon']==2:assert {8,5,6}<=case['shot_types']
                        if identity=='darkwing'and task['weapon']==3:assert {8,7}<=case['shot_types']
                        break
                elif stage_age>=24:
                    assert q.get('InvSelected',9)==0 and q.get('RlVariant')==1 and not pool(q,identity);break
            else:raise AssertionError((identity,task['name'],'bounded source stage did not complete',case,snapshot(q),[(q.get('RgShotType',i),q.get('RgShotX',i),q.get('RgShotY',i))for i in range(10)]))
            assert pending is None
            case.update(updates=stage_age+1,after=snapshot(q),shot_types=sorted(case['shot_types']),bullet_types=sorted(case['bullet_types']))
    finally:NesMPU.step=original
    assert calls<=3000
    return dict(passed=True,source_CPU_only=True,native_run=False,ROM_sha256=EXPECTED,identity=identity,character=char,mode=1,
      initial_actual=cold,initial_GameLoop_owners=init_owners,GameLoop_calls=calls,plan=plan,cases=rows,
      setup='CPU arena normal initializedclock399 only; native module must not write clock. Same legal logical/visible scene, mature typedactors or complete Rollcapsule metadata; only real source hurt/debit produces tested health/energy deficits.',
      consumer='Actual SamusFreezeUpdateScreen between completeGameLoops followed by two originalInitBuffer zero stores; source CPU environment, not NMI/budget proof.',
      limits='Not native/Lua execution/art/PPU/cadence/audio proof. Mature actor contact, not reveal/rise/RNG; no health/ammo/ownership/adaptor/selection/outcome seeds.')

if __name__=='__main__':
    import argparse,hashlib
    ap=argparse.ArgumentParser();ap.add_argument('--identity',choices=['darkwing','roll'],required=True);a=ap.parse_args()
    rom=B/'mega_proto_body_palette_9ea.nes';assert hashlib.sha256(rom.read_bytes()).hexdigest()==EXPECTED
    result=campaign(scoped_load(rom),a.identity);out=B/('current-ab221e-'+a.identity+'-earned-source-v1.json');assert not out.exists()
    out.write_text(json.dumps(result,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,identity=a.identity,calls=result['GameLoop_calls'],cases=len(result['cases']),path=str(out))))

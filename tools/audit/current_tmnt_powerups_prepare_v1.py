"""Prepare earned TMNT components on frozen9ea; source CPU only, never Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU
from observe_chip_committed_write import lua

EXPECTED = '9ea11eab2fc5c373a3795b013f6ed9e0d5e9781891b2ae3bf40ad2556c27b85e'
VARIANTS = dict(leonardo=0, raphael=1, michelangelo=2, donatello=3)
PLAN = [dict(name='cold-primary-right',kind='primary',health=128,face=1,limit=120,picture='01-primary.png'),
        dict(name='full-health-mushroom-cap',kind='food',health=128,pickup=0,heal=32,limit=80),
        dict(name='earn32HP-deficit',kind='contact',health=128,hits=2,limit=700),
        dict(name='mushroom-restores32',kind='food',health=96,pickup=0,heal=32,limit=80,picture='02-mushroom.png'),
        dict(name='earn64HP-deficit',kind='contact',health=128,hits=4,limit=1300),
        dict(name='flower-restores64',kind='food',health=64,pickup=1,heal=64,limit=80,picture='03-flower.png'),
        dict(name='full-health-flower-Kiai',kind='kiai',health=128,pickup=1,limit=80,picture='04-kiai-pickup.png'),
        dict(name='Kiai-native-volley',kind='weapon',health=128,gear=4,face=1,limit=180),
        dict(name='single-shuriken-earned-refill-cap',kind='gear',health=128,gear=1,count=6,stock=99,limit=100),
        dict(name='Select-primary-gear-toggle',kind='select',health=128,limit=60),
        dict(name='single-shuriken-left',kind='weapon',health=128,gear=1,face=2,limit=180,picture='05-shuriken.png'),
        dict(name='triple-shuriken-replacement-refill',kind='gear',health=128,gear=2,count=2,stock=40,limit=80),
        dict(name='triple-shuriken-one-debit',kind='weapon',health=128,gear=2,face=1,limit=180,picture='06-triple.png'),
        dict(name='boomerang-replacement-refill',kind='gear',health=128,gear=3,count=2,stock=40,limit=80),
        dict(name='boomerang-left-hit-catch-refund',kind='weapon',health=128,gear=3,face=2,limit=240,picture='07-boomerang.png',catch_picture='08-catch.png')]
ALLOWED = '''Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits
Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce TnVXHi TnVXLo TnVYHi TnVYLo TnXFraction TnYFraction
ScrollThirtyTwo AreaParserTaskNum ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc
Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits
Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_Y_MoveForce Enemy_MovingDir Enemy_SprAttrib EnemyOffscrBitsMasked
PowerUpType InvPickupOwner InvPickup TnPickupStamp TnDropKind TnDropX TnDropPage TnDropY TnDropTimer'''.split()
RESOURCE_BANS = '''PlayerStatus PlayerSize TnHealth TnEquipment TnAmmo TnFood TnMarker TnLife TnVariant TnDropCounter TnGearSelected TnAttack TnThrow TnHurt TnHurtMove TnShotKind TnEnemyHP TnEnemyType TnEnemyHurt TnDropReceipt InjuryTimer InvOwnedLo InvOwnedHi InvAmmo InvSelected PseudoRandomBitReg CheatInvincible MmDeathFlag GuestPowerupActive'''.split()
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
put = lambda p,z: p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')


def scene(q, task):
    assert all(q.get('TnShotKind',i)==0 for i in range(3))
    assert all(q.get(n)==0 for n in ['TnAttack','TnThrow','TnHurt','InjuryTimer','Player_State'])
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for page in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',0x54,page*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    q.put(Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,
          Player_State=0,PlayerFacingDir=task.get('face',1),Player_MovingDir=task.get('face',1),
          Player_CollisionBits=255,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,
          ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,ScrollLock=1,ScrollThirtyTwo=0,AreaParserTaskNum=0)
    for n in ['Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce',
              'TnVXHi','TnVXLo','TnVYHi','TnVYLo','TnXFraction','TnYFraction']:q.set(n,0)


def actor(q,x,y,kind,slot):
    for n,v in dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=128 if kind==0x2e else 0,
                    Enemy_BoundBoxCtrl=3 if kind==0x2e else 9,Enemy_X_Position=x,
                    Enemy_PageLoc=0,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,
                    Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1,
                    Enemy_SprAttrib=0,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0).items():q.set(n,v,slot)


def target(q,task,contact=False):
    x,y=(112,184) if contact else (140 if task.get('face',1)==1 else 88,168)
    if not contact:
        for col in range(x//16,(x+16)//16+1):q.set('Block_Buffer_1',0x54,160+col)
    actor(q,x,y,6,0)


def pickup(q,task):
    actor(q,112,184,0x2e,5)
    for n,v in dict(PowerUpType=task['pickup'],InvPickupOwner=19,
                    InvPickup=0xb4 if task['kind']=='kiai' else 0xfc,
                    TnPickupStamp=4 if task['kind']=='kiai' else 0).items():q.set(n,v,5)
    q.invoke('TnPreparePickupDispatch',x=5)
    assert q.get('InvPickup',5)==(0xb4 if task['kind']=='kiai' else 0xfc)
    assert q.get('TnPickupStamp',5)==(4 if task['kind']=='kiai' else 0)


def drop(q,kind):
    assert q.get('TnDropKind',0)==0
    for n,v in dict(TnDropKind=kind,TnDropX=120,TnDropPage=0,TnDropY=184,TnDropTimer=120).items():q.set(n,v,0)


def campaign(b,variant,mode):
    q=Arena(b,19)
    q.put(TnVariant=variant,CrossoverBehaviorVersion=mode,OperMode_Task=3,AreaType=1,
          PlayerStatus=0,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,
          Player_State=0,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,
          ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,Player_CollisionBits=255,Player_MovingDir=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('CrossoverGraphicsBank')
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for p in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,p*208+row*16+col)
    stepno=0
    def main(buttons=0):
        nonlocal stepno
        q.put(SavedJoypadBits=buttons,FrameCounter=stepno%256);stepno+=1
        return q.invoke('GameLoop')
    for _ in range(30):main()
    assert [q.get('TnHealth',i)for i in range(4)]==[128]*4
    assert all(q.get(n,i)==0 for n in ['TnEquipment','TnAmmo'] for i in range(4))
    rec=None;age=0;original=NesMPU.step
    names=['TnPickupDispatch','TnGiveEquipment','TnInjuryStart','TnWeapons::Normal','TnShotEnemies::Ordinary','TnRestoreBoomerang']
    owners={(address(b,n),(location(b,n)-16)//8192):n for n in names}
    def step(c):
        bank=q.m.banks[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1
        name=owners.get((c.pc,bank))
        if rec is not None and name:
            rec['owners'][name]=rec['owners'].get(name,0)+1
            if name=='TnGiveEquipment':
                kind=4 if task['kind']=='kiai' else task['gear']
                assert c.a==kind
                rec['expected_grant']=min(q.get('TnAmmo',variant)+20,99) if q.get('TnEquipment',variant)==kind else 20
                rec['grants']+=1
            elif name=='TnInjuryStart' and q.get('TnHurt')==0:
                assert task['kind']=='contact';rec['expected_hit']=q.get('TnHealth',variant)-16
            elif name in ['TnWeapons::Normal','TnShotEnemies::Ordinary']:
                assert c.x==0 and q.get('TnEnemyHP',0)>0;rec['contacts']+=1
            elif name=='TnRestoreBoomerang':rec['refunds']+=1
        original(c)
    NesMPU.step=step
    results=[]
    try:
        for task in PLAN:
            assert q.get('TnHealth',variant)==task['health'],(task['name'],'earnedHP',q.get('TnHealth',variant))
            scene(q,task)
            if task['kind'] in ['primary','weapon']:target(q,task)
            elif task['kind']=='contact':target(q,task,True)
            elif task['kind'] in ['food','kiai']:pickup(q,task)
            elif task['kind']=='gear':drop(q,task['gear'])
            rec=dict(name=task['name'],owners={},grants=0,contacts=0,refunds=0,hits=0,spawns=0,debits=0,toggles=0)
            health0=q.get('TnHealth',variant);food0=q.get('TnFood');ammo0=q.get('TnAmmo',variant)
            lastSelected=q.get('TnGearSelected');lastAmmo=ammo0;remove=False;rearm=False
            for age in range(1,task['limit']+1):
                if remove:q.set('Enemy_Flag',0,0);q.set('Enemy_CollisionBits',0,0);remove=False
                quiet=all(q.get(n)==0 for n in ['TnAttack','TnThrow','TnHurt','InjuryTimer','Player_State'])and all(q.get('TnShotKind',i)==0 for i in range(3))
                if rearm and quiet:scene(q,task);target(q,task,True);rearm=False
                buttons=64 if task['kind'] in ['primary','weapon']and 8<=age<12 else 32 if task['kind']=='select'and(5<=age<9 or 16<=age<20)else 0
                _,writes=main(buttons)
                for w in writes:
                    if address(b,'TnShotKind')<=w['address']<address(b,'TnShotKind')+3 and w['value']!=0:rec['spawns']+=1
                    if w['address']==address(b,'TnAmmo')+variant:
                        if task['kind']=='weapon'and w['value']==lastAmmo-1:rec['debits']+=1
                        lastAmmo=w['value']
                if 'expected_hit'in rec:
                    assert q.get('TnHealth',variant)==rec.pop('expected_hit')and q.get('TnHurt')and q.get('InjuryTimer')
                    rec['hits']+=1;remove=True;rearm=rec['hits']<task['hits']
                if 'expected_grant'in rec:
                    assert q.get('TnAmmo',variant)==rec.pop('expected_grant')
                    if task['kind']=='gear'and rec['grants']<task['count']:drop(q,task['gear'])
                assert q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8
                for i in range(4):
                    if i!=variant:assert q.get('TnHealth',i)==128 and q.get('TnAmmo',i)==q.get('TnEquipment',i)==0
                quiet=all(q.get(n)==0 for n in ['TnAttack','TnThrow','TnHurt','InjuryTimer','Player_State'])and all(q.get('TnShotKind',i)==0 for i in range(3))
                if rec['contacts']>0 and q.get('Enemy_State',0)&32:rec['defeat_seen']=True
                kind=task['kind'];complete=False
                if kind=='food'and rec['owners'].get('TnPickupDispatch',0):
                    assert q.get('Enemy_Flag',5)==0 and q.get('TnHealth',variant)==min(health0+task['heal'],128)and q.get('TnFood')==1-food0
                    complete=age>=8
                elif kind=='kiai'and rec['grants']==1:
                    assert q.get('TnEquipment',variant)==4 and q.get('TnAmmo',variant)==20 and q.get('Enemy_Flag',5)==0
                    complete=age>=8
                elif kind=='contact':complete=rec['hits']==task['hits']and not remove and quiet
                elif kind=='gear':complete=rec['grants']==task['count']and q.get('TnDropKind',0)==0
                elif kind=='select':
                    sel=q.get('TnGearSelected')
                    if sel!=lastSelected:rec['toggles']+=1;lastSelected=sel
                    if age>=26:assert rec['toggles']==2 and sel==1;complete=True
                elif kind in ['primary','weapon']and age>=35 and quiet:
                    assert rec['contacts']==1 and rec.get('defeat_seen'),(task['name'],rec,age,q.get('Enemy_State',0),q.get('TnEnemyHP',0))
                    if kind=='weapon':
                        assert rec['spawns']==(3 if task['gear']==2 else 1)and rec['debits']==1 and rec['refunds']==int(task['gear']==3),(task,rec)
                        assert q.get('TnAmmo',variant)==ammo0-1+rec['refunds']
                    complete=True
                if complete:break
            else:raise AssertionError(('finite CPU component limit',task,rec,age,[q.get(n)for n in ['TnHurt','InjuryTimer','Player_State','TnAttack','TnThrow']]))
            if task['kind']=='gear':assert q.get('TnAmmo',variant)==task['stock']
            rec.update(GameLoop_calls=age,health_after=q.get('TnHealth',variant),gear_after=q.get('TnEquipment',variant),ammo_after=q.get('TnAmmo',variant))
            results.append(rec)
    finally:NesMPU.step=original
    return dict(passed=True,variant=variant,mode=mode,full_GameLoop_calls=stepno,cases=results,
                scope='Typed logical actors/map/motion, external CPU FrameCounter clock and cold variant configuration. No player health/gear/ammo/timer/attack/projectile/RNG outcomes written after actual source initialization. No native/PPU/interrupt/audio or natural drop eligibility claim.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--identity',choices=VARIANTS,required=True)
    ap.add_argument('--mode',choices=['easy','hard'],default='hard')
    ap.add_argument('--rom',type=Path,default=R/'build/bill_early_cache.nes')
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();rom=a.rom.resolve();out=a.output.resolve();variant=VARIANTS[a.identity];mode=int(a.mode=='hard')
    assert sha(rom)==EXPECTED and out.is_relative_to((R/'build').resolve())
    assert not out.exists() or all(p.name.startswith('source-first-failure') for p in out.iterdir()),'Only reuse this unbound source draft; never a frozen packet'
    b=scoped_load(rom);fixture=R/'tests/current-tmnt-powerups.lua';text=fixture.read_text()
    baseline=R/'tools/audit/current_pit_powerups_v3.lua';old=baseline.read_text()
    begin='-- All callback registration is startup-static.';end="emu.addEventCallback(function()\n if not entered"
    assert text[text.index(begin):text.index(end)]==old[old.index(begin):old.index(end)]
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and 'dofile('not in text
    assert not set(ALLOWED)&set(RESOURCE_BANS)
    names=set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))|set(ALLOWED)
    names|=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))&set(b['syms'])
    ram={n:address(b,n)for n in names}
    assert all(isinstance(ram[n],int)for n in names),'No nil callback ranges, including every bare C.ram reference'
    def hook(n,delta=0,size=3):
        off=location(b,n)+delta;pc=address(b,n)+delta;bank=(off-16)//8192;bs=list(b['raw'][off:off+size]);banks=[bank]
        if bank==127:
            assert list(b['raw'][16+125*8192+(off-16)%8192:16+125*8192+(off-16)%8192+size])==bs;banks=[125,127]
        return dict(pc=pc,banks=banks,bytes=bs,source_symbol=n,source_delta=delta)
    hooks={k:hook(n)for k,n in dict(PhysicalPickup='TnPickupDispatch',GiveEquipment='TnGiveEquipment',InjuryStart='TnInjuryStart',PrimaryDefeat='TnWeapons::Normal',ShotDefeat='TnShotEnemies::Ordinary',BoomRefund='TnRestoreBoomerang',NmiEntry='NonMaskableInterrupt',IrqEntry='IrqScrollSplit').items()}
    off=location(b,'GameLoop');nd=address(b,'NmiDisable')
    assert b['raw'][off:off+5]==bytes([169,255,141,nd&255,nd>>8]);hooks['GameLoopOwned']=hook('GameLoop',5)
    for key,n,op in [('GameLoopFinish','GameLoop',96),('NmiReturn','NonMaskableInterrupt',64),('IrqReturn','IrqScrollSplit',64)]:
        d=int(b['syms'][n]['size'],0)-1;assert b['raw'][location(b,n)+d]==op;hooks[key]=hook(n,d,1)
    off=location(b,'PostDmaMaskEnable');mirror=address(b,'Mirror_PPUMASK');load=bytes([165,mirror])if mirror<256 else bytes([173,mirror&255,mirror>>8])
    assert b['raw'][off-3:off]==b'\x8d\x14\x40'and b['raw'][off:off+len(load)+3]==load+b'\x8d\x01\x20';hooks['DmaComplete']=hook('PostDmaMaskEnable',len(load))
    out.mkdir(parents=True,exist_ok=True)
    try:source=campaign(b,variant,mode)
    except Exception as e:
        failure=out/('source-first-failure-'+str(len(list(out.glob('source-first-failure*')))+1).zfill(2)+'.json')
        put(failure,dict(passed=False,native_run=False,error=repr(e),ROM_sha256=EXPECTED,fixture_sha256=sha(fixture),tool_sha256=sha(__file__)))
        raise
    scope='Actual cold menu/mode/alternate, typed mature food/classified flower/private physical gear actors; native health/contact/collection/stock/primary/Select/four secondary/cost/kill/catch/cleanup. No natural reveal/drop RNG, star/1up/death/fullpool/exhaustion/water/campaign/everypixel/originalmusic fidelity qualification.'
    cfg=dict(ROM_sha256=EXPECTED,identity=a.identity,character=19,variant=variant,mode=mode,hooks=hooks,ram=ram,
             setup_allowed={n:True for n in ALLOWED},plan=PLAN,scope=scope,dma_store_return=address(b,'PostDmaMaskEnable'),
             smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
             metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    put(out/'config.json',cfg);put(out/'source-controls.json',dict(source,hardware_guard_literal_exact=True,all_bare_callback_addresses_bound=True,resource_write_bans=RESOURCE_BANS))
    (out/'run.lua').write_text('CURRENT_TMNT_POWERUPS='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths={rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),fixture,Path(__file__),baseline,R/'docs/qa/current37-powerup-reuse-index-2026-10-27.json'}
    paths|={R/'tools/audit'/n for n in ['run_mesen_isolated.py','capture_budget.py','final_item_abilities_native.lua','final_item_abilities_static_return_v1.lua']}
    paths|={R/'tools/run_mesen.py',Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')}
    paths|={R/'src'/n for n in ['tmnt.s','tmnt_state.inc','tmnt_core.s','tmnt_equipment.s','tmnt_combat.s','tmnt_projectiles.s','tmnt_dispatch.s','tmnt_equipment_draw.s','inventory.s','mario_source.s','game.s','reset.s']}
    paths|={out/n for n in ['config.json','run.lua','source-controls.json','command.json']}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and ('py65'in f or str(R/'tools/audit')in f)and Path(f).is_file():paths.add(Path(f))
    put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',native_run=False,passed=False,goal_complete=False,
        ROM_sha256=EXPECTED,identity=a.identity,variant=variant,actual_numeric_mode=mode,scope=scope,
        caps=dict(wall_frames=8000,updates=3500,host_seconds=1200,bytes=2000000000,files=64,PNGs=8,perframe_files=0),
        setup='GameLoop+5/NmiDisableFF typed scene actor/map/motion only. Gear1..3 use source private physical drop actors; fullHP flower classified B4/stamp4. No ownership/health/ammo/stock/tier/attack/hurt/RNG/counter/projectile outcomes seeded. Natural acquisition eligibility not claimed.',
        source_controls='Complete logical CPU GameLoop campaign; actual PPU/hardware/physical-contact/menu/Lua execution requires separately authorized native run.',
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
    print(json.dumps(dict(prepared=True,native_run=False,identity=a.identity,variant=variant,source_calls=source['full_GameLoop_calls'],ready=str(out/'prepared-not-run.json'),ready_sha256=sha(out/'prepared-not-run.json'))))


if __name__=='__main__':main()

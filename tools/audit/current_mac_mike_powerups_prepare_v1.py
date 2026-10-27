"""Earned Mac/Mike Hard components on ab221e; source CPU only, never Mesen."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
from current_shared_star_life_prepare_v1 import hooks_for,EXPECTED,sha,put
from current_roster_compact_11_v1 import BASE,navigation,lua
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

REFILLS=[10,10,10,5,5,10,3,10,99,20]
WEAPONS=['baseball-bat','bola','fire','miracle-mirror','asterisk','shooting-star','spikes','baseball','super-laser','mega-laser']
ALLOWED='''Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits
Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce MmVX MmVY MmXFraction MmYFraction
ScrollThirtyTwo AreaParserTaskNum ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc
Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits
Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_Y_MoveForce Enemy_MovingDir Enemy_SprAttrib EnemyOffscrBitsMasked
PowerUpType InvPickupOwner InvPickup LmStamp JnDropKind JnDropX JnDropPage JnDropY JnDropAge'''.split()
BANS='''PlayerStatus PlayerSize LmHealth LmStars LmHearts LmAttack LmSuper LmHurt LmInvul LmReady LmLife
JnHealth JnMaxHearts JnOwnedTier JnSelected JnAmmo JnStars JnAttack JnHurt JnTier JnWeapon JnShotKind JnEnemyHP JnEnemyType JnEnemyHurt JnDropReceipt
InjuryTimer StarInvincibleTimer TimerControl GuestHurtTicks MmDeathFlag CheatInvincible NumberofLives PseudoRandomBitReg InvOwnedLo InvOwnedHi InvAmmo InvSelected GuestPowerupActive GuestPowerupTarget'''.split()


def plan_for(mac):
    out=[]
    def add(name,kind,hp,**kw):out.append(dict(name=name,kind=kind,health=hp,limit=1800 if kind=='contact'else 240,**kw))
    def attack(name,hp,weapon,face=1,super=False,attacks=1,picture=None):
        d=dict(weapon=weapon,face=face,super=super,attacks=attacks,wait=130 if super or weapon>=4 else 90)
        if picture:d['picture']=picture
        add(name,'weapon',hp,**d)
    if mac:
        attack('cold-normal-right',96,0,picture='01-normal.png')
        add('six-separated-native-contacts','contact',96,hits=6)
        add('mushroom-real-deficit-heal24','pickup',48,pickup=0,afterHP=72,afterStock=0,picture='02-heal.png')
        add('second-mushroom-restores96','pickup',72,pickup=0,afterHP=96,afterStock=0)
        add('four-flowers-earned-cap3','pickup',96,pickup=1,count=4,afterHP=96,afterStock=3,picture='03-star-cap.png')
        attack('star-uppercut-right-3to2',96,0,super=True,picture='04-uppercut-right.png')
        attack('star-uppercut-left-2to1',96,0,face=2,super=True,picture='05-uppercut-left.png')
        attack('third-earned-star-1to0',96,0,super=True,picture='06-last-star.png')
        add('empty-stars-UpB-does-not-invent-punch','empty',96)
        add('one-real-contact-no-stars','contact',96,hits=1)
        add('mushroom-caps-real88-deficit-at96','pickup',88,pickup=0,afterHP=96,afterStock=0,picture='07-heal-cap.png')
        add('real-crouch-rest-restores-empty-stamina','rest',96)
        attack('normal-left-after-spend',96,0,face=2)
    else:
        attack('cold-yoyo-actual-two-hits',6,1,attacks=2,picture='01-yoyo.png')
        add('real-contact-before-heart','contact',6,hits=1)
        add('private-heart-actual-heal2','drop',4,drop=1,afterHP=6,remainder=0)
        add('real-contact-before-star-restoration','contact',6,hits=1)
        add('five-real-private-stars-convert-to-heal2','drop',4,drop=2,count=5,afterHP=6,remainder=0)
        add('heart-container-mushroom','pickup',6,pickup=0,item=1,afterHP=8,afterStock=1)
        add('earned-tier2-before-HP-threshold','pickup',8,pickup=1,item=2,afterHP=8,afterStock=2)
        attack('owned-tier2-lowHP-still-yoyo',8,1,attacks=2)
        add('two-more-real-heart-containers','pickup',8,pickup=0,item=1,count=2,afterHP=12,afterStock=2,picture='02-heart-growth.png')
        attack('HP12-earned-primary-star',12,2)
        add('five-more-real-heart-containers','pickup',12,pickup=0,item=1,count=5,afterHP=22,afterStock=2)
        add('earned-tier3-flower','pickup',22,pickup=1,item=3,afterHP=22,afterStock=3)
        attack('HP22-earned-supernova',22,3,picture='03-supernova.png')
        for i,name in enumerate(WEAPONS):
            add('physical-flower-'+name,'pickup',22,pickup=1,item=i+4,afterHP=22,afterStock=3)
            pic={3:'04-mirror.png',4:'05-asterisk.png',7:'06-baseball.png',9:'07-mega-laser.png'}.get(i)
            attack('actual-'+name,22,i+4,face=2 if i in [0,7]else 1,picture=pic)
        for i,name in enumerate(WEAPONS):
            add('Select-earned-'+name,'select',22,edges=2 if i==0 else 1,selected=i+1)
            add('real-refill-'+name,'pickup',22,pickup=1,item=i+4,afterHP=22,afterStock=3,**({'picture':'08-refilled.png'}if i==9 else{}))
    return out


def quiet(q,mac):
    return q.get('Player_State')==q.get('InjuryTimer')==q.get('LmAttack'if mac else'JnAttack')==q.get('LmHurt'if mac else'JnHurt')==0 and(not mac or q.get('LmInvul')==0)and(mac or all(q.get('JnShotKind',i)==0 for i in range(6)))


def scene(q,mac,face):
    assert quiet(q,mac)
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for p in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,p*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    q.put(Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=face,Player_MovingDir=face,Player_CollisionBits=255,
          ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,ScrollLock=1,ScrollThirtyTwo=0,AreaParserTaskNum=0)
    for n in ['Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce']:q.set(n,0)
    for n in ['MmVX','MmVY']:q.array(n,[0]*3)
    for n in ['MmXFraction','MmYFraction']:q.array(n,[0]*2)


def actor(q,x,y,kind,slot):
    for n,v in dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=128 if kind==46 else 0,Enemy_BoundBoxCtrl=3 if kind==46 else 9,
        Enemy_X_Position=x,Enemy_PageLoc=0,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1,Enemy_SprAttrib=0,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0).items():q.set(n,v,slot)


def pickup(q,t,mac):
    actor(q,112,184,46,5);q.set('PowerUpType',t['pickup'],5)
    q.invoke('LmPrepareGate'if mac else'JnPreparePickup',x=5)
    expected=(0xe0+t['pickup'])if mac else(0x80+t['item'])
    assert q.get('InvPickup',5)==expected and q.get('InvPickupOwner',5)==(15 if mac else 16),('Actual pickup producer stamp',t,q.get('InvPickup',5))
    if mac:assert q.get('LmStamp',5)==expected


def drop(q,kind):
    assert q.get('JnDropKind',0)==0
    for n,v in dict(JnDropKind=kind,JnDropX=112,JnDropPage=0,JnDropY=192,JnDropAge=0).items():q.set(n,v,0)


def target(q,t,contact,mirror):
    if contact:actor(q,112,184,6,0)
    elif t['weapon']==7:actor(q,160,184,mirror,0);actor(q,188,184,6,1)
    else:actor(q,88 if t.get('face')==2 else 140,184,6,0)


def campaign(b,mac,plan,hooks,mirror):
    character=15 if mac else 16;q=Arena(b,character)
    q.put(CrossoverBehaviorVersion=1,OperMode_Task=3,AreaType=1,PlayerStatus=0,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,
          ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,Player_CollisionBits=255,Player_MovingDir=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for p in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,p*208+row*16+col)
    calls=0;rec=None;phase='settle';original=NesMPU.step;results=[]
    def hp():return q.get('LmHealth'if mac else'JnHealth')
    def stock():return q.get('LmStars'if mac else'JnOwnedTier')
    lookup={(h['pc'],bank):n for n,h in hooks.items()for bank in h['banks']if n in ['Collect','Injury','Defeat','Reflect','DropCollect']}
    def step(c):
        bank=q.m.banks[(c.pc-0x8000)//8192]if c.pc>=0x8000 else-1;n=lookup.get((c.pc,bank))
        if rec is not None and n:
            if n=='Collect':
                valid=q.get('InvPickupOwner',c.x)==character and((q.get('LmStamp',c.x)>=224)if mac else 129<=q.get('InvPickup',c.x)<=141)
                if valid:
                    assert phase=='pickup'and c.x==5
                    rec['pending_grant']=dict(hp=hp(),stock=stock(),hearts=q.get('LmHearts'if mac else'JnMaxHearts'));rec['grants']+=1
            elif n=='Injury'and q.get('LmInvul'if mac else'JnHurt')==0:
                assert phase=='contact'and not rec.get('pending_hit')
                rec['pending_hit']=dict(hp=hp()-(8 if mac else 2),stock=stock(),hearts=q.get('LmHearts'if mac else'JnMaxHearts'))
            elif n=='Defeat':assert phase=='weapon'and c.x==(1 if t['weapon']==7 else 0);rec['contacts']+=1
            elif n=='Reflect':assert phase=='weapon'and t['weapon']==7;rec['reflects']+=1
            elif n=='DropCollect'and phase=='drop':assert c.x==0 and q.get('JnDropKind',0)==t['drop'];rec['drops']+=1
        original(c)
    def main(buttons=0):
        nonlocal calls
        q.set('SavedJoypadBits',buttons);calls+=1;return q.invoke('GameLoop')[1]
    NesMPU.step=step
    try:
        for _ in range(30):main()
        assert hp()==(96 if mac else 6)and stock()==(0 if mac else 1)
        if mac:assert q.get('LmHearts')==20
        else:assert q.get('JnMaxHearts')==3 and q.get('JnSelected')==0 and all(q.get('JnAmmo',i)==0 for i in range(10))
        for t in plan:
            assert hp()==t['health'],('Carried actual health',t['name'],hp())
            phase=t['kind'];scene(q,mac,t.get('face',1))
            rec=dict(name=t['name'],health=hp(),stock=stock(),hearts=q.get('LmHearts'if mac else'JnMaxHearts'),grants=0,hits=0,contacts=0,debits=0,births=0,reflects=0,splits=0,drops=0,toggles=0)
            ammo=[q.get('JnAmmo',i)for i in range(10)]if not mac else[];lastammo=ammo.copy()
            if phase=='pickup':pickup(q,t,mac)
            elif phase in ['contact','weapon']:target(q,t,phase=='contact',mirror)
            elif phase=='drop':drop(q,t['drop'])
            remove=False;rearm=False;again=False;lastselect=q.get('JnSelected')if not mac else 0;separated=-1
            for age in range(1,t['limit']+1):
                if remove:q.set('Enemy_Flag',0,0);q.set('Enemy_CollisionBits',0,0);remove=False;separated=calls
                if rearm and quiet(q,mac)and calls>separated:scene(q,mac,1);target(q,t,True,mirror);rearm=False
                if again:
                    if phase=='pickup':pickup(q,t,mac)
                    else:drop(q,t['drop'])
                    again=False
                bkey=(8<=age<12 or(t.get('weapon')==8 and 20<=age<24)or(t.get('attacks')==2 and 40<=age<44))and phase in ['weapon','empty']
                buttons=(64 if bkey else 0)|(8 if phase=='empty'or t.get('super')else 0)
                if phase=='select'and 4<=age<t['edges']*10 and(age-4)%10<4:buttons=32
                if phase=='rest'and age>=4:buttons=4
                writes=main(buttons)
                if not mac:
                    for w in writes:
                        i=w['address']-address(b,'JnAmmo')
                        if 0<=i<10:
                            if phase=='weapon'and w['value']==lastammo[i]-1:rec['debits']+=1
                            lastammo[i]=w['value']
                        if phase=='weapon'and address(b,'JnShotKind')<=w['address']<address(b,'JnShotKind')+6 and w['value']:rec['births']+=1
                assert q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8,('No death',t,age,hp())
                if rec.get('pending_hit'):
                    h=rec.pop('pending_hit');assert hp()==h['hp']and(q.get('InjuryTimer')==0 if mac else q.get('InjuryTimer')>0)and q.get('LmHurt'if mac else'JnHurt')>0
                    if mac:assert stock()==max(0,h['stock']-1)and q.get('LmHearts')==max(0,h['hearts']-3)and q.get('LmInvul')==64 and q.get('LmHurt')==16
                    rec['hits']+=1;remove=True;rearm=rec['hits']<t['hits']
                if rec.get('pending_grant'):
                    h=rec.pop('pending_grant')
                    if mac:assert hp()==(min(96,h['hp']+24)if t['pickup']==0 else h['hp'])and stock()==(min(3,h['stock']+1)if t['pickup']==1 else h['stock'])
                    elif t['item']==1:assert q.get('JnMaxHearts')==min(22,h['hearts']+1)and hp()==2*q.get('JnMaxHearts')
                    elif t['item']<4:assert stock()==max(h['stock'],t['item'])and hp()==h['hp']
                    else:assert q.get('JnAmmo',t['item']-4)==REFILLS[t['item']-4]and q.get('JnSelected')==t['item']-3 and hp()==h['hp']
                    assert q.get('Enemy_Flag',5)==0
                    again=rec['grants']<t.get('count',1)
                slot=1 if t.get('weapon')==7 else 0
                if rec['contacts']and(q.get('Enemy_State',slot)&32 or q.get('Enemy_Flag',slot)==0):rec['defeat_seen']=True
                complete=False
                if phase=='pickup'and rec['grants']==t.get('count',1)and not again and age>=8:assert hp()==t['afterHP']and stock()==t['afterStock'];complete=True
                elif phase=='contact':complete=rec['hits']==t['hits']and not remove and quiet(q,mac)
                elif phase=='drop'and rec['drops']and q.get('JnDropKind',0)==0:
                    if rec['drops']<t.get('count',1):again=True
                    else:assert hp()==t['afterHP']and q.get('JnStars')&7==t['remainder'];complete=True
                elif phase=='select':
                    selected=q.get('JnSelected')
                    if selected!=lastselect:rec['toggles']+=1;lastselect=selected
                    if age>=t['edges']*10+5:assert rec['toggles']==t['edges']and selected==t['selected'];complete=True
                elif phase=='empty'and age>=20:assert q.get('LmAttack')==q.get('LmStars')==0 and q.get('LmHearts')==rec['hearts'];complete=True
                elif phase=='rest'and age>=35:assert hp()==rec['health']and q.get('LmStars')==0 and rec['hearts']==0 and q.get('LmHearts')==20;complete=True
                elif phase=='weapon':
                    if not mac and t['weapon']==8:rec['splits']+=sum(q.get('JnShotKind',i)==8 and q.get('JnShotHit',i)&128!=0 for i in range(6))
                    if age>=t['wait']and quiet(q,mac):
                        assert rec['contacts']==1 and rec.get('defeat_seen')and hp()==rec['health'],('Actual weapon kill',t,age,rec,hp())
                        if mac:assert stock()==rec['stock']-int(t['super'])and q.get('LmHearts')==rec['hearts'],('Mac debit/refund',t,rec,q.get('LmHearts'))
                        else:
                            assert [q.get('JnAmmo',i)for i in range(10)]==[v-int(t['weapon']>=4 and i==t['weapon']-4)for i,v in enumerate(ammo)]
                            assert rec['debits']==int(t['weapon']>=4)and rec['births']==(2 if t['weapon']in [7,8]else t['attacks']),('Birth/debit',t,rec)
                            if t['weapon']==7:assert rec['reflects']==1
                            if t['weapon']==8:assert rec['splits']>0
                        complete=True
                if complete:break
            else:raise AssertionError(('Finite source component limit',t,rec,dict(hp=hp(),state=q.get('Player_State'),injury=q.get('InjuryTimer'),hurt=q.get('LmHurt'if mac else'JnHurt'))))
            rec.update(full_GameLoop_calls=age,health_after=hp(),stock_after=stock())
            if not mac:rec['ammo_after']=[q.get('JnAmmo',i)for i in range(10)]
            results.append(rec);rec=None
    finally:NesMPU.step=original
    return dict(passed=True,native_run=False,full_GameLoop_calls=calls,components=results,scope='Actual full assembled GameLoop/producer/collision/attack/restore calls with logical typed scenes and external neutral/controller input. Cold owner/mode/context configured only before source initialization. No health/owned/ammo/timer/attack/hurt/kill/RNG outcome writes. No native menu/PPU/audio/interrupt or natural reveal/drop-eligibility claim.')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=['mac','mike'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();rom=R/'build/mega_proto_body_palette_9ea.nes';assert sha(rom)==EXPECTED
    assert out.is_relative_to(R/'build')and(not out.exists()or all(p.name.startswith('source-negative-')for p in out.iterdir()))
    fixture=R/'tests/current-mac-mike-powerups.lua';text=fixture.read_text();guard=R/'tools/audit/current_pit_powerups_v3.lua';g=guard.read_text();begin='-- All callback registration is startup-static.';end='emu.addEventCallback(function()\n if not entered'
    assert text[text.index(begin):text.index(end)]==g[g.index(begin):g.index(end)]
    assert text.count('emu.write(')==2 and 'removeMemoryCallback'not in text and not set(ALLOWED)&set(BANS)
    b=scoped_load(rom);hooks,_=hooks_for(b);mac=a.identity=='mac';plan=plan_for(mac);menu,character,_,_=BASE[a.identity]
    def hook(n):
        off=location(b,n);return dict(pc=address(b,n),banks=[(off-16)//8192],bytes=list(b['raw'][off:off+3]),source_symbol=n)
    hooks.update({n:hook(v)for n,v in (dict(Collect='LmCollectGate',Injury='LmInjuryGate',Defeat='LmHitEnemies::Normal')if mac else dict(Collect='JnCollectPickup',Injury='JnInjury',Defeat='JnDefeat',Reflect='JnReflectMagic',DropCollect='JnUpdateDrops::Collect')).items()})
    mirror=address(b,'BulletBill_CannonVar')
    names=set(ALLOWED)|set(BANS)|set(re.findall(r"[rw]\('([A-Za-z_][A-Za-z_0-9]*)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    names|=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9]*)'",text))&set(b['syms'])
    ram={n:address(b,n)for n in names};assert all(isinstance(v,int)for v in ram.values())
    out.mkdir(parents=True,exist_ok=True)
    try:source=campaign(b,mac,plan,hooks,mirror)
    except Exception as e:put(out/('source-negative-'+str(len(list(out.glob('source-negative-*')))+1)+'.json'),dict(passed=False,native_run=False,error=repr(e),ROM_sha256=EXPECTED,fixture_sha256=sha(fixture),tool_sha256=sha(__file__)));raise
    scope=('Mac earned heal24/cap96, real six-contact HP deficit, four real flowers cap3, three earned uppercuts/star costs and right/left normal kills/empty-star refusal.'if mac else'Mike physical heart containers and HP-gated primary1/2/3; both private restoration pickups; all10 actual source special kinds4..13, native one-stock costs, actual Mirror reflection/derived laser kill and second-B Asterisk split, Select and each exact selected-weapon refill.')+' Typed mature actor/classification/private-drop scenes; no natural reveal/RNG/drop-eligibility/death/exhaustion/fullpool/campaign/everypixel/original-art or melody-fidelity claim.'
    cfg=dict(ROM_sha256=EXPECTED,identity=a.identity,character=character,menu=menu,mac=mac,mode=1,plan=plan,refills=REFILLS,mirror_target=mirror,ram=ram,hooks=hooks,scope=scope,
        navigation=navigation(b['raw'],lambda n:location(b,n),menu),setup_allowed={n:True for n in ALLOWED},resource_bans={n:True for n in BANS},
        dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
        metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    put(out/'config.json',cfg);put(out/'source-controls.json',dict(source,hardware_guard_literal_exact=True,all_bare_dynamic_literal_RAM_bound=True,resource_write_bans=BANS))
    (out/'run.lua').write_text('CURRENT_MAC_MIKE_POWERUPS='+lua(cfg)+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(rom),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths={rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl'),fixture,Path(__file__),guard,R/'tools/audit/current_shared_star_life_prepare_v1.py',R/'build/mega_proto_body_palette_9ea_handoff.json'}
    paths|={R/'tools/audit'/n for n in ['run_mesen_isolated.py','capture_budget.py']};paths|={R/'tools/run_mesen.py',Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')}
    paths|={R/'src'/n for n in ['little_mac.s','little_mac_core.s','little_mac_combat.s','little_mac_pickups.s','little_mac_state.inc','mike_jones.s','mike_jones_core.s','mike_jones_weapons.s','mike_jones_pickups.s','mike_jones_dispatch.s','mike_jones_state.inc','collision.s','game.s','inventory.s','reset.s']}
    paths|={out/n for n in ['config.json','source-controls.json','run.lua','command.json']}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and('py65'in f or str(R/'tools/audit')in f)and Path(f).is_file():paths.add(Path(f))
    put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,ROM_sha256=EXPECTED,identity=a.identity,mode=1,scope=scope,
        caps=dict(wall_frames=8000,updates=4000,host_seconds=1200,files=64,bytes=2000000000,PNGs=8,perframe_files=0),
        setup='GameLoop+5/NmiDisableFF flat map/motion/live actors and mature source-classified pickups/private physical drops only; no owned tier/health/ammo/stock/attack/hurt/RNG/results seeded. Genuine compiled19-node menu BFS and actual numeric Hard readback.',
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
    print(json.dumps(dict(prepared=True,native_run=False,identity=a.identity,cases=len(plan),source_calls=source['full_GameLoop_calls'],ready=str(out/'prepared-not-run.json'),ready_sha256=sha(out/'prepared-not-run.json'))))


if __name__=='__main__':main()

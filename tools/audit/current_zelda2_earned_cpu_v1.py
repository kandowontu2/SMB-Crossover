"""Current ZeldaII earned RPG components, complete compiled GameLoop models only."""
from pathlib import Path
import argparse,hashlib,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
ROM=ROOT/'build/roster-20261028-fixes.nes'
EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def scene(q):
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for p in [0,1]:
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,p*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    q.put(ScrollLock=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,ScrollThirtyTwo=0,AreaParserTaskNum=0,
          Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,PlayerFacingDir=1,Player_MovingDir=1,Player_CollisionBits=255,MmOldX=112,
          Player_X_Speed=0,Player_Y_Speed=0,Player_X_MoveForce=0,Player_Y_MoveForce=0)
    for n,size in [('MmVX',3),('MmVY',3),('MmXFraction',2),('MmYFraction',2)]:q.array(n,[0]*size)

def actor(q,kind,x,y,slot=0):
    values=dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=128 if kind==46 else 0,Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=x&255,Enemy_PageLoc=x>>8,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1 if kind==46 else 2,Enemy_SprAttrib=0,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,MmEnemyHealthLo=0,MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0)
    for n,v in values.items():q.set(n,v,slot)

def snapshot(q):
    return {n:q.get(n)for n in ['Z2Hp','Z2Mp','Z2ExpLo','Z2ExpHi','Z2LevelsLo','Z2LevelsHi','Z2Containers','Z2LearnedSpells','Z2Tech','Z2ActiveSpells','Z2Selection','Z2HpPending','Z2MpPending','Z2ExpPendingLo','Z2ExpPendingHi','Z2UiState','Z2UiCursor','Z2PanelActive','Z2PanelPending','GamePauseStatus','Z2CachedPose','Player_X_Position','Player_Y_Position','Player_State']}

def campaign(b,mode):
    q=Arena(b,4);q.put(Z2Variant=1,CrossoverBehaviorVersion=mode,PlayerStatus=0,OperMode_Task=3,AreaType=1)
    scene(q);q.array('GameTimerDisplay',[3,9,9]);end=address(b,'E_GroundArea2')-1;assert b['raw'][location(b,'E_GroundArea2')-1]==255
    q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
    rows=[];counts={};calls=0;current={};events=[]
    names=['Z2PreparePickupGate','Z2CollectPickupGate','Z2CollectReward','Z2TryCast','Z2LevelUp','Z2Damage','Z2JarPickup','Z2QueueExp','Z2HitEnemy','Z2AwardEnemy','Z2SpellWorldEffects','Z2WeaponsGate','Z2Movement','Z2UiTickGate','Z2PanelTick','Z2PanelSync']
    owners={(address(b,n),(location(b,n)-16)//8192):n for n in names};original=NesMPU.step
    def step(c):
        bank=q.m.banks[(c.pc-32768)//8192]if c.pc>=32768 else-1;n=owners.get((c.pc,bank))
        if n:
            counts[n]=counts.get(n,0)+1
            if n in ['Z2CollectReward','Z2TryCast','Z2LevelUp','Z2Damage','Z2JarPickup','Z2QueueExp','Z2HitEnemy','Z2AwardEnemy']:
                events.append(dict(update=calls,owner=n,a=c.a,x=c.x,pc=c.pc,bank=bank,Hp=q.get('Z2Hp'),Mp=q.get('Z2Mp')))
        original(c)
    def update(bits=0):
        nonlocal calls
        calls+=1;q.put(SavedJoypadBits=bits,SavedJoypad1Bits=bits);q.invoke('GameLoop')
        ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('PnPaletteScreenUpdate');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
        assert q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8,('source life',snapshot(q))
    def wait(predicate,limit=250):
        for i in range(limit):
            if predicate():return i
            update()
        raise AssertionError(('finite source wait',snapshot(q),events[-5:]))
    def edge(bits):update();update(bits);update()
    def open_panel():
        wait(lambda:q.get('GamePauseTimer')==0,80);edge(16)
        wait(lambda:q.get('GamePauseStatus')&1 and q.get('Z2PanelActive')and not q.get('Z2PanelPending'),30)
    def close_panel():
        edge(128);wait(lambda:not q.get('GamePauseStatus')&1 and not q.get('Z2PanelActive')and not q.get('Z2PanelPending'),30)
    def select_spell(spell):
        open_panel()
        if q.get('Z2UiState')&1:edge(1)
        wait(lambda:q.get('Z2PanelPage')==0 and not q.get('Z2PanelPending'),30)
        for _ in range(8):
            if q.get('Z2Selection')&7==spell:break
            edge(4)
        assert q.get('Z2Selection')&7==spell
        close_panel()
    def cast(spell):
        select_spell(spell);before=snapshot(q);magic=(q.get('Z2LevelsLo')>>3)&7
        cost=b['raw'][location(b,'SpellCosts')+spell*8+magic]
        edge(32);after=snapshot(q)
        assert after['Z2Mp']==before['Z2Mp']-cost,('real paid cast',spell,cost,before,after,events[-5:])
        rows.append(dict(name='cast-'+str(spell),cost=cost,before=before,after=after))
    def drop(kind):
        # Complete actual pickup actor, not a grant/owned-resource write.
        scene(q)
        for n,v in dict(Z2DropKind=kind,Z2DropX=120,Z2DropPage=0,Z2DropY=176,Z2DropVY=0,Z2DropFraction=0,Z2DropAge=0).items():q.set(n,v,5)
        before=snapshot(q);update();assert q.get('Z2DropKind',5)==0
        wait(lambda:q.get('Z2MpPending')==0 and q.get('Z2ExpPendingLo')==q.get('Z2ExpPendingHi')==0,300)
        rows.append(dict(name='physical-drop-'+hex(kind),before=before,after=snapshot(q)))
    def level(category):
        wait(lambda:q.get('Z2ExpPendingLo')==q.get('Z2ExpPendingHi')==0)
        wait(lambda:q.get('GamePauseStatus')&1 and q.get('Z2PanelActive')and not q.get('Z2PanelPending'),40)
        if not q.get('Z2UiState')&1:edge(1)
        wait(lambda:q.get('Z2PanelPage')==1 and not q.get('Z2PanelPending'),40)
        for _ in range(4):
            if q.get('Z2UiCursor')==category:break
            edge(4)
        assert q.get('Z2UiCursor')==category
        before=snapshot(q);cost=[200,100,50][category];exp=q.get('Z2ExpLo')+256*q.get('Z2ExpHi')
        edge(128);wait(lambda:not q.get('Z2PanelPending'),40)
        assert q.get('Z2ExpLo')+256*q.get('Z2ExpHi')==exp-cost,('actual level debit',category,before,snapshot(q))
        rows.append(dict(name='earned-level-'+str(category),threshold=cost,before=before,after=snapshot(q)))
    def sword_defeat():
        scene(q);update()
        for col in [8,9]:q.set('Block_Buffer_1',84,160+col)
        actor(q,6,136,168);before=snapshot(q);start=len(events)
        diag=[]
        for age in range(160):
            update(64 if age%18 in [1,2]else 0)
            if age<20:diag.append([age]+[q.get(n)for n in ['Z2CachedPose','Z2AttackStage','Z2AttackTimer','Z2RectW','Z2RectY','Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_Y_Position','Z2EnemyHp','Z2EnemyExpReceipt']])
            if q.get('Enemy_State')&32:break
        else:raise AssertionError(('sword contact deadline',snapshot(q),diag,events[-8:]))
        hits=[e for e in events[start:]if e['owner']=='Z2HitEnemy'];awards=[e for e in events[start:]if e['owner']=='Z2AwardEnemy']
        assert len(hits)>=2 and awards and hits[0]['a']==2
        wait(lambda:not any(q.get('Z2ShotKind',i)for i in [0,1])and q.get('Z2AttackTimer')==0,100)
        rows.append(dict(name='real-sword-defeat-EXP',hits=hits,awards=awards,before=before,after=snapshot(q)))
    NesMPU.step=step
    try:
        for _ in range(30):update()
        assert q.get('Z2Hp')==q.get('Z2Mp')==127 and q.get('Z2Containers')==51 and q.get('Z2LearnedSpells')==0
        # A real body hit creates the deficit. No HP/hurt outcome is seeded.
        scene(q);actor(q,6,112,168)
        before=snapshot(q)
        for _ in range(2):update()
        assert q.get('Z2Hp')==before['Z2Hp']-16,('real Goomba damage',snapshot(q),events[-5:])
        q.set('Enemy_Flag',0)
        for _ in range(40):update()
        rows.append(dict(name='real-injury',before=before,after=snapshot(q)))
        # Use the actual producer, and then physical contact of its mature actor.
        for i in range(20):
            if i==19:
                scene(q);actor(q,6,112,168);hp=q.get('Z2Hp')
                update();update();assert q.get('Z2Hp')==hp-16
                q.set('Enemy_Flag',0);wait(lambda:q.get('Z2HurtTimer')==0,60)
                cast(4);assert q.get('Z2Mp')==15
            scene(q);actor(q,46,112,184,5);q.set('PowerUpType',0 if i==0 else 1,5);q.invoke('Z2PreparePickupGate',x=5)
            reward=q.get('InvPickup',5);prepared={n:q.get(n,5)for n in ['PowerUpType','InvPickupOwner','InvPickup','InvPickupSaveLo']};before=snapshot(q)
            expected=[192,193,194,195,196,197,198,199,200,201,202,203,204,203,204,203,204,203,204,205][i]
            assert reward==expected,(i,reward,prepared,snapshot(q))
            for age in range(100):
                update()
                if not q.get('Enemy_Flag',5)and q.get('Z2HpPending')==q.get('Z2MpPending')==0:break
            else:raise AssertionError(('pickup deadline',i,reward,snapshot(q),events[-5:]))
            assert q.get('Enemy_Flag',5)==0
            rows.append(dict(name=f'reward-{reward:02x}-{i}',prepared=prepared,updates=age+1,before=before,after=snapshot(q)))
        assert q.get('Z2LearnedSpells')==255 and q.get('Z2Tech')==148 and q.get('Z2Containers')==119 and q.get('Z2Hp')==255 and q.get('Z2Mp')==47
        drop(0x91);assert q.get('Z2Mp')==255
        cast(0)
        assert q.get('Z2ActiveSpells')&1
        drop(0x90);assert q.get('Z2Mp')==223
        drop(0x91);assert q.get('Z2Mp')==255
        scene(q);actor(q,6,112,168);hp=q.get('Z2Hp')
        for _ in range(2):update()
        assert q.get('Z2Hp')==hp-8
        q.set('Enemy_Flag',0);wait(lambda:q.get('Z2HurtTimer')==0,60)
        cast(2);wait(lambda:q.get('Z2HpPending')==0,80);assert q.get('Z2Hp')==255
        cast(1);assert q.get('Z2ActiveSpells')&2
        scene(q);before=snapshot(q)
        update(128)
        low=q.get('Player_Y_Position')
        for _ in range(60):update(128);low=min(low,q.get('Player_Y_Position'))
        wait(lambda:q.get('Player_State')==0,100)
        assert low<before['Player_Y_Position']-64,('real Jump benefit',low,before,snapshot(q))
        rows.append(dict(name='paid-Jump-motion',before=before,minimumY=low,after=snapshot(q)))
        sword_defeat()
        drop(0x8a);level(2)
        drop(0x8c);level(1)
        drop(0x8c);level(0)
        wait(lambda:not q.get('GamePauseStatus')&1 and not q.get('Z2PanelPending'),50)
        assert q.get('Z2LevelsLo')==73 and q.get('Z2LevelsHi')==128
        cast(4);assert rows[-1]['cost']==160 and q.get('Z2ActiveSpells')&16
        scene(q);update()
        # Goomba's native 24px body rests on Y192; fire travels at Y180.
        for col in [10,11]:q.set('Block_Buffer_1',84,160+col)
        actor(q,6,160,168);before=snapshot(q);start=len(events);seen_fire=False
        fire_diag=[]
        for age in range(180):
            update(64 if age%20 in [1,2]else 0)
            seen_fire|=any(q.get('Z2ShotKind',i)==2 for i in [0,1])
            if age<45:fire_diag.append([age]+[q.get(n)for n in ['Z2CachedPose','Z2NativeAttackStand','Z2AttackStage','Z2AttackTimer','Z2ShotKind','Z2ShotX','Z2ShotY','Enemy_Flag','Enemy_State','Enemy_X_Position','Enemy_Y_Position','Z2EnemyHp']])
            if q.get('Enemy_State')&32:break
        else:raise AssertionError(('Fire defeat',snapshot(q),fire_diag,events[-8:]))
        assert seen_fire and any(e['owner']=='Z2HitEnemy'and e['a']==3 for e in events[start:])
        rows.append(dict(name='actual-Fire-attack-level-benefit',before=before,after=snapshot(q)))
        # Every expensive spell is paid from genuinely collected red jars.
        drop(0x91);cast(5);assert q.get('Z2ActiveSpells')&32
        scene(q);update();actor(q,21,130,176);before=snapshot(q);start=len(events)
        for _ in range(12):
            update()
            if not q.get('Enemy_Flag')and any(q.get('Z2ShotKind',i)==2 for i in [0,1]):break
        else:raise AssertionError(('Reflect real flame',snapshot(q),[q.get(n)for n in ['Enemy_Flag','Enemy_ID','Enemy_X_Position','Enemy_Y_Position','Z2RectX','Z2RectY']],events[-8:]))
        assert q.get('Z2Hp')==before['Z2Hp']
        rows.append(dict(name='actual-Reflect-flame',before=before,after=snapshot(q)))
        wait(lambda:not any(q.get('Z2ShotKind',i)for i in [0,1]),140)
        drop(0x91);scene(q);update();actor(q,0,180,184);before=snapshot(q)
        cast(6);assert q.get('Enemy_ID')==6 and not q.get('Z2ActiveSpells')&64
        rows.append(dict(name='actual-Spell-transform-enemy',before=before,after=snapshot(q)))
        drop(0x91);scene(q);update();actor(q,0,180,184);before=snapshot(q);start=len(events)
        cast(7);assert q.get('Enemy_State')&32 and not q.get('Z2ActiveSpells')&128
        assert any(e['owner']=='Z2HitEnemy'and e['a']==50 for e in events[start:])
        rows.append(dict(name='actual-Thunder-defeat',before=before,after=snapshot(q)))
        # Glove uses the real sword/block producer on a source-authored brick.
        scene(q);update();q.set('Block_Buffer_1',0x51,9*16+8);before=snapshot(q)
        for age in range(40):
            update(64 if age==1 else 0)
            if q.get('Block_Buffer_1',9*16+8)!=0x51:break
        else:raise AssertionError(('Glove brick',snapshot(q),q.get('Block_Buffer_1',9*16+8)))
        rows.append(dict(name='actual-Glove-brick',before=before,after=snapshot(q)))
        # Native thrust poses are reached with actual jump/direction input.
        for down in [False,True]:
            scene(q);update();update(128| (4 if down else 8));before=snapshot(q)
            wait(lambda:q.get('Z2CachedPose')==(9 if down else 8),30)
            px=q.get('Player_X_Position');py=q.get('Player_Y_Position')
            actor(q,6,px+4,py+(16 if down else -16));start=len(events)
            update((128|4)if down else(128|8))
            hits=[e for e in events[start:]if e['owner']=='Z2HitEnemy']
            assert hits and hits[0]['a']==3,('real thrust contact',down,snapshot(q),events[-5:])
            assert q.get('Z2NativeVY')==(254 if down else 0),('actual thrust motion',down,snapshot(q),q.get('Z2NativeVY'))
            rows.append(dict(name='actual-'+('Down'if down else'Up')+'-thrust',hits=hits,before=before,after=snapshot(q)))
            q.set('Enemy_Flag',0);wait(lambda:q.get('Player_State')==0,150)
        drop(0x91);cast(3);assert q.get('Z2ActiveSpells')&8
        scene(q);update();before=snapshot(q)
        for _ in range(12):update(9)
        assert q.get('Player_X_Position')>before['Player_X_Position']and q.get('Player_Y_Position')<before['Player_Y_Position']and q.get('Player_State')==1
        rows.append(dict(name='actual-Fairy-controlled-motion',before=before,after=snapshot(q)))
    finally:NesMPU.step=original
    return dict(passed=True,ROM_sha256=EXPECTED,mode=mode,GameLoop_calls=calls,rows=rows,events=events,owner_counts=counts,native_run=False,scope='Typed CPU arena + actual producer/full GameLoop pickup/control path. No native/PPU/input polling/timing proof.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',type=int,choices=[0,1],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert sha(ROM)==EXPECTED and not a.output.exists()
    z=campaign(scoped_load(ROM),a.mode);z['tool_sha256']=sha(Path(__file__));a.output.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,path=str(a.output),GameLoops=z['GameLoop_calls'],sha256=sha(a.output))))

if __name__=='__main__':main()

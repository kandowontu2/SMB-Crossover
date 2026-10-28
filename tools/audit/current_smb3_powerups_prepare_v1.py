"""Finite earned SMB3 suit/ability campaigns on bdf9; never launches Mesen."""
from pathlib import Path
import argparse,ast,hashlib,json,re,sys,traceback
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from current_roster_compact_11_v1 import BASE,navigation,lua
from current_shared_star_life_prepare_v1 import hooks_for
# Readiness is bound to the real sparse assembled injury-clock successor.
# The original bdf9 earned-contact counterexample is retained separately.
ROM=B/'current_smb3_timer.nes'
EXPECTED=None
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
N={n:'M3Native::Player_'+n for n in ['Power','FlyTime','WagCount','TailAttack','TailCount','Statue','QueueSuit','IsDucking','Frame','XVel','YVel','InWater','FrogHopCnt','SwimCnt','FlipBits','FireCount']}
PLAN=[dict(name='cold-small-jump',kind='jump',form=0),dict(name='real-super-mushroom',kind='pickup',form=0,to=1,picture='01-super.png'),
 dict(name='super-crouch-and-real-head-brick',kind='head',form=1),dict(name='real-fire-flower',kind='pickup',form=1,to=2),
 dict(name='native-fireball-right',kind='shot',form=2,face=1,picture='02-fireball.png'),dict(name='native-fireball-left',kind='shot',form=2,face=2),
 dict(name='real-raccoon-leaf',kind='pickup',form=2,to=3),dict(name='raccoon-tail-enemy',kind='tail',form=3,face=1),
 dict(name='raccoon-tail-real-brick',kind='tailblock',form=3),dict(name='earned-raccoon-P-flight-wag',kind='flight',form=3,picture='03-raccoon-flight.png'),
 dict(name='real-frog-suit',kind='pickup',form=3,to=4),dict(name='frog-ground-hop',kind='jump',form=4),dict(name='frog-directional-water-swim',kind='swim',form=4,picture='04-frog-swim.png'),
 dict(name='real-tanooki-suit',kind='pickup',form=4,to=5),dict(name='tanooki-tail-enemy',kind='tail',form=5,face=2),
 dict(name='earned-tanooki-P-flight-wag',kind='flight',form=5),dict(name='tanooki-statue-real-protected-contact-release',kind='statue',form=5,picture='05-statue.png'),
 dict(name='real-hammer-suit',kind='pickup',form=5,to=6),dict(name='native-hammer-right',kind='shot',form=6,face=1,picture='06-hammer.png'),
 dict(name='native-hammer-left',kind='shot',form=6,face=2),dict(name='actual-Star-contact-expiry',kind='star',form=6,picture='07-star-contact.png'),
 dict(name='physical-1Up-gain-popup-cleanup',kind='life',form=6),dict(name='real-higher-suit-injury-to-super',kind='hurt',form=6,to=1),
 dict(name='real-super-injury-shrink-to-small',kind='hurt',form=1,to=0,picture='08-small-cleanup.png')]
ALLOWED='''Block_Buffer_1 MmSolidTerrain MmBrickHealth Enemy_Flag Enemy_CollisionBits
Player_X_Speed Player_Y_Speed Player_X_MoveForce Player_Y_MoveForce MmVX MmVY MmXFraction MmYFraction
ScrollThirtyTwo AreaParserTaskNum ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_PageLoc ScreenRight_X_Pos AreaType
Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos Player_State PlayerFacingDir Player_MovingDir Player_CollisionBits
Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_Y_MoveForce Enemy_MovingDir Enemy_SprAttrib EnemyOffscrBitsMasked
PowerUpType InvPickupOwner InvPickup InvRisePhase'''.split()
BANS='''M3Form M3Marker M3Ready M3Growth M3Poof M3Fresh M3Previous M3ShotKind M3ShotAge M3ShotVX M3ShotVY M3Life
PlayerStatus PlayerSize InjuryTimer GuestInvulTicks GuestHurtTicks MmDeathFlag StarInvincibleTimer NumberofLives
InvOwnedLo InvOwnedHi InvAmmo InvSelected PseudoRandomBitReg CheatInvincible GuestPowerupActive GuestPowerupTarget'''.split()+list(N.values())

def quiet(q):
    return q.get('Player_State')==0 and q.get('Player_X_Speed')==0 and q.get('M3Growth')==q.get('M3Poof')==0 and all(q.get('M3ShotKind',i)==0 for i in range(2))and q.get(N['Statue'])==0 and q.get(N['FlyTime'])==0 and all(q.get('Block_State',i)==0 for i in range(2))

def actor(q,kind,x=112,y=184,slot=0,state=0):
    for n,v in dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=state,Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=x,Enemy_PageLoc=0,Enemy_Y_Position=y,Enemy_Y_HighPos=1,
        Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=1,Enemy_SprAttrib=0,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0).items():q.set(n,v,slot)

def arena(q,t):
    assert quiet(q),'Prior real suit/shot/move/particle cleanup'
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for p in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,p*208+row*16+col)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    q.put(AreaType=0 if t['kind']=='swim'else 1,Player_X_Position=16 if t['kind']=='flight'else 112,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0,
        PlayerFacingDir=t.get('face',1),Player_MovingDir=t.get('face',1),Player_CollisionBits=255,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,ScrollThirtyTwo=0,AreaParserTaskNum=0)
    for n in ['Player_X_Speed','Player_Y_Speed','Player_X_MoveForce','Player_Y_MoveForce']:q.set(n,0)
    for n in ['MmVX','MmVY']:q.array(n,[0]*3)
    for n in ['MmXFraction','MmYFraction']:q.array(n,[0]*2)
    if t['kind']=='head':q.set('Block_Buffer_1',81,7*16+7)
    if t['kind']=='tailblock':q.set('Block_Buffer_1',81,10*16+8)
    if t['kind']=='shot':actor(q,6,(176 if t.get('face',1)==1 else 56)if t['form']==6 else(144 if t.get('face',1)==1 else 80),184)
    if t['kind']=='tail':actor(q,6,136 if t.get('face',1)==1 else 88,184)
    if t['kind']=='hurt':actor(q,6)

def hooks(b):
    h,extra=hooks_for(b)
    for n,s in dict(Collect='M3CollectPickup',Injury='M3Injury',Throw='M3Throw',Tail='M3TailEnemies',TailBlock='M3TailBlock',Defeat='M3DefeatEnemy',ProjectileDamage='M3ProjectileDamage',Graphics='M3Graphics',ShotRender='M3DrawWorld::Render',RosterReady='RosterOamReady').items():
        off=location(b,s);h[n]=dict(pc=address(b,s),banks=[(off-16)//8192],bytes=list(b['raw'][off:off+3]),source_symbol=s,source_delta=0)
    return h,extra

def injury_controls(b):
    import itertools
    old=scoped_load(B/'kirby-mike-polish-production.nes');flags=[32|(i&15)|((i&16)<<2)|((i&32)<<2)for i in range(64)]
    def run(q,name,p,x=0,interrupt=None):
        pc=address(q.b,name);w=(pc-32768)//8192;k=(location(q.b,name)-16)//8192;q.m.page(w,k)
        if w in (1,2):q.set('CurrentBank'if w==1 else'CurrentBankC',k|128)
        c=NesMPU(memory=q.m,pc=pc);c.p=p;c.x=x;c.y=73;c.a=165;c.sp=253;c.stPushWord(0x5aff);q.m.writes=[];trace=[]
        for ix in range(100000):
            if c.pc==0x5b00:break
            if ix==interrupt:
                def irq_state():
                    m=list(q.m[:32768]);m[256:512]=[0]*256
                    for at in[0x2005,0x2006,0x5128,0x5130]:m[at]=0
                    return(c.pc,c.a,c.x,c.y,c.p&207,c.sp,tuple(q.m.banks),bytes(m))
                before=irq_state();start=len(q.m.writes)
                assert not c.p&4;c.irq()
                for _ in range(500):
                    if c.pc==before[0]and c.sp==before[5]:break
                    c.step()
                else:raise AssertionError('Actual IRQ return timeout')
                after=irq_state();assert before==after,('IRQ context',ix,before[:7],after[:7])
                assert all(at in[0x2005,0x2006,0x5128,0x5130]or 256<=at<512 for at,v in q.m.writes[start:]);del q.m.writes[start:]
            trace.append((c.pc,c.p));c.step()
        else:raise AssertionError(('Actual source call timeout',name))
        assert c.sp==253;return c,trace
    direct=[]
    for form,f,slot in itertools.product(range(1,7),flags,[0,5]):
        a=Arena(old,17);z=Arena(b,17)
        for q in[a,z]:q.put(M3Form=form,M3PaletteValid=1,GameEngineSubroutine=8,GuestHurtKind=0,GuestHurtTicks=0,GuestLegacyHurt=0,CheatInvincible=0)
        c,_=run(a,'M3Injury',f,slot);d,t=run(z,'M3Injury',f,slot)
        assert a.get('GuestHurtKind')==0 and z.get('GuestHurtKind')==17
        a.set('GuestHurtKind',17) # The sole explicitly intended final state delta.
        assert(c.a,c.x,c.y,c.p,c.sp,tuple(a.m.banks),bytes(a.m[:32768]))==(d.a,d.x,d.y,d.p,d.sp,tuple(z.m.banks),bytes(z.m[:32768]))
        assert c.processorCycles==d.processorCycles
        # Only the exact old duplicate palette invalidation disappears; the
        # earlier real ClearSuitState write and every other write are retained.
        ow=list(a.m.writes[:-1]);nw=list(z.m.writes);kind=address(old,'GuestHurtKind');pal=address(old,'M3PaletteValid')
        hits=[i for i,(at,v)in enumerate(ow)if at==pal];assert len(hits)==2 and ow[hits[-1]][1]==0;del ow[hits[-1]]
        ow=[(at,17 if at==kind else v)for at,v in ow];assert ow==nw
        direct.append(d.processorCycles-c.processorCycles)
    q=Arena(b,17);q.put(M3Form=6,M3PaletteValid=1,GuestHurtKind=0,GuestLegacyHurt=0);_,trace=run(q,'M3Injury',32)
    interrupts=0
    for ix,(pc,p)in enumerate(trace):
        if p&4:continue
        q=Arena(b,17);q.put(M3Form=6,M3PaletteValid=1,GuestHurtKind=0,GuestLegacyHurt=0);run(q,'M3Injury',32,interrupt=ix);interrupts+=1
    ticks=[]
    for engine,pause,power,timer in itertools.product([7,8],[0,1],[0,1],[0,1,113]):
        for f in[32,35,97,225]:
            a=Arena(old,17);z=Arena(b,17)
            for q in[a,z]:q.put(GameEngineSubroutine=engine,GamePauseStatus=pause,GuestPowerupActive=power,GuestInvulTicks=timer,GuestHurtKind=17,GuestHurtTicks=0,GuestLegacyHurt=0,InjuryTimer=int(timer>0))
            c,_=run(a,'GuestInjuryTick',f);d,_=run(z,'GuestInjuryTick',f)
            assert(c.a,c.x,c.y,c.p,c.sp,tuple(a.m.banks),bytes(a.m[:32768]),a.m.writes,c.processorCycles)==(d.a,d.x,d.y,d.p,d.sp,tuple(z.m.banks),bytes(z.m[:32768]),z.m.writes,d.processorCycles)
            want=0 if engine!=8 else timer if pause or power else max(0,timer-1);assert z.get('GuestInvulTicks')==want
            ticks.append(want)
    foreign=0
    for identity,(menu,character,variant_name,variant)in BASE.items():
        if character==17:continue
        for mode in[0,1]:
            qs=[]
            for source in[old,b]:
                q=Arena(source,character);q.put(CrossoverBehaviorVersion=mode,OperMode_Task=3,PlayerStatus=0,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,ScrollLock=1,ScreenLeft_PageLoc=0,ScreenRight_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_X_Pos=255)
                if variant_name:q.set(variant_name,variant)
                q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
                for row in[11,12]:
                    for col in range(16):q.set('Block_Buffer_1',84,row*16+col)
                c,_=run(q,'GameLoop',32);qs.append((c.a,c.x,c.y,c.p,c.sp,bytes(q.m[:32768]),tuple(q.m.banks),q.m.writes,c.processorCycles))
            assert qs[0]==qs[1],('Foreign full Main state/writes/cycles',identity,mode);foreign+=1
    return dict(passed=True,native_run=False,foreign_full_GameLoop_state_writes_cycles=foreign,direct_full_M3Injury_AXYP_SP_entire_stack_RAM_banks_cases=len(direct),direct_cycle_delta_range=[min(direct),max(direct)],actual_IRQ_boundaries=interrupts,full_GuestInjuryTick_pause_transform_expiry_cancel_cases=len(ticks),
        explicit_final_state_delta='GuestHurtKind0->17 only at injury return; prior ClearSuitState palette invalidation retained, exact redundant later write removed.',
        expiry_contract='Existing shared GuestInjuryTick owns113 subsequent active Main ticks, holds InjuryTimer, pauses on pause/powerup and cancels outside engine8. Own M3 two-tick blink still reads the same timer. No new timer or physics.')

def campaign(b,mode,var):
    q=Arena(b,17);q.put(CrossoverBehaviorVersion=mode,M3Variant=var,OperMode_Task=3,AreaType=1,PlayerStatus=0,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,Player_MovingDir=1,Player_CollisionBits=255,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1)
    q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
    # Execute the real cold-reset seed prefix; never choose/write RNG outcomes.
    pc=address(b,'FinializeMarioInit');q.m.page((pc-32768)//8192,(location(b,'FinializeMarioInit')-16)//8192);c=NesMPU(memory=q.m,pc=pc)
    assert q.m[pc:pc+9]==[88,169,165,141,address(b,'WarmBootValidation')&255,address(b,'WarmBootValidation')>>8,141,address(b,'PseudoRandomBitReg')&255,address(b,'PseudoRandomBitReg')>>8]
    while c.pc<pc+9:c.step()
    assert q.get('PseudoRandomBitReg')==165
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for p in range(2):
        for row in [11,12]:
            for col in range(16):q.set('Block_Buffer_1',84,p*208+row*16+col)
    h,_=hooks(b);lookup={(d['pc'],k):n for n,d in h.items()for k in d['banks']};rec=None;task=None;calls=0;origin=NesMPU.step
    def step(cpu):
        k=q.m.banks[(cpu.pc-32768)//8192]if cpu.pc>=32768 else -1;n=lookup.get((cpu.pc,k))
        if rec is not None and n:
            if n=='Collect'and cpu.x==5 and q.get('PowerUpType',5)<2:
                assert task['kind']=='pickup'and q.get('Enemy_State',5)>=128 and q.get('InvPickupOwner',5)==17 and q.get('InvPickup',5)==208+task['to']
                rec['collect']+=1;rec['collected_at']=rec['age'];assert rec['age']>=48,'No collection inside the source48-tick rise'
            elif n in ['Throw','Tail','TailBlock','Defeat','ProjectileDamage','Injury','StarContact','LifeIncrement','AreaMusic']:
                rec[n]=rec.get(n,0)+1
                if n=='Tail':rec.setdefault('tail_entries',[]).append(dict(age=rec['age'],x=q.get('Player_X_Position'),y=q.get('Player_Y_Position'),flip=q.get(N['FlipBits']),enemyflag=q.get('Enemy_Flag',0),enemyid=q.get('Enemy_ID',0),enemyx=q.get('Enemy_X_Position',0),enemyy=q.get('Enemy_Y_Position',0),enemystate=q.get('Enemy_State',0)))
            if n=='Injury':assert task['kind']=='hurt','No unintended player injury'
        origin(cpu)
    def main(button=0):
        nonlocal calls
        calls+=1;q.set('SavedJoypadBits',button)
        pc=address(b,'GameLoop');window=(pc-32768)//8192;owner=(location(b,'GameLoop')-16)//8192;q.m.page(window,owner)
        if window in (1,2):q.set('CurrentBank'if window==1 else'CurrentBankC',owner|128)
        q.m.writes=[];c=NesMPU(memory=q.m,pc=pc);c.sp=253;c.stPushWord(0x5aff)
        for _ in range(100000):
            if c.pc==0x5b00:break
            c.step()
        else:raise AssertionError(('Source Main timeout',hex(c.pc)))
        assert c.sp==253;writes=[dict(address=p,value=v)for p,v in q.m.writes]
        if rec is not None:rec['source_Main_CPU_sum']=rec.get('source_Main_CPU_sum',0)+c.processorCycles;rec['source_Main_CPU_max']=max(rec.get('source_Main_CPU_max',0),c.processorCycles)
        # Drain the actual published native VRAM/CHR/audio pipeline. Omitting
        # NMI leaves Block_RepFlag behind a forever-full VRAM queue, which is
        # not a valid brick-cleanup model. This has no native PPU-time claim.
        n=NesMPU(memory=q.m,pc=0x5b00);n.sp=253;n.nmi()
        for _ in range(100000):
            if n.pc==0x5b00 and n.sp==253:break
            n.step()
        else:raise AssertionError(('Source NMI timeout',hex(n.pc)))
        assert q.get('MmDeathFlag')==0 and q.get('GameEngineSubroutine')==8,('No staged death/transition',task,rec,dict(x=q.get('Player_X_Position'),page=q.get('Player_PageLoc'),y=q.get('Player_Y_Position'),camera=q.get('ScreenLeft_X_Pos'),parser=q.get('AreaParserTaskNum')))
        return writes
    NesMPU.step=step
    results=[]
    try:
        for _ in range(30):main()
        assert q.get('M3Form')==0 and quiet(q)
        for task in PLAN:
            assert q.get('M3Form')==task['form'],('Carried earned form',task,q.get('M3Form'))
            # Wait for the naturally evolving source random register; never
            # reseed it or grant a requested form directly.
            wait=0
            if task['kind']=='pickup'and task['to']>1:
                while q.get('PseudoRandomBitReg',2)%5+2!=task['to']:
                    main();wait+=1;assert wait<512,'Finite genuine random-classification wait'
            arena(q,task);rec=dict(name=task['name'],kind=task['kind'],age=0,collect=0,rng_wait=wait,form_before=q.get('M3Form'),rise_seen=0,jump=False,duck=False,fly=False,wag=False,hop=False,swim=False,statue=False,protected=False,throws=0,peakY=176)
            kind=task['kind'];life=q.get('NumberofLives');invul=q.get('GuestInvulTicks');spawned=False;charged=None;contact=False;shot=False;music=[]
            if kind=='pickup':
                rec['rng_at_birth']=q.get('PseudoRandomBitReg',2);actor(q,46,112,200,5,1);q.set('PowerUpType',0 if task['to']==1 else 1,5);q.invoke('M3PreparePickup',x=5)
                assert q.get('InvPickup',5)==208+task['to']and q.get('InvPickupOwner',5)==17
            elif kind in ['star','life']:actor(q,46,112,184,5,128);q.set('PowerUpType',2 if kind=='star'else 3,5)
            for age in range(1,1101):
                rec['age']=age;button=0
                if kind=='jump':button=128 if 8<=age<16 else 0
                elif kind=='head':button=4 if 4<=age<16 else 128 if 22<=age<30 else 0
                elif kind in ['shot','tail','tailblock']:
                    button=(2 if task.get('face',1)==2 else 1)if 4<=age<8 else 64 if 8<=age<12 else 0
                elif kind=='flight':
                    if charged is None:
                        if q.get(N['Power'])==127:charged=age;rec['power127_at']=age;button=193
                        else:button=65
                    elif age-charged<8:button=193
                    elif 12<=age-charged<20 and(age-charged)%4<2:button=128
                elif kind=='swim':button=129 if 8<=age<18 else 136 if 24<=age<40 else 130 if 45<=age<55 else 0
                elif kind=='statue':
                    button=68 if 8<=age<12 else 4 if 12<=age<65 else 0
                    if q.get(N['Statue'])and not spawned:actor(q,6);spawned=True;rec['contact_form']=q.get('M3Form')
                writes=main(button);music.extend(w['value']for w in writes if w['address']==address(b,'AreaMusicQueue'))
                assert q.get('M3Variant')==var and q.get('CrossoverBehaviorVersion')==mode
                assert q.get('M3Form')==(task.get('to')if kind=='hurt'and rec.get('Injury',0)else task['form'])or kind=='pickup',('Unexpected form change',task,age,q.get('M3Form'))
                rec['jump']|=q.get('Player_State')!=0;rec['duck']|=q.get('CrouchingFlag')!=0;rec['fly']|=q.get(N['FlyTime'])>0;rec['wag']|=q.get(N['WagCount'])>0;rec['hop']|=q.get(N['FrogHopCnt'])>0;rec['swim']|=q.get(N['InWater'])>0 and q.get('Player_State')!=0;rec['statue']|=q.get(N['Statue'])>0
                rec['peakY']=min(rec['peakY'],q.get('Player_Y_Position'))
                if kind=='flight'and age<150 and age%8==0:rec.setdefault('run_flight_path',[]).append([age,q.get('Player_X_Position'),q.get('Player_PageLoc'),q.get('Player_Y_Position'),q.get('Player_State'),q.get(N['Power']),q.get(N['FlyTime']),q.get('Block_Buffer_1',11*16+(q.get('Player_X_Position')>>4))])
                if kind=='pickup'and q.get('Enemy_Flag',5):rec['rise_seen']+=1
                if kind in ['shot','tail','statue']and(q.get('Enemy_State',0)&32 or q.get('Enemy_Flag',0)==0):rec['protected']|=kind=='statue';rec['defeated']=True
                if kind=='shot':
                    shot|=any(q.get('M3ShotKind',i)>0 for i in range(2));rec['live_shot_seen']=shot
                    if age<64 and age%4==0:rec.setdefault('shot_path',[]).append([age,q.get('M3ShotKind',1),q.get('M3ShotX',1),q.get('M3ShotPage',1),q.get('M3ShotY',1),q.get('M3ShotVY',1),q.get('Enemy_X_Position',0),q.get('Enemy_Y_Position',0)])
                if kind=='hurt'and rec.get('Injury',0)and not contact:q.set('Enemy_Flag',0,0);q.set('Enemy_CollisionBits',0,0);contact=True
                if kind=='star':
                    if q.get('StarInvincibleTimer')and not spawned:actor(q,6);spawned=True;rec['star_grant_at']=age
                    if rec.get('StarContact',0):rec['protected']=True
                complete=False
                if kind=='pickup':complete=rec['collect']==1 and q.get('M3Form')==task['to']and q.get('M3Growth')==q.get('M3Poof')==0 and quiet(q)and age>=50
                elif kind=='jump':complete=rec['jump']and quiet(q)and age>=60
                elif kind=='head':complete=rec['duck']and q.get('Block_Buffer_1',7*16+7)==0 and quiet(q)and age>=100
                elif kind in ['shot','tail']:complete=rec.get('defeated',False)and(kind!='shot'or shot)and quiet(q)and age>=90
                elif kind=='tailblock':complete=q.get('Block_Buffer_1',10*16+8)==0 and quiet(q)and age>=100
                elif kind=='flight':complete=rec['fly']and rec['wag']and charged is not None and quiet(q)and age-charged>270
                elif kind=='swim':
                    if age==90:q.set('AreaType',1)
                    complete=rec['swim']and quiet(q)and age>=150
                elif kind=='statue':complete=rec['statue']and rec['protected']and q.get(N['Statue'])==0 and quiet(q)and age>=100
                elif kind=='star':complete=rec['protected']and q.get('StarInvincibleTimer')==0 and rec.get('AreaMusic',0)>0 and quiet(q)
                elif kind=='life':complete=q.get('NumberofLives')==life+1 and q.get('FloateyNum_Control',5)==0 and rec.get('LifeIncrement',0)==1 and quiet(q)
                elif kind=='hurt':complete=contact and q.get('M3Form')==task['to']and q.get('GuestInvulTicks')==q.get('InjuryTimer')==0 and quiet(q)
                assert q.get('NumberofLives')==life+int(kind=='life'and rec.get('LifeIncrement',0)>0),'Exact physical life credit only'
                if complete:break
            else:raise AssertionError(('Finite source case',task,rec,dict(form=q.get('M3Form'),x=q.get('Player_X_Position'),page=q.get('Player_PageLoc'),y=q.get('Player_Y_Position'),state=q.get('Player_State'),fly=q.get(N['FlyTime']),power=q.get(N['Power']),statue=q.get(N['Statue']),injury=q.get('InjuryTimer'),invul=q.get('GuestInvulTicks'),enemy=q.get('Enemy_State',0))))
            rec.update(updates=age,form_after=q.get('M3Form'),music_requests=music,lives_before=life,lives_after=q.get('NumberofLives'))
            results.append(rec);rec=None
    finally:NesMPU.step=origin
    return dict(passed=True,native_run=False,mode=mode,variant=var,cases=len(results),complete_GameLoop_calls=calls,records=results,
        cold_seed='Executed genuine FinializeMarioInit prefix; no selected RNG value or phase reset',scope='Actual complete assembled Main and native pickup/48-rise/collect/move/combat/injury/timer/popup owners. Typed map/actor/external neutral pose setup only; no acquired form, private physics, P-meter, star/life, injury, kill or RNG outcome writes. Not native menu/PPU/IRQ/deadline proof.')

def prepare(b,identity,output,source):
    fixture=R/'tests/current-smb3-powerups.lua';text=fixture.read_text();guard=R/'tests/current-mike-powerups-v2.lua';g=guard.read_text()
    start='-- All callback registration is startup-static. No callback adds/removes callbacks.';end="hook('DmaComplete',function()\n if not imagePending"
    oldend='emu.addEventCallback(function()\n if not entered'
    assert text[text.index(start):text.index(end)]==g[g.index(start):g.index(oldend)],'Literal original strict hardware guard'
    assert 'removeMemoryCallback'not in text and text.count('emu.write(')==2 and not set(ALLOWED)&set(BANS)
    # All addresses, including bare callback ranges and dynamic scoped native
    # names, must resolve before Mesen can register any callback.
    names=set(ALLOWED)|set(BANS)|set(N.values())|set(re.findall(r"(?<![A-Za-z_])[rw]\('([A-Za-z_][A-Za-z_0-9:]*)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
    names|=set(re.findall(r"'([A-Za-z_][A-Za-z_0-9:]*)'",text))&set(b['syms'])
    ram={n:address(b,n)for n in names};assert all(isinstance(v,int)for v in ram.values())
    h,_=hooks(b);menu,character,variant_name,var=BASE[identity];assert character==17 and variant_name=='M3Variant'
    scope='Actual physical source-classified48-update suit emergence/collection and carried forms0..6; source movement/crouch/headbrick/tail enemy+brick/fire+hammer both directions/P-meter flight+wag/Frog hop+swim/Tanooki statue contact+release/Star contact+expiry/physical1Up/real injury cleanup. Typed flat arena, actor/classification/neutral external pose and water-room setup; no acquired form, native private physics, RNG, P-meter, timers, lives, health, injury or enemy outcome seeds. No natural question-block reveal/drop eligibility/world route, every-pixel/art/palette/melody fidelity, all terrain/capacity/exhaustion or universal timing claim.'
    cfg=dict(ROM_sha256=EXPECTED,identity=identity,character=17,menu=menu,variant=var,mode=1,plan=PLAN,native=N,ram=ram,hooks=h,scope=scope,
        navigation=navigation(b['raw'],lambda n:location(b,n),menu),setup_allowed={n:True for n in ALLOWED},resource_bans={n:True for n in BANS},
        dma_store_return=address(b,'PostDmaMaskEnable'),smc=[address(b,n)+1 for n in ['NextBank_SMC','SafecallA_SMC','SafereturnA_SMC','FarcallJmpTarget_SMC']]+[address(b,'FarcallJmpTarget_SMC')+2],
        metatiles={n:dict(bank=(location(b,n)-16)//8192,offset=(location(b,n)-16)%8192)for n in ['MTileTopLeft','MTileTopRight','MTileBotLeft','MTileBotRight','MTileAttribute']})
    def ascii_only(v):
        if isinstance(v,str):assert v.isascii(),('Lua config must be ASCII',v)
        elif isinstance(v,dict):
            for k,x in v.items():ascii_only(k);ascii_only(x)
        elif isinstance(v,list):
            for x in v:ascii_only(x)
    ascii_only(cfg);serialized=lua(cfg);assert not re.search(r'\\u[0-9a-fA-F]{4}',serialized)
    out=output.resolve();assert out.is_relative_to(B)and not out.exists();out.mkdir()
    put(out/'config.json',cfg);put(out/'source-controls.json',dict(source,hardware_guard_literal_exact=True,all_bare_dynamic_literal_RAM_bound=True,ASCII_config=True,Lua_VM_executed=False,resource_write_bans=BANS))
    (out/'run.lua').write_text('CURRENT_SMB3_POWERUPS='+serialized+'\ndofile([=['+fixture.as_posix()+']=])\n',newline='\n')
    argv=[sys.executable,'-B',str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out/'native'),str(out/'run.lua'),str(ROM),'--timeout','1200','--option=--doNotSaveSettings','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false']
    put(out/'command.json',dict(PREPARED_DO_NOT_RUN=True,ROOT_owns_native_lease=True,argv=argv))
    paths={ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),fixture,Path(__file__),guard,B/'current_smb3_source_controls.json',R/'tools/audit/current_shared_star_life_prepare_v1.py',R/'tools/audit/current_smb3_injury_candidate_v1.py',B/'current_smb3_timer_build.json',B/'current_smb3_timer_dispatch.s',B/'current_smb3_timer.patch',B/'current_smb3_injury_counterexample.json',B/'current_smb3_qualified_preparer.py',B/'current_smb3_prepare_metadata_negative.json'}
    paths|={R/'tools/audit'/n for n in ['run_mesen_isolated.py','capture_budget.py']};paths|={R/'tools/run_mesen.py',Path('C:/Mesen2/Mesen.exe'),Path('C:/Mesen2/MesenCore.dll'),Path('C:/Mesen2/settings.json')}
    paths|={R/'src'/n for n in ['smb3_mario_pickups.s','smb3_mario_state.inc','smb3_mario_core.s','smb3_mario_motion.s','smb3_mario_combat.s','smb3_mario_dispatch.s','smb3_mario_render.s','smb3_mario_world.s','smb3_native_controller.inc','smb3_native_projectiles.inc','smb3_projectile_damage.s','game.s','reset.s','collision.s','powerup.s']if(R/'src'/n).is_file()}
    paths|={out/n for n in ['config.json','source-controls.json','run.lua','command.json']}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f and('py65'in f or str(R/'tools/audit')in f)and Path(f).is_file():paths.add(Path(f))
    put(out/'prepared-not-run.json',dict(status='PREPARED_DO_NOT_RUN',passed=False,native_run=False,goal_complete=False,ROM_sha256=EXPECTED,identity=identity,mode=1,variant=var,scope=scope,
        caps=dict(wall_frames=8000,updates=5000,host_seconds=1200,files=64,bytes=2000000000,PNGs=8,perframe_files=0),
        setup='GameLoop+5/NmiDisableFF only: typed flat logical+visible map, actors, source-RNG classified emerging reward, neutral external pose and water-room setup. Native private M3 controller bytes and earned resources are strictly banned. Cold compiled19-node BFS and actual alternate/Hard readbacks.',
        source_qualification='Four actual complete GameLoop+full NMI source campaigns on immutable ROM; real48-tick rise/physical grants; both modes/variants. Memory bus does not emulate native PPU deadlines or physical DMA.',
        bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]))
    return dict(identity=identity,cases=len(PLAN),ready=str(out/'prepared-not-run.json'),ready_sha256=sha(out/'prepared-not-run.json'))

def main():
    global EXPECTED
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-only',action='store_true');p.add_argument('--prepare',action='store_true');a=p.parse_args()
    build=json.loads((B/'current_smb3_timer_build.json').read_text());assert build['passed']and build['parent_sha256']=='5a0a37a97e95ce3c1086f91f6000ad0157bb477f923027d39f0342d9389e6db2';EXPECTED=build['candidate_sha256']
    assert sha(ROM)==EXPECTED;b=scoped_load(ROM);out=B/'current_smb3_source_controls.json'
    if a.prepare:
        source=json.loads(out.read_text());assert source['passed']and source['ROM_sha256']==EXPECTED
        assert source['fixture_sha256']==sha(R/'tests/current-smb3-powerups.lua'),'Qualified fixture byte identity'
        predecessor=B/'current_smb3_qualified_preparer.py';assert sha(predecessor)==source['tool_source_sha256']
        def source_ast(path):
            nodes=ast.parse(Path(path).read_text()).body
            nodes=[n for n in nodes if not isinstance(n,(ast.Import,ast.ImportFrom))and not(isinstance(n,ast.FunctionDef)and n.name in ['main','prepare'])]
            return ast.dump(ast.Module(body=nodes,type_ignores=[]),include_attributes=False)
        assert source_ast(predecessor)==source_ast(__file__),'Every source campaign/control/helper/global AST remains exactly qualified'
        source=dict(source,metadata_only_successor=dict(qualified_preparer_sha256=sha(predecessor),current_preparer_sha256=sha(__file__),source_campaign_control_helper_global_AST_exact=True,change='Word-boundary address regex excludes nr aliases; source execution unmodified. Additional prepare-only qualification binding.'))
        print(json.dumps([prepare(b,n,B/('current-smb3-timer-'+n+'-hard-items-v1'),source)for n in ['mario3','luigi3']]));return
    result=dict(passed=False,native_run=False,ROM_sha256=EXPECTED,tool_source_sha256=sha(__file__),fixture_sha256=sha(R/'tests/current-smb3-powerups.lua'),records=[])
    try:
        result['injury_controls']=injury_controls(b)
        for mode,var in [(0,0),(1,0),(0,1),(1,1)]:result['records'].append(campaign(b,mode,var))
        result.update(passed=True)
    except Exception as e:
        result.update(error=repr(e),traceback=traceback.format_exc());put(out,result);raise
    put(out,result);print(json.dumps(dict(passed=True,campaigns=len(result['records']),source_calls=sum(r['complete_GameLoop_calls']for r in result['records']))))

if __name__=='__main__':main()

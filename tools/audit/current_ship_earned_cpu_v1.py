"""Finite actual-GameLoop ship pickup/bar/Bell campaigns; no Mesen launch."""
from pathlib import Path
import argparse,hashlib,json
from link_pit_rygar_sophia_audit_cpu import Arena,scoped_load
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

ROOT=Path(__file__).resolve().parents[2]
ROM=ROOT/'build/kirby-mike-polish-production.nes'
EXPECTED='5a0a37a97e95ce3c1086f91f6000ad0157bb477f923027d39f0342d9389e6db2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ACTOR='Enemy_Flag Enemy_ID Enemy_State Enemy_BoundBoxCtrl Enemy_X_Position Enemy_PageLoc Enemy_Y_Position Enemy_Y_HighPos Enemy_X_Speed Enemy_Y_Speed Enemy_Y_MoveForce Enemy_MovingDir Enemy_SprAttrib EnemyOffscrBitsMasked Enemy_CollisionBits MmEnemyHealthLo MmEnemyHealthHi MmEnemyFlash RgEnemyStun PowerUpType InvPickupOwner InvPickup'.split()
ENV='Block_Buffer_1 MmSolidTerrain MmBrickHealth ScrollLock ScreenLeft_X_Pos ScreenLeft_PageLoc ScreenRight_X_Pos ScreenRight_PageLoc ScrollThirtyTwo AreaParserTaskNum'.split()
PICKUP='PnCapActive PnCapX PnCapPage PnCapY PnCapAge PnCapFraction PnCapVX PnCapVXF PnCapHits PnCapChange PnCapAnim'.split()

def plans(v):
    if v==0:
        p=[dict(name='cold-shot',kind='fire',limit=130,image=True)]
        for cell,name,field,value in [(1,'speed','VvSpeed',1),(2,'missile','VvMissile',1),(3,'double','VvGun',2),(4,'laser','VvGun',1),(5,'option1','VvOptions',1),(5,'option2','VvOptions',2)]:
            p.append(dict(name=name,kind='gear',cell=cell,field=field,value=value,limit=250,fire=True,image=name in ['double','laser','option2']))
        p += [dict(name='option-cap-refusal',kind='gear',cell=5,field='VvOptions',value=2,refuse=True,limit=120),dict(name='shield5',kind='gear',cell=6,field='VvShield',value=5,limit=180,image=True)]
        p += [dict(name='shield-contact'+str(i+1),kind='contact',shield=4-i,limit=40)for i in range(5)]
        return p
    p=[dict(name='cold-shot',kind='fire',limit=130)]
    p += [dict(name='speed'+str(i),kind='gear',cell=1,field='VvSpeed',value=i,limit=180)for i in range(1,5)]
    p += [dict(name='speed-cap-refusal',kind='gear',cell=1,field='VvSpeed',value=4,refuse=True,limit=120)]
    p += [dict(name=n,kind='gear',cell=c,field='VvGun',mask=m,value=z,fire=True,limit=250,image=True)for c,n,m,z in [(2,'missile',8,8),(4,'tail-double',192,64),(8,'alternate-gun',192,128)]]
    cap=4 if v==1 else 3
    p += [dict(name='option'+str(i),kind='gear',cell=16,field='VvGun',mask=7,value=i,limit=250,fire=i==cap,image=i==cap)for i in range(1,cap+1)]
    p += [dict(name='option-cap-refusal',kind='gear',cell=16,field='VvGun',mask=7,value=cap,refuse=True,limit=150),dict(name='shield15',kind='gear',cell=64,field='PnAux',value=15,limit=220)]
    p += [dict(name='shield-contact'+str(i+1),kind='contact',shield=14-i,limit=40)for i in range(15)]
    p += [dict(name='power-down',kind='gear',cell=32,field='VvGun',value=0,reset=True,limit=250),dict(name='roulette',kind='bell',pickup=5,limit=200),dict(name='gold-score',kind='bell',pickup=6,limit=100),dict(name='blue-bomb',kind='bell',pickup=7,limit=280,image=True),dict(name='red-three',kind='bell',pickup=9,limit=1800,image=True),dict(name='big-duration',kind='bell',pickup=8,limit=1750,image=True),dict(name='white-life',kind='bell',pickup=10,limit=100)]
    return p

def world(q):return q.get('VvObjX')-8+q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc')
def score(q):return sum(q.get('Player1ScoreDisplay',i)*10**(5-i) for i in range(6))
def arena(q):
    for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
    for i in range(6):q.set('Enemy_Flag',0,i);q.set('Enemy_CollisionBits',0,i)
    q.put(ScrollLock=1,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,ScrollThirtyTwo=0,AreaParserTaskNum=0)

def actor(q,kind,x,y,slot=0,power=0):
    d=dict(Enemy_Flag=1,Enemy_ID=kind,Enemy_State=128 if kind==46 else 0,Enemy_BoundBoxCtrl=3 if kind==46 else 9,Enemy_X_Position=x&255,Enemy_PageLoc=x>>8,Enemy_Y_Position=y,Enemy_Y_HighPos=1,Enemy_X_Speed=0,Enemy_Y_Speed=0,Enemy_Y_MoveForce=0,Enemy_MovingDir=2,Enemy_SprAttrib=0,EnemyOffscrBitsMasked=0,Enemy_CollisionBits=0,MmEnemyHealthLo=0,MmEnemyHealthHi=0,MmEnemyFlash=0,RgEnemyStun=0)
    if kind==46:d.update(PowerUpType=power,InvPickupOwner=255,InvPickup=252)
    for n,v in d.items():q.set(n,v,slot)

def capsule(q,kind):
    for n,v in dict(PnCapActive=kind,PnCapX=world(q)&255,PnCapPage=world(q)>>8,PnCapY=q.get('Player_Y_Position')+8,PnCapAge=0,PnCapFraction=0,PnCapVX=0,PnCapVXF=0,PnCapHits=4,PnCapChange=0,PnCapAnim=0).items():q.set(n,v,0)

def shots(q,v):
    if v==0:return [(i,q.get('VvObjAnim',i),q.get('VvObjSub',i))for i in range(3,12)if q.get('VvObjAnim',i)]
    return [(i,q.get('PnType',i),q.get('PnActive',i))for i in range(6,28)if q.get('PnActive',i)]

def setup(q,t,rec):
    arena(q)
    rec.update(stage='caps'if t['kind']=='gear'else t['kind'],target=False,age=0,stageAge=0,startLives=q.get('NumberofLives'),startScore=score(q),beforeShield=q.get('VvShield')if rec['variant']==0 else q.get('PnAux'))
    if t['kind']=='contact':actor(q,6,world(q)+4,q.get('Player_Y_Position')-(1 if rec['variant']==0 else 9))
    if t['kind']=='bell':capsule(q,t['pickup'])

def before(q,t,rec):
    v=rec['variant'];stage=rec['stage'];a=rec['stageAge']
    if stage=='caps'and q.get('VvMeter')!=t['cell']and not q.get('Enemy_Flag',5):
        # Both native request0/1 are converted to this capsule by the genuine
        # VvPrepareDispatch. Its static+9..21 box crosses the ship point/core.
        actor(q,46,world(q),q.get('Player_Y_Position')-(0 if v==0 else 8),5,1)
    if stage=='roulette'and a>=12 and q.get('VvMeter')&(~q.get('VvFlags')&255):return 64
    if stage=='buy':return 64 if a>=4 else 0
    if stage=='fire':return 128 if 5<=a<40 else 0
    if stage in ['blue','red']:
        return 128 if a>=5 and not q.get('PnActive',27)and not q.get('VvPrevious')&128 else 0
    return 0

def after(q,t,rec):
    v=rec['variant'];rec['age']+=1;rec['stageAge']+=1;s=rec['stage'];a=rec['stageAge']
    active=shots(q,v);rec['seen_types']=sorted(set(rec['seen_types'])|{(z[1],z[2])for z in active})
    if active:rec['live']+=1
    if s in ['fire','blue','red']and not rec['target']and active:
        i=active[0][0]
        if v==0:x=q.get('VvObjX',i)-8+q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc');y=q.get('VvObjY',i)+32
        else:x=q.get('PnX',i)+q.get('ScreenLeft_X_Pos')+256*q.get('ScreenLeft_PageLoc');y=q.get('PnY',i)+15
        if 8<=x+16<232 and 32<=y<200:actor(q,6,x+16,y);rec['target']=True
    def stage(n):rec['stage']=n;rec['stageAge']=0
    if s=='caps'and q.get('VvMeter')==t['cell']:stage('buy')
    elif s=='buy':
        if a>=8:
            assert q.get(t['field'])&t.get('mask',255)==t['value'],(t,q.get(t['field']),q.get('VvFlags'))
            if t.get('refuse'):
                assert q.get('VvMeter')==t['cell'];return True
            assert q.get('VvMeter')==0
            if t.get('reset'):assert q.get('VvSpeed')==0 and not q.get('VvGun')
            if t.get('fire'):stage('fire')
            else:return True
    elif s=='fire'and a>=130:
        assert rec['live'] and rec['defeats'] and not active,(t,rec,active);return True
    elif s=='contact'and a>=20:
        shield=q.get('VvShield')if v==0 else q.get('PnAux')
        assert shield==t['shield']and rec['defeats']==1 and not q.get('MmDeathFlag'),(t,shield,rec)
        return True
    elif s=='bell':
        k=t['pickup'];flag=q.get('PnBellFlags')
        if k==5 and flag&16:stage('roulette')
        elif k==6 and a>=50:assert rec['takes']==1 and score(q)==rec['startScore']+500;rec['score_delta']=score(q)-rec['startScore'];return True
        elif k==7 and flag&1:stage('blue')
        elif k==9 and flag&4:assert q.get('PnRedRemaining')==3;stage('red')
        elif k==8 and flag&2:stage('big')
        elif k==10 and a>=20:assert q.get('NumberofLives')==rec['startLives']+1;return True
    elif s=='roulette':
        rec['roulette'].add(q.get('VvMeter'))
        if not q.get('PnBellFlags')&16 and a>=13:assert len(rec['roulette'])>=3;return True
    elif s=='blue'and not q.get('PnBellFlags')&1 and a>10:
        assert rec['specialTicks']>0 and rec['defeats']>0;return True
    elif s=='red'and not q.get('PnBellFlags')&4 and a>10:
        assert q.get('PnRedRemaining')==0 and rec['red_fires']==3;return True
    elif s=='big':
        rec['skins'].add(q.get('PnSkin'))
        if q.get('PnSkin')!=v and not rec['target']:actor(q,6,world(q)+4,q.get('Player_Y_Position')-9);rec['target']=True
        if not q.get('PnBellFlags')&2 and a>20:
            assert q.get('PnSkin')==v and rec['defeats']==1 and any(s!=v for s in rec['skins']);return True
    assert rec['age']<t['limit'],('finite source stage',t,rec,q.get('VvMeter'),q.get('PnBellFlags'),q.get('PnActive',27),{n:q.get(n,5)for n in ['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_Y_Position','PowerUpType']},{n:q.get(n)for n in ['Player_X_Position','Player_Y_Position','VvObjX','VvObjY']} )

def campaign(b,v,mode):
    assert b['raw'][location(b,'InvItemCount')+18]==0
    for n in ['InvSelectable','InvInitialAmmo','InvMaxAmmo']:
        assert b['raw'][location(b,n)+288:location(b,n)+304]==bytes(16)
    q=Arena(b,18);q.put(VvVariant=v,PlayerStatus=0,CrossoverBehaviorVersion=mode,OperMode_Task=3,AreaType=1,Player_X_Position=80,Player_PageLoc=0,Player_Y_Position=120,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScrollLock=1)
    prepared=[]
    for requested in [0,1]:
        q.set('PowerUpType',requested,5);q.invoke('VvPrepareDispatch',x=5)
        got=[q.get(n,5)for n in ['PowerUpType','InvPickupOwner','InvPickup']]
        assert got==[1,255,252];prepared.append(dict(requested=requested,actual_prepared_type_owner_item=got))
    q.array('GameTimerDisplay',[3,9,9]);arena(q)
    end=address(b,'E_GroundArea2')-1;assert b['raw'][location(b,'E_GroundArea2')-1]==255;q.put(EnemyDataLow=end&255,EnemyDataHigh=end>>8,EnemyDataOffset=0)
    rec=None;events=[];names=['VvPickupDispatch','VvTake','PnTakeKind','VvBuyUpgrade','PnNativeGear','VvWeapons','PnWeapons','VvBody','PnBody','ShellOrBlockDefeat','Pb9a86','PnBombWorldDamage','Pn81fa']
    pcs={(address(b,n),(location(b,n)-16)//8192):n for n in names};original=NesMPU.step
    def step(cpu):
        bank=q.m.banks[(cpu.pc-0x8000)//8192]if cpu.pc>=0x8000 else-1;n=pcs.get((cpu.pc,bank))
        if rec and n:
            rec['owners'][n]=rec['owners'].get(n,0)+1
            if n=='VvPickupDispatch':
                assert cpu.x==5 and q.get('Enemy_ID',5)==46 and q.get('Enemy_State',5)>=128 and q.get('PowerUpType',5)<2,(cpu.x,q.get('Enemy_ID',5),q.get('Enemy_State',5),q.get('PowerUpType',5))
                rec['collections']+=1
            if n in ['VvTake','PnTakeKind']:rec['takes']+=1
            if n=='ShellOrBlockDefeat':rec['defeats']+=1
            if n=='Pb9a86':rec['red_fires']+=1
            if n=='PnBombWorldDamage':rec['specialTicks']+=1
            if n=='Pn81fa':
                now=q.get('PnBigTimerLo')+256*q.get('PnBigTimerHi')
                assert now==1279-rec['big_ticks'],('Actual full Big timer before native decrement',now,rec['big_ticks'])
                rec['big_ticks']+=1
        original(cpu)
    def update(bits):
        q.set('SavedJoypadBits',bits);q.invoke('GameLoop')
        ptr=address(b,'VRAM_Buffer1');q.put(NmiR0=ptr&255,NmiR1=ptr>>8,VRAM_Buffer_AddrCtrl=0);q.invoke('PnPaletteScreenUpdate');q.put(VRAM_Buffer1=0,VRAM_Buffer1_Offset=0)
        assert q.get('GameEngineSubroutine')==8 and not q.get('MmDeathFlag'),('source life',v,mode,q.get('GameEngineSubroutine'))
    NesMPU.step=step
    try:
        for _ in range(30):update(0)
        assert q.get('VvMeter')==0 and q.get('VvSpeed')==0 and q.get('VvGun')==0
        for t in plans(v):
            rec=dict(name=t['name'],variant=v,collections=0,takes=0,defeats=0,red_fires=0,specialTicks=0,big_ticks=0,live=0,seen_types=[],owners={},roulette=set(),skins=set())
            setup(q,t,rec)
            while True:
                bits=before(q,t,rec);update(bits)
                if after(q,t,rec):break
            assert q.get('PlayerStatus')==0 and (v==0 or q.get('PnMissing')==0)
            if t['kind']=='gear':assert rec['collections']>0
            if t['kind']=='bell':assert rec['takes']==1
            if t.get('pickup')==8:assert rec['big_ticks']==1279
            rec['final']={n:q.get(n)for n in ['VvMeter','VvSpeed','VvGun','VvMissile','VvOptions','VvShield','PnAux','PnSkin','PnBellFlags','PnRedRemaining','NumberofLives']}
            rec['roulette']=sorted(rec['roulette']);rec['skins']=sorted(rec['skins']);events.append(rec)
    finally:NesMPU.step=original
    return dict(passed=True,variant=v,mode=mode,GameLoop_calls=30+sum(r['age']for r in events),actual_VvPrepareDispatch_controls=prepared,no_standard_inventory_IDs=True,cases=events)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--variant',type=int,choices=range(4),required=True);p.add_argument('--mode',type=int,choices=[0,1],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    assert sha(ROM)==EXPECTED and not a.output.exists();b=scoped_load(ROM)
    z=campaign(b,a.variant,a.mode);z.update(ROM_sha256=EXPECTED,native_run=False,Lua_executed=False,tool_sha256=sha(Path(__file__)),scope=__doc__)
    a.output.write_text(json.dumps(z,indent=2)+'\n',newline='\n');print(json.dumps(dict(passed=True,path=str(a.output),GameLoops=z['GameLoop_calls'],cases=len(z['cases']),sha256=sha(a.output))))

if __name__=='__main__':main()

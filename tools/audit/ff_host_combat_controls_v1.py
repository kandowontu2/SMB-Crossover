"""Actual RAM3 FF combat instructions and genuine native consumers, offline only.

The RAM image is explicitly fixture-preloaded. No loader, Main, native video,
resource allocation or installed-route claim follows from these controls.
"""
from pathlib import Path
import argparse, copy, hashlib, itertools, json, re, sys, traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_ram3_execution_controls_v2 as E
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def bundle(packet):
    b=qualified(E.P/'candidate.nes')
    # Parse true scoped RAM3 symbols without assigning its segment IDs to ROM.
    scopes={};symbols=[]
    for line in (packet/'kernel.dbg').read_text().splitlines():
        kind,_,tail=line.partition('\t')
        if kind not in ['scope','sym']:continue
        d=dict(x.split('=',1)for x in tail.split(',')if '='in x)
        if kind=='scope':scopes[d['id']]=d
        elif 'val'in d:symbols.append(d)
    def prefix(k):
        s=scopes.get(k,{})
        return '::'.join(x for x in ([prefix(s['parent'])]if'parent'in s else[])+[s.get('name','').strip('"')]if x)
    for s in symbols:
        n=s['name'].strip('"');p=prefix(s.get('scope'))
        b['syms'][p+'::'+n if p else n]=dict(s)
    b['packet']=packet
    return b

def setv(m,n,v,i=0):m[address(m.bundle,n)+i]=v
def get(m,n,i=0):return m[address(m.bundle,n)+i]
def put(m,**v):
    for n,z in v.items():setv(m,n,z)
def make(b):
    m=E.make(b,True);m.ram[3][:]=(b['packet']/'ram3.bin').read_bytes()
    # Legal, empty typed combat environment; non-owner RAM banks remain poison.
    put(m,TimerControl=0,MmDeathFlag=0,GamePauseStatus=0,ObjectOffset=4,
        ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,Player_State=0,
        CrossoverBehaviorVersion=1,Square1SoundQueue=0,Square2SoundQueue=0)
    for n in ['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc',
              'Enemy_Y_Position','Enemy_Y_HighPos','Enemy_BoundBoxCtrl',
              'MmEnemyHealthLo','MmEnemyHealthHi','MmEnemyFlash','FloateyNum_Control']:
        for i in range(6):setv(m,n,0,i)
    run(m,'FfEnsure')
    m.writes.clear();m.ram_writes.clear()
    return m

def run(m,name,**kw):return E.run(m,name,True,**kw)
def actor(m,x=0,kind=None,px=144,page=0,y=160,box=3,state=0,flag=1,high=1):
    if kind is None:kind=address(m.bundle,'Goomba')
    for n,v in [('Enemy_Flag',flag),('Enemy_ID',kind),('Enemy_State',state),
                ('Enemy_X_Position',px),('Enemy_PageLoc',page),('Enemy_Y_Position',y),
                ('Enemy_Y_HighPos',high),('Enemy_BoundBoxCtrl',box)]:setv(m,n,v,x)
def hp(m,x=0):return get(m,'MmEnemyHealthLo',x)+256*get(m,'MmEnemyHealthHi',x)
def image(m):return bytes(m[:0x100]+m[0x200:0x8000]),[bytes(a)for a in m.ram]
def flags():return [0x30|sum(((n>>i)&1)*bit for i,bit in enumerate([1,2,4,8,64,128]))for n in range(64)]
def app_writes(m):return [(a,v)for a,v in m.writes if not 0x100<=a<0x200 and not 0x5114<=a<=0x5117 and not 0x15a<=a<0x17b]

def fresh_foreign(b):
    rows=[]
    for owner in [0,1,9,21,23,32,255]:
        m=make(b);put(m,SelectedCharacter=owner,FfReady=0x77,FfVariant=3)
        before=get(m,'FfReady');run(m,'FfHostFresh')
        rows.append(dict(owner=owner,before=before,after=get(m,'FfReady'),writes=app_writes(m)))
    assert all(z['after']==z['before']for z in rows),('foreign FfReady mutation',rows)
    return dict(cases=len(rows),rows=rows)

def geometry(b):
    at=location(qualified(E.P/'candidate.nes'),'BoundBoxCtrlData')
    raw=b['raw'][at:at+84];rows=[]
    for box,px,page,y in itertools.product(range(21),[0,1,7,127,248,254,255],[0,1,255],[0,1,224,240,247,248,255]):
        m=make(b);actor(m,box=box,px=px,page=page,y=y)
        c,tr,_=run(m,'FfHostTarget')
        l,t,r,bot=raw[box*4:box*4+4];l=l-256 if l&128 else l
        want=y+t<256
        assert bool(c.p&1)==want,('native bbox eligibility',box,px,page,y)
        if want:
            wx=(page*256+px+l)&65535
            actual=[get(m,n)for n in ['FfTargetX','FfTargetPage','FfTargetY','FfTargetW','FfTargetH']]
            assert actual==[wx&255,wx>>8,y+t,r-l+1,bot-t+1],('inclusive native box',box,actual)
        assert c.x==0
        rows.append([box,px,page,y,int(want)])
    reject=[]
    for field,value in [('Enemy_Flag',0),('Enemy_Flag',128),('Enemy_State',32),
                        ('Enemy_Y_HighPos',0),('Enemy_Y_HighPos',2),
                        ('Enemy_BoundBoxCtrl',21),('Enemy_BoundBoxCtrl',255),
                        ('Enemy_State',2),('Enemy_State',4),('Enemy_ID',21),('Enemy_ID',255)]:
        m=make(b);actor(m);setv(m,field,value)
        c,_,_=run(m,'FfHostTarget');assert not c.p&1,(field,value)
        reject.append([field,value])
    for x in [6,7,255]:
        m=make(b);c,_,_=run(m,'FfHostTarget',x=x);assert not c.p&1
    accepted=[]
    for k in list(range(21))+[address(b,'Bowser'),address(b,'BulletBill_CannonVar')]:
        m=make(b);actor(m,kind=k);c,_,_=run(m,'FfHostTarget');assert c.p&1,k;accepted.append(k)
    return dict(world_box_cases=len(rows),accepted_ids=accepted,rejected_fields=reject,invalid_slots=3,
                signed_left_page_wrap=True,top_overflow_rejected=True,rows=rows)

def guards(b):
    rows=[]
    for owner,engine,pause,timer,dead in [(n,8,0,0,0)for n in range(34)if n!=22]+[
        (22,e,0,0,0)for e in range(16)if e!=8]+[(22,8,1,0,0),(22,8,3,0,0),(22,8,0,1,0),(22,8,0,0,1)]:
        m=make(b);put(m,SelectedCharacter=owner,GameEngineSubroutine=engine,GamePauseStatus=pause,TimerControl=timer,MmDeathFlag=dead)
        actor(m);put(m,FfAction=1);before=image(m);run(m,'FfHostWeapons')
        assert image(m)==before,('inactive weapons writes',owner,engine,pause,timer,dead)
        rows.append([owner,engine,pause,timer,dead])
    # Active phase even pause bits only: exact native low-bit pause contract.
    m=make(b);put(m,GamePauseStatus=2);c,tr,_=run(m,'FfHostWeapons')
    assert (address(b,'FfWeapons'),3)in tr
    return dict(inactive_cases=len(rows),active_nonpause_bit_pass=True,rows=rows)

def damage(b):
    health=[100,100,100,100,100,200,75,150,100,100,75,75,255,75,100,100,100,200,100,100,50]
    immune=[address(b,n)for n in ['Podoboo','BuzzyBeetle','BulletBill_FrenzyVar','BulletBill_CannonVar']]
    rows=[];native=[]
    for kind,world,value,seed in itertools.product(list(range(21))+[address(b,'Bowser')],range(8),[1,25,75,100,150,200,255],[0,1,255,256,600,1100]):
        # Wide16-bit boundary cases across actual IDs and world-derived init.
        if world not in [0,4,5,6,7] or (kind!=address(b,'Bowser') and world!=0):continue
        m=make(b);actor(m,x=2,kind=kind);put(m,FfDamage=value,WorldNumber=world,ObjectOffset=5)
        setv(m,'MmEnemyHealthLo',seed&255,2);setv(m,'MmEnemyHealthHi',seed>>8,2)
        put(m,DuplicateObj_Offset=3)
        c,tr,_=run(m,'FfHostDamage',x=2)
        if kind in immune:
            assert not c.p&1 and hp(m,2)==seed and get(m,'Enemy_State',2)==0
            want=seed
        else:
            initial=seed or ((600 if world<5 else 900 if world<7 else 1100)if kind==address(b,'Bowser')else health[kind])
            want=max(0,initial-value)
            assert c.p&1 and hp(m,2)==want,('HP exact',kind,world,value,seed,hp(m,2),want)
            assert c.x==2 and get(m,'ObjectOffset')==5
            if want:
                assert get(m,'MmEnemyFlash',2)==2 and get(m,'Square1SoundQueue')==address(b,'Sfx_EnemySmack')
            else:
                target='HandleEnemyFBallCol'if kind==address(b,'Bowser')else'ShellOrBlockDefeat'
                assert any(pc==address(b,target)for pc,tag in tr),('genuine native defeat',kind)
                assert get(m,'Enemy_State',2)&32
                score=9 if kind==address(b,'Bowser')else 1 if kind==address(b,'Goomba')else 6 if kind==address(b,'HammerBro')else 2
                assert get(m,'FloateyNum_Control',2)==score,('native score',kind,get(m,'FloateyNum_Control',2),score)
                if kind==address(b,'Bowser'):
                    assert get(m,'BowserHitPoints')==0 and get(m,'Square2SoundQueue')==address(b,'Sfx_BowserFall')
                assert get(m,'Square1SoundQueue')==address(b,'Sfx_EnemySmack')
                native.append([kind,world,value,seed,score])
        rows.append([kind,world,value,seed,want])
    return dict(HP_cases=len(rows),native_defeat_cases=len(native),rows=rows,defeats=native)

GROUPS=dict(fresh_foreign=fresh_foreign,geometry=geometry,guards=guards,damage=damage)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--packet',type=Path,default=R/'build/final-fantasy-host-combat-v1')
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--only',default=','.join(GROUPS));a=ap.parse_args()
    assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True)
    proof=json.loads((a.packet/'build-proof.json').read_text())
    for p,h in proof['bindings'].items():assert sha(p)==h,p
    b=bundle(a.packet);d=dict(passed=False,native=False,host_Main=False,fixture_RAM3_preloaded=True,checks={},failures={})
    for n in a.only.split(','):
        try:d['checks'][n]=GROUPS[n](b)
        except Exception as e:d['failures'][n]=dict(error=repr(e),traceback=traceback.format_exc())
    d['passed']=not d['failures']
    d['bindings']={**proof['bindings'],str((a.packet/'build-proof.json').resolve()):sha(a.packet/'build-proof.json'),str(Path(__file__).resolve()):sha(__file__)}
    a.output.write_text(json.dumps(d,indent=2)+'\n')
    for p,h in d['bindings'].items():assert sha(p)==h,p
    print(json.dumps(dict(passed=d['passed'],checks=list(d['checks']),failures=d['failures'])))
    assert d['passed']
if __name__=='__main__':main()

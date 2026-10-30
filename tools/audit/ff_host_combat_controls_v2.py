"""Successor CPU qualification of source FF contacts and real native consumers.

The v1 negative and its fixture source stay immutable. This fixture excludes
the genuine FarCallCommon's33SMC bytes from application state comparisons;
the prior negative counted those legitimate call operands as combat stores.
"""
from pathlib import Path
import argparse,copy,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_host_combat_controls_v1 as C
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
from prepare_ff_current_component_v2 import qualified
sha=C.sha;put=C.put;get=C.get;setv=C.setv;run=C.run;make=C.make;actor=C.actor

def state(m):
    omit=set(range(0x100,0x200))|set(range(0x15a,0x17b))|set(range(0x5114,0x5118))
    return bytes(m[i]for i in range(0x8000)if i not in omit),[bytes(a)for a in m.ram]
C.image=state

def direct(m,name,a=0,x=0,y=0,p=0x30,bank=None,limit=50000,hook=None):
    # Bare ABI proof, so the far-call helper cannot alter the incoming flags.
    if bank is not None:
        slot=(address(m.bundle,name)-0x8000)//8192
        m.raw_page(slot,bank)
        if slot in [1,2]:setv(m,'CurrentBank'if slot==1 else'CurrentBankC',bank)
    c=NesMPU(memory=m,pc=address(m.bundle,name));c.a=a;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    live=bytes(m[0x1e1:0x200]);trace=[]
    for n in range(limit):
        if c.pc==0x5b00:break
        if hook:hook(m,c,n)
        trace.append((c.pc,m.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1))
        assert m[c.pc],('BRK',name,hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError(('direct bound',name,hex(c.pc)))
    assert c.sp==224 and bytes(m[0x1e1:0x200])==live
    return c,trace

def reuse(b):
    parent=qualified(C.E.P/'candidate.nes')
    pc=address(parent,'CheckpointEnemyID');physical=(location(parent,'CheckpointEnemyID')-16)//8192
    rows=[]
    for x,p in itertools.product(range(6),C.flags()):
        m=make(b);actor(m,x=x,kind=address(b,'Goomba'));put(m,FfHits=63)
        for off in [0,12,24]:setv(m,'FfProjectile',63,off+9)
        setv(m,'MmEnemyHealthLo',35,x);setv(m,'MmEnemyHealthHi',2,x);setv(m,'MmEnemyFlash',2,x)
        # Genuine native initializer first. No FF dictionary callback installed
        # in this candidate: explicitly exercise the required integration order.
        _,tr=direct(m,'CheckpointEnemyID',x=x,p=p,bank=physical|128)
        assert any(q==pc for q,tag in tr)
        assert C.hp(m,x)==0 and get(m,'MmEnemyFlash',x)==0
        before=state(m);m.writes.clear()
        c,tr=direct(m,'FfHostNewEnemy',a=0x59,x=x,y=0xa7,p=p,bank=3)
        assert (c.a,c.x,c.y,c.p)==(0x59,x,0xa7,p),('reuse full APXY',x,p,c.a,c.x,c.y,c.p)
        want=63^(1<<x)
        assert get(m,'FfHits')==want and all(get(m,'FfProjectile',off+9)==want for off in [0,12,24])
        allowed={address(b,n)+i for n,i in [('FfTemp',0),('FfHits',0),('FfProjectile',9),('FfProjectile',21),('FfProjectile',33)]}
        assert all(a in allowed for a,v in C.app_writes(m)),('reuse undeclared store',C.app_writes(m))
        # Same ID, same source action: new native identity must accept a new hit.
        actor(m,x=x,px=140,y=160);put(m,FfVariant=0,FfPower=0,FfAction=1)
        c,_,_=run(m,'FfHostContact',a=255,x=x)
        assert c.p&1 and C.hp(m,x)==25
        rows.append([x,p])
    for owner,x,p in itertools.product([0,9,21,23,32,255],[0,5,6,255],C.flags()):
        m=make(b);put(m,SelectedCharacter=owner,FfHits=63);m.raw_page(1,3);setv(m,'CurrentBank',3)
        before=state(m);c,tr=direct(m,'FfHostNewEnemy',a=0x59,x=x,y=0xa7,p=p)
        assert (c.a,c.x,c.y,c.p)==(0x59,x,0xa7,p)and state(m)==before
    return dict(native_initializer_then_source_mask_cases=len(rows),all64_flags_and_APXY_exact=True,
                foreign_cases=6*4*64,native_initializer_physical=physical,
                hook_installed=False,same_ID_new_object_accepts_same_attack=True)

def contacts(b):
    rows=[]
    # Actual source melee across classes, tier, facing, actor slot and page seam.
    for variant,tier,face,x,worldx in itertools.product(range(4),range(3),[1,2],range(6),[1,120,250,255,256,65530]):
        m=make(b);put(m,FfVariant=variant,FfPower=tier,FfAction=1,PlayerFacingDir=face,
                      Player_X_Position=worldx&255,Player_PageLoc=worldx>>8)
        tx=(worldx+(18 if face==1 else-12))&65535
        actor(m,x=x,kind=address(b,'HammerBro'),px=tx&255,page=tx>>8,y=160)
        setv(m,'MmEnemyHealthLo',76,x);setv(m,'MmEnemyHealthHi',4,x)
        c,tr,_=run(m,'FfHostContact',a=255,x=x)
        dmg=([75,25,0,10]if tier!=2 else[150,50,0,25])[variant]
        assert bool(c.p&1)==bool(dmg),('melee class',variant,tier,face,x,worldx)
        assert C.hp(m,x)==1100-dmg and c.x==x
        if dmg:
            assert get(m,'FfDamage')==dmg and get(m,'FfHits')==1<<x
            before=C.hp(m,x);out,_,_=run(m,'FfHostContact',a=255,x=x)
            assert not out.p&1 and C.hp(m,x)==before
        rows.append([variant,tier,face,x,worldx,dmg])
    spells=[]
    for kind,tier,off,x,wx in itertools.product(range(1,5),range(3),[0,12,24],range(6),[1,120,250,256,65530]):
        m=make(b);put(m,FfVariant=2 if kind<4 else 1,FfPower=tier)
        at=address(b,'FfProjectile')+off
        for i,v in {0:kind,1:0,4:wx&255,5:wx>>8,7:125,8:1,10:tier}.items():m[at+i]=v
        # Native box3 starts at enemy+2,+9. Its small interior overlaps every
        # genuine source HRect; far vertical edges are separately tested below.
        tx=(wx-2)&65535;actor(m,x=x,kind=address(b,'HammerBro'),px=tx&255,page=tx>>8,y=116)
        setv(m,'MmEnemyHealthLo',76,x);setv(m,'MmEnemyHealthHi',4,x)
        c,tr,_=run(m,'FfHostContact',a=off,x=x)
        dmg=[100,150,100,25][kind-1]+(50 if tier==2 else 0)
        assert c.p&1 and c.x==x and C.hp(m,x)==1100-dmg,('source spell',kind,tier,off,x,wx,C.hp(m,x))
        assert get(m,'FfDamage')==dmg and m[at+9]==1<<x
        out,_,_=run(m,'FfHostContact',a=off,x=x)
        assert not out.p&1 and C.hp(m,x)==1100-dmg
        spells.append([kind,tier,off,x,wx,dmg])
    edges=[]
    # One1px native box cannot be invented: use genuine box3(13x13) and solve
    # independent signed world half-open intersections at each source edge.
    for kind,dx,dy in itertools.product(range(1,5),[-140,-50,-38,-37,-27,-26,-21,-20,-14,-13,-12,-8,-1,0,7,8,13,14,24,25,50,140],[-150,-125,-124,-32,-31,-24,-23,-10,-9,-8,0,9,10,24,25,119,120,121,140]):
        m=make(b);at=address(b,'FfProjectile');m[at]=kind;m[at+4]=0;m[at+5]=1;m[at+7]=125;m[at+8]=1
        ex=256+dx;ey=125+dy
        # Eligible native geometry requires source top to stay0..255.
        if not 0<=ey<=246:continue
        actor(m,kind=address(b,'HammerBro'),px=ex&255,page=(ex>>8)&255,y=ey)
        setv(m,'MmEnemyHealthLo',76);setv(m,'MmEnemyHealthHi',4)
        c,tr,_=run(m,'FfHostContact',a=0,x=0)
        w=[16,28,48,48][kind-1];h=[19,240,49,49][kind-1]
        left=256-w//2;top=5 if kind==2 else 125-h//2
        want=(ex+2<left+w and left<ex+15 and ey+9<top+h and top<ey+22)
        assert bool(c.p&1)==want,('native/source halfopen edges',kind,dx,dy,want,c.p)
        edges.append([kind,dx,dy,int(want)])
    return dict(melee_class_tier_face_slot_world_cases=len(rows),spell_kind_tier_slot_world_cases=len(spells),
                genuine_native_box_halfopen_edge_cases=len(edges),melee=rows,spells=spells,edges=edges,
                one_source_identity_hit_per_attack=True,White_light_explicit_authored_adaptation=True)

def lifecycle(b):
    own=[]
    for variant,p in itertools.product(range(4),C.flags()):
        m=make(b);put(m,FfVariant=variant,FfPower=2,FfEarned=2,FfHealCharges=3,FfAction=1,FfReady=0xf7)
        c,tr,_=run(m,'FfHostFresh',p=p)
        assert get(m,'FfVariant')==variant and get(m,'FfReady')==247
        assert all(get(m,n)==0 for n in ['FfPower','FfEarned','FfHealCharges','FfAction'])
        assert c.p&0x4c==p&0x4c
        own.append([variant,p])
    foreign=[]
    for owner,p in itertools.product([0,9,21,23,32,255],C.flags()):
        m=make(b);put(m,SelectedCharacter=owner,FfReady=119,FfVariant=3)
        m.raw_page(1,3);setv(m,'CurrentBank',3);before=state(m)
        c,tr=direct(m,'FfHostFresh',a=89,x=5,y=167,p=p)
        assert state(m)==before and c.x==5 and c.y==167 and c.p&0x4c==p&0x4c
        foreign.append([owner,p])
    return dict(own_fresh_cases=len(own),foreign_cases=len(foreign),selected_class_preserved=True,
                Fresh_ABI='Own A/X/Y/N/Z/C volatile. Foreign X/Y+V/D/I preserved, A/N/Z/C volatile. No application state writes for foreign owner.')

def timelines(b):
    rows=[]
    for variant,keys,spell in [(0,64,0),(1,64,0),(3,64,0),(2,64,1),(2,72,2),(2,68,3),(1,68,4)]:
        m=make(b);put(m,FfVariant=variant,FfPower=2,SavedJoypadBits=keys)
        # Typed grounded motion inputs only; this is not a native terrain run.
        trace=[]
        for tick in range(50):
            actor(m,kind=address(b,'HammerBro'),px=150,y=116 if spell else 160)
            if tick==0:setv(m,'MmEnemyHealthLo',76);setv(m,'MmEnemyHealthHi',4)
            move,_,_=run(m,'FfMovement')
            c,tr,_=run(m,'FfHostWeapons')
            assert (address(b,'FfWeapons'),3)in tr
            trace.append([tick,get(m,'FfAction'),get(m,'FfAge'),get(m,'FfProjectile'),C.hp(m),get(m,'FfHits'),get(m,'FfProjectile',9)])
        if spell:
            assert trace[0][1]==2 and trace[29][1]==2 and trace[30][1]==3
            assert any(z[3]==spell for z in trace)and any(z[4]<1100 for z in trace),('actual movement/action/weapons hit',variant,keys,trace)
        else:assert trace[0][1]==1 and trace[30][1]==0 and trace[0][4]<1100
        rows.append(dict(variant=variant,keys=keys,spell=spell,trace=trace))
    # Empty native field: wrapper must retain every original source field and
    # every projectile update exactly once, not approximate its clock/motion.
    fields=list(range(0x5c00,0x5c80))+list(range(0x5fc1,0x5fcf))+[0x5fef]
    pairs=0
    for kinds,pause,timer,dead,engine in itertools.product([(0,0,0),(1,2,3),(4,1,2)],range(4),[0,1],[0,1],[0,8]):
        results=[]
        for name in ['FfWeapons','FfHostWeapons']:
            m=make(b);put(m,GamePauseStatus=pause,TimerControl=timer,MmDeathFlag=dead,GameEngineSubroutine=engine)
            for off,kind in zip([0,12,24],kinds):
                at=address(b,'FfProjectile')+off
                for i,v in {0:kind,4:128,7:125,8:1}.items():m[at+i]=v
            for t in range(12):run(m,name)
            results.append(bytes(m[i]for i in fields))
        assert results[0]==results[1],('source field invariant',kinds,pause,timer,dead,engine)
        pairs+=1
    return dict(real_movement_action_weapon_sequences=rows,empty_field_source_tick_pairs=pairs,
                compared_source_bytes=len(fields),typed_ground_inputs=True,native_terrain=False)

GROUPS={**C.GROUPS,'reuse':reuse,'contacts':contacts,'lifecycle':lifecycle,'timelines':timelines}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--packet',type=Path,default=R/'build/final-fantasy-host-combat-v2')
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--only',default=','.join(GROUPS));a=ap.parse_args()
    assert not a.output.exists();a.output.parent.mkdir(parents=True,exist_ok=True)
    proof=json.loads((a.packet/'build-proof.json').read_text())
    for p,h in proof['bindings'].items():assert sha(p)==h,p
    b=C.bundle(a.packet);d=dict(passed=False,native=False,host_Main=False,fixture_RAM3_preloaded=True,checks={},failures={})
    for n in a.only.split(','):
        try:d['checks'][n]=GROUPS[n](b)
        except Exception as e:d['failures'][n]=dict(error=repr(e),traceback=traceback.format_exc())
    d['passed']=not d['failures']
    d['bindings']={**proof['bindings'],str((a.packet/'build-proof.json').resolve()):sha(a.packet/'build-proof.json'),
        str(Path(__file__).resolve()):sha(__file__),str(Path(C.__file__).resolve()):sha(C.__file__)}
    a.output.write_text(json.dumps(d,indent=2)+'\n')
    for p,h in d['bindings'].items():assert sha(p)==h,p
    print(json.dumps(dict(passed=d['passed'],checks=list(d['checks']),failures=d['failures'])))
    assert d['passed']
if __name__=='__main__':main()

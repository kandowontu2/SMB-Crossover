"""Actual candidate four-caller Ensure ABI and declared lifecycle components."""
from pathlib import Path
from unittest.mock import patch
import json,itertools
import bowser_life_source_components_1116 as T

C,N,W=T.C,T.N,T.W
def run(parent):
    raw,composition=C.proposal(parent);cases=0;gain_cases=0;scopes={};boundaries=set();lifecycle=[]
    for identity in(0,1):
        seed=T.Current.cold(raw,'smb1'if identity else'smb3');b=seed.bundle
        a={n:W.address(b,n)for n in('BwReady','BwPlayerKey','BwVariant','BwTier','BwHP','BwPersistent','BwEnsure','CurrentPlayer','NumberofLives','PlayerStatus')}
        ensure=a['BwEnsure'];maxhp=5 if identity else 34
        for caller,scope,player,f in itertools.product(('BwMovement','BwWeaponTail','BwInjury','BwGraphics'),('equal','gain','loss','last-death','invalid-ready','member'),(0,1),range(8)):
            q=T.fork(seed);key=player*4;active=(1-player)*4 if scope=='member'else key
            q.ram[3][a['BwPlayerKey']&8191]=active;q.ram[3][a['BwReady']&8191]=0 if scope=='invalid-ready' else 0xb7
            q.ram[3][a['BwHP']&8191]=maxhp-1;q.ram[3][a['BwTier']&8191]=1
            N.put(q,CurrentPlayer=player,PlayerStatus=1,NumberofLives=3 if scope=='gain' else 1 if scope=='loss' else 255 if scope=='last-death' else 2)
            for member in(0,4):q.ram[3][(a['BwPersistent']&8191)+member:(a['BwPersistent']&8191)+member+4]=bytes((maxhp-1,1,0 if scope=='last-death' else 2,0xb7))
            old=T.reference(q,parent);trials=[];entry=W.address(b,caller);assert T.Current.image(raw)[entry&8191:(entry&8191)+3]==bytes((0x20,ensure&255,ensure>>8))
            for model in(old,q):
                reached={}
                def watch(m,c):
                    if c.pc==ensure and m.rawtags[1]==3 and not reached:
                        reached.update(private=[bytes(v)for v in m.ram],native=bytes(m[:0x800]),write_index=len(m.ram_writes),SP=c.sp,regs=(c.a,c.x,c.y,c.p))
                def stop(m,c):return bool(reached)and c.pc==entry+3 and m.rawtags[1]==3
                c,r=T.call(model,caller,p=T.flags(f),stop=stop,watch=watch)
                assert reached and c.sp==(reached['SP']+2)&255
                trials.append((model,c,r,reached))
            _,oc,_,_=trials[0];_,nc,_,prior=trials[1]
            assert(oc.a,oc.x,oc.y,oc.p,oc.sp)==(nc.a,nc.x,nc.y,nc.p,nc.sp),'Actual caller Ensure return AXYP/SP'
            boundaries.add((caller,entry+3,nc.sp))
            if scope=='gain':
                offset=(a['BwPersistent']&8191)+2+key
                assert q.ram[3][offset]==3 and q.ram_writes[prior['write_index']:]==[(3,offset,3)]
                assert bytes(q[:0x800])==prior['native']
                for bank in range(4):assert all(x==y for at,(x,y)in enumerate(zip(prior['private'][bank],q.ram[bank]))if not(bank==3 and at==offset))
                gain_cases+=1
            else:T.application_equal(old,q)
            cases+=1;scopes[scope]=scopes.get(scope,0)+1
        for mode in('area-construct','explicit-newgame-construct','public-area-scene'):
            q=T.fork(seed);q.ram[3][a['BwTier']&8191]=2;q.ram[3][a['BwHP']&8191]=maxhp-1
            q.ram[3][(a['BwPersistent']&8191):(a['BwPersistent']&8191)+4]=bytes((maxhp-1,2,2,0xb7))
            N.put(q,PlayerStatus=2)
            if mode=='explicit-newgame-construct':
                q.ram[3][a['BwReady']&8191]=0;q.ram[3][(a['BwPersistent']&8191)+3]=0
            if mode=='public-area-scene':N.put(q,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,FamilyMainCommit=1)
            old=T.reference(q,parent);name='BwScene'if mode=='public-area-scene'else'BwConstruct'
            oc,orr=T.call(old,name);nc,nrr=T.call(q,name)
            assert(oc.a,oc.x,oc.y,oc.p,oc.sp)==(nc.a,nc.x,nc.y,nc.p,nc.sp)
            T.application_equal(old,q)
            expected_tier=0 if mode=='explicit-newgame-construct' else 2
            expected_hp=maxhp if mode=='explicit-newgame-construct'else maxhp-1
            assert(q.ram[3][a['BwTier']&8191],q.ram[3][a['BwHP']&8191])==(expected_tier,expected_hp)
            lifecycle.append(dict(identity=identity,component=mode,tier=expected_tier,HP=expected_hp,cycles=nrr['cycles']))
    q=dict(passed=True,composition=composition,actual_caller_cases=cases,gain_only_saved_life_write_cases=gain_cases,scope_counts=scopes,
        actual_caller_return_boundaries=[dict(caller=x[0],PC=x[1],SP=x[2])for x in sorted(boundaries)],lifecycle=lifecycle,
        caller_AXYP_SP_exact=True,original_reset_paths_and_area_callbacks_match_parent=True,
        scope='Actual candidate callbacks on cloned compiled-cold arenas; seeded lifecycle components only, not natural acquisition/full-stage claims',outputs=0,Mesen=False)
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    parent=C.ROM.read_bytes()
    def deny(*a,**kw):raise AssertionError('Caller component attempted files/native')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):q=run(parent)
    print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)

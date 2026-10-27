"""Immutable Mike-only remainder conservation correction; never launches Mesen."""
from pathlib import Path
import csv
import hashlib
import json
import sys

R=Path(__file__).resolve().parents[2]
OLD=R/'tools/audit/current_mac_mike_powerups_prepare_v1.py'
FIXTURE=R/'tests/current-mac-mike-powerups.lua'
NEW=R/'tests/current-mike-powerups-v2.lua'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
LUA_PAIRS=[
 (" if not C.mac then rec.ammo={};", " if not C.mac then rec.remainder=r('JnStars')&7;assert(rec.remainder<5,'Actual source star remainder0..4');rec.ammo={};"),
 ("r('JnStars')&7==t.remainder", "r('JnStars')&7==(rec.remainder+(t.drop==2 and(t.count or 1)or 0))%5")]
PY_PAIRS=[
 ("fixture=R/'tests/current-mac-mike-powerups.lua'", "fixture=R/'tests/current-mike-powerups-v2.lua'"),
 ("            ammo=[q.get('JnAmmo',i)for i in range(10)]if not mac else[];lastammo=ammo.copy()", "            rec['remainder']=q.get('JnStars')&7 if not mac else 0\n            assert 0<=rec['remainder']<5\n            ammo=[q.get('JnAmmo',i)for i in range(10)]if not mac else[];lastammo=ammo.copy()"),
 ("q.get('JnStars')&7==t['remainder']", "q.get('JnStars')&7==(rec['remainder']+(t.get('count',1)if t['drop']==2 else 0))%5"),
 ("    print(json.dumps(dict(prepared=True", "    if False:print(json.dumps(dict(prepared=True")]


def change(text,pairs):
    for a,b in pairs:assert text.count(a)==1,a;text=text.replace(a,b)
    return text


def prefix_controls(ns):
    b=ns['scoped_load'](R/'build/mega_proto_body_palette_9ea.nes');result=[]
    for kind,count in [(1,1),(2,5)]:
        for prefix in range(5):
            q=ns['Arena'](b,16)
            q.put(CrossoverBehaviorVersion=1,OperMode_Task=3,AreaType=1,PlayerStatus=0,Player_X_Position=112,Player_PageLoc=0,Player_Y_Position=176,Player_State=0,
                  ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,ScreenRight_PageLoc=0,ScreenRight_X_Pos=255,ScrollLock=1,Player_CollisionBits=255,Player_MovingDir=1)
            q.array('GameTimerDisplay',[3,9,9]);q.invoke('InventoryInit');q.invoke('CrossoverGraphicsBank')
            for n in ['Block_Buffer_1','MmSolidTerrain','MmBrickHealth']:q.array(n,[0]*416)
            for p in range(2):
                for row in [11,12]:
                    for col in range(16):q.set('Block_Buffer_1',84,p*208+row*16+col)
            calls=0
            def main():
                nonlocal calls
                calls+=1;q.set('SavedJoypadBits',0);q.invoke('GameLoop')
            for _ in range(30):main()
            assert q.get('JnHealth')==6 and q.get('JnStars')&7==0
            ns['scene'](q,False,1);ns['target'](q,dict(kind='contact'),True,51)
            for _ in range(20):
                main()
                if q.get('JnHealth')==4:break
            else:raise AssertionError('Real prefix contact must cause the2HP deficit')
            q.set('Enemy_Flag',0,0);q.set('Enemy_CollisionBits',0,0)
            for _ in range(200):
                main()
                if ns['quiet'](q,False):break
            else:raise AssertionError('Real source hurt/landing expiry')
            assert q.get('JnHealth')==4
            def collect(which):
                assert q.get('JnDropKind',0)==0;ns['drop'](q,which)
                for i in range(10):
                    main()
                    if q.get('JnDropKind',0)==0:break
                else:raise AssertionError('Real physical private restoration pickup')
            for _ in range(prefix):collect(2)
            assert q.get('JnStars')&7==prefix and q.get('JnHealth')==4
            before=q.get('JnStars')&7
            for _ in range(count):collect(kind)
            after=q.get('JnStars')&7
            assert q.get('JnHealth')==6 and q.get('JnMaxHearts')==3 and after==(before+(count if kind==2 else 0))%5
            result.append(dict(private_kind=kind,actual_prefix_star_collections=prefix,tested_physical_collections=count,
                               initial_remainder=before,final_remainder=after,health_before=4,health_after=q.get('JnHealth'),full_GameLoop_calls=calls,
                               old_literal_zero_oracle_passes=after==0,conservation_oracle_passes=True))
    assert sum(not r['old_literal_zero_oracle_passes']for r in result)==8
    return dict(passed=True,native_run=False,cases=result,scope='Actual complete CPU Main, actual Goomba contact deficit, actual private physical star prefix0..4 and heart/5star collections. No health/remainder/ownership/timer/kill seeds; staged physical actors do not prove drop RNG eligibility.')


def main():
    assert sha(OLD)=='25f07ac574beacea299a382cfe618f9798ae6f409ed99a43f9dd75c42b291890'
    assert sha(FIXTURE)=='b70ef2cacfc57837b18fade5973e2c8af2309644047069a7b15ddb0feaa905a0'
    assert '--identity'in sys.argv and sys.argv[sys.argv.index('--identity')+1]=='mike'
    text=change(FIXTURE.read_text(),LUA_PAIRS);assert text==NEW.read_text()
    for a,b in reversed(LUA_PAIRS):text=text.replace(b,a)
    assert text==FIXTURE.read_text(),'Exact reverse fixture delta; original mechanics/guard/caps/input remain'
    code=change(OLD.read_text(),PY_PAIRS)
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'_mike_remainder_v2'};exec(compile(code,str(OLD),'exec'),ns)
    controls=prefix_controls(ns);ns['main']()
    out=Path(sys.argv[sys.argv.index('--output')+1]).resolve();proof=out/'remainder-controls.json';put(proof,controls)
    ready=out/'prepared-not-run.json';z=json.loads(ready.read_text())
    paths={Path(p['path'])for p in z['bindings']}|{OLD,FIXTURE,NEW,Path(__file__).resolve(),proof,R/'build/current-ab221-mike-hard-items-v1/prepared-not-run.json',R/'build/current-ab221-mike-hard-items-v1/kind-source-controls.json'}
    z.update(successor='Observed pre-case remainder plus exact modulo5 conservation; real5star count/healing/costs unchanged',original_Mike_v1='Native UNRUN; retained literal0 oracle has source counterexamples after legitimate earned private stars',native_run=False)
    z['bindings']=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)];put(ready,z)
    print(json.dumps(dict(prepared=True,native_run=False,ready=str(ready),ready_sha256=sha(ready),bindings=len(z['bindings']),prefix_controls=str(proof))))


if __name__=='__main__':main()

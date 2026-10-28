"""Execute the real shared actor gate, not just the River City leaf.

Compare selected native actor state and returned AXYP/SP for foreign profiles.
This is a bounded CPU component check, not whole-RAM/stack/NMI equivalence or
native frame timing. JumpEngine's dead dispatch-pointer scratch may differ.
"""
from pathlib import Path
import argparse, hashlib, itertools, json
from link_pit_rygar_sophia_audit_cpu import Arena, scoped_load
from check_tmnt_render_oa import address

FIELDS=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc',
        'Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed',
        'Enemy_MovingDir','Enemy_Y_MoveForce','Enemy_YMoveForceFractional',
        'EnemyIntervalTimer','RgEnemyStun']


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def setup(bundle, char, slot, kind, stun):
    q=Arena(bundle,char)
    q.put(ObjectOffset=slot,TimerControl=0,AreaType=1,FrameCounter=32)
    for name,value in [('Enemy_Flag',1),('Enemy_ID',kind),('Enemy_State',0),
        ('Enemy_X_Position',96),('Enemy_PageLoc',1),('Enemy_Y_Position',160),
        ('Enemy_Y_HighPos',1),('Enemy_X_Speed',0xf8),('Enemy_Y_Speed',0),
        ('Enemy_MovingDir',2),('RgEnemyStun',stun)]:
        q.set(name,value,slot)
    return q


def snapshot(q,c):
    return dict(cpu=[c.a,c.x,c.y,c.p&0xcf,c.sp],
        actors={name:[q.get(name,i)for i in range(6)]for name in FIELDS},
        ObjectOffset=q.get('ObjectOffset'))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists()
    old,new=scoped_load(a.baseline),scoped_load(a.rom)
    proof=dict(passed=False,scope=__doc__,baseline_sha256=sha(a.baseline),ROM_sha256=sha(a.rom),tool_sha256=sha(__file__))
    try:
        for name in ['RunNormalEnemies','OffscreenBoundsCheck','MoveNormalEnemy','MoveBloober','MoveBulletBill']:
            assert address(old,name)==address(new,name),name
        foreign=[]
        for char,slot,kind,stun in itertools.product(range(20),range(6),[0,6,8,9,19],[0,3]):
            pair=[setup(b,char,slot,kind,stun)for b in [old,new]]
            values=[];cycles=[]
            for q in pair:
                c,_=q.invoke('EnemyMovementSubs',x=slot,y=7)
                values.append(snapshot(q,c));cycles.append(c.processorCycles)
            assert values[0]==values[1],dict(char=char,slot=slot,kind=kind,stun=stun,old=values[0],new=values[1])
            foreign.append(dict(char=char,slot=slot,kind=kind,stun=stun,cycle_delta=cycles[1]-cycles[0]))
        proof['foreign_cases']=len(foreign)
        proof['foreign_cycle_delta']=[min(v['cycle_delta']for v in foreign),max(v['cycle_delta']for v in foreign)]
        city=[]
        for variant,slot in itertools.product([0,1],range(6)):
            q=setup(new,21,slot,6,0)
            q.put(RcVariant=variant,RcCarrySlot=255,RcThrowSlot=255)
            q.set('RcEnemyStun',12,slot);q.set('RcEnemyType',7,slot);q.set('RcEnemyStamp',1,slot)
            before=[q.get(n,slot)for n in ['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_X_Speed','Enemy_Y_Speed']]
            for _ in range(4):
                c,_=q.invoke('EnemyMovementSubs',x=slot)
                assert c.sp==253 and c.x==slot and q.get('RcEnemyStun',slot)==12
                assert [q.get(n,slot)for n in ['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_X_Speed','Enemy_Y_Speed']]==before
            q.put(RcCarrySlot=slot,RcCarryType=6,RcHurt=0,Player_X_Position=120,Player_PageLoc=2,Player_Y_Position=140)
            c,_=q.invoke('EnemyMovementSubs',x=slot)
            assert c.x==slot and q.get('ObjectOffset')==slot
            assert [q.get(n,slot)for n in ['Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_X_Speed','Enemy_Y_Speed']]==[120,2,124,0,0]
            city.append(dict(variant=variant,slot=slot,stun_frames=4,carried_origin=[2,120,124]))
        proof['shared_city_cases']=city
        proof['following_native_PCs_preserved']=True
        proof['passed']=True
    except Exception as e:
        proof['error']=repr(e)
        raise
    finally:
        a.output.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in ['passed','foreign_cases','foreign_cycle_delta']}))


if __name__=='__main__':
    main()

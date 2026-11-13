"""Current Kirby inhale boundary/state/copy audit, explicit CPU fixtures only."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json

import check_kirby_inhale_native_1112 as Old
import check_kirby_red_catch_1112 as Catch

A,N,Main,Bind=Old.A,Old.N,Old.Main,Old.Bind
PIN='a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a'
KIRBY_BANK_SHA='119a6fe415a914c415a51bc46f0cc22569cd4c7e1282d83f512c3b2031573e9d'


def bundle(raw):
    assert len(raw)==2097168
    if KIRBY_BANK_SHA is None:
        assert sha256(raw).hexdigest()==PIN
    else:
        start=Old.Wide.offset(0xa000)
        assert sha256(raw[start:start+8192]).hexdigest()==KIRBY_BANK_SHA
    b=Old.bundle(raw)
    # Authenticate the delivered capture and shell changes by exact inverse
    # preimages and forward source recomposition; do not rerun passed suites.
    parent=bytearray(raw)
    for pc,body in (Old.CLOCK,Old.TAIL):
        at=Old.Wide.offset(pc);parent[at:at+len(body)]=body
    assert Old.proposal(bytes(parent))[0]==raw
    parent=raw[:Catch.offset(Catch.START)]+Catch.PREIMAGE+raw[Catch.offset(Catch.END):]
    assert Catch.proposal(parent)[0]==raw
    return b


def actor(m,name,slot,face,gap,dy=8):
    kind=A.address(m.bundle,name)
    Main.actor(m,kind,112+(gap if face==1 else -gap),y=176+dy,slot=slot)
    N.put(m,ObjectOffset=slot)
    Bind.call(m,'CheckpointEnemyID',x=slot)
    Bind.put_slot(m,slot,Enemy_Y_Position=176+dy,Enemy_Y_HighPos=1,EnemyOffscrBitsMasked=0,
                  Enemy_MovingDir=3-face)
    if name=='BulletBill_CannonVar':
        Bind.put_slot(m,slot,Enemy_State=1,Enemy_BoundBoxCtrl=9)
    if name in ('GreenKoopa','BuzzyBeetle','RedKoopa','HammerBro','Goomba','Spiny'):
        speed=N.get(m,'Enemy_X_Speed',slot)
        signed=speed-256 if speed&128 else speed
        Bind.put_slot(m,slot,Enemy_X_Speed=((-abs(signed)) if face==1 else abs(signed))&255)


def step(m,pad):
    Main.keys(m,pad)
    o=Old.Observe(m.bundle)
    Main.call(m,'GameLoop',o)
    assert not m.blocked and not o.errors,(m.blocked,o.errors)
    return o.events


def boundaries(seed):
    counts,witnesses=Counter(),[]
    for name,face,mode,gap in product(Old.ENEMIES,(1,2),(0,1),range(6)):
        m=N.fork(seed);Main.scene(m,face)
        N.put(m,CrossoverBehaviorVersion=mode)
        actor(m,name,0,face,gap)
        before=Old.eligible(m,0)
        events=step(m,64)
        after=Old.eligible(m,0)
        health=N.get(m,'KbHealth')
        counts['cases']+=1
        counts['injured' if health<6 else 'uninjured']+=1
        if N.get(m,'KbMouth'):counts['captured']+=1
        if before['in_range'] and health<6:
            witnesses.append(dict(name=name,face=face,mode=mode,gap=gap,before=before,after=after,
                health=health,mouth=N.get(m,'KbMouth'),events=events))
    return dict(counts=dict(counts),front_start_injuries=witnesses)


def acquired(seed,name,face,*,swallow=False):
    row,m=Old.one_main(seed,name,face,6,1,64,held=8,return_model=True)
    assert row['mouth']and row['health']==6,(name,face,row)
    family=row['copy'];N.consume(m)
    step(m,4 if swallow else 0);N.consume(m)
    assert N.get(m,'KbHealth')==6
    if swallow:
        assert N.get(m,'KbCopy')==family and not N.get(m,'KbMouth')
        step(m,0);N.consume(m)
    else:assert N.get(m,'KbMouth')
    return m,dict(enemy=name,face=face,family=family,swallowed=swallow)


def projectile_pages(seed):
    """Earn actual spit stars; only target NPC data varies across pages."""
    rows=[]
    defeat=A.address(seed.bundle,'ShellOrBlockDefeat')
    for face in(1,2):
        source,earned=acquired(seed,'Goomba',face)
        for page in(0,1,2):
            m=N.fork(source)
            actor(m,'Goomba',3,face,32 if face==1 else 16)
            Bind.put_slot(m,3,Enemy_Y_HighPos=page)
            seen=[];observer=Main.Observe(m.bundle)
            def observe(m,c,i):
                observer(m,c,i)
                if c.pc==defeat and m.rawtags[(c.pc-0x8000)//8192]==254:
                    seen.append(dict(slot=c.x,high=N.get(m,'Enemy_Y_HighPos',c.x),
                        x=Bind.world(m,'Enemy_X_Position','Enemy_PageLoc',c.x),
                        y=N.get(m,'Enemy_Y_Position',c.x),shot=Bind.shot(m),instruction=i))
            Main.keys(m,64);Main.call(m,'GameLoop',observe)
            assert not m.blocked,m.blocked
            assert len(seen)==1 and seen[0]['slot']==3 and seen[0]['high']==page
            assert N.get(m,'KbHealth')==6 and not N.get(m,'KbShotType')
            rows.append(dict(earned=earned,target_page=page,health=N.get(m,'KbHealth'),
                mouth=N.get(m,'KbMouth'),shot=Bind.shot(m),defeats=seen,
                target=dict(flag=N.get(m,'Enemy_Flag',3),state=N.get(m,'Enemy_State',3),
                            high=N.get(m,'Enemy_Y_HighPos',3),y=N.get(m,'Enemy_Y_Position',3)),
                calls=dict(observer.counts)))
    return rows


def native_podoboo(seed):
    """Native constructor and movement reach the target state without Y writes."""
    rows=[]
    for face in(1,2):
        m,earned=acquired(seed,'Goomba',face)
        x=144 if face==1 else 96
        Main.actor(m,A.address(m.bundle,'Podoboo'),x,slot=3)
        N.put(m,ObjectOffset=3);Bind.call(m,'CheckpointEnemyID',x=3)
        initial=dict(high=N.get(m,'Enemy_Y_HighPos',3),y=N.get(m,'Enemy_Y_Position',3),
                     timer=N.get(m,'EnemyIntervalTimer',3),speed=N.get(m,'Enemy_Y_Speed',3))
        pages=Counter();samples=[];seen=[]
        defeat=A.address(m.bundle,'ShellOrBlockDefeat')
        def observe(m,c,i):
            if c.pc==defeat and m.rawtags[(c.pc-0x8000)//8192]==254:
                seen.append(dict(slot=c.x,high=N.get(m,'Enemy_Y_HighPos',c.x),
                    y=N.get(m,'Enemy_Y_Position',c.x),shot=Bind.shot(m),instruction=i))
        fired=None
        for update in range(700):
            high,y=N.get(m,'Enemy_Y_HighPos',3),N.get(m,'Enemy_Y_Position',3)
            pages[str(high)]+=1
            if update%24==0:samples.append(dict(update=update,high=high,y=y,timer=N.get(m,'EnemyIntervalTimer',3)))
            fire=high!=1 and 184<=y<=208 and N.get(m,'Enemy_Flag',3)
            Main.keys(m,64 if fire else 0);Main.call(m,'GameLoop',observe)
            assert not m.blocked and N.get(m,'KbHealth')==6
            if fire:
                fired=dict(update=update,high=high,y=y,defeats=seen,shot=Bind.shot(m),
                    target_flag=N.get(m,'Enemy_Flag',3),target_state=N.get(m,'Enemy_State',3))
                break
            N.consume(m)
        assert initial['high']==2 and initial['y']==2 and fired is None
        assert pages=={'2':2,'1':698},pages
        rows.append(dict(earned=earned,native_initial=initial,pages=dict(pages),fired=fired,
            samples=(samples[0],samples[-1]),observed_updates=700))
    return rows


def ground_actions(seed):
    """Ability is earned from one NPC; only the grounded target is seeded."""
    rows=[]
    modes=(('spit','Goomba'),('copy','HammerBro'),('copy','Bloober'),('copy','GreyCheepCheep'),
           ('copy','RedCheepCheep'),('copy','Spiny'),('copy','PiranhaPlant'),('copy','Podoboo'))
    for(face,(action,name),target)in product((1,2),modes,('Goomba','GreenKoopa')):
        m,earned=acquired(seed,name,face,swallow=action=='copy')
        actor(m,target,3,face,28 if face==1 else 12)
        saved=[];shots=[]
        for update in range(50):
            o=Main.Observe(m.bundle)
            Main.keys(m,64 if update<3 else 0);Main.call(m,'GameLoop',o)
            assert not m.blocked,m.blocked
            if update<4:shots.append(dict(update=update,shot=Bind.shot(m),target_y=N.get(m,'Enemy_Y_Position',3)))
            if o.counts['ShellOrBlockDefeat']:
                saved.append(dict(update=update,calls=dict(o.counts),state=N.get(m,'Enemy_State',3),
                    y=N.get(m,'Enemy_Y_Position',3),high=N.get(m,'Enemy_Y_HighPos',3),
                    health=N.get(m,'KbHealth'),mouth=N.get(m,'KbMouth'),copy=N.get(m,'KbCopy')))
                break
            N.consume(m)
        assert saved and saved[0]['state']&32 and saved[0]['health']==6,(earned,target,saved,shots)
        assert N.get(m,'KbCopy')==(earned['family']if action=='copy'else 0)
        rows.append(dict(earned=earned,action=action,target=target,kill_update=saved[0]['update'],
            final_health=N.get(m,'KbHealth'),final_copy=N.get(m,'KbCopy'),first_shot=shots[0]['shot']))
    return dict(cases=len(rows),all_native_defeat=True,all_HP6=True,rows=rows)


def compound(seed):
    counts=Counter();witnesses=[]
    names=tuple(name for name in Old.ENEMIES if name not in('Goomba','Lakitu'))
    for name,face,mode,front in product(names,(1,2),(0,1),(False,True)):
        m=N.fork(seed);Main.scene(m,face);N.put(m,CrossoverBehaviorVersion=mode)
        actor(m,'Goomba',5,face,6)
        actor(m,name,0,face,6 if front else -6)
        before=Old.eligible(m,0)
        events=step(m,64)
        captures=[e for e in events if e['name']=='KbWeapons::Capture']
        contacts=[e for e in events if e['name']=='KbBodyContact'and e['slot']==0]
        assert captures and captures[0]['slot']==5,(name,face,front,events)
        health=N.get(m,'KbHealth');counts['cases']+=1
        counts['front'if front else'rear']+=1
        counts['body_contacts']+=len(contacts)
        counts['injured'if health<6 else'uninjured']+=1
        if front and before['in_range']:
            assert health==6,(name,face,mode,before,events)
            counts['eligible_front_protected']+=1
        if not front and health<6:counts['rear_damage_preserved']+=1
        if contacts and len(witnesses)<8:
            witnesses.append(dict(name=name,face=face,mode=mode,front=front,health=health,mouth=N.get(m,'KbMouth'),contacts=contacts))
    return dict(counts=dict(counts),witnesses=witnesses)


def descending(seed):
    rows=[]
    for name,face in product(('Goomba','GreenKoopa','BuzzyBeetle','HammerBro','Spiny'),(1,2)):
        m=N.fork(seed);Main.scene(m,face)
        # An explicit small pit opens only under the native NPC. Kirby keeps
        # the existing supporting ground. Gravity and native retirement run.
        for row in(11,12):
            for col in(range(8,13)if face==1 else range(2,7)):
                m[A.address(m.bundle,'Block_Buffer_1')+row*16+col]=0
        actor(m,name,3,face,40)
        started=None;trace=[];pulls=Counter();captured=False;baseline=None;paired=0
        def native_state(m):
            return tuple(N.get(m,n,3)for n in('Enemy_Flag','Enemy_State','Enemy_ID','Enemy_X_Position',
                'Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_Y_MoveForce'))
        for update in range(180):
            high,y=N.get(m,'Enemy_Y_HighPos',3),N.get(m,'Enemy_Y_Position',3)
            if started is None and(high!=1 or y>196):
                started=update;baseline=N.fork(m)
            if started is not None and len(trace)<16:
                trace.append(dict(update=update,high=high,y=y,x=Bind.world(m,'Enemy_X_Position','Enemy_PageLoc',3),flag=N.get(m,'Enemy_Flag',3)))
            events=step(m,64 if started is not None else 0)
            if baseline is not None:
                step(baseline,0)
                assert native_state(m)==native_state(baseline),(name,face,update,native_state(m),native_state(baseline))
                paired+=1
            pulls.update(e['name']for e in events)
            captured|=bool(N.get(m,'KbMouth'))
            assert N.get(m,'KbHealth')==6,(name,face,update,events)
            if not N.get(m,'Enemy_Flag',3):break
            N.consume(m)
            if baseline is not None:N.consume(baseline)
        assert started is not None and not captured and not N.get(m,'Enemy_Flag',3),(name,face,started,trace)
        rows.append(dict(name=name,face=face,inhale_started=started,updates=update+1,
            retired=not N.get(m,'Enemy_Flag',3),captured=captured,health=N.get(m,'KbHealth'),
            trace=(trace[0],trace[-1]),paired_no_B_updates=paired,calls=dict(pulls)))
    return rows


def ground_pull(seed):
    rows=[]
    for name,face in product(('Goomba','GreenKoopa','BuzzyBeetle','HammerBro','Spiny'),(1,2)):
        m=N.fork(seed);Main.scene(m,face);actor(m,name,0,face,56)
        positions=[];counts=Counter()
        for update in range(70):
            if N.get(m,'Enemy_Flag'):
                positions.append((Bind.world(m,'Enemy_X_Position','Enemy_PageLoc'),N.get(m,'Enemy_Y_HighPos'),N.get(m,'Enemy_Y_Position')))
            events=step(m,64);counts.update(e['name']for e in events)
            assert N.get(m,'KbHealth')==6
            if N.get(m,'KbMouth'):break
            N.consume(m)
        assert N.get(m,'KbMouth')and N.get(m,'KbMouthCopy')==Old.EXPECTED[name],(name,face,positions)
        assert all(high==1 and 172<=y<=184 for _,high,y in positions),(name,face,positions)
        rows.append(dict(name=name,face=face,updates=update+1,positions=len(positions),
            minimum_y=min(p[2]for p in positions),maximum_y=max(p[2]for p in positions),
            native_foot=208,health=N.get(m,'KbHealth'),mouth=N.get(m,'KbMouth'),family=N.get(m,'KbMouthCopy'),calls=dict(counts)))
    return rows


def plant_cycle(seed):
    rows=[]
    for face in(1,2):
        m=N.fork(seed);Main.scene(m,face)
        Main.actor(m,A.address(m.bundle,'PiranhaPlant'),160 if face==1 else 64,y=184,slot=3)
        N.put(m,ObjectOffset=3);Bind.call(m,'CheckpointEnemyID',x=3)
        initial=dict(down=N.get(m,'PiranhaPlantDownYPos',3),up=N.get(m,'PiranhaPlantUpYPos',3))
        started=None;trace=[]
        for update in range(360):
            y=N.get(m,'Enemy_Y_Position',3)
            moving=N.get(m,'PiranhaPlant_MoveFlag',3)
            speed=N.get(m,'PiranhaPlant_Y_Speed',3)
            if started is None and moving and speed==1 and 180<=y<=184:started=update
            if started is not None:
                trace.append(dict(update=update,x=Bind.world(m,'Enemy_X_Position','Enemy_PageLoc',3),
                    high=N.get(m,'Enemy_Y_HighPos',3),y=y,moving=moving,speed=speed))
            step(m,64 if started is not None else 0)
            assert N.get(m,'KbHealth')==6
            if N.get(m,'KbMouth'):break
            N.consume(m)
        assert started is not None and N.get(m,'KbMouthCopy')==12 and N.get(m,'KbMouth'),(face,started,trace)
        assert all(p['high']==1 and 172<=p['y']<=196 for p in trace)
        rows.append(dict(face=face,native_initial=initial,actual_descent_start=started,
            capture_update=update+1,health=N.get(m,'KbHealth'),mouth=N.get(m,'KbMouth'),
            minimum_Y=min(p['y']for p in trace),maximum_Y=max(p['y']for p in trace),trace=trace))
    return rows


def frenzy_initializer(seed):
    rows=[]
    for face,mode,gap in product((1,2),(0,1),range(6)):
        m=N.fork(seed);Main.scene(m,face);N.put(m,CrossoverBehaviorVersion=mode)
        actor(m,'FlyingCheepCheep',0,face,gap)
        before=Old.eligible(m,0)
        native_initial=dict(x=Bind.world(m,'Enemy_X_Position','Enemy_PageLoc'),
            high=N.get(m,'Enemy_Y_HighPos'),y=N.get(m,'Enemy_Y_Position'),flag=N.get(m,'Enemy_Flag'))
        events=step(m,64)
        assert not before['in_range']and not N.get(m,'KbMouth')and N.get(m,'KbHealth')==6,(before,native_initial,events)
        rows.append(dict(face=face,mode=mode,requested_gap=gap,before=before,native_initial=native_initial,
            flag=N.get(m,'Enemy_Flag'),mouth=N.get(m,'KbMouth'),health=N.get(m,'KbHealth')))
    # Separate legal visible-position fixture after the genuine frenzy init.
    # Only NPC position is restored, as declared for the other native types.
    live=[]
    for face,mode in product((1,2),(0,1)):
        m=N.fork(seed);Main.scene(m,face);N.put(m,CrossoverBehaviorVersion=mode)
        actor(m,'FlyingCheepCheep',0,face,6)
        Bind.put_slot(m,0,Enemy_X_Position=118 if face==1 else 106,Enemy_PageLoc=0)
        before=Old.eligible(m,0);events=step(m,64)
        assert before['in_range']and N.get(m,'KbMouthCopy')==8 and N.get(m,'KbMouth')and N.get(m,'KbHealth')==6
        live.append(dict(face=face,mode=mode,mouth=N.get(m,'KbMouth'),copy=N.get(m,'KbMouthCopy'),health=N.get(m,'KbHealth')))
    return dict(initializer_noneligibility_cases=len(rows),initial_X_values=sorted(set(r['native_initial']['x']for r in rows)),
                family_values=sorted(set(r['before']['family']for r in rows)),visible_legal_position_capture_cases=live)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part',choices=('bindings','boundaries','projectile-pages','native-podoboo','ground-actions','compound','descending','ground-pull','plant-cycle','frenzy-initializer'),default='boundaries')
    args=parser.parse_args()
    raw=Bind.NIGHTLY.read_bytes();b=bundle(raw)
    start=Old.Wide.offset(0xa000)
    print(json.dumps(dict(event='bindings',ROM_SHA256=sha256(raw).hexdigest(),
        Kirby_PRG74_SHA256=sha256(raw[start:start+8192]).hexdigest(),output_files=0)),flush=True)
    if args.part=='bindings':return
    seed,origin=Old.Wide.spawn_seed(b)
    print(json.dumps(dict(event='actual_menu_parser',parser_updates=origin,settle_updates=40)),flush=True)
    result={'boundaries':boundaries,'projectile-pages':projectile_pages,'native-podoboo':native_podoboo,
            'ground-actions':ground_actions,'compound':compound,'descending':descending,
            'ground-pull':ground_pull,'plant-cycle':plant_cycle,'frenzy-initializer':frenzy_initializer}[args.part](seed)
    print(json.dumps(dict(part=args.part,result=result,source_CPU=True,native_emulator=False,
                         actor_data_fixtures=True,output_files=0)),flush=True)


if __name__=='__main__':main()

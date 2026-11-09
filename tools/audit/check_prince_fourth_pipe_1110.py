"""Replay the exact fourth-pipe Goomba contact with source-faithful control variations."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_goomba_climb_handoff_1110 as Approach


Recovery,Route,R,P,N,Current,Seam=Approach.Recovery,Approach.Route,Approach.R,Approach.P,Approach.N,Approach.Current,Approach.Seam
NATIVE=R/'build/prince-goomba-clear-native-1110-v2/native/capture'
PINS={
    'third-goombas.json':'58d7441046d2ab77d9e3f329b80af1fed692bc2507fc4354f15f5c2153925ebb',
    'third-pipe.json':'00454c4e3f840dd2da31591b161dfef9425d35a9e7527e05a23dc9c2bcb47146',
    'full11.json':'84eb702968ef677e90086d453eb7a222c2c73248bb2cefd00ef9fe4d2502b127',
    'prince-diagnostic.json':'ca18b92e5523bb989751986fc0ae0bd4e95a30007905444f2643d6253cb66ccf',
    'binding.json':'f116ae348fc782eec687012c9dac961f94b8b796a8c872df74325dfb92cd9d9a',
}


def trace():
    for name,pin in PINS.items():
        assert sha256((NATIVE/name).read_bytes()).hexdigest()==pin,name
    group,third,full,diag,bound=(Current.read(NATIVE/n) for n in PINS)
    assert all(q['ROM_sha256']==Route.PIN for q in (group,third,full,diag,bound))
    assert group['passed'] and third['passed'] and not full['passed'] and full['HP']==0
    assert (full['admitted'],full['frames'])==(1839,4427)
    hit,=diag['first_pipe_route']['precontacts']
    assert hit['native_enemy_world']==[887,198,897,204] and hit['native_player_world']==[897,185,909,209]
    born=group['group']['births'][1]
    passed=group['group']['clear']['actors'][1]
    assert (born['slot'],born['x'],passed['slot'],passed['x'],passed['direction'])==(1,843,1,843,1)
    assert (hit['native_collision_slot'],hit['native_enemy']['id'],hit['native_enemy']['x'])==(1,6,884)
    writes=diag['first_pipe_route']['HP_bus_writes'][1:]
    assert [(q['PC'],q['write_value']) for q in writes]==[(0xa291,4),*((0xa345,i) for i in (3,2,1,0))]
    return dict(birth=born,passed=passed,hit=hit,landing_damage_writer=writes[0]['PC'],fatal_writer=writes[1]['PC'])


def put_pipe(model):
    # X912 and X928 are both on the odd native Block Buffer page.
    block=Route.I.address(model.bundle,'Block_Buffer_2')
    for x in (912,928):
        for y in (144,160,176,192):
            model[block+((x&255)>>4)+16*((y-32)>>4)]=(0x12 if y==144 else 0x14)+int(x==928)


def arrival(env,seed,labels,right_start,goal):
    captured=None
    controls=Route.controls
    def with_fourth_pipe(e,model,lab,pad):
        nonlocal captured
        if captured is None:
            put_pipe(model)
            captured=model
        return controls(e,model,lab,pad)
    Route.controls=with_fourth_pipe
    try:
        route=Approach.replay(env,seed,labels,right_start,goal,709,8)
    finally:
        Route.controls=controls
    return captured,route


def fourth(env,seed,labels,profile):
    m=N.fork(seed)
    mode='up' if profile=='early-up' else 'approach'
    changed=0
    events=[]
    contacts=[]
    terminal='bound'
    max_x=0
    native=N.NesMPU
    previous=None
    def go(next_mode):
        nonlocal mode,changed
        events.append(dict(transition=f'{mode} to {next_mode}',row=q))
        mode,changed=next_mode,epoch
    class Trace(native):
        def step(self):
            if self.memory is m and self.pc==0xbd22 and m.rawtags[1]==3:
                hit=Recovery.sample(m,epoch)
                hit['slot']=self.x
                contacts.append(hit)
            return super().step()
    N.NesMPU=Trace
    try:
        for epoch in range(370):
            q=Recovery.sample(m,epoch)
            x,y,pose=q['x'],q['y'],q['frame']
            max_x=max(max_x,x)
            support=Recovery.grounded(m,q)
            idle=support and pose==15 and q['mode']==0 and q['a_lock']==0
            age=epoch-changed
            if q['hp']==0 or q['engine']!=8 or q['lives']!=2:
                terminal='death'
                break
            if q['hp']!=previous:
                events.append(dict(transition='HP',row=q))
                previous=q['hp']
            if mode=='approach':
                if 870<=x<=895 and Recovery.running(m,q):
                    go('A')
                elif x>=896:
                    go('settle')
            elif mode=='A':
                if q['action']==4:
                    go('flight')
                elif age>28:
                    go('settle')
            elif mode=='flight' and q['action']!=4 and support and age>=12:
                go('settle')
            elif mode=='settle' and idle:
                go('up')
            elif mode in ('up','flight') and (q['mode'] in (2,6) or q['action']==10):
                go('climb')
            elif mode=='climb' and q['action']==10 and q['foot']<=147:
                go('cap')
            if mode=='cap' and support and 899<=x<944 and y in range(110,115) and not any(
                    e['transition']=='physical-cap' for e in events):
                events.append(dict(transition='physical-cap',row=q))
            if mode=='cap' and x>=960 and y==176 and support and any(e['transition']=='physical-cap' for e in events):
                terminal='cleared-fourth'
                break
            if age>230:
                terminal=f'{mode}-bound'
                break
            pad={'approach':1,'A':129,'flight':1,'settle':0,'up':8 if age<64 else 201,
                 'climb':9,'cap':1}[mode]
            if mode=='flight' and x>=870 and q['action']==4 and 40<=pose<=42 and q['foot']-24<=175:
                pad=9
            Route.controls(env,m,labels,pad)
    finally:
        N.NesMPU=native
    return dict(profile=profile,terminal=terminal,maximum_x=max_x,events=events,contacts=contacts,end=q)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build' and not (out/'proof.json').exists()
    contact=trace()
    raw=Route.ROM.read_bytes()
    assert sha256(raw).hexdigest()==Route.PIN
    template,_,_=Current.current()
    env,seed,labels,start=Approach.Earned.fixture(dict(template,raw=raw))
    results=[]
    for right_start,goal in ((748,803),(748,765),(748,773),(748,779),(748,785),(707,773),(707,779)):
        m,third=arrival(env,seed,labels,right_start,goal)
        tests=[]
        if third['terminal']=='cleared':
            modes=('standard','early-up') if goal==803 else ('standard',)
            tests=[fourth(env,m,labels,mode) for mode in modes]
        results.append(dict(start_right=right_start,goal=goal,third=third,fourth=tests))
        print(right_start,goal,third['terminal'],third['end']['x'],third['end']['hp'],
              [(q['profile'],q['terminal'],q['end']['x'],q['end']['hp'],
                [(e['transition'],e['row']['epoch'],e['row']['x']) for e in q['events']]) for q in tests],flush=True)
    out.mkdir(exist_ok=True)
    refs=(Path(__file__),Path(Approach.__file__),Path(Recovery.__file__),Path(Route.__file__),Route.ROM,
          *(NATIVE/n for n in PINS))
    report=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,actor=contact,
                fixture_start=start,results=results,
                scope='Explicit corridor start, typed fourth-pipe metatiles and original native group parser cursor. '
                      'After fixture placement, only controller inputs determine camera, donor and enemy behavior.',
                bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'proof.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

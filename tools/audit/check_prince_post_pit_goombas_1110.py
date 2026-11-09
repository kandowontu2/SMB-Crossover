"""Measure the actual post-pit Goomba pair and original running-jump timings."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_second_pit_1110 as Second


R, N, Route, Recovery, I = Second.R, Second.N, Second.Route, Second.Recovery, Second.I
V5 = R/'build/prince-second-pit-native-1110'
CAPTURE = V5/'capture'
PREVIOUS = R/'build/prince-second-pit-1110/proof.json'
PREVIOUS_SHA = 'ed0910b9daf9310c0c44e00c18d93dd0371d948b87fbc7ec313ae1133996d01e'
STOP, TURN = 1490, 1477


def native_contact():
    full, pit, diag = (Second.First.Pit.Current.read(CAPTURE/n) for n in
                       ('full11.json','second-pit.json','prince-diagnostic.json'))
    assert all(q['ROM_sha256']==Route.PIN for q in (full,pit,diag))
    assert pit['passed'] and not full['passed'] and pit['state']['world_x']==1443
    assert (full['frames'],full['admitted'],full['HP'],full['state']['world_x'],full['state']['source_action'])==(
        6286,2765,0,1541,85)
    pre, = [q for q in diag['first_pipe_route']['precontacts'] if q['Main']==2765]
    assert pre['enemy']==dict(bound_control=9,flag=1,gap=10,high=1,id=6,slot=0,state=0,x=1551,y=184)
    assert pre['native_player_world']==[1543,184,1555,208] and pre['native_enemy_world']==[1554,198,1558,204]
    assert (pre['source_action'],pre['source_frame'],pre['source_mode'],pre['native_DY'],pre['native_no_stomp'])==(1,13,1,0,1)
    writes = [q for q in diag['first_pipe_route']['HP_bus_writes'] if q['Main']==2765]
    assert [(q['PC'],q['write_value']) for q in writes]==[(0xa345,n) for n in (3,2,1,0)]
    return dict(contact=pre,HP_writes=[dict(PC=q['PC'],value=q['write_value']) for q in writes],terminal=full['state'])


def authored(base):
    m = N.Bus(base)
    N.put(m,AreaPointer=37,AreaType=1,WorldNumber=0,LevelNumber=0,SelectedCharacter=38)
    N.invoke(m,'GetAreaDataAddrs')
    assert N.get(m,'AreaDataLow')+256*N.get(m,'AreaDataHigh')==I.address(base,'L_GroundArea6')+2
    at = I.address(base,'AreaObjectLength')
    m[at:at+3] = [255]*3
    columns = {}
    for col in range(112):
        N.put(m,CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32)
        N.invoke(m,'AreaParserCore')
        block = I.address(base,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
        columns[col] = [m[block+16*i+(col&15)] for i in range(13)]
    return columns


def arrival(base, columns):
    env, m, labels = Second.arrival(columns)
    _, choices, terminal, _ = Second.approach(env,m,labels)
    assert terminal=='takeoff-bound'
    (before,seed), = [(q,s) for q,s in choices if (q['x'],q['frame'],q['phase'])==(1342,11,1)]
    holder = None
    controls = Route.controls

    def capture(e,model,lab,pad):
        nonlocal holder
        holder = model
        return controls(e,model,lab,pad)

    Route.controls = capture
    try:
        crossing = Second.flight(env,seed,labels)
    finally:
        Route.controls = controls
    assert crossing['terminal']=='far-ground' and holder is not None
    assert (before['camera_right'],crossing['end']['x'],crossing['end']['hp'])==(1407,1441,4)
    for col in range(80,112):
        block = I.address(base,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
        for row,tile in enumerate(columns[col]):
            holder[block+row*16+(col&15)] = tile
    return env,holder,labels,crossing['end']


def observation(m, epoch):
    q = Recovery.sample(m,epoch)
    q['support'] = Recovery.grounded(m,q)
    q['enemy_cursor'] = N.get(m,'EnemyDataOffset')
    return q


def targets(q):
    return [a for a in q['actors'] if a['id']==6 and a['x']>=1510 and not a['state']&32]


def scan(env, seed, labels, turn):
    m = N.fork(seed)
    changes, states, births, choices = [],[],[],{}
    tracked = set()
    stage = 'initial' if turn else 'run-up'
    pads = {'initial':1,'brake-right':0,'left':2,'brake-left':0,'run-up':1}
    terminal = 'bound'
    for epoch in range(410):
        q = observation(m,epoch)
        x = q['x']
        actors = targets(q)
        for a in actors:
            if a['slot'] not in tracked:
                tracked.add(a['slot'])
                births.append(dict(actor=a,player=q))
        if q['hp']==0 or q['engine']!=8 or q['lives']!=2:
            terminal = 'contact-or-death'
            break
        prior = stage
        idle = q['support'] and q['frame']==15 and q['mode']==0 and q['a_lock']==0
        if stage=='initial' and x>=STOP:
            stage = 'brake-right'
        elif stage=='brake-right' and idle:
            stage = 'left'
        elif stage=='left' and x<=TURN and q['facing']==0:
            stage = 'brake-left'
        elif stage=='brake-left' and idle:
            stage = 'run-up'
        if stage!=prior:
            changes.append(dict(stage=stage,state=q))
        if epoch%8==0:
            states.append(q)
        ahead = [a for a in actors if a['x']>x and abs(a['y']-184)<=16]
        if stage=='run-up' and ahead and Recovery.running(m,q) and q['phase']<=1:
            a = min(ahead,key=lambda a:a['x'])
            gap = a['x']-x
            if 40<=gap<=139:
                bucket = (gap-40)//8
                if bucket not in choices:
                    choices[bucket] = q,a,N.fork(m)
        if x>=1625:
            terminal = 'past-contact-position'
            break
        if x<1433:
            terminal = 'retreated-to-lip'
            break
        Route.controls(env,m,labels,pads[stage])
    return dict(turn=turn,transitions=changes,samples=states,births=births,terminal=terminal,end=q),choices


def jump(env, seed, labels, actor):
    m = N.fork(seed)
    q = begin = observation(m,0)
    phases, contacts = [],[]
    previous = None
    admission = None
    target_slots = {a['slot'] for a in targets(begin)}
    assert actor['slot'] in target_slots
    terminal = 'bound'
    original = N.NesMPU

    class Trace(original):
        def step(self):
            if self.memory is m and self.pc==0xbd22 and m.rawtags[1]==3:
                contacts.append(dict(slot=self.x,state=observation(m,epoch)))
            return super().step()

    N.NesMPU = Trace
    try:
        for epoch in range(145):
            q = observation(m,epoch)
            actors = targets(q)
            if q['enemy_cursor']<=19:
                target_slots.update(a['slot'] for a in actors)
            key = q['action'],q['mode'],q['frame'],q['hp']
            if key!=previous:
                phases.append(q)
                previous = key
            if q['hp']==0 or q['engine']!=8 or q['lives']!=2:
                terminal = 'contact-or-death'
                break
            if q['action']==4 and admission is None:
                admission = q
            if admission and q['support'] and q['x']>=1620 and len(target_slots)>=2 and all(
                    a['x']+13<q['x']+2 for a in actors if a['slot'] in target_slots):
                terminal = 'pair-behind'
                break
            if not admission and epoch>28:
                terminal = 'no-A-admission'
                break
            Route.controls(env,m,labels,1 if admission else 129)
    finally:
        N.NesMPU = original
    return dict(begin=begin,target=actor,admission=admission,phases=phases,contacts=contacts,
                target_slots=sorted(target_slots),terminal=terminal,end=q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    assert sha256(PREVIOUS.read_bytes()).hexdigest()==PREVIOUS_SHA
    native = native_contact()
    template,_,_ = Second.First.Pit.Current.current()
    base = dict(template,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = authored(base)
    env, model, labels, entry = arrival(base,columns)
    approaches, attempts = [],[]
    for turn in (False,True):
        a,choices = scan(env,model,labels,turn)
        approaches.append(a)
        print('Approach',turn,a['terminal'],a['end']['x'],[(t['stage'],t['state']['x'],t['state']['camera_right'])
              for t in a['transitions']], 'births',[(b['actor']['x'],b['player']['x'],b['player']['camera_right'])
              for b in a['births']], 'legal',[(s['x'],s['camera_right'],a['x']-s['x'],s['frame'])
              for s,a,_ in choices.values()],flush=True)
        for q,a,seed in choices.values():
            f = jump(env,seed,labels,a)
            attempts.append(dict(turn=turn,**f))
            print('A',turn,q['x'],a['x']-q['x'],q['camera_right'],f['terminal'],f['end']['x'],f['end']['hp'],
                  [(p['frame'],p['x'],p['foot']) for p in f['phases'] if 39<=p['frame']<=43],flush=True)
            if f['terminal']=='pair-behind':
                break
        if attempts and attempts[-1]['terminal']=='pair-behind':
            break
    refs = (Path(__file__),Path(Second.__file__),Route.ROM,PREVIOUS,
            *(CAPTURE/n for n in ('full11.json','second-pit.json','prince-diagnostic.json')))
    out.mkdir()
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                 native_negative=native,CPU_second_pit=entry,approaches=approaches,attempts=attempts,
                 authored_columns={16*i:columns[i] for i in range(91,106)},
                 scope='Actual donor and native GameLoop following prior authored second-pit CPU landing. '
                       'One-time installation of later native parser tiles; future native enemy parser and '
                       'original controller inputs only. Native emulator route remains unverified.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

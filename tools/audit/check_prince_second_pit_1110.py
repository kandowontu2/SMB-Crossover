"""Qualify a supported Prince run-up at the actual 48-pixel second pit."""

import argparse
import csv
from hashlib import sha256
import json
from pathlib import Path

import prepare_prince_first_pit_native_1110 as First


R, N, Route, Recovery = First.R, First.N, First.Route, First.Recovery
I = Route.I
OLD = R/'build/prince-first-pit-native-1110'
CAPTURE = OLD/'native/capture'
LEFT, RIGHT = 1376, 1424
BRAKE_RIGHT, BRAKE_LEFT = 1320, 1312


def native_failure():
    full, first, diag = (First.Pit.Current.read(CAPTURE/name) for name in
                         ('full11.json','first-pit.json','prince-diagnostic.json'))
    assert all(q['ROM_sha256']==Route.PIN for q in (full,first,diag))
    assert first['passed'] and first['state']['world_x']==1154 and not full['passed']
    assert (full['frames'],full['admitted'],full['route']['index'],full['state']['world_x'],
            full['state']['native_y'],full['engine'],full['HP'],full['final_lives'])==(5818,2528,5,1409,246,11,4,2)
    events = [q for q in full['route']['events'] if q['Main'] in (2381,2383,2427)]
    assert [(q['tag'],q['world_x'],q['source_action']) for q in events]==[
        ('takeoff',1291,1),('aerial',1291,4),('approach',1316,1)]
    assert full['route']['jump']['world_x']==1291 and 'combat' not in full['route']
    assert not [q for q in diag['first_pipe_route']['HP_bus_writes'] if q['Main']>=2381]
    with (CAPTURE/'source-phases.csv').open(newline='') as stream:
        fall, = [q for q in csv.DictReader(stream) if q['event']=='original-advance-return' and q['wrappers']=='2505']
    assert tuple(int(fall[n]) for n in ('world_x','source_action','source_frame','pad','HP','lives'))==(1404,7,102,1,4,2)
    return dict(short_jump=events,original_fall=fall,terminal=full['state'])


def second_columns(base):
    m = N.Bus(base)
    N.put(m,AreaPointer=37,AreaType=1,WorldNumber=0,LevelNumber=0,SelectedCharacter=38)
    N.invoke(m,'GetAreaDataAddrs')
    assert N.get(m,'AreaDataLow')+256*N.get(m,'AreaDataHigh')==I.address(base,'L_GroundArea6')+2
    at = I.address(base,'AreaObjectLength')
    m[at:at+3] = [255]*3
    columns = {}
    for col in range(100):
        N.put(m,CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32)
        N.invoke(m,'AreaParserCore')
        block = I.address(base,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
        columns[col] = [m[block+16*i+(col&15)] for i in range(13)]
    assert [columns[i][11] for i in range(85,90)]==[84,0,0,0,84]
    return columns


def arrival(columns):
    # Reuse the previously qualified CPU first-pit prefix. The final GameLoop
    # call is observed only to retain the complete actual resulting model.
    holder = None
    flight, controls = First.Late.flight, Route.controls

    def retain(env, model, labels, pad):
        nonlocal holder
        holder = env, model, labels
        return controls(env,model,labels,pad)

    def run(*args):
        Route.controls = retain
        try:
            return flight(*args)
        finally:
            Route.controls = controls

    First.Late.flight = run
    try:
        prior = First.qualify()
    finally:
        First.Late.flight = flight
    assert holder is not None
    env, m, labels = holder
    assert Recovery.sample(m,0)=={k:v for k,v in prior['flight']['end'].items()
                                 if k not in ('support','lip_tiles','scroll','epoch')} | {'epoch':0}
    for col in range(68,100):
        block = I.address(m.bundle,'Block_Buffer_2' if col&16 else 'Block_Buffer_1')
        for row,tile in enumerate(columns[col]):
            m[block+row*16+(col&15)] = tile
    return env,m,labels


def sample(m, epoch):
    q = Recovery.sample(m,epoch)
    q['support'] = Recovery.grounded(m,q)
    q['lips'] = [Route.query_support(m,x,208) for x in range(1360,1425,16)]
    assert q['lips']==[84,0,0,0,84]
    return q


def approach(env, seed, labels):
    m = N.fork(seed)
    modes = {'initial':1,'brake-right':0,'left':2,'brake-left':0,'run-up':1}
    stage = 'initial'
    events, choices = [],[]
    seen = set()
    for epoch in range(570):
        q = sample(m,epoch)
        x = q['x']
        if (q['engine'],q['hp'],q['lives'])!=(8,4,2):
            return events,choices,'contact-or-death',q
        idle = q['support'] and q['frame']==15 and q['mode']==0 and q['a_lock']==0
        previous = stage
        if stage=='initial' and x>=BRAKE_RIGHT:
            stage = 'brake-right'
        elif stage=='brake-right' and idle:
            stage = 'left'
        elif stage=='left' and x<=BRAKE_LEFT and q['facing']==0:
            stage = 'brake-left'
        elif stage=='brake-left' and idle:
            stage = 'run-up'
        elif stage=='run-up' and 1328<=x<=1356 and Recovery.running(m,q):
            key = (x,q['frame'],q['phase'])
            if key not in seen:
                choices.append((q,N.fork(m)))
                seen.add(key)
        if stage!=previous:
            events.append(dict(stage=stage,state=q))
        if x>=1361:
            return events,choices,'takeoff-bound',q
        Route.controls(env,m,labels,modes[stage])
    return events,choices,'approach-bound',q


def flight(env, seed, labels):
    m = N.fork(seed)
    q = begin = sample(m,0)
    poses = []
    admitted = None
    previous = None
    terminal = 'bound'
    for epoch in range(104):
        q = sample(m,epoch)
        key = (q['action'],q['frame'],q['mode'])
        if key!=previous:
            poses.append(q)
            previous = key
        if (q['engine'],q['hp'],q['lives'])!=(8,4,2):
            terminal = 'contact-or-death'
            break
        if q['action']==4 and admitted is None:
            admitted = q
        if admitted and q['x']>=RIGHT+16 and q['y']==176 and q['support']:
            terminal = 'far-ground'
            break
        if admitted and q['y']>215:
            terminal = 'below-far-lip'
            break
        if admitted and q['action']!=4 and epoch>=15 and q['x']+13<LEFT and q['y']==176 and q['support']:
            terminal = 'short-ground'
            break
        if not admitted and epoch>28:
            terminal = 'not-admitted'
            break
        Route.controls(env,m,labels,1 if admitted else 129)
    return dict(begin=begin,admission=admitted,poses=poses,terminal=terminal,end=q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    first_proof = OLD/'turn-evidence.json'
    assert sha256(first_proof.read_bytes()).hexdigest()=='6477a3ec72ff533f0723800fe019ad92bbced02680176e31d9194f3f7aaf7be3'
    negative = native_failure()
    template,_,_ = First.Pit.Current.current()
    base = dict(template,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = second_columns(base)
    env,m,labels = arrival(columns)
    transitions,choices,terminal,end = approach(env,m,labels)
    print('Approach:',terminal,[(p['stage'],p['state']['x'],p['state']['camera_right']) for p in transitions],
          'legal requests:',[(q['x'],q['frame'],q['phase'],q['camera_right']) for q,_ in choices],flush=True)
    attempts = []
    considered = set()
    for q,seed in choices:
        key = q['x'],q['frame']
        if q['phase']>1 or key in considered:
            continue
        considered.add(key)
        got = flight(env,seed,labels)
        attempts.append(got)
        print('Request',q['x'],q['frame'],q['phase'],q['camera_right'],got['terminal'],got['end']['x'],
              [(p['frame'],p['x'],p['foot']) for p in got['poses'] if 39<=p['frame']<=44],flush=True)
    refs = (Path(__file__),first_proof,Path(First.__file__),Route.ROM,
            *(CAPTURE/name for name in ('first-pit.json','full11.json','prince-diagnostic.json','source-phases.csv')))
    receipt = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,native_negative=negative,
                   authored_columns={16*i:columns[i] for i in range(81,94)},
                   approach=transitions,approach_terminal=terminal,approach_end=end,
                   legal_requests=[q for q,_ in choices],flights=attempts,
                   scope='Actual compiled native AreaParserCore tiles, installed once at the prior CPU first-pit '
                         'landing. Then actual donor and native GameLoop with original controller input only. '
                         'The CPU fixture does not establish a native Mesen crossing.',
                   bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    out.mkdir()
    (out/'proof.json').write_text(json.dumps(receipt,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

"""Test pre-birth running A and the authored high block against the native pair."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_post_pit_goombas_1110 as Pair


R, N, Route, Recovery = Pair.R, Pair.N, Pair.Route, Pair.Recovery
PARENT = R/'build/prince-post-pit-goombas-1110/proof.json'
PARENT_SHA = '42d54fe5361411c63e8cdf2231eae2fa866672beee123189069ea222c85d202e'


def runway(env, seed, labels, stop):
    m = N.fork(seed)
    stage = 'approach'
    transitions, asks, ledges = [],[],[]
    seen = set()
    for epoch in range(395):
        q = Pair.observation(m,epoch)
        x = q['x']
        if q['hp']==0 or q['engine']!=8 or q['lives']!=2 or x<1433 or x>=1511 and stage=='run-up':
            break
        idle = q['support'] and q['frame']==15 and q['mode']==0 and q['a_lock']==0
        previous = stage
        if stage=='approach' and x>=stop:
            stage = 'brake-right'
        elif stage=='brake-right' and idle:
            stage = 'left'
        elif stage=='left' and x<=Pair.TURN and q['facing']==0:
            stage = 'brake-left'
        elif stage=='brake-left' and idle:
            stage = 'run-up'
        if stage!=previous:
            transitions.append(dict(stage=stage,state=q))
        if stage=='run-up' and Recovery.running(m,q) and q['phase']<=1:
            k = x,q['frame']
            if k not in seen and 1463<=x<=1490:
                if q['enemy_cursor']==15:
                    asks.append((q,N.fork(m)))
                if 1470<=x<=1486:
                    ledges.append((q,N.fork(m)))
                seen.add(k)
        Route.controls(env,m,labels,{'approach':1,'left':2,'brake-right':0,'brake-left':0,'run-up':1}[stage])
    return transitions,asks,ledges,q


def attempt(env, seed, labels, method):
    m = N.fork(seed)
    q = begin = Pair.observation(m,0)
    stage = 'A' if method=='jump' else 'brake'
    previous = None
    changed = 0
    phases, contacts, births, events = [],[],[],[]
    pair_slots = set()
    admission = None
    cap = None
    terminal = 'bound'
    native = N.NesMPU

    class Trace(native):
        def step(self):
            if self.memory is m and self.pc==0xbd22 and m.rawtags[1]==3:
                contacts.append(dict(slot=self.x,state=Pair.observation(m,epoch)))
            return super().step()

    N.NesMPU = Trace
    try:
        for epoch in range(235):
            q = Pair.observation(m,epoch)
            x = q['x']
            if q['enemy_cursor'] in (17,19):
                for a in Pair.targets(q):
                    if a['slot'] not in pair_slots:
                        pair_slots.add(a['slot'])
                        births.append(dict(actor=a,player=q))
            tracked = [a for a in q['actors'] if a['slot'] in pair_slots and a['id']==6 and not a['state']&32]
            behind = len(pair_slots)>=2 and len(tracked)==2 and all(a['x']+13<x+2 for a in tracked)
            key = stage,q['action'],q['frame'],q['mode'],q['hp']
            if key!=previous:
                phases.append(q)
                previous = key
            if q['hp']==0 or q['lives']!=2 or q['engine']!=8:
                terminal = 'contact-or-death'
                break
            old = stage
            if stage=='A' and q['action']==4:
                stage = 'flight'
                admission = q
            elif stage=='brake' and q['frame']==15 and q['mode']==0 and q['support'] and q['a_lock']==0:
                stage = 'up'
            elif stage=='up' and (q['mode'] in (2,6) or q['action']==10):
                stage = 'climb'
            elif stage=='climb' and 111<=q['y']<=115 and q['support'] and q['frame']==15 and 1491<=x<1520:
                assert any(Route.query_support(m,x+dx,144)==88 for dx in (2,13))
                stage = 'perch'
                cap = q
            elif stage=='perch' and behind:
                stage = 'exit'
            if stage!=old:
                events.append(dict(stage=stage,state=q))
                changed = epoch
            if stage in ('flight','exit') and x>=1600 and q['y']==176 and q['support'] and behind:
                terminal = 'pair-behind'
                break
            if epoch-changed>{'A':28,'brake':100,'up':125,'climb':100,'perch':130,'flight':135,'exit':125}[stage]:
                terminal = f'{stage}-bound'
                break
            Route.controls(env,m,labels,{'A':129,'flight':1,'brake':0,'up':8,'climb':8,'perch':0,'exit':1}[stage])
    finally:
        N.NesMPU = native
    return dict(method=method,begin=begin,admission=admission,cap=cap,births=births,events=events,
                phases=phases,contacts=contacts,terminal=terminal,end=q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'early.json').exists()
    assert sha256(PARENT.read_bytes()).hexdigest()==PARENT_SHA
    base,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(base,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = Pair.authored(base)
    assert columns[94][7]==88 and columns[94][11]==84
    env,seed,labels,_ = Pair.arrival(base,columns)
    results, runs = [],[]
    for stop in (1490,1501):
        transitions,asks,ledges,last = runway(env,seed,labels,stop)
        runs.append(dict(stop=stop,transitions=transitions,end=last))
        print('Runway',stop,[(e['stage'],e['state']['x'],e['state']['camera_right']) for e in transitions],
              'A',[(q['x'],q['camera_right']) for q,_ in asks],'Up',[(q['x'],q['camera_right']) for q,_ in ledges],flush=True)
        for method, choices in (('jump',asks),('ledge',ledges)):
            for q,m in choices:
                f = attempt(env,m,labels,method)
                results.append(dict(stop=stop,**f))
                print(stop,method,q['x'],q['camera_right'],f['terminal'],f['end']['x'],f['end']['hp'],
                      [(e['stage'],e['state']['x'],e['state']['y']) for e in f['events']],flush=True)
                if f['terminal']=='pair-behind':
                    break
            if results and results[-1]['terminal']=='pair-behind':
                break
        if results and results[-1]['terminal']=='pair-behind':
            break
    refs = (Path(__file__),Path(Pair.__file__),PARENT,Route.ROM,R/'src/level_tiles.s')
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,runs=runs,attempts=results,
                 scope='Prior actual parser corridor and second-pit CPU landing. Only authentic buttons change after '
                       'that fixture. Both original approaches use the natural group birth and active enemy flags.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'early.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

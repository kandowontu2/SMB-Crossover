"""Qualify Prince's original standing A from the authored block above both Goombas."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_post_pit_early_1110 as Early


Pair, R, N, Route = Early.Pair, Early.R, Early.N, Early.Route
PRIOR = Early.PARENT.with_name('early.json')
PRIOR_SHA = '53f1d218994f640e64da03c342aab1b94245e1a30d0833f68848d3071ddf8ff1'


def takeoff(env, model, labels):
    _, _, ledges, _ = Early.runway(env,model,labels,1490)
    (begin, seed), = [(q,s) for q,s in ledges if (q['x'],q['camera_right'])==(1474,1545)]
    controls = Route.controls
    cap = None

    class CapReached(Exception):
        pass

    def capture(e,m,lab,pad):
        nonlocal cap
        q = Pair.observation(m,0)
        if (q['x'],q['y'],q['action'],q['frame'],q['mode'])==(1491,112,10,15,0) and q['support']:
            cap = N.fork(m)
            raise CapReached
        return controls(e,m,lab,pad)

    Route.controls = capture
    try:
        Early.attempt(env,seed,labels,'ledge')
    except CapReached:
        pass
    finally:
        Route.controls = controls
    assert cap is not None
    return begin,cap


def leap(env, seed, labels, release):
    m = N.fork(seed)
    start = Pair.observation(m,0)
    assert (start['x'],start['y'],start['action'],start['frame'],start['mode'],start['a_lock'])==(1491,112,10,15,0,0)
    pair = {a['slot'] for a in start['actors'] if a['id']==6 and 1470<=a['x']<=1520 and a['y']==184}
    assert len(pair)==2 and sorted(a['x'] for a in start['actors'] if a['slot'] in pair)==[1485,1509]
    assert Route.query_support(m,1504,144)==88 and start['support']
    admission = None
    phases, contacts = [],[]
    previous = None
    terminal = 'bound'
    native = N.NesMPU

    class Trace(native):
        def step(self):
            if self.memory is m and self.pc==0xbd22 and m.rawtags[1]==3:
                contacts.append(dict(slot=self.x,state=Pair.observation(m,epoch)))
            return super().step()

    N.NesMPU = Trace
    try:
        for epoch in range(145):
            q = Pair.observation(m,epoch)
            key = q['action'],q['frame'],q['mode'],q['hp']
            if key!=previous:
                phases.append(q)
                previous = key
            if q['hp']==0 or q['engine']!=8 or q['lives']!=2:
                terminal = 'contact-or-death'
                break
            if q['action']==3 and admission is None:
                admission = q
            actors = [a for a in q['actors'] if a['slot'] in pair and a['id']==6 and not a['state']&32]
            if admission and q['x']>=1545 and q['y']==176 and q['support'] and len(actors)==2 and all(
                    a['x']+13<q['x']+2 for a in actors):
                terminal = 'pair-behind'
                break
            if not admission and epoch>28:
                terminal = 'no-A-admission'
                break
            Route.controls(env,m,labels,128 if admission is None else release)
    finally:
        N.NesMPU = native
    return dict(start=start,admission=admission,phases=phases,contacts=contacts,terminal=terminal,end=q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'cap.json').exists()
    assert sha256(PRIOR.read_bytes()).hexdigest()==PRIOR_SHA
    base,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(base,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = Pair.authored(base)
    env,model,labels,_ = Pair.arrival(base,columns)
    begin,cap = takeoff(env,model,labels)
    result = leap(env,cap,labels,1)
    print(result['terminal'],result['end']['x'],result['end']['y'],result['end']['hp'],
          'action3',None if not result['admission'] else result['admission']['epoch'],
          'actors',result['end']['actors'],'contacts',len(result['contacts']),flush=True)
    refs = (Path(__file__),Path(Early.__file__),Path(Pair.__file__),PRIOR,Route.ROM)
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                 ledge_request=begin,standing_A=result,
                 scope='Authentic running/turn/Up and original standing A from actual authored $58 block. '
                       'Both enemy actors come from the unchanged native group parser in the CPU fixture.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'cap.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

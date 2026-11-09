"""Check an original facing turn before each careful step at the high brick."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_post_pit_delayed_group_1110 as Delayed


Pair, R, Route = Delayed.Pair, Delayed.R, Delayed.Route


def align(env, m, labels):
    stage = 'approach'
    moves = []
    pads = {'approach':1,'brake':0,'face-left':2,'settle-left':0,'step-left':64,'stop-left':0,
            'face-right':1,'settle-right':0,'step-right':64}
    for epoch in range(460):
        q = Pair.observation(m,epoch)
        x = q['x']
        idle = q['support'] and q['frame']==15 and q['mode']==0 and q['a_lock']==0
        if (q['engine'],q['lives'],q['hp'])!=(8,2,4) or not 1435<=x<=1510:
            break
        previous = stage
        if stage=='approach' and x>=1467:
            stage = 'brake'
        elif stage=='brake' and idle:
            stage = 'face-left'
        elif stage=='face-left' and q['facing']==0:
            stage = 'settle-left'
        elif stage=='settle-left' and idle:
            stage = 'step-left'
        elif stage=='step-left' and q['action']==42 and q['frame']==127:
            stage = 'stop-left'
        elif stage=='stop-left' and idle:
            stage = 'face-right'
        elif stage=='face-right' and q['facing']==255:
            stage = 'settle-right'
        elif stage=='settle-right' and idle:
            stage = 'step-right'
        elif stage=='step-right' and q['action']==42 and q['frame']==127:
            moves.append(dict(stage='climb-brake',state=q))
            return moves,q,True
        if previous!=stage:
            moves.append(dict(stage=stage,state=q))
        Route.controls(env,m,labels,pads[stage])
    return moves,q,False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    previous = out/'careful.json'
    assert out.is_relative_to(R/'build') and not (out/'careful-turn.json').exists()
    assert sha256(previous.read_bytes()).hexdigest()=='d32562a5a73b400e5b41ed61496ff12191f0b13c4879b6f65e6477812dabe996'
    base,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(base,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = Pair.authored(base)
    env,model,labels,_ = Pair.arrival(base,columns)
    moves,at,ready = align(env,model,labels)
    print('Alignment',ready,[(e['stage'],e['state']['x'],e['state']['camera_right'],e['state']['facing'])
                             for e in moves], 'end',at['x'],at['frame'],at['facing'],flush=True)
    result = Delayed.climb_and_hop(env,model,labels) if ready else None
    if result:
        print('Climb',result['terminal'],result['end']['x'],result['end']['hp'],
              [(e['stage'],e['state']['epoch'],e['state']['x'],e['state']['camera_right']) for e in result['events']],
              [(a['actor']['x'],a['player']['epoch']) for a in result['births']],flush=True)
    refs = (Path(__file__),Path(Delayed.__file__),previous,Delayed.NATIVE,Route.ROM)
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,moves=moves,end=at,result=result,
                 scope='Original direction and neutral before each original B step, then actual Up and standing A. '
                       'All actors come from the genuine native group parser after the earlier authored CPU fixture.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'careful-turn.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

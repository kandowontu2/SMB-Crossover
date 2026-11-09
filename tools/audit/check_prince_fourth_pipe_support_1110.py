"""Qualify the fourth-pipe controller through the original hang and cap."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_fourth_pipe_1110 as Fourth


Approach,Recovery,Route,R,P,N,Current=Fourth.Approach,Fourth.Recovery,Fourth.Route,Fourth.R,Fourth.P,Fourth.N,Fourth.Current
PREVIOUS='813fe771ce2410b777d5a7104fc4c9ce9bc5398d5db1c9b96167aca0d9ed8833'
PREVIOUS_SUPPORT='00e3a28b5035f8e596eb2016d971375fe1cac39cbf99fc9da254e3b0ade1ff43'


def replay(env,seed,labels,policy):
    m=N.fork(seed)
    mode='settle' if policy=='early-settle' else 'approach'
    changed=0
    events,poses=[],[]
    terminal='bound'
    last=None
    cap_seen=False
    maximum=0
    for epoch in range(340):
        q=Recovery.sample(m,epoch)
        x,y,pose=q['x'],q['y'],q['frame']
        maximum=max(maximum,x)
        q['pipe_top']=[Route.query_support(m,i,144) for i in (912,928)]
        key=q['action'],pose,q['mode'],mode,q['hp']
        if key!=last:
            poses.append(q)
            last=key
        age=epoch-changed
        support=Recovery.grounded(m,q)
        next_mode=mode
        if q['hp']==0 or q['engine']!=8 or q['lives']!=2:
            terminal='death'
            break
        if mode=='approach' and x>=896:
            next_mode='settle'
        elif mode=='settle' and support and pose==15 and q['mode']==0 and q['a_lock']==0:
            next_mode='up'
        elif mode=='up' and (q['mode'] in (2,6) or q['action']==10):
            next_mode='climb'
        elif mode=='climb' and q['action']==10:
            if policy in ('settled-cap','standing-cap'):
                if support and pose==15 and q['mode']==0 and x+13>=912 and y in range(111,115):
                    if policy=='standing-cap':
                        cap_seen=True
                        events.append(dict(transition='physical-cap',row=q))
                        next_mode='cap-A'
                    else:
                        next_mode='cap'
            elif q['foot']<=147:
                next_mode='cap'
        elif mode=='cap-A':
            if q['action']==3:
                next_mode='cap'
            elif age>28:
                terminal='standing-A-unadmitted'
                break
        if mode=='cap' and not cap_seen and support and x+13>=912 and x<944 and y in range(111,115):
            cap_seen=True
            events.append(dict(transition='physical-cap',row=q))
        if cap_seen and support and x>=960 and y==176:
            terminal='clear'
            break
        if next_mode!=mode:
            events.append(dict(transition=f'{mode} to {next_mode}',row=q))
            mode,changed=next_mode,epoch
        elif age>200:
            terminal=f'{mode}-bound'
            break
        pad={'approach':1,'settle':0,'up':8 if epoch-changed<64 else 201,
             'climb':9 if policy=='legacy' else 8,'cap-A':128,'cap':1}[mode]
        Route.controls(env,m,labels,pad)
    return dict(policy=policy,events=events,poses=poses,terminal=terminal,maximum=maximum,end=q)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--standing',action='store_true')
    args=p.parse_args()
    out=args.output.resolve()
    receipt=out/'support.json'
    assert out.is_relative_to(R/'build')
    if args.standing:
        assert sha256(receipt.read_bytes()).hexdigest()==PREVIOUS_SUPPORT
        earlier=Current.read(receipt)
    else:
        assert not receipt.exists()
    parent=out/'proof.json'
    assert sha256(parent.read_bytes()).hexdigest()==PREVIOUS
    raw=Route.ROM.read_bytes()
    assert sha256(raw).hexdigest()==Route.PIN
    template,_,_=Current.current()
    env,seed,labels,_=Approach.Earned.fixture(dict(template,raw=raw))
    results=[]
    cases=((707,779,('standing-cap',)),(748,785,('standing-cap',))) if args.standing else (
        (707,779,('legacy','up-only','settled-cap','early-settle')),
        (707,773,('early-settle',)),(748,785,('up-only','early-settle')))
    for right_start,goal,policies in cases:
        m,arrival=Fourth.arrival(env,seed,labels,right_start,goal)
        assert arrival['terminal']=='cleared'
        trials=[]
        for policy in policies:
            q=replay(env,m,labels,policy)
            trials.append(q)
            print(right_start,goal,policy,q['terminal'],q['maximum'],q['end']['x'],q['end']['hp'],
                  [(r['transition'],r['row']['epoch'],r['row']['x']) for r in q['events']],flush=True)
        results.append(dict(start_right=right_start,goal=goal,third=arrival,fourth=trials))
    refs=(Path(__file__),Path(Fourth.__file__),Route.ROM,parent)
    report=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,results=results,
                scope='Original donor and native pipe/camera/enemy execution after explicit corridor and terrain placement. '
                      'The controlled difference is Up/recovery timing and direction only.',
                bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    if args.standing:
        report['prior_CPU_receipt_SHA256']=PREVIOUS_SUPPORT
        report['prior_CPU_results']=earlier['results']
    temp=out/'support-pending.json'
    temp.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    temp.replace(receipt)


if __name__=='__main__':
    main()

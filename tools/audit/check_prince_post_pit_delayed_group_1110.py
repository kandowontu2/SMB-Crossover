"""Qualify the actual high brick climb with a later native Goomba-group birth."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_post_pit_cap_1110 as Cap


Pair, Early, R, N, Route = Cap.Pair, Cap.Early, Cap.R, Cap.N, Cap.Route
ROOT = R/'build/prince-post-pit-goombas-1110'
CAPTURE = ROOT/'native/capture'
NATIVE = CAPTURE/'post-pit-goombas.json'
NATIVE_SHA = '934784bfefa69eb94c14f19006c68c68663a29b3561ed4afae26e4e2772c2eb1'


def failure():
    assert sha256(NATIVE.read_bytes()).hexdigest()==NATIVE_SHA
    q = Pair.Second.First.Pit.Current.read(NATIVE)
    events = {e['stage']:e for e in q['route']['events']}
    assert not q['passed'] and q['ROM_sha256']==Route.PIN
    assert (q['frame'],q['state']['world_x'],q['state']['source_frame'],q['state']['HP'])==(6719,1503,76,0)
    assert (events['brake-ledge']['Main'],q['group']['begin']['Main'],events['up']['Main'])==(2921,2925,2962)
    assert [a['x'] for a in q['group']['births']]==[1552,1576]
    return dict(brake=events['brake-ledge'],birth=q['group']['begin'],up=events['up'],terminal=q['state'])


def direct(env, seed, labels):
    m = N.fork(seed)
    options = []
    seen = set()
    for epoch in range(55):
        q = Pair.observation(m,epoch)
        x = q['x']
        if x>=1482:
            break
        if 1466<=x and q['support'] and q['facing']==255 and q['action']==1 and q['phase']<=1 and x not in seen:
            options.append((q,N.fork(m)))
            seen.add(x)
        Route.controls(env,m,labels,1)
    return options


def climb_and_hop(env, seed, labels):
    m = N.fork(seed)
    pads = dict(brake=0,up=8,climb=8,cap_A=128,flight=1)
    bounds = dict(brake=100,up=110,climb=100,cap_A=28,flight=140)
    stage, changed = 'brake',0
    result = dict(terminal='bound',births=[],events=[],poses=[],contacts=[])
    actors_seen = set()
    previous = None
    native = N.NesMPU

    class Trace(native):
        def step(self):
            if self.memory is m and self.pc==0xbd22 and m.rawtags[1]==3:
                result['contacts'].append(dict(slot=self.x,state=Pair.observation(m,epoch)))
            return super().step()

    N.NesMPU = Trace
    try:
        for epoch in range(335):
            q = Pair.observation(m,epoch)
            x,y = q['x'],q['y']
            key = stage,q['action'],q['mode'],q['frame'],q['hp']
            if key!=previous:
                result['poses'].append(q)
                previous = key
            if q['enemy_cursor'] in (17,19):
                for a in Pair.targets(q):
                    if a['slot'] not in actors_seen:
                        actors_seen.add(a['slot'])
                        result['births'].append(dict(actor=a,player=q))
            if (q['engine'],q['lives'],q['hp'])!=(8,2,4):
                result['terminal'] = 'contact-or-death'
                break
            prior = stage
            idle = q['support'] and q['frame']==15 and q['mode']==0 and q['a_lock']==0
            if stage=='brake' and idle:
                if not 1484<=x<=1501 or y!=176:
                    result['terminal'] = 'outside-up-scan'
                    break
                stage = 'up'
            elif stage=='up' and (q['mode'] in (2,6) or q['action']==10):
                stage = 'climb'
            elif stage=='climb' and q['action']==10 and idle and 111<=y<=115 and any(
                    Route.query_support(m,x+dx,144)==88 for dx in (2,13)):
                stage = 'cap_A'
            elif stage=='cap_A' and q['action']==3:
                stage = 'flight'
            if stage!=prior:
                changed = epoch
                result['events'].append(dict(stage=stage,state=q))
            if stage=='flight' and x>=1545 and y==176 and q['support']:
                group = [a for a in q['actors'] if a['slot'] in actors_seen and a['id']==6 and not a['state']&32]
                if len(group)==2 and all(a['x']+13<x+2 for a in group):
                    result['terminal'] = 'pair-behind'
                    break
            if epoch-changed>bounds[stage]:
                result['terminal'] = f'{stage}-bound'
                break
            Route.controls(env,m,labels,pads[stage])
    finally:
        N.NesMPU = native
    return dict(result,end=q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not out.exists()
    native = failure()
    base,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(base,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = Pair.authored(base)
    env,seed,labels,_ = Pair.arrival(base,columns)
    attempts, approaches = [],[]
    for stop in (1480,1474,0):
        if stop:
            moves,_,options,last = Early.runway(env,seed,labels,stop)
            approaches.append(dict(stop=stop,transitions=moves,last=last))
            options = [(q,m) for q,m in options if q['camera_right']<=1545]
        else:
            options = direct(env,seed,labels)
        print('Brake policy',stop,[(q['x'],q['frame'],q['phase'],q['camera_right']) for q,_ in options],flush=True)
        for q,m in options:
            f = climb_and_hop(env,m,labels)
            attempts.append(dict(stop=stop,request=q,**f))
            print('Trial',stop,q['x'],q['camera_right'],f['terminal'],f['end']['x'],f['end']['hp'],
                  [(e['stage'],e['state']['epoch'],e['state']['x'],e['state']['camera_right']) for e in f['events']],
                  [(a['actor']['x'],a['player']['epoch']) for a in f['births']],flush=True)
            if f['terminal']=='pair-behind' and not f['contacts']:
                break
        if attempts and attempts[-1]['terminal']=='pair-behind' and not attempts[-1]['contacts']:
            break
    refs = (Path(__file__),Path(Early.__file__),Path(Pair.__file__),NATIVE,Route.ROM)
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                 native_failure=native,approaches=approaches,attempts=attempts,
                 scope='Later real native group activation by changes to controller approach only. '
                       'The authentic authored terrain CPU fixture enters on the previously qualified second-pit landing.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    out.mkdir()
    (out/'proof.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

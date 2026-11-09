"""Check an original reverse jump and native Goomba fall at the second pit."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_post_pit_landing_writer_1110 as W


R, Route, Pair, N = W.R,W.Route,W.Pair,W.N
ROOT = R/'build/prince-post-pit-landing-writer-1110'
V7 = ROOT/'native/capture/post-pit-goombas.json'


def run_ready(q, face):
    return q['support'] and q['action']==1 and q['mode']==1 and 6<=q['frame']<=13 and q['a_lock']==0 and q['facing']==face


def observe(m, epoch):
    q = Pair.observation(m,epoch)
    q['pit'] = [Route.query_support(m,x,208) for x in range(1360,1425,16)]
    assert q['pit']==[84,0,0,0,84]
    return q


def legal_requests(env, seed, labels, face):
    m = N.fork(seed)
    end = None
    options = []
    seen = set()
    for epoch in range(150):
        q = observe(m,epoch)
        x = q['x']
        end = q
        if (q['hp'],q['lives'],q['engine'])!=(4,2,8):
            break
        if (face==0 and x<1432) or (face==255 and x>1362):
            break
        actor_x = [a['x'] for a in q['actors'] if a['id']==6 and a['x']>x]
        gap = min(actor_x)-x if actor_x else None
        candidate = (1442<=x<=1478 and gap is not None and gap>=34) if face==0 else 1335<=x<=1358
        if candidate and run_ready(q,face) and q['phase']<=1 and (x,q['frame']) not in seen:
            seen.add((x,q['frame']))
            options.append((q,N.fork(m)))
        Route.controls(env,m,labels,2 if face==0 else 1)
    return options,end


def flight(env, seed, labels, face):
    m = N.fork(seed)
    begin = observe(m,0)
    assert run_ready(begin,face)
    direction = 2 if face==0 else 1
    admission,previous = None,None
    rows = []
    terminal = 'bound'
    for epoch in range(120):
        q = observe(m,epoch)
        key = q['action'],q['frame'],q['mode']
        if key!=previous:
            rows.append(q)
            previous = key
        if (q['hp'],q['lives'],q['engine'])!=(4,2,8):
            terminal = 'contact-or-death'
            break
        if q['action']==4 and admission is None:
            admission = q
        on_bank = q['x']<=1363 if face==0 else q['x']>=1440
        if admission and on_bank and q['y']==176 and q['support']:
            terminal = 'far-ground'
            break
        if q['y']>=215:
            terminal = 'below-bank'
            break
        if not admission and epoch>28:
            terminal = 'not-admitted'
            break
        Route.controls(env,m,labels,direction if admission else 128|direction)
    return dict(face=face,request=begin,admission=admission,poses=rows,terminal=terminal,end=q),m


def wait_for_fall(env, m, labels, slots):
    first_fall, cleared = {},{}
    for epoch in range(330):
        q = observe(m,epoch)
        if (q['hp'],q['lives'],q['engine'])!=(4,2,8) or q['x']<1307 or q['x']>=1370:
            break
        active = {a['slot']:a for a in q['actors'] if a['id']==6 and a['slot'] in slots}
        for slot in slots:
            a = active.get(slot)
            if a and 1376<=a['x']<1424 and a['y']>=204 and slot not in first_fall:
                first_fall[slot] = dict(actor=a,player=q)
            if a is None and slot in first_fall and slot not in cleared:
                cleared[slot] = q
        if len(cleared)==len(slots) and q['support'] and q['frame']==15 and q['mode']==0:
            return dict(passed=True,falls=first_fall,cleared=cleared,end=q)
        Route.controls(env,m,labels,0)
    return dict(passed=False,falls=first_fall,cleared=cleared,end=q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out==ROOT/'retreat' and not out.exists()
    previous = ROOT/'writer.json'
    assert sha256(previous.read_bytes()).hexdigest()=='b02298eaf32bc8763f39691972d958c877f7f7b4e2f961cca284b8594ca91fa3'
    native = W.Brick.Delayed.Pair.Second.First.Pit.Current.read(V7)
    assert native['ROM_sha256']==Route.PIN and not native['passed'] and native['state']['source_frame']==78
    base,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(base,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    env,model,labels,_ = Pair.arrival(base,Pair.authored(base))
    _,_,ready = W.Brick.Turn.align(env,model,labels)
    assert ready
    start,_,births,entry = W.earlier_birth(env,model,labels)
    assert start and len(births)==2 and (entry['x'],entry['camera_right'])==(1482,1555)
    slots = {r['actor']['slot'] for r in births}
    options,last = legal_requests(env,start,labels,0)
    print('Reverse requests',[(q['x'],q['frame'],[(a['x'],a['y']) for a in q['actors']]) for q,_ in options],
          'scan end',last['x'],last['hp'],flush=True)
    reverse,forward,waiting = [],[],[]
    for _,seed in options:
        f,m = flight(env,seed,labels,0)
        reverse.append(f)
        print('Reverse',f['request']['x'],f['terminal'],f['end']['x'],f['end']['y'],f['end']['hp'],flush=True)
        if f['terminal']!='far-ground':
            continue
        wait = wait_for_fall(env,m,labels,slots)
        waiting.append(wait)
        print('Native falls',wait['passed'],list(wait['falls']),list(wait['cleared']),wait['end']['x'],flush=True)
        if not wait['passed']:
            continue
        candidates,end = legal_requests(env,m,labels,255)
        print('Re-cross requests',[(q['x'],q['frame']) for q,_ in candidates], 'scan end',end['x'],flush=True)
        for _,s in candidates:
            g,_ = flight(env,s,labels,255)
            forward.append(g)
            print('Forward',g['request']['x'],g['terminal'],g['end']['x'],g['end']['hp'],flush=True)
            if g['terminal']=='far-ground':
                break
        if forward and forward[-1]['terminal']=='far-ground':
            break
    refs = (Path(__file__),Path(W.__file__),previous,V7,Route.ROM)
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,entry=entry,births=births,
                 reverse=reverse,waiting=waiting,forward=forward,reverse_scan_end=last,
                 scope='Natural original left running A, existing pit and native actor physics on the same CPU corridor. '
                       'No actor, camera or contact state is written by these route inputs.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    out.mkdir(exist_ok=True)
    (out/'proof.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

"""Run the genuine Up scan from the careful-step landing at X1483."""

import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path

import check_prince_post_pit_careful_turn_1110 as Turn


Delayed, Pair, R, Route = Turn.Delayed, Turn.Pair, Turn.R, Turn.Route


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    earlier = out/'careful-turn.json'
    assert out.is_relative_to(R/'build') and not (out/'brick-x1483.json').exists()
    old = Pair.Second.First.Pit.Current.read(earlier)
    assert old['ROM_SHA256']==Route.PIN and old['result']['terminal']=='outside-up-scan'
    assert (old['result']['end']['x'],old['result']['end']['camera_right'])==(1483,1543)
    for p,digest in old['bindings'].items():
        assert sha256((R/p).read_bytes()).hexdigest()==digest,p
    template,_,_ = Pair.Second.First.Pit.Current.current()
    base = dict(template,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    columns = Pair.authored(base)
    env,model,labels,_ = Pair.arrival(base,columns)
    moves,q,ready = Turn.align(env,model,labels)
    assert ready and q==old['end'] and moves==old['moves']
    # The prior checker stopped before pressing Up. Adjust only its fixture
    # interval so the real source and native collision decide this coordinate.
    source = inspect.getsource(Delayed.climb_and_hop)
    assert source.count('1484<=x<=1501')==1
    oracle = vars(Delayed).copy()
    exec(compile(source.replace('1484<=x<=1501','1483<=x<=1501'),str(Path(__file__)),'exec'),oracle)
    result = oracle['climb_and_hop'](env,model,labels)
    print(result['terminal'],result['end']['x'],result['end']['hp'],
          [(e['stage'],e['state']['epoch'],e['state']['x'],e['state']['camera_right']) for e in result['events']],
          [(a['actor']['x'],a['player']['epoch']) for a in result['births']],flush=True)
    refs = (Path(__file__),earlier,Path(Turn.__file__),Path(Delayed.__file__),Delayed.NATIVE,Route.ROM)
    proof = dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,arrival=q,moves=moves,result=result,
                 scope='Original Up at X1483, accepted for measurement by the CPU observer. No changes to the authentic '
                       'scene, control, terrain, group parser, collision or standing A.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    (out/'brick-x1483.json').write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

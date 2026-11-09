"""Use genuine careful steps to gain camera room for Prince's first pit."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_first_pit_late_1110 as Late


Pit, R, N, Route, Recovery = Late.Pit, Late.R, Late.N, Late.Route, Late.Recovery


def approach(env, initial, labels, release_x):
    m = N.fork(initial)
    samples, candidates = [], []
    previous = None
    release = None
    for epoch in range(420):
        q = Late.sample(m, epoch)
        x = q['x']
        if q['engine'] != 8 or q['hp'] != 4 or q['lives'] != 2:
            break
        if x >= release_x and release is None:
            release = q
        key = x, q['action'], q['frame']
        if key != previous:
            samples.append(q)
        previous = key
        if 1083 <= x <= 1101 and Recovery.running(m,q):
            if not candidates or (x,q['frame']) != (candidates[-1][0]['x'],candidates[-1][0]['frame']):
                candidates.append((q,N.fork(m)))
        if x >= 1106:
            break
        Route.controls(env, m, labels, 65 if release is None else 1)
    return dict(release_at=release_x, release=release, samples=samples, end=q), candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'camera.json').exists()
    assert sha256(Late.EARLY.read_bytes()).hexdigest() == Late.EARLY_SHA
    template, _, _ = Pit.Current.current()
    raw = Route.ROM.read_bytes()
    assert sha256(raw).hexdigest() == Route.PIN
    base = dict(template, raw=raw)
    env, seed, labels, _ = Pit.start(base, Pit.authored(base))
    attempts = []
    for release_x in (1000, 1032, 1056):
        pre, branches = approach(env,seed,labels,release_x)
        release = pre['release']
        print('Careful',release_x,'release',None if not release else (release['x'],release['camera_right']),
              'arms',[(q['x'],q['frame'],q['camera_right']) for q,_ in branches],flush=True)
        variants=[]
        for q,m in branches[-4:]:
            z=Late.flight(env,m,labels,'Right')
            variants.append(z)
            print('Run jump',q['x'],q['frame'],z['terminal'],z['end']['x'],z['end']['y'],flush=True)
            if z['terminal']=='far-ground':
                break
        attempts.append(dict(approach=pre,flights=variants))
    report=dict(completed=True,ROM_written=False,Mesen_run=False,ROM_SHA256=Route.PIN,
                scope='Actual original B careful steps then ordinary Right, followed by supported original A. '
                      'Same authored CPU fixture as the preceding receipt; no control writes other than input.',
                attempts=attempts, bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()
                                             for p in (Path(__file__),Path(Late.__file__),Late.EARLY,Route.ROM)})
    (out/'camera.json').write_text(json.dumps(report,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()

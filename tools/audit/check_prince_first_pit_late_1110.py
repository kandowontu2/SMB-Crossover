"""Test the last source-legal first-pit inputs on the authored 1-1 map."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

import check_prince_first_pit_1110 as Pit


R, N, Route, Recovery = Pit.R, Pit.N, Pit.Route, Pit.Recovery
EARLY = R/'build/prince-first-pit-1110/proof.json'
EARLY_SHA = 'd3c1b1cd2d5a04793494b84b7d36bc7559400e4cd9c769c1ab3cb4cfe6828d6c'


def sample(m, epoch):
    q = Recovery.sample(m, epoch)
    q['support'] = Recovery.grounded(m, q)
    q['lip_tiles'] = [Route.query_support(m, x, 208) for x in (1088, 1104, 1120, 1136)]
    assert q['lip_tiles'] == [84, 0, 0, 84]
    q['scroll'] = N.get(m, 'Player_X_Scroll')
    return q


def flight(env, model, labels, policy):
    m = N.fork(model)
    begin = sample(m, 0)
    poses, clamps = [], []
    admitted = False
    fall_seen = False
    last_pose = None
    original = N.NesMPU

    class Trace(original):
        def step(self):
            if self.memory is m and self.pc == 0xaa59 and m.rawtags[1] == 129:
                x = N.get(m, 'Player_X_Position') + 256*N.get(m, 'Player_PageLoc')
                if x != (x & 0xff00) + self.a:
                    clamps.append((epoch, x, self.a, self.y, Route.Seam.xcamera(m)[1], m.ram[2][0x617]))
            return super().step()

    terminal = 'bounded'
    N.NesMPU = Trace
    try:
        for epoch in range(90):
            q = sample(m, epoch)
            key = q['action'], q['mode'], q['frame']
            if key != last_pose:
                poses.append(q)
                last_pose = key
            if q['hp'] == 0 or q['engine'] != 8 or q['lives'] != 2:
                terminal = 'death'
                break
            if q['action'] == 4:
                admitted = True
            if q['action'] in (10, 24) and q['mode'] in (2, 6):
                fall_seen = True
            if admitted and q['x'] >= Pit.RIGHT + 16 and q['y'] == 176 and q['support']:
                terminal = 'far-ground'
                break
            if admitted and q['x']+13 < Pit.LEFT and q['support'] and q['action'] != 4 and epoch >= 15:
                terminal = 'short-ground'
                break
            if admitted and q['y'] > 215 and not fall_seen:
                terminal = 'below-far-lip'
                break
            if not admitted and epoch > 28:
                terminal = 'not-admitted'
                break
            pad = 129 if not admitted else 1
            if policy == 'Up on descending reach' and admitted and q['frame'] >= 42:
                pad = 9
            Route.controls(env, m, labels, pad)
    finally:
        N.NesMPU = original
    return dict(policy=policy, begin=begin, terminal=terminal, poses=poses, clamps=clamps, end=q)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'late.json').exists()
    assert sha256(EARLY.read_bytes()).hexdigest() == EARLY_SHA
    first = Pit.Current.read(EARLY)
    assert first['ROM_SHA256'] == Route.PIN
    for name, digest in first['bindings'].items():
        assert sha256((R/name).read_bytes()).hexdigest() == digest, name
    template, _, _ = Pit.Current.current()
    base = dict(template, raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest() == Route.PIN
    env, seed, labels, _ = Pit.start(base, Pit.authored(base))
    arrivals, candidates = [], []
    previous = None
    for epoch in range(230):
        q = sample(seed, epoch)
        x = q['x']
        if x >= 1078:
            ready = Recovery.running(seed, q)
            key = x, q['frame'], q['phase'], ready
            if key != previous:
                arrivals.append(dict(q, run_ready=ready))
                if ready and x + 2 < Pit.LEFT:
                    candidates.append((q, N.fork(seed)))
            previous = key
        if x >= Pit.LEFT + 7:
            break
        assert q['engine'] == 8 and q['lives'] == 2 and q['hp'] == 4
        Route.controls(env, seed, labels, 1)
    assert arrivals and candidates and len(candidates) <= 24
    results = []
    for q, m in candidates:
        for policy in ('Right', 'Up on descending reach'):
            result = flight(env, m, labels, policy)
            results.append(result)
            print(q['x'], q['frame'], q['phase'], policy, result['terminal'], result['end']['x'],
                  result['end']['y'], [(p['frame'],p['x'],p['foot']) for p in result['poses'] if 39<=p['frame']<=44],
                  flush=True)
    receipt = dict(completed=True, ROM_written=False, Mesen_run=False, ROM_SHA256=Route.PIN,
                   earlier_SHA256=EARLY_SHA, results=results, arrivals=arrivals,
                   scope='Authentic input from the authored 1-1 CPU fixture in the earlier receipt. Branches '
                         'cover every distinct legal running request phase from X1078 through the near lip, '
                         'under the same continuous Right approach. No synthetic takeoff or native crossing.',
                   bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest()
                             for p in (EARLY,Path(__file__),Route.ROM)})
    (out/'late.json').write_text(json.dumps(receipt, separators=(',', ':'))+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()

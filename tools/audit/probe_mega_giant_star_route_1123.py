"""Bounded source-only continuation from both earned upgrades to natural Star."""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path
import sys

import probe_mega_giant_flower_route_1123 as F

H = lambda raw: sha256(raw).hexdigest()
PIN = '52d16533e5c033c72a28624c78384cb9448d3be26a0714a2857b2b6de8a87da5'


class StarRoute(F.Route):
    latest = None

    def __init__(self):
        super().__init__()
        StarRoute.latest = self
        self.to_star = False
        self.star_birth = None
        self.star_head = None
        self.star_collect = None
        self.star_effect = None
        self.star_returns = []

    def observe(self, q, m, contacts, collector):
        if not self.to_star:
            super().observe(q, m, contacts, collector)
            if self.done:
                self.to_star = True
                self.done = False
            return
        self.last = q
        self.tail.append(q)
        N = F.Base.N
        assert q['lives'] == 2 and q['status'] == 2 and not q['growth_active']
        assert N.get(m, 'GuestLegacyHurt') == 0 and q['y'] < 224 and N.get(m, 'Player_Y_HighPos') == 1
        if self.star_head is None:
            candidates = [r for r in contacts if r['tile'] == 0x57 and 1580 <= r['x'] <= 1600]
            if candidates:
                self.star_head = candidates[0]
        for i in range(6):
            if N.get(m, 'Enemy_Flag', i) and N.get(m, 'Enemy_ID', i) == 46 and N.get(m, 'PowerUpType', i) == 2:
                if self.star_birth is None:
                    self.star_birth = dict(hero=q, slot=i, state=N.get(m, 'Enemy_State', i),
                        x=N.get(m, 'Enemy_X_Position', i)+256*N.get(m, 'Enemy_PageLoc', i),
                        y=N.get(m, 'Enemy_Y_Position', i))
                    assert self.star_head and self.star_birth['x'] == 1616
        records = [r for r in collector if r['event'] == 'HandlePowerUpCollision' and r['kind'] == 2]
        if records and self.star_collect is None:
            self.star_collect = records[0]
            assert self.star_birth and self.star_collect['actor_state'] >= 6
        if self.star_collect:
            timer, music = N.get(m, 'StarInvincibleTimer'), N.get(m, 'AreaMusicQueue')
            if self.star_effect is None:
                assert timer == 35 and music == 64, ('Native real Star effect', timer, music, q)
                self.star_effect = dict(hero=q, timer=timer, music=music)
            else:
                assert timer > 0 and q['engine'] == 8
                self.star_returns.append(dict(hero=q, timer=timer, grounded=N.get(m, 'Player_State') == 0))
                if len(self.star_returns) == 25:
                    score = lambda r: int(''.join(map(str, r['score'])))
                    assert score(q) >= score(self.star_collect)+1000
                    assert q['x'] > self.star_effect['hero']['x']
                    assert all(r['grounded'] for r in self.star_returns)
                    self.done = True


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert H(Path(F.__file__).read_bytes()) == PIN
    source = inspect.getsource(F.main)
    def report(line, **kwargs):
        record = json.loads(line)
        item = record['report']
        route = StarRoute.latest
        item.update(Star_head=route.star_head, Star_birth=route.star_birth,
            Star_collection=route.star_collect, Star_effect=route.star_effect,
            Star_followup=len(route.star_returns), Star_last=route.star_returns[-1:] or None,
            Star_source_SHA256=H(Path(__file__).read_bytes()))
        record['receipt_SHA256'] = H(json.dumps(item, sort_keys=True, separators=(',', ':')).encode())
        print(json.dumps(record), flush=True)
    namespace = dict(F.__dict__, Route=StarRoute, print=report)
    exec(compile(source, '<frozen Flower kernel with Star observer>', 'exec'), namespace)
    sys.argv = [__file__, '--output', str(args.output), '--limit', '1800']
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())

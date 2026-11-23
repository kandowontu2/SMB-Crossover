"""Source-only genuine hidden 1-UP access after the naturally earned Mushroom."""
import argparse
from hashlib import sha256
import inspect
import json
from pathlib import Path
import sys

import probe_mega_giant_flower_route_1123 as F

H = lambda raw: sha256(raw).hexdigest()
PIN = '52d16533e5c033c72a28624c78384cb9448d3be26a0714a2857b2b6de8a87da5'


class LifeRoute(F.Route):
    latest = None

    def __init__(self):
        super().__init__()
        LifeRoute.latest = self
        self.life_phase = 'approach'
        self.life_since = None
        self.life_launch = None
        self.life_birth = None
        self.life_collect = None
        self.life_credit = None
        self.life_follow = []

    def observe(self, q, m, contacts, collector):
        if self.m_returns < 25:
            return super().observe(q, m, contacts, collector)
        N = F.Base.N
        self.last = q
        self.tail.append(dict(q, vx=N.get(m, 'Player_X_Speed'), native_state=N.get(m, 'Player_State')))
        assert q['status'] == 1 and not q['growth_active'] and q['lives'] in (2, 3)
        assert N.get(m, 'GuestLegacyHurt') == 0 and q['y'] < 224 and N.get(m, 'Player_Y_HighPos') == 1
        for i in range(6):
            if N.get(m, 'Enemy_Flag', i) and N.get(m, 'Enemy_ID', i) == 46 and N.get(m, 'PowerUpType', i) == 3:
                if self.life_birth is None:
                    self.life_birth = dict(hero=q, slot=i, state=N.get(m, 'Enemy_State', i),
                        x=N.get(m, 'Enemy_X_Position', i)+256*N.get(m, 'Enemy_PageLoc', i),
                        y=N.get(m, 'Enemy_Y_Position', i))
                    assert self.life_launch and self.life_birth['x'] == 1024
        records = [r for r in collector if r['event'] == 'HandlePowerUpCollision' and r['kind'] == 3]
        if records and self.life_collect is None:
            self.life_collect = records[0]
            assert self.life_birth and self.life_collect['actor_state'] >= 6 and self.life_collect['lives'] == 2
        if q['lives'] == 3:
            assert self.life_collect
            if self.life_credit is None:
                self.life_credit = q
            elif N.get(m, 'Player_State') == 0 and q['y'] == 176:
                self.life_follow.append(q)
                if len(self.life_follow) == 25:
                    assert q['x'] > self.life_credit['x']
                    self.done = True

    def drive(self, q, m):
        if self.m_returns < 25 or (q['x'] < 980 and self.life_phase == 'approach'):
            return super().drive(q, m)
        N = F.Base.N
        if self.life_credit:
            return 1
        if self.life_phase == 'approach':
            self.life_phase = 'align'
            self.life_since = q['active']
        assert q['active']-self.life_since < 260, ('Finite true hidden-block alignment/jump', q)
        if self.life_phase == 'align':
            vx = N.get(m, 'Player_X_Speed')
            vx = vx-256 if vx >= 128 else vx
            if q['y'] != 176 or N.get(m, 'Player_State') != 0:
                # The ordinary X912 pipe jump is still descending at X981.
                # Brake in that real arc, then qualify native floor support.
                return 2 if vx > 0 else 1 if vx < 0 else 0
            assert q['y'] == 176 and N.get(m, 'Player_State') == 0, ('Real supported launch approach', q)
            if abs(vx) <= 2 and 1015 <= q['x'] <= 1017:
                self.life_phase = 'jump'
                self.life_launch = dict(q, vx=vx)
                return 128
            predicted = q['x'] + vx*abs(vx)/64
            if predicted > 1017:
                return 2
            if predicted < 1015:
                return 1
            return 2 if vx > 0 else 1 if vx < 0 else 0
        return 128 if not self.life_birth and q['active']-self.life_launch['active'] < 24 else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    assert H(Path(F.__file__).read_bytes()) == PIN
    source = inspect.getsource(F.main)
    marker = "    captured = []"
    injection = """    source = once(source,
        \"assert (get('SelectedCharacter'), get('MarioVariant'), get('NumberofLives')) == (0, 9, 2), state()\",
        \"assert (get('SelectedCharacter'), get('MarioVariant')) == (0, 9) and get('NumberofLives') in (2, 3), state()\")
    source = once(source, 'if len(events) < 40:', 'if len(events) < 400:')
"""
    source = F.once(source, marker, injection+marker)
    def report(line, **kwargs):
        record = json.loads(line)
        item = record['report']
        route = LifeRoute.latest
        item.update(Life_phase=route.life_phase, Life_launch=route.life_launch, Life_birth=route.life_birth,
            Life_collection=route.life_collect, Life_credit=route.life_credit,
            Life_followup=len(route.life_follow), Life_source_SHA256=H(Path(__file__).read_bytes()))
        record['receipt_SHA256'] = H(json.dumps(item, sort_keys=True, separators=(',', ':')).encode())
        print(json.dumps(record), flush=True)
    namespace = dict(F.__dict__, Route=LifeRoute, print=report)
    exec(compile(source, '<frozen Flower opening with hidden life observer>', 'exec'), namespace)
    sys.argv = [__file__, '--output', str(args.output), '--limit', '1400']
    return namespace['main']()


if __name__ == '__main__':
    raise SystemExit(main())

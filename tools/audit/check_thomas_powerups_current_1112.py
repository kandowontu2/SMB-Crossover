"""Current Thomas native item callbacks and controller-only 1-1 route."""

import argparse
from collections import Counter, deque
from hashlib import sha256
import json

import audit_current_roster_powerups_1110 as C
import check_roster_powerup_continuation_1110 as Frames


W, N = C.W, C.N
PIN = '8fc57b8b4268a47f8a906af8b5813834bbf76ca7376d1d12767d510708da9582'
LIFTS = ((400, 176), (560, 160), (688, 144), (864, 144))
KERNEL = 'ef6f43c25359401ba280bb5480b93a5a5a663683aa04137ce2de67c062ad04cc'


def world(model, low, high, slot=0):
    return N.get(model, low, slot)+256*N.get(model, high, slot)


def actor(model, slot):
    return dict(slot=slot, flag=N.get(model, 'Enemy_Flag', slot), id=N.get(model, 'Enemy_ID', slot),
                kind=N.get(model, 'PowerUpType', slot), state=N.get(model, 'Enemy_State', slot),
                x=world(model, 'Enemy_X_Position', 'Enemy_PageLoc', slot),
                y=N.get(model, 'Enemy_Y_Position', slot))


def player(model):
    return dict(x=world(model, 'Player_X_Position', 'Player_PageLoc'), y=N.get(model, 'Player_Y_Position'),
                state=N.get(model, 'Player_State'), vx=N.get(model, 'Player_X_Speed'),
                status=N.get(model, 'PlayerStatus'), engine=N.get(model, 'GameEngineSubroutine'),
                active=N.get(model, 'GuestPowerupActive'), age=N.get(model, 'GuestPowerupAge'),
                lives=N.get(model, 'NumberofLives'), timer=N.get(model, 'TimerControl'))


def cold(raw, *, expected=PIN, kernel=None, cookie=None):
    assert sha256(raw).hexdigest() == expected
    b = W.Symbols.bundle()
    b['raw'] = raw
    opening, model = C.cold(b, dict(name='THOMAS', slot=10, cycle=2, raw=10))
    at = 16+1048576+426*1024
    if kernel is None:
        assert sha256(raw[at:at+6144]).hexdigest() == KERNEL
    else:
        assert raw[at:at+6144] == kernel
    assert bytes(model.ram[3][:6144]) == raw[at:at+6144]
    cookie = cookie or bytes.fromhex('a70a4002a5d85501bf9e69d0625ddc43')
    assert all(bytes(model.ram[i][0x1fe0:0x1ff0]) == cookie for i in (2, 3))
    return opening, model


def pickups(seed):
    cases = []
    for kind, tier in ((0, 0), (1, 1), (2, 0), (2, 2), (3, 0), (3, 2)):
        model = C.L.clone(seed)
        N.put(model, PlayerStatus=tier)
        row = Frames.directed(model, kind, 70)
        first, last = row['collected'], row['states'][-1]
        assert row['actor_erased'] and row['hosted_recovered'], row
        assert row['calls']['HandlePowerUpCollision'] == row['calls']['MarioSourcePowerupCollision'] == 1, row
        assert first['Square2SoundQueue'] == 32
        if kind < 2:
            assert row['calls']['GuestPowerupUpdate'] == 60 and last['PlayerStatus'] == tier+1, row
            assert last['GameEngineSubroutine'] == 8 and last['TimerControl'] == 0
        else:
            assert last['PlayerStatus'] == tier and not first['GuestPowerupActive']
        if kind == 2:
            assert first['StarInvincibleTimer'] == 35 and first['AreaMusicQueue'] == 64, row
        if kind == 3:
            assert first['floaty'] == 11 and last['NumberofLives'] == first['NumberofLives'], row
            # The generic directed probe stops after three updates for an
            # immediate item. Run this actor's real deferred floaty handler.
            probe = C.L.clone(model)
            N.put(probe, NmiDisable=255, ObjectOffset=5)
            for name, value in dict(Enemy_Flag=1, Enemy_ID=46, Enemy_State=128, PowerUpType=3).items():
                probe[W.address(probe.bundle, name)+5] = value
            N.invoke(probe, 'HandlePowerUpCollision', x=5)
            for tick in range(6):
                N.invoke(probe, 'FloateyNumbersCore', x=5)
                assert N.get(probe, 'NumberofLives') == first['NumberofLives']+int(tick == 5)
            last['NumberofLives'] = N.get(probe, 'NumberofLives')
        cases.append(dict(kind=kind, tier=tier, status=last['PlayerStatus'], freeze_ticks=row['calls'].get('GuestPowerupUpdate', 0),
                          star=first['StarInvincibleTimer'], music=first['AreaMusicQueue'],
                          lives=last['NumberofLives'], floaty=first['floaty'], erased=row['actor_erased']))
    return cases


class Route:
    def __init__(self, flower_lift=False):
        self.phase = 'approach'
        self.flower_lift = flower_lift
        self.epoch = 0
        self.phase_epoch = 0
        self.lift = 0
        self.previous_y = None
        self.pickups = []
        self.ticks = Counter()
        self.events = []
        self.trace = deque(maxlen=16)
        self.flower_lift_y = None

    def phase_to(self, phase):
        self.phase, self.phase_epoch = phase, self.epoch

    def pad(self, s, actors):
        x, y = s['x'], s['y']
        age, ground = self.epoch-self.phase_epoch, s['state'] == 0
        helper = next((a for a in actors if a['id'] == 37 and a['x'] == 1200), None)
        boarded_helper = helper and helper['contact'] == helper['slot']
        previous_helper_y = self.flower_lift_y
        self.flower_lift_y = helper['y'] if helper else None
        if s['active']:
            return 0
        if len(self.pickups) >= 2:
            return 2
        if self.phase == 'approach':
            if x >= 325:
                self.phase_to('first-jump')
                return 73
            return 65
        if self.phase == 'first-jump':
            if age >= 8:
                self.phase_to('park')
                return 65
            return 73
        if self.phase == 'park':
            if not self.pickups:
                return 65 if x < 400 else 0
            self.phase_to('retry')
        if self.phase == 'flower-approach':
            if x >= 1238 and ground:
                self.phase_to('flower-wait')
                return 8
            if self.hostile(x, y, actors):
                return 4+(64 if self.epoch % 24 < 6 else 0)
            if ground and x >= 1000 and self.epoch % 8 < 3 and (
                    s['obstacle'] or not s['support']):
                return 9
            return 1
        if self.phase == 'flower-wait':
            if len(self.pickups) >= 2:
                return 1
            flower = next((a for a in actors if a['id'] == 46 and a['kind'] == 1), None)
            if flower and self.flower_lift:
                self.phase_to('flower-lift-retreat')
                return 2
            if flower and flower['state'] & 128 and ground:
                return (1 if x < flower['x']-8 else 2 if x > flower['x']-2 else 0)+8
            if not flower and ground and age > 30 and age % 24 < 4:
                return 8
            return 0
        if self.phase == 'flower-lift-retreat':
            if x > 1176 or not ground:
                return 2
            self.phase_to('flower-lift-wait')
            return 0
        if self.phase == 'flower-lift-wait':
            if helper and helper['y'] >= 188 and (previous_helper_y is None or helper['y'] >= previous_helper_y):
                self.phase_to('flower-lift-runup')
            return 0
        if self.phase == 'flower-lift-runup':
            if age >= 6:
                self.phase_to('flower-lift-hop')
            return 1
        if self.phase == 'flower-lift-hop':
            if x >= 1214 or age >= 64:
                if boarded_helper:
                    self.phase_to('flower-lift-ride')
                    self.events.append(dict(flower_board=self.epoch, helper=helper, player=s))
                elif ground or age >= 64:
                    self.phase_to('flower-lift-retreat')
                return 0
            return 9 if age < 3 else 1
        if self.phase == 'flower-lift-ride':
            if boarded_helper and y <= 96:
                self.phase_to('flower-lift-depart')
                self.events.append(dict(flower_depart=self.epoch, helper=helper, player=s))
            elif ground and not boarded_helper:
                self.phase_to('flower-lift-retreat')
            return 0
        if self.phase == 'flower-lift-depart':
            if len(self.pickups) < 2 and ground and x > 1270:
                self.phase_to('flower-lift-retreat')
                return 2
            return 1

        lift, top = LIFTS[self.lift]
        a = next((q for q in actors if q['id'] == 37 and q['x'] == lift and q['flag'] == 1), None)
        ly = a['y'] if a else None
        boarded = a and a['contact'] == a['slot']
        previous, self.previous_y = self.previous_y, ly
        if x >= lift+96:
            self.events.append(dict(pipe=lift+48, epoch=self.epoch, x=x, status=s['status']))
            self.lift += 1
            self.previous_y = None
            self.phase_to('flower-approach' if self.lift == len(LIFTS) else 'approach-lift')
            return 1
        if self.hostile(x, y, actors):
            if not boarded and self.phase in ('runup', 'hop'):
                self.phase_to('retry')
            return 4+(64 if self.epoch % 24 < 6 else 0)
        if self.phase == 'retry':
            if boarded and x >= lift+14:
                self.phase_to('ride')
            elif ground and x > lift-24:
                return 2
            elif ground:
                self.phase_to('wait')
            return 0
        if self.phase == 'approach-lift':
            if x >= lift-24:
                self.phase_to('wait')
                return 0
            return 1
        if self.phase == 'wait':
            if ly is not None and ly >= 188 and (previous is None or ly >= previous):
                self.phase_to('runup')
            return 0
        if self.phase == 'runup':
            if age >= 6:
                self.phase_to('hop')
            return 1
        if self.phase == 'hop':
            if x >= lift+14 or age >= 64:
                if boarded:
                    self.phase_to('ride')
                elif ground or age >= 64:
                    self.phase_to('retry')
                return 0
            return 9 if age < 3 else 1
        if self.phase == 'ride':
            if boarded and y+32 <= top-16:
                self.phase_to('cross')
            elif ground and not boarded:
                self.phase_to('retry')
            return 0
        assert self.phase == 'cross', self.phase
        return 9 if 6 <= age < 9 else 1

    @staticmethod
    def hostile(x, y, actors):
        return any(0 < a['flag'] < 128 and a['id'] < 21 and not a['state'] & 32
                   and 0 < a['x']-x <= 38 and abs(a['y']-y) <= 24 for a in actors)


def route(seed, limit, *, flower_lift=False):
    model = C.L.clone(seed)
    control = Route(flower_lift)
    points = {(W.address(model.bundle, name), ((W.location(model.bundle, name)-16)//8192)|128): name
              for name in ('HandlePowerUpCollision', 'GuestPowerupUpdate', 'SetupPowerUp', 'PlayerHeadCollision')}
    pending = None
    block = W.address(model.bundle, 'Block_Buffer_1')

    def tile(x, y):
        if not 32 <= y < 240:
            return 0
        return model[block+((x//256) % 2)*208+((y-32)//16)*16+(x%256)//16]

    def solid(x, y):
        return tile(x, y) not in (0, 0x23, 0x26, 0xc2)

    def observe(m, c):
        nonlocal pending
        if pending and (c.pc, c.sp) == pending[0]:
            a = pending[1]
            result = player(m)
            assert not actor(m, a['slot'])['flag'] and result['active'] == 1
            assert N.get(m, 'FloateyNum_Control', a['slot']) == 6
            assert N.get(m, 'Square2SoundQueue') == 32
            control.pickups.append(dict(item=a, player=result, epoch=control.epoch))
            print(json.dumps(dict(event='earned', **control.pickups[-1])), flush=True)
            pending = None
        if c.pc < 0x8000:
            return
        name = points.get((c.pc, m.rawtags[(c.pc-0x8000)//8192]))
        if name == 'HandlePowerUpCollision':
            a = actor(m, c.x)
            assert a['flag'] and a['id'] == 46 and a['state'] & 128 and a['kind'] == len(control.pickups), a
            ret = m[0x101+c.sp]+256*m[0x102+c.sp]+1, c.sp+2
            pending = ret, a
        elif name == 'GuestPowerupUpdate':
            control.ticks[len(control.pickups)] += 1
        elif name == 'SetupPowerUp':
            control.events.append(dict(setup=control.epoch, player=player(m)))
        elif name == 'PlayerHeadCollision' and control.phase.startswith('flower') and len(control.events) < 28:
            control.events.append(dict(head=control.epoch, player=player(m), tile=c.a, y=c.y))

    for epoch in range(limit):
        control.epoch = epoch
        now = player(model)
        x, y = now['x'], now['y']
        now.update(obstacle=solid(x+20, y+31), support=solid(x+12, y+32))
        actors = [dict(actor(model, slot), contact=N.get(model, 'PlatformCollisionFlag', slot))
                  for slot in range(6) if N.get(model, 'Enemy_Flag', slot)]
        if epoch % 128 == 0:
            print(json.dumps(dict(event='checkpoint', epoch=epoch, phase=control.phase,
                                  lift=control.lift, player=now, actors=actors)), flush=True)
        if 1220 <= x < 1245 and not any('flower_terrain' in row for row in control.events):
            control.events.append(dict(flower_terrain={xx: {yy: tile(xx, yy) for yy in range(96, 209, 16)}
                                        for xx in range(1216, 1281, 16)}))
        control.trace.append(dict(epoch=epoch, phase=control.phase, **now))
        if now['lives'] != 2 or now['engine'] == 11:
            break
        if len(control.pickups) == 2 and not now['active'] and now['status'] == 2 \
                and abs(now['x']-control.pickups[-1]['player']['x']) >= 16:
            assert dict(control.ticks) == {1: 60, 2: 60}, control.ticks
            return dict(passed=True, final=now, collected=control.pickups, progression=dict(control.ticks), events=control.events)
        model.controller_pad = control.pad(now, actors)
        Frames.frame(model, observe)
    return dict(passed=False, collected=control.pickups, progression=dict(control.ticks),
                events=control.events, trace=list(control.trace))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', choices=('pickups', 'route'), default='pickups')
    parser.add_argument('--limit', type=int, default=3300)
    args = parser.parse_args()
    opening, seed = cold(C.ROM.read_bytes())
    print(json.dumps(dict(event='cold', **opening)), flush=True)
    result = pickups(seed) if args.part == 'pickups' else route(seed, args.limit)
    print(json.dumps(dict(ROM_SHA256=PIN, CPU_only=True, output_files=0, evidence=result)), flush=True)
    if isinstance(result, dict):
        assert result['passed']


if __name__ == '__main__':
    main()

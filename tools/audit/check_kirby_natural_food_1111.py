"""Run Kirby's authored World 1-1 food blocks from the reset vector."""

import argparse
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path

import check_ff_white_mushroom_current_1110 as Host
import prepare_kirby_contacts_current_1108_v1 as Authority


N = Host.N
PIN = '409d5a2e3b8ca1fdf6fa4512cac399310c44c1837b88b9f7d2a1e5bde858d280'
PRINCE_IDLE_PIN = 'ac2624467d4c3abc8988088ab22a4d2a0f52059e2e2d23373940fc9d17006066'
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
RIGHT, LEFT, DOWN, UP, START, B, A = 1, 2, 4, 8, 16, 64, 128
MENU_STEPS = (LEFT, RIGHT, RIGHT, RIGHT, DOWN, LEFT, LEFT, LEFT, LEFT, RIGHT,
              RIGHT, RIGHT, 0, LEFT, LEFT, LEFT, LEFT, RIGHT, RIGHT, RIGHT, UP,
              LEFT, LEFT, LEFT, LEFT, RIGHT, RIGHT, RIGHT, UP, LEFT, LEFT, LEFT)


class BootBus(Host.ControllerBus):
    def __getitem__(self, address):
        if address == 0x2002:
            self.toggle = 0
            return 128
        return super().__getitem__(address)


class Replay:
    def __init__(self, raw):
        self.rom_sha256 = sha256(raw).hexdigest()
        assert self.rom_sha256 in (PIN, PRINCE_IDLE_PIN)
        assert Authority.sha(Authority.AUTHORITY) == Authority.AUTHORITY_ROM
        assert Authority.sha(Authority.AUTHORITY.with_suffix('.dbg')) == Authority.AUTHORITY_DBG
        bundle = Authority.scoped_load(Authority.AUTHORITY)
        self.points = {}
        for name in ('MushFlowerBlock', 'SetupPowerUp', 'UnionPwrUpCore', 'PowerUpObjHandler',
                     'NrPickupCollision', 'HandlePowerUpCollision', 'KbPickupDispatch', 'KbHealPickup',
                     'KbInjuryStart', 'KbWeapons::Capture', 'KillPlayer'):
            offset = Host.location(bundle, name)
            assert raw[offset:offset+4] == bundle['raw'][offset:offset+4], name
            self.points[(128 | ((offset-16)//8192), Host.address(bundle, name))] = name
        bundle['raw'] = raw
        self.mem = BootBus(bundle)
        self.cpu = N.NesMPU(memory=self.mem, pc=None)
        self.idle = (Host.address(bundle, 'IdleLoop'), 253)
        self.tick = 0
        self.events = []
        self.counts = Counter()
        self.food_actors = {}
        self.pending = None
        self.trail = deque(maxlen=18)
        self.run_until(self.idle, 'reset')

    def run_until(self, stop, phase, observe=False):
        for _ in range(500_000):
            if (self.cpu.pc, self.cpu.sp) == stop:
                return
            if observe:
                self.watch()
            assert self.mem[self.cpu.pc], ('unexpected BRK', phase, hex(self.cpu.pc), self.mem.rawtags)
            self.cpu.step()
        raise AssertionError(('CPU instruction bound', phase, hex(self.cpu.pc), self.cpu.sp))

    def get(self, name, slot=0):
        return N.get(self.mem, name, slot)

    def world_x(self, prefix, slot=0):
        return self.get(prefix+'_PageLoc', slot)*256 + self.get(prefix+'_X_Position', slot)

    def state(self):
        return dict(tick=self.tick, x=self.world_x('Player'), y=self.get('Player_Y_Position'),
                    state=self.get('Player_State'), health=self.get('KbHealth'), hurt=self.get('KbHurt'),
                    food=self.get('KbFoodKind'), heal=self.get('KbHeal'), copy=self.get('KbCopy'),
                    lives=self.get('NumberofLives'), facing=self.get('PlayerFacingDir'),
                    engine=self.get('GameEngineSubroutine'))

    def actor(self, slot):
        return dict(slot=slot, id=self.get('Enemy_ID', slot), flag=self.get('Enemy_Flag', slot),
                    state=self.get('Enemy_State', slot), type=self.get('PowerUpType', slot),
                    x=self.world_x('Enemy', slot), y=self.get('Enemy_Y_Position', slot))

    def actors(self, kind):
        return [self.actor(i) for i in range(6) if self.get('Enemy_Flag', i) == 1
                and self.get('Enemy_ID', i) == kind and not (kind == 6 and self.get('Enemy_State', i) & 32)]

    def watch(self):
        c, m = self.cpu, self.mem
        if self.pending and (c.pc, c.sp) == self.pending[0]:
            slot = self.pending[1]
            self.events.append(dict(event='pickup_return', player=self.state(), actor=self.actor(slot),
                                    score=self.get('FloateyNum_Control', slot),
                                    sound=self.get('Square2SoundQueue')))
            self.pending = None
        if c.pc < 0x8000:
            return
        name = self.points.get((m.rawtags[(c.pc-0x8000)//8192], c.pc))
        if name is None:
            return
        self.counts[name] += 1
        if name in ('MushFlowerBlock', 'SetupPowerUp', 'UnionPwrUpCore', 'KbInjuryStart'):
            event = dict(event=name, player=self.state(), slot=c.x)
            if name in ('UnionPwrUpCore', 'KbInjuryStart'):
                event['actor'] = self.actor(c.x)
            self.events.append(event)
        if name == 'HandlePowerUpCollision':
            ret = (m[0x101+c.sp] + 256*m[0x102+c.sp] + 1, c.sp+2)
            assert self.pending is None
            self.pending = ret, c.x
            self.events.append(dict(event='pickup_contact', player=self.state(), actor=self.actor(c.x)))
        if name == 'KbHealPickup':
            self.events.append(dict(event=name, player=self.state(), actor=self.actor(c.x), type=c.a))
        if name == 'KillPlayer':
            raise AssertionError(('native death', self.state(), list(self.trail)))

    def frame(self, pad=0, observe=False):
        self.mem.controller_pad = pad
        Host.clear_logs(self.mem)
        self.cpu.nmi()
        self.run_until(self.idle, 'NMI')
        assert self.get('NmiDisable') == 255
        self.cpu.step()
        self.run_until(self.idle, 'Main', observe)
        assert self.get('NmiDisable') == 0 and not self.mem.blocked
        self.tick += 1
        if observe:
            assert self.get('CheatStartLevel') == self.get('CheatInvincible') == 0
            assert self.get('NumberofLives') == 2 and self.get('GameEngineSubroutine') == 8
            self.trail.append(dict(pad=pad, **self.state()))
            for actor in self.actors(46):
                seen = self.food_actors.setdefault(actor['type'], {})
                seen.setdefault('emerging', dict(tick=self.tick, actor=actor))
                if actor['state'] >= 128:
                    seen.setdefault('mature', dict(tick=self.tick, actor=actor))

    def wait(self, predicate, limit):
        for _ in range(limit):
            if predicate():
                return
            self.frame()
        raise AssertionError(('controller wait bound', self.tick, self.state(), list(self.trail)))

    def press(self, pad):
        for _ in range(2):
            self.frame(pad)
        for _ in range(8):
            self.frame()

    def start(self):
        self.wait(lambda: self.tick >= 70 and self.get('CrossoverTitleDrawn') == 1
                  and self.get('DisableScreenFlag') == 0, 250)
        self.press(START)
        self.wait(lambda: self.get('CrossoverMenuState') == 2 and self.get('DisableScreenFlag') == 0, 180)
        route = []
        for _ in range(16):
            index = self.get('CrossoverMenuIndex')
            if index == 12:
                break
            pad = MENU_STEPS[index]
            assert pad, index
            route.append(pad)
            self.press(pad)
        assert self.get('CrossoverMenuIndex') == 12
        assert (self.get('SelectedCharacter'), self.get('KbVariant'), self.get('CrossoverBehaviorVersion')) == (13,0,0)
        self.press(START)
        self.wait(lambda: (self.get('OperMode'),self.get('OperMode_Task'),self.get('GameEngineSubroutine'),
                          self.get('TimerControl')) == (1,3,8,0), 450)
        assert (self.get('WorldNumber'),self.get('LevelNumber'),self.get('AreaAddrsLOffset')) == (0,0,5)
        assert self.get('CheatStartLevel') == self.get('CheatInvincible') == 0
        assert (self.get('KbHealth'),self.get('NumberofLives'),self.get('KbFoodKind')) == (6,2,0)
        return dict(menu_pad=route, player=self.state())

    def food(self):
        phase = 'approach'
        last_jump = -100
        for step in range(500):
            s = self.state()
            x, y, ground = s['x'], s['y'], s['state'] == 0
            item = next(iter(self.actors(46)), None)
            if s['food'] == 1:
                return s
            if phase == 'approach' and x >= 332:
                phase = 'brake'
            if phase == 'approach':
                pad = RIGHT
            elif item:
                gap = item['x'] - x
                pad = int(gap > 4) | (LEFT if gap < -12 else 0) if item['state'] >= 128 else 0
                if item['state'] >= 128 and item['y'] < y-20 and ground and step-last_jump > 25:
                    pad |= A
                    last_jump = step
            else:
                gap = 334-x
                pad = int(gap > 4) | (LEFT if gap < -4 else 0)
                if abs(gap) <= 4 and ground and step-last_jump > 20:
                    last_jump = step
            if step-last_jump < 24:
                pad |= A
            self.frame(pad, True)
        raise AssertionError(('first food controller bound', self.state(), self.actors(46), self.events, list(self.trail)))

    def flower(self):
        phase = 'route'
        last_jump = -100
        birth = None
        pipe_launches = set()
        for step in range(1400):
            s = self.state()
            x, y, ground = s['x'], s['y'], s['state'] == 0
            item = next(iter(self.actors(46)), None)
            if s['food'] == 0:
                return s
            if item and birth is None:
                assert item['x'] == 1248 and item['type'] == 1, item
                birth = step
                phase = 'reveal'
            if phase == 'reveal' and step-birth >= 40:
                phase = 'pickup'
            if phase == 'route' and x >= 1228:
                phase = 'under'
            if phase == 'route' and x >= 800 and s['health'] > 4:
                phase = 'meet_goombas'
            if phase == 'meet_goombas' and s['health'] == 4:
                phase = 'route'
            if phase == 'route':
                pad = RIGHT
                for left,top in ((448,176),(608,160),(736,144),(912,144),(1104,144)):
                    if left-55 <= x < left+30:
                        if ground and left not in pipe_launches:
                            last_jump = step
                            pipe_launches.add(left)
                        if y > top-30 and step-last_jump >= 23:
                            pad |= UP
                        break
                if 445 <= x <= 480 and y > 144 and self.get('KbFloat') == 0 and not ground:
                    pad |= UP
                if self.get('KbFloat') and not (pad & UP) and y <= 144 and step-last_jump > 24:
                    pad |= B
            elif phase == 'meet_goombas':
                pad = RIGHT if x < 815 else LEFT if x > 850 else 0
                if self.get('KbFloat'):
                    pad |= B
            elif phase == 'under':
                gap = 1242-x
                pad = int(gap > 3) | (LEFT if gap < -3 else 0)
                if y <= 130 and x > 1210:
                    pad = LEFT
                if ground and y > 145 and abs(gap) <= 4 and step-last_jump > 27:
                    last_jump = step
            elif phase == 'pickup':
                assert item is not None
                if ground and x <= item['x']-37 and step-last_jump > 32:
                    last_jump = step
                if step-last_jump < 24:
                    pad = RIGHT
                elif x > item['x']-37 and y > item['y']+20:
                    pad = LEFT
                else:
                    pad = int(x < item['x']-8) | (LEFT if x > item['x']+3 else 0)
                    if y > item['y']-8 and not ground:
                        pad |= UP
            else:
                pad = 0
            if step-last_jump < 23:
                pad |= A
            self.frame(pad, True)
        raise AssertionError(('flower controller bound', phase, self.state(), self.actors(46), self.events, list(self.trail)))

    def verify_food(self):
        def events(name):
            return [e for e in self.events if e['event'] == name]

        assert self.counts['MushFlowerBlock'] == self.counts['SetupPowerUp'] == 2
        assert self.counts['KbPickupDispatch'] == self.counts['KbHealPickup'] == 2
        assert self.counts['KbWeapons::Capture'] == 0
        origins = events('UnionPwrUpCore')
        pickups = events('KbHealPickup')
        returns = events('pickup_return')
        assert len(origins) == len(pickups) == len(returns) == 2
        injuries = events('KbInjuryStart')
        assert [hit['player']['health'] for hit in injuries] == [6, 6, 5]
        assert all(hit['actor']['id'] == 6 and hit['actor']['flag'] == 1 for hit in injuries)
        for kind, (x, hp) in enumerate(((336, 5), (1248, 4))):
            origin, pickup, result = origins[kind], pickups[kind], returns[kind]
            initial = self.food_actors[kind]['emerging']
            mature = self.food_actors[kind]['mature']
            assert origin['actor']['x'] == initial['actor']['x'] == x and origin['actor']['y'] == 136
            assert origin['player']['tick'] < initial['tick'] < mature['tick'] <= pickup['player']['tick']
            assert initial['actor']['flag'] == 1 and 1 <= initial['actor']['state'] < 128
            assert mature['actor']['state'] >= 128 and mature['actor']['y'] < initial['actor']['y']
            assert pickup['type'] == pickup['actor']['type'] == kind
            assert pickup['actor']['slot'] == result['actor']['slot'] == initial['actor']['slot']
            assert pickup['player']['health'] == hp and pickup['player']['food'] == kind
            assert result['player']['health'] == 6 and result['player']['food'] == 1-kind
            assert result['player']['heal'] == 24 and result['player']['copy'] == 0
            assert result['actor']['flag'] == result['actor']['id'] == result['actor']['state'] == 0
            assert (result['score'], result['sound']) == (6, 32)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=ROM)
    args = parser.parse_args()
    replay = Replay(args.rom.read_bytes())
    start = replay.start()
    mushroom = replay.food()
    flower = replay.flower()
    replay.verify_food()
    result = dict(passed=True, ROM_SHA256=replay.rom_sha256, start=start, mushroom=mushroom, flower=flower,
                  events=replay.events, actors=replay.food_actors, counts=replay.counts, output_files=0)
    body = json.dumps(result, sort_keys=True, separators=(',', ':'))
    print(body, flush=True)
    print('receipt_SHA256='+sha256(body.encode()).hexdigest(), flush=True)


if __name__ == '__main__':
    main()

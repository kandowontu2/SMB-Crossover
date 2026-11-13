"""Ordinary-input Thomas Star and hidden-1UP approaches on the flower candidate."""

import argparse
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path
import re

import check_thomas_powerups_current_1112 as Base
import compose_thomas_flower_lift_1112 as Lift


N, W = Base.N, Base.W
PIN = '15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533'
CURRENT = '318a087735b4204c74274b4107efbc302bc15a674a7f6f9d3bed598cea90d08d'
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def authenticate(raw):
    digest = sha256(raw).hexdigest()
    if digest == PIN:
        return raw
    assert digest == CURRENT
    from deliver_karnov_bomb_1113 import previous_image
    parent = previous_image(raw)
    assert sha256(parent).hexdigest() == PIN
    assert raw[Lift.START:Lift.START+8192] == parent[Lift.START:Lift.START+8192]
    assert raw[Lift.COOKIE:Lift.COOKIE+16] == parent[Lift.COOKIE:Lift.COOKIE+16]
    return parent


def availability(raw):
    source = (W.R/'src/level_tiles.s').read_text()
    rows = []
    for name in ('L_GroundArea6', 'L_UndergroundArea1'):
        data = bytearray()
        for line in source.split(name+':', 1)[1].splitlines():
            if '.byte' in line:
                data.extend(int(value, 16) for value in re.findall(r'\$([0-9a-fA-F]{2})', line.split(';')[0]))
                if data[-1] == 253:
                    break
        data = bytes(data)
        assert raw.count(data) == 1
        items, pipes, page = [], [], 0
        for offset in range(2, len(data)-1, 2):
            a, b = data[offset:offset+2]
            page += bool(b & 128)
            row = a & 15
            if row == 13 and not b & 64 and not b & 128:
                page = b & 31
            position = dict(stream_offset=offset, bytes=data[offset:offset+2].hex(),
                            left=page*256+(a >> 4)*16, top=32+row*16)
            if row < 12 and not b & 112:
                items.append(dict(position, kind=b & 15))
            if row < 12 and b & 112 == 112:
                pipes.append(dict(position, width=32))
        rows.append(dict(area=name, ROM_offset=raw.index(data), stream_SHA256=sha256(data).hexdigest(),
                         items=items, pipes=pipes))
    assert any(item['kind'] == 3 and (item['left'], item['top']) == (1024, 128) for item in rows[0]['items'])
    assert any(item['kind'] == 6 and (item['left'], item['top']) == (1616, 144) for item in rows[0]['items'])
    assert any(item['kind'] == 8 and (item['left'], item['top']) == (1424, 32) for item in rows[1]['items'])
    return dict(scope='Source level streams authenticated byte-for-byte in candidate; positions follow native page-control decoding', areas=rows)


class Control(Base.Route):
    def __init__(self, mode):
        super().__init__(flower_lift=True)
        self.mode = mode
        self.star_phase = None
        self.gap_pending = False
        self.star = None
        self.hidden = []
        self.origin_minimum = 255
        self.oneup_jump = 0
        self.previous_air = False
        self.oneup_minimum = 255
        self.oneup_attempts = []

    def pad(self, s, actors):
        x, y, ground = s['x'], s['y'], s['state'] == 0
        if s['active']:
            return 0
        if self.mode == 'oneup' and self.phase == 'cross' and self.lift == 3 and x >= 929:
            if y > 112:
                return 0
            self.star_phase = 'oneup-pipe-launch'
            self.phase_to('oneup-pipe-launch')
        if self.mode == 'oneup' and self.phase.startswith('oneup'):
            self.origin_minimum = min(self.origin_minimum, y)
            if 1010 <= x <= 1040:
                self.oneup_minimum = min(self.oneup_minimum, y)
            if self.phase == 'oneup-pipe-launch':
                if x >= 1017:
                    self.phase_to('oneup-release')
                    return 0
                return 9 if x < 964 else 1
            if self.phase == 'oneup-release':
                if self.epoch-self.phase_epoch >= 4:
                    self.phase_to('oneup-jump')
                return 0
            if not ground and not self.previous_air:
                self.oneup_jump += 1
                self.oneup_attempts.append(dict(epoch=self.epoch, player=s))
            self.previous_air = not ground
            return 8 if ground and (self.epoch-self.phase_epoch) % 48 < 4 else 0
        if len(self.pickups) < 2:
            return super().pad(s, actors)
        if self.star_phase is None:
            self.star_phase = 'star-approach'
            self.phase_to('star-approach')
        if self.star:
            return 0
        if self.phase == 'star-wait':
            star = next((a for a in actors if a['id'] == 46 and a['kind'] == 2), None)
            if star:
                return 1 if x < star['x']-8 else 2 if x > star['x']+4 else 8 if ground else 0
            return 8 if ground else 0
        if x >= 1606 and ground:
            self.phase_to('star-wait')
            return 9
        if ground and 1360 <= x < 1424 and y == 176 and x >= 1372 and s['left_support'] and not s['support']:
            self.gap_pending = True
        if self.gap_pending and (s['state'] == 1 and s['vy'] & 128 or x >= 1378):
            self.gap_pending = False
        if self.gap_pending:
            return 9
        if ground and 1350 <= x < 1372 and y == 176:
            return 1
        if self.hostile(x, y, actors):
            return 4+(64 if self.epoch % 24 < 6 else 0)
        return 9 if ground and self.epoch % 8 < 3 and (s['obstacle'] or not s['support']) else 1


def run(seed, mode, limit):
    model = Base.C.L.clone(seed)
    control, pending = Control(mode), None
    block = W.address(model.bundle, 'Block_Buffer_1')
    points = {(W.address(model.bundle, name), ((W.location(model.bundle, name)-16)//8192)|128): name
              for name in ('HandlePowerUpCollision', 'GuestPowerupUpdate', 'SetupPowerUp',
                           'PlayerHeadCollision', 'Hidden1UpBlock', 'ShellOrBlockDefeat')}
    counts, recent = Counter(), deque(maxlen=12)
    births, head = [], []

    def tile(x, y):
        return model[block+((x//256)%2)*208+((y-32)//16)*16+(x%256)//16] if 32 <= y < 240 else 0

    def solid(x, y):
        return tile(x, y) not in (0, 0x23, 0x26, 0xc2)

    def observe(m, cpu):
        nonlocal pending
        if pending and (cpu.pc, cpu.sp) == pending['return']:
            a, now = pending['item'], Base.player(m)
            assert not Base.actor(m, a['slot'])['flag']
            if a['kind'] < 2:
                assert now['active'] == 1 and now['age'] == 0
                control.pickups.append(dict(item=a, player=now, epoch=control.epoch))
            elif a['kind'] == 2:
                assert N.get(m, 'StarInvincibleTimer') == 35 and N.get(m, 'AreaMusicQueue') == 64
                control.star = dict(item=a, player=now, epoch=control.epoch)
            else:
                assert a['kind'] == 3 and N.get(m, 'FloateyNum_Control', a['slot']) == 11
                control.star = dict(oneup=a, player=now, epoch=control.epoch)
            print(json.dumps(dict(event='native_collection', kind=a['kind'], player=now, epoch=control.epoch)), flush=True)
            pending = None
        if cpu.pc < 0x8000:
            return
        name = points.get((cpu.pc, m.rawtags[(cpu.pc-0x8000)//8192]))
        if not name:
            return
        counts[name] += 1
        if name == 'HandlePowerUpCollision':
            a = Base.actor(m, cpu.x)
            assert a['id'] == 46 and a['flag'] and a['state'] & 128
            pending = dict(item=a, return_ignored=0)
            pending['return'] = m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1, cpu.sp+2
        elif name == 'Hidden1UpBlock':
            control.hidden.append(dict(epoch=control.epoch, flag=N.get(m, 'Hidden1UpFlag'), player=Base.player(m)))
        elif name == 'PlayerHeadCollision' and (control.phase.startswith('oneup') or control.phase.startswith('star')):
            if len(head) < 12:
                head.append(dict(epoch=control.epoch, tile=cpu.a, player=Base.player(m)))

    for epoch in range(limit):
        control.epoch = epoch
        s = Base.player(model)
        x, y = s['x'], s['y']
        s.update(support=solid(x+12,y+32), left_support=solid(x+3,y+32), obstacle=solid(x+20,y+31), vy=N.get(model,'Player_Y_Speed'))
        actors = [dict(Base.actor(model, i), contact=N.get(model, 'PlatformCollisionFlag', i))
                  for i in range(6) if N.get(model, 'Enemy_Flag', i)]
        for a in actors:
            if a['id'] == 46 and not any(q['slot'] == a['slot'] and q['kind'] == a['kind'] for q in births):
                births.append(a)
        if mode == 'oneup' and 990 <= x <= 1035 and len(control.hidden) < 12:
            control.hidden.append(dict(epoch=epoch, tile=tile(1024,128), flag=N.get(model,'Hidden1UpFlag'), player=s))
        if epoch % 128 == 0:
            print(json.dumps(dict(event='route', epoch=epoch, phase=control.phase, player=s, actors=actors)), flush=True)
        recent.append(dict(epoch=epoch, phase=control.phase, **s))
        if mode == 'gap' and len(control.pickups) == 2 and x >= 1340:
            return gap_sweep(model)
        if mode == 'oneup-sweep' and control.phase == 'cross' and control.lift == 3 and x >= 908:
            return oneup_sweep(model)
        if s['lives'] < 2 or s['engine'] == 11:
            break
        if control.star and epoch-control.star['epoch'] >= 8:
            return dict(passed=True, mode=mode, native_item=control.star, final=s,
                        counts=dict(counts), births=births, hidden=control.hidden, heads=head)
        if mode == 'oneup' and control.oneup_jump >= 5 and s['state'] == 0:
            return dict(passed=False, mode=mode, reason='five-ordinary-jumps-no-1up', minimum_Y=control.origin_minimum,
                        target_minimum_Y=control.oneup_minimum, attempts=control.oneup_attempts,
                        hidden=control.hidden, heads=head, recent=list(recent), counts=dict(counts), births=births)
        model.controller_pad = control.pad(s, actors)
        Base.Frames.frame(model, observe)
    return dict(passed=False, mode=mode, recent=list(recent), counts=dict(counts), births=births,
                hidden=control.hidden, heads=head, minimum_Y=control.origin_minimum)


def gap_sweep(seed):
    rows = []
    for latency in (0, 1):
        for threshold in range(1368, 1377):
            model = Base.C.L.clone(seed)
            previous, requested, released = 1, None, False
            trace, rising, landing = [], None, None
            for epoch in range(112):
                s = Base.player(model)
                s.update(epoch=epoch, vy=N.get(model, 'Player_Y_Speed'))
                pad = 1
                if not released and s['state'] == 0 and s['x'] >= threshold:
                    requested = requested or s
                if requested and not released:
                    pad = 9
                    if s['state'] == 1 and s['vy'] & 128:
                        rising = s
                        released = True
                        pad = 1
                if rising and not landing and s['state'] == 0:
                    landing = s
                if 1366 <= s['x'] <= 1380 or s['engine'] == 11 or s['x'] >= 1420:
                    trace.append(dict(s, selected_pad=pad, applied_pad=previous if latency else pad))
                if s['engine'] == 11 or s['x'] >= 1432 and s['state'] == 0:
                    break
                model.controller_pad = previous if latency else pad
                previous = pad
                Base.Frames.frame(model)
            row = dict(threshold=threshold, delayed_updates=latency, requested=requested,
                       cleared=s['x'] >= 1432 and s['state'] == 0 and s['engine'] == 8,
                       rising=rising, landing=landing, final=s, trace=trace)
            rows.append(row)
            compact = lambda state: {name: state[name] for name in ('epoch', 'x', 'y', 'state', 'vy')} if state else None
            print(json.dumps(dict(event='gap_case', threshold=threshold, delayed_updates=latency,
                                  requested=compact(requested), rising=compact(rising), landing=compact(landing),
                                  final=compact(s), cleared=row['cleared'])), flush=True)
    return dict(passed=any(row['cleared'] for row in rows), scope='Natural earned-flower approach cloned in memory; controller-only takeoff threshold and one-update latency sweep',
                cases=len(rows), successes=[dict(threshold=row['threshold'], delayed_updates=row['delayed_updates'])
                                           for row in rows if row['cleared']])


def oneup_sweep(seed):
    rows = []
    for brake_at in (908, 912, 916, 920, 924, 928):
        model = Base.C.L.clone(seed)
        phase, settled, launched, minimum, touched = 'coast', None, None, 255, False
        samples = []
        for epoch in range(360):
            s = Base.player(model)
            s.update(epoch=epoch, vy=N.get(model, 'Player_Y_Speed'))
            if 1010 <= s['x'] <= 1040:
                minimum = min(minimum, s['y'])
            if any(N.get(model, 'Enemy_Flag', slot) and N.get(model, 'Enemy_ID', slot) == 46
                   and N.get(model, 'PowerUpType', slot) == 3 for slot in range(6)):
                touched = True
            if s['engine'] == 11 or s['x'] >= 1040:
                break
            if phase == 'coast':
                pad = int(s['x'] < brake_at)
                if s['state'] == 0 and s['y'] == 112:
                    settled, phase = s, 'edge'
                elif s['state'] == 0 and s['y'] == 176:
                    phase = 'floor'
            elif phase == 'edge':
                pad = 1
                if s['x'] >= 936:
                    launched, phase, pad = s, 'jump', 9
            elif phase == 'jump':
                pad = 9 if epoch-launched['epoch'] < 3 else 1
            else:
                pad = 1
            if 930 <= s['x'] < 947 or 1010 <= s['x'] <= 1030:
                samples.append(dict(s, pad=pad))
            model.controller_pad = pad
            Base.Frames.frame(model)
        row = dict(brake_at=brake_at, settled_on_pipe=settled, fresh_pipe_launch=launched,
                   reached_target=minimum < 255, target_minimum_Y=minimum,
                   oneup_actor_seen=touched, final=s, samples=samples)
        rows.append(row)
        print(json.dumps(dict(event='oneup_pipe_case', **{name: value for name, value in row.items() if name != 'samples'})), flush=True)
    return dict(passed=any(row['oneup_actor_seen'] for row in rows),
                scope='Six controller-only pipe-stop approaches cloned from the natural fourth-pipe crossing; original jump and actual native Main/NMI',
                cases=len(rows), pipe_landings=sum(row['settled_on_pipe'] is not None for row in rows),
                target_reached=sum(row['reached_target'] for row in rows),
                revealed=sum(row['oneup_actor_seen'] for row in rows),
                target_minimum_Y=min(row['target_minimum_Y'] for row in rows))


def star_return(seed):
    cases = []
    for tier in (0, 2):
        model = Base.C.L.clone(seed)
        N.put(model, PlayerStatus=tier)
        result = Base.Frames.directed(model, 2, 8)
        first = result['collected']
        returned = result['returned']
        assert not returned['P'] & 1
        assert first['actor_flag'] == 0 and first['floaty'] == 6
        assert first['Square2SoundQueue'] == 32 and first['StarInvincibleTimer'] == 35 and first['AreaMusicQueue'] == 64
        assert first['PlayerStatus'] == tier and not first['GuestPowerupActive']
        assert result['calls']['MarioSourcePowerupCollision'] == 1
        cases.append(dict(tier=tier, returned=returned, collected=first, calls=result['calls']))
    return dict(passed=True, scope='Explicit mature Star actors through the exact native collector after cold Thomas menu/start', cases=cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('star', 'oneup', 'gap', 'oneup-sweep', 'availability', 'star-return'), default='star')
    parser.add_argument('--rom', type=Path, default=ROM)
    parser.add_argument('--limit', type=int, default=4300)
    args = parser.parse_args()
    raw = args.rom.read_bytes()
    authenticate(raw)
    digest = sha256(raw).hexdigest()
    if args.mode == 'availability':
        print(json.dumps(dict(ROM_SHA256=digest, output_files=0, result=availability(raw))), flush=True)
        return
    kernel = raw[Lift.START:Lift.START+6144]
    _, seed = Base.cold(raw, expected=digest, kernel=kernel, cookie=raw[Lift.COOKIE:Lift.COOKIE+16])
    result = star_return(seed) if args.mode == 'star-return' else run(seed, args.mode, args.limit)
    print(json.dumps(dict(ROM_SHA256=digest, CPU_only=True, output_files=0, result=result)), flush=True)


if __name__ == '__main__':
    main()

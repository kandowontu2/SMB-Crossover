"""Ordinary-input Thomas hidden-1UP approach using the proposed eighth native lift."""

from collections import Counter
from hashlib import sha256
import json

import check_thomas_star_route_1113 as Current
import compose_thomas_oneup_lift_1113 as Fix


Base, N, W = Current.Base, Current.N, Current.W


class Control(Base.Route):
    def __init__(self):
        super().__init__(flower_lift=True)
        self.helper_y = None
        self.boarded = None
        self.jump_request = None
        self.oneup = None
        self.head_contact = False

    def pad(self, s, actors):
        if s['active']:
            return 0
        x, y, ground = s['x'], s['y'], s['state'] == 0
        helper = next((a for a in actors if a['id'] == 37 and a['x'] == 1008), None)
        previous, self.helper_y = self.helper_y, helper['y'] if helper else None
        contact = helper and helper['contact'] == helper['slot']
        if self.phase == 'cross' and self.lift == 3 and x >= 960:
            self.events.append(dict(pipe=912, epoch=self.epoch, x=x))
            self.phase_to('oneup-retreat')
        if not self.phase.startswith('oneup'):
            return super().pad(s, actors)
        age = self.epoch-self.phase_epoch
        if self.oneup:
            return 0
        if self.phase == 'oneup-retreat':
            if x > 984 or not ground:
                return 2
            self.phase_to('oneup-wait')
            return 0
        if self.phase == 'oneup-wait':
            if helper and helper['y'] >= 188 and (previous is None or helper['y'] >= previous):
                self.phase_to('oneup-runup')
            return 0
        if self.phase == 'oneup-runup':
            if age >= 6:
                self.phase_to('oneup-hop')
            return 1
        if self.phase == 'oneup-hop':
            if x >= 1022 or age >= 64:
                if contact:
                    self.boarded = dict(player=s, actor=helper, epoch=self.epoch)
                    self.phase_to('oneup-jump')
                elif ground or age >= 64:
                    self.phase_to('oneup-retreat')
                return 0
            return 9 if age < 3 else 1
        if self.phase == 'oneup-jump':
            self.jump_request = self.jump_request or dict(player=s, helper=helper, epoch=self.epoch)
            if self.head_contact:
                self.phase_to('oneup-chase')
                return 0
            assert age < 24
            return 9
        item = next((a for a in actors if a['id'] == 46 and a['kind'] == 3), None)
        if item and item['state'] & 128:
            return 1 if x < item['x']-8 else 2 if x > item['x']+4 else 0
        return 0


def run(seed, limit=4300):
    model, control = Base.C.L.clone(seed), Control()
    points = {(W.address(model.bundle, name), ((W.location(model.bundle, name)-16)//8192)|128): name
              for name in ('HandlePowerUpCollision', 'GuestPowerupUpdate', 'SetupPowerUp', 'PlayerHeadCollision', 'FloateyNumbersCore')}
    pending, counts, heads, births, awards = None, Counter(), [], [], []
    block = W.address(model.bundle, 'Block_Buffer_1')

    def solid(x, y):
        tile = model[block+((x//256)%2)*208+((y-32)//16)*16+(x%256)//16] if 32 <= y < 240 else 0
        return tile not in (0, 0x23, 0x26, 0xc2)

    def observe(m, cpu):
        nonlocal pending
        if pending and (cpu.pc, cpu.sp) == pending['return']:
            item, now = pending['item'], Base.player(m)
            assert not Base.actor(m, item['slot'])['flag'] and cpu.p & 1
            if item['kind'] == 0:
                assert now['active'] == 1
                control.pickups.append(dict(item=item, player=now))
            else:
                assert item['kind'] == 3 and control.boarded and control.jump_request
                assert any(head['tile'] == 96 for head in heads)
                assert N.get(m, 'FloateyNum_Control', item['slot']) == 11
                assert not now['active'] and now['status'] == 1
                control.oneup = dict(item=item, player=now, epoch=control.epoch)
            pending = None
        if cpu.pc < 0x8000:
            return
        name = points.get((cpu.pc, m.rawtags[(cpu.pc-0x8000)//8192]))
        if not name:
            return
        counts[name] += 1
        if name == 'HandlePowerUpCollision':
            item = Base.actor(m, cpu.x)
            pending = dict(item=item, return_pc=0)
            pending['return'] = m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1, cpu.sp+2
        elif name == 'PlayerHeadCollision' and cpu.a == 96:
            assert control.jump_request and N.get(m, 'SavedJoypadBits') & 8
            assert m.ram[2][0x69] & 4 and N.get(m, 'Player_Y_Speed') & 128
            heads.append(dict(tile=cpu.a, player=Base.player(m), epoch=control.epoch,
                              source_air=m.ram[2][0x69], source_b6=m.ram[2][0xb6]))
            control.head_contact = True

    for epoch in range(limit):
        control.epoch = epoch
        s = Base.player(model)
        x, y = s['x'], s['y']
        s.update(support=solid(x+12, y+32), obstacle=solid(x+20, y+31))
        actors = [dict(Base.actor(model, slot), contact=N.get(model, 'PlatformCollisionFlag', slot))
                  for slot in range(6) if N.get(model, 'Enemy_Flag', slot)]
        for a in actors:
            if a['id'] == 46 and a['kind'] == 3 and not births:
                births.append(dict(actor=a, player=s, epoch=epoch))
        if s['lives'] == 3 and not awards:
            assert control.oneup
            awards.append(dict(player=s, epoch=epoch))
        if awards and epoch-awards[0]['epoch'] >= 8:
            return dict(passed=True, final=s, board=control.boarded, jump=control.jump_request,
                        head=heads, births=births, collected=control.oneup, award=awards, counts=dict(counts))
        if epoch % 128 == 0:
            print(json.dumps(dict(event='oneup_route', epoch=epoch, phase=control.phase, player=s, actors=actors)), flush=True)
        assert s['lives'] >= 2 and s['engine'] != 11
        model.controller_pad = control.pad(s, actors)
        Base.Frames.frame(model, observe)
    return dict(passed=False, final=Base.player(model), phase=control.phase, board=control.boarded,
                jump=control.jump_request, heads=heads, births=births, counts=dict(counts))


def main():
    raw = Current.ROM.read_bytes()
    image, info = Fix.proposal(raw)
    _, seed = Base.cold(image, expected=sha256(image).hexdigest(), kernel=info['kernel'], cookie=info['cookie'])
    result = run(seed)
    print(json.dumps(dict(candidate_SHA256=sha256(image).hexdigest(), CPU_only=True, output_files=0, result=result)), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()

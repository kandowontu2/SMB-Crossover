"""Replay a controller-only ammo drop on Jay's exact composed ROM."""

import argparse
import json
from pathlib import Path

import check_jay_silius_camera_handoff_1111 as Motion
import check_jay_silius_enemy_ammo_1111 as Ammo
import check_jay_silius_pause_ui_1111 as Pause
import check_jay_silius_world_hit_1111 as Hit


C, H, N, W = Ammo.C, Ammo.H, Ammo.N, Ammo.W
PIN = '4df817587ea5b0aff3f278a4201976745bad4d9dd1b2a99d6cb5fd3b9c74dadc'
CAPTURE = 0xbaa8
DROP_FIELDS = Ammo.FIELDS | Ammo.HOST_FIELDS


def seed(raw):
    assert C.digest(raw) == PIN
    hot = C.offset(94,0xb27f)
    envelope = raw[hot:hot+129]
    prefix = bytes((0xa7,16,32,8))
    assert envelope.count(prefix) == 1
    cookie_at = envelope.index(prefix)
    cookie = envelope[cookie_at:cookie_at+16]
    m, trial, _ = Motion.parent(raw=raw,pin=PIN,cookie=cookie)
    roll, linked = Ammo.assemble()
    code, aliases = Hit.assemble(trial,native_defeat=CAPTURE)
    Hit.check_loaded(m,code)
    data = roll['images']['AMMODROP']
    assert m.ram[3][0x1700:0x1700+len(data)] == data
    native = {name:W.address(trial,address) for name,address in Motion.NATIVE.items()}
    return m, dict(fields=linked['ram'],motion_fields=native), aliases, roll['symbols'], cookie


def drop(m, field):
    return m.ram[2][DROP_FIELDS[field]-0xc000]


def ammo(m):
    return m.ram[2][Ammo.AMMO-0xc000]


def goomba(m):
    centers = [256*N.get(m,'Enemy_PageLoc',i)+N.get(m,'Enemy_X_Position',i)+8
               for i in range(6) if N.get(m,'Enemy_Flag',i)==1 and N.get(m,'Enemy_ID',i)==6
               and not N.get(m,'Enemy_State',i)&0x20]
    return min(centers,default=0xffff)


def frame(m, pad=0, observe=None):
    m.controller_pad = pad
    C.Game.frame(m,observe)
    assert tuple(N.get(m,k) for k in Motion.STATES) == (1,3,8)
    assert N.get(m,'NumberofLives') == 2


def approach(m, linked):
    fields = linked['motion_fields']
    initial = dict(clock=N.get(m,'FrameCounter'),position=Motion.position(m,fields))
    for update in range(300):
        x, y, camera = Motion.position(m,fields)
        if x >= 215 and goomba(m) <= 272:
            assert y == 176 and camera > 0
            return dict(update=update,player=[x,y],camera=camera,goomba=goomba(m),
                        initial=initial,clock=N.get(m,'FrameCounter'))
        frame(m,1 if x < 215 else 0)
    raise AssertionError('The first authored Goomba did not reach the firing point')


def fire(m, aliases):
    for _ in range(4):
        frame(m)
    assert ammo(m) == 63 and drop(m,'DropRandom') == 0 and drop(m,'DropStage') == 0
    before = dict(clock=N.get(m,'FrameCounter'),goomba=goomba(m))
    hits = []

    def observe(memory, cpu):
        if memory.rawtags[1] == 3 and cpu.pc == aliases['CaptureAmmoDefeat']:
            slot = cpu.x
            assert N.get(m,'Enemy_ID',slot) == 6 and N.get(m,'Enemy_Flag',slot) == 1
            assert N.get(m,'ObjectOffset') == slot
            shot_slot = m.ram[2][aliases['ShotIndex']-0xc000]
            shot = Ammo.Hit.F.slot(m,shot_slot)
            x = 256*N.get(m,'Enemy_PageLoc',slot)+N.get(m,'Enemy_X_Position',slot)+8
            hits.append(dict(slot=slot,world_x=x,projectile=[16*shot[0]+shot[1]//16,shot[7]],
                             velocity=list(shot[4:6])))

    for i in range(16):
        frame(m,64 if i == 0 else 0,observe)
        assert ammo(m) == 61
        if hits:
            assert len(hits) == 1
            slot = hits[0]['slot']
            assert N.get(m,'Enemy_State',slot)&0x20 and N.get(m,'FloateyNum_Control',slot) == 1
            return dict(before=before,from_B=i,**hits[0],roll=drop(m,'DropRandom'),
                        stage=drop(m,'DropStage'),clock=drop(m,'DropSourceClock'))
    raise AssertionError(('The controller volley missed the natural Goomba',before))


def collect(m, linked, symbols):
    assert drop(m,'DropStage') == 0x23 and drop(m,'DropTimer') == 24
    for age in range(1,70):
        frame(m)
        stage = drop(m,'DropStage')
        if age < 24:
            assert stage == 0x23 and drop(m,'DropTimer') == 24-age
        elif age == 24:
            assert stage == 0x22 and drop(m,'DropVelocityY') == 0xc0
        else:
            assert stage == 0x22
            if not drop(m,'DropVelocityY') and not drop(m,'DropFlags')&4:
                break
    else:
        raise AssertionError('The dropped ammo did not land')
    x = drop(m,'DropWorldXHi')*256+drop(m,'DropWorldXLo')
    y_q4 = drop(m,'DropWorldYHi')*256+drop(m,'DropWorldYLo')
    collected = []

    def observe(memory, cpu):
        if memory.rawtags[1] == 3 and cpu.pc == symbols['ClaimAmmo']:
            collected.append(ammo(m))

    for right in range(1,70):
        frame(m,1,observe)
        if ammo(m) != 61:
            break
    assert collected == [61] and ammo(m) == 63 and drop(m,'DropStage') == 0
    assert m.ram[2][linked['fields'][0xd1]-0xc000] == 0x18
    return dict(birth_age=24,landed_age=age,world=[x,y_q4//16],world_y_Q4=y_q4,right_updates=right,ammo=[61,63],
                player=Motion.position(m,linked['motion_fields']),sound=0x18)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,default=Ammo.NIGHTLY)
    args = parser.parse_args()
    m, linked, aliases, symbols, cookie = seed(args.rom.read_bytes())
    Hit.select_spread(m,linked,Pause)
    point = approach(m,linked)
    hit = fire(m,aliases)
    result = collect(m,linked,symbols)
    assert C.Common.headers(m) == (cookie,)*2
    print(json.dumps(dict(passed=True,ROM_SHA256=PIN,cookie=cookie.hex(),firing_point=point,
        idle_before_B=4,hit=hit,pickup=result,output_files=0),sort_keys=True),flush=True)


if __name__ == '__main__':
    main()

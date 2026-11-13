"""Audit current Jay item callbacks and a controller-only first authored pickup."""

import argparse
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import audit_current_roster_powerups_1110 as C
import check_roster_powerup_continuation_1110 as Frames


W, N = C.W, C.N
PIN = '65ee94ca9ac6e1b5ad44303d08f76ecbc175a88232c82ef8c32712edf150a643'
COOKIE = bytes.fromhex('a810200a8071b239e4a3bcb6a1eae213')
ROM = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
ROW = dict(name='JAY MCCRAY', slot=15, cycle=1, raw=16)


def state(m):
    names = ('Player_Y_Position', 'Player_State', 'PlayerStatus', 'NumberofLives', 'GameEngineSubroutine',
             'GuestPowerupActive', 'JnHealth', 'JnMaxHearts', 'JnOwnedTier', 'JnSelected', 'JnStars',
             'StarInvincibleTimer', 'Square2SoundQueue', 'AreaMusicQueue')
    row = {name: N.get(m, name) for name in names}
    row.update(x=N.get(m, 'Player_X_Position')+256*N.get(m, 'Player_PageLoc'),
               camera=N.get(m,'ScreenLeft_X_Pos')+256*N.get(m,'ScreenLeft_PageLoc'),
               donor_flags=m.ram[2][0x12],donor_control=m.ram[2][0x13],
               donor_weapon=m.ram[2][0x20], donor_ammo=m.ram[2][0xbe])
    return row


def actor(m, slot):
    return dict(slot=slot, flag=N.get(m, 'Enemy_Flag', slot), id=N.get(m, 'Enemy_ID', slot),
                kind=N.get(m, 'PowerUpType', slot), state=N.get(m, 'Enemy_State', slot),
                x=N.get(m, 'Enemy_X_Position', slot)+256*N.get(m, 'Enemy_PageLoc', slot),
                y=N.get(m, 'Enemy_Y_Position', slot), private=N.get(m, 'InvPickup', slot),
                owner=N.get(m, 'InvPickupOwner', slot))


def cold(raw, *, pin=PIN, cookie=COOKIE):
    assert sha256(raw).hexdigest() == pin
    hot = 16+94*8192+(0xb2ef & 8191)
    assert raw[hot:hot+16] == cookie
    bundle = W.Symbols.bundle()
    bundle['raw'] = raw
    opening, model = C.cold(bundle, ROW)
    assert N.get(model, 'SelectedCharacter') == 16 and model[0x730b] & 96 == 32
    assert all(bytes(model.ram[bank][0x1fe0:0x1ff0]) == cookie for bank in (2, 3))
    assert bytes(model.ram[3][0x168d:0x1690]) == bytes.fromhex('4c00b8')
    return opening, model


def directed(seed):
    rows = []
    for kind in range(4):
        model = C.L.clone(seed)
        before = state(model)
        latest = []
        parent_cpu = N.NesMPU
        class ObservedMPU(parent_cpu):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                latest[:] = [self.memory]
        with patch.object(N, 'NesMPU', ObservedMPU):
            item = Frames.directed(model, kind, 70)
        actual = latest[0]
        rows.append(dict(kind=kind, before=before, after=state(actual), actor=actor(actual, 5),
                         collected=item['collected'], returned=item['returned'], calls=item['calls'],
                         erased=item['actor_erased'], recovered=item['hosted_recovered']))
    return rows


def natural(seed, limit, *, pipe_reverse=426, pad_observer=None):
    model = C.L.clone(seed)
    counts, recent = Counter(), deque(maxlen=12)
    phase, phase_at, pending, collected = 'approach', 0, None, None
    births, heads, jumps, probes = [], [], [], []
    collect_trace = []
    pending_probe = None
    points = {(W.address(model.bundle, name), ((W.location(model.bundle, name)-16)//8192)|128): name
              for name in ('HandlePowerUpCollision', 'SetupPowerUp', 'PlayerHeadCollision', 'JnPreparePickup',
                           'JnCollectPickup', 'MarioSourcePowerupCollision', 'GuestPowerupUpdate',
                           'PlayerBGCollision', 'BillBGHeadConsumer', 'JnHeadDispatch')}

    def observe(m, cpu):
        nonlocal pending, collected, pending_probe
        if pending_probe and (cpu.pc, cpu.sp) == pending_probe['return']:
            if len(probes) < 24:
                probes.append(dict(epoch=epoch, tile=cpu.a, yspeed=N.get(m, 'Player_Y_Speed'),
                                   before=pending_probe['state'], after=state(m)))
            pending_probe = None
        if pending and (cpu.pc, cpu.sp) == pending['return']:
            collected = dict(item=pending['item'], before=pending['before'], after=state(m),
                             returned_P=cpu.p, epoch=epoch,
                             erased=N.get(m,'Enemy_Flag',pending['item']['slot']) == 0)
            pending = None
        if cpu.pc < 0x8000:
            return
        name = points.get((cpu.pc, m.rawtags[(cpu.pc-0x8000)//8192]))
        if not name:
            return
        counts[name] += 1
        if name == 'HandlePowerUpCollision':
            pending = dict(item=actor(m, cpu.x), before=state(m))
            pending['return'] = m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1, cpu.sp+2
        elif name == 'PlayerHeadCollision':
            heads.append(dict(tile=cpu.a, player=state(m), epoch=epoch))
        elif name == 'BillBGHeadConsumer' and phase == 'reveal' and len(probes) < 24:
            pending_probe = dict(state=dict(state(m), yspeed=N.get(m, 'Player_Y_Speed')))
            pending_probe['return'] = m[0x101+cpu.sp]+256*m[0x102+cpu.sp]+1, cpu.sp+2

    for epoch in range(limit):
        now = state(model)
        x, y, ground = now['x'], now['Player_Y_Position'], now['Player_State'] == 0
        actors = [actor(model, slot) for slot in range(6) if N.get(model, 'Enemy_Flag', slot)]
        item = next((a for a in actors if a['id'] == 46), None)
        if item and not births:
            births.append(dict(actor=item, player=now, epoch=epoch))
        if collected and epoch-collected['epoch'] >= 8:
            assert now['NumberofLives'] == 2 and now['GameEngineSubroutine'] == 8
            assert collected['erased'] and collected['item']['state'] == 128
            assert (collected['item']['private'],collected['item']['owner']) == (129,16)
            assert (collected['before']['JnHealth'],collected['before']['JnMaxHearts']) == (6,3)
            assert (collected['after']['JnHealth'],collected['after']['JnMaxHearts']) == (8,4)
            assert collected['after']['Square2SoundQueue'] == 32 and collected['after']['GuestPowerupActive'] == 0
            assert (now['JnHealth'],now['JnMaxHearts']) == (8,4)
            return dict(passed=True, collected=collected, final=now, births=births, heads=heads, counts=dict(counts))
        assert now['NumberofLives'] == 2 and now['GameEngineSubroutine'] != 11
        near = any(a['id'] < 21 and not a['state'] & 32 and 0 < a['x']-x < 100 and abs(a['y']-y) < 30 for a in actors)
        shot = 64 if near and epoch % 12 < 2 else 0
        if phase == 'approach' and x >= 332 and ground:
            phase, phase_at = 'park', epoch
        if phase == 'park' and epoch-phase_at >= 8:
            phase, phase_at = 'reveal', epoch
        if item and phase in ('approach', 'park', 'reveal'):
            phase, phase_at = 'pipe-approach', epoch
        if phase == 'approach':
            pad = 1+shot
        elif phase == 'park':
            pad = shot
        elif phase == 'reveal':
            pad = (128 if epoch-phase_at < 18 else 0)+shot
            if epoch-phase_at < 36:
                jumps.append(dict(epoch=epoch, pad=pad, yspeed=N.get(model, 'Player_Y_Speed'), **now))
        elif item and phase == 'pipe-approach':
            pad = 1+shot
            if x >= 400 and ground:
                phase, phase_at = 'pipe-jump', epoch
                pad |= 128
        elif item and phase == 'pipe-jump':
            pad = (1 if x < pipe_reverse else 2)+shot
            if epoch-phase_at < 12:
                pad |= 128
            if ground and y == 144:
                phase, phase_at = 'pipe-turn', epoch
                pad = 0
        elif item and phase == 'pipe-turn':
            pad = shot
            if epoch-phase_at >= 1 and not now['donor_flags']&4 and not now['donor_control']&0x38:
                if now['donor_flags']&2:
                    phase,phase_at = 'collect-jump',epoch
                    pad = 130+shot
                else:
                    phase,phase_at = 'pipe-face',epoch
                    pad = 2+shot
        elif item and phase == 'pipe-face':
            pad = 2+shot
            if epoch-phase_at >= 4 and not now['donor_flags']&4 and not now['donor_control']&0x38:
                phase,phase_at = 'pipe-runup',epoch
        elif item and phase == 'pipe-runup':
            pad = 2+shot
            if epoch-phase_at >= 1 and not now['donor_flags']&4:
                phase, phase_at = 'collect-jump', epoch
                pad |= 128
        elif item and phase == 'collect-jump':
            pad = (2 if x > item['x'] else 0)+shot
            if epoch-phase_at < 18:
                pad |= 128
        else:
            pad = 0
        if pad_observer:
            pad_observer(model,epoch,pad)
        recent.append(dict(epoch=epoch, phase=phase, pad=pad, **now))
        if phase == 'collect-jump' and len(collect_trace) < 120:
            collect_trace.append(dict(epoch=epoch,pad=pad,**now))
        if epoch % 128 == 0:
            print(json.dumps(dict(event='jay_pickup_route', epoch=epoch, phase=phase, player=now, actors=actors)), flush=True)
        model.controller_pad = pad
        Frames.frame(model, observe)
    return dict(passed=False, phase=phase, recent=list(recent), births=births, heads=heads,
                jump=jumps, probes=probes, collect_trace=collect_trace, counts=dict(counts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section', choices=('callbacks', 'route'), default='callbacks')
    parser.add_argument('--limit', type=int, default=1400)
    args = parser.parse_args()
    raw=ROM.read_bytes()
    actual=sha256(raw).hexdigest()
    cookie=COOKIE
    if actual != PIN:
        import compose_jay_head_bridge_1113 as Bridge
        assert actual in (Bridge.PARENT_PIN,Bridge.CANDIDATE_PIN)
        if actual == Bridge.CANDIDATE_PIN:
            cookie=Bridge.NEW_COOKIE
    opening, seed = cold(raw,pin=actual,cookie=cookie)
    result = directed(seed) if args.section == 'callbacks' else natural(seed, args.limit)
    print(json.dumps(dict(ROM_SHA256=actual, cookie=cookie.hex(), opening=opening,
                          CPU_only=True, output_files=0, result=result)), flush=True)
    if args.section == 'route':
        assert result['passed']


if __name__ == '__main__':
    main()

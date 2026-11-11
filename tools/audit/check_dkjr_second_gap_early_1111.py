"""Check original DK Jr. jumps on the second gap at the recorded arrival phase."""

import argparse
from collections import deque
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_late_terrain_1110 as Late
import check_dkjr_second_gap_probe_1110 as Gap


B, N = Gap.B, Gap.N
PINS = (
    'b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576',
    '852712c9a2afce71c45f9f2c970e1f5c7969c58d878cfa0a250d2bdb7ba93383',
)
BIRTH, ARRIVAL, OLD_TAKEOFF = 4481,4747,4958
CAMERA = 1285


def oscillator(seed,age,phase):
    m,idle = Late.entry(seed,Gap.TAKEOFF,176)
    Gap.seed_actor(m,Gap.ACTOR_LEFT)
    N.put(m,ObjectOffset=Gap.SLOT,FrameCounter=phase)
    m[N.address(m.bundle,'PlatformCollisionFlag')+Gap.SLOT] = 255
    for tick in range(age-1):
        N.invoke(m,'XMovingPlatform',x=Gap.SLOT)
        N.put(m,FrameCounter=(phase+tick+1)&255)
    N.put(m,ObjectOffset=0)
    m.ram[2][Late.Second.S.SEEN] = 9
    # Commit translated ingress by an ordinary neutral update. The actor
    # takes its next stock step under the real gameplay dispatcher.
    Late.Second.update(m,idle,0)
    p = Gap.Gap.player(m,0)
    assert (p['x'],p['y'],p['source'],p['state'])==(Gap.TAKEOFF,176,1,0),p
    return m,idle


def replay(seed,idle):
    m = Late.slim_fork(seed)
    planes = deque(maxlen=3)
    contacts, carries = [],[]
    pending = False
    bank = None

    def stock():
        return dict(left=B.world(m,'Enemy_X_Position','Enemy_PageLoc',Gap.SLOT),
                    direction=N.get(m,'Enemy_MovingDir',Gap.SLOT),
                    primary_counter=N.get(m,'Enemy_Y_Speed',Gap.SLOT),
                    secondary_counter=N.get(m,'Enemy_X_Speed',Gap.SLOT),
                    top=N.get(m,'Enemy_Y_Position',Gap.SLOT),box=N.get(m,'Enemy_BoundBoxCtrl',Gap.SLOT))

    def observe(c):
        nonlocal pending
        if c.pc not in (0xac29,0xa966,0xb5c8,0xb5d9,0xb5fd,0xb60a,0xb61c):
            return
        bank_id = B.V.Q.tags(c)
        if (bank_id,c.pc)==(199,0xac29) and c.x==Gap.SLOT:
            carries.append((tick,B.player(m),N.get(m,'Player_Y_Position')))
        if bank_id!=3:
            return
        if c.pc==0xb5c8 and m[0xc8f0]==Gap.SLOT:
            pending = (m[0xc8dd],stock())
        elif c.pc in (0xb5d9,0xb5fd,0xb60a):
            pending = False
        elif c.pc==0xb61c and pending:
            count,lift = pending
            assert m[0xc8dd]==count+4 and m[0xc8e5]==m[0xc8e7]==Gap.ACTOR_TOP
            planes.append((tick,B.player(m),lift['left']))
            pending = False
        elif c.pc==0xa966 and Gap.LEFT<=B.player(m)<Gap.RIGHT:
            contacts.append(dict(tick=tick,x=B.player(m),y=m.ram[2][0x210],planes=list(planes),actor=stock()))

    actor = stock()
    first = Gap.Gap.player(m,0)
    for tick in range(170):
        p = Gap.Gap.player(m,tick)
        x,y = p['x'],p['y']
        if p['source']==5 or p['lives']!=2 or p['engine']!=8:
            outcome = 'defeat'
            break
        if bank is None and x>=1412 and (y,p['source'],p['state'])==(176,1,0):
            bank = p
        if x>=Gap.RIGHT and bank is not None and (y,p['source'],p['state'])==(176,1,0):
            outcome = 'far-supported'
            break
        Late.Second.update(m,idle,129 if tick<8 else 1,observe)
    else:
        outcome = 'bound'
    return dict(outcome=outcome,first=first,actor=actor,bank=bank,terminal=p,lands=contacts,carries=carries)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=Gap.Gap.NIGHTLY)
    raw = parser.parse_args().rom.read_bytes()
    pin = sha256(raw).hexdigest()
    assert pin in PINS
    base = Gap.Gap.terrain(raw,CAMERA)
    assert tuple(N.address(base.bundle,name) for name in ('Enemy_X_Speed','Enemy_Y_Speed',
            'Enemy_MovingDir','FrameCounter'))==(0x47,0x8f,0x53f,0x0e)
    assert Gap.tiles(base)==[0x54,0,0,0,0x54]
    early = ARRIVAL-BIRTH
    cases = (*((early,phase) for phase in range(4)),(early+1,0),(early+2,0),(OLD_TAKEOFF-BIRTH,0))
    for age,phase in cases:
        seed,idle = oscillator(base,age,phase)
        result = replay(seed,idle)
        print(json.dumps(dict(image_SHA256=pin,stock_age=age,frame_phase=phase,**result),
                         separators=(',',':')),flush=True)
        if age in (early,OLD_TAKEOFF-BIRTH):
            assert result['outcome']=='far-supported' and not result['carries'],result
            assert (result['terminal']['x'],result['terminal']['y'],result['terminal']['lives'])==(1424,176,2)
            assert result['bank']['x']==1412 and result['lands'][0]['x']==1393,result
            first_land = result['lands'][0]
            assert first_land['planes'][-1][:2]==(first_land['tick'],first_land['x'])


if __name__=='__main__':
    main()

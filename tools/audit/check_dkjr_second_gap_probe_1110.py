"""Probe the authored second gap with the original DK Jr. jump and stock ID 28."""
from collections import deque
from hashlib import sha256
import json

import check_dkjr_four_pipe_funded_1110 as Four
import check_dkjr_gap_cap_probe_1110 as Gap
from check_mini_funded_actor_1108_v3 import slim_fork


B, N = Gap.B, Gap.N
LEFT, RIGHT, CAM, SLOT = 1376, 1424, 1248, 5
ACTOR_LEFT, ACTOR_TOP, TAKEOFF = 1408, 208, 1366


def tiles(m):
    return [m[0x300+((x>>8)&1)*208+11*16+((x>>4)&15)]
            for x in range(LEFT-16,RIGHT+16,16)]


def seed_actor(m, left):
    assert N.get(m,'Enemy_Flag',SLOT)==0
    for name,value in dict(Enemy_Flag=1,Enemy_ID=0x28,Enemy_Y_Position=ACTOR_TOP,Enemy_Y_HighPos=1,
                           Enemy_X_Position=left&255,Enemy_PageLoc=left>>8).items():
        m[N.address(m.bundle,name)+SLOT] = value
    N.put(m,ObjectOffset=SLOT)
    N.invoke(m,'InitEnemyObject',x=SLOT)
    address = N.address(m.bundle,'Enemy_BoundBoxCtrl')+SLOT
    assert m[address]==6
    N.put(m,ObjectOffset=0)


def replay(seed, start, left, *, admission=None):
    m = slim_fork(seed)
    N.put(m,Player_X_Position=start&255,Player_PageLoc=start>>8,Player_Y_Position=176,Player_Y_HighPos=1,
          Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,Player_X_Scroll=0,NmiDisable=0)
    m.ram[2][0x8fe] = 1
    if left is not None and admission is None:
        seed_actor(m,left)
    idle = N.address(m.bundle,'IdleLoop')
    carries = []
    lands = []
    planes = deque(maxlen=6)
    changes = []
    pending = None
    previous = None
    first_lost_overlap = None
    begin = None
    born = None

    def actor():
        if left is None or N.get(m,'Enemy_ID',SLOT)!=0x28 or not N.get(m,'Enemy_Flag',SLOT):
            return None
        return dict(left=B.world(m,'Enemy_X_Position','Enemy_PageLoc',SLOT),
                    flag=N.get(m,'Enemy_Flag',SLOT),id=N.get(m,'Enemy_ID',SLOT),
                    y=N.get(m,'Enemy_Y_Position',SLOT),direction=N.get(m,'Enemy_MovingDir',SLOT),
                    collision=N.get(m,'PlatformCollisionFlag',SLOT),
                    bounds=list(m[0x658+4*(SLOT+1):0x65c+4*(SLOT+1)]))

    def observe(c):
        nonlocal pending
        if c.pc not in (0xac29,0xa966,0xb5c8,0xb5d9,0xb5fd,0xb61c):
            return
        point = B.V.Q.tags(c),c.pc
        if point==(199,0xac29) and c.x==SLOT:
            carries.append((tick,B.player(m),N.get(m,'Player_Y_Position'),actor()['left']))
        elif point==(3,0xb5c8) and m[0xc8f0]==SLOT:
            lift = actor()
            if lift is not None:
                pending = (m[0xc8dd], c.a, lift)
        elif point in ((3,0xb5d9),(3,0xb5fd)):
            pending = None
        elif point==(3,0xb61c) and pending is not None:
            count, top, lift = pending
            assert m[0xc8dd]==count+4 and lift['bounds'][1]==top
            assert (m[0xc8e4],m[0xc8e5],m[0xc8e6],m[0xc8e7]) == (
                lift['bounds'][0],top,lift['bounds'][2],top)
            planes.append((tick,B.player(m),top,lift['left']))
            pending = None
        elif point==(3,0xa966) and LEFT<=B.player(m)<RIGHT:
            lands.append(dict(tick=tick,x=B.player(m),source_y=m.ram[2][0x210],actor=actor(),
                              preceding_planes=list(planes)[-2:]))

    for tick in range(800):
        p = Gap.player(m,tick)
        lift = actor()
        body = list(m[0x658:0x65c])
        if first_lost_overlap is None and lift and p['x']>=LEFT and lift['bounds'][2]<body[0]:
            first_lost_overlap = dict(player=p,actor=lift,body=body)
        key = p['source'],p['state']
        if key!=previous:
            changes.append(dict(player=p,actor=lift,body=body))
            previous = key
        if p['source']==5 or p['lives']!=2 or p['engine']!=8 or p['y']>=224:
            outcome = 'defeat'
            break
        if p['x']>=RIGHT and (p['y'],p['state'],p['source'])==(176,0,1):
            outcome = 'far-supported'
            break
        pad = 0
        if admission is None:
            if tick==1:
                assert (p['x'],p['y'],p['state'],p['source'])==(start,176,0,1),p
                begin = dict(player=p,actor=lift)
        else:
            if born is None and p['camera']>=admission:
                seed_actor(m,left)
                born = dict(player=p,actor=actor())
            if tick and p['x']<TAKEOFF:
                pad = 1
            elif p['x']==TAKEOFF and (p['y'],p['state'],p['source'])==(176,0,1):
                if lift and lift['left']>=left and lift['direction']==2 and begin is None:
                    begin = dict(player=p,actor=lift)
        if begin is not None:
            pad = 129 if tick<begin['player']['tick']+8 else 1
        m.controller_pad = pad
        N.consume(m)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,0x31
        c.stPushWord(0xe33b)
        B.run(c,lambda z:(z.pc,z.sp)==(idle+12,252),observe)
        B.C.I.C.clear(m)
    else:
        outcome = 'bound'
    return dict(outcome=outcome,start=start,initial_left=left,initial_top=ACTOR_TOP,box=6,born=born,
                carries=carries,lands=lands,begin=begin,terminal=p,terminal_actor=lift,
                first_lost_overlap=first_lost_overlap,changes=changes,planes=list(planes))


def main():
    raw = Gap.NIGHTLY.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest in (Gap.SECOND,Four.PIN)
    seed = Gap.terrain(raw,CAM)
    assert tiles(seed)==[0x54,0,0,0,0x54],tiles(seed)
    assert seed.ram[3][0x15c8:0x15cc]==bytes.fromhex('c920900d')
    assert seed.ram[3][0x15fe:0x1601]==bytes.fromhex('acddc8')
    assert seed.ram[3][0x1619:0x161d]==bytes.fromhex('8cddc860')
    print(json.dumps(dict(image_SHA256=digest,ground=tiles(seed))),flush=True)
    for start,left in ((TAKEOFF,None),(TAKEOFF,1376),(1372,1376),(TAKEOFF,1392),(TAKEOFF,ACTOR_LEFT)):
        q = replay(seed,start,left)
        print(json.dumps(q,separators=(',',':')),flush=True)
        if left==ACTOR_LEFT:
            verify_crossing(q)
        else:
            assert q['outcome']=='defeat' and not q['carries'],q
            if left is None:
                assert not q['lands'] and not q['planes'],q
            else:
                assert q['lands'] and q['terminal_actor']['flag']==1,q
                lost = q['first_lost_overlap']
                assert lost['actor']['bounds'][2]<lost['body'][0],q
    approach = replay(Gap.terrain(raw,1108),1220,ACTOR_LEFT,admission=1152)
    print(json.dumps(approach,separators=(',',':')),flush=True)
    verify_crossing(approach)
    assert approach['born']['player']['camera']==1152
    assert approach['born']['player']['tick']<approach['begin']['player']['tick']


def verify_crossing(result):
    assert result['outcome']=='far-supported' and not result['carries'],result
    assert len(result['lands'])==1,result
    land = result['lands'][0]
    assert (land['x'],land['source_y'],land['actor']['id'])==(1393,191,0x28),land
    assert land['preceding_planes'][-1][:3]==(land['tick'],1393,ACTOR_TOP),land
    bank = next(row['player'] for row in result['changes'] if row['player']['x']>=1412)
    assert (bank['x'],bank['y'],bank['state'],bank['source'])==(1412,176,0,1),bank
    terminal = result['terminal']
    assert (terminal['x'],terminal['y'],terminal['lives'],terminal['engine'])==(RIGHT,176,2,8),terminal


if __name__=='__main__':
    main()

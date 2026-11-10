"""Replay the authored fourth-pipe exit from a supported DK Jr. roof pose."""
from collections import deque
from hashlib import sha256
import json

import check_dkjr_four_pipe_funded_1110 as Four
import check_dkjr_gap_cap_probe_1110 as Gap
from check_mini_funded_actor_1108_v3 import slim_fork


B, N = Gap.B, Gap.N
START, DOWN_LEFT, SLOT = 916, 944, 4


def test(seed, center, stop):
    m = slim_fork(seed)
    N.put(m,Player_X_Position=START&255,Player_PageLoc=START>>8,Player_Y_Position=112,
          Player_Y_HighPos=1,Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,
          Player_X_Scroll=0,NmiDisable=0)
    m.ram[2][0x8fe] = 1
    for name,value in dict(Enemy_Flag=1,Enemy_ID=0x25,Enemy_Y_Position=192,Enemy_Y_HighPos=1,
                           Enemy_X_Position=DOWN_LEFT&255,Enemy_PageLoc=DOWN_LEFT>>8).items():
        m[N.address(m.bundle,name)+SLOT] = value
    N.put(m,ObjectOffset=SLOT)
    N.invoke(m,'InitEnemyObject',x=SLOT)
    m[0x47+SLOT] = center
    m[N.address(m.bundle,'Enemy_BoundBoxCtrl')+SLOT] = 5
    N.put(m,ObjectOffset=0)

    idle = N.address(m.bundle,'IdleLoop')
    phase = 'roof'
    old_top = None
    carries = 0
    events = []
    tail = deque(maxlen=4)
    top_range = [255,0]

    def observe(c):
        nonlocal carries
        if c.pc==0xac29 and B.V.Q.tags(c)==199 and c.x==SLOT:
            top = N.get(m,'Enemy_Y_Position',SLOT)
            native_y = N.get(m,'Player_Y_Position')
            if top-32==native_y and m.ram[2][0x6b]==1 and m.ram[2][0x210]==native_y+15:
                carries += 1

    for tick in range(1000):
        p = Gap.player(m,tick)
        x,y = p['x'],p['y']
        top = N.get(m,'Enemy_Y_Position',SLOT)
        top_range = [min(top_range[0],top),max(top_range[1],top)]
        grounded = (p['state'],p['source'])==(0,1)
        on_girder = bool(carries and grounded and y==top-32)
        before,pad = phase,0
        tail.append([tick,x,y,top,p['source'],p['state']])
        if p['source']==5 or p['lives']!=2 or p['engine']!=8:
            phase = 'injury'
            break
        if phase=='roof':
            pad = int(x<DOWN_LEFT-2)
            if on_girder:
                phase = 'lower'
            elif x>=DOWN_LEFT-2 and grounded and old_top is not None and 152<=top<=161 and top<=old_top:
                phase = 'step-down'
        elif phase=='step-down':
            pad = int(x<DOWN_LEFT+8)
            if on_girder:
                phase = 'lower'
        elif phase=='lower':
            pad = int(x<DOWN_LEFT+stop)
            if x>=DOWN_LEFT+stop and on_girder and 192<=top<=208 and top>=old_top:
                phase = 'depart'
        elif phase=='depart':
            pad = 1
            if x>=DOWN_LEFT+36 and grounded and y==176:
                phase = 'far-ground'
        if before!=phase:
            events.append([phase,tick,x,y,top])
        if phase=='far-ground':
            break
        old_top = top
        m.controller_pad = pad
        N.consume(m)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,0x31
        c.stPushWord(0xe33b)
        B.run(c,lambda z:(z.pc,z.sp)==(idle+12,252),observe)
        B.C.I.C.clear(m)
    return dict(center_y=center,stop_offset=stop,outcome=phase,events=events,carries=carries,
                top_range=top_range,terminal=p,tail=list(tail))


def main():
    raw = Gap.NIGHTLY.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest in (Gap.SECOND,Four.PIN)
    seed = Gap.terrain(raw,START-112)
    print(json.dumps(dict(image_SHA256=digest)),flush=True)
    for center,stop,expected in ((161,16,'injury'),(177,16,'roof'),
                                 (161,31,'far-ground'),(177,31,'roof')):
        result = test(seed,center,stop)
        print(json.dumps(result,separators=(',',':')),flush=True)
        assert result['outcome']==expected,result
        if expected=='roof':
            assert result['carries']==0 and result['top_range']==[144,211],result
        elif expected=='far-ground':
            terminal = result['terminal']
            assert (terminal['x'],terminal['y'],terminal['lives'])==(980,176,2),terminal


if __name__=='__main__':
    main()

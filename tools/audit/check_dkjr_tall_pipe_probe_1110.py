"""Isolate the third and fourth authored pipes with stock native girder fixtures."""
from collections import Counter, deque
from hashlib import sha256
import json

import check_dkjr_gap_cap_probe_1110 as Gap


B, N = Gap.B, Gap.N
CENTER = 0x47


def test(raw, pipe, up_left, down_left, center):
    start = up_left - 10
    m = Gap.terrain(raw, start-112)
    N.put(m,Player_X_Position=start&255,Player_PageLoc=start>>8,Player_Y_Position=176,
          Player_Y_HighPos=1,Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,
          Player_X_Scroll=0,NmiDisable=0)
    m.ram[2][0x8fe] = 1
    for slot,left in ((5,up_left),(4,down_left)):
        fields = dict(Enemy_Flag=1,Enemy_ID=0x25,Enemy_Y_Position=192,Enemy_Y_HighPos=1,
                      Enemy_X_Position=left&255,Enemy_PageLoc=left>>8)
        for name,value in fields.items():
            m[N.address(m.bundle,name)+slot] = value
        N.put(m,ObjectOffset=slot)
        N.invoke(m,'InitEnemyObject',x=slot)
        m[CENTER+slot] = center
        m[N.address(m.bundle,'Enemy_BoundBoxCtrl')+slot] = 5
    N.put(m,ObjectOffset=0)

    idle = N.address(m.bundle,'IdleLoop')
    phase, hold, rearm = 'approach',0,0
    old_lower = None
    events, tail, carries = [],deque(maxlen=8),Counter()
    tops = [[],[]]

    def observe(c):
        if (B.V.Q.tags(c),c.pc)==(199,0xac29) and c.x in (4,5):
            top = N.get(m,'Enemy_Y_Position',c.x)
            native_y = N.get(m,'Player_Y_Position')
            if top-32==native_y and m.ram[2][0x6b]==1 and m.ram[2][0x210]==native_y+15:
                carries[c.x] += 1

    for tick in range(1150):
        s = Gap.player(m,tick)
        x,y = s['x'],s['y']
        upper,lower = (N.get(m,'Enemy_Y_Position',slot) for slot in (5,4))
        for value,history in zip((upper,lower),tops):
            history.append(value)
        grounded = s['state']==0 and s['source']==1
        before, pad = phase,0
        if s['lives']!=2 or s['engine']!=8 or s['source']==5:
            phase = 'injury'
            break
        if phase=='approach':
            pad = 1
            if x>=up_left+10:
                phase,pad = 'board',0
        elif phase=='board':
            if grounded and upper-32==y<176 and carries[5]:
                phase='rise'
            elif grounded and tick>=rearm and 192<=upper<=208:
                hold,rearm=tick+8,tick+47
        elif phase=='rise':
            pad = int(x<up_left+29)
            if x>=up_left+29 and grounded and upper-32==y and 138<=upper<=144:
                hold,phase=tick+8,'cross'
        elif phase=='cross':
            pad=1
            if x>=pipe+4 and grounded and y==112:
                phase='roof'
        elif phase=='roof':
            pad=int(x<down_left-2)
            if carries[4] and grounded and lower-32==y:
                phase='lower'
            elif x>=down_left-2 and grounded and old_lower is not None and 152<=lower<=161 and lower<=old_lower:
                phase='step-down'
        elif phase=='step-down':
            pad=int(x<down_left+8)
            if carries[4] and grounded and lower-32==y:
                phase='lower'
        elif phase=='lower':
            pad=int(x<down_left+31)
            if x>=down_left+31 and grounded and lower-32==y and 192<=lower<=208 and lower>=old_lower:
                phase='depart'
        elif phase=='depart':
            pad=1
            if x>=down_left+36 and grounded and y==176:
                phase='far-ground'
        if before!=phase:
            events.append([phase,tick,x,y,upper,lower])
        tail.append([tick,x,y,upper,lower,s['source'],s['state']])
        if phase=='far-ground':
            break
        old_lower=lower
        m.controller_pad=pad | (128 if tick<hold else 0)
        N.consume(m)
        c=N.NesMPU(memory=m,pc=idle)
        c.sp,c.p=255,0x31
        c.stPushWord(0xe33b)
        B.run(c,lambda z:(z.pc,z.sp)==(idle+12,252),observe)
        B.C.I.C.clear(m)
    return dict(pipe=pipe,lefts=[up_left,down_left],center_y=center,outcome=phase,
                events=events,carries=dict(carries),terminal=s,
                top_ranges=[(min(v),max(v)) for v in tops],tail=list(tail))


def main():
    raw = Gap.NIGHTLY.read_bytes()
    assert sha256(raw).hexdigest()==Gap.SECOND
    for pipe in (736,912):
        for offset,center in ((48,161),(32,161),(48,169),(32,169),(48,128),(32,128)):
            result=test(raw,pipe,pipe-offset,pipe-offset+64,center)
            print(json.dumps(result,separators=(',',':')),flush=True)
            if result['outcome']=='far-ground':
                assert set(result['carries'])=={4,5}
                break


if __name__=='__main__':
    main()

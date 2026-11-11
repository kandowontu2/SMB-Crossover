"""Compare original controls at the late fifth-pipe descent on exact e295."""

from collections import deque
from hashlib import sha256
import json

import check_dkjr_late_terrain_1110 as Late
import stage_dkjr_late_nightly_1111 as Stage


B, N = Late.B, Late.N
ROOF_MAIN, DOWN_BIRTH = 8013, 7480
LEFT, ROOF_X, EDGE, FAR = 2640, 2614, 2671, 2676


def roof_fixture(image):
    m,idle = Late.entry(Late.Gap.terrain(image,ROOF_X-112),ROOF_X,144)
    slot = Late.seed_girder(m,LEFT,center=128)
    N.put(m,ObjectOffset=slot,FrameCounter=0)
    m[N.address(m.bundle,'PlatformCollisionFlag')+slot] = 255
    # Replay the stock vertical actor from birth to the recorded roof age.
    # This does not move or attach the translated player to the actor.
    for age in range(ROOF_MAIN-DOWN_BIRTH):
        N.invoke(m,'YMovingPlatform',x=slot)
        N.put(m,FrameCounter=(age+1)&255)
    assert N.get(m,'Enemy_Y_Position',slot)==58
    N.put(m,ObjectOffset=0)
    m.ram[2][Late.Second.S.SEEN] = 11
    return m,idle,slot


def replay(seed,idle,slot,launch_top):
    m = Late.slim_fork(seed)
    phase,last_top,hold,last_carry = 'roof',None,0,-100
    hop = None
    transitions = []
    lands = deque(maxlen=8)
    falls = deque(maxlen=4)

    def observe(c):
        nonlocal last_carry
        if c.pc==0xac29 and c.x==slot and B.V.Q.tags(c)==199:
            top = N.get(m,'Enemy_Y_Position',slot)
            y = N.get(m,'Player_Y_Position')
            if y+32==top and m.ram[2][0x210]==y+15 and m.ram[2][0x6b]==1:
                last_carry = tick
        elif c.pc==0xa966 and B.V.Q.tags(c)==3:
            lands.append((tick,B.player(m),m.ram[2][0x210],N.get(m,'Enemy_Y_Position',slot)))
        elif c.pc==0xa8e1 and B.V.Q.tags(c)==3:
            falls.append((tick,B.player(m),m.ram[2][0x210],m.ram[2][0x76],m.ram[2][0x7b]))

    for tick in range(680 if launch_top is None else 350):
        p = Late.Gap.player(m,tick)
        x,y = p['x'],p['y']
        top = N.get(m,'Enemy_Y_Position',slot)
        grounded = (p['source'],p['state'])==(1,0)
        on_plane = p['source']==1 and abs(y+32-top)<=1 and m.ram[2][0x210]==y+15
        carried = on_plane and y+32==top and tick-last_carry<=2
        before,pad = phase,0
        if p['source']==5 or p['lives']!=2 or p['engine']!=8:
            phase = 'defeat'
            break
        if phase=='roof':
            pad = int(tick>0 and x<LEFT-2)
            if carried:
                phase = 'lower'
            elif x>=LEFT-2 and grounded and y==144 and 184<=top<=193 and top<=last_top:
                phase = 'step'
        if phase=='step':
            pad = int(x<LEFT+8)
            if carried:
                phase = 'lower'
        if phase=='deck-hop':
            pad = int(x<EDGE)
            if tick>=hop+6 and on_plane:
                # The late edge is the intentional matched failure. Its
                # earlier departure lets the stock rise expose the fall.
                edge,minimum = (EDGE,190) if launch_top==186 else (LEFT+27,188)
                if x>=edge and minimum<=top<=208:
                    phase = 'depart'
                else:
                    phase = 'lower'
        if phase=='lower':
            pad = int(x<LEFT+27)
            if launch_top is not None and hop is None and x>=LEFT+1 and on_plane and top==launch_top and top>=last_top:
                hop,hold = tick,tick+8
                phase = 'deck-hop'
            elif x>=LEFT+27 and carried and 192<=top<=208 and top>=last_top:
                phase = 'depart'
        if phase=='depart':
            pad = 1
            if x>=FAR and grounded and y==176:
                phase = 'far-supported'
        if phase!=before:
            transitions.append((phase,tick,x,y,top,last_carry))
        if phase=='far-supported':
            break
        last_top = top
        Late.Second.update(m,idle,pad | (128 if tick<hold else 0),observe)
    return dict(outcome=phase,terminal=p,events=transitions,source_lands=list(lands),fall_checks=list(falls))


def main():
    current = Late.Gap.NIGHTLY.read_bytes()
    from deliver_jay_stock_draw_1111 import PIN as JAY_PIN, Parent
    if sha256(current).hexdigest()==JAY_PIN:
        current = Parent.Recipe.proposal(Parent.Recipe.V1.BASE.read_bytes())[0]
    image = current if sha256(current).hexdigest()==Stage.PIN else Stage.proposal(current)[0]
    seed = roof_fixture(image)
    runs = [replay(*seed,top) for top in (None,186,188)]
    baseline,fast,late = runs
    for result,top in zip(runs,(None,186,188),strict=True):
        print(json.dumps(dict(image_SHA256=Stage.PIN,launch_top=top,**result),separators=(',',':')),flush=True)
    assert baseline['outcome']==fast['outcome']=='far-supported'
    assert baseline['terminal']['tick']-fast['terminal']['tick']==384
    assert ('deck-hop',178,2641,154,186,156) in fast['events']
    assert ('depart',227,2671,159,191,156) in fast['events']
    assert fast['terminal']['lives']==2 and late['outcome']=='defeat'
    assert late['fall_checks'][-1][2]-late['fall_checks'][-1][3]>=late['fall_checks'][-1][4]


if __name__=='__main__':
    main()

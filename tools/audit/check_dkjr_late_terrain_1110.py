"""Run original DK Jr. control on the authored late 1-1 terrain in memory."""
import argparse
from collections import deque
from hashlib import sha256
import json

import check_dkjr_gap_cap_probe_1110 as Gap
import check_dkjr_second_gap_admission_1110 as Second
from check_mini_funded_actor_1108_v3 import slim_fork
from check_sonic_sms_ring_rebase_1110 import parent_bytes


B, N = Gap.B, Gap.N
CURRENT = '36e9a6a8b2f8dfb79447c8d9e74633245dd412ede0a408d075e3df2db01b85ca'
PIN = '3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8'


def image_bytes():
    image = Gap.NIGHTLY.read_bytes()
    digest = sha256(image).hexdigest()
    if digest==PIN:
        return image
    assert digest==CURRENT,digest
    base = parent_bytes()
    dk = Second.proposal(base)[0]
    changes = [(i,v) for i,(b,v) in enumerate(zip(base,dk,strict=True)) if b!=v]
    assert len(changes)==248
    assert all(base[i]==image[i] for i,_ in changes)
    joined = bytearray(image)
    for i,v in changes:
        joined[i] = v
    assert sha256(joined).hexdigest()==PIN
    return bytes(joined)


def column(m,x):
    base = 0x300+((x>>8)&1)*208+((x>>4)&15)
    return [(32+16*r,m[base+16*r]) for r in range(13) if m[base+16*r]]


def top(m,x):
    return next(iter(column(m,x)),None)


def entry(seed,x,y):
    m = slim_fork(seed)
    N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=y,
          Player_Y_HighPos=1,Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,
          Player_X_Scroll=0,NmiDisable=0)
    m.ram[2][0x8fe] = 1
    return m,N.address(m.bundle,'IdleLoop')


def replay(seed,x,y,*,target,hold,limit=140):
    m,idle = entry(seed,x,y)
    changes, land = [],[]
    previous = None
    tail = deque(maxlen=4)
    apex,max_x = y,x

    def observe(c):
        if c.pc==0xa966 and B.V.Q.tags(c)==3:
            land.append((tick,B.player(m),m.ram[2][0x210]))

    for tick in range(limit):
        p = Gap.player(m,tick)
        tail.append(p)
        apex,max_x = min(apex,p['y']),max(max_x,p['x'])
        key = p['source'],p['state']
        if key!=previous:
            changes.append(p)
            previous = key
        if tick==1:
            assert (p['x'],p['y'],p['source'],p['state'])==(x,y,1,0),p
        if p['source']==5 or p['lives']!=2 or p['engine']!=8:
            outcome = 'defeat'
            break
        if p['x']>=target[0] and p['y']==target[1] and p['source']==1 and p['state']==0:
            outcome = 'supported'
            break
        pad = 0 if tick==0 else 129 if tick<=hold else 1
        Second.update(m,idle,pad,observe)
    else:
        outcome = 'bound'
    return dict(start=[x,y],target=target,hold=hold,outcome=outcome,apex=apex,max_x=max_x,
                terminal=p,changes=changes,land=land[:12],tail=list(tail))


def stairs(seed,start,risers,goal,*,gap_launch=None,limit=520):
    m,idle = entry(seed,*start)
    actions, reached = [],[]
    index,hold = 0,0
    jumped_gap = False
    for tick in range(limit):
        p = Gap.player(m,tick)
        x,y = p['x'],p['y']
        grounded = (p['source'],p['state'])==(1,0)
        if p['source']==5 or p['lives']!=2 or p['engine']!=8:
            outcome = 'defeat'
            break
        if x>=goal[0] and y==goal[1] and grounded:
            outcome = 'supported'
            break
        if index<len(risers):
            edge,top_y = risers[index]
            if grounded and y==top_y-32:
                reached.append((tick,x,y,edge))
                index += 1
            elif tick and grounded and x>=edge-16 and y==top_y-16 and tick>hold:
                hold=tick+8
                actions.append((tick,x,y,edge))
        elif gap_launch is not None and not jumped_gap and grounded and x==gap_launch:
            assert y==112 and tick>=hold,p
            hold=tick+8
            actions.append((tick,x,y,'gap'))
            jumped_gap = True
        pad = 0 if tick==0 else 129 if tick<hold else 1
        Second.update(m,idle,pad)
    else:
        outcome = 'bound'
    return dict(start=start,goal=goal,outcome=outcome,actions=actions,reached=reached,terminal=p)


def seed_girder(m,left,*,top_y=192,center=128,box=5):
    slot = next(slot for slot in range(5,-1,-1) if not N.get(m,'Enemy_Flag',slot))
    for name,value in dict(Enemy_Flag=1,Enemy_ID=0x25,Enemy_Y_Position=top_y,Enemy_Y_HighPos=1,
                           Enemy_X_Position=left&255,Enemy_PageLoc=left>>8).items():
        m[N.address(m.bundle,name)+slot] = value
    saved = N.get(m,'ObjectOffset')
    N.put(m,ObjectOffset=slot)
    N.invoke(m,'InitEnemyObject',x=slot)
    N.put(m,ObjectOffset=saved)
    m[0x47+slot] = center
    m[N.address(m.bundle,'Enemy_BoundBoxCtrl')+slot] = box
    return slot


def girder_pipe(seed,pipe,target,*,center=177,descent=False,descent_center=128,down_edge=27):
    left = pipe-32
    m,idle = entry(seed,left-10,176)
    slot = seed_girder(m,left,center=center)
    down_left = pipe+32
    down_slot = seed_girder(m,down_left,center=descent_center) if descent else None
    phase,hold,rearm = 'approach',0,0
    events,tail = [],deque(maxlen=6)
    fall_checks = deque(maxlen=6)
    contact_events = []
    carries = {s:0 for s in (slot,down_slot) if s is not None}
    previous_down = None
    bounce_pc = 0xd7a4

    def observe(c):
        if c.pc==0xa8e1 and B.V.Q.tags(c)==3:
            fall_checks.append((tick,B.player(m),m.ram[2][0x210],m.ram[2][0x76],m.ram[2][0x7b]))
        if c.pc in (0xbd93,bounce_pc) and B.V.Q.tags(c)==(3 if c.pc==0xbd93 else 2):
            actors = [(s,N.get(m,'Enemy_ID',s),B.world(m,'Enemy_X_Position','Enemy_PageLoc',s),
                       N.get(m,'Enemy_Y_Position',s)) for s in range(6) if N.get(m,'Enemy_Flag',s)]
            contact_events.append(dict(tick=tick,x=B.player(m),y=N.get(m,'Player_Y_Position'),
                                       routine=hex(c.pc),slot=N.get(m,'ObjectOffset'),actors=actors))
        if c.pc==0xac29 and c.x in carries and B.V.Q.tags(c)==199:
            top_y = N.get(m,'Enemy_Y_Position',c.x)
            y = N.get(m,'Player_Y_Position')
            if y+32==top_y and m.ram[2][0x210]==y+15 and m.ram[2][0x6b]==1:
                carries[c.x] += 1

    for tick in range(980):
        p = Gap.player(m,tick)
        x,y = p['x'],p['y']
        top_y = N.get(m,'Enemy_Y_Position',slot)
        down = N.get(m,'Enemy_Y_Position',down_slot) if descent else None
        grounded = (p['source'],p['state'])==(1,0)
        on_girder = carries[slot] and p['source']==1 and y+32==top_y
        on_down = descent and carries[down_slot] and p['source']==1 and y+32==down
        before = phase
        pad = 0
        tail.append([tick,x,y,top_y,down,p['source'],p['state']])
        if p['source']==5 or p['lives']!=2 or p['engine']!=8:
            phase = 'defeat'
            break
        if phase=='approach':
            pad = 1
            if x>=left+10:
                phase,pad = 'board',0
        if phase=='board':
            if on_girder and y<176:
                phase = 'rise'
            elif grounded and tick>=rearm and 192<=top_y<=208:
                hold,rearm = tick+8,tick+47
        if phase=='rise' and on_girder:
            phase = 'edge'
        if phase=='edge':
            pad = int(x<left+23)
            if x>=left+23 and grounded and y==144:
                phase = 'cross'
            elif x>=left+23 and on_girder and 170<=top_y<=176:
                hold,phase = tick+8,'cross'
        if phase=='cross':
            pad = 1
            if x>=pipe+4 and grounded and y==144:
                phase = 'roof'
        if phase=='roof':
            if descent:
                pad = int(x<down_left-2)
                if on_down:
                    phase = 'lower'
                elif x>=down_left-2 and y==144 and p['source']==1 and 184<=down<=193 and down<=previous_down:
                    phase = 'step-down'
            else:
                pad = 1
                if x>=target[0] and y==target[1] and grounded:
                    phase = 'far-supported'
        if phase=='step-down':
            pad = int(x<down_left+8)
            if on_down:
                phase = 'lower'
        if phase=='lower':
            pad = int(x<down_left+down_edge)
            if x>=down_left+down_edge and on_down and 192<=down<=208 and down>=previous_down:
                phase = 'depart'
        if phase=='depart':
            pad = 1
            if x>=target[0] and y==target[1] and grounded:
                phase = 'far-supported'
        if phase!=before:
            events.append([phase,tick,x,y,top_y,down])
        if phase=='far-supported':
            break
        previous_down = down
        Second.update(m,idle,pad | (128 if tick<hold else 0),observe)
    return dict(pipe=pipe,left=left,center=left+16,initial_top=192,oscillator_center=center,box=5,slot=slot,
                descent_left=down_left if descent else None,descent_slot=down_slot,
                descent_center_y=descent_center if descent else None,descent_edge=down_edge if descent else None,
                outcome=phase,events=events,carries=carries,terminal=p,fall_checks=list(fall_checks),
                contacts=contact_events,tail=list(tail))


def girder_descent(seed,*,exit_stage=False):
    left = 3040
    m,idle = entry(seed,3026,48)
    slot = seed_girder(m,left)
    phase,last_top = 'cap',None
    events,tail = [],deque(maxlen=6)
    carries = 0

    def observe(c):
        nonlocal carries
        if c.pc==0xac29 and c.x==slot and B.V.Q.tags(c)==199:
            y = N.get(m,'Player_Y_Position')
            if y+32==N.get(m,'Enemy_Y_Position',slot) and m.ram[2][0x210]==y+15 and m.ram[2][0x6b]==1:
                carries += 1

    for tick in range(680):
        p = Gap.player(m,tick)
        x,y = p['x'],p['y']
        top_y = N.get(m,'Enemy_Y_Position',slot)
        grounded = (p['source'],p['state'])==(1,0)
        on_girder = carries and p['source']==1 and y+32==top_y
        before = phase
        pad = 0
        tail.append([tick,x,y,top_y,p['source'],p['state']])
        if p['source']==5 or p['lives']!=2 or p['engine']!=8:
            phase = 'defeat'
            break
        if phase=='cap':
            pad = int(x<left-2)
            if on_girder and x>=left-2:
                phase = 'lower'
            elif x>=left-2 and p['source']==1 and y==48 and 80<=top_y<=92 and top_y>last_top:
                phase = 'board'
        if phase=='board':
            pad = int(x<left+8)
            if on_girder:
                phase = 'lower'
        if phase=='lower':
            pad = int(x<left+27)
            if x>=left+27 and on_girder and 192<=top_y<=208 and top_y>=last_top:
                phase = 'depart'
        if phase=='depart':
            pad = 1
            if x>=left+36 and grounded and y==176:
                phase = 'far-supported'
        if phase!=before:
            events.append([phase,tick,x,y,top_y])
        if phase=='far-supported':
            break
        last_top = top_y
        Second.update(m,idle,pad,observe)
    result = dict(left=left,center=left+16,initial_top=192,oscillator_center=128,box=5,slot=slot,
                  outcome=phase,events=events,carries=carries,terminal=p,tail=list(tail))
    if exit_stage and phase=='far-supported':
        result['stage_exit'] = finish_stage(m,idle)
    return result


def finish_stage(m,idle):
    transitions = []
    previous = None
    hold = 0
    flag_hop = None
    for tick in range(1600):
        p = Gap.player(m,tick)
        level,mode,task,area,world = (N.get(m,name) for name in (
            'LevelNumber','OperMode','OperMode_Task','AreaType','WorldNumber'))
        key = level,mode,task,p['engine'],area
        if key!=previous:
            transitions.append(dict(level=level,mode=mode,task=task,area=area,**p))
            previous = key
        if p['lives']!=2 or p['source']==5 or world!=0:
            break
        if key==(1,1,3,8,2):
            assert any(e['engine']==4 and e['level']==0 for e in transitions),transitions
            return dict(outcome='active-underground-1-2',transitions=transitions,flag_hop=flag_hop)
        m.controller_pad = int(level==0 and p['engine']==8)
        if m.controller_pad and (p['x'],p['y'],p['source'],p['state'])==(3152,176,1,0) and flag_hop is None:
            hold = tick+8
            flag_hop = p
        if m.controller_pad and tick<hold:
            m.controller_pad |= 128
        N.consume(m)
        cpu = N.NesMPU(memory=m,pc=idle)
        cpu.sp,cpu.p = 255,0x31
        cpu.stPushWord(0xe33b)
        for _ in range(250000 if p['engine'] else 4000000):
            if (cpu.pc,cpu.sp)==(idle+12,252):
                break
            assert m[cpu.pc],(p,hex(cpu.pc),m.rawtags)
            cpu.step()
        else:
            raise AssertionError(('Native stage loop bound',p,hex(cpu.pc),cpu.sp))
        B.C.I.C.clear(m)
    return dict(outcome='stopped',transitions=transitions,terminal=p,flag_hop=flag_hop)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section',choices=('all','local','stairs','pipe-helpers','progression','exit'),default='all')
    args = parser.parse_args()
    image = image_bytes()
    print(json.dumps(dict(image_SHA256=PIN)),flush=True)
    cases = (
        ('third-gap',2304,((2438,112,(2480,112),8),(2438,112,(2480,112),0),
                           (2438,112,(2544,176),8))),
        ('first-stairs',2000,((2130,176,(2144,160),8),(2130,176,(2144,160),16))),
        ('third-gap-stairs',2224,((2354,176,(2368,160),8),(2354,176,(2368,160),16))),
        ('late-pipe',2480,((2594,176,(2608,144),8),)),
        ('last-pipe-and-stairs',2736,((2850,176,(2864,144),8),(2888,144,(2912,144),0))),
        ('last-stairs-descent',2896,((3026,48,(3060,176),0),(3026,48,(3060,176),8))),
    )
    if args.section in ('all','local'):
        for name,cam,probes in cases:
            seed = Gap.terrain(image,cam)
            print(json.dumps(dict(scene=name,terrain={x:top(seed,x) for x in range(cam,cam+384,16)})),flush=True)
            for x,y,target,hold in probes:
                result = replay(seed,x,y,target=target,hold=hold,limit=260 if target[0]==2544 else 180)
                print(json.dumps(dict(scene=name,**result),separators=(',',':')),flush=True)
    if args.section in ('all','stairs','progression'):
        climbs = ((2000,(2130,176),2144,4,192,2198,(2304,176)),
                  (2224,(2354,176),2368,4,192,2438,(2544,176)),
                  (2736,(2888,144),2928,6,160,None,(3026,48)))
        for cam,start,first,count,first_y,jump,target in climbs:
            seed = Gap.terrain(image,cam)
            risers = tuple((first+16*i,first_y-16*i) for i in range(count))
            assert all(top(seed,edge)==(y,97) for edge,y in risers)
            result = stairs(seed,start,risers,target,gap_launch=jump)
            assert result['outcome']=='supported',result
            print(json.dumps(dict(scene='linked-stairs',**result),separators=(',',':')),flush=True)
        seed = Gap.terrain(image,2896)
        for hold in (0,8):
            result = replay(seed,3026,48,target=(3060,176),hold=hold,limit=180)
            print(json.dumps(dict(scene='last-stairs-descent',**result),separators=(',',':')),flush=True)
    if args.section in ('all','pipe-helpers','progression'):
        for pipe,target,descent in ((2608,(2648,176),False),(2608,(2676,176),True),(2864,(2912,144),False)):
            seed = Gap.terrain(image,pipe-154)
            result = girder_pipe(seed,pipe,target,descent=descent)
            print(json.dumps(dict(scene='stock-pipe-girder',**result),separators=(',',':')),flush=True)
        result = girder_descent(Gap.terrain(image,2896),exit_stage=args.section=='all')
        print(json.dumps(dict(scene='stock-descent-girder',**result),separators=(',',':')),flush=True)
    if args.section=='exit':
        m,idle = entry(Gap.terrain(image,2964),3076,176)
        print(json.dumps(finish_stage(m,idle),separators=(',',':')),flush=True)


if __name__=='__main__':
    main()

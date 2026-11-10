"""Measure DK Jr.'s unassisted jump on the authored first-gap terrain."""
from collections import deque
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_first_native_girder_1110 as B
from check_mini_funded_actor_1108_v3 import slim_fork


N, C = B.N, B.C
PIN = '9897c2b85489024be25b4b296d0ea57975a579ba1e3ff37a71f7ac3e0b195b97'
SECOND = 'a20d254d4730583ee1f039b10abcf873559987e4f989968037a38e17427faac1'
NIGHTLY = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
LEFT, RIGHT, CAM = 1104, 1136, 960


def terrain(raw, camera=CAM):
    m = C.cold(raw,raw[534485:534501])
    N.put(m, AreaPointer=0x25, AreaType=1, WorldNumber=0, LevelNumber=0,
          AreaDataOffset=0, AreaObjectPageLoc=0, AreaObjectPageSel=0,
          BackloadingFlag=0, BehindAreaParserFlag=0)
    N.invoke(m,'GetAreaDataAddrs')
    assert N.get(m,'AreaDataLow') == 0xce
    lengths = N.address(m.bundle,'AreaObjectLength')
    m[lengths:lengths+3] = bytes([255])*3
    columns = []
    for col in range(camera//16+32):
        N.put(m,CurrentPageLoc=col//16,CurrentColumnPos=col%16,BlockBufferColumnPos=col%32)
        N.invoke(m,'AreaParserCore')
        tile = N.address(m.bundle,'MetatileBuffer')
        columns.append(bytes(m[tile:tile+13]))
    if camera == CAM:
        assert [columns[col][11] for col in range(LEFT//16-1,RIGHT//16+1)] == [0x54,0,0,0x54]
    assert [(16*col,16*(r+2)) for col,row in enumerate(columns) for r,t in enumerate(row)
            if t in (0x10,0x12)][:4] == [(448,176),(608,160),(736,144),(912,144)]
    end = camera//16+32
    N.put(m,CurrentPageLoc=end//16,CurrentColumnPos=end%16,BlockBufferColumnPos=end%32,
          AreaParserTaskNum=0,ScrollThirtyTwo=0,
          ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8,
          ScreenRight_X_Pos=(camera+255)&255,ScreenRight_PageLoc=(camera+255)>>8)
    return m


def player(m, tick):
    return dict(tick=tick, x=B.player(m), y=N.get(m,'Player_Y_Position'),
                state=N.get(m,'Player_State'), source=m.ram[2][0x6b],
                source_frac=m.ram[2][0x76],camera=B.camera(m),
                lives=N.get(m,'NumberofLives'), engine=N.get(m,'GameEngineSubroutine'))


def replay(seed, x, idle_ticks, hold):
    m = slim_fork(seed)
    N.put(m,Player_X_Position=x&255,Player_PageLoc=x>>8,Player_Y_Position=176,Player_Y_HighPos=1,
          Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,Player_X_Scroll=0,NmiDisable=0)
    # Re-enter the ordinary native ingress. It imports the translated anchor.
    m.ram[2][0x8fe] = 1
    idle = N.address(m.bundle,'IdleLoop')
    begin, apex, max_x = None,255,x
    tail = deque(maxlen=6)
    changes, carry_calls = [], []
    previous = None

    def observe(c):
        if (B.V.Q.tags(c),c.pc)==(199,0xac29):
            carry_calls.append((tick,c.x))

    for tick in range(85):
        row = player(m,tick)
        tail.append(row)
        key = row['source'],row['state']
        if key != previous:
            changes.append(row)
            previous = key
        apex, max_x = min(apex,row['y']),max(max_x,row['x'])
        if tick == idle_ticks:
            if row['source'] != 1 or row['state'] != 0 or row['y'] != 176:
                return dict(request=x,idle=idle_ticks,hold=hold,outcome='no-supported-takeoff',terminal=row)
            begin = row
        if row['x'] >= RIGHT and row['source'] == 1 and row['state'] == 0 and row['y'] == 176:
            outcome = 'far-supported'
            break
        if row['engine'] != 8 or row['lives'] != 2 or row['source'] == 5 or row['y'] >= 224:
            outcome = 'below-gap-or-death'
            break
        m.controller_pad = 0 if tick < idle_ticks else 129 if tick < idle_ticks+hold else 1
        N.consume(m)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,0x31
        c.stPushWord(0xe33b)
        B.run(c,lambda z:(z.pc,z.sp)==(idle+12,252),observe)
        B.C.I.C.clear(m)
    else:
        outcome = 'bound'
    return dict(request=x,idle=idle_ticks,hold=hold,outcome=outcome,begin=begin,
                apex=apex,max_x=max_x,terminal=row,state_changes=changes,
                carry_calls=carry_calls,tail=list(tail))


def main():
    raw = NIGHTLY.read_bytes()
    digest = sha256(raw).hexdigest()
    assert digest in (PIN,SECOND)
    seed = terrain(raw)
    no_a = replay(seed,1094,1,0)
    result = replay(seed,1094,1,8)
    assert (no_a['outcome'],no_a['terminal']['x'],no_a['terminal']['tick']) == ('below-gap-or-death',1105,34)
    assert (result['outcome'],result['apex'],result['terminal']['tick']) == ('far-supported',161,70)
    assert result['terminal']['lives']==2 and result['terminal']['engine']==8
    assert not (no_a['carry_calls'] or result['carry_calls'])
    print(json.dumps(dict(image_SHA256=digest,right=no_a,right_A=result),separators=(',',':')),flush=True)


if __name__=='__main__':
    main()

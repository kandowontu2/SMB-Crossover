"""Assemble and qualify DK Jr.'s stock second-gap actor in memory."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json

import check_dkjr_four_pipe_funded_1110 as Four
import check_dkjr_second_gap_probe_1110 as Probe


R, B, N, S = Four.R, Four.B, Four.N, Four.S
SOURCE = R/'tools/reference/dkjr_second_gap_admission_1110.s'
LAYOUT = dict(Four.LAYOUT,REFRESH=(0xb624,129))
del LAYOUT['ORDINAL']
del LAYOUT['DK_COLD']
LEFTS = (*Four.LEFTS,Probe.ACTOR_LEFT)
PARENT = Four.PIN
PIN = 'c506ffea482d031a7c3ea6e7866c482e50629494e500443a7bfbeab1dc9270ed'


def proposal(raw):
    assert sha256(raw).hexdigest()==PARENT
    carrier = bytearray(S.V.T.payload(raw))
    original_cookie = raw[Four.COOKIE_AT:Four.COOKIE_AT+16]
    assert original_cookie==Four.COOKIE[:3]+sha256(carrier).digest()[:13]
    old_layout = {name:Four.LAYOUT[name] for name in (*LAYOUT,'ORDINAL')}
    old = Four.Previous.assemble(Four.SOURCE.read_text(encoding='utf-8'),old_layout)
    new = Four.Previous.assemble(SOURCE.read_text(encoding='utf-8'),LAYOUT)
    assert new['used']=={'BOX':8,'CAMERA_START':4,'WINDOW_MASK':4,'ROWS':17,
                         'PIPE':117,'REFRESH_TARGET':3,'REFRESH':129}
    labels = new['symbols']
    assert (labels['DkPipeScope'],labels['DkPipeEnd'],labels['DkRefreshPlatform'],
            labels['DkRefreshPlatformEnd'])==(0xd18b,0xd200,0xb624,0xb6a5)
    for name,(pc,size) in LAYOUT.items():
        at = Four.Previous.offset(pc)
        original = old['images'][name]
        if name=='REFRESH':
            original += old['images']['ORDINAL']
        pad = b'\xea' if name=='BOX' else b'\xff'
        assert carrier[at:at+size]==original.ljust(size,pad),name
        carrier[at:at+size] = new['images'][name].ljust(size,pad)
    cookie = original_cookie[:3]+sha256(carrier).digest()[:13]
    image = bytearray(raw)
    pages = []
    for i,page in enumerate(S.V.T.PAGES):
        at = S.Art.CHR+1024*page
        updated = carrier[1024*i:1024*(i+1)]
        if updated!=raw[at:at+1024]:
            pages.append(page)
            image[at:at+1024] = updated
    assert pages==[881,883,960],pages
    image[Four.COOKIE_AT:Four.COOKIE_AT+16] = cookie
    assert S.V.T.payload(image)==carrier
    atlas = json.loads(S.Art.ATLAS.read_text(encoding='utf-8'))
    for selection in atlas['all_legal_8x16_selections']:
        page = selection['physical_page']
        first,last = selection['physical_byte_half_open']
        if page==960 and selection['native_tile'] in S.Art.ALIASES:
            tile = S.Art.ALIASES[selection['native_tile']]
            assert S.Art.art(raw,tile)==S.Art.art(image,tile)
        else:
            at = S.Art.CHR+page*1024
            assert image[at+first:at+last]==raw[at+first:at+last]
    assert sha256(image).hexdigest()==PIN
    return bytes(image),cookie,labels


def actor(m, slot):
    return (B.world(m,'Enemy_X_Position','Enemy_PageLoc',slot),
            N.get(m,'Enemy_Y_Position',slot),N.get(m,'Enemy_ID',slot),
            N.get(m,'Enemy_Flag',slot),N.get(m,'Enemy_BoundBoxCtrl',slot),
            N.get(m,'Enemy_State',slot),N.get(m,'Enemy_X_Speed',slot),
            N.get(m,'Enemy_Y_Speed',slot))


def verify_admission(seed, labels):
    results = Four.verify_admission(seed,labels)
    count = 0
    for cam,seen in product(range(1024,1536),range(10)):
        m = Four.fixture(seed,cam,seen)
        admitted = 256<=Probe.ACTOR_LEFT-cam<=287 and seen<=8
        c = S.direct(m,labels['DkPipeScope'])
        assert bool(c.p&1)==admitted,(cam,seen)
        assert m.ram[2][S.SEEN]==(8 if admitted else seen)
        count += 1
    results['camera_and_cursor'] += count
    for cam,slot in product((1121,1152),range(6)):
        m = Four.fixture(seed,cam,8,6)
        saved = Four.abi(m)
        S.direct(m,labels['DkRefreshPlatform'])
        assert m.ram[2][S.SEEN]==8 and Four.abi(m)==saved
        Four.put_slot(m,slot,Enemy_Flag=0,Enemy_X_Speed=0x7f,Enemy_Y_Speed=0x55)
        c = S.direct(m,labels['DkRefreshPlatform'])
        assert (c.a,c.x,c.y,c.p&0xef)==(85,7,91,0x21) and Four.abi(m)==saved
        assert actor(m,slot)==(1408,208,0x28,1,6,0,0,0),actor(m,slot)
        assert all((N.get(m,'Enemy_Flag',other),N.get(m,'Enemy_ID',other))==(1,6)
                   for other in range(6) if other!=slot)
        assert m.ram[2][S.SEEN]==9
        Four.put_slot(m,slot,Enemy_Flag=0)
        S.direct(m,labels['DkRefreshPlatform'])
        assert N.get(m,'Enemy_Flag',slot)==0 and m.ram[2][S.SEEN]==9
        results['full_pool_retry_and_birth'] += 1
    m = Four.fixture(seed,1121,8)
    N.put(m,AreaDataLow=0)
    S.direct(m,labels['DkRefreshPlatform'])
    assert m.ram[2][S.SEEN]==8 and all(not N.get(m,'Enemy_Flag',s) for s in range(6))
    m.ram[2][S.SEEN] = 9
    N.invoke(m,'HuFresh')
    assert m.ram[2][S.SEEN]==0
    results['wrong_loaded_room'] += 1
    results['warm_life_reset'] += 1
    return results


def verify_refresh(before, after, labels):
    counts = Counter()
    cycle_deltas = {}
    for slot,enemy,flag,dx in product(range(6),range(0x24,0x2d),(0,1,0x80),(-32,0,63,255,288)):
        rows = []
        for seed in (before,after):
            m = Four.fixture(seed,1024,9)
            x = 1024+dx
            Four.put_slot(m,slot,Enemy_Flag=flag,Enemy_ID=enemy,Enemy_X_Position=x&255,
                          Enemy_PageLoc=x>>8,Enemy_Y_Position=192,Enemy_Y_HighPos=1,
                          Enemy_BoundBoxCtrl=4 if enemy>=0x2b else 5)
            m.writes.clear()
            m.ppu_log.clear()
            c = S.direct(m,labels['DkRefreshPlatform'])
            result = ((c.a,c.x,c.y,c.p,c.sp),Four.abi(m),bytes(m[:0x100]),bytes(m[0x200:0x800]),
                      bytes(m.ram[2][:0x900]),tuple(m.ppu_log))
            writes = [(at,value) for at,value in m.writes if not 0x17b<=at<0x200]
            rows.append((result,writes,c.processorCycles))
        old,new = rows
        assert old[0]==new[0],(slot,enemy,flag,dx)
        if flag==1:
            assert old[1]==new[1],(slot,enemy,flag,dx)
            group = 'active'
        else:
            assert not old[1]
            assert all(at in (*range(3,11),0x0d,0x162,0x16a,0x16c,0x16d,0x179)
                       for at,_ in new[1]),new[1]
            group = 'empty_or_inactive'
        cycle_deltas.setdefault(group,[]).append(new[2]-old[2])
        counts[group] += 1
    return dict(counts,cycles={key:[min(v),max(v)] for key,v in cycle_deltas.items()})


def route_entry(image):
    m = Probe.Gap.terrain(image,1108)
    N.put(m,Player_X_Position=1220&255,Player_PageLoc=1220>>8,Player_Y_Position=176,
          Player_Y_HighPos=1,Player_State=0,Player_X_Speed=0,Player_Y_Speed=0,
          Player_X_Scroll=0,NmiDisable=0)
    assert all(not N.get(m,'Enemy_Flag',s) for s in range(6))
    m.ram[2][0x8fe] = 1
    return m,N.address(m.bundle,'IdleLoop')


def update(m,idle,pad,observe=None):
    m.controller_pad = pad
    N.consume(m)
    c = N.NesMPU(memory=m,pc=idle)
    c.sp,c.p = 255,0x31
    c.stPushWord(0xe33b)
    B.run(c,lambda z:(z.pc,z.sp)==(idle+12,252),observe)
    B.C.I.C.clear(m)
    return c.processorCycles


def verify_route(image, labels):
    # Translate the ingress only. The actual refresh call creates the actor.
    m,idle = route_entry(image)
    constructor = N.address(m.bundle,'InitEnemyObject')
    takeoff = None
    born, lands, bank = [],[],None
    slot = None

    def observe(c):
        nonlocal slot
        if c.pc==labels['Birth'] and m.ram[2][S.SEEN]==8:
            assert slot is None and B.V.Q.tags(c)==2 and c.p&1
            slot = c.x
        elif c.pc==constructor and c.x==slot and B.V.Q.tags(c)==130:
            born.append((tick,B.camera(m),B.player(m),actor(m,slot)[:4]))
        elif c.pc==0xa966 and B.V.Q.tags(c)==3 and Probe.LEFT<=B.player(m)<Probe.RIGHT:
            assert slot is not None and actor(m,slot)[2:5]==(0x28,1,6)
            lands.append((tick,B.player(m),actor(m,slot)))

    for tick in range(800):
        row = Probe.Gap.player(m,tick)
        x,y = row['x'],row['y']
        grounded = (y,row['state'],row['source'])==(176,0,1)
        assert row['source']!=5 and row['engine']==8 and row['lives']==2,row
        if grounded and x>=1412 and bank is None:
            bank = row
        if grounded and x==Probe.RIGHT:
            assert len(born)==len(lands)==1 and bank['x']==1412,row
            assert born[0][1:]==(1121,1233,(1408,208,0x28,1)),born
            assert lands[0][1]==1393 and m.ram[2][S.SEEN]==9,lands
            return dict(birth=born[0],takeoff=takeoff,land=lands[0],bank=bank,terminal=row)
        pad = int(tick>0 and x<Probe.TAKEOFF)
        if x==Probe.TAKEOFF and grounded and takeoff is None and slot is not None:
            if actor(m,slot)[0]>=Probe.ACTOR_LEFT and N.get(m,'Enemy_MovingDir',slot)==2:
                takeoff = row
        if takeoff is not None:
            pad = 129 if tick<takeoff['tick']+8 else 1
        update(m,idle,pad,observe)
    raise AssertionError((born,takeoff,lands,row,actor(m,slot) if slot is not None else None))


def verify_idle_and_walk(raw,image):
    timelines = []
    for rom in (raw,image):
        m,idle = route_entry(rom)
        cycles, players = [],[]
        for tick in range(28):
            cycles.append(update(m,idle,int(tick>=14)))
            assert all(not N.get(m,'Enemy_Flag',s) for s in range(6)),tick
            players.append(Probe.Gap.player(m,tick))
        timelines.append((cycles,players))
    (old,old_players),(new,new_players) = timelines
    assert old_players==new_players and {b-a for a,b in zip(old,new,strict=True)}=={451}
    return dict(updates=len(old),baseline_cycles=[min(old),max(old)],
                candidate_cycles=[min(new),max(new)],delta=451)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route-only',action='store_true')
    args = parser.parse_args()
    raw = Four.NIGHTLY.read_bytes()
    image,cookie,labels = proposal(raw)
    result = dict(parent_SHA256=PARENT,memory_only_SHA256=sha256(image).hexdigest(),cookie=cookie.hex())
    result['route'] = verify_route(image,labels)
    print(json.dumps(result,separators=(',',':')),flush=True)
    if not args.route_only:
        before = Four.cold(raw,raw[Four.COOKIE_AT:Four.COOKIE_AT+16])
        after = Four.cold(image,cookie)
        counts = verify_admission(after,labels)
        counts['actual_cold_readback_and_committed_headers'] = 2
        counts['refresh'] = verify_refresh(before,after,labels)
        counts['empty_idle_and_walking_frames'] = verify_idle_and_walk(raw,image)
        print(json.dumps(dict(checks=counts,output_files=0),separators=(',',':')),flush=True)


if __name__=='__main__':
    main()

"""Assemble and qualify all thirteen DK Jr. stock actor rows on the current ROM."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json

import check_dkjr_four_pipe_funded_1110 as Four
import check_dkjr_late_terrain_1110 as Late
import check_dkjr_second_gap_admission_1110 as Second
from check_mini_funded_actor_1108_v3 import slim_fork


R, B, N, S = Four.R, Four.B, Four.N, Four.S
SOURCE = R/'tools/reference/dkjr_late_girder_admission_1111.s'
PARENT = Late.PIN
PIN = 'f837a0259b069392003a8dbd1a71571f86189a309c92a6c68b468e8794321dab'
SUCCESSORS = {
    PARENT: PIN,
    '6cb828b3c97bd287f5fb3421e01a478319bf3615e5f2eeed8a6b7888b15c9657':
        'b1d449ebd7bbcc6f9c75be00891afc627a8354acb56a18bb9cd7a4ef40129576',
}
PARENT_COOKIE = bytes.fromhex('a72801b96058ad9af823ba7f575bf9d0')
LAYOUT = {name:Second.LAYOUT[name] for name in ('BOX','ROWS','PIPE','REFRESH_TARGET','REFRESH')}
LAYOUT['NATIVE_CALL'] = (0xb7ca,30)
LEFTS = (*Second.LEFTS,2576,2640,2832,3040)
CENTERS = (*Four.CENTERS,0,177,128,177,128)
OLD_NATIVE_CALLS = bytes.fromhex('a96f8d6c01a9be8d6d01a9804c5a01a9cb8d6c01a9a18d6d01a9804c5a01')


def source_parent(current=None):
    """Recover the exact DK parent from itself or the verified Sonic successor."""
    if current is None:
        current = Four.NIGHTLY.read_bytes()
    digest = sha256(current).hexdigest()
    if digest==PARENT:
        return current
    from check_sonic_sms_fast_snapshot_1111 import PIN as SONIC_PIN, LIVE, Leaf, from_installed
    if digest!=SONIC_PIN:
        assert digest==Late.CURRENT,digest
        from deliver_dkjr_second_gap_1111 import merge
        from check_sonic_sms_ring_rebase_1110 import parent_bytes
        return merge(parent_bytes(),current)
    parent = bytearray(current)
    at = LIVE.CHR+330*1024+Leaf.ENTRY-0xbc00
    parent[at:at+3] = Leaf.PREIMAGE[:3]
    at = LIVE.CHR+334*1024+Leaf.PROBE-0xd800
    parent[at:at+33] = b'\xff'*33
    parent[LIVE.COOKIE:LIVE.COOKIE+16] = bytes.fromhex('a72b018c2e04635376b3ef263b330c8f')
    assert sha256(parent).hexdigest()==PARENT
    assert from_installed(bytes(parent))[0]==current
    return bytes(parent)


def proposal(raw):
    """Return candidate ROM bytes, owner cookie, and linked source addresses."""
    parent = sha256(raw).hexdigest()
    assert parent in SUCCESSORS
    payload = S.V.T.payload(raw)
    assert raw[Four.COOKIE_AT:Four.COOKIE_AT+16]==PARENT_COOKIE
    assert PARENT_COOKIE==b'\xa7\x28\x01'+sha256(payload).digest()[:13]
    old = Four.Previous.assemble(Second.SOURCE.read_text(encoding='utf-8'),Second.LAYOUT)
    new = Four.Previous.assemble(SOURCE.read_text(encoding='utf-8'),LAYOUT)
    assert new['used']=={'BOX':8,'ROWS':13,'PIPE':117,'REFRESH_TARGET':3,'REFRESH':128,'NATIVE_CALL':30}
    labels = new['symbols']
    assert (labels['DkPipeCreated'],labels['DkAfterNativeConstructor'],labels['DkPipeEnd'],
            labels['DkRefreshPlatformEnd'])==(0xbd41,0xd1f0,0xd200,0xb6a4)
    cols = new['images']['ROWS']
    assert tuple(c*16 for c in cols)==LEFTS and all(c&15 for c in cols)
    index = labels['OscillatorY']-LAYOUT['REFRESH'][0]
    assert new['images']['REFRESH'][index:]==bytes(CENTERS)
    # The only absolute transfers to the two retired private bbox shims
    # are the two calls in the replaced refresh span.
    for target in (0xb7ca,0xb7d9):
        address = target.to_bytes(2,'little')
        transfers = [(at,op) for op in (0x20,0x4c) for at in range(len(payload)-2)
                     if payload[at:at+3]==bytes([op])+address]
        assert len(transfers)==1 and transfers[0][1]==0x20 and 0x1624<=transfers[0][0]<0x16a5,transfers
    carrier = bytearray(payload)
    for name,(pc,size) in LAYOUT.items():
        at = Four.Previous.offset(pc)
        pad = b'\xea' if name=='BOX' else b'\xff'
        original = OLD_NATIVE_CALLS if name=='NATIVE_CALL' else old['images'][name].ljust(size,pad)
        assert carrier[at:at+size]==original,name
        replacement = new['images'][name].ljust(size,pad)
        if name=='ROWS':
            replacement = new['images'][name]+original[len(cols):]
        carrier[at:at+size] = replacement

    cookie = PARENT_COOKIE[:3]+sha256(carrier).digest()[:13]
    image = bytearray(raw)
    pages = []
    for i,page in enumerate(S.V.T.PAGES):
        at = S.Art.CHR+1024*page
        update = carrier[1024*i:1024*(i+1)]
        if update!=raw[at:at+1024]:
            pages.append(page)
            image[at:at+1024] = update
    assert pages==[881,883,960],pages
    image[Four.COOKIE_AT:Four.COOKIE_AT+16] = cookie
    assert S.V.T.payload(image)==carrier
    atlas = json.loads(S.Art.ATLAS.read_text(encoding='utf-8'))
    for selection in atlas['all_legal_8x16_selections']:
        page = selection['physical_page']
        first,last = selection['physical_byte_half_open']
        if page==960 and selection['native_tile'] in S.Art.ALIASES:
            alias = S.Art.ALIASES[selection['native_tile']]
            assert S.Art.art(image,alias)==S.Art.art(raw,alias)
        else:
            at = S.Art.CHR+page*1024
            assert image[at+first:at+last]==raw[at+first:at+last]
    assert sha256(image).hexdigest()==SUCCESSORS[parent]
    return bytes(image),cookie,labels


def scope_cases(before,after,labels):
    counts = Counter()
    for cam,seen in product(range(12*256),range(15)):
        m = Four.fixture(after,cam,seen)
        row = next((i for i,left in enumerate(LEFTS) if i>=seen and 256<=left-cam<=287),None)
        c = S.direct(m,labels['DkPipeScope'])
        assert bool(c.p&1)==(row is not None),(cam,seen,row)
        assert m.ram[2][S.SEEN]==(seen if row is None else row),(cam,seen,row)
        counts['scope'] += 1
        if cam<5*256 and seen<10:
            old = Four.fixture(before,cam,seen)
            a = S.direct(old,0xd18b)
            assert (a.p&1,old.ram[2][S.SEEN])==(c.p&1,m.ram[2][S.SEEN]),(cam,seen)
            counts['old_scope_pairs'] += 1
    for cam,seen,room in product((0x8000,0xffff,0x08f1,0x0a00),(0,13,255),(0,0xce)):
        m = Four.fixture(after,cam,seen)
        N.put(m,AreaDataLow=room)
        expected = next((i for i,left in enumerate(LEFTS) if room==0xce and i>=seen and 256<=left-cam<=287),None)
        assert bool(S.direct(m,labels['DkPipeScope']).p&1)==(expected is not None)
        assert m.ram[2][S.SEEN]==(seen if expected is None else expected)
        counts['foreign_room_or_high_camera'] += 1
    return dict(counts)


def refresh_outcome(m,c):
    return ((c.a,c.x,c.y,c.p,c.sp),Four.abi(m),bytes(m[:0x100]),bytes(m[0x200:0x800]),
            bytes(m.ram[2][:0x900]),tuple(m.ppu_log))


def birth_cases(before,after,labels):
    cases,constructor_sites = Counter(),Counter()
    for row,left in enumerate(LEFTS):
        for cam,slot in product(sorted({left-287,left-256,*[v for v in range(left-287,left-255) if v&255 in (0,255)]}),range(6)):
            outputs = []
            for seed in (before,after) if row<9 else (after,):
                m = Four.fixture(seed,cam,row,6)
                original = Four.abi(m)
                m[0x0b],m[0x0c] = 0x9a,0x17
                S.direct(m,labels['DkRefreshPlatform'])
                assert m.ram[2][S.SEEN]==row and Four.abi(m)==original
                assert all((N.get(m,'Enemy_Flag',s),N.get(m,'Enemy_ID',s))==(1,6) for s in range(6))
                Four.put_slot(m,slot,Enemy_Flag=0,Enemy_X_Speed=0x7f,Enemy_Y_Speed=0x55)
                ctor = []

                def observe(c):
                    if c.pc==0xa74f and B.V.Q.tags(c)==130:
                        ctor.append((c.x,Second.actor(m,c.x)[:4]))
                    if seed is after and c.pc in (labels['DkPipeCreated'],labels['DkAfterNativeConstructor']):
                        constructor_sites[(c.pc,B.V.Q.tags(c))] += 1

                m.ppu_log.clear()
                c = S.direct(m,labels['DkRefreshPlatform'],observe)
                vertical = row!=8
                y,enemy,box = (192,0x25,5) if vertical else (208,0x28,6)
                assert ctor==[(slot,(left,y,enemy,1))],(row,cam,slot,ctor)
                assert Second.actor(m,slot)==(left,y,enemy,1,box,0,CENTERS[row],0),(row,cam,slot)
                assert m.ram[2][S.SEEN]==row+1 and Four.abi(m)==original
                assert (c.a,c.x,c.y,c.p&0xef,c.sp)==(85,7,91,0x21,242)
                assert (m[0x0b],m[0x0c])==(0x9a,0x17)
                assert all((N.get(m,'Enemy_Flag',s),N.get(m,'Enemy_ID',s))==(1,6) for s in range(6) if s!=slot)
                outputs.append(refresh_outcome(m,c))
                Four.put_slot(m,slot,Enemy_Flag=0)
                S.direct(m,labels['DkRefreshPlatform'])
                assert not N.get(m,'Enemy_Flag',slot) and m.ram[2][S.SEEN]==row+1
            if row<9:
                assert outputs[0]==outputs[1],(row,cam,slot)
            cases['old' if row<9 else 'late'] += 1
    assert set(constructor_sites)=={(0xbd41,3),(0xd1f0,2)},constructor_sites
    m = Four.fixture(after,2753,13)
    N.invoke(m,'HuFresh')
    assert m.ram[2][S.SEEN]==0
    return dict(cases,warm_life_reset=1,hooks={f'{b}:{a:04x}':n for (a,b),n in constructor_sites.items()})


def refresh_cases(before,after,labels):
    counts = Counter()
    cycles = {}
    for slot,enemy,flag,dx,state,cam in product(range(6),range(0x24,0x2d),(0,1,0x80),
                                                (-32,0,63,255,288),(0,0x40),(1024,2432)):
        samples = []
        for seed in (before,after):
            m = Four.fixture(seed,cam,13)
            x = cam+dx
            Four.put_slot(m,slot,Enemy_Flag=flag,Enemy_ID=enemy,Enemy_State=state,Enemy_X_Position=x&255,
                          Enemy_PageLoc=x>>8,Enemy_Y_Position=192,Enemy_Y_HighPos=1,
                          Enemy_BoundBoxCtrl=4 if enemy>=0x2b else 5)
            m.ppu_log.clear()
            c = S.direct(m,labels['DkRefreshPlatform'])
            samples.append((refresh_outcome(m,c),c.processorCycles))
        assert samples[0][0]==samples[1][0],(slot,enemy,flag,dx,state,cam)
        group = 'active' if flag==1 else 'empty_or_inactive'
        cycles.setdefault(group,[]).append(samples[1][1]-samples[0][1])
        counts[group] += 1
    return dict(counts,cycle_deltas={k:[min(v),max(v)] for k,v in cycles.items()})


def native_birth_frames(image,labels):
    evidence = []
    for row,ingress in enumerate(((2400,128),(2468,112),(2657,176),(2868,144)),start=9):
        left = LEFTS[row]
        camera = left-287
        m,idle = Late.entry(Late.Gap.terrain(image,camera),*ingress)
        m.ram[2][S.SEEN] = row
        witnesses = []

        def observe(c):
            if c.pc==0xa74f and B.V.Q.tags(c)==130 and N.get(m,'Enemy_ID',c.x)==0x25:
                witnesses.append((c.x,B.camera(m),B.player(m),Second.actor(m,c.x)[:4]))
            elif c.pc==labels['DkPipeCreated'] and B.V.Q.tags(c)==3:
                assert len(witnesses)==1 and c.x==witnesses[0][0]
                assert Second.actor(m,c.x)==(left,192,0x25,1,5,0,CENTERS[row],0)

        for tick in range(4):
            Second.update(m,idle,0,observe)
            if witnesses:
                break
        assert len(witnesses)==1 and witnesses[0][1]==camera,(row,witnesses,Late.Gap.player(m,tick))
        assert m.ram[2][S.SEEN]==row+1
        evidence.append(dict(row=row,update=tick,constructor=witnesses[0]))
    return evidence


def interrupt_cases(image,labels):
    Q = B.V.Q
    checks = Counter()
    pcs = {(3,labels[name]) for name in ('DkRefreshPlatform','DkSetPlatformTypeAndPosition',
           'DkNativeFarCall','DkNativeBBox','DkPipeCreated','PopScratch')}
    pcs.update((2,labels[name]) for name in ('DkPipeScope','Search','Found','DkAfterNativeConstructor'))
    pcs.add((130,0xa74f))
    minimum = 255

    def snapshot(c):
        clone = N.NesMPU(memory=slim_fork(c.memory),pc=c.pc)
        clone.a,clone.x,clone.y,clone.p,clone.sp = c.a,c.x,c.y,c.p,c.sp
        return clone

    for row,ingress in ((8,(1233,176)),(9,(2400,128)),(12,(2868,144))):
        camera = LEFTS[row]-287
        m,idle = Late.entry(Late.Gap.terrain(image,camera),*ingress)
        m.ram[2][S.SEEN] = row
        cuts = {}

        def capture(c):
            if c.pc>=0x8000 and (key:=(Q.tags(c),c.pc)) in pcs and key not in cuts:
                cuts[key] = snapshot(c)

        m.controller_pad = 0
        N.consume(m)
        c = N.NesMPU(memory=m,pc=idle)
        c.sp,c.p = 255,0x31
        c.stPushWord(0xe33b)
        end = idle+12,252
        B.run(c,lambda z:(z.pc,z.sp)==end,capture)
        baseline = Q.final(c),bytes(m[3:14])
        assert set(cuts)==(pcs if row!=8 else pcs-{(3,labels['DkPipeCreated'])}),cuts.keys()
        for key,cut in cuts.items():
            for irq in ((False,) if cut.p&4 else (False,True)):
                test = snapshot(cut)
                bus = test.memory
                entry = test.pc,test.sp
                before = Q.live(test),bytes(bus[0x0b:0x0d])
                skip = N.get(bus,'NmiSkipped')
                bus.writes.clear()
                if irq:
                    test.irq()
                    assert (Q.tags(test),test.pc)==(254,0x8000)
                else:
                    assert N.get(bus,'NmiDisable')==255
                    test.nmi()

                def check_stack(c):
                    nonlocal minimum
                    minimum = min(minimum,c.sp)
                    assert c.sp>0x7a and Q.tags(c) not in (2,3)

                B.run(test,lambda z:(z.pc,z.sp)==entry,check_stack)
                assert (Q.live(test),bytes(bus[0x0b:0x0d]))==before,(row,key,irq)
                assert N.get(bus,'NmiSkipped')==(skip+int(not irq))&255
                assert not any(at in (0x2007,0x4014) for at,_ in bus.writes)
                B.run(test,lambda z:(z.pc,z.sp)==end)
                assert (Q.final(test),bytes(bus[3:14]))==baseline,(row,key,irq)
                checks['IRQ' if irq else 'FF_NMI'] += 1
    return dict(checks,minimum_ISR_SP=minimum)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--section',choices=('all','scope','birth','refresh','frames','vectors'),default='all')
    args = parser.parse_args()
    raw = source_parent()
    image,cookie,labels = proposal(raw)
    print(json.dumps(dict(parent_SHA256=PARENT,memory_only_SHA256=sha256(image).hexdigest(),cookie=cookie.hex(),
                          DkPipeCreated=hex(labels['DkPipeCreated']),
                          DkAfterNativeConstructor=hex(labels['DkAfterNativeConstructor']))),flush=True)
    if args.section in ('all','frames'):
        print(json.dumps(dict(actual_frames=native_birth_frames(image,labels)),separators=(',',':')),flush=True)
    if args.section in ('all','vectors'):
        print(json.dumps(dict(vectors=interrupt_cases(image,labels)),separators=(',',':')),flush=True)
    if args.section not in ('frames','vectors'):
        before = Four.cold(raw,PARENT_COOKIE)
        after = Four.cold(image,cookie)
        for name,test in (('scope',scope_cases),('birth',birth_cases),('refresh',refresh_cases)):
            if args.section in ('all',name):
                print(json.dumps({name:test(before,after,labels)},separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
